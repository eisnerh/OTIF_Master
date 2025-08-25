import pandas as pd
import os
from pathlib import Path
import logging
import numpy as np
import concurrent.futures
import gc

# Configurar logging con nivel más alto para reducir operaciones innecesarias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Solo configurar nivel INFO para el logger principal
logger.setLevel(logging.INFO)

def procesar_archivo_devoluciones(archivo):
    """
    Procesa un archivo de devoluciones aplicando las transformaciones de Power Query.
    """
    try:
        logger.info(f"Procesando archivo: {archivo.name}")
        
        # Leer la hoja Z_DEVO_ALV con parámetros optimizados
        df = pd.read_excel(
            archivo, 
            sheet_name="Z_DEVO_ALV",
            engine='openpyxl',
            dtype_backend='numpy_nullable'  # Usar backend optimizado
        )
        
        # Filtrar por Categoría (VENT, PROP, BONI)
        categorias_validas = ["VENT", "PROP", "BONI"]
        df = df[df['Categoría'].isin(categorias_validas)]
        
        # Cambiar tipos de datos de manera más segura
        # Convertir columnas numéricas con manejo de errores
        columnas_numericas = {
            'Entrega': 'Int64',
            'Pedido HH': 'Int64', 
            'Guía': 'Int64',
            'Ruta de Ventas': 'Int64',
            'Ruta de Distrib': 'Int64',
            'Cod Empleado 1': 'Int64',
            'Cod Empleado 2': 'Int64', 
            'Cod Empleado 3': 'Int64',
            'Cod. Cliente': 'Int64',
            'Material': 'Int64',
            'Cod Rechazo': 'Int64',
            'Cantidad': 'Int64'
        }
        
        for col, tipo in columnas_numericas.items():
            if col in df.columns:
                try:
                    # Primero convertir a float para manejar valores decimales
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Luego redondear y convertir a entero
                    df[col] = df[col].round().astype('Int64')
                except Exception as e:
                    logger.warning(f"No se pudo convertir la columna {col}: {str(e)}")
                    # Mantener como string si no se puede convertir
                    df[col] = df[col].astype(str)
        
        # Convertir fecha
        if 'Fecha' in df.columns:
            try:
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            except Exception as e:
                logger.warning(f"No se pudo convertir la columna Fecha: {str(e)}")
        
        # Convertir columnas de texto
        columnas_texto = [
            'Centro', 'Categoría', 'Zona de Ventas', 'Zona Distribucion',
            'Nombre Empleado 1', 'Nombre Empleado 2', 'Nombre Empleado 3',
            'Nombre Cliente', 'Descrip Material', 'Descrip Cod Rechazo',
            'Procesos', 'Estado Entregas', 'Segmento', 'Sub Área'
        ]
        
        for col in columnas_texto:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Reemplazar valores en Segmento (equivalente a Table.ReplaceValue)
        reemplazos_segmento = {
            "CERVEZA & BAS": "C&B",
            "DESTILADOS": "VYD", 
            "VINOS": "VYD",
            "CARBONATADAS": "BNA",
            "AGUAS & REFRESCOS": "BNA",
            "ALIMENTOS": "ALI"
        }
        
        if 'Segmento' in df.columns:
            df['Segmento'] = df['Segmento'].replace(reemplazos_segmento)
            
            # Reemplazar N/A por OTROS
            df['Segmento'] = df['Segmento'].replace('N/A', 'OTROS')
            df['Segmento'] = df['Segmento'].replace('nan', 'OTROS')
            df['Segmento'] = df['Segmento'].fillna('OTROS')
        
        # Renombrar columna Segmento a Familia
        if 'Segmento' in df.columns:
            df = df.rename(columns={'Segmento': 'Familia'})
        
        # Agrupar datos (equivalente a Table.Group)
        columnas_agrupacion = ['Centro', 'Entrega', 'Descrip Cod Rechazo', 'Fecha', 'Procesos', 'Estado Entregas', 'Familia']
        
        # Verificar que todas las columnas de agrupación existen
        columnas_existentes = [col for col in columnas_agrupacion if col in df.columns]
        
        if 'Cajas Eq.' in df.columns and columnas_existentes:
            df_agrupado = df.groupby(columnas_existentes)['Cajas Eq.'].sum().reset_index()
            df_agrupado = df_agrupado.rename(columns={'Cajas Eq.': 'Cajas Equiv NE'})
        else:
            logger.warning(f"No se pudo agrupar por falta de columnas. Columnas disponibles: {list(df.columns)}")
            df_agrupado = df
        
        # Reemplazar valores vacíos en Estado Entregas
        if 'Estado Entregas' in df_agrupado.columns:
            df_agrupado['Estado Entregas'] = df_agrupado['Estado Entregas'].replace('', 'Canc Parcial')
            df_agrupado['Estado Entregas'] = df_agrupado['Estado Entregas'].fillna('Canc Parcial')
        
        # Agregar columna de archivo origen
        df_agrupado['archivo_origen'] = archivo.name
        
        logger.info(f"Se procesaron {len(df_agrupado)} filas del archivo {archivo.name}")
        return df_agrupado
        
    except Exception as e:
        logger.error(f"Error al procesar el archivo {archivo.name}: {str(e)}")
        return None

