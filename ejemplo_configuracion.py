#!/usr/bin/env python3
"""
📋 EJEMPLO DE USO DEL SISTEMA DE CONFIGURACIÓN - OTIF MASTER
============================================================

Este script muestra cómo usar el sistema de configuración del OTIF Master
para cargar y modificar rutas de archivos.

Autor: OTIF Master
Fecha: 2025
"""

import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ejemplo_uso_configuracion():
    """
    Ejemplo de cómo usar el sistema de configuración.
    """
    
    logger.info("📋 EJEMPLO DE USO DEL SISTEMA DE CONFIGURACIÓN")
    logger.info("="*60)
    
    try:
        # Importar el módulo de configuración
        from scripts.configuracion_sistema import (
            cargar_configuracion, 
            guardar_configuracion,
            obtener_ruta_archivo,
            obtener_carpeta_salida,
            verificar_configuracion,
            mostrar_configuracion_actual
        )
        
        logger.info("✅ Módulo de configuración importado correctamente")
        
        # 1. Cargar configuración actual
        logger.info("\n📂 Paso 1: Cargando configuración actual...")
        config = cargar_configuracion()
        logger.info(f"✅ Configuración cargada con {len(config['rutas_archivos'])} rutas definidas")
        
        # 2. Mostrar configuración actual
        logger.info("\n📋 Paso 2: Mostrando configuración actual...")
        mostrar_configuracion_actual()
        
        # 3. Verificar configuración
        logger.info("\n🔍 Paso 3: Verificando configuración...")
        if verificar_configuracion():
            logger.info("✅ Configuración válida")
        else:
            logger.error("❌ Error en la configuración")
            return
        
        # 4. Ejemplos de uso de rutas
        logger.info("\n📁 Paso 4: Ejemplos de rutas obtenidas desde configuración...")
        
        # Obtener rutas de archivos
        rutas_archivos = [
            ("rep_plr_combinado", "Archivo combinado Rep PLR"),
            ("no_entregas_combinado", "Archivo combinado No Entregas"),
            ("vol_portafolio_combinado", "Archivo combinado Vol Portafolio"),
            ("datos_completos", "Archivo datos completos")
        ]
        
        for tipo_archivo, descripcion in rutas_archivos:
            try:
                ruta = obtener_ruta_archivo(tipo_archivo)
                logger.info(f"  • {descripcion}: {ruta}")
            except Exception as e:
                logger.error(f"  ❌ Error al obtener ruta para {tipo_archivo}: {str(e)}")
        
        # Obtener carpetas de salida
        logger.info("\n📂 Carpetas de salida:")
        carpetas_salida = [
            ("rep_plr_output", "Carpeta salida Rep PLR"),
            ("no_entregas_output", "Carpeta salida No Entregas"),
            ("vol_portafolio_output", "Carpeta salida Vol Portafolio"),
            ("output_unificado", "Carpeta output unificado"),
            ("output_final", "Carpeta output final")
        ]
        
        for tipo_carpeta, descripcion in carpetas_salida:
            try:
                carpeta = obtener_carpeta_salida(tipo_carpeta)
                logger.info(f"  • {descripcion}: {carpeta}")
            except Exception as e:
                logger.error(f"  ❌ Error al obtener carpeta para {tipo_carpeta}: {str(e)}")
        
        # 5. Ejemplo de modificación de configuración
        logger.info("\n⚙️ Paso 5: Ejemplo de modificación de configuración...")
        
        # Crear una copia de la configuración
        nueva_config = config.copy()
        
        # Modificar una ruta (ejemplo)
        ruta_original = nueva_config["rutas_archivos"]["output_unificado"]
        nueva_config["rutas_archivos"]["output_unificado"] = "Data/Output_Unificado_Backup"
        
        logger.info(f"  • Ruta original: {ruta_original}")
        logger.info(f"  • Nueva ruta: {nueva_config['rutas_archivos']['output_unificado']}")
        
        # Guardar la nueva configuración
        logger.info("\n💾 Guardando nueva configuración...")
        guardar_configuracion(nueva_config)
        logger.info("✅ Nueva configuración guardada")
        
        # Restaurar configuración original
        logger.info("\n🔄 Restaurando configuración original...")
        guardar_configuracion(config)
        logger.info("✅ Configuración original restaurada")
        
        # 6. Resumen final
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMEN DEL EJEMPLO")
        logger.info("="*60)
        logger.info("✅ Sistema de configuración funcionando correctamente")
        logger.info("✅ Rutas obtenidas desde configuración")
        logger.info("✅ Configuración modificable y persistente")
        logger.info("✅ Fallback robusto en caso de errores")
        
        logger.info("\n💡 Cómo usar en tus scripts:")
        logger.info("1. Importa el módulo de configuración")
        logger.info("2. Usa cargar_configuracion() para obtener la configuración")
        logger.info("3. Usa obtener_ruta_archivo() para rutas de archivos")
        logger.info("4. Usa obtener_carpeta_salida() para carpetas")
        logger.info("5. Usa verificar_configuracion() para validar")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error al importar módulo de configuración: {str(e)}")
        logger.info("💡 Asegúrate de que el archivo scripts/configuracion_sistema.py existe")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        return False

