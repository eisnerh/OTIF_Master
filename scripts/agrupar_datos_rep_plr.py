# rep_plr_processor.py
import pandas as pd
import os
from pathlib import Path
import logging
import concurrent.futures
import gc
import time

# Importar módulo de configuración
try:
    from configuracion_sistema import cargar_configuracion, obtener_carpeta_salida, verificar_configuracion
except ImportError:
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
        if tipo == "rep_plr_output":
            return Path(config["rutas_archivos"]["rep_plr"]) / "Output"
        return Path("Data/Rep PLR/Output")
    
    def verificar_configuracion():
        return True

# Configurar logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Columnas clave para el join
COLUMNAS_REP_PLR = [
    'Entrega', 'Centro', 'Cliente', 'Nombre del Cliente',
    'Verificado', 'Guia Entrega', 'Fuerza Ventas', 'Desc Zona Vtas',
    'Desc Zona Superv', 'Fe.Entrega', 'Cajas Equiv.', 'Macro Canal',
    'Clasificación Clt', 'Tipo Negocio', 'Provincia', 'Cantón', 'Distrito',
    'Latitud', 'Longitud'
]

TIPO_DATOS_REP_PLR = {
    'Entrega': 'string',
    'Centro': 'category',
    'Cliente': 'string',
    'Nombre del Cliente': 'string',
    'Verificado': 'category',
    'Guia Entrega': 'string',
    'Fuerza Ventas': 'category',
    'Desc Zona Vtas': 'category',
    'Desc Zona Superv': 'category',
    'Fe.Entrega': 'datetime64[ns]',
    'Cajas Equiv.': 'float32',
    'Macro Canal': 'category',
    'Clasificación Clt': 'category',
    'Tipo Negocio': 'category',
    'Provincia': 'category',
    'Cantón': 'category',
    'Distrito': 'category',
    'Latitud': 'string',
    'Longitud': 'string'
}

def procesar_rep_plr():
    """
    Procesa archivos REP PLR y retorna DataFrame optimizado para join
    """
    logger.info("🚀 Iniciando procesamiento REP PLR...")
    
    if not verificar_configuracion():
        logger.error("❌ Error en configuración")
        return pd.DataFrame()
    
    config = cargar_configuracion()
    carpeta_rep_plr = Path(config["rutas_archivos"]["rep_plr"])
    
    # Buscar archivos
    archivos_excel = list(carpeta_rep_plr.glob("*.xlsx"))
    
    if not archivos_excel:
        logger.warning("⚠️ No se encontraron archivos")
        return pd.DataFrame({col: pd.Series(dtype=TIPO_DATOS_REP_PLR.get(col, 'object')) 
                           for col in COLUMNAS_REP_PLR})
    
    dataframes = []
    
    for archivo in archivos_excel:
        try:
            logger.info(f"📖 Procesando: {archivo.name}")
            
            # Leer solo columnas necesarias
            df = pd.read_excel(
                archivo,
                sheet_name="REP PLR",
                engine='openpyxl',
                usecols=COLUMNAS_REP_PLR,
                dtype=TIPO_DATOS_REP_PLR,
                na_values=['', 'NULL', 'N/A']
            )
            
            dataframes.append(df)
            logger.info(f"✅ {archivo.name}: {len(df):,} filas")
            
        except Exception as e:
            logger.error(f"❌ Error en {archivo.name}: {e}")
    
    if dataframes:
        df_combinado = pd.concat(dataframes, ignore_index=True)
        logger.info(f"📊 Total REP PLR: {len(df_combinado):,} filas")
        return df_combinado
    else:
        return pd.DataFrame()