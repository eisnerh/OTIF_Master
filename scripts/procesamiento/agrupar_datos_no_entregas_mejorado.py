# agrupar_datos_no_entregas_mejorado.py
import pandas as pd
import os
from pathlib import Path
import logging
import concurrent.futures
import gc
import time
from datetime import datetime

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

# Configurar logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Columnas esperadas y tipos optimizados
COLUMNAS_NO_ENTREGAS = ['Entrega', 'Segmento', 'Cajas Eq.', 'Categoría']
TIPO_DATOS_NO_ENTREGAS = {
    'Entrega': 'string',
    'Segmento': 'category',
    'Cajas Eq.': 'float32',
    'Categoría': 'category'
}

# Mapeo de segmentos para estandarización
MAPEO_SEGMENTOS = {
    'CERVEZA & BAS': 'C&B',
    'DESTILADOS': 'VYD',
    'CARBONATADAS': 'VYD', 
    'AGUAS & REFRESCOS': 'BNA',
    'VINOS': 'BNA',
    'ALIMENTOS': 'ALI',
    'ENVASE': 'ENV',
    'OTROS': 'OTROS'
}

# Categorías a filtrar
CATEGORIAS_FILTRO = ['BONI', 'PROP', 'VENT']

# ============================================================================
# CLASES AUXILIARES
# ============================================================================

class ProgresoLectura:
    """Clase para monitorear el progreso de lectura de archivos"""
    
    def __init__(self, total_archivos):
        self.total_archivos = total_archivos
        self.archivos_procesados = 0
        self.inicio_tiempo = time.time()
        
    def actualizar(self, nombre_archivo, exito=True, filas_procesadas=0):
        """Actualizar y mostrar progreso"""
        self.archivos_procesados += 1
        estado = "✅" if exito else "❌"
        tiempo_transcurrido = time.time() - self.inicio_tiempo
        porcentaje = (self.archivos_procesados / self.total_archivos) * 100
        
        mensaje = f"{estado} [{self.archivos_procesados}/{self.total_archivos}] ({porcentaje:.1f}%)"
        mensaje += f" - {nombre_archivo}"
        if filas_procesadas > 0:
            mensaje += f" - {filas_procesadas:,} filas"
        mensaje += f" - {tiempo_transcurrido:.1f}s"
        
        logger.info(mensaje)

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def optimizar_dataframe(df):
    """Optimizar el DataFrame para reducir uso de memoria"""
    if df.empty:
        return df
    
    # Aplicar tipos de datos optimizados
    for col in df.columns:
        if col in TIPO_DATOS_NO_ENTREGAS:
            try:
                df[col] = df[col].astype(TIPO_DATOS_NO_ENTREGAS[col])
            except Exception as e:
                logger.warning(f"No se pudo convertir columna {col}: {e}")
                # Conversión genérica para objetos
                if df[col].dtype == 'object':
                    unique_ratio = df[col].nunique() / len(df)
                    if unique_ratio < 0.5:
                        df[col] = df[col].astype('category')
    
    return df

def verificar_hoja_devoluciones(archivo):
    """Verificar si el archivo tiene la hoja Z_DEVO_ALV"""
    try:
        with pd.ExcelFile(archivo, engine='openpyxl') as excel_file:
            return "Z_DEVO_ALV" in excel_file.sheet_names
    except Exception as e:
        logger.warning(f"Error verificando hoja en {archivo.name}: {e}")
        return False

def crear_dataframe_vacio_no_entregas():
    """Crear un DataFrame vacío con la estructura correcta para no entregas"""
    return pd.DataFrame({
        'Entrega': pd.Series(dtype='string'),
        'Segmento': pd.Series(dtype='category'),
        'Cajas Eq.': pd.Series(dtype='float32'),
        'archivo_origen': pd.Series(dtype='string')
    })

def guardar_archivo_intermedio(df):
    """Guardar archivo intermedio para verificación"""
    try:
        carpeta_salida = obtener_carpeta_salida("no_entregas_output")
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        
        archivo_intermedio = carpeta_salida / "no_entregas_procesado.parquet"
        
        df.to_parquet(
            archivo_intermedio,
            index=False,
            compression='snappy',
            engine='pyarrow'
        )
        
        logger.info(f"💾 Archivo intermedio guardado: {archivo_intermedio}")
        
    except Exception as e:
        logger.warning(f"No se pudo guardar archivo intermedio: {e}")

# ============================================================================
# FUNCIONES DE PROCESAMIENTO
# ============================================================================

