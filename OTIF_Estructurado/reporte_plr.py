import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

excel_path_folder = r"D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\OTIF ENT CD01\YTD\2025"

parquet_path = r"D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\reporte_plr.parquet"

# Columns to select
columns_to_select = ["Centro","Entrega","Ruta", "Cliente",	"Nombre del Cliente", "Ruta Dist.", "Viaje", "Guia Entrega","Origen","Fuerza Ventas",	"Region","Macro Canal","Clasificación Clt","Tipo Negocio","Provincia","Cantón","Distrito","Latitud","Longitud"]

# List to store the dataframes
all_dataframes = []

# Verify and create the destination directory
parquet_dir = os.path.dirname(parquet_path)
if not os.path.exists(parquet_dir):
    print(f"El directorio {parquet_dir} no existe. Se creará.")
    os.makedirs(parquet_dir)

# Read and process all Excel files in the folder
try:
    for file in os.listdir(excel_path_folder):
        if file.endswith('.xlsx'):
            excel_path = os.path.join(excel_path_folder, file)
            print(f"Procesando el archivo: {file}")

            try:
                # Read the Excel file and select columns from the "REP PLR" sheet
                df = pd.read_excel(excel_path, sheet_name="REP PLR", usecols=columns_to_select)
                all_dataframes.append(df)
                print(f"Datos de '{file}' leídos y agregados.")
            except ValueError:
                print(f"Advertencia: La hoja 'REP PLR' no fue encontrada en '{file}' o las columnas no coinciden.")
            except Exception as e:
                print(f"Error al leer '{file}': {e}")

    # Concatenate all DataFrames after the loop has finished
    if all_dataframes:
        consolidated_df = pd.concat(all_dataframes, ignore_index=True)
        print('Consolidación de datos completada.')

        print('Transformación de datos finalizada.')

        # Convert to PyArrow table and save to Parquet
        tabla_consolidada = pa.Table.from_pandas(consolidated_df)
        pq.write_table(tabla_consolidada, parquet_path)
        print(f'Archivo Parquet guardado exitosamente en: {parquet_path}')

    else:
        print("No se encontraron datos en los archivos de Excel para procesar.")

except FileNotFoundError:
    print(f"Error: La ruta de la carpeta '{excel_path_folder}' no fue encontrada.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")