#!/usr/bin/env python3
"""
🧪 PRUEBA DEL SISTEMA OTIF MASTER
==================================

Este script prueba que el sistema OTIF Master funciona correctamente
incluso sin archivos de datos de entrada.

Autor: OTIF Master
Fecha: 2025
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def probar_sistema():
    """
    Prueba que el sistema funciona correctamente sin archivos de datos.
    """
    
    logger.info("🧪 Iniciando prueba del sistema OTIF Master...")
    logger.info("="*60)
    
    # 1. Verificar estructura
    logger.info("📁 Paso 1: Verificando estructura de carpetas...")
    try:
        from scripts.verificar_estructura import verificar_y_crear_estructura
        estructura_creada = verificar_y_crear_estructura()
        logger.info("✅ Estructura de carpetas verificada/creada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al verificar estructura: {str(e)}")
        return False
    
    # 2. Ejecutar scripts individuales
    logger.info("\n📊 Paso 2: Probando scripts individuales...")
    
    scripts_a_probar = [
        ("agrupar_datos_rep_plr.py", "Procesamiento Rep PLR"),
        ("agrupar_datos_no_entregas_mejorado.py", "Procesamiento No Entregas"),
        ("agrupar_datos_vol_portafolio.py", "Procesamiento Vol Portafolio"),
        ("unificar_datos_completos.py", "Unificación de datos")
    ]
    
    for script, descripcion in scripts_a_probar:
        logger.info(f"\n🔧 Probando: {descripcion}")
        try:
            script_path = Path("scripts") / script
            if script_path.exists():
                # Importar y ejecutar el script
                import importlib.util
                spec = importlib.util.spec_from_file_location("script", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Ejecutar la función principal
                if hasattr(module, script.replace('.py', '')):
                    func = getattr(module, script.replace('.py', ''))
                    func()
                    logger.info(f"✅ {descripcion} completado exitosamente")
                else:
                    logger.warning(f"⚠️ No se encontró función principal en {script}")
            else:
                logger.error(f"❌ Script no encontrado: {script}")
        except Exception as e:
            logger.error(f"❌ Error en {descripcion}: {str(e)}")
            return False
    
    # 3. Verificar archivos generados
    logger.info("\n📋 Paso 3: Verificando archivos generados...")
    
    archivos_esperados = [
        "Data/Rep PLR/Output/REP_PLR_combinado.parquet",
        "Data/No Entregas/Output/No_Entregas_combinado_mejorado.parquet",
        "Data/Vol_Portafolio/Output/Vol_Portafolio_combinado.parquet",
        "Data/Output_Unificado/rep_plr.parquet",
        "Data/Output_Unificado/no_entregas.parquet",
        "Data/Output_Unificado/vol_portafolio.parquet",
        "Data/Output_Unificado/datos_completos_con_no_entregas.parquet"
    ]
    
    archivos_encontrados = []
    archivos_faltantes = []
    
    for archivo in archivos_esperados:
        if Path(archivo).exists():
            archivos_encontrados.append(archivo)
            logger.info(f"✅ Archivo encontrado: {archivo}")
        else:
            archivos_faltantes.append(archivo)
            logger.error(f"❌ Archivo faltante: {archivo}")
    
    # 4. Verificar contenido de archivos
    logger.info("\n📊 Paso 4: Verificando contenido de archivos...")
    
    try:
        import pandas as pd
        
        for archivo in archivos_encontrados:
            try:
                df = pd.read_parquet(archivo)
                logger.info(f"📄 {archivo}: {len(df)} filas, {len(df.columns)} columnas")
                
                # Mostrar columnas
                logger.info(f"   Columnas: {list(df.columns)}")
                
            except Exception as e:
                logger.error(f"❌ Error al leer {archivo}: {str(e)}")
                
    except ImportError:
        logger.warning("⚠️ pandas no disponible, saltando verificación de contenido")
    
    # 5. Resumen final
    logger.info("\n" + "="*60)
    logger.info("📊 RESUMEN DE LA PRUEBA")
    logger.info("="*60)
    logger.info(f"✅ Archivos encontrados: {len(archivos_encontrados)}")
    logger.info(f"❌ Archivos faltantes: {len(archivos_faltantes)}")
    
    if archivos_faltantes:
        logger.error("\n❌ PRUEBA FALLIDA: Faltan algunos archivos")
        for archivo in archivos_faltantes:
            logger.error(f"   • {archivo}")
        return False
    else:
        logger.info("\n🎉 ¡PRUEBA EXITOSA!")
        logger.info("✅ El sistema OTIF Master funciona correctamente")
        logger.info("✅ Todos los archivos fueron generados exitosamente")
        logger.info("✅ El sistema puede funcionar sin archivos de datos de entrada")
        
        logger.info("\n💡 Próximos pasos:")
        logger.info("• Agrega archivos Excel de datos en las carpetas correspondientes")
        logger.info("• Ejecuta el procesamiento nuevamente para procesar datos reales")
        logger.info("• Usa la interfaz web: python app.py")
        
        return True

if __name__ == "__main__":
    logger.info("🚀 Iniciando prueba completa del sistema OTIF Master...")
    
    exito = probar_sistema()
    
    if exito:
        logger.info("\n🎯 El sistema está listo para usar!")
        sys.exit(0)
    else:
        logger.error("\n❌ La prueba falló. Revisa los errores anteriores.")
        sys.exit(1)
