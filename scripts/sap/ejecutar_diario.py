#!/usr/bin/env python3
"""
[HORA] SCRIPT DE EJECUCIÓN DIARIA
============================

Este script está diseñado para ejecutarse diariamente y extraer
automáticamente todos los reportes de SAP con la lógica de fechas
apropiada.

Uso:
- Programar en Task Scheduler de Windows para ejecución diaria
- Ejecutar manualmente para pruebas
- Genera logs detallados de la ejecución

Funcionalidades:
[OK] Ejecución automática diaria
[OK] Lógica de fechas inteligente
[OK] Logs detallados
[OK] Notificaciones de estado
[OK] Manejo de errores robusto
"""

import sys
import os
import json
import logging
from datetime import datetime
from automatizacion_reportes_sap import AutomatizacionSAP

# Configurar logging para ejecución diaria
def configurar_logging():
    """
    Configura el sistema de logging para ejecución diaria
    """
    # Crear directorio de logs si no existe
    log_dir = r"C:\Data\SAP_Automatizado\Logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Nombre del archivo de log con fecha
    fecha_log = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f"ejecucion_diaria_{fecha_log}.log")
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def cargar_configuracion():
    """
    Carga la configuración desde el archivo JSON
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'configuracion_reportes.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"[ERROR] Error cargando configuración: {e}")
        return None

def verificar_requisitos():
    """
    Verifica que se cumplan los requisitos para la ejecución
    """
    logger = logging.getLogger(__name__)
    
    # Verificar que SAP GUI esté disponible
    try:
        import win32com.client
        sap_gui_auto = win32com.client.GetObject("SAPGUI")
        if not sap_gui_auto:
            logger.error("[ERROR] SAP GUI no está disponible")
            return False
        logger.info("[OK] SAP GUI disponible")
    except Exception as e:
        logger.error(f"[ERROR] Error verificando SAP GUI: {e}")
        return False
    
    # Verificar directorios
    directorios = [
        r"C:\Data\SAP_Automatizado",
        r"C:\Data\SAP_Automatizado\Logs",
        r"C:\Data\SAP_Automatizado\Backup"
    ]
    
    for directorio in directorios:
        try:
            os.makedirs(directorio, exist_ok=True)
            logger.info(f"[OK] Directorio verificado: {directorio}")
        except Exception as e:
            logger.error(f"[ERROR] Error creando directorio {directorio}: {e}")
            return False
    
    return True

def enviar_notificacion(estado, mensaje, config):
    """
    Envía notificación del resultado de la ejecución
    """
    logger = logging.getLogger(__name__)
    
    if not config.get('notificaciones', {}).get('enviar_email', False):
        logger.info(" Notificaciones por email deshabilitadas")
        return
    
    # Aquí se podría implementar envío de email
    # Por ahora solo se registra en el log
    logger.info(f" Notificación: {estado} - {mensaje}")

def crear_resumen_ejecucion(resultado, inicio, fin):
    """
    Crea un resumen de la ejecución
    """
    logger = logging.getLogger(__name__)
    
    duracion = fin - inicio
    
    resumen = {
        'fecha_ejecucion': inicio.strftime('%Y-%m-%d %H:%M:%S'),
        'duracion_minutos': round(duracion.total_seconds() / 60, 2),
        'estado': 'EXITOSO' if resultado else 'FALLIDO',
        'hora_fin': fin.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Guardar resumen en archivo JSON
    resumen_dir = r"C:\Data\SAP_Automatizado\Logs"
    fecha_str = inicio.strftime('%Y%m%d')
    resumen_file = os.path.join(resumen_dir, f"resumen_{fecha_str}.json")
    
    try:
        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        logger.info(f"[LISTA] Resumen guardado: {resumen_file}")
    except Exception as e:
        logger.error(f"[ERROR] Error guardando resumen: {e}")
    
    return resumen

def main():
    """
    Función principal de ejecución diaria
    """
    # Configurar logging
    logger = configurar_logging()
    
    # Marcar inicio
    inicio_ejecucion = datetime.now()
    
    logger.info("[INICIO] INICIANDO EJECUCIÓN DIARIA DE REPORTES SAP")
    logger.info("=" * 80)
    logger.info(f"[FECHA] Fecha: {inicio_ejecucion.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"[SISTEMA] Usuario: {os.getenv('USERNAME', 'Desconocido')}")
    logger.info(f"[PC] Sistema: {os.getenv('COMPUTERNAME', 'Desconocido')}")
    logger.info("=" * 80)
    
    try:
        # Cargar configuración
        logger.info("[LISTA] Cargando configuración...")
        config = cargar_configuracion()
        if not config:
            logger.error("[ERROR] No se pudo cargar la configuración")
            return False
        
        # Verificar requisitos
        logger.info("[BUSCAR] Verificando requisitos...")
        if not verificar_requisitos():
            logger.error("[ERROR] Requisitos no cumplidos")
            return False
        
        # Crear instancia de automatización
        logger.info("[CONFIGURACION] Inicializando automatización SAP...")
        automatizacion = AutomatizacionSAP()
        
        # Ejecutar automatización
        logger.info(" Ejecutando extracción de reportes...")
        resultado = automatizacion.main()
        
        # Marcar fin
        fin_ejecucion = datetime.now()
        
        # Crear resumen
        resumen = crear_resumen_ejecucion(resultado, inicio_ejecucion, fin_ejecucion)
        
        # Enviar notificación
        if resultado:
            logger.info("[EXITO] EJECUCIÓN COMPLETADA EXITOSAMENTE")
            enviar_notificacion("EXITOSO", "Todos los reportes se extrajeron correctamente", config)
        else:
            logger.error("[ERROR] EJECUCIÓN FALLÓ")
            enviar_notificacion("FALLIDO", "Algunos reportes no se pudieron extraer", config)
        
        # Log final
        logger.info("=" * 80)
        logger.info("[DASHBOARD] ESTADÍSTICAS DE EJECUCIÓN")
        logger.info("=" * 80)
        logger.info(f"⏱ Duración total: {resumen['duracion_minutos']} minutos")
        logger.info(f"[GRAFICO] Estado: {resumen['estado']}")
        logger.info(f"[CARPETA] Directorio de salida: {automatizacion.output_dir}")
        logger.info("=" * 80)
        
        return resultado
        
    except KeyboardInterrupt:
        logger.warning("[ADVERTENCIA] Ejecución interrumpida por el usuario")
        return False
        
    except Exception as e:
        logger.error(f"[ERROR] Error inesperado en ejecución diaria: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"[ERROR] Error crítico: {e}")
        sys.exit(1)
