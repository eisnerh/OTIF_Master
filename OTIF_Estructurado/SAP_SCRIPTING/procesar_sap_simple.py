#!/usr/bin/env python3
"""
Script especializado para procesar archivos SAP sin emojis
"""

import pandas as pd
import os
import json
from datetime import datetime

def process_sap_file_content(file_path, encodings_to_try):
    """
    Process SAP file with specialized method that works
    """
    try:
        # Read the file line by line to understand its structure
        # "C:\data\Nite\SAP_Document\REP_PLR_HOY.xls"
        lines = None
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                print(f"Successfully read file with encoding: {encoding}")
                break
            except:
                continue
        
        if lines is None:
            print("Could not read file with any encoding")
            return None
        
        print(f"File has {len(lines)} lines")
        
        # Find the data section (skip headers)
        data_start = None
        for i, line in enumerate(lines):
            if 'Centro' in line and 'Fe.Entrega' in line and 'Ruta' in line:
                data_start = i
                print(f"Found header at line {i+1}")
                break
        
        if data_start is None:
            print("Could not find data header")
            return None
        
        # Extract header
        header_line = lines[data_start].strip()
        headers = [col.strip() for col in header_line.split('\t')]
        print(f"Found {len(headers)} columns: {headers[:5]}...")
        
        # Extract data rows
        data_rows = []
        for i in range(data_start + 1, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('19.09.2025'):  # Skip date headers
                row_data = line.split('\t')
                if len(row_data) >= len(headers):
                    data_rows.append(row_data[:len(headers)])
        
        print(f"Found {len(data_rows)} data rows")
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Clean up the DataFrame
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        print(f"DataFrame created with shape: {df.shape}")
        return df
        
    except Exception as e:
        print(f"Error processing SAP file content: {e}")
        return None


def transform_data_for_powerbi(df):
    """
    Transform and clean data for optimal Power BI compatibility
    """
    print("Transforming data for Power BI compatibility...")
    
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Remove any rows that are completely empty or contain only whitespace
    df_clean = df_clean.dropna(how='all')
    df_clean = df_clean[~df_clean.astype(str).eq('').all(axis=1)]
    
    # Clean column names - remove extra spaces and special characters
    df_clean.columns = df_clean.columns.str.strip()
    df_clean.columns = df_clean.columns.str.replace(r'\s+', ' ', regex=True)
    
    # Convert date columns to proper datetime format
    date_columns = ['Fe.Entrega', 'Fecha Guía', 'Creado el']
    for col in date_columns:
        if col in df_clean.columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            except:
                print(f"Warning: Could not convert {col} to datetime")
    
    # Convert time columns to proper time format
    time_columns = ['Hora Guía', 'Hora']
    for col in time_columns:
        if col in df_clean.columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], format='%H:%M:%S', errors='coerce').dt.time
            except:
                print(f"Warning: Could not convert {col} to time")
    
    # Convert numeric columns
    numeric_columns = ['Cajas R.S.', 'Cajas Físicas', 'Cajas Equiv.', 'Ruta', 'Entrega', 'Cliente']
    for col in numeric_columns:
        if col in df_clean.columns:
            try:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            except:
                print(f"Warning: Could not convert {col} to numeric")
    
    # Clean text columns - remove extra spaces
    text_columns = ['Centro', 'Nombre del Cliente', 'Estatus', 'Ruta Dist.', 'Camión', 
                   'Guia Entrega', 'Rol Alisto', 'Reprogramado', 'Ped. Clte', 'Ped. SAP',
                   'Tipo Ped.', 'Desc. Tipo', 'Origen', 'Tipo Ruta', 'Fuerza Ventas',
                   'Region', 'Zona Vtas', 'Desc Zona Vtas', 'Zona Superv', 'Desc Zona Superv',
                   'Agente Vtas', 'Nombre']
    
    for col in text_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].replace('nan', '')
    
    # Add calculated columns useful for Power BI analysis
    if 'Fe.Entrega' in df_clean.columns:
        df_clean['Año'] = df_clean['Fe.Entrega'].dt.year
        df_clean['Mes'] = df_clean['Fe.Entrega'].dt.month
        df_clean['Día'] = df_clean['Fe.Entrega'].dt.day
        df_clean['Día_Semana'] = df_clean['Fe.Entrega'].dt.day_name()
        df_clean['Semana'] = df_clean['Fe.Entrega'].dt.isocalendar().week
    
    # Add performance indicators
    if 'Cajas R.S.' in df_clean.columns and 'Cajas Físicas' in df_clean.columns:
        df_clean['Diferencia_Cajas'] = df_clean['Cajas Físicas'] - df_clean['Cajas R.S.']
        df_clean['Porcentaje_Cumplimiento'] = (df_clean['Cajas Físicas'] / df_clean['Cajas R.S.'] * 100).round(2)
    
    # Add status categories for better filtering in Power BI
    if 'Estatus' in df_clean.columns:
        df_clean['Estatus_Categoria'] = df_clean['Estatus'].apply(categorize_status)
    
    # Add route type categories
    if 'Tipo Ruta' in df_clean.columns:
        df_clean['Tipo_Ruta_Categoria'] = df_clean['Tipo Ruta'].apply(categorize_route_type)
    
    print(f"Data transformation completed. Final dataset shape: {df_clean.shape}")
    return df_clean


