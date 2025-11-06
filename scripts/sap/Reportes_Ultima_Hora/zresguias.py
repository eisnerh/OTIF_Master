# -*- coding: utf-8 -*-
"""
ZRESGUIAS (homologado)
----------------------
• Patrón robusto (find()/timeouts), autodetección de conexión/sesión (--conn -1, --sess -1),
  manejo de pop-ups y retorno a SAP Easy Access.
• Flujo: zresguias → Selección → limpiar ENAME-LOW → buscar → ALV fila 26 (por defecto)
  → fecha PFECHA-LOW **SIEMPRE AYER** (dd.mm.yyyy) por calendario F4 (o escritura directa con --no-calendar)
  → Ejecutar → Exportar → Guardar → Verificar → Volver a SAP Easy Access.
• Exporta por Menú → Hoja de cálculo (formato [1,0]); encoding por defecto 0000.

Ejemplos:
  python zresguias.py --debug
  python zresguias.py --row 26 -o "C:\\data\\SAP_Extraction\\Zresguias" -f "Zresguias_05-10-2025.xls"
  python zresguias.py --no-calendar  # escribe la fecha en el campo sin abrir calendario
"""
import os
import sys
import time
import argparse
from datetime import datetime, timedelta

try:
    import win32com.client  # type: ignore
except ImportError:
    print(" Falta pywin32. Instala con: pip install pywin32")
    sys.exit(1)

class SAPGuiError(Exception):
    pass

# ------------------------------ utilidades base --------------------------------
def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def attach_to_sap(connection_index: int = -1, session_index: int = -1):
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

# ------------------------------ helpers de fecha -------------------------------

def set_date_text(session, field_id: str, date_str: str):
    ctrl = find(session, f"wnd[0]/usr/ctxt{field_id}")
    ctrl.text = date_str
    try:
        ctrl.setFocus()
        ctrl.caretPosition = len(date_str)
    except Exception:
        pass


def set_date_calendar(session, field_id: str, date_str: str):
    # Convertir dd.mm.yyyy -> yyyymmdd
    try:
        d = datetime.strptime(date_str, "%d.%m.%Y")
        ymd = d.strftime("%Y%m%d")
    except ValueError:
        raise SAPGuiError(f"Fecha inválida: {date_str}. Usa formato dd.mm.yyyy")

    fld = find(session, f"wnd[0]/usr/ctxt{field_id}")
    try:
        fld.setFocus(); fld.caretPosition = 1
    except Exception:
        pass
    find(session, "wnd[0]").sendVKey(4)  # F4

    cal_id = "wnd[1]/usr/cntlCONTAINER/shellcont/shell"
    cal = find(session, cal_id)
    try:
        cal.focusDate = ymd
        cal.selectionInterval = f"{ymd},{ymd}"
    except Exception:
        cal.focusDate = ymd
    press_if_exists(session, "wnd[1]/tbar[0]/btn[0]")

# ------------------------------ flujo ZRESGUIAS --------------------------------

def run_zresguias(session,
                  row_number: int,
                  output_path: str,
                  filename: str,
                  date_str: str,
                  encoding: str = "0000",
                  use_calendar: bool = True,
                  debug: bool = False):
    # 1) Ir a ZRESGUIAS
    send_tcode(session, "zresguias")

    # 2) Botón de selección
    if press_if_exists(session, "wnd[0]/tbar[1]/btn[17]") is False and debug:
        print(" No se encontró el botón de selección [17]; puede que ya estés en la dynpro de selección.")

    # 3) Pop-up: limpiar ENAME-LOW y buscar
    ename = find(session, "wnd[1]/usr/txtENAME-LOW")
    ename.text = ""
    try:
        ename.setFocus(); ename.caretPosition = 0
    except Exception:
        pass
    find(session, "wnd[1]/tbar[0]/btn[8]").press()

    # 4) Seleccionar fila en ALV y doble clic (con scroll)
    alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    try:
        if row_number > 10:
            alv.firstVisibleRow = max(row_number - 14, 0)
    except Exception:
        pass
    alv.currentCellRow = row_number
    alv.selectedRows = str(row_number)
    alv.doubleClickCurrentCell()

    # 5) Fecha en PFECHA-LOW (siempre AYER)
    if use_calendar:
        set_date_calendar(session, "PFECHA-LOW", date_str)
    else:
        set_date_text(session, "PFECHA-LOW", date_str)

    # 6) Ejecutar
    find(session, "wnd[0]/tbar[1]/btn[8]").press()

    # 7) Exportar: Menú -> Hoja de cálculo
    find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
    rb = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
    find(session, rb).select()
    find(session, "wnd[1]/tbar[0]/btn[0]").press()

    # 8) Guardar
    ensure_dir(output_path)
    if filename and '.' not in filename:
        filename = filename + '.xls'
    full_path = os.path.join(output_path, filename)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except PermissionError:
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{datetime.now().strftime('%H%M%S')}{ext or '.xls'}"
            full_path = os.path.join(output_path, filename)

    find(session, "wnd[1]/usr/ctxtDY_PATH").text = output_path
    find(session, "wnd[1]/usr/ctxtDY_FILENAME").text = filename
    enc = find(session, "wnd[1]/usr/ctxtDY_FILE_ENCODING")
    enc.text = encoding
    try:
        enc.setFocus(); enc.caretPosition = len(encoding)
    except Exception:
        pass
    find(session, "wnd[1]/tbar[0]/btn[11]").press()

    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")

    if not os.path.isfile(full_path):
        if debug:
            dump_controls(session, "wnd[0]")
        press_if_exists(session, "wnd[0]/tbar[0]/btn[3]")
        raise SAPGuiError(f"El archivo no se generó: {full_path}")

    go_to_easy_access(session)
    return full_path

