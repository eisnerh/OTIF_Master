
# -*- coding: utf-8 -*-
"""
Script: amalgama_y_rep_plr.py
Descripción:
  - Ejecuta el reporte PLR con auto-login a SAP si no está abierto
  - Si SAP ya está abierto, crea una nueva sesión
  - Exporta los datos limpios con la fecha de HOY
  - Genera archivo Excel procesado
  
ADVERTENCIA DE SEGURIDAD:
  Este archivo usa credenciales de credentials.ini para pruebas locales.
  No subir el archivo credentials.ini a repositorios públicos.
"""
from __future__ import annotations

import os
import sys
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import configparser
import pandas as pd

# Agregar el directorio padre al sys.path para poder importar y_rep_plr
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

TCODE       = "zsd_rep_planeamiento"
NODE_KEY    = "F00120"
ROW_NUMBER  = 11  # Ajustar según la fila que se necesite
OUTPUT_DIR  = Path(r"C:/data/SAP_Extraction/rep_plr")
# Usar fecha de HOY (no ayer)
DATE_STR = datetime.now().strftime("%d.%m.%Y")
FILENAME    = "REP_PLR.txt"  # nombre del archivo exportado
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
    # Primero intenta importar desde el directorio actual
    sys.path.insert(0, str(SCRIPT_DIR))
    import y_rep_plr as yplr
except ImportError:
    try:
        # Si no está, intenta desde la carpeta padre
        sys.path.insert(0, str(PARENT_DIR))
        import y_rep_plr as yplr
    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar 'y_rep_plr.py'.")
        print(f"Se buscó en: {SCRIPT_DIR} y {PARENT_DIR}")
        print(f"Detalle: {e}")
        print(f"Verifica que el archivo 'y_rep_plr.py' existe en: {SCRIPT_DIR / 'y_rep_plr.py'}")
        sys.exit(1)

# Logging
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("amalgama_y_rep_plr")

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
    """Obtiene la aplicación SAP GUI. Si no está abierta y start_if_needed=True, la inicia."""
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
    # Buscar saplogon.exe en ubicaciones comunes
    candidates = [
        r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
        r"C:\Program Files\SAP\FrontEnd\SAPgui\saplogon.exe",
    ]
    for exe in candidates:
        if os.path.isfile(exe):
            try:
                logger.info(f"🚀 Iniciando SAP GUI desde: {exe}")
                os.startfile(exe)
                break
            except Exception as e:
                logger.warning(f"⚠️  No se pudo iniciar SAP desde {exe}: {e}")
                continue
    # Esperar a que SAP GUI esté disponible
    t0 = time.time()
    while time.time() - t0 < wait_timeout:
        app = _try_get()
        if app:
            logger.info("✅ SAP GUI iniciado correctamente")
            return app
        time.sleep(0.5)
    return None

def open_connection_or_reuse_new_session(system_label: str, client: str, user: str, password: str, language: str = "ES"):
    """
    Abre una conexión a SAP o reutiliza una existente creando una nueva sesión.
    
    Si SAP no está abierto: lo inicia y hace login.
    Si SAP ya está abierto: crea una nueva sesión en la conexión existente.
    """
    app = _get_sap_application(start_if_needed=True)
    if not app:
        raise SapHelperError("No se obtuvo SAP GUI Scripting. Verifica instalación y que el scripting esté habilitado.")
    
    # Verificar si hay conexiones existentes
    try:
        conn_count = app.Children.Count
    except Exception:
        conn_count = 0
    
    logger.info(f"📊 Conexiones SAP encontradas: {conn_count}")
    
    if conn_count > 0:
        # Hay conexiones existentes, intentar crear una nueva sesión
        logger.info("♻️  Reutilizando conexión existente y creando nueva sesión...")
        connection = app.Children(conn_count - 1)
        try:
            before = connection.Children.Count
        except Exception:
            before = 0
        
        logger.info(f"📝 Sesiones antes de crear nueva: {before}")
        
        try:
            # Crear nueva sesión
            connection.Children(0).CreateSession()
            logger.info("✅ Nueva sesión creada")
        except Exception as e:
            logger.warning(f"⚠️  No se pudo crear nueva sesión: {e}")
            pass
        
        # Esperar a que la nueva sesión esté disponible
        t0 = time.time()
        session = None
        while time.time() - t0 < 10:
            try:
                now = connection.Children.Count
            except Exception:
                now = before
            if now > before:
                session = connection.Children(now - 1)
                logger.info(f"✅ Nueva sesión disponible (total sesiones: {now})")
                break
            time.sleep(0.3)
        
        if session is None:
            if before == 0:
                raise SapHelperError("La conexión no tiene sesiones activas.")
            logger.warning("⚠️  No se pudo crear nueva sesión, usando sesión existente")
            session = connection.Children(before - 1)
        
        return app, connection, session

    # No hay conexiones, abrir nueva conexión y hacer login
    logger.info("🔐 No hay conexiones existentes, abriendo nueva conexión y haciendo login...")
    try:
        connection = app.OpenConnection(system_label, True)
        logger.info("✅ Conexión abierta")
        
        # Esperar un poco para que la ventana de login esté disponible
        time.sleep(2)
        
        session = connection.Children(0)
        
        # Hacer login
        logger.info(f"🔑 Iniciando sesión como usuario: {user}")
        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = client
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = user
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        session.findById("wnd[0]/usr/txtRSYST-LANGU").text = language
        session.findById("wnd[0]").sendVKey(0)
        
        # Esperar a que termine el login
        time.sleep(2)
        logger.info("✅ Login completado")
        
    except Exception as e:
        raise SapHelperError(f"Fallo al abrir conexión o hacer login: {e}")
    
    return app, connection, session