def procesar_archivo_no_entregas(archivo, progreso=None):
    """
    Procesa un archivo de devoluciones de manera optimizada
    Retorna DataFrame con columns: ['Entrega', 'Segmento', 'Cajas Eq.', 'archivo_origen']
    """
    try:
        logger.info(f"📖 Procesando: {archivo.name}")
        
        # Verificar si el archivo es válido
        if archivo.stat().st_size == 0:
            logger.warning(f"Archivo vacío: {archivo.name}")
            if progreso:
                progreso.actualizar(archivo.name, exito=False)
            return None
        
        # Verificar si existe la hoja Z_DEVO_ALV
        if not verificar_hoja_devoluciones(archivo):
            logger.warning(f"Hoja Z_DEVO_ALV no encontrada en {archivo.name}")
            if progreso:
                progreso.actualizar(archivo.name, exito=False)
            return None
        
        # Leer solo las columnas necesarias para optimizar memoria
        try:
            # Primero leer solo los nombres de columnas para verificar
            columnas_disponibles = pd.read_excel(
                archivo, 
                sheet_name="Z_DEVO_ALV", 
                nrows=0
            ).columns.tolist()
            
            # Filtrar solo columnas esperadas que existan
            columnas_a_leer = [col for col in COLUMNAS_NO_ENTREGAS if col in columnas_disponibles]
            columnas_faltantes = [col for col in COLUMNAS_NO_ENTREGAS if col not in columnas_disponibles]
            
            if columnas_faltantes:
                logger.warning(f"Columnas faltantes en {archivo.name}: {columnas_faltantes}")
            
            # Leer la hoja con parámetros optimizados
            df = pd.read_excel(
                archivo, 
                sheet_name="Z_DEVO_ALV",
                engine='openpyxl',
                usecols=columnas_a_leer if columnas_a_leer else None,
                dtype={col: TIPO_DATOS_NO_ENTREGAS.get(col, 'object') for col in columnas_a_leer},
                na_values=['', 'NULL', 'N/A', 'NaN'],
                keep_default_na=False
            )
            
        except Exception as e:
            logger.warning(f"Error leyendo estructura de {archivo.name}, intentando lectura completa: {e}")
            # Fallback: leer todas las columnas
            df = pd.read_excel(
                archivo, 
                sheet_name="Z_DEVO_ALV",
                engine='openpyxl'
            )
        
        # Verificar que tenemos las columnas mínimas necesarias
        if 'Entrega' not in df.columns:
            logger.error(f"Columnas esenciales no encontradas en {archivo.name}")
            if progreso:
                progreso.actualizar(archivo.name, exito=False)
            return None
        
        # Renombrar columnas si es necesario
        mapeo_columnas = {
            'Cajas Eq.': ['Cajas Eq.', 'Cajas_Equiv_NE', 'CajasEquivNE', 'Cajas'],
            'Segmento': ['Segmento', 'Family', 'Producto'],
            'Entrega': ['Entrega', 'Delivery', 'Pedido'],
            'Categoría': ['Categoría', 'Categoria', 'Category', 'Tipo']
        }
        
        for columna_estandar, posibles_nombres in mapeo_columnas.items():
            if columna_estandar not in df.columns:
                for nombre_posible in posibles_nombres:
                    if nombre_posible in df.columns:
                        df.rename(columns={nombre_posible: columna_estandar}, inplace=True)
                        logger.info(f"Renombrada columna {nombre_posible} -> {columna_estandar}")
                        break
        
        # Si no existe Cajas Eq., crear columna con 0
        if 'Cajas Eq.' not in df.columns:
            df['Cajas Eq.'] = 0
            logger.info("Columna Cajas Eq. creada con valor 0")
        
        # FILTRAR POR CATEGORÍA (BONI;PROP;VENT)
        if 'Categoría' in df.columns:
            filas_antes_filtro = len(df)
            # Convertir a string y limpiar
            df['Categoría'] = df['Categoría'].astype(str).str.strip().str.upper()
            # Filtrar solo las categorías deseadas
            df = df[df['Categoría'].isin(CATEGORIAS_FILTRO)]
            filas_despues_filtro = len(df)
            
            logger.info(f"📊 Filtro categoría: {filas_antes_filtro} → {filas_despues_filtro} filas")
        else:
            logger.warning(f"⚠️ Columna 'Categoría' no encontrada en {archivo.name}, no se aplicó filtro")
        
        # Seleccionar solo las columnas que necesitamos
        columnas_finales = [col for col in ['Entrega', 'Segmento', 'Cajas Eq.'] if col in df.columns]
        df = df[columnas_finales]
        
        # Agregar columna para identificar el archivo de origen
        df['archivo_origen'] = archivo.name
        
        # Optimizar memoria
        df = optimizar_dataframe(df)
        
        logger.info(f"✅ {archivo.name}: {len(df):,} filas procesadas después de filtro")
        
        if progreso:
            progreso.actualizar(archivo.name, exito=True, filas_procesadas=len(df))
            
        return df
        
    except Exception as e:
        logger.error(f"❌ Error procesando {archivo.name}: {str(e)}")
        if progreso:
            progreso.actualizar(archivo.name, exito=False)
        return None

