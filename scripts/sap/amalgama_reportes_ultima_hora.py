# -*- coding: utf-8 -*-
"""
Script: amalgama_reportes_ultima_hora.py
Descripción:
  - Descarga múltiples reportes de SAP secuencialmente
  - Limpia datos residuales entre cada ejecución
  - Usa la fecha de ayer para todos los reportes
  - Genera archivos .txt
  - Guarda en la carpeta reportes_ultima_hora
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
    """Limpia la sesión SAP antes de ejecutar el siguiente reporte (modo robusto)"""
    try:
        logger.info("Limpiando sesión SAP...")
        
        # Verificar que la sesión sigue activa
        try:
            wnd0 = session.findById("wnd[0]")
        except Exception as e:
            logger.warning(f"No se pudo acceder a wnd[0]: {e}")
            return
        
        # Intentar ir al menú principal de manera suave
        try:
            wnd0.sendVKey(0)  # Enter primero
            time.sleep(0.5)
        except:
            pass
        
        try:
            # Comando /n para ir al menú principal
            ok = session.findById("wnd[0]/tbar[0]/okcd")
            ok.text = "/n"
            wnd0.sendVKey(0)
            time.sleep(1)
        except Exception as e:
            logger.warning(f"No se pudo ejecutar comando /n: {e}")
            # Intentar método alternativo
            try:
                wnd0.sendCommand("/n")
                time.sleep(1)
            except:
                pass
        
        # Cerrar ventanas adicionales de manera suave
        for i in range(1, 5):
            try:
                wnd = session.findById(f"wnd[{i}]")
                wnd.close()
                time.sleep(0.3)
            except:
                break
        
        time.sleep(1)
        logger.info("✓ Sesión SAP limpiada correctamente")
        
    except Exception as e:
        logger.warning(f"⚠ Error al limpiar sesión: {e}")
        logger.info("Continuando con el siguiente reporte...")

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

@dataclass
class ReporteConfig:
    """Configuración de un reporte a descargar"""
    nombre: str  # Nombre descriptivo del reporte
    tcode: str   # Código de transacción
    filename: str  # Nombre del archivo de salida
    # Agregar más campos según sea necesario para cada tipo de reporte

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
        
        # Lista de reportes a descargar (nombre, función)
        reportes = [
            ("Y_DEV_74 - Monitor de Guías", descargar_reporte_y_dev_74),
            ("Y_DEV_45", descargar_reporte_y_dev_45),
            ("Y_DEV_82", descargar_reporte_y_dev_82),
            ("Y_REP_PLR - Planeamiento", descargar_reporte_y_rep_plr),
            ("Z_DEVO_ALV", descargar_reporte_z_devo_alv),
            ("ZHBO", descargar_reporte_zhbo),
            ("ZRED", descargar_reporte_zred),
            ("ZRESGUIAS - Resguardo de Guías", descargar_reporte_zresguias),
            ("ZSD_INCIDENCIAS", descargar_reporte_zsd_incidencias),
        ]
        
        total_reportes = len(reportes)
        logger.info(f"Total de reportes a descargar: {total_reportes}")
        logger.info("=" * 70)
        
        # Descargar cada reporte
        for i, (nombre, funcion) in enumerate(reportes, 1):
            try:
                logger.info(f"\n[{i}/{total_reportes}] Procesando: {nombre}")
                archivo = funcion(session)
                reportes_descargados.append((nombre, archivo))
                logger.info(f"✓ Reporte {nombre} descargado exitosamente")
            except Exception as e:
                logger.error(f"✗ Error al descargar {nombre}: {e}")
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
            for nombre, archivo in reportes_descargados:
                logger.info(f"  • {nombre}")
                logger.info(f"    └─ {archivo.name}")
        
        if reportes_fallidos:
            logger.info("\n✗ REPORTES CON ERRORES:")
            for nombre, error in reportes_fallidos:
                logger.info(f"  • {nombre}")
                logger.info(f"    └─ Error: {error}")
        
        logger.info("\n" + "=" * 70)
        logger.info(f"Directorio de salida: {OUTPUT_DIR}")
        logger.info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(reportes_fallidos) == 0:
            logger.info("PROCESO COMPLETADO EXITOSAMENTE - TODOS LOS REPORTES DESCARGADOS")
        elif len(reportes_descargados) > 0:
            logger.info("PROCESO COMPLETADO CON ADVERTENCIAS - ALGUNOS REPORTES FALLARON")
        else:
            logger.info("PROCESO FALLIDO - NO SE DESCARGÓ NINGÚN REPORTE")
        
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

