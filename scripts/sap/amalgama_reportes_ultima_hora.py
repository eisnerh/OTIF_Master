# -*- coding: utf-8 -*-
"""
Script: amalgama_reportes_ultima_hora.py
Descripción:
  - Descarga múltiples reportes de SAP secuencialmente
  - Convierte automáticamente archivos .txt a Excel (.xlsx)
  - Aplica transformaciones específicas por reporte
  - Limpia datos residuales entre cada ejecución
  - Usa la fecha de ayer para todos los reportes
  - Guarda en carpetas separadas por reporte
  - Flujo completo: Descarga SAP → TXT → Excel procesado
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

# Agregar el directorio padre al sys.path
SCRIPT_DIR = Path(__file__).parent
REPORTES_DIR = SCRIPT_DIR / "Reportes_Ultima_Hora"
if str(REPORTES_DIR) not in sys.path:
    sys.path.insert(0, str(REPORTES_DIR))

# Importar módulos auxiliares desde Reportes_Ultima_Hora
try:
    import y_dev_45
    import y_dev_74
    import y_dev_82
    import y_rep_plr
    import z_devo_alv
    import zhbo
    import zred
    import zresguias
    import zsd_incidencias
    print("[OK] Todos los módulos de reportes importados correctamente")
except ImportError as e:
    print(f"ERROR: No se pudieron importar los módulos necesarios: {e}")
    print(f"Verifica que todos los archivos estén en: {REPORTES_DIR}")
    sys.exit(1)

# Dependencias SAP GUI (Windows)
try:
    import pythoncom
    import win32com.client
except Exception:
    print("ERROR: No se pudo importar pywin32. Instala con: pip install pywin32")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: No se pudo importar pandas. Instala con: pip install pandas openpyxl")
    sys.exit(1)

# Logging
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("reportes_ultima_hora")

# ---------------------- CONFIGURACIÓN -----------------------------
OUTPUT_DIR = Path(r"C:/data/SAP_Extraction/reportes_ultima_hora")
FECHA_AYER = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
FECHA_AYER_FILENAME = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
TIEMPO_ESPERA_ENTRE_REPORTES = 10  # segundos

# ------------------------------------------------------------------

def load_credentials() -> dict:
    """Carga credenciales desde credentials.ini"""
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

class SapHelperError(Exception):
    pass

def _coinit() -> None:
    """Inicializa COM para el thread actual"""
    try:
        pythoncom.CoInitialize()
    except Exception:
        pass

def _get_sap_application(start_if_needed: bool = True, wait_timeout: float = 20.0):
    """Obtiene la aplicación SAP GUI"""
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

def open_connection_or_reuse_new_session(system_label: str, client: str, user: str, 
                                          password: str, language: str = "ES"):
    """Abre conexión a SAP o reutiliza una existente"""
    app = _get_sap_application(start_if_needed=True)
    if not app:
        raise SapHelperError("No se obtuvo SAP GUI Scripting.")
    
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
    
    # Abrir nueva conexión
    try:
        connection = app.OpenConnection(system_label, True)
        session = connection.Children(0)
        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = client
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = user
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        session.findById("wnd[0]/usr/txtRSYST-LANGU").text = language
        session.findById("wnd[0]").sendVKey(0)
    except Exception as e:
        raise SapHelperError(f"Fallo al abrir conexión: {e}")
    return app, connection, session

def limpiar_sesion_sap(session):
    """Limpia la sesión SAP antes de ejecutar el siguiente reporte"""
    try:
        logger.info("Limpiando sesión SAP...")
        # Ir al menú principal
        session.findById("wnd[0]").sendVKey(0)
        session.findById("wnd[0]").sendCommand("/n")
        session.findById("wnd[0]").sendVKey(0)
        
        # Cerrar ventanas adicionales
        for i in range(1, 10):
            try:
                session.findById(f"wnd[{i}]").close()
            except:
                break
        
        time.sleep(2)
        logger.info("Sesión SAP limpiada correctamente")
    except Exception as e:
        logger.warning(f"Error al limpiar sesión: {e}")

def ensure_dir(path: Path) -> None:
    """Asegura que el directorio existe"""
    path.mkdir(parents=True, exist_ok=True)

def wait_for_file(file_path: Path, timeout: int = 60) -> None:
    """Espera a que el archivo se genere"""
    t0 = time.time()
    while not file_path.exists():
        if time.time() - t0 > timeout:
            raise FileNotFoundError(f"Archivo no encontrado en {timeout}s: {file_path}")
        time.sleep(1)

# ==================== FUNCIONES DE PROCESAMIENTO TXT → EXCEL ====================

def leer_archivo_txt(ruta_txt: Path) -> pd.DataFrame:
    """Lee un archivo .txt tabulado y lo convierte en DataFrame"""
    try:
        with open(ruta_txt, 'r', encoding='utf-8', errors='replace') as f:
            lineas = f.readlines()
        data = [linea.rstrip('\r\n').split('\t') for linea in lineas]
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        raise RuntimeError(f"Error al leer {ruta_txt}: {e}")

def procesar_y_dev_45_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Y_DEV_45: Eliminar cols A,C | fila 6 | primeras 4 filas"""
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 2]]
    df = df.iloc[:, columnas_mantener]
    return df

