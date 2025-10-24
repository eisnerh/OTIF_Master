import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

# Define the paths
excel_folder_path = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Proyectos Reportes 3PL\3-Reporte de Tipificación de Devoluciones\País\2025"
parquet_path = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\volumen_no_procesado_familia.parquet"

# Columns to select
columns_to_select = ["Entrega", "Categoría", "Descrip Cod Rechazo", "Cajas Eq.", "Estado Entregas", "Segmento"]

# List to store the dataframes
all_dataframes = []

# Verify and create the destination directory
parquet_dir = os.path.dirname(parquet_path)
if not os.path.exists(parquet_dir):
    print(f"El directorio {parquet_dir} no existe. Se creará.")
    os.makedirs(parquet_dir)

# Read and process all Excel files in the folder
try:
    for file in os.listdir(excel_folder_path):
        if file.endswith('.xlsx'):
            excel_path = os.path.join(excel_folder_path, file)
            print(f"Procesando el archivo: {file}")
            
            try:
                # Read the Excel file and select columns from the "Z_DEVO_ALV" sheet
                df = pd.read_excel(excel_path, sheet_name="Z_DEVO_ALV", usecols=columns_to_select)
                all_dataframes.append(df)
                print(f"Datos de '{file}' leídos y agregados.")
            except ValueError:
                print(f"Advertencia: La hoja 'Z_DEVO_ALV' no fue encontrada en '{file}' o las columnas no coinciden.")
            except Exception as e:
                print(f"Error al leer '{file}': {e}")

    # Concatenate all DataFrames after the loop has finished
    if all_dataframes:
        consolidated_df = pd.concat(all_dataframes, ignore_index=True)
        print('Consolidación de datos completada.')

        # Data Transformation Steps
        # 1. Filtrar filas
        consolidated_df = consolidated_df[consolidated_df["Categoría"].isin(["BONI", "PROP", "VENT"])].copy()

        # 2. Rellenar valores nulos
        consolidated_df["Estado Entregas"] = consolidated_df["Estado Entregas"].fillna("Canc Parcial")

        # 3. Mapeo de valores en la columna "Segmento"
        replace_map = {
            "CERVEZA & BAS": "C&B",
            "CARBONATADAS": "BNA",
            "AGUAS & REFRESCOS": "BNA",
            "VINOS": "VYD",
            "DESTILADOS": "VYD",
            "ALIMENTOS": "ALI",
            "ENVASE": "ENV",
            "OTROS": "OTROS"
        }
        # Utilizar .replace con un diccionario para el mapeo
        consolidated_df["Segmento"] = consolidated_df["Segmento"].replace(replace_map)
        # Rellenar los valores que no están en el diccionario con "OTROS"
        consolidated_df["Segmento"] = consolidated_df["Segmento"].fillna("OTROS")
        # Rellenar los valores N/A con "OTROS"
        consolidated_df["Segmento"] = consolidated_df["Segmento"].replace("#N/A", "OTROS")

        # Rellenar los valores N/A con "OTROS"
        consolidated_df["Segmento"] = consolidated_df["Segmento"].replace("N/A", "OTROS")
        
        # 4. Agrupar, sumar y renombrar
        # Agrupar y sumar
        grouped_df = consolidated_df.groupby(["Entrega", "Descrip Cod Rechazo", "Estado Entregas", "Segmento"]).sum(numeric_only=True)
        # Resetear el índice para que las columnas agrupadas vuelvan a ser columnas regulares
        grouped_df = grouped_df.reset_index()
        # Renombrar la columna
        grouped_df = grouped_df.rename(columns={"Cajas Eq.": "Cajas Eq. No Entregadas"})

        print('Transformación de datos finalizada.')
        
        # Crear la columna 'No Entregas' basada en la columna 'Entrega'
        # Asigna 1 a la primera aparición de cada valor en 'Entrega' y 0 a las siguientes.
        if "Entrega" in grouped_df.columns:
            grouped_df['No Entregas'] = (~grouped_df.duplicated(subset=['Entrega'])).astype(int)
            print("Columna 'No Entregas' creada exitosamente.")
        else:
            print("Advertencia: No se encontró la columna 'Entrega'. La columna 'No Entregas' no se creará.")

        # Convert to PyArrow table and save to Parquet
        tabla_consolidada = pa.Table.from_pandas(grouped_df)
        pq.write_table(tabla_consolidada, parquet_path)
        print(f'Archivo Parquet guardado exitosamente en: {parquet_path}')

    else:
        print("No se encontraron datos en los archivos de Excel para procesar.")

except FileNotFoundError:
    print(f"Error: La ruta de la carpeta '{excel_folder_path}' no fue encontrada.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")