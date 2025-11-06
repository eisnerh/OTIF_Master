# -*- coding: utf-8 -*-
"""
Script: procesar_txt_a_excel.py
Descripción:
  - Procesa archivos .txt de reportes SAP y los convierte a Excel
  - Aplica transformaciones específicas para cada tipo de reporte
  - Elimina columnas y filas según las reglas de negocio
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging

# Logging
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("procesar_txt_excel")

# Directorio de reportes
REPORTES_DIR = Path(r"C:/data/SAP_Extraction/reportes_ultima_hora")


def leer_archivo_txt(ruta_txt: Path) -> pd.DataFrame:
    """Lee un archivo .txt tabulado y lo convierte en DataFrame"""
    try:
        # Leer archivo con separador de tabulación
        with open(ruta_txt, 'r', encoding='utf-8', errors='replace') as f:
            lineas = f.readlines()
        
        # Separar por tabulaciones
        data = [linea.rstrip('\r\n').split('\t') for linea in lineas]
        df = pd.DataFrame(data)
        
        logger.info(f"  Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
        return df
        
    except Exception as e:
        raise RuntimeError(f"Error al leer {ruta_txt}: {e}")


def procesar_y_dev_45(df: pd.DataFrame) -> pd.DataFrame:
    """
    Y_DEV_45:
    - Eliminar columnas A y C (índices 0 y 2)
    - Eliminar fila 6 (índice 5)
    - Eliminar primeras 4 filas
    """
    logger.info("  Aplicando transformaciones Y_DEV_45...")
    
    # Eliminar fila 6 (índice 5)
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    
    # Eliminar primeras 4 filas
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # Eliminar columnas A y C (índices 0 y 2)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 2]]
    df = df.iloc[:, columnas_mantener]
    
    return df


def procesar_monitor_guias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Monitor_Guias (Y_DEV_74):
    - Eliminar columnas A y C (índices 0 y 2)
    - Eliminar fila 6 (índice 5)
    - Eliminar primeras 4 filas
    """
    logger.info("  Aplicando transformaciones Monitor de Guías...")
    
    # Eliminar fila 6 (índice 5)
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    
    # Eliminar primeras 4 filas
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # Eliminar columnas A y C (índices 0 y 2)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 2]]
    df = df.iloc[:, columnas_mantener]
    
    return df


def procesar_y_dev_82(df: pd.DataFrame) -> pd.DataFrame:
    """
    Y_DEV_82:
    - Eliminar columnas A y D (índices 0 y 3)
    - Eliminar fila 6 (índice 5)
    - Eliminar primeras 4 filas
    """
    logger.info("  Aplicando transformaciones Y_DEV_82...")
    
    # Eliminar fila 6 (índice 5)
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    
    # Eliminar primeras 4 filas
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # Eliminar columnas A y D (índices 0 y 3)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 3]]
    df = df.iloc[:, columnas_mantener]
    
    return df


def procesar_rep_plr(df: pd.DataFrame) -> pd.DataFrame:
    """
    REP_PLR (Y_REP_PLR):
    - Eliminar columna A (índice 0)
    - Eliminar fila 5 (índice 4)
    - Eliminar primeras 4 filas
    - Filtrar columna H = "1"
    """
    logger.info("  Aplicando transformaciones REP_PLR...")
    
    # Eliminar fila 5 (índice 4)
    if len(df) > 4:
        df = df.drop(index=4).reset_index(drop=True)
    
    # Eliminar primeras 4 filas
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # Eliminar columna A (índice 0)
    if len(df.columns) > 0:
        df = df.iloc[:, 1:]
    
    # Filtrar columna H = "1" (ahora es índice 7 porque eliminamos columna A)
    if len(df.columns) > 7 and len(df) > 0:
        # La primera fila puede ser encabezados
        df = df[df.iloc[:, 7] == "1"]
    
    return df