def categorize_status(status):
    """Categorize delivery status for better Power BI filtering"""
    if pd.isna(status):
        return 'Sin Estatus'
    
    status_str = str(status).strip()
    if status_str in ['5']:
        return 'Entregado'
    elif status_str in ['1', '2', '3']:
        return 'En Proceso'
    elif status_str in ['4']:
        return 'Pendiente'
    else:
        return 'Otro'


def categorize_route_type(route_type):
    """Categorize route type for better Power BI analysis"""
    if pd.isna(route_type):
        return 'Sin Tipo'
    
    route_str = str(route_type).strip().upper()
    if 'MODERNO' in route_str:
        return 'Moderno'
    elif 'TRADICIONAL' in route_str:
        return 'Tradicional'
    elif 'RURAL' in route_str:
        return 'Rural'
    else:
        return 'Otro'


def save_powerbi_files(df, excel_path, csv_path, parquet_path):
    """
    Save the dataframe in multiple formats optimized for Power BI
    """
    print("Saving files in Power BI compatible formats...")
    
    try:
        # Save as Excel with proper formatting
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='REP_PLR_Data', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['REP_PLR_Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Excel file saved: {excel_path}")
        
        # Save as CSV with UTF-8 encoding (Power BI preferred)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"CSV file saved: {csv_path}")
        
        # Save as Parquet for better performance in Power BI
        df.to_parquet(parquet_path, index=False)
        print(f"Parquet file saved: {parquet_path}")
        
        # Create a metadata file for Power BI
        create_powerbi_metadata(df, os.path.dirname(excel_path))
        
        print("\nAll Power BI compatible files created successfully!")
        print("Recommended file for Power BI: Use the .parquet file for best performance")
        print("Use the .csv file if you need to import into other tools")
        print("Use the .xlsx file for manual review and analysis")
        
    except Exception as e:
        print(f"Error saving Power BI files: {e}")


def create_powerbi_metadata(df, output_path):
    """
    Create a metadata file with column descriptions for Power BI
    """
    try:
        metadata = {
            "dataset_info": {
                "name": "REP_PLR_HOY",
                "description": "Reporte de Planeamiento de Rutas - Datos del día",
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_records": len(df),
                "total_columns": len(df.columns)
            },
            "columns": {}
        }
        
        # Define column descriptions
        column_descriptions = {
            "Centro": "Centro de distribución",
            "Fe.Entrega": "Fecha de entrega programada",
            "Ruta": "Número de ruta",
            "Entrega": "Número de entrega",
            "Cliente": "Código del cliente",
            "Nombre del Cliente": "Nombre del cliente",
            "Estatus": "Estatus de la entrega (5=Entregado)",
            "Verificado": "Indicador de verificación",
            "Cajas R.S.": "Cajas requeridas según sistema",
            "Cajas Físicas": "Cajas físicas entregadas",
            "Cajas Equiv.": "Cajas equivalentes",
            "Ruta Dist.": "Ruta de distribución",
            "Viaje": "Número de viaje",
            "Camión": "Número de camión",
            "Guia Entrega": "Número de guía de entrega",
            "Fecha Guía": "Fecha de la guía",
            "Hora Guía": "Hora de la guía",
            "Creado el": "Fecha de creación del registro",
            "Hora": "Hora de creación",
            "Rol Alisto": "Rol de alistamiento",
            "Reprogramado": "Indicador de reprogramación",
            "Ped. Clte": "Pedido del cliente",
            "Ped. SAP": "Pedido en SAP",
            "Ped. Traslado": "Pedido de traslado",
            "Tipo Ped.": "Tipo de pedido",
            "Desc. Tipo": "Descripción del tipo",
            "Origen": "Origen del pedido",
            "Tipo Ruta": "Tipo de ruta",
            "Fuerza Ventas": "Fuerza de ventas",
            "Region": "Región",
            "Zona Vtas": "Zona de ventas",
            "Desc Zona Vtas": "Descripción de zona de ventas",
            "Zona Superv": "Zona de supervisión",
            "Desc Zona Superv": "Descripción de zona de supervisión",
            "Agente Vtas": "Código del agente de ventas",
            "Nombre": "Nombre del agente de ventas",
            "Año": "Año de la entrega (calculado)",
            "Mes": "Mes de la entrega (calculado)",
            "Día": "Día de la entrega (calculado)",
            "Día_Semana": "Día de la semana (calculado)",
            "Semana": "Semana del año (calculado)",
            "Diferencia_Cajas": "Diferencia entre cajas físicas y requeridas (calculado)",
            "Porcentaje_Cumplimiento": "Porcentaje de cumplimiento (calculado)",
            "Estatus_Categoria": "Categoría del estatus (calculado)",
            "Tipo_Ruta_Categoria": "Categoría del tipo de ruta (calculado)"
        }
        
        # Add column information
        for col in df.columns:
            metadata["columns"][col] = {
                "description": column_descriptions.get(col, "Sin descripción disponible"),
                "data_type": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique())
            }
        
        # Save metadata as JSON
        metadata_path = os.path.join(output_path, "REP_PLR_HOY_Metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata file saved: {metadata_path}")
        
    except Exception as e:
        print(f"Warning: Could not create metadata file: {e}")