# ----------------------------------- CLI ---------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Ejecuta ZRESGUIAS y exporta a Excel (homologado; fecha SIEMPRE AYER).")
    p.add_argument("-r", "--row", type=int, default=26, help="Fila del ALV a seleccionar (por defecto: 26)")
    p.add_argument("-o", "--output", default=r"C:\\data\\SAP_Extraction\\Zresguias", help="Ruta de salida (por defecto: C:\\data\\SAP_Extraction\\Zresguias)")
    p.add_argument("-f", "--filename", help="Nombre del archivo (si no se especifica, se genera automáticamente con fecha)")
    p.add_argument("--encoding", default="0000", help='Codificación de archivo (DY_FILE_ENCODING).')
    p.add_argument("--conn", type=int, default=-1, help="Índice de conexión SAP (-1 = auto)")
    p.add_argument("--sess", type=int, default=-1, help="Índice de sesión SAP (-1 = auto)")
    p.add_argument("--debug", action="store_true", help="Muestra diagnóstico de controles si hay fallos.")
    p.add_argument("--no-calendar", action="store_true", help="NO abrir calendario; escribe la fecha en el campo.")
    return p.parse_args()


def main():
    args = parse_args()

    # FECHA FORZADA = AYER (dd.mm.yyyy)
    date_str = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

    if not args.filename:
        hoy = datetime.now().strftime('%d-%m-%Y')
        args.filename = f"Zresguias_{hoy}.xls"

    ensure_dir(args.output)

    print("INICIANDO SCRIPT ZRESGUIAS (HOMOLOGADO)")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        _, _, session, resolved_conn, resolved_sess = attach_to_sap(args.conn, args.sess)
        print(f"Conexión={resolved_conn}, Sesión={resolved_sess}")
        print(f"ALV Row: {args.row} | Fecha (AYER): {date_str}")
        print(f"Salida: {args.output}\\{args.filename}")
        print(f"Modo fecha: {'CALENDARIO' if not args.no_calendar else 'ESCRITURA DIRECTA'}")
        print(f"Debug: {'ON' if args.debug else 'OFF'}")
        print("=" * 60)

        full_path = run_zresguias(
            session=session,
            row_number=args.row,
            output_path=args.output,
            filename=args.filename,
            date_str=date_str,
            encoding=args.encoding,
            use_calendar=(not args.no_calendar),
            debug=args.debug,
        )

        print("\n" + "=" * 60)
        print(" PROCESO ZRESGUIAS COMPLETADO")
        print("=" * 60)
        print(f" Archivo generado: {os.path.basename(full_path)}")
        print(f" Ubicación: {os.path.dirname(full_path)}")
        print(f" Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n Script interrumpido por el usuario"); sys.exit(1)
    except SAPGuiError as e:
        print(f" Error SAP: {e}")
        if args.debug:
            try:
                _, _, session, _, _ = attach_to_sap(args.conn, args.sess)
                dump_controls(session, "wnd[0]")
            except Exception:
                pass
        sys.exit(1)
    except Exception as e:
        print(f" Error inesperado: {e}")
        if args.debug:
            try:
                _, _, session, _, _ = attach_to_sap(args.conn, args.sess)
                dump_controls(session, "wnd[0]")
            except Exception:
                pass
        sys.exit(1)

if __name__ == "__main__":
    main()