def procesar_zhbo(df: pd.DataFrame) -> pd.DataFrame:
    """
    ZHBO:
    - Eliminar columnas A y B (índices 0 y 1)
    - Eliminar fila 6 (índice 5)
    - Eliminar primeras 4 filas
    """
    logger.info("  Aplicando transformaciones ZHBO...")
    
    # Eliminar fila 6 (índice 5)
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    
    # Eliminar primeras 4 filas
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # Eliminar columnas A y B (índices 0 y 1)
    if len(df.columns) > 2:
        df = df.iloc[:, 2:]
    
    return df


def procesar_zred(df: pd.DataFrame) -> pd.DataFrame:
    """
    ZRED:
    - Eliminar columna A (índice 0)
    - Eliminar fila 5 (índice 4)
    - Eliminar primeras 3 filas
    """
    logger.info("  Aplicando transformaciones ZRED...")
    
    # Eliminar fila 5 (índice 4)
    if len(df) > 4:
        df = df.drop(index=4).reset_index(drop=True)
    
    # Eliminar primeras 3 filas
    if len(df) > 3:
        df = df.iloc[3:].reset_index(drop=True)
    
    # Eliminar columna A (índice 0)
    if len(df.columns) > 0:
        df = df.iloc[:, 1:]
    
    return df


def procesar_zresguias(df: pd.DataFrame) -> pd.DataFrame:
    """
    ZRESGUIAS:
    - Eliminar columnas A, B y O (índices 0, 1 y 14)
    - Eliminar fila 6 (índice 5)
    - Eliminar primeras 4 filas
    """
    logger.info("  Aplicando transformaciones ZRESGUIAS...")
    
    # Eliminar fila 6 (índice 5)
    if len(df) > 5:
        df = df.drop(index=5).reset_index(drop=True)
    
    # Eliminar primeras 4 filas
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # Eliminar columnas A, B y O (índices 0, 1 y 14)
    columnas_mantener = [i for i in range(len(df.columns)) if i not in [0, 1, 14]]
    df = df.iloc[:, columnas_mantener]
    
    return df


