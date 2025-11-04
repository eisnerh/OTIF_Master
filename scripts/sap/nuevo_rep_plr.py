# -*- coding: utf-8 -*-
"""
Script: nuevo_rep_plr_robusto.py
Autor: M365 Copilot para Eisner Lopez A
Descripción:
  - Conecta de forma robusta a SAP GUI Scripting.
  - Ejecuta la transacción zsd_rep_planeamiento, selecciona parámetros y exporta el reporte a XLS.
  - Post-procesa el archivo (HTML/XLS de SAP) y guarda versiones para Power BI (XLSX/CSV/Parquet).

Notas:
  - Requiere SAP GUI for Windows con Scripting habilitado.
  - Requiere paquetes: pywin32 (win32com), pandas, openpyxl (opcional para Excel), pyarrow/fastparquet (opcional para Parquet).

Ajusta la sección CONFIG según tu entorno.
"""

import os
import sys
import time
import re
from datetime import datetime

try:
    import win32com.client  # type: ignore
except Exception:
    win32com = None

import pandas as pd

# =========================== CONFIG ===========================
AFTER_HOUR = 14  # Ejecutar sólo si la hora actual es >= 14
CONNECTION_NAME = None  # p.ej. "PRD (ECC)". Si None, toma la primera sesión disponible
TCODE = "zsd_rep_planeamiento"

BASE_DIR = r"C:\Data\Nite"  # Carpeta base de trabajo
EXPORT_SUBDIR = "SAP_Document"
EXPORT_FILENAME = "REP_PLR_HOY.xls"  # SAP suele generar HTML con extensión .xls

POWERBI_BASE_NAME = "REP_PLR_HOY"
# ==============================================================

EXPORT_DIR = os.path.join(BASE_DIR, EXPORT_SUBDIR)
EXPORT_PATH = os.path.join(EXPORT_DIR, EXPORT_FILENAME)

EXCEL_OUT = os.path.join(BASE_DIR, f"{POWERBI_BASE_NAME}_PowerBI.xlsx")
CSV_OUT = os.path.join(BASE_DIR, f"{POWERBI_BASE_NAME}_PowerBI.csv")
PARQUET_OUT = os.path.join(BASE_DIR, f"{POWERBI_BASE_NAME}_PowerBI.parquet")

ENCODINGS_TO_TRY = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']

# ------------------------ Utilidades -------------------------

