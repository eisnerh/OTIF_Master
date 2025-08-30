# vol_portafolio_processor.py
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
        if tipo == "vol_portafolio_output":
            return Path(config["rutas_archivos"]["vol_portafolio"]) / "Output"
        return Path("Data/Vol_Portafolio/Output")
    
    def verificar_configuracion():
        return True

# Configurar logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Columnas clave para el join
COLUMNAS_VOL_PORTFOLIO = ['Entrega', 'Familia', 'Zona']
TIPO_DATOS_VOL = {
    'Entrega': 'string',
    'Familia': 'category',
    'Zona': 'category'
}

def procesar_vol_portafolio():
    """
    Procesa volumen portafolio y retorna DataFrame optimizado para join con REP PLR
    """
    logger.info("🚀 Iniciando procesamiento Volumen Portafolio...")
    
    if not verificar_configuracion():
        logger.error("❌ Error en configuración")
        return pd.DataFrame()
    
    config = cargar_configuracion()
    carpeta_vol = Path(config["rutas_archivos"]["vol_portafolio"])
    archivo_excel = carpeta_vol / "VOL POR PORTAFOLIO ENE-2025.xlsx"
    
    if not archivo_excel.exists():
        logger.warning("⚠️ Archivo no encontrado")
        return pd.DataFrame({col: pd.Series(dtype=TIPO_DATOS_VOL.get(col, 'object')) 
                          for col in COLUMNAS_VOL_PORTFOLIO})
    
    try:
        # Leer todas las hojas
        with pd.ExcelFile(archivo_excel, engine='openpyxl') as xls:
            hojas = xls.sheet_names
        
        dataframes = []
        
        for hoja in hojas:
            try:
                # Leer solo columnas necesarias para el join
                df = pd.read_excel(
                    archivo_excel,
                    sheet_name=hoja,
                    engine='openpyxl',
                    usecols=COLUMNAS_VOL_PORTFOLIO,
                    dtype=TIPO_DATOS_VOL
                )
                
                df['hoja_origen'] = hoja
                dataframes.append(df)
                logger.info(f"✅ Hoja {hoja}: {len(df):,} filas")
                
            except Exception as e:
                logger.warning(f"⚠️ Error en hoja {hoja}: {e}")
        
        if dataframes:
            df_combinado = pd.concat(dataframes, ignore_index=True)
            logger.info(f"📊 Total Vol Portafolio: {len(df_combinado):,} filas")
            return df_combinado
        else:
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return pd.DataFrame()