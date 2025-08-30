# unificador_principal.py
import pandas as pd
import logging
from pathlib import Path
from agrupar_datos_rep_plr import procesar_rep_plr
from agrupar_datos_vol_portafolio import procesar_vol_portafolio
from agrupar_datos_no_entregas_mejorado import procesar_no_entregas

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def probar_joins_con_parquet():
    """
    Prueba los joins únicamente con archivos parquet ya generados
    para diagnosticar problemas sin procesar archivos Excel
    """
    logger.info("🧪 Iniciando prueba de joins con archivos parquet...")
    
    # Rutas de archivos parquet
    try:
        from configuracion_sistema import cargar_configuracion
        config = cargar_configuracion()
        output_path = Path(config["rutas_archivos"]["output_unificado"])
    except:
        output_path = Path("Data/Output_Unificado")
    
    # Archivos parquet a cargar
    archivos_parquet = {
        'rep_plr': output_path / "rep_plr.parquet",
        'vol_portafolio': output_path / "vol_portafolio.parquet", 
        'no_entregas': output_path / "no_entregas.parquet"
    }
    
    # Cargar DataFrames desde parquet
    dataframes = {}
    for nombre, archivo in archivos_parquet.items():
        if archivo.exists():
            try:
                dataframes[nombre] = pd.read_parquet(archivo, engine='pyarrow')
                logger.info(f"✅ {nombre}: {len(dataframes[nombre]):,} filas cargadas desde {archivo.name}")
            except Exception as e:
                logger.error(f"❌ Error cargando {nombre}: {e}")
                dataframes[nombre] = pd.DataFrame()
        else:
            logger.warning(f"⚠️ Archivo no encontrado: {archivo}")
            dataframes[nombre] = pd.DataFrame()
    
    # Extraer DataFrames
    df_rep_plr = dataframes.get('rep_plr', pd.DataFrame())
    df_vol = dataframes.get('vol_portafolio', pd.DataFrame())
    df_no_entregas = dataframes.get('no_entregas', pd.DataFrame())
    
    # Realizar joins de prueba
    return realizar_joins_de_prueba(df_rep_plr, df_vol, df_no_entregas)