def ts_print(msg: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def get_sap_session(target_connection_name: str | None = None, wait_seconds: int = 15):
    """
    Devuelve (application, connection, session) de SAP GUI Scripting.
    Si target_connection_name es None, toma la primera conexión con al menos 1 sesión.
    """
    if win32com is None:
        raise RuntimeError("win32com (pywin32) no está disponible en este entorno.")

    try:
        sap_gui_auto = win32com.client.GetObject("SAPGUI")
    except Exception as e:
        raise RuntimeError("No se pudo obtener SAPGUI. ¿Está SAP Logon abierto?") from e

    try:
        application = sap_gui_auto.GetScriptingEngine
    except Exception as e:
        raise RuntimeError("No se pudo obtener el motor de Scripting. Verifica que el scripting esté habilitado en SAP GUI.") from e

    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        try:
            if application is None or application.Children.Count == 0:
                time.sleep(1)
                continue

            # Si se especificó un nombre de conexión, filtrarlo
            if target_connection_name:
                for i in range(application.Children.Count):
                    conn = application.Children(i)
                    name = getattr(conn, "Description", None) or getattr(conn, "Name", None) or f"(idx {i})"
                    if name and target_connection_name.lower() in str(name).lower():
                        if conn.Children.Count > 0:
                            return application, conn, conn.Children(0)
                        break  # espera a que aparezca la sesión
            else:
                # Tomar la primera conexión que tenga sesión
                for i in range(application.Children.Count):
                    conn = application.Children(i)
                    if conn.Children.Count > 0:
                        return application, conn, conn.Children(0)
        except Exception:
            pass
        time.sleep(1)

    # Diagnóstico si falla
    diag = [f"Conexiones encontradas: {getattr(application.Children, 'Count', 0)}"]
    try:
        for i in range(application.Children.Count):
            conn = application.Children(i)
            name = getattr(conn, "Description", None) or getattr(conn, "Name", f"(sin nombre idx {i})")
            diag.append(f"- [{i}] {name} | sesiones: {conn.Children.Count}")
    except Exception:
        pass
    raise RuntimeError("No se encontró una sesión activa de SAP.\n" + "\n".join(diag))

def wait_until_not_busy(session, timeout: int = 60):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if not session.Busy:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError("La sesión SAP sigue ocupada después de esperar.")

def safe_find(session, sid: str):
    try:
        return session.findById(sid)
    except Exception as e:
        raise RuntimeError(f"No se encontró el control SAP: {sid}") from e

# ---------------------- Automatización SAP -------------------

def run_tcode_and_export(session, tcode: str, export_full_path: str, report_date_yyyymmdd: str) -> None:
    """
    Ejecuta la transacción y exporta el reporte a export_full_path.
    Ajustado desde el guion original de Eisner.
    """
    wnd0 = safe_find(session, "wnd[0]")
    try:
        wnd0.maximize()
    except Exception:
        pass

    # Ir a la transacción
    ok = safe_find(session, "wnd[0]/tbar[0]/okcd")
    ok.text = tcode
    wnd0.sendVKey(0)
    wait_until_not_busy(session, timeout=60)

    # Abrir búsqueda (matchcode) del campo ENAME-LOW como en el script original
    try:
        safe_find(session, "wnd[0]/tbar[1]/btn[17]").press()
        wait_until_not_busy(session)

        txt = safe_find(session, "wnd[1]/usr/txtENAME-LOW")
        txt.text = ""
        txt.setFocus()
        txt.caretPosition = 0
        safe_find(session, "wnd[1]/tbar[0]/btn[8]").press()  # ejecutar búsqueda
        wait_until_not_busy(session)

        # Seleccionar fila 12 en ALV (validar que exista)
        alv = safe_find(session, "wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
        row_count = getattr(alv, 'RowCount', None)
        if row_count is None or row_count <= 12:
            raise RuntimeError(f"El ALV no tiene 13 filas para seleccionar. RowCount={row_count}")
        alv.currentCellRow = 18
        alv.selectedRows = "18"
        alv.doubleClickCurrentCell()
        wait_until_not_busy(session)
    except Exception as e:
        ts_print(f"⚠️ Aviso: No se pudo completar la selección por ALV exactamente como en el script original: {e}")
        ts_print("Se continuará con los siguientes pasos si la pantalla lo permite…")

    # Colocar fecha de entrega (matchcode calendario)
    try:
        fld = safe_find(session, "wnd[0]/usr/ctxtP_LFDAT-LOW")
        fld.setFocus()
        fld.caretPosition = 1
        wnd0.sendVKey(4)  # abrir calendario
        wait_until_not_busy(session)
        # calendario puede abrir en wnd[1] o wnd[2]
        cal = None
        for alt in ("wnd[1]/usr/cntlCONTAINER/shellcont/shell", "wnd[2]/usr/cntlCONTAINER/shellcont/shell"):
            try:
                cal = session.findById(alt)
                break
            except Exception:
                continue
        if cal is None:
            raise RuntimeError("No se encontró el control de calendario para seleccionar fecha.")
        cal.focusDate = report_date_yyyymmdd
        cal.selectionInterval = f"{report_date_yyyymmdd},{report_date_yyyymmdd}"
    except Exception as e:
        ts_print(f"⚠️ Aviso: No se pudo fijar la fecha mediante calendario: {e}. Intentando escribir la fecha directamente…")
        try:
            fld = safe_find(session, "wnd[0]/usr/ctxtP_LFDAT-LOW")
            # Convertir YYYYMMDD a DD.MM.YYYY si el campo espera ese formato
            ddmmyyyy = f"{report_date_yyyymmdd[6:8]}.{report_date_yyyymmdd[4:6]}.{report_date_yyyymmdd[0:4]}"
            fld.text = ddmmyyyy
        except Exception as e2:
            raise RuntimeError(f"No se pudo establecer la fecha de reporte: {e2}")

    # Ejecutar el reporte (F8)
    safe_find(session, "wnd[0]/tbar[1]/btn[8]").press()
    wait_until_not_busy(session)

    # Espera breve adicional por el ALV
    time.sleep(2)

    # Exportar a hoja de cálculo
    try:
        safe_find(session, "wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()  # Lista -> Exportar -> Hoja cálculo (puede variar)
    except Exception:
        # Alternativa: botón de exportar en la barra estándar (posiciones pueden variar)
        try:
            safe_find(session, "wnd[0]/tbar[0]/btn[45]").press()
        except Exception as e:
            raise RuntimeError("No se pudo abrir el diálogo de exportación de hoja de cálculo.") from e

    # Seleccionar formato de exportación (Spreadsheet)
    try:
        safe_find(session, "wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        safe_find(session, "wnd[1]/tbar[0]/btn[0]").press()
    except Exception:
        # Algunos sistemas muestran directamente el diálogo de archivo
        pass
    # Especificar carpeta/archivo
    # A veces el diálogo de ruta es wnd[1], a veces wnd[2]
    path_ok = False
    for w in ("wnd[1]", "wnd[2]"):
        try:
            base_dir = os.path.dirname(export_full_path)
            fname = os.path.basename(export_full_path)
            dy_path = session.findById(f"{w}/usr/ctxtDY_PATH")
            dy_path.text = base_dir
            try:
                dy_path.setFocus()
                dy_path.caretPosition = 0
            except Exception:
                pass
            # Abrir diálogo de nombre de archivo
            session.findById(f"{w}").sendVKey(4)
            # El nombre y encoding suelen estar en la siguiente ventana
            w2 = "wnd[2]" if w == "wnd[1]" else "wnd[3]"
            try:
                session.findById(f"{w2}/usr/ctxtDY_FILENAME").text = fname
                try:
                    session.findById(f"{w2}/usr/ctxtDY_FILE_ENCODING").text = "0000"
                except Exception:
                    pass
                session.findById(f"{w2}/tbar[0]/btn[0]").press()
            except Exception:
                # Si no aparece una ventana extra, intentemos escribir directo en la misma
                try:
                    session.findById(f"{w}/usr/ctxtDY_FILENAME").text = fname
                except Exception:
                    pass
            # Confirmar guardado
            session.findById(f"{w}/tbar[0]/btn[0]").press()
            path_ok = True
            break
        except Exception:
            continue

    if not path_ok:
        raise RuntimeError("No se pudo establecer la ruta/archivo en el diálogo de exportación.")

    ts_print(f"Exportación solicitada a: {export_full_path}")
    # Pequeña espera para que SAP escriba el archivo
    time.sleep(3)

# -------------------- Post-proceso Power BI ------------------

def read_text_file_any_encoding(path: str) -> str | None:
    for enc in ENCODINGS_TO_TRY:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return None

def parse_tab_delimited_to_df(content: str) -> pd.DataFrame | None:
    # Separar por líneas y detectar encabezado por palabras comunes del reporte
    lines = [ln.strip('\n') for ln in content.splitlines()]
    header_idx = None
    for i, ln in enumerate(lines):
        if ('Centro' in ln and 'Fe.Entrega' in ln and 'Ruta' in ln) or ('Centro' in ln and 'Pedido' in ln):
            header_idx = i
            break
    if header_idx is None:
        # fallback: buscar la primera línea con muchos tabs
        for i, ln in enumerate(lines):
            if ln.count('\t') >= 4:
                header_idx = i
                break
    if header_idx is None:
        return None

    headers = [c.strip() for c in lines[header_idx].split('\t')]

    data_rows = []
    for ln in lines[header_idx + 1:]:
        if not ln.strip():
            continue
        # omitir líneas que sean títulos de fecha estilo "19.09.2025" solas
        if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", ln.strip()):
            continue
        parts = ln.split('\t')
        if len(parts) < len(headers):
            # completar con vacíos si la fila es más corta
            parts += [""] * (len(headers) - len(parts))
        data_rows.append(parts[:len(headers)])

    df = pd.DataFrame(data_rows, columns=headers)
    # Limpiezas básicas
    df.replace({'\u00A0': ' '}, regex=True, inplace=True)  # NBSP
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def process_exported_file_to_df(path: str) -> pd.DataFrame:
    content = read_text_file_any_encoding(path)
    if content is None:
        raise RuntimeError("No se pudo leer el archivo exportado con ninguna codificación probada.")

    if content.lstrip().startswith('<'):
        ts_print("Detectado HTML con extensión XLS. Intentando leer tablas HTML…")
        # Intentar con varias codificaciones
        tables = None
        for enc in ENCODINGS_TO_TRY:
            try:
                tables = pd.read_html(path, encoding=enc)
                if tables:
                    break
            except Exception:
                continue
        if not tables:
            raise RuntimeError("No se pudieron leer tablas HTML del archivo exportado.")
        df = tables[0]
        # Limpiezas
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, know='all', inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    else:
        ts_print("Procesando como texto/tab-delimited de SAP…")
        df = parse_tab_delimited_to_df(content)
        if df is None:
            raise RuntimeError("No se pudo interpretar el contenido tab-delimited del archivo SAP.")
        return df

def transform_data_for_powerbi(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Normalizar nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]

    # Ejemplos de transformaciones comunes (ajusta según tus columnas reales):
    # Convertir columnas de fecha si existen
    for col in df.columns:
        if re.search(r"fe(\.|\s|_)?entrega|fecha", col, flags=re.IGNORECASE):
            try:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
            except Exception:
                pass
    # Quitar espacios
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    return df

def save_powerbi_files(df: pd.DataFrame, excel_path: str, csv_path: str, parquet_path: str) -> None:
    # Excel
    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos")
        ts_print(f"✅ Guardado Excel: {excel_path}")
    except Exception as e:
        ts_print(f"⚠️ No se pudo guardar Excel: {e}")

    # CSV
    try:
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        ts_print(f"✅ Guardado CSV: {csv_path}")
    except Exception as e:
        ts_print(f"⚠️ No se pudo guardar CSV: {e}")

    # Parquet
    try:
        df.to_parquet(parquet_path, index=False)
        ts_print(f"✅ Guardado Parquet: {parquet_path}")
    except Exception as e:
        ts_print(f"⚠️ No se pudo guardar Parquet: {e}")

# --------------------------- MAIN ----------------------------

def main(force_run: bool = False):
    # Ventana horaria
    current_hour = datetime.now().hour
    if not force_run and current_hour < AFTER_HOUR:
        ts_print(f"La hora actual es {current_hour}:00. El script corre a partir de las {AFTER_HOUR}:00. Saliendo…")
        return 0

    today_sap = datetime.today().strftime('%Y%m%d')

    # Preparar carpetas
    ensure_dir(EXPORT_DIR)
    ensure_dir(BASE_DIR)

    # Limpiar archivo previo
    if os.path.exists(EXPORT_PATH):
        try:
            os.remove(EXPORT_PATH)
        except Exception:
            pass

    # Conectar a SAP
    ts_print("Conectando a SAP GUI Scripting…")
    application, connection, session = get_sap_session(CONNECTION_NAME, wait_seconds=20)

    # Ejecutar transacción y exportar
    ts_print(f"Ejecutando transacción {TCODE}…")
    run_tcode_and_export(session, TCODE, EXPORT_PATH, today_sap)

    if not os.path.exists(EXPORT_PATH):
        raise RuntimeError(f"El archivo exportado no se encontró: {EXPORT_PATH}")

    ts_print("Leyendo y transformando archivo exportado…")
    df = process_exported_file_to_df(EXPORT_PATH)
    df = transform_data_for_powerbi(df)

    ts_print("Guardando salidas para Power BI…")
    save_powerbi_files(df, EXCEL_OUT, CSV_OUT, PARQUET_OUT)

    ts_print("✅ Proceso completado correctamente.")
    return 0

if __name__ == "__main__":
    force = False
    # Permitir ejecutar con --force para ignorar la hora
    if any(arg in ("--force", "-f") for arg in sys.argv[1:]):
        force = True
    try:
        sys.exit(main(force_run=force))
    except Exception as e:
        ts_print(f"❌ Error: {e}")
        sys.exit(1)