import pandas as pd
import os
from pathlib import Path
import logging
import concurrent.futures
import gc

# Importar módulo de configuración
try:
    from configuracion_sistema import cargar_configuracion, obtener_carpeta_salida, verificar_configuracion
except ImportError:
    # Si no se puede importar, usar rutas por defecto
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
    
    def obtener_carpeta_salida(tipo):
        config = cargar_configuracion()
        if tipo == "vol_portafolio_output":
            return Path(config["rutas_archivos"]["vol_portafolio"]) / "Output"
        return Path("Data/Vol_Portafolio/Output")
    
    def verificar_configuracion():
        return True

# Configurar logging con nivel más alto para reducir operaciones innecesarias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Solo configurar nivel INFO para el logger principal
logger.setLevel(logging.INFO)

def agrupar_datos_vol_portafolio():
    """
    Agrupa los datos de las 4 hojas del archivo Excel en la carpeta Vol_Portafolio
    y los guarda como un archivo parquet usando la configuración del sistema.
    """
    
    # Verificar configuración al inicio
    logger.info("⚙️ Verificando configuración del sistema...")
    if not verificar_configuracion():
        logger.error("❌ Error en la configuración del sistema")
        return
    
    # Cargar configuración
    config = cargar_configuracion()
    
    # Definir la ruta del archivo desde la configuración
    carpeta_vol_portafolio = Path(config["rutas_archivos"]["vol_portafolio"])
    archivo_excel = carpeta_vol_portafolio / "VOL POR PORTAFOLIO ENE-2025.xlsx"
    
    logger.info(f"📁 Usando carpeta Vol Portafolio: {carpeta_vol_portafolio}")
    logger.info(f"📄 Buscando archivo: {archivo_excel.name}")
    
    # Verificar que el archivo existe
    if not archivo_excel.exists():
        logger.warning(f"El archivo {archivo_excel} no existe. Creando archivo parquet vacío...")
        
        # Obtener carpeta de salida desde la configuración
        carpeta_salida = obtener_carpeta_salida("vol_portafolio_output")
        
        # Crear DataFrame vacío con estructura básica
        df_combinado = pd.DataFrame({
            'Entrega': [],
            'Familia': [],
            'Zona': [],
            'hoja_origen': [],
            'archivo_origen': []
        })
        
        logger.info("✅ DataFrame vacío creado con estructura básica")
    else:
        try:
            # Leer el archivo Excel para ver las hojas disponibles
            excel_file = pd.ExcelFile(archivo_excel, engine='openpyxl')
            hojas_disponibles = excel_file.sheet_names
            
            logger.info(f"Archivo encontrado: {archivo_excel.name}")
            logger.info(f"Hojas disponibles: {hojas_disponibles}")
            logger.info(f"Total de hojas: {len(hojas_disponibles)}")
            
            # Lista para almacenar todos los DataFrames
            dataframes = []
            
            # Función para procesar una hoja
            def procesar_hoja(hoja):
                try:
                    logger.info(f"Procesando hoja: {hoja}")
                    
                    # Leer la hoja con parámetros optimizados
                    df = pd.read_excel(
                        archivo_excel, 
                        sheet_name=hoja,
                        engine='openpyxl',
                        dtype_backend='numpy_nullable'  # Usar backend optimizado
                    )
                    
                    # Agregar columna para identificar la hoja de origen
                    df['hoja_origen'] = hoja
                    
                    # Agregar columna para identificar el archivo de origen
                    df['archivo_origen'] = archivo_excel.name
                    
                    logger.info(f"Se agregaron {len(df)} filas de la hoja {hoja}")
                    
                    # Mostrar información básica de la hoja
                    logger.info(f"  - Columnas: {len(df.columns)}")
                    logger.info(f"  - Filas: {len(df)}")
                    
                    return df
                    
                except Exception as e:
                    logger.error(f"Error al procesar la hoja {hoja}: {str(e)}")
                    return None
            
            # Usar procesamiento paralelo para procesar las hojas
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                resultados = list(executor.map(procesar_hoja, hojas_disponibles))
            
            # Filtrar los resultados None
            dataframes = [df for df in resultados if df is not None]
            
            if not dataframes:
                logger.warning("No se pudieron leer datos de ninguna hoja. Creando archivo parquet vacío...")
                
                # Crear DataFrame vacío con estructura básica
                df_combinado = pd.DataFrame({
                    'Entrega': [],
                    'Familia': [],
                    'Zona': [],
                    'hoja_origen': [],
                    'archivo_origen': []
                })
                
                logger.info("✅ DataFrame vacío creado con estructura básica")
            else:
                # Combinar todos los DataFrames de manera eficiente
                logger.info("Combinando todos los DataFrames...")
                df_combinado = pd.concat(dataframes, ignore_index=True)
                
                # Liberar memoria
                del dataframes
                gc.collect()
                
                logger.info(f"DataFrame combinado: {len(df_combinado)} filas y {len(df_combinado.columns)} columnas")
                
                # Mostrar información sobre las columnas
                logger.info("Columnas del DataFrame combinado:")
                for i, col in enumerate(df_combinado.columns, 1):
                    logger.info(f"{i}. {col}")
        except Exception as e:
            logger.error(f"Error al procesar el archivo Excel: {str(e)}. Creando archivo parquet vacío...")
            
            # Crear DataFrame vacío con estructura básica
            df_combinado = pd.DataFrame({
                'Entrega': [],
                'Familia': [],
                'Zona': [],
                'hoja_origen': [],
                'archivo_origen': []
            })
            
            logger.info("✅ DataFrame vacío creado con estructura básica")
    
    # Obtener carpeta de salida desde la configuración
    carpeta_salida = obtener_carpeta_salida("vol_portafolio_output")
    
    # Guardar como archivo parquet con compresión optimizada
    archivo_parquet = carpeta_salida / "Vol_Portafolio_combinado.parquet"
    
    # Verificar si el archivo ya existe
    archivo_existe = archivo_parquet.exists()
    
    try:
        df_combinado.to_parquet(
            archivo_parquet, 
            index=False,
            compression='snappy',  # Compresión rápida y eficiente
            engine='pyarrow'
        )
        
        if archivo_existe:
            logger.info(f"Archivo parquet actualizado exitosamente en: {archivo_parquet}")
        else:
            logger.info(f"Archivo parquet creado exitosamente en: {archivo_parquet}")
            
        logger.info(f"Tamaño del archivo: {archivo_parquet.stat().st_size / (1024*1024):.2f} MB")
        
        # Mostrar un resumen de los datos
        logger.info("\n=== RESUMEN DE DATOS ===")
        logger.info(f"Total de filas: {len(df_combinado)}")
        logger.info(f"Total de columnas: {len(df_combinado.columns)}")
        
        if len(df_combinado) > 0:
            logger.info(f"Hojas procesadas: {df_combinado['hoja_origen'].nunique()}")
            logger.info(f"Hojas de origen: {df_combinado['hoja_origen'].unique()}")
            
            # Mostrar distribución por hoja
            logger.info("\n=== DISTRIBUCIÓN POR HOJA ===")
            distribucion = df_combinado['hoja_origen'].value_counts()
            for hoja, cantidad in distribucion.items():
                logger.info(f"{hoja}: {cantidad} registros")
        else:
            logger.info("Archivo vacío creado - no hay datos para procesar")
        
        # Mostrar las primeras filas
        logger.info("\n=== PRIMERAS 5 FILAS ===")
        print(df_combinado.head())
        
    except Exception as e:
        logger.error(f"Error al guardar el archivo parquet: {str(e)}")

if __name__ == "__main__":
    agrupar_datos_vol_portafolio()