def ejemplo_crear_configuracion_personalizada():
    """
    Ejemplo de cómo crear una configuración personalizada.
    """
    
    logger.info("\n🎨 EJEMPLO DE CONFIGURACIÓN PERSONALIZADA")
    logger.info("="*60)
    
    try:
        from scripts.configuracion_sistema import guardar_configuracion
        
        # Crear configuración personalizada
        config_personalizada = {
            "rutas_archivos": {
                "rep_plr": "Mi_Data/Rep PLR",
                "no_entregas": "Mi_Data/No Entregas/2025",
                "vol_portafolio": "Mi_Data/Vol_Portafolio",
                "output_unificado": "Mi_Data/Output_Unificado",
                "output_final": "Mi_Data/Output/calculo_otif"
            },
            "archivos_principales": [
                "rep_plr.parquet",
                "no_entregas.parquet",
                "vol_portafolio.parquet",
                "datos_completos_con_no_entregas.parquet"
            ],
            "configuracion_personalizada": True,
            "descripcion": "Configuración de ejemplo personalizada"
        }
        
        logger.info("📝 Creando configuración personalizada...")
        logger.info("  • Rutas personalizadas con prefijo 'Mi_Data'")
        logger.info("  • Configuración marcada como personalizada")
        logger.info("  • Descripción incluida")
        
        # Guardar configuración personalizada
        guardar_configuracion(config_personalizada)
        logger.info("✅ Configuración personalizada guardada")
        
        # Mostrar la configuración
        logger.info("\n📋 Configuración personalizada creada:")
        for ruta, path in config_personalizada["rutas_archivos"].items():
            logger.info(f"  • {ruta}: {path}")
        
        logger.info("\n💡 Esta configuración se puede usar para:")
        logger.info("  • Proyectos específicos con rutas diferentes")
        logger.info("  • Entornos de desarrollo separados")
        logger.info("  • Configuraciones de diferentes usuarios")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error al crear configuración personalizada: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando ejemplos del sistema de configuración...")
    
    # Ejecutar ejemplo principal
    exito_principal = ejemplo_uso_configuracion()
    
    if exito_principal:
        # Ejecutar ejemplo de configuración personalizada
        ejemplo_crear_configuracion_personalizada()
        
        logger.info("\n🎉 ¡Ejemplos completados exitosamente!")
        logger.info("✅ El sistema de configuración está funcionando correctamente")
        logger.info("✅ Puedes usar estas funciones en tus propios scripts")
    else:
        logger.error("\n❌ Los ejemplos fallaron. Revisa los errores anteriores.")