def realizar_joins_de_prueba(df_rep_plr, df_vol, df_no_entregas):
    """
    Realiza los joins de prueba con DataFrames ya cargados
    """
    logger.info("🔬 Iniciando joins de prueba...")
    
    # Diagnóstico inicial de DataFrames
    logger.info("\n📊 DIAGNÓSTICO INICIAL:")
    logger.info("="*50)
    logger.info(f"df_rep_plr: {len(df_rep_plr):,} filas, columnas: {list(df_rep_plr.columns)}")
    logger.info(f"df_vol: {len(df_vol):,} filas, columnas: {list(df_vol.columns)}")
    logger.info(f"df_no_entregas: {len(df_no_entregas):,} filas, columnas: {list(df_no_entregas.columns)}")
    
    # Verificar columnas necesarias
    logger.info("\n🔍 VERIFICACIÓN DE COLUMNAS:")
    logger.info("="*30)
    
    columnas_requeridas = {
        'df_rep_plr': ['Entrega'],
        'df_vol': ['Entrega', 'Zona'],
        'df_no_entregas': ['Entrega', 'Segmento', 'Cajas Eq.']
    }
    
    problemas_encontrados = []
    
    for df_name, columnas in columnas_requeridas.items():
        df = locals()[df_name]
        for col in columnas:
            if col not in df.columns:
                problema = f"❌ {df_name}: Columna '{col}' no encontrada"
                logger.error(problema)
                problemas_encontrados.append(problema)
            else:
                logger.info(f"✅ {df_name}: Columna '{col}' encontrada")
    
    if problemas_encontrados:
        logger.error(f"\n❌ PROBLEMAS ENCONTRADOS: {len(problemas_encontrados)}")
        for problema in problemas_encontrados:
            logger.error(f"   {problema}")
        return None
    
    # PRIMER JOIN: Vol Portafolio + REP PLR
    logger.info("\n🔗 PRIMER JOIN: Vol Portafolio + REP PLR")
    logger.info("="*40)
    
    if not df_vol.empty and not df_rep_plr.empty:
        # Verificar tipos de datos de la columna Entrega
        logger.info(f"Tipo de 'Entrega' en df_vol: {df_vol['Entrega'].dtype}")
        logger.info(f"Tipo de 'Entrega' en df_rep_plr: {df_rep_plr['Entrega'].dtype}")
        
        # Mostrar algunos valores de ejemplo
        logger.info(f"Ejemplos 'Entrega' en df_vol: {df_vol['Entrega'].head(3).tolist()}")
        logger.info(f"Ejemplos 'Entrega' en df_rep_plr: {df_rep_plr['Entrega'].head(3).tolist()}")
        
        # Verificar valores únicos
        entregas_vol = df_vol['Entrega'].nunique()
        entregas_rep = df_rep_plr['Entrega'].nunique()
        logger.info(f"Entregas únicas en df_vol: {entregas_vol:,}")
        logger.info(f"Entregas únicas en df_rep_plr: {entregas_rep:,}")
        
        # Verificar estructura de datos
        logger.info(f"📊 Estructura de df_vol:")
        logger.info(f"   - Total filas: {len(df_vol):,}")
        logger.info(f"   - Entregas únicas: {df_vol['Entrega'].nunique():,}")
        if 'Familia' in df_vol.columns:
            logger.info(f"   - Familias únicas: {df_vol['Familia'].nunique():,}")
            logger.info(f"   - Combinaciones Entrega+Familia únicas: {df_vol.groupby(['Entrega', 'Familia'], observed=False).size().shape[0]:,}")
        
        # Intentar el join
        try:
            df_join_1 = pd.merge(
                df_vol,  # Usar df_vol completo
                df_rep_plr,  # Agregar datos de REP PLR
                on='Entrega',
                how='left'
            )
            logger.info(f"✅ Primer join exitoso: {len(df_join_1):,} filas")
            
            # Estadísticas del primer join
            matches = df_join_1['Zona'].notna().sum()
            logger.info(f"   - Entregas con zona: {matches:,} ({(matches/len(df_join_1)*100):.1f}%)")
            logger.info(f"   - Entregas sin zona: {(len(df_join_1) - matches):,}")
            
        except Exception as e:
            logger.error(f"❌ Error en primer join: {e}")
            return None
    else:
        logger.error("❌ No se puede realizar el primer join - DataFrames vacíos")
        return None
    
    # SEGUNDO JOIN: Resultado anterior + No Entregas
    logger.info("\n🔗 SEGUNDO JOIN: Resultado anterior + No Entregas")
    logger.info("="*45)
    
    if not df_join_1.empty and not df_no_entregas.empty:
        # Verificar tipos de datos
        logger.info(f"Tipo de 'Entrega' en df_join_1: {df_join_1['Entrega'].dtype}")
        logger.info(f"Tipo de 'Entrega' en df_no_entregas: {df_no_entregas['Entrega'].dtype}")
        logger.info(f"Tipo de 'Segmento' en df_no_entregas: {df_no_entregas['Segmento'].dtype}")
        
        # Mostrar algunos valores de ejemplo
        logger.info(f"Ejemplos 'Entrega' en df_join_1: {df_join_1['Entrega'].head(3).tolist()}")
        logger.info(f"Ejemplos 'Entrega' en df_no_entregas: {df_no_entregas['Entrega'].head(3).tolist()}")
        logger.info(f"Ejemplos 'Segmento' en df_no_entregas: {df_no_entregas['Segmento'].head(3).tolist()}")
        
        # Verificar valores únicos
        entregas_join1 = df_join_1['Entrega'].nunique()
        entregas_ne = df_no_entregas['Entrega'].nunique()
        segmentos_ne = df_no_entregas['Segmento'].nunique()
        logger.info(f"Entregas únicas en df_join_1: {entregas_join1:,}")
        logger.info(f"Entregas únicas en df_no_entregas: {entregas_ne:,}")
        logger.info(f"Segmentos únicos en df_no_entregas: {segmentos_ne:,}")
        
        # Verificar si necesitamos mapear Familia a Segmento
        if 'Familia' in df_join_1.columns and 'Segmento' not in df_join_1.columns:
            logger.info("🔄 Mapeando columna 'Familia' a 'Segmento' para el join...")
            df_join_1['Segmento'] = df_join_1['Familia']
        
        # Intentar el join
        try:
            df_final = pd.merge(
                df_join_1,
                df_no_entregas[['Entrega', 'Segmento', 'Cajas Eq.']],
                on=['Entrega', 'Segmento'],
                how='left'
                # Removemos validate='one_to_one' para permitir múltiples combinaciones
            )
            logger.info(f"✅ Segundo join exitoso: {len(df_final):,} filas")
            
            # Estadísticas del segundo join
            matches = df_final['Cajas Eq.'].notna().sum()
            logger.info(f"   - Entregas con no entrega: {matches:,} ({(matches/len(df_final)*100):.1f}%)")
            logger.info(f"   - Entregas sin no entrega: {(len(df_final) - matches):,}")
            
        except Exception as e:
            logger.error(f"❌ Error en segundo join: {e}")
            return None
    else:
        logger.error("❌ No se puede realizar el segundo join - DataFrames vacíos")
        return None
    
    # Resumen final
    logger.info("\n🎉 PRUEBA DE JOINS COMPLETADA EXITOSAMENTE")
    logger.info("="*50)
    logger.info(f"📊 Resultado final: {len(df_final):,} filas")
    logger.info(f"📈 Columnas finales: {len(df_final.columns)}")
    logger.info(f"📋 Columnas: {list(df_final.columns)}")
    
    return df_final