def process_sap_file():
    """
    Procesa el archivo SAP con formato específico
    """
    try:
        # Define file paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        source_data_dir = os.path.join(script_dir, "data")
        existing_file = os.path.join(source_data_dir, "REP_PLR_HOY.xls")
        
        # Use the specified directory C:\Data\Nite for output
        data_dir = r"C:\Data\Nite"
        os.makedirs(data_dir, exist_ok=True)
        print(f"Using output directory: {data_dir}")
        
        if not os.path.exists(existing_file):
            print(f"File not found: {existing_file}")
            return False
        
        print(f"Processing SAP file: {existing_file}")
        
        # Define output file paths
        base_name = "REP_PLR_HOY"
        excel_path = os.path.join(data_dir, f"{base_name}_PowerBI.xlsx")
        csv_path = os.path.join(data_dir, f"{base_name}_PowerBI.csv")
        parquet_path = os.path.join(data_dir, f"{base_name}_PowerBI.parquet")
        
        # Process the file
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        df = process_sap_file_content(existing_file, encodings_to_try)
        
        if df is None:
            print("Could not process SAP file")
            return False
        
        # Transform for Power BI
        df = transform_data_for_powerbi(df)
        
        # Save in multiple formats
        save_powerbi_files(df, excel_path, csv_path, parquet_path)
        
        print("SAP file processed successfully!")
        return True
        
    except Exception as e:
        print(f"Error processing SAP file: {e}")
        return False


if __name__ == "__main__":
    print("Starting specialized SAP file processing...")
    print("=" * 60)
    
    success = process_sap_file()
    
    if success:
        print("\nPROCESSING COMPLETED SUCCESSFULLY")
        print("Files generated in: C:\\Data\\Nite")
    else:
        print("\nPROCESSING FAILED")
    
    print("=" * 60)
