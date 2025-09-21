import pandas as pd
from datetime import datetime
import os

def limpiar_datos(df):
    # Agrupar y sumar columnas relevantes
    df = df.groupby([
        'Zona', 'Centro', 'Ruta Dist', 'Guía', 'Viaje', 'Tipo de Guía', 'Fecha', 'Cap. Real'
    ]).agg({
        'Cajas RS': 'sum',
        'Cajas Fisicas': 'sum',
        'Cajas Equivalentes': 'sum'
    }).reset_index()

    # Normalizar el número de viajes
    df['Viaje'] = df['Viaje'].apply(lambda x: 2 if x >= 2 else x)

    # Insertar columna de cantidad de viajes
    df.insert(4, 'Cant Viajes', "1")

    # Convertir la columna 'Fecha' a tipo datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    return df

# Ruta del archivo de entrada
archivo_excel = r'C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Planeamientos de Rutas - 1. Dashboard Planeamiento\ZRESGUIAS\ZRESGUIAS.xlsx'

# Cargar datos desde la hoja "PEGAR"
df_original = pd.read_excel(archivo_excel, sheet_name="PEGAR")

# Limpiar y transformar los datos
df_limpio = limpiar_datos(df_original)

# Filtrar registros del año actual
año_actual = datetime.now().year
df_filtrado = df_limpio[df_limpio['Fecha'].dt.year == año_actual]

# Crear carpeta de salida si no existe
carpeta_salida = r"c:\data\PLR"
os.makedirs(carpeta_salida, exist_ok=True)

# Guardar los datos filtrados en formato Parquet
archivo_salida = os.path.join(carpeta_salida, "zresguias.parquet")
df_filtrado.to_parquet(archivo_salida, index=False)

print("✅ Archivo guardado exitosamente en:", archivo_salida)
