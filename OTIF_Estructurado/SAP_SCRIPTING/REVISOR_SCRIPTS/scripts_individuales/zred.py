#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatiza la transacción ZRED (Reporte de Red) y exporta a Excel usando SAP GUI Scripting (COM).
No requiere 'BaseSAPScript'. Probado con IDs basados en tu VBScript.

Requisitos:
  - SAP GUI Scripting habilitado en cliente y servidor.
  - pywin32 instalado: pip install pywin32
  - SAP Logon abierto y sesión activa.

Uso:
  python zred.py --output "C:\\data" --filename "zred.xls" --row 1 --conn 0 --sess 0
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
    
import uuid

def ensure_output_dir(path: str) -> str:
    """
    Garantiza que 'path' sea un directorio válido.
    - Si existe como carpeta: OK.
    - Si no existe: la crea.
    - Si existe como ARCHIVO: crea una carpeta alternativa (path + '_OUT' o con sufijo único).
    Devuelve siempre la ruta de carpeta usable.
    """
    if os.path.isdir(path):
        return path

    if os.path.isfile(path):
        base_dir, name = os.path.split(path)
        alt = os.path.join(base_dir, f"{name}_OUT")
        # Evitar colisiones repetidas
        if os.path.exists(alt) and not os.path.isdir(alt):
            alt = os.path.join(base_dir, f"{name}_OUT_{uuid.uuid4().hex[:6]}")
        os.makedirs(alt, exist_ok=True)
        print(f"⚠️ Aviso: '{path}' es un archivo. Usaré la carpeta alternativa: {alt}")
        return alt

    # No existe: crear carpeta objetivo
    os.makedirs(path, exist_ok=True)
    return path


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
        raise SAPGuiError(f"No existe la conexión index={connection_index}. Verifica que SAP está conectado.")

    try:
        session = connection.Children(session_index)
    except Exception:
        raise SAPGuiError(f"No existe la sesión index={session_index}. Abre la sesión en SAP.")

    return application, connection, session


