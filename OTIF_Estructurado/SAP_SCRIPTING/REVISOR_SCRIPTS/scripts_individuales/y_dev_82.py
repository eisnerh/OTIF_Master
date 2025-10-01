#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatiza la transacción Y_DEV_82 (y_dev_42000082) y exporta a Excel usando SAP GUI Scripting (COM).
Incluye retorno automático a SAP Easy Access al finalizar.

Requisitos:
  - SAP GUI Scripting habilitado en cliente y servidor.
  - pywin32 instalado: pip install pywin32
  - SAP Logon abierto y sesión activa.

Uso (ejemplo):
  python y_dev_82.py --output "C:\\data" --filename "y_dev_82.xls" --row 2 --conn 0 --sess 0
"""

import os
import sys
import time
import argparse
from datetime import datetime

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


def select_tree_node(session, node_key: str):
    tree_id = "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell"
    tree = find(session, tree_id)
    tree.selectedNode = node_key
    tree.doubleClickNode(node_key)


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


def run_y_dev_82(session, row_number: int, output_path: str, filename: str, encoding: str = "0000"):
    """
    Flujo basado en tu configuración:
      - tcode y_dev_42000082 -> nodo F00139
      - botón selección -> limpiar ENAME-LOW -> buscar -> ALV (fila) -> doble clic
      - ejecutar -> exportar -> guardar
    """
    # 1) Ir a la transacción
    send_tcode(session, "y_dev_42000082")  # de tu archivo adjunto [3](https://florida1-my.sharepoint.com/personal/elopez21334_fifco_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/y_dev_82.py)

    # 2) Seleccionar nodo del árbol y abrir
    select_tree_node(session, "F00139")    # de tu archivo adjunto [3](https://florida1-my.sharepoint.com/personal/elopez21334_fifco_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/y_dev_82.py)

    # 3) Botón de selección
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
    alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    alv.currentCellRow = row_number
    alv.selectedRows = str(row_number)
    alv.doubleClickCurrentCell()

    # 6) Ejecutar reporte
    find(session, "wnd[0]/tbar[1]/btn[8]").press()

    # 7) Exportar: Menú -> Hoja de cálculo
    find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()

    # 8) Selector de formato (radio [1,0]) y continuar
    rb = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
    find(session, rb).select()
    find(session, "wnd[1]/tbar[0]/btn[0]").press()

    # 9) Guardado
    ensure_dir(output_path)
    full_path = os.path.join(output_path, filename)
    
    # Eliminar archivo si ya existe para evitar conflictos
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except PermissionError:
            # Si no se puede eliminar por permisos, intentar con nombre único
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

    # 10) Pop-ups
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")

    # 11) Verificación local
    if not os.path.isfile(full_path):
        raise SAPGuiError(f"El archivo no se generó: {full_path}")

    # === CALL: volver a SAP Easy Access
    go_to_easy_access(session)

    return full_path


def parse_args():
    p = argparse.ArgumentParser(description="Ejecuta Y_DEV_82 y exporta a Excel (standalone).")
    p.add_argument("-o", "--output", default=r"C:\data\y_dev_82", help="Ruta de salida (por defecto: C:\\data\\y_dev_82)")
    p.add_argument("-f", "--filename", help="Nombre del archivo (si no se especifica, se genera automáticamente con fecha)")
    p.add_argument("-r", "--row", type=int, default=2, help="Fila del ALV a seleccionar (por defecto: 2)")
    p.add_argument("--conn", type=int, default=0, help="Índice de conexión SAP (por defecto: 0)")
    p.add_argument("--sess", type=int, default=0, help="Índice de sesión SAP (por defecto: 0)")
    return p.parse_args()


def main():
    args = parse_args()
    
    # Generar nombre de archivo con fecha si no se especifica
    if not args.filename:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        args.filename = f"y_dev_82_{fecha_actual}.xls"
    
    # Asegurar que el directorio existe
    os.makedirs(args.output, exist_ok=True)

    print("INICIANDO SCRIPT Y_DEV_82")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Conexión={args.conn}, Sesión={args.sess}")
    print(f"Salida: {args.output}\\{args.filename} | Fila ALV: {args.row}")
    print("=" * 60)

    try:
        _, _, session = attach_to_sap(args.conn, args.sess)
        full_path = run_y_dev_82(
            session,
            row_number=args.row,
            output_path=args.output,
            filename=args.filename,
        )
        print("\n" + "=" * 60)
        print("🎉 PROCESO Y_DEV_82 COMPLETADO EXITOSAMENTE")
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
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()