def ensure_dir(path: Path) -> None:
    """Crea el directorio si no existe."""
    path.mkdir(parents=True, exist_ok=True)

def wait_for_file(file_path: Path, timeout: int = 60) -> None:
    """Espera a que un archivo exista."""
    t0 = time.time()
    while not file_path.exists():
        if time.time() - t0 > timeout:
            raise FileNotFoundError(f"Archivo no encontrado en {timeout} s: {file_path}")
        time.sleep(1)

def process_tab_file(input_path: Path, output_path: Path) -> None:
    """Procesa el archivo tabulado y lo convierte a Excel."""
    try:
        logger.info(f"📄 Procesando archivo: {input_path}")
        
        # Leer archivo con tabulaciones
        with input_path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        # Procesar líneas
        data = [line.rstrip("\n").split("\t") for line in lines]
        df = pd.DataFrame(data)
        
        # Guardar como Excel
        ensure_dir(output_path.parent)
        df.to_excel(output_path, index=False, header=False, engine="openpyxl")
        logger.info(f"✅ Archivo procesado: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Error al procesar archivo tabulado: {e}")

def clean_excel_file(xlsx_path: Path, rows_to_drop: int = 5) -> None:
    """Elimina las primeras N filas del Excel y sobrescribe el archivo."""
    try:
        logger.info(f"🧹 Limpiando archivo Excel (eliminando primeras {rows_to_drop} filas)...")
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        
        if len(df.index) <= rows_to_drop:
            logger.warning(f"⚠️  El archivo tiene {len(df.index)} filas; se eliminarán todas o quedará vacío.")
        
        # Eliminar primeras N filas
        df = df.iloc[rows_to_drop:].reset_index(drop=True)
        df.to_excel(xlsx_path, index=False, header=False, engine="openpyxl")
        logger.info(f"✅ Archivo limpiado: {xlsx_path}")
    except Exception as e:
        raise RuntimeError(f"Error al limpiar el archivo Excel: {e}")

@dataclass
class RunConfig:
    system_label: str
    client: str
    user: str
    password: str
    language: str = "ES"
    tcode: str = "zsd_rep_planeamiento"
    node_key: str = "F00120"
    row_number: int = 11
    output_dir: Path = OUTPUT_DIR
    date_str: str = DATE_STR

def run_once(cfg: RunConfig) -> Path:
    """Ejecuta el proceso completo una vez."""
    if yplr is None:
        raise SapHelperError("No se pudo importar 'y_rep_plr.py'.")
    
    _coinit()
    logger.info("🔌 Conectando a SAP...")
    _app, _conn, session = open_connection_or_reuse_new_session(
        cfg.system_label, cfg.client, cfg.user, cfg.password, cfg.language
    )
    logger.info(f"✅ Conectado. Ejecutando {cfg.tcode}...")

    ensure_dir(cfg.output_dir)
    
    # Ejecutar el script de extracción
    full_path = yplr.run_y_rep_plr(
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

    # Espera inicial + espera activa por el archivo
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✅ Exportación completada: {txt_path}")

    # TXT -> Excel
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    xlsx_path = txt_path.with_name(f"REP_PLR_{fecha_actual}_processed.xlsx")
    process_tab_file(txt_path, xlsx_path)

    # Limpiar Excel (eliminar primeras 5 filas)
    clean_excel_file(xlsx_path, rows_to_drop=5)

    logger.info("=" * 60)
    logger.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")
    logger.info("=" * 60)
    logger.info(f"📁 Archivo TXT: {txt_path}")
    logger.info(f"📊 Archivo Excel: {xlsx_path}")
    logger.info("=" * 60)

    return txt_path

def main() -> int:
    """Función principal."""
    # Validar configuración
    for name, val in (("SAP_SYSTEM", SAP_SYSTEM), ("SAP_CLIENT", SAP_CLIENT), ("SAP_USER", SAP_USER), ("SAP_PASS", SAP_PASS)):
        if not val:
            logger.error(f"❌ Falta '{name}' en configuración.")
            return 2

    cfg = RunConfig(
        system_label=SAP_SYSTEM, 
        client=SAP_CLIENT, 
        user=SAP_USER, 
        password=SAP_PASS,
        language=SAP_LANG or "ES", 
        tcode=TCODE, 
        node_key=NODE_KEY, 
        row_number=ROW_NUMBER,
        output_dir=OUTPUT_DIR, 
        date_str=DATE_STR,
    )
    
    logger.info("=" * 60)
    logger.info("🚀 INICIO | Amalgama Y_REP_PLR")
    logger.info("=" * 60)
    logger.info(f"📅 Fecha: {DATE_STR}")
    logger.info(f"🕐 Hora local: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        txt_path = run_once(cfg)
        logger.info(f"✅ OK | Reporte generado desde: {txt_path}")
        return 0
    except Exception as e:
        logger.exception(f"❌ Error en ejecución: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