def realizar_join_completo():
    """
    Realiza el join completo entre los tres datasets:
    1. Vol Portafolio + REP PLR (llave: Entrega)
    2. Resultado anterior + No Entregas (llave: Entrega + Segmento)
    """
    logger.info("🔄 Iniciando proceso de unificación...")
    
    # Paso 1: Procesar Volumen Portafolio
    logger.info("📊 Procesando Volumen Portafolio...")
    df_vol = procesar_vol_portafolio()
    
    # Paso 2: Procesar REP PLR
    logger.info("📊 Procesando REP PLR...")
    df_rep_plr = procesar_rep_plr()
    
    # Paso 3: Procesar No Entregas
    logger.info("📊 Procesando No Entregas...")
    df_no_entregas = procesar_no_entregas()
    
    # Paso 4: Join Vol Portafolio + REP PLR (llave: Entrega)
    logger.info("🔗 Realizando join Vol Portafolio + REP PLR...")
    
    # Diagnóstico de DataFrames
    logger.info(f"📊 df_vol: {len(df_vol):,} filas, columnas: {list(df_vol.columns)}")
    logger.info(f"📊 df_rep_plr: {len(df_rep_plr):,} filas, columnas: {list(df_rep_plr.columns)}")
    
    # Verificar columnas necesarias
    if 'Entrega' not in df_vol.columns:
        logger.error("❌ Columna 'Entrega' no encontrada en df_vol")
    if 'Entrega' not in df_rep_plr.columns:
        logger.error("❌ Columna 'Entrega' no encontrada en df_rep_plr")
    if 'Zona' not in df_vol.columns:
        logger.error("❌ Columna 'Zona' no encontrada en df_vol")
    
    if not df_vol.empty and not df_rep_plr.empty:
        # Verificar estructura de datos
        logger.info(f"📊 Estructura de df_vol:")
        logger.info(f"   - Total filas: {len(df_vol):,}")
        logger.info(f"   - Entregas únicas: {df_vol['Entrega'].nunique():,}")
        if 'Familia' in df_vol.columns:
            logger.info(f"   - Familias únicas: {df_vol['Familia'].nunique():,}")
            logger.info(f"   - Combinaciones Entrega+Familia únicas: {df_vol.groupby(['Entrega', 'Familia'], observed=False).size().shape[0]:,}")
        
        # Hacer left join manteniendo todas las combinaciones de Vol Portafolio
        # Esto permite que una entrega tenga múltiples familias/portafolios
        df_join_1 = pd.merge(
            df_vol,  # Usar df_vol completo, no limpiado
            df_rep_plr,  # Agregar datos de REP PLR
            on='Entrega',
            how='left'
        )
        logger.info(f"✅ Join 1 completado: {len(df_join_1):,} filas")
    else:
        logger.warning("⚠️ No se pudo realizar el primer join")
        df_join_1 = df_rep_plr.copy()
        df_join_1['Zona'] = None
        df_join_1['hoja_origen'] = None
    
    # Paso 5: Join resultado anterior + No Entregas (llave: Entrega + Segmento)
    logger.info("🔗 Realizando join con No Entregas...")
    
    # Diagnóstico de DataFrames para segundo join
    logger.info(f"📊 df_join_1: {len(df_join_1):,} filas, columnas: {list(df_join_1.columns)}")
    logger.info(f"📊 df_no_entregas: {len(df_no_entregas):,} filas, columnas: {list(df_no_entregas.columns)}")
    
    # Verificar columnas necesarias para segundo join
    if 'Entrega' not in df_join_1.columns:
        logger.error("❌ Columna 'Entrega' no encontrada en df_join_1")
    if 'Entrega' not in df_no_entregas.columns:
        logger.error("❌ Columna 'Entrega' no encontrada en df_no_entregas")
    if 'Segmento' not in df_no_entregas.columns:
        logger.error("❌ Columna 'Segmento' no encontrada en df_no_entregas")
    
    if not df_join_1.empty and not df_no_entregas.empty:
        # Verificar si necesitamos mapear Familia a Segmento
        if 'Familia' in df_join_1.columns and 'Segmento' not in df_join_1.columns:
            logger.info("🔄 Mapeando columna 'Familia' a 'Segmento' para el join...")
            df_join_1['Segmento'] = df_join_1['Familia']
        
        # Verificar estructura para el segundo join
        logger.info(f"📊 Estructura para segundo join:")
        logger.info(f"   - df_join_1: {len(df_join_1):,} filas")
        logger.info(f"   - df_no_entregas: {len(df_no_entregas):,} filas")
        logger.info(f"   - Combinaciones únicas en df_join_1: {df_join_1.groupby(['Entrega', 'Segmento'], observed=False).size().shape[0]:,}")
        logger.info(f"   - Combinaciones únicas en df_no_entregas: {df_no_entregas.groupby(['Entrega', 'Segmento'], observed=False).size().shape[0]:,}")
        
        # Hacer left join para mantener todas las combinaciones del primer join
        df_final = pd.merge(
            df_join_1,
            df_no_entregas[['Entrega', 'Segmento', 'Cajas Eq.']],
            on=['Entrega', 'Segmento'],
            how='left'
            # Removemos validate='one_to_one' para permitir múltiples combinaciones
        )
        logger.info(f"✅ Join 2 completado: {len(df_final):,} filas")
    else:
        logger.warning("⚠️ No se pudo realizar el segundo join")
        df_final = df_join_1.copy()
        df_final['Cajas Eq.'] = None
    
    # Paso 6: Limpieza y optimización final
    logger.info("✨ Realizando limpieza final...")
    
    # Rellenar valores nulos
    df_final['Cajas Eq.'] = df_final['Cajas Eq.'].fillna(0)
    df_final['Zona'] = df_final['Zona'].fillna('DESCONOCIDA')
    
    # Optimizar memoria final
    columnas_optimizar = {
        'Zona': 'category',
        'Cajas Eq.': 'float32'
    }
    
    for col, dtype in columnas_optimizar.items():
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(dtype)
    
    # Paso 7: Guardar resultado final
    logger.info("💾 Guardando resultado final...")
    
    # Usar configuración para la ruta de salida
    try:
        from configuracion_sistema import cargar_configuracion
        config = cargar_configuracion()
        output_path = Path(config["rutas_archivos"]["output_final"])
    except:
        output_path = Path("Data/Output/calculo_otif")
    
    output_path.mkdir(parents=True, exist_ok=True)
    archivo_final = output_path / "dataset_unificado_final.parquet"
    
    df_final.to_parquet(
        archivo_final,
        index=False,
        compression='snappy',
        engine='pyarrow'
    )
    
    # Mostrar resumen final
    logger.info("="*60)
    logger.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")
    logger.info("="*60)
    logger.info(f"📊 Filas totales: {len(df_final):,}")
    logger.info(f"📈 Columnas totales: {len(df_final.columns)}")
    logger.info(f"💾 Archivo guardado: {archivo_final}")
    
    if not df_final.empty:
        logger.info("\n🔍 Estadísticas de joins:")
        logger.info(f"   - Entregas con zona: {df_final['Zona'].notna().sum():,}")
        logger.info(f"   - Entregas sin no entrega: {(df_final['Cajas Eq.'] == 0).sum():,}")
        logger.info(f"   - Entregas con no entrega: {(df_final['Cajas Eq.'] > 0).sum():,}")
    
    logger.info("="*60)
    
    return df_final

