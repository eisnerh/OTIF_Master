#!/usr/bin/env python3
"""
🎯 OTIF MASTER - SCRIPT MAESTRO COMPLETO
========================================

Este script ejecuta todos los procesos de procesamiento de datos OTIF en orden:
1. Procesar datos Rep PLR
2. Procesar datos No Entregas
3. Procesar datos Vol Portafolio
4. Unificar todos los datos
5. Copiar archivos a carpeta final
6. Crear resumen final

Autor: OTIF Master
Fecha: 2025
"""

import os
import sys
import time
import logging
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesamiento_maestro.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProcesamientoMaestro:
    def __init__(self):
        self.scripts_dir = Path("scripts")
        self.data_dir = Path("Data")
        self.output_dir = Path("Data/Output/calculo_otif")
        self.archivos_procesados = []
        self.errores = []
        self.inicio_tiempo = None
        
    def verificar_estructura(self):
        """Verifica que la estructura de carpetas esté correcta."""
        logger.info("🔍 Verificando estructura de carpetas...")
        
        carpetas_requeridas = [
            self.scripts_dir,
            self.data_dir / "Rep PLR",
            self.data_dir / "No Entregas" / "2025",
            self.data_dir / "Vol_Portafolio"
        ]
        
        for carpeta in carpetas_requeridas:
            if not carpeta.exists():
                logger.error(f"❌ Carpeta no encontrada: {carpeta}")
                return False
            else:
                logger.info(f"✅ Carpeta encontrada: {carpeta}")
        
        # Crear carpeta de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Carpeta de salida: {self.output_dir}")
        
        return True
    
    def ejecutar_script(self, nombre_script, descripcion):
        """Ejecuta un script específico con optimizaciones y manejo robusto de errores."""
        script_path = self.scripts_dir / nombre_script
        
        if not script_path.exists():
            error_msg = f"❌ Script no encontrado: {script_path}"
            logger.error(error_msg)
            self.errores.append(error_msg)
            return False
        
        logger.info(f"🚀 Ejecutando: {descripcion}")
        logger.info(f"📁 Script: {script_path}")
        
        # Configuración optimizada para Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        try:
            # Ejecutar script con optimizaciones
            resultado = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                encoding='cp1252',  # Encoding específico para Windows
                errors='replace',   # Reemplazar caracteres problemáticos
                timeout=600,        # Timeout de 10 minutos
                startupinfo=startupinfo,
                env=dict(os.environ, PYTHONIOENCODING='cp1252')
            )
            
            if resultado.returncode == 0:
                logger.info(f"✅ {descripcion} completado exitosamente")
                self.archivos_procesados.append(nombre_script)
                return True
            else:
                error_msg = f"❌ Error en {descripcion}: {resultado.stderr}"
                logger.error(error_msg)
                self.errores.append(error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = f"❌ Timeout en {descripcion} (10 minutos)"
            logger.error(error_msg)
            self.errores.append(error_msg)
            return False
        except UnicodeDecodeError as e:
            error_msg = f"❌ Error de encoding en {descripcion}: {str(e)}"
            logger.error(error_msg)
            self.errores.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ Error al ejecutar {descripcion}: {str(e)}"
            logger.error(error_msg)
            self.errores.append(error_msg)
            return False
    
    def copiar_archivos_finales(self):
        """Copia todos los archivos generados a la carpeta final."""
        logger.info("📁 Copiando archivos a carpeta final...")
        
        archivos_a_copiar = [
            "Data/Rep PLR/Output/REP_PLR_combinado.parquet",
            "Data/No Entregas/Output/No_Entregas_combinado_mejorado.parquet",
            "Data/Vol_Portafolio/Output/Vol_Portafolio_combinado.parquet",
            "Data/Output_Unificado/rep_plr.parquet",
            "Data/Output_Unificado/no_entregas.parquet",
            "Data/Output_Unificado/vol_portafolio.parquet",
            "Data/Output_Unificado/rep_plr_vol_portafolio_unido.parquet",
            "Data/Output_Unificado/datos_completos_con_no_entregas.parquet"
        ]
        
        archivos_copiados = []
        
        for archivo_origen in archivos_a_copiar:
            origen = Path(archivo_origen)
            if origen.exists():
                destino = self.output_dir / origen.name
                try:
                    shutil.copy2(origen, destino)
                    archivos_copiados.append(archivo_origen)
                    logger.info(f"✅ Copiado: {origen.name}")
                except Exception as e:
                    error_msg = f"❌ Error al copiar {archivo_origen}: {str(e)}"
                    logger.error(error_msg)
                    self.errores.append(error_msg)
            else:
                logger.warning(f"⚠️ Archivo no encontrado: {archivo_origen}")
        
        return archivos_copiados
    
    def crear_resumen_final(self):
        """Crea un archivo de resumen con información de todos los archivos generados."""
        logger.info("📊 Creando resumen final...")
        
        resumen = {
            "fecha_procesamiento": datetime.now().isoformat(),
            "tiempo_total_segundos": (datetime.now() - self.inicio_tiempo).total_seconds() if self.inicio_tiempo else 0,
            "scripts_ejecutados": self.archivos_procesados,
            "errores": self.errores,
            "archivos_generados": [],
            "estadisticas": {}
        }
        
        # Analizar archivos principales
        archivos_principales = [
            "REP_PLR_combinado.parquet",
            "No_Entregas_combinado_mejorado.parquet", 
            "Vol_Portafolio_combinado.parquet",
            "rep_plr.parquet",
            "no_entregas.parquet",
            "vol_portafolio.parquet",
            "rep_plr_vol_portafolio_unido.parquet",
            "datos_completos_con_no_entregas.parquet"
        ]
        
        try:
            import pandas as pd
            
            for archivo in archivos_principales:
                ruta_archivo = self.output_dir / archivo
                if ruta_archivo.exists():
                    try:
                        df = pd.read_parquet(ruta_archivo)
                        info_archivo = {
                            "nombre": archivo,
                            "filas": len(df),
                            "columnas": len(df.columns),
                            "tamaño_mb": ruta_archivo.stat().st_size / (1024*1024)
                        }
                        resumen["archivos_generados"].append(info_archivo)
                        
                        # Estadísticas específicas
                        if "REP_PLR" in archivo:
                            resumen["estadisticas"]["rep_plr"] = {
                                "total_registros": len(df),
                                "centros_unicos": df['Centro'].nunique() if 'Centro' in df.columns else 0
                            }
                        elif "No_Entregas" in archivo:
                            resumen["estadisticas"]["no_entregas"] = {
                                "total_registros": len(df),
                                "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0
                            }
                        elif "Vol_Portafolio" in archivo:
                            resumen["estadisticas"]["vol_portafolio"] = {
                                "total_registros": len(df),
                                "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0,
                                "zonas_unicas": df['Zona'].nunique() if 'Zona' in df.columns else 0
                            }
                        elif "rep_plr" in archivo:
                            resumen["estadisticas"]["rep_plr_final"] = {
                                "total_registros": len(df),
                                "centros_unicos": df['Centro'].nunique() if 'Centro' in df.columns else 0
                            }
                        elif "no_entregas" in archivo:
                            resumen["estadisticas"]["no_entregas_final"] = {
                                "total_registros": len(df),
                                "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0
                            }
                        elif "vol_portafolio" in archivo and "unido" not in archivo:
                            resumen["estadisticas"]["vol_portafolio_final"] = {
                                "total_registros": len(df),
                                "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0
                            }
                        elif "rep_plr_vol_portafolio_unido" in archivo:
                            resumen["estadisticas"]["rep_plr_vol_portafolio_unido"] = {
                                "total_registros": len(df),
                                "columnas_totales": len(df.columns),
                                "registros_con_match": len(df.dropna(subset=[col for col in df.columns if 'vol_portafolio' in col]))
                            }
                        elif "datos_completos_con_no_entregas" in archivo:
                            resumen["estadisticas"]["datos_completos_con_no_entregas"] = {
                                "total_registros": len(df),
                                "columnas_totales": len(df.columns),
                                "registros_con_match": len(df.dropna(subset=[col for col in df.columns if 'no_entregas' in col]))
                            }
                            
                    except Exception as e:
                        logger.error(f"Error al leer {archivo}: {str(e)}")
                        
        except ImportError:
            logger.warning("⚠️ Pandas no disponible, omitiendo análisis de archivos")
        
        # Guardar resumen
        archivo_resumen = self.output_dir / "resumen_procesamiento.json"
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Resumen guardado en: {archivo_resumen}")
        return resumen
    
    def replicar_vol_portafolio(self):
        """Replica el archivo Vol_Portafolio_combinado.parquet como paso final."""
        logger.info("🔄 Replicando archivo Vol_Portafolio...")
        
        try:
            archivo_origen = Path("Data/Vol_Portafolio/Output/Vol_Portafolio_combinado.parquet")
            
            if not archivo_origen.exists():
                logger.error(f"❌ El archivo {archivo_origen} no existe")
                return False
            
            archivo_destino = self.output_dir / "Vol_Portafolio_combinado_replicado.parquet"
            shutil.copy2(archivo_origen, archivo_destino)
            
            if archivo_destino.exists():
                logger.info(f"✅ Archivo replicado exitosamente: {archivo_destino}")
                return True
            else:
                logger.error("❌ Error: El archivo no se copió correctamente")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al replicar el archivo: {str(e)}")
            return False
    
    def ejecutar_procesamiento_completo(self):
        """Ejecuta todo el procesamiento en orden."""
        logger.info("🎯 INICIANDO PROCESAMIENTO MAESTRO OTIF")
        logger.info("=" * 60)
        
        self.inicio_tiempo = datetime.now()
        
        # Verificar estructura
        if not self.verificar_estructura():
            logger.error("❌ Error en la estructura de carpetas. Abortando.")
            return False
        
        # Paso 1: Procesar Rep PLR
        logger.info("\n📋 PASO 1: PROCESANDO DATOS REP PLR")
        logger.info("-" * 40)
        if not self.ejecutar_script("agrupar_datos_rep_plr.py", "Procesamiento Rep PLR"):
            logger.error("❌ Falló el procesamiento de Rep PLR")
            return False
        
        # Paso 2: Procesar No Entregas
        logger.info("\n📋 PASO 2: PROCESANDO DATOS NO ENTREGAS")
        logger.info("-" * 40)
        if not self.ejecutar_script("agrupar_datos_no_entregas_mejorado.py", "Procesamiento No Entregas"):
            logger.error("❌ Falló el procesamiento de No Entregas")
            return False
        
        # Paso 3: Procesar Vol Portafolio
        logger.info("\n📋 PASO 3: PROCESANDO DATOS VOL PORTAFOLIO")
        logger.info("-" * 40)
        if not self.ejecutar_script("agrupar_datos_vol_portafolio.py", "Procesamiento Vol Portafolio"):
            logger.error("❌ Falló el procesamiento de Vol Portafolio")
            return False
        
        # Paso 4: Unificar datos
        logger.info("\n📋 PASO 4: UNIFICANDO DATOS")
        logger.info("-" * 40)
        if not self.ejecutar_script("unificar_datos_completos.py", "Unificación de datos"):
            logger.warning("⚠️ Falló la unificación de datos, continuando...")
        
        # Paso 5: Copiar archivos a carpeta final
        logger.info("\n📋 PASO 5: COPIANDO ARCHIVOS A CARPETA FINAL")
        logger.info("-" * 40)
        archivos_copiados = self.copiar_archivos_finales()
        
        # Paso 6: Crear resumen final
        logger.info("\n📋 PASO 6: CREANDO RESUMEN FINAL")
        logger.info("-" * 40)
        resumen = self.crear_resumen_final()
        
        # Paso 7: Replicar archivo Vol_Portafolio
        logger.info("\n📋 PASO 7: REPLICANDO ARCHIVO VOL_PORTAFOLIO")
        logger.info("-" * 40)
        self.replicar_vol_portafolio()
        
        # Resumen final
        tiempo_total = (datetime.now() - self.inicio_tiempo).total_seconds()
        logger.info("\n🎉 ¡PROCESAMIENTO MAESTRO COMPLETADO!")
        logger.info("=" * 60)
        logger.info(f"⏱️ Tiempo total: {tiempo_total:.2f} segundos")
        logger.info(f"✅ Scripts ejecutados: {len(self.archivos_procesados)}")
        logger.info(f"📁 Archivos copiados: {len(archivos_copiados)}")
        logger.info(f"❌ Errores: {len(self.errores)}")
        logger.info(f"📊 Archivos generados: {len(resumen.get('archivos_generados', []))}")
        logger.info(f"📂 Carpeta de salida: {self.output_dir}")
        
        if self.errores:
            logger.warning("\n⚠️ Errores encontrados:")
            for error in self.errores:
                logger.warning(f"  • {error}")
        
        return True

def main():
    """Función principal."""
    print("🎯 PROCESAMIENTO MAESTRO OTIF")
    print("=" * 60)
    
    procesador = ProcesamientoMaestro()
    
    try:
        if procesador.ejecutar_procesamiento_completo():
            print("\n✅ ¡PROCESAMIENTO COMPLETADO EXITOSAMENTE!")
            print(f"📂 Revisa los archivos en: {procesador.output_dir}")
            return 0
        else:
            print("\n❌ El procesamiento falló. Revisa los logs.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n👋 Procesamiento interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
