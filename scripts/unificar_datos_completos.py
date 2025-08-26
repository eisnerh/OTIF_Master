import pandas as pd
import os
from pathlib import Path
import logging
import gc

# Configurar logging con nivel más alto para reducir operaciones innecesarias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Solo configurar nivel INFO para el logger principal
logger.setLevel(logging.INFO)

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
            df_rep_plr = pd.read_parquet(archivo_rep_plr, engine='pyarrow')
            logger.info(f"Rep PLR: {len(df_rep_plr)} filas y {len(df_rep_plr.columns)} columnas")
        else:
            logger.warning(f"⚠️ El archivo {archivo_rep_plr} no existe. Creando archivo vacío...")
            # Crear DataFrame vacío con estructura básica
            df_rep_plr = pd.DataFrame({
                'Entrega': [],
                'Centro': [],
                'Familia': [],
                'archivo_origen': []
            })
            logger.info("✅ Archivo REP_PLR vacío creado con estructura básica")
        
        # Guardar archivo Rep PLR con compresión optimizada
        archivo_rep_plr_final = carpeta_salida / "rep_plr.parquet"
        
        # Verificar si el archivo ya existe
        archivo_existe = archivo_rep_plr_final.exists()
        
        df_rep_plr.to_parquet(
            archivo_rep_plr_final, 
            index=False,
            compression='snappy',
            engine='pyarrow'
        )
        
        if archivo_existe:
            logger.info(f"✅ Archivo REP_PLR actualizado: {archivo_rep_plr_final}")
        else:
            logger.info(f"✅ Archivo REP_PLR creado: {archivo_rep_plr_final}")
        
        # 2. ARCHIVO NO_ENTREGAS
        logger.info("📦 Procesando archivo NO_ENTREGAS...")
        if archivo_no_entregas.exists():
            df_no_entregas = pd.read_parquet(archivo_no_entregas, engine='pyarrow')
            logger.info(f"No Entregas: {len(df_no_entregas)} filas y {len(df_no_entregas.columns)} columnas")
        else:
            logger.warning(f"⚠️ El archivo {archivo_no_entregas} no existe. Creando archivo vacío...")
            # Crear DataFrame vacío con estructura básica
            df_no_entregas = pd.DataFrame({
                'Entrega': [],
                'Familia': [],
                'Cajas Equiv NE': [],
                'archivo_origen': []
            })
            logger.info("✅ Archivo NO_ENTREGAS vacío creado con estructura básica")
        
        # Guardar archivo No Entregas con compresión optimizada
        archivo_no_entregas_final = carpeta_salida / "no_entregas.parquet"
        
        # Verificar si el archivo ya existe
        archivo_existe = archivo_no_entregas_final.exists()
        
        df_no_entregas.to_parquet(
            archivo_no_entregas_final, 
            index=False,
            compression='snappy',
            engine='pyarrow'
        )
        
        if archivo_existe:
            logger.info(f"✅ Archivo NO_ENTREGAS actualizado: {archivo_no_entregas_final}")
        else:
            logger.info(f"✅ Archivo NO_ENTREGAS creado: {archivo_no_entregas_final}")
        
        # 3. ARCHIVO VOL_PORTAFOLIO
        logger.info("📈 Procesando archivo VOL_PORTAFOLIO...")
        if archivo_vol_portafolio.exists():
            df_vol_portafolio = pd.read_parquet(archivo_vol_portafolio, engine='pyarrow')
            logger.info(f"Vol Portafolio: {len(df_vol_portafolio)} filas y {len(df_vol_portafolio.columns)} columnas")
        else:
            logger.warning(f"⚠️ El archivo {archivo_vol_portafolio} no existe. Creando archivo vacío...")
            # Crear DataFrame vacío con estructura básica
            df_vol_portafolio = pd.DataFrame({
                'Entrega': [],
                'Familia': [],
                'Zona': [],
                'archivo_origen': []
            })
            logger.info("✅ Archivo VOL_PORTAFOLIO vacío creado con estructura básica")
        
        # Guardar archivo Vol Portafolio con compresión optimizada
        archivo_vol_portafolio_final = carpeta_salida / "vol_portafolio.parquet"
        
        # Verificar si el archivo ya existe
        archivo_existe = archivo_vol_portafolio_final.exists()
        
        df_vol_portafolio.to_parquet(
            archivo_vol_portafolio_final, 
            index=False,
            compression='snappy',
            engine='pyarrow'
        )
        
        if archivo_existe:
            logger.info(f"✅ Archivo VOL_PORTAFOLIO actualizado: {archivo_vol_portafolio_final}")
        else:
            logger.info(f"✅ Archivo VOL_PORTAFOLIO creado: {archivo_vol_portafolio_final}")
        
        # 4. UNIR VOL_PORTAFOLIO CON REP_PLR POR ENTREGA Y LUEGO CON NO_ENTREGAS
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
        
        # Liberar memoria de los dataframes originales
        del df_rep_plr
        del df_vol_portafolio
        gc.collect()
        
        logger.info(f"✅ Join completado: {len(df_unido)} filas y {len(df_unido.columns)} columnas")
        
        # Mostrar estadísticas del join
        registros_con_match = df_unido.dropna(subset=[col for col in df_unido.columns if 'vol_portafolio' in col]).shape[0]
        logger.info(f"📊 Registros con match en VOL_PORTAFOLIO: {registros_con_match:,}")
        logger.info(f"📊 Registros sin match: {len(df_unido) - registros_con_match:,}")
        
        # 5. UNIR DATOS COMPLETOS CON NO_ENTREGAS POR ENTREGA Y FAMILIA
        logger.info("🔗 Uniendo datos completos con NO_ENTREGAS por columnas Entrega y Familia...")
        
        # Verificar que ambas tablas tengan las columnas necesarias
        columnas_requeridas_rep_plr = ['Entrega', 'Familia']
        columnas_requeridas_no_entregas = ['Entrega', 'Familia']
        
        # Verificar columnas en df_unido (después del primer merge)
        if 'Entrega' not in df_unido.columns:
            logger.error(f"❌ La columna 'Entrega' no existe en datos completos")
            return
        
        # Buscar la columna Familia en df_unido (puede tener sufijos)
        columna_familia_unido = None
        for col in df_unido.columns:
            if 'Familia' in col:
                columna_familia_unido = col
                break
        
        if columna_familia_unido is None:
            logger.error(f"❌ No se encontró columna 'Familia' en datos completos")
            return
        
        logger.info(f"📋 Usando columna '{columna_familia_unido}' para el join")
        
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
        logger.info(f"Tipo de datos Familia en datos completos: {df_unido[columna_familia_unido].dtype}")
        logger.info(f"Tipo de datos Familia en NO_ENTREGAS: {df_no_entregas['Familia'].dtype}")
        
        # Convertir a string para asegurar compatibilidad
        df_unido['Entrega'] = df_unido['Entrega'].astype(str)
        df_no_entregas['Entrega'] = df_no_entregas['Entrega'].astype(str)
        df_unido[columna_familia_unido] = df_unido[columna_familia_unido].astype(str)
        df_no_entregas['Familia'] = df_no_entregas['Familia'].astype(str)
        
        # Realizar el join (left join para mantener todos los registros de datos completos)
        df_final_unido = df_unido.merge(
            df_no_entregas, 
            left_on=['Entrega', columna_familia_unido],
            right_on=['Entrega', 'Familia'],
            how='left', 
            suffixes=('_completos', '_no_entregas')
        )
        
        # Liberar memoria del dataframe intermedio
        del df_unido
        del df_no_entregas
        gc.collect()
        
        logger.info(f"✅ Join completado: {len(df_final_unido)} filas y {len(df_final_unido.columns)} columnas")
        
        # Mostrar estadísticas del join
        registros_con_match = df_final_unido.dropna(subset=[col for col in df_final_unido.columns if 'no_entregas' in col]).shape[0]
        logger.info(f"📊 Registros con match en NO_ENTREGAS: {registros_con_match:,}")
        logger.info(f"📊 Registros sin match: {len(df_final_unido) - registros_con_match:,}")
        
        # 6. AGREGAR COLUMNAS DE CONTEO: "Entregas" Y "No Entrega"
        logger.info("📊 Agregando columnas de conteo: 'Entregas' y 'No Entrega'...")
        
        # Crear columna "Entregas" - contar 1 solo para la primera ocurrencia de cada combinación única
        logger.info("🔢 Creando columna 'Entregas'...")
        
        # Crear un identificador único para cada combinación de Entrega + Familia
        df_final_unido['combinacion_entrega_familia'] = df_final_unido['Entrega'] + '_' + df_final_unido['Familia']
        
        # Marcar solo la primera ocurrencia de cada combinación única
        df_final_unido['Entregas'] = df_final_unido['combinacion_entrega_familia'].duplicated().map({True: 0, False: 1})
        
        # Crear columna "No Entrega" - contar 1 solo para la primera ocurrencia con "Cajas Equiv NE" > 0
        logger.info("❌ Creando columna 'No Entrega'...")
        
        # Buscar columnas que contengan "Cajas Equiv NE"
        columnas_cajas_equiv = [col for col in df_final_unido.columns if 'Cajas Equiv NE' in col]
        
        if columnas_cajas_equiv:
            logger.info(f"📋 Columnas encontradas con 'Cajas Equiv NE': {columnas_cajas_equiv}")
            
            # Crear un identificador único para cada combinación de Entrega + Familia
            df_final_unido['combinacion_no_entrega'] = df_final_unido['Entrega'] + '_' + df_final_unido['Familia']
            
            # Filtrar registros que tengan "Cajas Equiv NE" con valores > 0
            registros_con_no_entrega = df_final_unido[df_final_unido[columnas_cajas_equiv].sum(axis=1) > 0]
            
            if len(registros_con_no_entrega) > 0:
                # Crear una máscara para las combinaciones que tienen "Cajas Equiv NE" > 0
                mascara_cajas_equiv = df_final_unido[columnas_cajas_equiv].sum(axis=1) > 0
                
                # Marcar solo la primera ocurrencia de cada combinación que tenga "Cajas Equiv NE" > 0
                df_final_unido['No Entrega'] = 0
                
                # Para cada combinación única que tenga "Cajas Equiv NE" > 0, marcar solo la primera ocurrencia
                combinaciones_con_no_entrega = df_final_unido[mascara_cajas_equiv]['combinacion_no_entrega'].drop_duplicates()
                
                for combinacion in combinaciones_con_no_entrega:
                    # Encontrar el primer índice donde aparece esta combinación con "Cajas Equiv NE" > 0
                    indices = df_final_unido[(df_final_unido['combinacion_no_entrega'] == combinacion) & mascara_cajas_equiv].index
                    if len(indices) > 0:
                        primer_indice = indices[0]
                        df_final_unido.loc[primer_indice, 'No Entrega'] = 1
                
                logger.info(f"✅ Columna 'No Entrega' creada: {len(combinaciones_con_no_entrega)} combinaciones únicas marcadas")
            else:
                logger.warning("⚠️ No se encontraron registros con 'Cajas Equiv NE' > 0")
                df_final_unido['No Entrega'] = 0
        else:
            logger.warning("⚠️ No se encontraron columnas con 'Cajas Equiv NE'")
            df_final_unido['No Entrega'] = 0
        
        # Limpiar columnas temporales
        df_final_unido = df_final_unido.drop(['combinacion_entrega_familia', 'combinacion_no_entrega'], axis=1)
        
        # Mostrar estadísticas de las nuevas columnas
        total_entregas = df_final_unido['Entregas'].sum()
        total_no_entregas = df_final_unido['No Entrega'].sum()
        
        logger.info(f"📊 Estadísticas de las nuevas columnas:")
        logger.info(f"  • Total 'Entregas': {total_entregas:,}")
        logger.info(f"  • Total 'No Entrega': {total_no_entregas:,}")
        
        # Guardar archivo final unido con las nuevas columnas y compresión optimizada
        archivo_final_unido = carpeta_salida / "datos_completos_con_no_entregas.parquet"
        
        # Verificar si el archivo ya existe
        archivo_existe = archivo_final_unido.exists()
        
        df_final_unido.to_parquet(
            archivo_final_unido, 
            index=False,
            compression='snappy',
            engine='pyarrow'
        )
        
        if archivo_existe:
            logger.info(f"✅ Archivo final unido actualizado con nuevas columnas: {archivo_final_unido}")
        else:
            logger.info(f"✅ Archivo final unido creado con nuevas columnas: {archivo_final_unido}")
        
        # Mostrar las columnas del archivo final unido
        logger.info("📋 Columnas del archivo final unido:")
        for i, col in enumerate(df_final_unido.columns, 1):
            logger.info(f"  {i}. {col}")
        
        # Liberar memoria del dataframe final
        del df_final_unido
        gc.collect()
        
        # Resumen final
        logger.info("\n🎉 ¡PROCESO COMPLETADO!")
        logger.info("=" * 50)
        logger.info("📁 Archivos generados en Data/Output_Unificado/:")
        logger.info("  • rep_plr.parquet")
        logger.info("  • no_entregas.parquet") 
        logger.info("  • vol_portafolio.parquet")
        logger.info("  • datos_completos_con_no_entregas.parquet (CON NUEVAS COLUMNAS)")
        logger.info("")
        logger.info("🆕 Nuevas columnas agregadas a datos_completos_con_no_entregas.parquet:")
        logger.info("  • 'Entregas': Conta 1 solo para la primera ocurrencia de cada combinación única de Entrega + Familia")
        logger.info("  • 'No Entrega': Conta 1 solo para la primera ocurrencia de cada combinación única con 'Cajas Equiv NE' > 0")
        
    except Exception as e:
        logger.error(f"❌ Error durante el procesamiento: {str(e)}")

if __name__ == "__main__":
    unificar_datos_completos()
