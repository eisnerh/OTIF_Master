import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

# Define la ruta del archivo excel usando una 'r' para ruta literal
# Pega aquí la ruta que copiaste del explorador de archivos
excel_path = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\VOL POR PORTAFOLIO ENE-2025.xlsx"

# Define la ruta donde se va a guardar el archivo parquet
parquet_path = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\volumen_procesado_familia.parquet"

# Crear el diccionario para almacenar el dataframe
volumen_procesado_familia = {}

# Leer el archivo excel y procesarlo
try:
    if not os.path.exists(excel_path):
        print(f"El archivo {excel_path} no fue encontrado. Por favor, verifica la ruta.")
        
    with pd.ExcelFile(excel_path) as xls:
        for sheet_name in xls.sheet_names:
            print(f"Leyendo la hoja: {sheet_name}")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            volumen_procesado_familia[sheet_name] = df
    
    # Concatenar todos los dataframes
    consolidado_volumen_procesado_familia = pd.concat(volumen_procesado_familia.values(), ignore_index=True)

    print('Se han leido los datos del archivo excel')
    
    # Crear la columna "Entregas" basado en la columna "Entrega"
    # Asignar 1 a la primera aparición de cada valor en "Entrega" y 0 a las siguientes
    
    if "Entrega" in consolidado_volumen_procesado_familia.columns:
        consolidado_volumen_procesado_familia['Entregas'] = (~consolidado_volumen_procesado_familia.duplicated(subset=['Entrega'])).astype(int)
        print("Columna 'Entregas' creada exitosamente.")
    else:
        print("Advertencia: No se encontró la columna 'Entrega'. La columna 'Entregas' no se creará.")

    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

    # Convertir el DataFrame a una tabla de PyArrow
    tabla_variacion_volumen = pa.Table.from_pandas(consolidado_volumen_procesado_familia)

    # Escribir la tabla en un archivo Parquet
    pq.write_table(tabla_variacion_volumen, parquet_path)
    
    print(f"El archivo parquet se guardará en: {parquet_path}")

except FileNotFoundError as e:
    print(f"Error: {e}")
except PermissionError:
    print(f"Error de permisos. No se puede escribir en: {parquet_path}")
    print("Verifica que tengas permisos de escritura en esa ubicación.")
except Exception as e:
    print(f"Error inesperado al procesar el archivo: {e}")