def find(session, obj_id, timeout=10.0, interval=0.2):
    """Espera hasta encontrar un control por ID."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            return session.FindById(obj_id)
        except Exception:
            time.sleep(interval)
    raise SAPGuiError(f"No se encontró el control: {obj_id}")


def exists(session, obj_id):
    """Devuelve True si existe el ID, sin excepciones."""
    try:
        session.FindById(obj_id)
        return True
    except Exception:
        return False


def press_if_exists(session, obj_id):
    """Presiona un botón si existe (útil para confirmaciones/sobrescritura)."""
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

# === NEW: volver a SAP Easy Access ===========================================
def go_to_easy_access(session):
    """
    Vuelve a la pantalla inicial de SAP (SAP Easy Access).
    Maneja pop-ups genéricos si aparecen (confirmaciones).
    """
    ok = find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = "/n"
    find(session, "wnd[0]").sendVKey(0)  # Enter

    # Pop-ups comunes: Sí/Continuar/Aceptar
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")   # Sí/Continuar
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")  # Guardar/Aceptar
        press_if_exists(session, f"wnd[{wnd_index}]/usr/btnSPOP-OPTION1")  # 'Sí' alternativo
# ==============================================================================


def run_zred(session, row_number: int, output_path: str, filename: str, encoding: str = "0000"):
    """
    Ejecuta ZRED con la secuencia equivalente a tu VBScript y exporta a Excel.
    row_number: fila a seleccionar en el ALV del pop-up (1 = primera).
    """
    # 1) Ir a ZRED
    send_tcode(session, "zred")

    # 2) Botón de selección (como en tu script: tbar[1]/btn[17])
    find(session, "wnd[0]/tbar[1]/btn[17]").press()

    # 3) En el pop-up, seleccionar fila en ALV y doble clic
    alv = find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    # Ajuste: ALV suele ser base-0 en algunas propiedades; tu VBScript usa "1".
    # Mantendremos la misma lógica:
    alv.currentCellRow = row_number
    alv.selectedRows = str(row_number)
    try:
        alv.doubleClickCurrentCell()
    except Exception:
        # Alternativa: alv.doubleClick(row_number, "<colname>") si fuera necesario
        raise

    # 4) Ejecutar reporte (tbar[1]/btn[8])
    find(session, "wnd[0]/tbar[1]/btn[8]").press()

    # 5) Exportar: Menú -> Hoja de cálculo (mbar/menu[0]/menu[3]/menu[2])
    # Ojo: estos índices pueden variar si el menú cambia; están tomados de tu VBScript.
    find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()

    # 6) Seleccionar formato en el selector de SAPLSPO5 (radio button [1,0])
    # En algunos entornos, puede ser [0,0] o [2,0]; ajusta si el formato cambia.
    rb = "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
    find(session, rb).select()
    find(session, "wnd[1]/tbar[0]/btn[0]").press()  # Continuar

    # 7) Rellenar ruta, archivo y codificación
    ensure_dir(output_path)
    full_path = os.path.join(output_path, filename)

    # Si aparece un diálogo de selección de ruta/archivo:
    # En tu VBScript eran estos IDs:
    find(session, "wnd[1]/usr/ctxtDY_PATH").text = output_path
    find(session, "wnd[1]/usr/ctxtDY_FILENAME").text = filename
    enc = find(session, "wnd[1]/usr/ctxtDY_FILE_ENCODING")
    enc.text = encoding
    try:
        enc.setFocus()
        enc.caretPosition = len(encoding)
    except Exception:
        pass

    # Guardar
    find(session, "wnd[1]/tbar[0]/btn[11]").press()

    # 8) Manejo de posibles pop-ups (sobrescribir, información, etc.)
    # Aceptar "Sí" si pregunta sobre sobrescritura (IDs pueden variar según idioma/versión)
    # Intento genérico: si hay wnd[2] con botón [0] (Sí/Aceptar)
    for wnd_index in (2, 1):
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[0]")  # Sí / Continuar
        press_if_exists(session, f"wnd[{wnd_index}]/tbar[0]/btn[11]")  # Guardar/Aceptar

    # 9) Verificación local (archivo creado)
    if not os.path.isfile(full_path):
        raise SAPGuiError(f"El archivo no se generó: {full_path}")
    
    # ==== CALL: volver a SAP Easy Access
    go_to_easy_access(session)

    return full_path


def parse_args():
    p = argparse.ArgumentParser(description="Ejecuta ZRED y exporta el reporte a Excel (standalone).")
    p.add_argument("-o", "--output", default=r"C:\data\zred", help="Ruta de salida (por defecto: C:\\data\\zred)")
    p.add_argument("-f", "--filename", help="Nombre del archivo (si no se especifica, se genera automáticamente con fecha)")
    p.add_argument("-r", "--row", type=int, default=1, help="Fila del ALV a seleccionar (por defecto: 1)")
    p.add_argument("--conn", type=int, default=0, help="Índice de conexión SAP (por defecto: 0)")
    p.add_argument("--sess", type=int, default=0, help="Índice de sesión SAP (por defecto: 0)")
    return p.parse_args()


def main():
    args = parse_args()
    
    # Generar nombre de archivo con fecha si no se especifica
    if not args.filename:
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        args.filename = f"zred_{fecha_actual}.xls"
    
    # Asegurar que el directorio existe
    os.makedirs(args.output, exist_ok=True)

    print("INICIANDO SCRIPT ZRED")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Conexión={args.conn}, Sesión={args.sess}")
    print(f"Salida: {args.output}\\{args.filename}")
    print("=" * 60)

    try:
        application, connection, session = attach_to_sap(args.conn, args.sess)
        full_path = run_zred(session, row_number=args.row, output_path=args.output, filename=args.filename)
        print("\n" + "=" * 60)
        print("🎉 PROCESO ZRED COMPLETADO EXITOSAMENTE")
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