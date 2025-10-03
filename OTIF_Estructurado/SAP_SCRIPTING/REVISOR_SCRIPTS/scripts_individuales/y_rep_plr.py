# -*- coding: utf-8 -*-
"""
Y_REP_PLR – Script robusto de SAP GUI Scripting (COM) 
=====================================================
• Patrón homologado con manejo robusto de controles (similar a y_dev_74 / y_dev_82_homologado).
• Autodetección de conexión/sesión por defecto (--conn -1, --sess -1).
• Detección dinámica del árbol (GuiTree) para entornos donde cambian los IDs.
• Parámetros flexibles para setear campos de selección (--set), seleccionar filas de ALV, 
  exportar a Excel y volver a SAP Easy Access al finalizar.
• Modo --debug para diagnóstico con DUMP de controles.

Requisitos:
- SAP GUI Scripting habilitado (cliente/servidor).
- pywin32 instalado: pip install pywin32
- SAP Logon abierto y sesión activa.

Ejemplos de uso:
  1) Ejecutar transacción Y_REP_PLR y exportar (autodetecta conexión/sesión):
     python y_rep_plr.py --tcode Y_REP_PLR --output "C:\\data\\y_rep_plr" --filename "reporte.xls" --debug

  2) Setear varios campos de selección antes de ejecutar (prefijo del tipo opcional):
     python y_rep_plr.py --tcode Y_REP_PLR \
       --set "ctxtSP$00001-LOW=01.10.2025" \
       --set "ctxtSP$00001-HIGH=31.10.2025" \
       --set "cboS_WERKS=1100" \
       --set "chkS_INCL_HIST=1" \
       --execute --export --output "C:\\data\\y_rep_plr" --filename "y_rep_plr.xls"

  3) Flujo con árbol y selección desde pop-up (ALV fila 2):
     python y_rep_plr.py --tcode Y_REP_PLR --node F00ABC --open-selection \
       --alv-row 2 --execute --export --debug

Notas:
- --set acepta N repeticiones. Si no especificas el prefijo (ctxt/txt/cbo/chk/rad), 
  se asume "ctxt" y se usará wnd[0]/usr/ctxt<Campo>. Para pop-ups usa --set-popup 
  (aplica sobre wnd[1]/usr/...)
- Para combos (cbo) se intenta .Key y luego .Text. Para checks (chk) se interpreta 1/0, true/false, yes/no.
- --export utiliza Menú -> Hoja de cálculo (ruta típica). Ajusta si tu sistema difiere.
"""
import os
import sys
import time
import argparse
from datetime import datetime

try:
    import win32com.client  # type: ignore
except ImportError:
    print("❌ Falta pywin32. Instala con: pip install pywin32")
    sys.exit(1)


class SAPGuiError(Exception):
    pass


# ------------------------------ utilidades base --------------------------------
def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def attach_to_sap(connection_index: int = -1, session_index: int = -1):
    """Adjunta a SAP GUI.
    Si connection_index o session_index son < 0, selecciona automáticamente el último disponible.
    Devuelve: (application, connection, session, resolved_conn_index, resolved_sess_index)
    """
    try:
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
    except Exception:
        raise SAPGuiError("No se encontró el objeto SAPGUI. ¿Está abierto SAP Logon?")
    try:
        application = SapGuiAuto.GetScriptingEngine
    except Exception:
        raise SAPGuiError("No se pudo obtener el motor de scripting. ¿Scripting habilitado?")

    # Resolver conexión
    try:
        conn_count = application.Children.Count
    except Exception:
        conn_count = 0
    if conn_count == 0:
        raise SAPGuiError("No hay conexiones abiertas en SAP Logon.")

    if connection_index is None or connection_index < 0:
        connection_index = conn_count - 1  # última
    if connection_index >= conn_count:
        raise SAPGuiError(f"No existe la conexión index={connection_index}. Total={conn_count}")
    try:
        connection = application.Children(connection_index)
    except Exception:
        raise SAPGuiError(f"No existe la conexión index={connection_index}.")

    # Resolver sesión
    try:
        sess_count = connection.Children.Count
    except Exception:
        sess_count = 0
    if sess_count == 0:
        raise SAPGuiError(f"La conexión index={connection_index} no tiene sesiones abiertas.")

    if session_index is None or session_index < 0:
        session_index = sess_count - 1  # última
    if session_index >= sess_count:
        raise SAPGuiError(
            f"No existe la sesión index={session_index} en la conexión {connection_index}. Total={sess_count}"
        )
    try:
        session = connection.Children(session_index)
    except Exception:
        raise SAPGuiError(f"No existe la sesión index={session_index}.")

    return application, connection, session, connection_index, session_index


