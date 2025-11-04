
# -*- coding: utf-8 -*-
"""
Script: amalgama_y_dev_74_quicktest.py (Opción A)
Descripción:
  - Ejecuta una corrida única: conecta a SAP, exporta TXT, espera 3s + confirmación del archivo,
    genera Excel (_processed.xlsx), elimina las primeras 5 filas y sobrescribe el mismo Excel.
  - Pensado para programarse con el Programador de Tareas de Windows (cada hora, 14:00–22:00).

ADVERTENCIA DE SEGURIDAD:
  Este archivo contiene credenciales embebidas SOLO para pruebas locales.
  Evita subirlo a repositorios y rota la contraseña si fue expuesta.
"""
from __future__ import annotations

import os
import sys
import time
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import configparser
import pandas as pd

# Agregar el directorio padre al sys.path para poder importar y_dev_74
SCRIPT_DIR = Path(__file__).parent
PARENT_DIR = SCRIPT_DIR.parent  # scripts/sap/
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

def load_credentials() -> dict:
    """Carga credenciales desde credentials.ini ubicado junto a este script.

    Formato esperado:
    [AUTH]
    sap_system = SAP R/3 Productivo [FIFCOR3]
    sap_client = 700
    sap_user = usuario
    sap_password = contraseña
    sap_language = ES
    """
    config = configparser.ConfigParser()
    creds_path = Path(__file__).parent / "credentials.ini"
    if not creds_path.exists():
        raise FileNotFoundError(
            f"No se encontró '{creds_path}'. Crea el archivo a partir de 'credentials.ini.example'."
        )
    config.read(creds_path, encoding="utf-8")
    if "AUTH" not in config:
        raise ValueError("El archivo credentials.ini no contiene la sección [AUTH].")
    auth = config["AUTH"]
    required = ["sap_system", "sap_client", "sap_user", "sap_password"]
    creds = {k: auth.get(k, "").strip() for k in required}
    creds["sap_language"] = auth.get("sap_language", "ES").strip() or "ES"
    missing = [k for k, v in creds.items() if k != "sap_language" and not v]
    if missing:
        raise ValueError(f"Faltan claves en credentials.ini: {', '.join(missing)}")
    return creds

# ---------------------- CONFIGURACIÓN (sin credenciales embebidas) -------------
_CREDS = load_credentials()
SAP_SYSTEM  = _CREDS["sap_system"]
SAP_CLIENT  = _CREDS["sap_client"]
SAP_USER    = _CREDS["sap_user"]
SAP_PASS    = _CREDS["sap_password"]
SAP_LANG    = _CREDS.get("sap_language", "ES") or "ES"

TCODE       = "y_dev_42000074"
NODE_KEY    = "F00119"
ROW_NUMBER  = 25
OUTPUT_DIR  = Path(r"C:/data/SAP_Extraction/y_dev_74")
DATE_STR    = datetime.now().strftime("%d.%m.%Y")
FILENAME    = "Monitor_Guias.txt"  # nombre del TXT exportado
# --------------------------------------------------------------------------------

# Dependencias SAP GUI (Windows)
try:
    import pythoncom  # type: ignore
    import win32com.client  # type: ignore
except Exception:
    pythoncom = None  # type: ignore
    win32com = None  # type: ignore

# Módulo auxiliar del usuario
try:
    import y_dev_74 as ydev
except ImportError as e:
    print(f"ERROR: No se pudo importar 'y_dev_74.py'.")
    print(f"Se buscó en: {PARENT_DIR}")
    print(f"Detalle: {e}")
    print(f"Verifica que el archivo 'y_dev_74.py' existe en: {PARENT_DIR / 'y_dev_74.py'}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR inesperado al importar 'y_dev_74.py': {e}")
    sys.exit(1)

# Logging
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("y_dev_74_quicktest")

class SapHelperError(Exception):
    pass

def _coinit() -> None:
    if pythoncom is None:
        return
    try:
        pythoncom.CoInitialize()
    except Exception:
        pass

def _get_sap_application(start_if_needed: bool = True, wait_timeout: float = 20.0):
    if win32com is None:
        return None
    def _try_get():
        try:
            SapGuiAuto = win32com.client.GetObject("SAPGUI")
            return SapGuiAuto.GetScriptingEngine
        except Exception:
            return None
    app = _try_get()
    if app or not start_if_needed:
        return app
    candidates = [
        r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
        r"C:\Program Files\SAP\FrontEnd\SAPgui\saplogon.exe",
    ]
    for exe in candidates:
        if os.path.isfile(exe):
            try:
                os.startfile(exe)
                break
            except Exception:
                continue
    t0 = time.time()
    while time.time() - t0 < wait_timeout:
        app = _try_get()
        if app:
            return app
        time.sleep(0.5)
    return None

def open_connection_or_reuse_new_session(system_label: str, client: str, user: str, password: str, language: str = "ES"):
    app = _get_sap_application(start_if_needed=True)
    if not app:
        raise SapHelperError("No se obtuvo SAP GUI Scripting. Verifica instalación y que el scripting esté habilitado.")
    # Reutilizar conexión si existe
    try:
        conn_count = app.Children.Count
    except Exception:
        conn_count = 0
    if conn_count > 0:
        connection = app.Children(conn_count - 1)
        try:
            before = connection.Children.Count
        except Exception:
            before = 0
        try:
            connection.Children(0).CreateSession()
        except Exception:
            pass
        t0 = time.time()
        session = None
        while time.time() - t0 < 10:
            try:
                now = connection.Children.Count
            except Exception:
                now = before
            if now > before:
                session = connection.Children(now - 1)
                break
            time.sleep(0.3)
        if session is None:
            if before == 0:
                raise SapHelperError("La conexión no tiene sesiones activas.")
            session = connection.Children(before - 1)
        return app, connection, session

    # Abrir nueva conexión y loguear
    try:
        connection = app.OpenConnection(system_label, True)
        session = connection.Children(0)
        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = client
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = user
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        session.findById("wnd[0]/usr/txtRSYST-LANGU").text = language
        session.findById("wnd[0]").sendVKey(0)
    except Exception as e:
        raise SapHelperError(f"Fallo al abrir conexión o hacer login: {e}")
    return app, connection, session

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def wait_for_file(file_path: Path, timeout: int = 60) -> None:
    t0 = time.time()
    while not file_path.exists():
        if time.time() - t0 > timeout:
            raise FileNotFoundError(f"Archivo no encontrado en {timeout} s: {file_path}")
        time.sleep(1)

