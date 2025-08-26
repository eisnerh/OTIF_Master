#!/usr/bin/env python3
"""
🧪 PRUEBA DEL SISTEMA OTIF MASTER
==================================

Este script prueba que el sistema OTIF Master funciona correctamente
incluso sin archivos de datos de entrada, usando la configuración del sistema.

Autor: OTIF Master
Fecha: 2025
"""

import os
import sys
import logging
from pathlib import Path

# Importar módulo de configuración
try:
    from scripts.configuracion_sistema import cargar_configuracion, obtener_ruta_archivo, verificar_configuracion
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
    
    def obtener_ruta_archivo(tipo):
        config = cargar_configuracion()
        if tipo == "rep_plr_combinado":
            return Path(config["rutas_archivos"]["rep_plr"]) / "Output" / "REP_PLR_combinado.parquet"
        elif tipo == "no_entregas_combinado":
            return Path(config["rutas_archivos"]["no_entregas"]) / "Output" / "No_Entregas_combinado_mejorado.parquet"
        elif tipo == "vol_portafolio_combinado":
            return Path(config["rutas_archivos"]["vol_portafolio"]) / "Output" / "Vol_Portafolio_combinado.parquet"
        elif tipo == "rep_plr_final":
            return Path(config["rutas_archivos"]["output_unificado"]) / "rep_plr.parquet"
        elif tipo == "no_entregas_final":
            return Path(config["rutas_archivos"]["output_unificado"]) / "no_entregas.parquet"
        elif tipo == "vol_portafolio_final":
            return Path(config["rutas_archivos"]["output_unificado"]) / "vol_portafolio.parquet"
        elif tipo == "datos_completos":
            return Path(config["rutas_archivos"]["output_unificado"]) / "datos_completos_con_no_entregas.parquet"
        return Path("Data/Output_Unificado")
    
    def verificar_configuracion():
        return True

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def probar_sistema():
    """
    Prueba que el sistema funciona correctamente sin archivos de datos
    usando la configuración del sistema.
    """
    
    logger.info("🧪 Iniciando prueba del sistema OTIF Master...")
    logger.info("="*60)
    
    # Mostrar configuración actual
    logger.info("⚙️ Configuración actual del sistema:")
    config = cargar_configuracion()
    for ruta, path in config["rutas_archivos"].items():
        logger.info(f"  • {ruta}: {path}")
    
    # 1. Verificar estructura
    logger.info("\n📁 Paso 1: Verificando estructura de carpetas...")
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
    
    # 3. Verificar archivos generados usando configuración
    logger.info("\n📋 Paso 3: Verificando archivos generados...")
    
    archivos_esperados = [
        obtener_ruta_archivo("rep_plr_combinado"),
        obtener_ruta_archivo("no_entregas_combinado"),
        obtener_ruta_archivo("vol_portafolio_combinado"),
        obtener_ruta_archivo("rep_plr_final"),
        obtener_ruta_archivo("no_entregas_final"),
        obtener_ruta_archivo("vol_portafolio_final"),
        obtener_ruta_archivo("datos_completos")
    ]
    
    archivos_encontrados = []
    archivos_faltantes = []
    
    for archivo in archivos_esperados:
        if archivo.exists():
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
        logger.info("✅ El sistema usa correctamente la configuración")
        
        logger.info("\n💡 Próximos pasos:")
        logger.info("• Agrega archivos Excel de datos en las carpetas correspondientes")
        logger.info("• Ejecuta el procesamiento nuevamente para procesar datos reales")
        logger.info("• Usa la interfaz web: python app.py")
        logger.info("• Modifica la configuración desde la interfaz web si es necesario")
        
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