def find(session, obj_id, timeout: float = 12.0, interval: float = 0.25):
    """Espera hasta encontrar un control por ID (con timeout)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            return session.FindById(obj_id)
        except Exception:
            time.sleep(interval)
    raise SAPGuiError(f"No se encontró el control: {obj_id}")


def exists(session, obj_id):
    try:
        session.FindById(obj_id)
        return True
    except Exception:
        return False


def press_if_exists(session, obj_id):
    if exists(session, obj_id):
        try:
            session.FindById(obj_id).press()
            return True
        except Exception:
            pass
    return False


def send_tcode(session, tcode: str):
    wnd0 = find(session, "wnd[0]")
    try:
        wnd0.maximize()
    except Exception:
        pass
    ok = find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = tcode
    wnd0.sendVKey(0)  # Enter


# ------------------------------ árbol dinámico ---------------------------------

def iter_children(obj):
    """Itera hijos de un objeto SAP GUI (seguro para objetos sin Children)."""
    try:
        count = obj.Children.Count
    except Exception:
        return
    for i in range(count):
        yield obj.Children(i)


def find_control_by_type(root, target_type: str, timeout: float = 8.0):
    """Búsqueda en anchura por .Type (p.ej., 'GuiTree') bajo 'root'."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        queue = [root]
        while queue:
            node = queue.pop(0)
            try:
                if getattr(node, "Type", "") == target_type:
                    return node
            except Exception:
                pass
            queue.extend(list(iter_children(node)))
        time.sleep(0.25)
    return None


def try_get_tree(session):
    """Intenta obtener el GuiTree principal por IDs comunes o por tipo (fallback)."""
    candidates = [
        "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell",
        "wnd[0]/usr/cntlTREE_CONTAINER/shellcont/shell/shellcont[0]/shell",
        "wnd[0]/usr/shell/shellcont[0]/shell",
        "wnd[0]/usr/cntlGRID_CONTAINER/shellcont/shell/shellcont[0]/shell",
    ]
    for cid in candidates:
        if exists(session, cid):
            ctl = session.FindById(cid)
            if getattr(ctl, "Type", "") in ("GuiTree", "GuiShell"):
                return ctl
    usr = find(session, "wnd[0]/usr")
    tree = find_control_by_type(usr, "GuiTree", timeout=6.0)
    return tree  # Puede ser None si no hay árbol en esta transacción


def select_tree_node_dynamic(session, node_key: str, debug: bool = False):
    tree = try_get_tree(session)
    if not tree:
        if debug:
            print("ℹ️ No se detectó GuiTree; se continuará sin seleccionar nodo.")
        return False
    try:
        tree.selectedNode = node_key
        tree.doubleClickNode(node_key)
        if debug:
            print(f"✅ Nodo del árbol abierto: {node_key}")
        return True
    except Exception as e:
        if debug:
            print(f"⚠️ No se pudo abrir el nodo {node_key}: {e}")
        return False


def dump_controls(session, wnd: str = "wnd[0]"):
    """Lista IDs/Type de controles bajo wnd[0]/usr (diagnóstico con --debug)."""
    print("\n--- DUMP DE CONTROLES (IDs y Types) ---")
    root = find(session, f"{wnd}/usr")
    queue = [(root, f"{wnd}/usr")]
    while queue:
        obj, path = queue.pop(0)
        t = ""
        try:
            t = obj.Type
        except Exception:
            pass
        print(f"{path} -> {t}")
        try:
            cnt = obj.Children.Count
            for i in range(cnt):
                child = obj.Children(i)
                try:
                    cid = child.Id
                except Exception:
                    cid = f"{path}/<?>[{i}]"
                queue.append((child, cid))
        except Exception:
            continue
    print("--- FIN DUMP ---\n")


# --------------------------- setters de campos flexibles ------------------------

def _apply_value_to_control(ctrl, value: str):
    """Aplica el valor apropiadamente según el tipo del control."""
    ctype = getattr(ctrl, 'Type', '')
    try:
        if 'GuiCTextField' in ctype or 'GuiTextField' in ctype or 'GuiComboBox' not in ctype:
            # Campos de texto/contexto
            if hasattr(ctrl, 'text'):
                ctrl.text = value
            else:
                try:
                    ctrl.Text = value
                except Exception:
                    pass
        if 'GuiCBox' in ctype or 'GuiComboBox' in ctype:
            # Combos: intentar Key y luego Text
            try:
                ctrl.Key = value
            except Exception:
                try:
                    ctrl.Text = value
                except Exception:
                    pass
        if 'GuiCheckBox' in ctype:
            v = str(value).strip().lower()
            ctrl.selected = v in ('1', 'true', 't', 'yes', 'y', 'si', 'sí')
        if 'GuiRadioButton' in ctype:
            v = str(value).strip().lower()
            if v in ('1', 'true', 't', 'yes', 'y', 'si', 'sí'):
                ctrl.select()
    except Exception:
        pass
    # foco/caret (no imprescindible)
    try:
        ctrl.setFocus()
        if hasattr(ctrl, 'caretPosition'):
            ctrl.caretPosition = len(str(value))
    except Exception:
        pass


