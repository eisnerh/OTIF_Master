#!/usr/bin/env python3
"""
⚙️ CONFIGURACIÓN DEL SISTEMA OTIF MASTER
========================================

Módulo para manejar la configuración del sistema OTIF Master.
Proporciona funciones para cargar y usar la configuración de rutas.

Autor: OTIF Master
Fecha: 2025
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def cargar_configuracion():
    """
    Carga la configuración de rutas desde el archivo JSON.
    Si no existe, crea una configuración por defecto.
    """
    try:
        with open('configuracion_rutas.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info("✅ Configuración cargada desde configuracion_rutas.json")
            return config
    except FileNotFoundError:
        logger.warning("⚠️ Archivo de configuración no encontrado. Creando configuración por defecto...")
        return crear_configuracion_por_defecto()
    except Exception as e:
        logger.error(f"❌ Error al cargar configuración: {str(e)}")
        logger.info("🔄 Usando configuración por defecto...")
        return crear_configuracion_por_defecto()

def crear_configuracion_por_defecto():
    """
    Crea una configuración por defecto y la guarda en el archivo JSON.
    """
    config_default = {
        "rutas_archivos": {
            "rep_plr": "Data/Rep PLR",
            "no_entregas": "Data/No Entregas/2025",
            "vol_portafolio": "Data/Vol_Portafolio",
            "output_unificado": "Data/Output_Unificado",
            "output_final": "Data/Output/calculo_otif"
        },
        "archivos_principales": [
            "rep_plr.parquet",
            "no_entregas.parquet", 
            "vol_portafolio.parquet",
            "datos_completos_con_no_entregas.parquet"
        ],
        "ultima_actualizacion": None
    }
    
    guardar_configuracion(config_default)
    logger.info("✅ Configuración por defecto creada y guardada")
    return config_default

def guardar_configuracion(config):
    """
    Guarda la configuración en el archivo JSON.
    """
    try:
        config["ultima_actualizacion"] = datetime.now().isoformat()
        with open('configuracion_rutas.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info("✅ Configuración guardada en configuracion_rutas.json")
    except Exception as e:
        logger.error(f"❌ Error al guardar configuración: {str(e)}")

def obtener_ruta_archivo(tipo_archivo):
    """
    Obtiene la ruta completa para un tipo de archivo específico.
    
    Args:
        tipo_archivo (str): Tipo de archivo ('rep_plr', 'no_entregas', 'vol_portafolio', etc.)
    
    Returns:
        Path: Ruta completa del archivo
    """
    config = cargar_configuracion()
    
    if tipo_archivo == "rep_plr_combinado":
        return Path(config["rutas_archivos"]["rep_plr"]) / "Output" / "REP_PLR_combinado.parquet"
    elif tipo_archivo == "no_entregas_combinado":
        return Path(config["rutas_archivos"]["no_entregas"]) / "Output" / "No_Entregas_combinado_mejorado.parquet"
    elif tipo_archivo == "vol_portafolio_combinado":
        return Path(config["rutas_archivos"]["vol_portafolio"]) / "Output" / "Vol_Portafolio_combinado.parquet"
    elif tipo_archivo == "rep_plr_final":
        return Path(config["rutas_archivos"]["output_unificado"]) / "rep_plr.parquet"
    elif tipo_archivo == "no_entregas_final":
        return Path(config["rutas_archivos"]["output_unificado"]) / "no_entregas.parquet"
    elif tipo_archivo == "vol_portafolio_final":
        return Path(config["rutas_archivos"]["output_unificado"]) / "vol_portafolio.parquet"
    elif tipo_archivo == "datos_completos":
        return Path(config["rutas_archivos"]["output_unificado"]) / "datos_completos_con_no_entregas.parquet"
    else:
        raise ValueError(f"Tipo de archivo no reconocido: {tipo_archivo}")

def obtener_carpeta_salida(tipo_carpeta):
    """
    Obtiene la ruta de una carpeta de salida específica.
    
    Args:
        tipo_carpeta (str): Tipo de carpeta ('rep_plr_output', 'no_entregas_output', etc.)
    
    Returns:
        Path: Ruta de la carpeta
    """
    config = cargar_configuracion()
    
    if tipo_carpeta == "rep_plr_output":
        return Path(config["rutas_archivos"]["rep_plr"]) / "Output"
    elif tipo_carpeta == "no_entregas_output":
        return Path(config["rutas_archivos"]["no_entregas"]) / "Output"
    elif tipo_carpeta == "vol_portafolio_output":
        return Path(config["rutas_archivos"]["vol_portafolio"]) / "Output"
    elif tipo_carpeta == "output_unificado":
        return Path(config["rutas_archivos"]["output_unificado"])
    elif tipo_carpeta == "output_final":
        return Path(config["rutas_archivos"]["output_final"])
    else:
        raise ValueError(f"Tipo de carpeta no reconocido: {tipo_carpeta}")

def crear_carpeta_si_no_existe(ruta_carpeta):
    """
    Crea una carpeta si no existe.
    
    Args:
        ruta_carpeta (Path): Ruta de la carpeta a crear
    
    Returns:
        bool: True si se creó o ya existía, False si hubo error
    """
    try:
        ruta_carpeta.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Carpeta verificada/creada: {ruta_carpeta}")
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear carpeta {ruta_carpeta}: {str(e)}")
        return False

def verificar_configuracion():
    """
    Verifica que la configuración sea válida y crea las carpetas necesarias.
    
    Returns:
        bool: True si la configuración es válida, False en caso contrario
    """
    try:
        config = cargar_configuracion()
        
        # Verificar que todas las rutas estén definidas
        rutas_requeridas = [
            "rep_plr", "no_entregas", "vol_portafolio", 
            "output_unificado", "output_final"
        ]
        
        for ruta in rutas_requeridas:
            if ruta not in config["rutas_archivos"]:
                logger.error(f"❌ Ruta faltante en configuración: {ruta}")
                return False
        
        # Crear carpetas de salida
        carpetas_a_crear = [
            obtener_carpeta_salida("rep_plr_output"),
            obtener_carpeta_salida("no_entregas_output"),
            obtener_carpeta_salida("vol_portafolio_output"),
            obtener_carpeta_salida("output_unificado"),
            obtener_carpeta_salida("output_final")
        ]
        
        for carpeta in carpetas_a_crear:
            if not crear_carpeta_si_no_existe(carpeta):
                return False
        
        logger.info("✅ Configuración verificada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al verificar configuración: {str(e)}")
        return False

def mostrar_configuracion_actual():
    """
    Muestra la configuración actual en los logs.
    """
    try:
        config = cargar_configuracion()
        logger.info("📋 CONFIGURACIÓN ACTUAL:")
        logger.info("="*50)
        
        for ruta, path in config["rutas_archivos"].items():
            logger.info(f"  {ruta}: {path}")
        
        logger.info("\n📄 ARCHIVOS PRINCIPALES:")
        for archivo in config["archivos_principales"]:
            logger.info(f"  • {archivo}")
        
        if config.get("ultima_actualizacion"):
            logger.info(f"\n🕒 Última actualización: {config['ultima_actualizacion']}")
        
    except Exception as e:
        logger.error(f"❌ Error al mostrar configuración: {str(e)}")

if __name__ == "__main__":
    # Configurar logging para pruebas
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🧪 Probando módulo de configuración...")
    
    # Probar carga de configuración
    config = cargar_configuracion()
    print(f"✅ Configuración cargada: {len(config['rutas_archivos'])} rutas definidas")
    
    # Probar verificación
    if verificar_configuracion():
        print("✅ Configuración verificada correctamente")
    else:
        print("❌ Error en la verificación de configuración")
    
    # Mostrar configuración
    mostrar_configuracion_actual()