def procesar_monitor_guias_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Monitor_Guias: Eliminar cols A,C | fila 6 | primeras 4 filas"""
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 2]]
    df = df.iloc[:, columnas_mantener]
    return df

def procesar_y_dev_82_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Y_DEV_82: Eliminar cols A,D | fila 6 | primeras 4 filas"""
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 3]]
    df = df.iloc[:, columnas_mantener]
    return df

def procesar_rep_plr_excel(df: pd.DataFrame) -> pd.DataFrame:
    """REP_PLR: Eliminar col A | fila 5 | primeras 4 filas | filtrar H=1"""
    if len(df) > 4:
        df = df.drop(index=4).reset_index(drop=True)
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    if len(df.columns) > 0:
        df = df.iloc[:, 1:]
    if len(df.columns) > 7 and len(df) > 0:
        df = df[df.iloc[:, 7] == "1"]
    return df

def procesar_zhbo_excel(df: pd.DataFrame) -> pd.DataFrame:
    """ZHBO: Eliminar cols A,B | fila 6 | primeras 4 filas"""
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    if len(df.columns) > 2:
        df = df.iloc[:, 2:]
    return df

def procesar_zred_excel(df: pd.DataFrame) -> pd.DataFrame:
    """ZRED: Eliminar col A | fila 5 | primeras 3 filas"""
    if len(df) > 4:
        df = df.drop(index=4).reset_index(drop=True)
    if len(df) > 3:
        df = df.iloc[3:].reset_index(drop=True)
    if len(df.columns) > 0:
        df = df.iloc[:, 1:]
    return df

def procesar_zresguias_excel(df: pd.DataFrame) -> pd.DataFrame:
    """ZRESGUIAS: Eliminar cols A,B,O | fila 6 | primeras 4 filas"""
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 1, 14]]
    df = df.iloc[:, columnas_mantener]
    return df