def set_fields(session, pairs, wnd_index: int = 0, default_prefix: str = 'ctxt'):
    """Setea campos bajo wnd[<wnd_index>]/usr a partir de pares ["<id>=<valor>"]
    <id> puede traer prefijo: ctxt, txt, cbo, chk, rad. Si no, se antepone `default_prefix`.
    Ej: 'ctxtSP$00001-LOW=01.10.2025' -> wnd[0]/usr/ctxtSP$00001-LOW
    """
    root = f"wnd[{wnd_index}]/usr"
    for item in pairs:
        if '=' not in item:
            raise SAPGuiError(f"Formato inválido en --set: '{item}'. Usa id=valor")
        key, value = item.split('=', 1)
        key = key.strip()
        value = value.strip()
        # Si no viene prefijo, agregar default
        if not any(key.startswith(p) for p in ('ctxt', 'txt', 'cbo', 'chk', 'rad')):
            key = f"{default_prefix}{key}"
        obj_id = f"{root}/{key}"
        ctrl = find(session, obj_id)
        _apply_value_to_control(ctrl, value)


# ------------------------------ volver a Easy Access ----------------------------

def go_to_easy_access(session):
    """Vuelve a SAP Easy Access y maneja pop-ups comunes."""
    ok = find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = "/n"
    find(session, "wnd[0]").sendVKey(0)  # Enter
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")   # Sí/Continuar
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")  # Guardar/Aceptar
        press_if_exists(session, f"wnd[{wnd_index}]/usr/btnSPOP-OPTION1")


# ------------------------------ flujo principal --------------------------------

def run_y_rep_plr(
    session,
    tcode: str,
    node_key: str | None,
    open_selection: bool,
    alv_row: int | None,
    set_pairs: list[str],
    set_popup_pairs: list[str],
    do_execute: bool,
    do_export: bool,
    output_path: str,
    filename: str,
    encoding: str = "0000",
    debug: bool = False,
):
    # 1) Transacción
    if tcode:
        send_tcode(session, tcode)

    # 2) Árbol (opcional)
    if node_key:
        ok = select_tree_node_dynamic(session, node_key=node_key, debug=debug)
        if debug and not ok:
            print("🔎 No se seleccionó nodo (no hay árbol o no coincide el ID).")

    # 3) Abrir pantalla de selección (si pidió)
    if open_selection:
        if press_if_exists(session, "wnd[0]/tbar[1]/btn[17]") is False and debug:
            print("ℹ️ No se encontró el botón de selección [17]; puede que ya estés en la dynpro de selección.")

    # 4) Setear campos en ventana principal (wnd[0])
    if set_pairs:
        set_fields(session, set_pairs, wnd_index=0, default_prefix='ctxt')

    # 5) Setear campos en pop-up (wnd[1])
    if set_popup_pairs:
        set_fields(session, set_popup_pairs, wnd_index=1, default_prefix='ctxt')

    # 6) Si hay un pop-up con lista ALV y se indicó fila, seleccionarla
    if alv_row is not None:
        alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
        try:
            if alv_row > 10:
                alv.firstVisibleRow = max(alv_row - 10, 0)
        except Exception:
            pass
        alv.currentCellRow = alv_row
        alv.selectedRows = str(alv_row)
        try:
            alv.doubleClickCurrentCell()
        except Exception:
            pass

    # 7) Ejecutar (opcional)
    if do_execute:
        find(session, "wnd[0]/tbar[1]/btn[8]").press()

    # 8) Exportar (opcional)
    full_path = None
    if do_export:
        # Menú -> Hoja de cálculo (ajustar si difiere en tu entorno)
        find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
        rb = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
        find(session, rb).select()
        find(session, "wnd[1]/tbar[0]/btn[0]").press()

        ensure_dir(output_path)
        full_path = os.path.join(output_path, filename)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except PermissionError:
                base_name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%H%M%S')
                filename = f"{base_name}_{timestamp}{ext}"
                full_path = os.path.join(output_path, filename)

        find(session, "wnd[1]/usr/ctxtDY_PATH").text = output_path
        find(session, "wnd[1]/usr/ctxtDY_FILENAME").text = filename
        enc = find(session, "wnd[1]/usr/ctxtDY_FILE_ENCODING")
        enc.text = encoding
        try:
            enc.setFocus()
            enc.caretPosition = len(encoding)
        except Exception:
            pass
        find(session, "wnd[1]/tbar[0]/btn[11]").press()

        for wnd_index in (2, 1):
            press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
            press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")

        if full_path and not os.path.isfile(full_path):
            if debug:
                dump_controls(session, "wnd[0]")
            press_if_exists(session, "wnd[0]/tbar[0]/btn[3]")
            raise SAPGuiError(f"El archivo no se generó: {full_path}")

    return full_path


