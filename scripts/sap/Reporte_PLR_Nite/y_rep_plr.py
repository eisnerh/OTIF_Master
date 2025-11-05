# -*- coding: utf-8 -*-
r"""
Y_REP_PLR (homologado estilo Y_DEV_74)
--------------------------------------
• Patrón robusto y dinámico (idéntico al de Y_DEV_74) con find()/timeouts, árbol dinámico y retorno a Easy Access.
• Autodetección de conexión/sesión (--conn -1, --sess -1) y logs de índices efectivos.
• Flujo completo para zsd_rep_planeamiento: nodo F00120 → selección → limpiar ENAME-LOW → ALV fila (por defecto 11)
  → setear fecha P_LFDAT-LOW (por defecto: HOY en dd.mm.yyyy) → ejecutar → exportar → guardar → verificar → volver a SAP Easy Access.
• Exporta por Menú → Hoja de cálculo (selección de formato [1,0]) con encoding configurable (por defecto 0000).

Ejemplos:
  python y_rep_plr.py --debug
  python y_rep_plr.py --date 27.09.2025 -o "C:\\data" -f "REP_PLR_2709.xls"
"""
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
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

def limpiar_sesion_sap(session):
    """
    Limpia la sesión SAP antes de ejecutar el script.
    - Cierra ventanas abiertas
    - Regresa al menú principal
    - Espera a que la sesión esté lista
    """
    try:
        # Ir al menú principal
        session.findById("wnd[0]").sendVKey(0)  # Enter
        session.findById("wnd[0]").sendCommand("/n")  # Comando para ir al menú principal
        session.findById("wnd[0]").sendVKey(0)  # Enter

        # Cerrar ventanas adicionales si existen
        for i in range(1, 10):  # Máximo 10 ventanas
            try:
                session.findById(f"wnd[{i}]").close()
            except:
                break  # No hay más ventanas

        # Esperar a que la sesión esté lista
        while not session.findById("wnd[0]/usr").Text:
            time.sleep(0.5)

        print("✅ Sesión SAP limpiada correctamente.")
    except Exception as e:
        print(f"⚠️  Error al limpiar la sesión SAP: {e}")


def attach_to_sap(connection_index: int = -1, session_index: int = -1):
    """Adjunta a SAP GUI (si índices < 0, toma la última conexión/sesión abiertas)."""
    try:
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
    except Exception:
        raise SAPGuiError("No se encontró el objeto SAPGUI. ¿Está abierto SAP Logon?")
    try:
        application = SapGuiAuto.GetScriptingEngine
    except Exception:
        raise SAPGuiError("No se pudo obtener el motor de scripting. ¿Scripting habilitado?")

    # Conexión
    try:
        conn_count = application.Children.Count
    except Exception:
        conn_count = 0
    if conn_count == 0:
        raise SAPGuiError("No hay conexiones abiertas en SAP Logon.")
    if connection_index is None or connection_index < 0:
        connection_index = conn_count - 1
    if connection_index >= conn_count:
        raise SAPGuiError(f"No existe la conexión index={connection_index}. Total={conn_count}")
    try:
        connection = application.Children(connection_index)
    except Exception:
        raise SAPGuiError(f"No existe la conexión index={connection_index}.")

    # Sesión
    try:
        sess_count = connection.Children.Count
    except Exception:
        sess_count = 0
    if sess_count == 0:
        raise SAPGuiError(f"La conexión index={connection_index} no tiene sesiones abiertas.")
    if session_index is None or session_index < 0:
        session_index = sess_count - 1
    if session_index >= sess_count:
        raise SAPGuiError(
            f"No existe la sesión index={session_index} en la conexión {connection_index}. Total={sess_count}")
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
    wnd0.sendVKey(0)

# ---- Árbol dinámico / Debug ----
def iter_children(obj):
    try:
        count = obj.Children.Count
    except Exception:
        return
    for i in range(count):
        yield obj.Children(i)

def find_control_by_type(root, target_type: str, timeout: float = 8.0):
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
    return find_control_by_type(usr, "GuiTree", timeout=6.0)

def select_tree_node_dynamic(session, node_key: str, debug: bool = False):
    tree = try_get_tree(session)
    if not tree:
        if debug:
            print("🔎 No se detectó GuiTree; se continuará sin seleccionar nodo.")
        return False
    try:
        tree.selectedNode = node_key
        tree.doubleClickNode(node_key)
        if debug:
            print(f"✅ Nodo del árbol abierto: {node_key}")
        return True
    except Exception as e:
        if debug:
            print(f"⚠️  No se pudo abrir el nodo {node_key}: {e}")
        return False

def dump_controls(session, wnd: str = "wnd[0]"):
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

def go_to_easy_access(session):
    ok = find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = "/n"
    find(session, "wnd[0]").sendVKey(0)
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")
        press_if_exists(session, f"wnd[{wnd_index}]/usr/btnSPOP-OPTION1")

# ------------------------------ flujo Y_REP_PLR (homologado) -------------------

def set_main_date(session, field_id: str, date_str: str):
    ctrl = find(session, f"wnd[0]/usr/ctxt{field_id}")
    ctrl.text = date_str
    try:
        ctrl.setFocus()
        ctrl.caretPosition = len(date_str)
    except Exception:
        pass