def procesar_z_devo_alv_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Z_DEVO_ALV: Eliminar col A | fila 5 | primeras 3 filas"""
    if len(df) > 4:
        df = df.drop(index=4).reset_index(drop=True)
    if len(df) > 3:
        df = df.iloc[3:].reset_index(drop=True)
    if len(df.columns) > 0:
        df = df.iloc[:, 1:]
    return df

def procesar_zsd_incidencias_excel(df: pd.DataFrame) -> pd.DataFrame:
    """ZSD_INCIDENCIAS: Procesamiento básico"""
    if len(df) > 5:
        df = df.iloc[5:].reset_index(drop=True)
    return df

def convertir_txt_a_excel(ruta_txt: Path, procesador_nombre: str) -> Path:
    """Convierte un archivo .txt a Excel aplicando las transformaciones correspondientes"""
    
    procesadores = {
        'Y_DEV_45': procesar_y_dev_45_excel,
        'Y_DEV_74': procesar_monitor_guias_excel,
        'Y_DEV_82': procesar_y_dev_82_excel,
        'Y_REP_PLR': procesar_rep_plr_excel,
        'ZHBO': procesar_zhbo_excel,
        'ZRED': procesar_zred_excel,
        'ZRESGUIAS': procesar_zresguias_excel,
        'Z_DEVO_ALV': procesar_z_devo_alv_excel,
        'ZSD_INCIDENCIAS': procesar_zsd_incidencias_excel,
    }
    
    try:
        logger.info(f"  Convirtiendo a Excel: {ruta_txt.name}")
        
        # Leer archivo
        df = leer_archivo_txt(ruta_txt)
        
        # Aplicar transformaciones
        procesador = procesadores.get(procesador_nombre)
        if procesador:
            df_procesado = procesador(df)
            logger.info(f"    Transformaciones aplicadas: {len(df_procesado)} filas x {len(df_procesado.columns)} cols")
        else:
            df_procesado = df
            logger.warning(f"    No se encontró procesador para {procesador_nombre}, usando datos sin procesar")
        
        # Generar archivo Excel
        ruta_excel = ruta_txt.with_suffix('.xlsx')
        df_procesado.to_excel(ruta_excel, index=False, header=False, engine='openpyxl')
        
        logger.info(f"  ✓ Excel generado: {ruta_excel.name}")
        return ruta_excel
        
    except Exception as e:
        logger.error(f"  ✗ Error al convertir a Excel: {e}")
        return None

# ==================== FIN FUNCIONES DE PROCESAMIENTO ====================

def descargar_y_procesar(session, funcion_descarga, nombre_procesador: str):
    """Wrapper que descarga un reporte y automáticamente lo convierte a Excel"""
    
    # Paso 1: Descargar archivo .txt
    ruta_txt = funcion_descarga(session)
    
    if ruta_txt is None:
        logger.error(f"  ✗ No se pudo descargar el reporte")
        return None, None
    
    # Paso 2: Convertir a Excel
    ruta_excel = convertir_txt_a_excel(ruta_txt, nombre_procesador)
    
    return ruta_txt, ruta_excel

# ==================== FUNCIONES DE DESCARGA ====================

def descargar_reporte_y_dev_74(session) -> Path:
    """Descarga el reporte Y_DEV_74 (Monitor de Guías)"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: Y_DEV_74 - Monitor de Guías")
    logger.info("=" * 70)
    
    # Carpeta específica para este reporte
    output_dir = OUTPUT_DIR / "Y_DEV_74"
    ensure_dir(output_dir)
    
    filename = f"Monitor_Guias_{FECHA_AYER_FILENAME}.txt"
    
    full_path = y_dev_74.run_y_dev_74(
        session=session,
        tcode="y_dev_42000074",
        node_key="F00119",
        row_number=4,
        output_path=str(output_dir),
        filename=filename,
        date_str=FECHA_AYER,
        debug=False,
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_y_dev_45(session) -> Path:
    """Descarga el reporte Y_DEV_45"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: Y_DEV_45")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "Y_DEV_45"
    ensure_dir(output_dir)
    filename = f"y_dev_45_{FECHA_AYER_FILENAME}.txt"
    
    full_path = y_dev_45.run_y_dev_45(
        session=session,
        row_number=2,
        output_path=str(output_dir),
        filename=filename,
        debug=False,
        encoding="0000"
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_y_dev_82(session) -> Path:
    """Descarga el reporte Y_DEV_82"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: Y_DEV_82")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "Y_DEV_82"
    ensure_dir(output_dir)
    filename = f"y_dev_82_{FECHA_AYER_FILENAME}.txt"
    
    full_path = y_dev_82.run_y_dev_82(
        session=session,
        tcode="y_dev_42000082",
        node_key="F00139",
        row_number=2,
        output_path=str(output_dir),
        filename=filename,
        encoding="0000",
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_y_rep_plr(session) -> Path:
    """Descarga el reporte Y_REP_PLR"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: Y_REP_PLR - Planeamiento")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "Y_REP_PLR"
    ensure_dir(output_dir)
    filename = f"rep_plr_{FECHA_AYER_FILENAME}.txt"
    
    full_path = y_rep_plr.run_y_rep_plr(
        session=session,
        tcode="zsd_rep_planeamiento",
        node_key="F00120",
        row_number=11,
        date_str=FECHA_AYER,
        output_path=str(output_dir),
        filename=filename,
        encoding="0000",
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_z_devo_alv(session) -> Path:
    """Descarga el reporte Z_DEVO_ALV"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: Z_DEVO_ALV (Y_DEVO_ALV)")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "Z_DEVO_ALV"
    ensure_dir(output_dir)
    filename = f"z_devo_alv_{FECHA_AYER_FILENAME}.txt"
    
    # Parámetros correctos según z_devo_alv.py:
    # - tcode: y_devo_alv (no z_devo_alv)
    # - node_key: F00072 (no F00001)
    # - row_number: 12 (no 0)
    full_path = z_devo_alv.run_z_devo_alv(
        session=session,
        tcode="y_devo_alv",
        node_key="F00072",
        row_number=12,
        output_path=str(output_dir),
        filename=filename,
        encoding="0000",
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_zhbo(session) -> Path:
    """Descarga el reporte ZHBO"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: ZHBO")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "ZHBO"
    ensure_dir(output_dir)
    filename = f"zhbo_{FECHA_AYER_FILENAME}.txt"
    
    # Parámetros correctos según zhbo.py:
    # - row_number: 11 (no 1)
    # - orden: session, row_number, output_path, filename, date_str
    full_path = zhbo.run_zhbo(
        session=session,
        row_number=11,
        output_path=str(output_dir),
        filename=filename,
        date_str=FECHA_AYER,
        encoding="0000",
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_zred(session) -> Path:
    """Descarga el reporte ZRED"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: ZRED")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "ZRED"
    ensure_dir(output_dir)
    filename = f"zred_{FECHA_AYER_FILENAME}.txt"
    
    full_path = zred.run_zred(
        session=session,
        row_number=1,
        output_path=str(output_dir),
        filename=filename,
        encoding="0000",
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_zresguias(session) -> Path:
    """Descarga el reporte ZRESGUIAS"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: ZRESGUIAS - Resguardo de Guías")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "ZRESGUIAS"
    ensure_dir(output_dir)
    filename = f"zresguias_{FECHA_AYER_FILENAME}.txt"
    
    full_path = zresguias.run_zresguias(
        session=session,
        row_number=26,
        date_str=FECHA_AYER,
        output_path=str(output_dir),
        filename=filename,
        encoding="0000",
        use_calendar=False,
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def descargar_reporte_zsd_incidencias(session) -> Path:
    """Descarga el reporte ZSD_INCIDENCIAS"""
    logger.info("=" * 70)
    logger.info("DESCARGANDO: ZSD_INCIDENCIAS")
    logger.info("=" * 70)
    
    output_dir = OUTPUT_DIR / "ZSD_INCIDENCIAS"
    ensure_dir(output_dir)
    filename = f"zsd_incidencias_{FECHA_AYER_FILENAME}.txt"
    
    # Parámetros correctos según zsd_incidencias.py:
    # - row_number: 12 (por defecto)
    # - orden: session, row_number, output_path, filename
    full_path = zsd_incidencias.run_zsd_incidencias(
        session=session,
        row_number=12,
        output_path=str(output_dir),
        filename=filename,
        encoding="0000",
        debug=False
    )
    
    txt_path = Path(full_path)
    time.sleep(3)
    wait_for_file(txt_path, timeout=60)
    logger.info(f"✓ Archivo generado: {txt_path.name}")
    logger.info(f"  Ubicación: {txt_path.parent}")
    return txt_path

def main() -> int:
    """Función principal"""
    logger.info("=" * 70)
    logger.info("INICIO: Descarga de Reportes de Última Hora")
    logger.info("=" * 70)
    logger.info(f"Fecha de referencia: {FECHA_AYER}")
    logger.info(f"Directorio de salida: {OUTPUT_DIR}")
    logger.info(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    try:
        # Cargar credenciales
        creds = load_credentials()
        _coinit()
        
        # Conectar a SAP
        logger.info("Conectando a SAP...")
        app, conn, session = open_connection_or_reuse_new_session(
            system_label=creds["sap_system"],
            client=creds["sap_client"],
            user=creds["sap_user"],
            password=creds["sap_password"],
            language=creds["sap_language"]
        )
        logger.info("✓ Conectado a SAP exitosamente")
        
        reportes_descargados = []
        reportes_fallidos = []
        
        # Lista de reportes a descargar (nombre, función de descarga, nombre del procesador)
        reportes = [
            ("Y_DEV_74 - Monitor de Guías", descargar_reporte_y_dev_74, "Y_DEV_74"),
            ("Y_DEV_45", descargar_reporte_y_dev_45, "Y_DEV_45"),
            ("Y_DEV_82", descargar_reporte_y_dev_82, "Y_DEV_82"),
            ("Y_REP_PLR - Planeamiento", descargar_reporte_y_rep_plr, "Y_REP_PLR"),
            ("Z_DEVO_ALV", descargar_reporte_z_devo_alv, "Z_DEVO_ALV"),
            ("ZHBO", descargar_reporte_zhbo, "ZHBO"),
            ("ZRED", descargar_reporte_zred, "ZRED"),
            ("ZRESGUIAS - Resguardo de Guías", descargar_reporte_zresguias, "ZRESGUIAS"),
            ("ZSD_INCIDENCIAS", descargar_reporte_zsd_incidencias, "ZSD_INCIDENCIAS"),
        ]
        
        total_reportes = len(reportes)
        logger.info(f"Total de reportes a descargar y procesar: {total_reportes}")
        logger.info("=" * 70)
        
        # Descargar y procesar cada reporte
        for i, (nombre, funcion, procesador) in enumerate(reportes, 1):
            try:
                logger.info(f"\n[{i}/{total_reportes}] Procesando: {nombre}")
                
                # Descargar archivo .txt
                archivo_txt = funcion(session)
                
                # Convertir a Excel
                archivo_excel = convertir_txt_a_excel(archivo_txt, procesador)
                
                if archivo_excel:
                    reportes_descargados.append((nombre, archivo_txt, archivo_excel))
                    logger.info(f"✓ Reporte {nombre} completado (TXT + Excel)")
                else:
                    reportes_descargados.append((nombre, archivo_txt, None))
                    logger.warning(f"⚠ Reporte {nombre} descargado pero sin Excel")
                    
            except Exception as e:
                logger.error(f"✗ Error al procesar {nombre}: {e}")
                reportes_fallidos.append((nombre, str(e)))
            
            # Esperar y limpiar sesión entre reportes (excepto después del último)
            if i < total_reportes:
                logger.info(f"Esperando {TIEMPO_ESPERA_ENTRE_REPORTES} segundos...")
                time.sleep(TIEMPO_ESPERA_ENTRE_REPORTES)
                limpiar_sesion_sap(session)
        
        # Resumen final
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE DESCARGA")
        logger.info("=" * 70)
        logger.info(f"Total de reportes procesados: {total_reportes}")
        logger.info(f"✓ Exitosos: {len(reportes_descargados)}")
        logger.info(f"✗ Fallidos: {len(reportes_fallidos)}")
        logger.info("=" * 70)
        
        if reportes_descargados:
            logger.info("\n✓ REPORTES DESCARGADOS EXITOSAMENTE:")
            for item in reportes_descargados:
                nombre = item[0]
                archivo_txt = item[1]
                archivo_excel = item[2] if len(item) > 2 else None
                
                logger.info(f"  • {nombre}")
                logger.info(f"    ├─ TXT:  {archivo_txt.name}")
                if archivo_excel:
                    logger.info(f"    └─ XLSX: {archivo_excel.name}")
                else:
                    logger.info(f"    └─ XLSX: (no generado)")
        
        if reportes_fallidos:
            logger.info("\n✗ REPORTES CON ERRORES:")
            for nombre, error in reportes_fallidos:
                logger.info(f"  • {nombre}")
                logger.info(f"    └─ Error: {error}")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"Directorio de salida: {OUTPUT_DIR}")
        logger.info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("")
        logger.info("Archivos generados por carpeta:")
        logger.info("  Cada carpeta contiene:")
        logger.info("    • archivo.txt  (original de SAP)")
        logger.info("    • archivo.xlsx (procesado y listo para análisis)")
        
        if len(reportes_fallidos) == 0:
            logger.info("\n✓ PROCESO COMPLETADO EXITOSAMENTE")
            logger.info("  Todos los reportes descargados y procesados a Excel")
        elif len(reportes_descargados) > 0:
            logger.info("\n⚠ PROCESO COMPLETADO CON ADVERTENCIAS")
            logger.info(f"  {len(reportes_descargados)} reportes exitosos, {len(reportes_fallidos)} fallidos")
        else:
            logger.info("\n✗ PROCESO FALLIDO")
            logger.info("  No se descargó ningún reporte")
        
        logger.info("=" * 70)
        
        # Retornar código según resultado
        if len(reportes_fallidos) == 0:
            return 0  # Todo exitoso
        elif len(reportes_descargados) > 0:
            return 2  # Parcialmente exitoso
        else:
            return 1  # Todo falló
        
    except Exception as e:
        logger.exception(f"ERROR CRÍTICO: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