# ----------------------------------- CLI ---------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Ejecuta Y_REP_PLR y exporta a Excel (patrón robusto).")
    p.add_argument("--tcode", required=True, help='Transacción a ejecutar (p.ej., "Y_REP_PLR")')
    p.add_argument("--node", help='Nodo del árbol a abrir (opcional, p.ej., "F00139")')
    p.add_argument("--open-selection", action="store_true", help='Presiona el botón de selección (tbar[1]/btn[17]).')
    p.add_argument("--alv-row", type=int, help='Fila del ALV en pop-up a seleccionar (wnd[1]).')
    p.add_argument("--set", dest="set_pairs", action="append", default=[], help='Setea campos en wnd[0]/usr: id=valor (repetible).')
    p.add_argument("--set-popup", dest="set_popup_pairs", action="append", default=[], help='Setea campos en wnd[1]/usr: id=valor (repetible).')
    p.add_argument("--execute", action="store_true", help='Presiona Ejecutar (tbar[1]/btn[8]).')
    p.add_argument("--export", action="store_true", help='Exporta a Excel (Menú -> Hoja de cálculo).')
    p.add_argument("-o", "--output", default=r"C:\\data\\y_rep_plr", help="Ruta de salida (por defecto: C:\\data\\y_rep_plr)")
    p.add_argument("-f", "--filename", help="Nombre del archivo (si no se especifica, se genera automáticamente con fecha)")
    p.add_argument("--encoding", default="0000", help='Codificación de archivo (campo DY_FILE_ENCODING).')
    p.add_argument("--conn", type=int, default=-1, help="Índice de conexión SAP (-1 = auto, por defecto: -1)")
    p.add_argument("--sess", type=int, default=-1, help="Índice de sesión SAP (-1 = auto, por defecto: -1)")
    p.add_argument("--debug", action="store_true", help="Muestra diagnóstico de controles si hay fallos.")
    p.add_argument("--no-easy-access", action="store_true", help="No volver a SAP Easy Access al finalizar.")
    return p.parse_args()


def main():
    args = parse_args()

    if not args.filename:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        args.filename = f"y_rep_plr_{fecha_actual}.xls"

    os.makedirs(args.output, exist_ok=True)

    print("INICIANDO SCRIPT Y_REP_PLR")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        _, _, session, resolved_conn, resolved_sess = attach_to_sap(args.conn, args.sess)
        print(f"Conexión={resolved_conn}, Sesión={resolved_sess}")
        print(f"TCode: {args.tcode}")
        if args.node:
            print(f"Nodo: {args.node}")
        if args.alv_row is not None:
            print(f"ALV Row: {args.alv_row}")
        print(f"Salida: {args.output}\\{args.filename}")
        print(f"Debug: {'ON' if args.debug else 'OFF'}")
        print("=" * 60)

        full_path = run_y_rep_plr(
            session=session,
            tcode=args.tcode,
            node_key=args.node,
            open_selection=args.open_selection,
            alv_row=args.alv_row,
            set_pairs=args.set_pairs,
            set_popup_pairs=args.set_popup_pairs,
            do_execute=args.execute,
            do_export=args.export,
            output_path=args.output,
            filename=args.filename,
            encoding=args.encoding,
            debug=args.debug,
        )

        # Volver a Easy Access (a menos que lo eviten)
        if not args.no_easy_access:
            go_to_easy_access(session)

        print("\n" + "=" * 60)
        print("🎉 PROCESO Y_REP_PLR COMPLETADO")
        print("=" * 60)
        if full_path:
            print(f"📁 Archivo generado: {os.path.basename(full_path)}")
            print(f"📂 Ubicación: {os.path.dirname(full_path)}")
        print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️ Script interrumpido por el usuario")
        sys.exit(1)
    except SAPGuiError as e:
        print(f"❌ Error SAP: {e}")
        if args.debug:
            try:
                _, _, session, _, _ = attach_to_sap(args.conn, args.sess)
                dump_controls(session, "wnd[0]")
            except Exception:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if args.debug:
            try:
                _, _, session, _, _ = attach_to_sap(args.conn, args.sess)
                dump_controls(session, "wnd[0]")
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
