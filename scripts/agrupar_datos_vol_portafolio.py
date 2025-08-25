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

def agrupar_datos_vol_portafolio():
    """
    Agrupa los datos de las 4 hojas del archivo Excel en la carpeta Vol_Portafolio
    y los guarda como un archivo parquet.
    """
    
    # Definir la ruta del archivo
    archivo_excel = Path("Data/Vol_Portafolio/VOL POR PORTAFOLIO ENE-2025.xlsx")
    
    # Verificar que el archivo existe
    if not archivo_excel.exists():
        logger.error(f"El archivo {archivo_excel} no existe")
        return
    
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
            logger.error("No se pudieron leer datos de ninguna hoja")
            return
        
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
        
        # Crear la carpeta de salida si no existe
        carpeta_salida = Path("Data/Vol_Portafolio/Output")
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        
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
            logger.info(f"Hojas procesadas: {df_combinado['hoja_origen'].nunique()}")
            logger.info(f"Hojas de origen: {df_combinado['hoja_origen'].unique()}")
            
            # Mostrar distribución por hoja
            logger.info("\n=== DISTRIBUCIÓN POR HOJA ===")
            distribucion_hoja = df_combinado['hoja_origen'].value_counts()
            for hoja, cantidad in distribucion_hoja.items():
                porcentaje = (cantidad / len(df_combinado)) * 100
                logger.info(f"{hoja}: {cantidad:,} registros ({porcentaje:.1f}%)")
            
            # Mostrar las primeras filas
            logger.info("\n=== PRIMERAS 5 FILAS ===")
            print(df_combinado.head())
            
            # Mostrar información de tipos de datos
            logger.info("\n=== TIPOS DE DATOS ===")
            tipos_datos = df_combinado.dtypes
            for columna, tipo in tipos_datos.items():
                logger.info(f"{columna}: {tipo}")
            
            # Guardar también un archivo con información de resumen
            resumen_hojas = df_combinado.groupby('hoja_origen').agg({
                'hoja_origen': 'count'
            }).rename(columns={'hoja_origen': 'total_registros'})
            
            archivo_resumen = carpeta_salida / "resumen_vol_portafolio.parquet"
            
            # Verificar si el archivo de resumen ya existe
            resumen_existe = archivo_resumen.exists()
            
            resumen_hojas.to_parquet(archivo_resumen)
            
            if resumen_existe:
                logger.info(f"Resumen actualizado en: {archivo_resumen}")
            else:
                logger.info(f"Resumen creado en: {archivo_resumen}")
            
        except Exception as e:
            logger.error(f"Error al guardar el archivo parquet: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    agrupar_datos_vol_portafolio()