def limpiar_datos_no_entregas(df):
    """Limpieza, validación y agrupación de datos de no entregas"""
    if df.empty:
        return df
    
    # Filtrar filas con Entrega vacía
    filas_antes = len(df)
    df = df[df['Entrega'].notna() & (df['Entrega'] != '')]
    filas_despues = len(df)
    
    if filas_antes != filas_despues:
        logger.info(f"🗑️  Filas filtradas (Entrega vacía): {filas_antes - filas_despues}")
    
    # Asegurar que Cajas Eq. sea numérico
    try:
        df['Cajas Eq.'] = pd.to_numeric(df['Cajas Eq.'], errors='coerce').fillna(0).astype('float32')
    except Exception as e:
        logger.warning(f"Error convirtiendo Cajas Eq.: {e}")
        df['Cajas Eq.'] = 0
    
    # Aplicar mapeo de segmentos
    if 'Segmento' in df.columns:
        filas_antes_segmento = len(df)
        df['Segmento'] = df['Segmento'].astype(str).str.strip().str.upper()
        
        # Aplicar el mapeo
        df['Segmento'] = df['Segmento'].apply(
            lambda x: MAPEO_SEGMENTOS.get(x, x) if pd.notna(x) else x
        )
        
        # Contar cambios realizados
        cambios = sum(1 for original, mapeado in zip(df['Segmento'], df['Segmento']) 
                     if original != mapeado and original in MAPEO_SEGMENTOS)
        logger.info(f"🔄 Segmentos renombrados: {cambios:,}")
    
    # AGRUPAR POR ENTREGA Y SEGMENTO, SUMANDO CAJAS EQ.
    filas_antes_agrupacion = len(df)
    
    # Agrupar y sumar
    df_agrupado = df.groupby(['Entrega', 'Segmento'], as_index=False)['Cajas Eq.'].sum()
    
    # Mantener información del archivo de origen (opcional, puedes eliminar si no la necesitas)
    # Para mantener el origen, podrías agregar una columna con el conteo de archivos
    if 'archivo_origen' in df.columns:
        conteo_archivos = df.groupby(['Entrega', 'Segmento'])['archivo_origen'].nunique().reset_index()
        conteo_archivos.rename(columns={'archivo_origen': 'archivos_origen_count'}, inplace=True)
        df_agrupado = df_agrupado.merge(conteo_archivos, on=['Entrega', 'Segmento'], how='left')
    
    filas_despues_agrupacion = len(df_agrupado)
    
    logger.info(f"📦 Agrupación: {filas_antes_agrupacion} → {filas_despues_agrupacion} registros")
    logger.info(f"📦 Total Cajas Eq. después de agrupar: {df_agrupado['Cajas Eq.'].sum():.2f}")
    
    return df_agrupado

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def procesar_no_entregas():
    """
    Procesa todos los archivos de no entregas y retorna DataFrame optimizado
    para join con llaves: ['Entrega', 'Segmento']
    """
    logger.info("🚀 Iniciando procesamiento de No Entregas...")
    inicio_proceso = time.time()
    
    # Verificar configuración
    if not verificar_configuracion():
        logger.error("❌ Error en la configuración del sistema")
        return crear_dataframe_vacio_no_entregas()
    
    config = cargar_configuracion()
    carpeta_no_entregas = Path(config["rutas_archivos"]["no_entregas"])
    
    logger.info(f"📁 Carpeta No Entregas: {carpeta_no_entregas}")
    
    if not carpeta_no_entregas.exists():
        logger.error(f"❌ La carpeta {carpeta_no_entregas} no existe")
        return crear_dataframe_vacio_no_entregas()
    
    # Buscar archivos Excel con diferentes patrones
    patrones_archivos = [
        "*-2025-Devoluciones.xlsx",
        "*Devoluciones*.xlsx", 
        "*devoluciones*.xlsx",
        "*.xlsx"
    ]
    
    archivos_excel = []
    for patron in patrones_archivos:
        archivos = list(carpeta_no_entregas.glob(patron))
        archivos_excel.extend(archivos)
        if archivos:
            logger.info(f"Encontrados {len(archivos)} archivos con patrón: {patron}")
    
    # Eliminar duplicados
    archivos_excel = list(set(archivos_excel))
    
    if not archivos_excel:
        logger.warning("⚠️ No se encontraron archivos de devoluciones")
        return crear_dataframe_vacio_no_entregas()
    
    logger.info(f"📊 Total de archivos a procesar: {len(archivos_excel)}")
    
    # Configurar progreso
    progreso = ProgresoLectura(len(archivos_excel))
    
    # Procesar archivos en paralelo con límite razonable
    dataframes = []
    max_workers = min(4, os.cpu_count() or 2)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear futures para cada archivo
        futures = {
            executor.submit(procesar_archivo_no_entregas, archivo, progreso): archivo 
            for archivo in archivos_excel
        }
        
        # Recolectar resultados
        for future in concurrent.futures.as_completed(futures):
            try:
                resultado = future.result()
                if resultado is not None:
                    dataframes.append(resultado)
            except Exception as e:
                archivo = futures[future]
                logger.error(f"❌ Error en future para {archivo.name}: {e}")
    
    # Combinar resultados
    if dataframes:
        logger.info("🔄 Combinando DataFrames...")
        df_combinado = pd.concat(dataframes, ignore_index=True)
        
        # Liberar memoria
        del dataframes
        gc.collect()
        
        # Limpieza adicional
        df_combinado = limpiar_datos_no_entregas(df_combinado)
        
        logger.info(f"📈 DataFrame combinado: {len(df_combinado):,} filas")
        
        # Guardar archivo intermedio para debug
        guardar_archivo_intermedio(df_combinado)
        
    else:
        logger.warning("⚠️ No se pudieron procesar datos válidos de ningún archivo")
        df_combinado = crear_dataframe_vacio_no_entregas()
    
    # Calcular estadísticas finales
    tiempo_total = time.time() - inicio_proceso
    logger.info(f"⏰ Tiempo total de procesamiento: {tiempo_total:.2f} segundos")
    
    return df_combinado

