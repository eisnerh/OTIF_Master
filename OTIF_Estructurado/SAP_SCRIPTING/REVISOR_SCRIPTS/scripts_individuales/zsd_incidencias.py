import os
import sys
import time
import argparse
from datetime import datetime

try:
    import win32com.client  # type: ignore
except ImportError:
    print("❌ Falta pywin32. Instala con: pip install pywin32")
    # No salimos aquí porque el archivo podría ser solo para lectura/descarga.


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
        print(f"⚠️ Error al limpiar la sesión SAP: {e}")


def attach_to_sap(connection_index: int = -1, session_index: int = -1):
    """Adjunta a SAP GUI. Si connection_index o session_index < 0, toma la última disponible.
    Devuelve: (application, connection, session, resolved_conn, resolved_sess)
    """
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


def go_to_easy_access(session):
    ok = find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = "/n"
    find(session, "wnd[0]").sendVKey(0)
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")
        press_if_exists(session, f"wnd[{wnd_index}]/usr/btnSPOP-OPTION1")


# ------------------------------ flujo ZSD_INCIDENCIAS ---------------------------
def export_with_fallback(session, output_path: str, filename: str, encoding: str = "0000"):
    """Guarda el archivo usando el diálogo estándar (wnd[1]) y si no funciona, usa el
    mecanismo tipo NITE (F4 -> wnd[2])."""
    # Intento estándar (todo en wnd[1])
    try:
        find(session, "wnd[1]/usr/ctxtDY_PATH").text = output_path
        find(session, "wnd[1]/usr/ctxtDY_FILENAME").text = filename
        enc = find(session, "wnd[1]/usr/ctxtDY_FILE_ENCODING")
        enc.text = encoding
        try:
            enc.setFocus(); enc.caretPosition = len(encoding)
        except Exception:
            pass
        find(session, "wnd[1]/tbar[0]/btn[11]").press()  # Guardar
        return True
    except Exception:
        pass

    # Fallback estilo NITE (F4 para abrir selector en wnd[2])
    try:
        find(session, "wnd[1]/usr/ctxtDY_PATH").text = output_path
        find(session, "wnd[1]").sendVKey(4)  # F4
        find(session, "wnd[2]/usr/ctxtDY_FILENAME").text = filename
        find(session, "wnd[2]/usr/ctxtDY_FILE_ENCODING").text = encoding
        try:
            f = find(session, "wnd[2]/usr/ctxtDY_FILENAME")
            f.setFocus(); f.caretPosition = len(filename)
        except Exception:
            pass
        find(session, "wnd[2]/tbar[0]/btn[0]").press()  # Continuar
        # En algunos entornos, hay que confirmar otra vez en wnd[1]
        press_if_exists(session, "wnd[1]/tbar[0]/btn[0]")
        press_if_exists(session, "wnd[1]/tbar[0]/btn[11]")
        return True
    except Exception:
        return False


def run_zsd_incidencias(session, row_number: int, output_path: str, filename: str,
                         encoding: str = "0000", debug: bool = False):
    # 0) Limpiar sesión SAP antes de comenzar
    limpiar_sesion_sap(session)
    
    # 1) Ir a la transacción
    send_tcode(session, "zsd_incidencias")

    # 2) Botón de selección (si aplica)
    if press_if_exists(session, "wnd[0]/tbar[1]/btn[17]") is False and debug:
        print("ℹ️ No se encontró el botón de selección [17]; puede que ya estés en la dynpro de selección.")

    # 3) Limpiar ENAME-LOW y Buscar
    ename = find(session, "wnd[1]/usr/txtENAME-LOW")
    ename.text = ""
    try:
        ename.setFocus(); ename.caretPosition = 0
    except Exception:
        pass
    find(session, "wnd[1]/tbar[0]/btn[8]").press()

    # 4) Seleccionar fila en ALV y doble clic (con posible scroll)
    alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    try:
        if row_number > 10:
            alv.firstVisibleRow = max(row_number - 10, 0)
    except Exception:
        pass
    alv.currentCellRow = row_number
    alv.selectedRows = str(row_number)
    alv.doubleClickCurrentCell()

    # 5) Ejecutar reporte
    find(session, "wnd[0]/tbar[1]/btn[8]").press()

    # 6) Exportar a Excel (menú -> hoja de cálculo)
    find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()

    # 7) Selector de formato SAPLSPO5 (radio [1,0]) y continuar
    rb = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
    find(session, rb).select()
    find(session, "wnd[1]/tbar[0]/btn[0]").press()

    # 8) Guardado con fallback
    ensure_dir(output_path)
    full_path = os.path.join(output_path, filename)

    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except PermissionError:
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{datetime.now().strftime('%H%M%S')}{ext}"
            full_path = os.path.join(output_path, filename)

    ok = export_with_fallback(session, output_path, filename, encoding=encoding)
    if not ok:
        raise SAPGuiError("No se pudo completar el guardado (estándar ni fallback)")

    # 9) Pop-ups comunes (sobrescritura, avisos)
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")

    # 10) Verificación local
    if not os.path.isfile(full_path):
        if debug:
            dump_controls(session, "wnd[0]")
        press_if_exists(session, "wnd[0]/tbar[0]/btn[3]")
        raise SAPGuiError(f"El archivo no se generó: {full_path}")

    # 11) Volver a SAP Easy Access
    go_to_easy_access(session)

    return full_path


# ----------------------------------- CLI ---------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Ejecuta ZSD_INCIDENCIAS y exporta a Excel (homologado).")
    p.add_argument("-r", "--row", type=int, default=12, help="Fila del ALV a seleccionar (por defecto: 12)")
    p.add_argument("-o", "--output", default=r"C:\\data\\SAP_Extraction\\zsd_incidencias", help="Ruta de salida (por defecto: C:\\data\\SAP_Extraction\\zsd_incidencias)")
    p.add_argument("-f", "--filename", help="Nombre del archivo (si no se especifica, se genera automáticamente con fecha)")
    p.add_argument("--encoding", default="0000", help="Codificación de archivo (campo DY_FILE_ENCODING)")
    p.add_argument("--conn", type=int, default=-1, help="Índice de conexión SAP (-1 = auto)")
    p.add_argument("--sess", type=int, default=-1, help="Índice de sesión SAP (-1 = auto)")
    p.add_argument("--debug", action="store_true", help="Muestra diagnóstico de controles si hay fallos")
    return p.parse_args()


def main():
    args = parse_args()

    if not args.filename:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        args.filename = f"zsd_incidencias_{fecha_actual}.xls"

    ensure_dir(args.output)

    print("INICIANDO SCRIPT ZSD_INCIDENCIAS (HOMOLOGADO)")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        _, _, session, resolved_conn, resolved_sess = attach_to_sap(args.conn, args.sess)
        print(f"Conexión={resolved_conn}, Sesión={resolved_sess}")
        print(f"ALV Row: {args.row}")
        print(f"Salida: {args.output}\\{args.filename}")
        print(f"Debug: {'ON' if args.debug else 'OFF'}")
        print("=" * 60)

        full_path = run_zsd_incidencias(
            session,
            row_number=args.row,
            output_path=args.output,
            filename=args.filename,
            encoding=args.encoding,
            debug=args.debug,
        )

        print("\n" + "=" * 60)
        print("🎉 PROCESO ZSD_INCIDENCIAS COMPLETADO")
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