def procesar_z_devo_alv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Z_DEVO_ALV:
    - Eliminar columna A (índice 0)
    - Eliminar fila 5 (índice 4)
    - Eliminar primeras 3 filas
    """
    logger.info("  Aplicando transformaciones Z_DEVO_ALV...")
    
    # Eliminar fila 5 (índice 4)
    if len(df) > 4:
        df = df.drop(index=4).reset_index(drop=True)
    
    # Eliminar primeras 3 filas
    if len(df) > 3:
        df = df.iloc[3:].reset_index(drop=True)
    
    # Eliminar columna A (índice 0)
    if len(df.columns) > 0:
        df = df.iloc[:, 1:]
    
    return df


def procesar_zsd_incidencias(df: pd.DataFrame) -> pd.DataFrame:
    """
    ZSD_INCIDENCIAS:
    - Procesamiento básico (sin transformaciones específicas por ahora)
    """
    logger.info("  Aplicando transformaciones ZSD_INCIDENCIAS (básicas)...")
    
    # Eliminar primeras 5 filas por defecto
    if len(df) > 5:
        df = df.iloc[5:].reset_index(drop=True)
    
    return df


# Mapeo de carpetas a funciones de procesamiento
PROCESADORES = {
    'Y_DEV_45': procesar_y_dev_45,
    'Y_DEV_74': procesar_monitor_guias,
    'Y_DEV_82': procesar_y_dev_82,
    'Y_REP_PLR': procesar_rep_plr,
    'ZHBO': procesar_zhbo,
    'ZRED': procesar_zred,
    'ZRESGUIAS': procesar_zresguias,
    'Z_DEVO_ALV': procesar_z_devo_alv,
    'ZSD_INCIDENCIAS': procesar_zsd_incidencias,
}


def procesar_archivo(ruta_txt: Path, procesador_func) -> Path:
    """Procesa un archivo .txt y lo convierte a Excel"""
    try:
        logger.info(f"Procesando: {ruta_txt.name}")
        
        # Leer archivo
        df = leer_archivo_txt(ruta_txt)
        
        # Aplicar transformaciones
        df_procesado = procesador_func(df)
        
        # Generar nombre de archivo Excel
        ruta_excel = ruta_txt.with_suffix('.xlsx')
        
        # Guardar Excel
        df_procesado.to_excel(ruta_excel, index=False, header=False, engine='openpyxl')
        
        logger.info(f"  ✓ Excel generado: {ruta_excel.name}")
        logger.info(f"    Dimensiones finales: {len(df_procesado)} filas x {len(df_procesado.columns)} columnas")
        
        return ruta_excel
        
    except Exception as e:
        logger.error(f"  ✗ Error al procesar {ruta_txt.name}: {e}")
        return None


def procesar_todos_los_reportes(directorio_base: Path = REPORTES_DIR):
    """Procesa todos los archivos .txt en las carpetas de reportes"""
    
    logger.info("=" * 70)
    logger.info("INICIO: Conversión de TXT a Excel")
    logger.info("=" * 70)
    logger.info(f"Directorio base: {directorio_base}")
    logger.info(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    if not directorio_base.exists():
        logger.error(f"El directorio no existe: {directorio_base}")
        return 1
    
    archivos_procesados = []
    archivos_fallidos = []
    
    # Buscar archivos .txt en cada carpeta
    for carpeta_nombre, procesador_func in PROCESADORES.items():
        carpeta = directorio_base / carpeta_nombre
        
        if not carpeta.exists():
            logger.warning(f"Carpeta no encontrada: {carpeta_nombre}")
            continue
        
        # Buscar archivos .txt en la carpeta
        archivos_txt = list(carpeta.glob("*.txt"))
        
        if not archivos_txt:
            logger.info(f"[{carpeta_nombre}] No se encontraron archivos .txt")
            continue
        
        logger.info(f"\n[{carpeta_nombre}] Encontrados {len(archivos_txt)} archivo(s) .txt")
        
        for archivo_txt in archivos_txt:
            resultado = procesar_archivo(archivo_txt, procesador_func)
            if resultado:
                archivos_procesados.append((carpeta_nombre, resultado))
            else:
                archivos_fallidos.append((carpeta_nombre, archivo_txt.name))
    
    # Resumen final
    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN DE PROCESAMIENTO")
    logger.info("=" * 70)
    logger.info(f"Total de archivos procesados: {len(archivos_procesados)}")
    logger.info(f"Total de archivos fallidos: {len(archivos_fallidos)}")
    logger.info("=" * 70)
    
    if archivos_procesados:
        logger.info("\n✓ ARCHIVOS PROCESADOS EXITOSAMENTE:")
        for carpeta, archivo in archivos_procesados:
            logger.info(f"  • [{carpeta}] {archivo.name}")
    
    if archivos_fallidos:
        logger.info("\n✗ ARCHIVOS CON ERRORES:")
        for carpeta, archivo in archivos_fallidos:
            logger.info(f"  • [{carpeta}] {archivo}")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(archivos_fallidos) == 0:
        logger.info("PROCESO COMPLETADO EXITOSAMENTE")
    else:
        logger.info("PROCESO COMPLETADO CON ADVERTENCIAS")
    
    logger.info("=" * 70)
    
    return 0 if len(archivos_fallidos) == 0 else 1


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Procesa archivos .txt de reportes SAP y los convierte a Excel"
    )
    parser.add_argument(
        "--directorio",
        type=str,
        default=str(REPORTES_DIR),
        help="Directorio base de reportes (por defecto: C:/data/SAP_Extraction/reportes_ultima_hora)"
    )
    
    args = parser.parse_args()
    
    directorio = Path(args.directorio)
    resultado = procesar_todos_los_reportes(directorio)
    
    return resultado


if __name__ == "__main__":
    sys.exit(main())

