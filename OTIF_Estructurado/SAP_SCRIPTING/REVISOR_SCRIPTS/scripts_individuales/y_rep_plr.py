#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatiza la transacción REP_PLR (zsd_rep_planeamiento) y exporta a Excel usando SAP GUI Scripting (COM).
Robustez añadida:
  - Detección dinámica del árbol (GuiTree). Si no existe, se salta la selección del nodo.
  - Retorno automático a SAP Easy Access al finalizar (go_to_easy_access).
  - Modo --debug para listar controles visibles e IDs (ayuda a ajustar IDs en tu entorno).

Requisitos:
  - SAP GUI Scripting habilitado en cliente y servidor.
  - pywin32 instalado: pip install pywin32
  - SAP Logon abierto y sesión activa.

Uso (ejemplos):
  python rep_plr.py --date "27.09.2025" --row 11 --output "C:\\data" --filename "REP_PLR.xls" --conn 0 --sess 0
  # Si omites --date, usa AYER automáticamente (dd.mm.yyyy)
"""

import os
import sys
import time
import argparse
from datetime import datetime, timedelta

try:
    import win32com.client
except ImportError:
    print("❌ Falta pywin32. Instala con: pip install pywin32")
    sys.exit(1)


class SAPGuiError(Exception):
    pass


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def attach_to_sap(connection_index=0, session_index=0):
    """Adjunta a la sesión de SAP ya abierta."""
    try:
        SapGuiAuto = win32com.client.GetObject("SAPGUI")
    except Exception:
        raise SAPGuiError("No se encontró el objeto SAPGUI. ¿Está abierto SAP Logon?")

    try:
        application = SapGuiAuto.GetScriptingEngine
    except Exception:
        raise SAPGuiError("No se pudo obtener el motor de scripting. ¿Scripting habilitado?")

    try:
        connection = application.Children(connection_index)
    except Exception:
        raise SAPGuiError(f"No existe la conexión index={connection_index}.")
    try:
        session = connection.Children(session_index)
    except Exception:
        raise SAPGuiError(f"No existe la sesión index={session_index}.")
    return application, connection, session


def find(session, obj_id, timeout=12.0, interval=0.25):
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


def set_main_date(session, field_id: str, date_str: str):
    """Setea la fecha en el campo de la dynpro principal (ctxt<field_id>)."""
    ctrl = find(session, f"wnd[0]/usr/ctxt{field_id}")
    ctrl.text = date_str
    try:
        ctrl.setFocus()
        ctrl.caretPosition = len(date_str)
    except Exception:
        pass


# ---------- NEW: utilidades de descubrimiento dinámico -----------------------

def iter_children(obj):
    """Itera hijos de un objeto SAP GUI (seguro para objetos sin Children)."""
    try:
        count = obj.Children.Count
    except Exception:
        return
    for i in range(count):
        yield obj.Children(i)


def find_control_by_type(root, target_type: str, timeout=8.0):
    """
    Busca en anchura bajo 'root' un control por .Type (p.ej., 'GuiTree', 'GuiGridView').
    Devuelve la primera coincidencia o None si no hay.
    """
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
    """
    Intenta obtener el GuiTree principal de la pantalla actual:
      1) Por IDs típicos (compatibilidad).
      2) Por exploración de tipo (GuiTree) bajo wnd[0]/usr.
    """
    # 1) IDs candidatos (de grabaciones comunes); prueba rápida
    candidates = [
        "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell",
        "wnd[0]/usr/cntlTREE_CONTAINER/shellcont/shell/shellcont[0]/shell",
        "wnd[0]/usr/shell/shellcont[0]/shell",
        "wnd[0]/usr/cntlGRID_CONTAINER/shellcont/shell/shellcont[0]/shell",
    ]
    for cid in candidates:
        if exists(session, cid):
            ctl = session.FindById(cid)
            # Algunos shells reportan Type 'GuiTree', otros 'GuiShell'; probemos ambos.
            if getattr(ctl, "Type", "") in ("GuiTree", "GuiShell"):
                return ctl

    # 2) Búsqueda por tipo (GuiTree) bajo wnd[0]/usr
    usr = find(session, "wnd[0]/usr")
    tree = find_control_by_type(usr, "GuiTree", timeout=6.0)
    return tree  # Puede ser None si no existe árbol en esta transacción


def select_tree_node_dynamic(session, node_key: str, debug=False):
    """
    Selecciona y abre (doble clic) un nodo de árbol si existe un GuiTree.
    Si no hay árbol, no falla: devuelve False y el caller decide continuar.
    """
    tree = try_get_tree(session)
    if not tree:
        if debug:
            print("ℹ️ No se detectó GuiTree en la pantalla; se continuará sin seleccionar nodo.")
        return False

    # Asegurar que el nodo existe (si el objeto soporta APIs de GuiTree)
    try:
        # GuiTree: SelectedNode / DoubleClickNode
        tree.selectedNode = node_key
        tree.doubleClickNode(node_key)
        if debug:
            print(f"✅ Nodo del árbol abierto: {node_key}")
        return True
    except Exception:
        # Algunos shells "tree-like" requieren enfoque previo
        try:
            tree.setFocus()
            tree.selectedNode = node_key
            tree.doubleClickNode(node_key)
            if debug:
                print(f"✅ Nodo del árbol abierto (tras focus): {node_key}")
            return True
        except Exception as e:
            if debug:
                print(f"⚠️ No se pudo abrir el nodo {node_key}: {e}")
            return False


def dump_controls(session, wnd="wnd[0]"):
    """
    Recorre y lista IDs/Type de los controles bajo wnd[0]/usr para diagnóstico.
    Útil con --debug si falla algún find().
    """
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
        # Encolar hijos con su id relativo
        try:
            cnt = obj.Children.Count
            for i in range(cnt):
                child = obj.Children(i)
                try:
                    cid = child.Id
                except Exception:
                    # construimos un path aproximado
                    cid = f"{path}/<?>[{i}]"
                queue.append((child, cid))
        except Exception:
            continue
    print("--- FIN DUMP ---\n")

# ---------- FIN utilidades dinámicas -----------------------------------------


# === NEW: volver a SAP Easy Access ===========================================
def go_to_easy_access(session):
    """
    Vuelve a la pantalla inicial de SAP (SAP Easy Access).
    Maneja pop-ups genéricos si aparecen (confirmaciones).
    """
    ok = find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = "/n"
    find(session, "wnd[0]").sendVKey(0)  # Enter

    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")   # Sí/Continuar
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")  # Guardar/Aceptar
        press_if_exists(session, f"wnd[{wnd_index}]/usr/btnSPOP-OPTION1")
# ==============================================================================


def run_rep_plr(session, row_number: int, output_path: str, filename: str,
                date_str: str, debug: bool = False, encoding: str = "0000"):
    """
    Flujo robusto:
      - tcode zsd_rep_planeamiento
      - (si hay) seleccionar nodo F00120 en árbol
      - botón selección -> limpiar ENAME-LOW -> buscar -> ALV (fila) -> doble clic
      - setear fecha P_LFDAT-LOW -> ejecutar -> exportar -> guardar
    """
    # 1) Ir a la transacción
    send_tcode(session, "zsd_rep_planeamiento")

    # 2) Intentar seleccionar el nodo del árbol (si existe). Si no, continuar.
    has_tree = select_tree_node_dynamic(session, node_key="F00120", debug=debug)
    if debug and not has_tree:
        print("🔎 No se seleccionó ningún nodo (no hay árbol o no coincide el ID).")

    # 3) Botón de selección
    #    Si la transacción abrió directo la dynpro, este botón debería existir igual.
    find(session, "wnd[0]/tbar[1]/btn[17]").press()

    # 4) Pop-up: limpiar ENAME-LOW y buscar
    ename = find(session, "wnd[1]/usr/txtENAME-LOW")
    ename.text = ""
    try:
        ename.setFocus()
        ename.caretPosition = 0
    except Exception:
        pass
    find(session, "wnd[1]/tbar[0]/btn[8]").press()

    # 5) Seleccionar fila en ALV y doble clic
    #    Si tu ALV fuese distinto, podemos detectar un GuiGridView genérico aquí.
    alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
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
    
    # Eliminar archivo si ya existe para evitar conflictos
    if os.path.exists(full_path):
        os.remove(full_path)

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

    # 11) Pop-ups
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")

    # 12) Verificación local
    if not os.path.isfile(full_path):
        # Antes de abortar, si pidió --debug, volcamos controles para que ajustes IDs
        if debug:
            dump_controls(session, "wnd[0]")
            press_if_exists(session, "wnd[0]/tbar[0]/btn[3]")  # Back, por si quedó en lista
        raise SAPGuiError(f"El archivo no se generó: {full_path}")

    # 13) Volver a SAP Easy Access
    go_to_easy_access(session)

    return full_path


def parse_args():
    p = argparse.ArgumentParser(description="Ejecuta REP_PLR y exporta a Excel (standalone y robusto).")
    p.add_argument("-o", "--output", default=r"C:\data\rep_plr", help="Ruta de salida (por defecto: C:\\data\\rep_plr)")
    p.add_argument("-f", "--filename", help="Nombre del archivo (si no se especifica, se genera automáticamente con fecha)")
    p.add_argument("-r", "--row", type=int, default=11, help="Fila del ALV a seleccionar (por defecto: 11)")
    p.add_argument("--date", help='Fecha para P_LFDAT-LOW (formato "dd.mm.yyyy"). Si se omite, usa AYER.')
    p.add_argument("--conn", type=int, default=0, help="Índice de conexión SAP (por defecto: 0)")
    p.add_argument("--sess", type=int, default=0, help="Índice de sesión SAP (por defecto: 0)")
    p.add_argument("--debug", action="store_true", help="Muestra diagnóstico de controles si hay fallos.")
    return p.parse_args()


def main():
    args = parse_args()
    date_str = args.date or (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    
    # Generar nombre de archivo con fecha si no se especifica
    if not args.filename:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        args.filename = f"rep_plr_{fecha_actual}.xls"
    
    # Asegurar que el directorio existe
    os.makedirs(args.output, exist_ok=True)

    print("INICIANDO SCRIPT REP_PLR")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Conexión={args.conn}, Sesión={args.sess}")
    print(f"Salida: {args.output}\\{args.filename} | Fila ALV: {args.row} | Fecha: {date_str}")
    print(f"Debug: {'ON' if args.debug else 'OFF'}")
    print("=" * 60)

    try:
        _, _, session = attach_to_sap(args.conn, args.sess)
        full_path = run_rep_plr(
            session,
            row_number=args.row,
            output_path=args.output,
            filename=args.filename,
            date_str=date_str,
            debug=args.debug,
        )
        print("\n" + "=" * 60)
        print("🎉 PROCESO REP_PLR COMPLETADO EXITOSAMENTE")
        print("=" * 60)
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
        # Si pidió --debug, ayudamos con inventario de controles
        if '--debug' in sys.argv:
            try:
                _, _, session = attach_to_sap(args.conn, args.sess)
                dump_controls(session, "wnd[0]")
            except Exception:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if '--debug' in sys.argv:
            try:
                _, _, session = attach_to_sap(args.conn, args.sess)
                dump_controls(session, "wnd[0]")
            except Exception:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()