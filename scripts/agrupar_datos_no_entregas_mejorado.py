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
        if tipo == "no_entregas_output":
            return Path(config["rutas_archivos"]["no_entregas"]) / "Output"
        return Path("Data/No Entregas/Output")
    
    def verificar_configuracion():
        return True

# Configurar logging con nivel más alto para reducir operaciones innecesarias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Solo configurar nivel INFO para el logger principal
logger.setLevel(logging.INFO)

def procesar_archivo_devoluciones(archivo):
    """
    Procesa un archivo de devoluciones y retorna el DataFrame resultante.
    """
    try:
        logger.info(f"Procesando archivo de devoluciones: {archivo.name}")
        
        # Leer el archivo Excel con parámetros optimizados
        excel_file = pd.ExcelFile(archivo, engine='openpyxl')
        
        # Verificar si existe la hoja Z_DEVO_ALV
        if "Z_DEVO_ALV" in excel_file.sheet_names:
            # Leer la hoja Z_DEVO_ALV con parámetros optimizados
            df = pd.read_excel(
                archivo, 
                sheet_name="Z_DEVO_ALV",
                engine='openpyxl',
                dtype_backend='numpy_nullable',  # Usar backend optimizado
            )
            
            # Agregar una columna para identificar el archivo de origen
            df['archivo_origen'] = archivo.name
            
            logger.info(f"Se agregaron {len(df)} filas del archivo {archivo.name}")
            return df
            
        else:
            logger.warning(f"La hoja Z_DEVO_ALV no existe en el archivo {archivo.name}")
            logger.info(f"Hojas disponibles: {excel_file.sheet_names}")
            return None
            
    except Exception as e:
        logger.error(f"Error al procesar el archivo {archivo.name}: {str(e)}")
        return None

def agrupar_datos_no_entregas():
    """
    Agrupa los datos de devoluciones de todos los archivos Excel en la carpeta No Entregas
    y los guarda como un archivo parquet usando la configuración del sistema.
    """
    
    # Verificar configuración al inicio
    logger.info("⚙️ Verificando configuración del sistema...")
    if not verificar_configuracion():
        logger.error("❌ Error en la configuración del sistema")
        return
    
    # Cargar configuración
    config = cargar_configuracion()
    
    # Definir la ruta de la carpeta No Entregas desde la configuración
    carpeta_no_entregas = Path(config["rutas_archivos"]["no_entregas"])
    
    logger.info(f"📁 Usando carpeta No Entregas: {carpeta_no_entregas}")
    
    # Verificar que la carpeta existe
    if not carpeta_no_entregas.exists():
        logger.error(f"La carpeta {carpeta_no_entregas} no existe")
        return
    
    # Lista para almacenar todos los DataFrames
    dataframes = []
    
    # Obtener todos los archivos Excel en la carpeta
    archivos_excel = list(carpeta_no_entregas.glob("*-2025-Devoluciones.xlsx"))
    
    if not archivos_excel:
        logger.warning("No se encontraron archivos de devoluciones en la carpeta. Creando archivo parquet vacío...")
        
        # Obtener carpeta de salida desde la configuración
        carpeta_salida = obtener_carpeta_salida("no_entregas_output")
        
        # Crear DataFrame vacío con estructura básica
        df_combinado = pd.DataFrame({
            'Entrega': [],
            'Familia': [],
            'Cajas Equiv NE': [],
            'archivo_origen': []
        })
        
        logger.info("✅ DataFrame vacío creado con estructura básica")
    else:
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
            logger.warning("No se pudieron leer datos de ningún archivo. Creando archivo parquet vacío...")
            
            # Crear DataFrame vacío con estructura básica
            df_combinado = pd.DataFrame({
                'Entrega': [],
                'Familia': [],
                'Cajas Equiv NE': [],
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
    
    # Obtener carpeta de salida desde la configuración
    carpeta_salida = obtener_carpeta_salida("no_entregas_output")
    
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
        
        if len(df_combinado) > 0:
            logger.info(f"Archivos procesados: {df_combinado['archivo_origen'].nunique()}")
            logger.info(f"Archivos de origen: {df_combinado['archivo_origen'].unique()}")
            
            # Mostrar estadísticas de Familia
            if 'Familia' in df_combinado.columns:
                logger.info("\n=== DISTRIBUCIÓN POR FAMILIA ===")
                distribucion = df_combinado['Familia'].value_counts()
                for familia, cantidad in distribucion.items():
                    logger.info(f"{familia}: {cantidad} registros")
        else:
            logger.info("Archivo vacío creado - no hay datos para procesar")
        
        # Mostrar las primeras filas
        logger.info("\n=== PRIMERAS 5 FILAS ===")
        print(df_combinado.head())
        
    except Exception as e:
        logger.error(f"Error al guardar el archivo parquet: {str(e)}")

if __name__ == "__main__":
    agrupar_datos_no_entregas()
