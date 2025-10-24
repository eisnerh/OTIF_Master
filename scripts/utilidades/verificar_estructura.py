#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE ESTRUCTURA - OTIF MASTER
=========================================

Este script verifica y crea la estructura de carpetas necesaria para el sistema OTIF.
Si las carpetas no existen, las crea automáticamente usando la configuración del sistema.

Autor: OTIF Master
Fecha: 2025
"""

import os
import logging
from pathlib import Path

# Importar módulo de configuración
try:
    from configuracion_sistema import cargar_configuracion, verificar_configuracion
except ImportError:
    # Si no se puede importar, usar configuración por defecto
    def cargar_configuracion():
        return {
            "rutas_archivos": {
                "rep_plr": "Data/Rep PLR",
                "no_entregas": "Data/No Entregas/2025",
                "vol_portafolio": "Data/Vol_Portafolio",
                "output_unificado": "Data/Output_Unificado",
                "output_final": "Data/Output/calculo_otif"
            }
        }
    
    def verificar_configuracion():
        return True

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_y_crear_estructura():
    """
    Verifica y crea la estructura de carpetas necesaria para el sistema OTIF
    usando la configuración del sistema.
    """
    
    logger.info("🔍 Verificando estructura de carpetas del sistema OTIF...")
    
    # Cargar configuración
    config = cargar_configuracion()
    
    # Definir la estructura de carpetas necesaria basada en la configuración
    estructura_carpetas = [
        "Data",
        config["rutas_archivos"]["rep_plr"],
        f"{config['rutas_archivos']['rep_plr']}/Output",
        config["rutas_archivos"]["no_entregas"],
        f"{config['rutas_archivos']['no_entregas']}/Output",
        config["rutas_archivos"]["vol_portafolio"],
        f"{config['rutas_archivos']['vol_portafolio']}/Output",
        config["rutas_archivos"]["output_unificado"],
        config["rutas_archivos"]["output_final"]
    ]
    
    carpetas_creadas = []
    carpetas_existentes = []
    
    for carpeta in estructura_carpetas:
        path_carpeta = Path(carpeta)
        
        if path_carpeta.exists():
            carpetas_existentes.append(carpeta)
            logger.info(f"✅ Carpeta existente: {carpeta}")
        else:
            try:
                path_carpeta.mkdir(parents=True, exist_ok=True)
                carpetas_creadas.append(carpeta)
                logger.info(f"📁 Carpeta creada: {carpeta}")
            except Exception as e:
                logger.error(f"❌ Error al crear carpeta {carpeta}: {str(e)}")
    
    # Resumen final
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMEN DE VERIFICACIÓN DE ESTRUCTURA")
    logger.info("="*50)
    logger.info(f"📁 Carpetas existentes: {len(carpetas_existentes)}")
    logger.info(f"📁 Carpetas creadas: {len(carpetas_creadas)}")
    
    if carpetas_creadas:
        logger.info("\n🆕 Carpetas creadas:")
        for carpeta in carpetas_creadas:
            logger.info(f"  • {carpeta}")
    
    logger.info("\n✅ Verificación de estructura completada")
    
    return len(carpetas_creadas) > 0

def verificar_archivos_ejemplo():
    """
    Verifica si existen archivos de ejemplo y proporciona información sobre la estructura esperada
    usando la configuración del sistema.
    """
    
    logger.info("\n📋 Verificando archivos de ejemplo...")
    
    # Cargar configuración
    config = cargar_configuracion()
    
    archivos_esperados = {
        config["rutas_archivos"]["rep_plr"]: "Archivos Excel con hoja 'REP PLR'",
        config["rutas_archivos"]["no_entregas"]: "Archivos Excel con formato '*-2025-Devoluciones.xlsx' y hoja 'Z_DEVO_ALV'",
        config["rutas_archivos"]["vol_portafolio"]: "Archivo 'VOL POR PORTAFOLIO ENE-2025.xlsx'"
    }
    
    archivos_faltantes = []
    
    for ruta, descripcion in archivos_esperados.items():
        path_ruta = Path(ruta)
        
        if ruta == config["rutas_archivos"]["vol_portafolio"]:
            # Buscar archivo específico de Vol Portafolio
            archivo_vol = path_ruta / "VOL POR PORTAFOLIO ENE-2025.xlsx"
            if archivo_vol.exists():
                logger.info(f"✅ Archivo encontrado: {archivo_vol}")
            else:
                archivos_faltantes.append(f"{ruta}/VOL POR PORTAFOLIO ENE-2025.xlsx")
                logger.warning(f"⚠️ Archivo no encontrado: {archivo_vol}")
        else:
            # Buscar archivos Excel en las carpetas
            archivos_excel = list(path_ruta.glob("*.xlsx"))
            if archivos_excel:
                logger.info(f"✅ Archivos Excel encontrados en {ruta}: {len(archivos_excel)} archivos")
                for archivo in archivos_excel[:3]:  # Mostrar solo los primeros 3
                    logger.info(f"  • {archivo.name}")
                if len(archivos_excel) > 3:
                    logger.info(f"  • ... y {len(archivos_excel) - 3} archivos más")
            else:
                archivos_faltantes.append(ruta)
                logger.warning(f"⚠️ No se encontraron archivos Excel en: {ruta}")
    
    if archivos_faltantes:
        logger.info("\n📝 INFORMACIÓN SOBRE ARCHIVOS ESPERADOS:")
        logger.info("="*50)
        for ruta, descripcion in archivos_esperados.items():
            logger.info(f"📁 {ruta}:")
            logger.info(f"   {descripcion}")
        
        logger.info("\n💡 CONSEJOS:")
        logger.info("• Si no tienes archivos de datos, el sistema creará archivos parquet vacíos")
        logger.info("• Los archivos parquet vacíos permitirán que el sistema funcione correctamente")
        logger.info("• Puedes agregar archivos de datos más tarde y ejecutar el procesamiento nuevamente")
    
    return len(archivos_faltantes) == 0

def mostrar_configuracion_actual():
    """
    Muestra la configuración actual del sistema.
    """
    try:
        config = cargar_configuracion()
        logger.info("\n⚙️ CONFIGURACIÓN ACTUAL DEL SISTEMA:")
        logger.info("="*50)
        
        for ruta, path in config["rutas_archivos"].items():
            logger.info(f"  {ruta}: {path}")
        
        logger.info("\n📄 ARCHIVOS PRINCIPALES:")
        for archivo in config.get("archivos_principales", []):
            logger.info(f"  • {archivo}")
        
        if config.get("ultima_actualizacion"):
            logger.info(f"\n🕒 Última actualización: {config['ultima_actualizacion']}")
        
    except Exception as e:
        logger.error(f"❌ Error al mostrar configuración: {str(e)}")

if __name__ == "__main__":
    logger.info("🚀 Iniciando verificación de estructura del sistema OTIF...")
    
    # Mostrar configuración actual
    mostrar_configuracion_actual()
    
    # Verificar y crear estructura de carpetas
    estructura_creada = verificar_y_crear_estructura()
    
    # Verificar archivos de ejemplo
    archivos_completos = verificar_archivos_ejemplo()
    
    logger.info("\n🎉 Verificación completada exitosamente!")
    
    if estructura_creada:
        logger.info("📁 Se crearon nuevas carpetas en la estructura")
    
    if not archivos_completos:
        logger.info("⚠️ Algunos archivos de datos no están presentes, pero el sistema funcionará con archivos vacíos")
    
    logger.info("\n✅ El sistema está listo para funcionar")
