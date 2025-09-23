import pandas as pd
import os

# Ruta del archivo original
ruta_archivo = r"C:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Planeamientos de Rutas - 1. Dashboard Planeamiento\ZRESGUIAS\ZRESGUIAS.xlsx"  # ← Cambia esto por la ruta real

# Nombre de la hoja que se va a conservar
hoja_objetivo = "PEGAR"

# Cargar solo la hoja PEGAR
df = pd.read_excel(ruta_archivo, sheet_name=hoja_objetivo)

# Asegúrate de que la columna de fecha esté en formato datetime
# Reemplaza 'fecha' por el nombre real de la columna que contiene la fecha
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

# Filtrar solo los datos del año actual (2025)
df_filtrado = df[df['Fecha'].dt.year == 2025]

# Crear nuevo nombre de archivo
nombre_archivo = os.path.basename(ruta_archivo)
nombre_nuevo = f"filtrado_{nombre_archivo}"
ruta_nueva = os.path.join(os.path.dirname(ruta_archivo), nombre_nuevo)

# Guardar el resultado en un nuevo archivo Excel
df_filtrado.to_excel(ruta_nueva, index=False)

print(f"Archivo guardado en: {ruta_nueva}")
