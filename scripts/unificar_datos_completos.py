import pandas as pd
import os
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def unificar_datos_completos():
    """
    Crea los 3 archivos principales y une vol_portafolio con rep_plr por Entrega.
    """
    
    # Definir rutas de los archivos parquet
    archivo_rep_plr = Path("Data/Rep PLR/Output/REP_PLR_combinado.parquet")
    archivo_no_entregas = Path("Data/No Entregas/Output/No_Entregas_combinado_mejorado.parquet")
    archivo_vol_portafolio = Path("Data/Vol_Portafolio/Output/Vol_Portafolio_combinado.parquet")
    
    # Crear carpeta de salida si no existe
    carpeta_salida = Path("Data/Output_Unificado")
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. ARCHIVO REP_PLR
        logger.info("📊 Procesando archivo REP_PLR...")
        if archivo_rep_plr.exists():
            df_rep_plr = pd.read_parquet(archivo_rep_plr)
            logger.info(f"Rep PLR: {len(df_rep_plr)} filas y {len(df_rep_plr.columns)} columnas")
            
            # Guardar archivo Rep PLR
            archivo_rep_plr_final = carpeta_salida / "rep_plr.parquet"
            df_rep_plr.to_parquet(archivo_rep_plr_final, index=False)
            logger.info(f"✅ Archivo REP_PLR guardado: {archivo_rep_plr_final}")
        else:
            logger.error(f"❌ El archivo {archivo_rep_plr} no existe")
            return
        
        # 2. ARCHIVO NO_ENTREGAS
        logger.info("📦 Procesando archivo NO_ENTREGAS...")
        if archivo_no_entregas.exists():
            df_no_entregas = pd.read_parquet(archivo_no_entregas)
            logger.info(f"No Entregas: {len(df_no_entregas)} filas y {len(df_no_entregas.columns)} columnas")
            
            # Guardar archivo No Entregas
            archivo_no_entregas_final = carpeta_salida / "no_entregas.parquet"
            df_no_entregas.to_parquet(archivo_no_entregas_final, index=False)
            logger.info(f"✅ Archivo NO_ENTREGAS guardado: {archivo_no_entregas_final}")
        else:
            logger.error(f"❌ El archivo {archivo_no_entregas} no existe")
        
        # 3. ARCHIVO VOL_PORTAFOLIO
        logger.info("📈 Procesando archivo VOL_PORTAFOLIO...")
        if archivo_vol_portafolio.exists():
            df_vol_portafolio = pd.read_parquet(archivo_vol_portafolio)
            logger.info(f"Vol Portafolio: {len(df_vol_portafolio)} filas y {len(df_vol_portafolio.columns)} columnas")
            
            # Guardar archivo Vol Portafolio
            archivo_vol_portafolio_final = carpeta_salida / "vol_portafolio.parquet"
            df_vol_portafolio.to_parquet(archivo_vol_portafolio_final, index=False)
            logger.info(f"✅ Archivo VOL_PORTAFOLIO guardado: {archivo_vol_portafolio_final}")
        else:
            logger.error(f"❌ El archivo {archivo_vol_portafolio} no existe")
            return
        
        # 4. UNIR VOL_PORTAFOLIO CON REP_PLR POR ENTREGA
        logger.info("🔗 Uniendo VOL_PORTAFOLIO con REP_PLR por columna Entrega...")
        
        # Verificar que ambas tablas tengan la columna Entrega
        if 'Entrega' not in df_rep_plr.columns:
            logger.error("❌ La columna 'Entrega' no existe en REP_PLR")
            return
        
        if 'Entrega' not in df_vol_portafolio.columns:
            logger.error("❌ La columna 'Entrega' no existe en VOL_PORTAFOLIO")
            return
        
        # Mostrar información de las columnas antes del join
        logger.info(f"Columnas REP_PLR: {list(df_rep_plr.columns)}")
        logger.info(f"Columnas VOL_PORTAFOLIO: {list(df_vol_portafolio.columns)}")
        
        # Verificar tipos de datos de la columna Entrega
        logger.info(f"Tipo de datos Entrega en REP_PLR: {df_rep_plr['Entrega'].dtype}")
        logger.info(f"Tipo de datos Entrega en VOL_PORTAFOLIO: {df_vol_portafolio['Entrega'].dtype}")
        
        # Convertir a string para asegurar compatibilidad
        df_rep_plr['Entrega'] = df_rep_plr['Entrega'].astype(str)
        df_vol_portafolio['Entrega'] = df_vol_portafolio['Entrega'].astype(str)
        
        # Realizar el join (left join para mantener todos los registros de REP_PLR)
        df_unido = df_rep_plr.merge(
            df_vol_portafolio, 
            on='Entrega', 
            how='left', 
            suffixes=('_rep_plr', '_vol_portafolio')
        )
        
        logger.info(f"✅ Join completado: {len(df_unido)} filas y {len(df_unido.columns)} columnas")
        
        # Mostrar estadísticas del join
        registros_con_match = df_unido.dropna(subset=[col for col in df_unido.columns if 'vol_portafolio' in col]).shape[0]
        logger.info(f"📊 Registros con match en VOL_PORTAFOLIO: {registros_con_match:,}")
        logger.info(f"📊 Registros sin match: {len(df_unido) - registros_con_match:,}")
        
        # Guardar archivo unido
        archivo_unido = carpeta_salida / "rep_plr_vol_portafolio_unido.parquet"
        df_unido.to_parquet(archivo_unido, index=False)
        logger.info(f"✅ Archivo unido guardado: {archivo_unido}")
        
        # Mostrar las columnas del archivo unido
        logger.info("📋 Columnas del archivo unido:")
        for i, col in enumerate(df_unido.columns, 1):
            logger.info(f"  {i}. {col}")
        
        # 5. UNIR DATOS COMPLETOS CON NO_ENTREGAS POR ENTREGA Y FAMILIA
        logger.info("🔗 Uniendo datos completos con NO_ENTREGAS por columnas Entrega y Familia...")
        
        # Verificar que ambas tablas tengan las columnas necesarias
        columnas_requeridas_rep_plr = ['Entrega', 'Familia']
        columnas_requeridas_no_entregas = ['Entrega', 'Familia']
        
        for col in columnas_requeridas_rep_plr:
            if col not in df_unido.columns:
                logger.error(f"❌ La columna '{col}' no existe en datos completos")
                return
        
        for col in columnas_requeridas_no_entregas:
            if col not in df_no_entregas.columns:
                logger.error(f"❌ La columna '{col}' no existe en NO_ENTREGAS")
                return
        
        # Mostrar información de las columnas antes del join
        logger.info(f"Columnas datos completos: {list(df_unido.columns)}")
        logger.info(f"Columnas NO_ENTREGAS: {list(df_no_entregas.columns)}")
        
        # Verificar tipos de datos de las columnas de unión
        logger.info(f"Tipo de datos Entrega en datos completos: {df_unido['Entrega'].dtype}")
        logger.info(f"Tipo de datos Entrega en NO_ENTREGAS: {df_no_entregas['Entrega'].dtype}")
        logger.info(f"Tipo de datos Familia en datos completos: {df_unido['Familia'].dtype}")
        logger.info(f"Tipo de datos Familia en NO_ENTREGAS: {df_no_entregas['Familia'].dtype}")
        
        # Convertir a string para asegurar compatibilidad
        df_unido['Entrega'] = df_unido['Entrega'].astype(str)
        df_no_entregas['Entrega'] = df_no_entregas['Entrega'].astype(str)
        df_unido['Familia'] = df_unido['Familia'].astype(str)
        df_no_entregas['Familia'] = df_no_entregas['Familia'].astype(str)
        
        # Realizar el join (left join para mantener todos los registros de datos completos)
        df_final_unido = df_unido.merge(
            df_no_entregas, 
            on=['Entrega', 'Familia'], 
            how='left', 
            suffixes=('_completos', '_no_entregas')
        )
        
        logger.info(f"✅ Join completado: {len(df_final_unido)} filas y {len(df_final_unido.columns)} columnas")
        
        # Mostrar estadísticas del join
        registros_con_match = df_final_unido.dropna(subset=[col for col in df_final_unido.columns if 'no_entregas' in col]).shape[0]
        logger.info(f"📊 Registros con match en NO_ENTREGAS: {registros_con_match:,}")
        logger.info(f"📊 Registros sin match: {len(df_final_unido) - registros_con_match:,}")
        
        # Guardar archivo final unido
        archivo_final_unido = carpeta_salida / "datos_completos_con_no_entregas.parquet"
        df_final_unido.to_parquet(archivo_final_unido, index=False)
        logger.info(f"✅ Archivo final unido guardado: {archivo_final_unido}")
        
        # Mostrar las columnas del archivo final unido
        logger.info("📋 Columnas del archivo final unido:")
        for i, col in enumerate(df_final_unido.columns, 1):
            logger.info(f"  {i}. {col}")
        
        # Resumen final
        logger.info("\n🎉 ¡PROCESO COMPLETADO!")
        logger.info("=" * 50)
        logger.info("📁 Archivos generados en Data/Output_Unificado/:")
        logger.info("  • rep_plr.parquet")
        logger.info("  • no_entregas.parquet") 
        logger.info("  • vol_portafolio.parquet")
        logger.info("  • rep_plr_vol_portafolio_unido.parquet")
        logger.info("  • datos_completos_con_no_entregas.parquet (NUEVO)")
        
    except Exception as e:
        logger.error(f"❌ Error durante el procesamiento: {str(e)}")

if __name__ == "__main__":
    unificar_datos_completos()