def run_y_rep_plr(session,
                  tcode: str,
                  node_key: str,
                  row_number: int,
                  output_path: str,
                  filename: str,
                  date_str: str,
                  debug: bool = False,
                  encoding: str = "0000"):
    """
    Flujo equivalente a Y_DEV_74, adaptado a PLR:
    - tcode (zsd_rep_planeamiento)
    - árbol → abrir nodo (F00120)
    - selección → limpiar ENAME-LOW → buscar → ALV (fila) → doble clic
    - setear fecha P_LFDAT-LOW → ejecutar → exportar → guardar → verificar → volver a Easy Access
    """
    # 1) Ir a la transacción
    send_tcode(session, tcode)

    # 2) Intentar seleccionar nodo del árbol (fallback si no hay)
    has_tree = select_tree_node_dynamic(session, node_key=node_key, debug=debug)
    if debug and not has_tree:
        print("🔎 No se seleccionó nodo (no hay árbol o no coincide el ID).")

    # 3) Botón de selección
    if press_if_exists(session, "wnd[0]/tbar[1]/btn[17]") is False and debug:
        print("⚠️  No se encontró el botón de selección [17]; se continúa si la dynpro ya está disponible.")

    # 4) Pop-up: limpiar ENAME-LOW y buscar
    ename = find(session, "wnd[1]/usr/txtENAME-LOW")
    ename.text = ""
    try:
        ename.setFocus()
        ename.caretPosition = 0
    except Exception:
        pass
    find(session, "wnd[1]/tbar[0]/btn[8]").press()

    # 5) Seleccionar fila en ALV y doble clic (con posible scroll)
    alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    try:
        if row_number > 10:
            alv.firstVisibleRow = max(row_number - 10, 0)
    except Exception:
        pass
    alv.currentCellRow = row_number
    alv.selectedRows = str(row_number)
    alv.doubleClickCurrentCell()

    # 6) Setear fecha en dynpro principal
    set_main_date(session, "P_LFDAT-LOW", date_str)

    # 7) Ejecutar reporte
    find(session, "wnd[0]/tbar[1]/btn[8]").press()

    # 8) Exportar: Menú -> Hoja de cálculo
    find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()

    # 9) Selector de formato (radio [1,0]) y continuar
    rb = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
    find(session, rb).select()
    find(session, "wnd[1]/tbar[0]/btn[0]").press()

    # 10) Guardado
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

    # 11) Pop-ups comunes
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")

    # 12) Verificación local
    if not os.path.isfile(full_path):
        if debug:
            dump_controls(session, "wnd[0]")
        press_if_exists(session, "wnd[0]/tbar[0]/btn[3]")  # Back
        raise SAPGuiError(f"El archivo no se generó: {full_path}")

    # 13) Volver a SAP Easy Access
    go_to_easy_access(session)
    return full_path

# ----------------------------------- CLI ---------------------------------------

def parse_args():
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    nombre_archivo = f"REP_PLR-{fecha_actual}.xls"

    p = argparse.ArgumentParser(description="Ejecuta Y_REP_PLR (homologado estilo Y_DEV_74) y exporta a Excel.")
    p.add_argument("--tcode", default="zsd_rep_planeamiento", help='Transacción (por defecto: "zsd_rep_planeamiento")')
    p.add_argument("--node", default="F00120", help='Nodo del árbol a abrir (por defecto: "F00120")')
    p.add_argument("-r", "--row", type=int, default=11, help="Fila del ALV a seleccionar (por defecto: 11)")
    p.add_argument("-o", "--output", default=r"C:\\data\\SAP_Extraction\\rep_plr", help="Ruta de salida (por defecto: C:\\data\\SAP_Extraction\\rep_plr)")
    p.add_argument("-f", "--filename", default=nombre_archivo, help=f"Nombre del archivo (por defecto: {nombre_archivo})")
    p.add_argument("--date", help='Fecha para P_LFDAT-LOW ("dd.mm.yyyy"). Si se omite, usa HOY.')
    p.add_argument("--encoding", default="0000", help='Codificación de archivo (campo DY_FILE_ENCODING).')
    p.add_argument("--conn", type=int, default=-1, help="Índice de conexión SAP (-1 = auto)")
    p.add_argument("--sess", type=int, default=-1, help="Índice de sesión SAP (-1 = auto)")
    p.add_argument("--debug", action="store_true", help="Muestra diagnóstico de controles si hay fallos.")
    return p.parse_args()

def main():
    args = parse_args()

    # Si no pasaron fecha, usar HOY (no ayer como en el original)
    date_str = args.date or datetime.now().strftime("%d.%m.%Y")

    print("INICIANDO SCRIPT Y_REP_PLR (HOMOLOGADO 74)")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        _, _, session, resolved_conn, resolved_sess = attach_to_sap(args.conn, args.sess)
        print(f"Conexión={resolved_conn}, Sesión={resolved_sess}")
        print(f"TCode: {args.tcode}\nNodo: {args.node}\nFila ALV: {args.row}")
        print(f"Salida: {args.output}\\{args.filename} \nFecha: {date_str}")
        print(f"Debug: {'ON' if args.debug else 'OFF'}")
        print("=" * 60)

        full_path = run_y_rep_plr(
            session=session,
            tcode=args.tcode,
            node_key=args.node,
            row_number=args.row,
            output_path=args.output,
            filename=args.filename,
            date_str=date_str,
            debug=args.debug,
            encoding=args.encoding,
        )

        print("\n" + "=" * 60)
        print("🎉 PROCESO Y_REP_PLR HOMOLOGADO (74) COMPLETADO")
        print("=" * 60)
        print(f"✅ Archivo generado: {os.path.basename(full_path)}")
        print(f"📁 Ubicación: {os.path.dirname(full_path)}")
        print(f"🕐 Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⚠️  Script interrumpido por el usuario"); sys.exit(1)
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

