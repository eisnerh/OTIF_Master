import pandas as pd
import os
from datetime import datetime

def extract_and_append_data(excel_file, sheet_name, output_file):
    print(f"Processing {sheet_name} from {excel_file}...")
    # Read the specified sheet from the Excel file
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        print(f"Successfully read {sheet_name}.")
    except FileNotFoundError:
        print(f"File {excel_file} not found.")
        return
    except ValueError:
        print(f"Sheet {sheet_name} not found in {excel_file}.")
        return
    except Exception as e: 
        print(f"An error occurred while reading {sheet_name}: {e}")
        return
    
    df['Fe.Entrega'] = pd.to_datetime(df['Fe.Entrega'], errors='coerce')
    
    if os.path.exists(output_file):
        print(f"El archivo {output_file} ya existe. Leyendo el archivo existente...")
        existing_df = pd.read_excel(output_file)
        # Check if the columns match
        if df.columns.tolist() != existing_df.columns.tolist():
            print("Las columnas no coinciden. No se puede combinar.")
            return
        # Append the new data to the existing DataFrame
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        print(f"Datos combinados. {len(df)} filas añadidas.")
    else:
        print(f"El archivo {output_file} no existe. Creando un nuevo archivo...")
        combined_df = df
        print(f"Datos leídos. {len(df)} filas añadidas.")
    
    try:
        combined_df.to_excel(output_file, index=False)
        print(f"Datos guardados en {output_file}.")
    except Exception as e:
        print(f"Error al guardar el archivo {output_file}: {e}")
    
def create_current_month_file(excel_file, sheet_name):
    print(f"Creando archivo del mes en curso para {sheet_name}...")
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df['Fe.Entrega'] = pd.to_datetime(df['Fe.Entrega'], errors='coerce')
    except Exception as e:
        print(f"Error al leer el archivo {excel_file}: {e}")
        return
    
    # Create a directory for monthly files if it doesn't exist
    monthly_dir = 'procesados_mes_'
    os.makedirs(monthly_dir, exist_ok=True)
    
    # Get current month and year
    current_month = datetime.now().strftime('%Y-%m')
    
    # Filter data for current month
    current_month_data = df[df['Fe.Entrega'].dt.to_period('M') == current_month]
    
    if not current_month_data.empty:
        output_file = os.path.join(monthly_dir, f"{sheet_name}_{current_month}.xlsx")
        
        # Check if file already exists
        if os.path.exists(output_file):
            print(f"El archivo {output_file} ya existe. Actualizando datos...")
            existing_df = pd.read_excel(output_file)
            # Check if columns match
            if current_month_data.columns.tolist() != existing_df.columns.tolist():
                print("Las columnas no coinciden. No se puede combinar.")
                return
            # Combine data
            combined_df = pd.concat([existing_df, current_month_data], ignore_index=True)
            print(f"Datos combinados. {len(current_month_data)} filas añadidas.")
        else:
            print(f"Creando nuevo archivo para el mes en curso...")
            combined_df = current_month_data
        
        try:
            combined_df.to_excel(output_file, index=False)
            print(f"Archivo mensual creado/actualizado: {output_file}")
        except Exception as e:
            print(f"Error al guardar el archivo {output_file}: {e}")
    else:
        print(f"No hay datos para el mes en curso ({current_month}) en la hoja {sheet_name}.")

# --- Main script execution ---
if __name__ == "__main__":
    # Define the Excel file and the sheets to process
    excel_file = r"C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\OTIF ENT CD01\YTD\2025\REP PLR ESTATUS ENTREGAS v25.xlsx"
    sheets = ['REP PLR']  # Add more sheet names as needed
    
    # Process each sheet
    for sheet in sheets:
        output_file = f"Procesamiento_YTD_{sheet}.xlsx"
        extract_and_append_data(excel_file, sheet, output_file)
        create_current_month_file(excel_file, sheet)