def process_tab_file(input_path: Path, output_path: Path) -> None:
    """Elimina fila 6 (índice 5) y columnas A y C (índices 0 y 2), y guarda Excel."""
    try:
        with input_path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        if len(lines) > 5:
            del lines[5]
        data = [line.rstrip("").split("	") for line in lines]
        processed = [[col for i, col in enumerate(row) if i not in (0, 2)] for row in data]
        df = pd.DataFrame(processed)
        ensure_dir(output_path.parent)
        df.to_excel(output_path, index=False, engine="openpyxl")
        logger.info("Archivo procesado: %s", output_path)
    except Exception as e:
        raise RuntimeError(f"Error al procesar archivo tabulado: {e}")

def drop_first_5_rows_inplace(xlsx_path: Path) -> None:
    """Elimina las primeras 5 filas del Excel y sobrescribe el archivo."""
    try:
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        if len(df.index) <= 5:
            logger.warning("El archivo tiene %d filas; se eliminarán todas o quedará vacío.", len(df.index))
        df = df.iloc[5:].reset_index(drop=True)
        df.to_excel(xlsx_path, index=False, header=False, engine="openpyxl")
        logger.info("Se eliminaron las primeras 5 filas y se sobrescribió: %s", xlsx_path)
    except Exception as e:
        raise RuntimeError(f"Error al eliminar las primeras 5 filas del Excel: {e}")

@dataclass
class RunConfig:
    system_label: str
    client: str
    user: str
    password: str
    language: str = "ES"
    tcode: str = "y_dev_42000074"
    node_key: str = "F00119"
    row_number: int = 25
    output_dir: Path = OUTPUT_DIR
    date_str: str = DATE_STR

def run_once(cfg: RunConfig) -> Path:
    if ydev is None:
        raise SapHelperError("No se pudo importar 'y_dev_74.py'. Déjalo junto a este archivo.")
    _coinit()
    logger.info("Conectando a SAP…")
    _app, _conn, session = open_connection_or_reuse_new_session(cfg.system_label, cfg.client, cfg.user, cfg.password, cfg.language)
    logger.info("Conectado. Ejecutando %s…", cfg.tcode)

    ensure_dir(cfg.output_dir)
    full_path = ydev.run_y_dev_74(
        session=session,
        tcode=cfg.tcode,
        node_key=cfg.node_key,
        row_number=cfg.row_number,
        output_path=str(cfg.output_dir),
        filename=FILENAME,
        date_str=cfg.date_str,
        debug=False,
    )
    txt_path = Path(full_path)

    # Espera inicial de 3s + espera activa por el archivo
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info("Exportación completada: %s", txt_path)

    # TXT -> Excel
    xlsx_path = txt_path.with_name(txt_path.stem + "_processed.xlsx")
    process_tab_file(txt_path, xlsx_path)

    # Eliminar primeras 5 filas del Excel
    drop_first_5_rows_inplace(xlsx_path)

    # Generar reporte con gráficos y enviar correo
    # Usa el archivo Excel procesado (después de TXT->XLSX y eliminar primeras 5 filas)
    try:
        logger.info("Generando reporte con gráficos...")
        import subprocess
        script_graficos = Path(__file__).parent / "generar_reporte_graficos.py"
        if script_graficos.exists():
            result = subprocess.run(
                [sys.executable, str(script_graficos), "--archivo", str(xlsx_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.info("✅ Reporte con gráficos generado y correo enviado")
            else:
                logger.warning(f"⚠️  El script de gráficos terminó con código {result.returncode}")
                if result.stderr:
                    logger.warning(f"Error: {result.stderr}")
        else:
            logger.warning("⚠️  No se encontró el script generar_reporte_graficos.py")
    except Exception as e:
        logger.warning(f"⚠️  Error al generar reporte con gráficos: {e}")

    return txt_path

def main() -> int:
    for name, val in (("SAP_SYSTEM", SAP_SYSTEM), ("SAP_CLIENT", SAP_CLIENT), ("SAP_USER", SAP_USER), ("SAP_PASS", SAP_PASS)):
        if not val:
            logger.error("Falta '%s' en CONFIGURACIÓN RÁPIDA.", name); return 2

    cfg = RunConfig(
        system_label=SAP_SYSTEM, client=SAP_CLIENT, user=SAP_USER, password=SAP_PASS,
        language=SAP_LANG or "ES", tcode=TCODE, node_key=NODE_KEY, row_number=ROW_NUMBER,
        output_dir=OUTPUT_DIR, date_str=DATE_STR,
    )
    logger.info("INICIO | Amalgama Y_DEV_74 (Quick Test - Opción A)")
    logger.info("Hora local: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        txt_path = run_once(cfg)
        logger.info("OK | Reporte generado desde: %s", txt_path)
        return 0
    except Exception as e:
        logger.exception("Error en ejecución: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())