def analizar_calidad_datos(df):
    """Analiza la calidad de los datos después del join"""
    if df.empty:
        return
    
    logger.info("\n🔍 ANÁLISIS DE CALIDAD DE DATOS:")
    logger.info("="*40)
    
    # Verificar llaves únicas
    entregas_unicas = df['Entrega'].nunique()
    logger.info(f"Entregas únicas: {entregas_unicas:,}")
    
    # Verificar completitud de joins
    join_1_completo = df['Zona'].notna().mean() * 100
    join_2_completo = (df['Cajas Eq.'] > 0).mean() * 100
    
    logger.info(f"Join 1 (Entregas con zona): {join_1_completo:.1f}%")
    logger.info(f"Join 2 (Entregas con no entrega): {join_2_completo:.1f}%")
    
    # Distribución por zona
    if 'Zona' in df.columns:
        logger.info("\n📊 Distribución por zona:")
        for zona, count in df['Zona'].value_counts().head(10).items():
            logger.info(f"   {zona}: {count:,}")

if __name__ == "__main__":
    import sys
    
    # Verificar si se quiere hacer prueba con parquet
    if len(sys.argv) > 1 and sys.argv[1] == "--test-parquet":
        logger.info("🧪 Ejecutando prueba con archivos parquet...")
        df_final = probar_joins_con_parquet()
        if df_final is not None:
            analizar_calidad_datos(df_final)
    else:
        logger.info("🔄 Ejecutando procesamiento completo...")
        df_final = realizar_join_completo()
        analizar_calidad_datos(df_final)