# ============================================================================
# FUNCIONES DE ANÁLISIS
# ============================================================================

def analizar_datos_no_entregas(df):
    """Análisis de los datos procesados"""
    if df.empty:
        logger.info("📊 Dataset vacío - no hay datos para analizar")
        return
    
    logger.info("\n📊 ANÁLISIS DE DATOS NO ENTREGAS:")
    logger.info("="*50)
    logger.info(f"Total de registros: {len(df):,}")
    logger.info(f"Entregas únicas: {df['Entrega'].nunique():,}")
    logger.info(f"Segmentos únicas: {df['Segmento'].nunique():,}")
    logger.info(f"Archivos procesados: {df['archivo_origen'].nunique():,}")
    
    # Estadísticas de Cajas Eq.
    total_cajas = df['Cajas Eq.'].sum()
    entregas_con_no_entrega = (df['Cajas Eq.'] > 0).sum()
    
    logger.info(f"Total Cajas No Entregadas: {total_cajas:,.2f}")
    logger.info(f"Entregas con No Entrega: {entregas_con_no_entrega:,}")
    logger.info(f"Porcentaje con No Entrega: {(entregas_con_no_entrega/len(df)*100):.1f}%")
    
    # Top Segmentos con más no entregas
    if not df.empty:
        logger.info("\n🏆 Top 5 Segmentos con más No Entregas:")
        top_Segmentos = df.groupby('Segmento')['Cajas Eq.'].sum().nlargest(5)
        for Segmento, cajas in top_Segmentos.items():
            logger.info(f"   {Segmento}: {cajas:,.2f} cajas")
            
def verificar_mapeo_segmentos(df):
    """Verificar que el mapeo de segmentos se aplicó correctamente"""
    if df.empty or 'Segmento' not in df.columns:
        return
    
    logger.info("\n🔍 VERIFICACIÓN DE MAPEO DE SEGMENTOS:")
    logger.info("="*40)
    
    # Mostrar valores únicos antes y después del mapeo
    segmentos_unicos = df['Segmento'].unique()
    logger.info(f"Segmentos únicos encontrados: {len(segmentos_unicos)}")
    
    # Mostrar los segmentos más comunes
    segmentos_count = df['Segmento'].value_counts().head(10)
    for segmento, count in segmentos_count.items():
        logger.info(f"   {segmento}: {count:,} registros")

# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    df_no_entregas = procesar_no_entregas()
    analizar_datos_no_entregas(df_no_entregas)
    verificar_mapeo_segmentos(df_no_entregas)
    
    # Mostrar sample de datos
    if not df_no_entregas.empty:
        logger.info("\n🔍 Primeras 5 filas:")
        print(df_no_entregas.head())
        
        logger.info("\n📋 Estructura final:")
        logger.info(f"Columnas: {list(df_no_entregas.columns)}")
        for col in df_no_entregas.columns:
            logger.info(f"   {col}: {df_no_entregas[col].dtype}")