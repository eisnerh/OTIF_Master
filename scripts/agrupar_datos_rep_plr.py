import pandas as pd
import os
from pathlib import Path
import logging
import concurrent.futures
import gc

# Configurar logging con nivel más alto para reducir operaciones innecesarias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Solo configurar nivel INFO para el logger principal
logger.setLevel(logging.INFO)

def agrupar_datos_rep_plr():
    """
    Agrupa los datos de la hoja REP_PLR de todos los archivos Excel en la carpeta Rep PLR
    y los guarda como un archivo parquet.
    """
    
    # Definir la ruta de la carpeta Rep PLR
    carpeta_rep_plr = Path("Data/Rep PLR")
    
    # Verificar que la carpeta existe
    if not carpeta_rep_plr.exists():
        logger.error(f"La carpeta {carpeta_rep_plr} no existe")
        return
    
    # Lista para almacenar todos los DataFrames
    dataframes = []
    
    # Obtener todos los archivos Excel en la carpeta
    archivos_excel = list(carpeta_rep_plr.glob("*.xlsx"))
    
    if not archivos_excel:
        logger.warning("No se encontraron archivos Excel en la carpeta Rep PLR")
        return
    
    logger.info(f"Se encontraron {len(archivos_excel)} archivos Excel")
    
    def procesar_archivo(archivo):
        """Procesa un archivo Excel y retorna el DataFrame resultante."""
        try:
            logger.info(f"Procesando archivo: {archivo.name}")
            
            # Leer el archivo Excel con parámetros optimizados
            excel_file = pd.ExcelFile(archivo, engine='openpyxl')
            
            # Verificar si existe la hoja REP PLR
            if "REP PLR" in excel_file.sheet_names:
                # Leer la hoja REP PLR con parámetros optimizados
                df = pd.read_excel(
                    archivo, 
                    sheet_name="REP PLR",
                    engine='openpyxl',
                    dtype_backend='numpy_nullable',  # Usar backend optimizado
                )
                
                # Agregar una columna para identificar el archivo de origen
                df['archivo_origen'] = archivo.name
                
                logger.info(f"Se agregaron {len(df)} filas del archivo {archivo.name}")
                return df
                
            else:
                logger.warning(f"La hoja REP PLR no existe en el archivo {archivo.name}")
                logger.info(f"Hojas disponibles: {excel_file.sheet_names}")
                return None
                
        except Exception as e:
            logger.error(f"Error al procesar el archivo {archivo.name}: {str(e)}")
            return None
    
    # Usar procesamiento paralelo para leer los archivos Excel
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(procesar_archivo, archivos_excel))
    
    # Filtrar los resultados None
    dataframes = [df for df in resultados if df is not None]
    
    if not dataframes:
        logger.error("No se pudieron leer datos de ningún archivo")
        return
    
    # Combinar todos los DataFrames de manera eficiente
    logger.info("Combinando todos los DataFrames...")
    df_combinado = pd.concat(dataframes, ignore_index=True)
    
    # Liberar memoria
    del dataframes
    gc.collect()
    
    logger.info(f"DataFrame combinado: {len(df_combinado)} filas y {len(df_combinado.columns)} columnas")
    
    # Mostrar información sobre las columnas originales
    logger.info("Columnas originales del DataFrame combinado:")
    for i, col in enumerate(df_combinado.columns, 1):
        logger.info(f"{i}. {col}")
    
    # Definir las columnas que queremos mantener
    columnas_deseadas = [
        'Centro',
        'Entrega', 
        'Cliente',
        'Nombre del Cliente',
        'Verificado',
        'Guia Entrega',
        'Fuerza Ventas',
        'Desc Zona Vtas',
        'Desc Zona Superv',
        'Fe.Entrega',
        'Cajas Equiv.',
        'Macro Canal',
        'Clasificación Clt',
        'Tipo Negocio',
        'Provincia',
        'Cantón',
        'Distrito',
        'Latitud',
        'Longitud',
        'archivo_origen'  # Mantener la columna de origen
    ]
    
    # Filtrar solo las columnas que existen en el DataFrame
    columnas_disponibles = [col for col in columnas_deseadas if col in df_combinado.columns]
    columnas_faltantes = [col for col in columnas_deseadas if col not in df_combinado.columns]
    
    logger.info(f"Columnas disponibles: {len(columnas_disponibles)}")
    logger.info(f"Columnas encontradas: {columnas_disponibles}")
    
    if columnas_faltantes:
        logger.warning(f"Columnas no encontradas: {columnas_faltantes}")
    
    # Seleccionar solo las columnas deseadas
    df_combinado = df_combinado[columnas_disponibles]
    
    logger.info(f"DataFrame filtrado: {len(df_combinado)} filas y {len(df_combinado.columns)} columnas")
    
    # Mostrar las columnas finales
    logger.info("Columnas finales del DataFrame:")
    for i, col in enumerate(df_combinado.columns, 1):
        logger.info(f"{i}. {col}")
    
    # Crear la carpeta de salida si no existe
    carpeta_salida = Path("Data/Rep PLR/Output")
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    # Guardar como archivo parquet con compresión optimizada
    archivo_parquet = carpeta_salida / "REP_PLR_combinado.parquet"
    
    try:
        df_combinado.to_parquet(
            archivo_parquet, 
            index=False,
            compression='snappy',  # Compresión rápida y eficiente
            engine='pyarrow'
        )
        logger.info(f"Archivo parquet guardado exitosamente en: {archivo_parquet}")
        logger.info(f"Tamaño del archivo: {archivo_parquet.stat().st_size / (1024*1024):.2f} MB")
        
        # Mostrar un resumen de los datos
        logger.info("\n=== RESUMEN DE DATOS ===")
        logger.info(f"Total de filas: {len(df_combinado)}")
        logger.info(f"Total de columnas: {len(df_combinado.columns)}")
        logger.info(f"Archivos procesados: {df_combinado['archivo_origen'].nunique()}")
        logger.info(f"Archivos de origen: {df_combinado['archivo_origen'].unique()}")
        
        # Mostrar las primeras filas
        logger.info("\n=== PRIMERAS 5 FILAS ===")
        print(df_combinado.head())
        
    except Exception as e:
        logger.error(f"Error al guardar el archivo parquet: {str(e)}")

if __name__ == "__main__":
    agrupar_datos_rep_plr()