def agrupar_datos_no_entregas():
    """
    Agrupa los datos de devoluciones de todos los archivos Excel en la carpeta No Entregas
    y los guarda como un archivo parquet.
    """
    
    # Definir la ruta de la carpeta No Entregas
    carpeta_no_entregas = Path("Data/No Entregas/2025")
    
    # Verificar que la carpeta existe
    if not carpeta_no_entregas.exists():
        logger.error(f"La carpeta {carpeta_no_entregas} no existe")
        return
    
    # Lista para almacenar todos los DataFrames
    dataframes = []
    
    # Obtener todos los archivos Excel en la carpeta
    archivos_excel = list(carpeta_no_entregas.glob("*-2025-Devoluciones.xlsx"))
    
    if not archivos_excel:
        logger.warning("No se encontraron archivos de devoluciones en la carpeta")
        return
    
    logger.info(f"Se encontraron {len(archivos_excel)} archivos de devoluciones")
    
    # Función para verificar y procesar un archivo
    def verificar_y_procesar(archivo):
        try:
            # Verificar si existe la hoja Z_DEVO_ALV
            excel_file = pd.ExcelFile(archivo, engine='openpyxl')
            
            if "Z_DEVO_ALV" in excel_file.sheet_names:
                return procesar_archivo_devoluciones(archivo)
            else:
                logger.warning(f"La hoja Z_DEVO_ALV no existe en el archivo {archivo.name}")
                logger.info(f"Hojas disponibles: {excel_file.sheet_names}")
                return None
                
        except Exception as e:
            logger.error(f"Error al procesar el archivo {archivo.name}: {str(e)}")
            return None
    
    # Usar procesamiento paralelo para procesar los archivos
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(verificar_y_procesar, archivos_excel))
    
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
    
    # Mostrar información sobre las columnas
    logger.info("Columnas del DataFrame combinado:")
    for i, col in enumerate(df_combinado.columns, 1):
        logger.info(f"{i}. {col}")
    
    # Crear la carpeta de salida si no existe
    carpeta_salida = Path("Data/No Entregas/Output")
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    # Guardar como archivo parquet con compresión optimizada
    archivo_parquet = carpeta_salida / "No_Entregas_combinado_mejorado.parquet"
    
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
        logger.info(f"Archivos procesados: {df_combinado['archivo_origen'].nunique()}")
        logger.info(f"Archivos de origen: {df_combinado['archivo_origen'].unique()}")
        
        # Mostrar estadísticas de Familia
        if 'Familia' in df_combinado.columns:
            logger.info("\n=== DISTRIBUCIÓN POR FAMILIA ===")
            distribucion = df_combinado['Familia'].value_counts()
            for familia, cantidad in distribucion.items():
                logger.info(f"{familia}: {cantidad} registros")
        
        # Mostrar las primeras filas
        logger.info("\n=== PRIMERAS 5 FILAS ===")
        print(df_combinado.head())
        
    except Exception as e:
        logger.error(f"Error al guardar el archivo parquet: {str(e)}")

if __name__ == "__main__":
    agrupar_datos_no_entregas()
