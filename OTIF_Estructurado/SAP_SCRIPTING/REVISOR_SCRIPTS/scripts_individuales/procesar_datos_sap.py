#!/usr/bin/env python3
"""
Script para procesar y corregir la estructura de DataFrames de archivos SAP
Basado en la estructura encontrada en la carpeta data
"""

import pandas as pd
import os
import json
from datetime import datetime
import logging

class ProcesadorDatosSAP:
    """
    Clase para procesar y corregir DataFrames de archivos SAP
    """
    
    def __init__(self, output_path="C:\\data"):
        """
        Inicializa el procesador de datos
        
        Args:
            output_path (str): Ruta donde guardar los archivos procesados
        """
        self.output_path = output_path
        self._setup_logging()
        
    def _setup_logging(self):
        """
        Configura el sistema de logging
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('procesamiento_datos_sap.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def procesar_archivo_sap(self, file_path, output_name=None):
        """
        Procesa un archivo SAP y corrige la estructura del DataFrame
        
        Args:
            file_path (str): Ruta al archivo SAP
            output_name (str): Nombre base para los archivos de salida
        """
        try:
            self.logger.info(f"📊 Procesando archivo: {file_path}")
            
            # Leer archivo SAP con múltiples codificaciones
            df = self._leer_archivo_sap(file_path)
            
            if df is None:
                self.logger.error("❌ No se pudo leer el archivo SAP")
                return False
            
            # Transformar datos para Power BI
            df_clean = self._transformar_para_powerbi(df)
            
            # Generar nombre de salida si no se proporciona
            if output_name is None:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_name = f"{base_name}_PowerBI"
            
            # Guardar en múltiples formatos
            success = self._guardar_archivos(df_clean, output_name)
            
            if success:
                self.logger.info(f"✅ Archivo procesado exitosamente: {output_name}")
                return True
            else:
                self.logger.error("❌ Error guardando archivos")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error procesando archivo: {e}")
            return False
    
    def _leer_archivo_sap(self, file_path):
        """
        Lee un archivo SAP con múltiples codificaciones
        
        Args:
            file_path (str): Ruta al archivo
            
        Returns:
            pd.DataFrame: DataFrame con los datos procesados
        """
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16le']
        lines = None
        
        # Intentar leer con diferentes codificaciones
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                self.logger.info(f"✅ Archivo leído con codificación: {encoding}")
                break
            except:
                continue
        
        # Si no funciona, intentar como binario
        if lines is None:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                try:
                    content_str = content.decode('utf-16')
                    lines = content_str.splitlines()
                    self.logger.info("✅ Archivo leído como UTF-16 binario")
                except:
                    content_str = content.decode('utf-16le')
                    lines = content_str.splitlines()
                    self.logger.info("✅ Archivo leído como UTF-16LE binario")
            except Exception as e:
                self.logger.error(f"❌ Error leyendo archivo: {e}")
                return None
        
        if lines is None:
            self.logger.error("❌ No se pudo leer el archivo con ninguna codificación")
            return None
        
        # Procesar líneas para encontrar encabezados y datos
        return self._procesar_lineas_sap(lines)
    
    def _procesar_lineas_sap(self, lines):
        """
        Procesa las líneas del archivo SAP para extraer encabezados y datos
        
        Args:
            lines (list): Lista de líneas del archivo
            
        Returns:
            pd.DataFrame: DataFrame con los datos procesados
        """
        try:
            self.logger.info(f"📋 Procesando {len(lines)} líneas")
            
            # Buscar línea de encabezados (generalmente en línea 7, índice 6)
            header_line_idx = 6  # Línea 7 (0-indexed)
            
            if header_line_idx >= len(lines):
                self.logger.error("❌ Archivo muy corto - no se encontró encabezado")
                return None
            
            # Extraer encabezados
            header_line = lines[header_line_idx].strip()
            headers = [col.strip() for col in header_line.split('\t')]
            
            # Limpiar encabezados
            clean_headers = []
            for i, header in enumerate(headers):
                clean_header = header.replace('\x00', '').strip()
                if clean_header:
                    clean_headers.append(clean_header)
                else:
                    clean_headers.append(f"Columna_{i+1}")
            
            headers = clean_headers
            self.logger.info(f"📊 Encontradas {len(headers)} columnas")
            
            # Buscar inicio de datos
            data_start = header_line_idx + 1
            while data_start < len(lines) and not lines[data_start].strip():
                data_start += 1
            
            # Extraer datos
            data_rows = []
            current_date = datetime.now().strftime('%d.%m.%Y')
            
            for i in range(data_start, len(lines)):
                line = lines[i].strip()
                
                # Saltar líneas vacías o encabezados de fecha
                if not line or line.startswith(current_date) or line.startswith('La lista no contiene datos'):
                    continue
                
                # Procesar línea de datos
                row_data = line.split('\t')
                
                # Asegurar que tenga el mismo número de columnas que los encabezados
                if len(row_data) >= len(headers):
                    clean_row = []
                    for j, cell in enumerate(row_data[:len(headers)]):
                        clean_cell = cell.replace('\x00', '').strip()
                        clean_row.append(clean_cell)
                    data_rows.append(clean_row)
                elif len(row_data) > 0:
                    # Completar con valores vacíos si faltan columnas
                    clean_row = []
                    for j in range(len(headers)):
                        if j < len(row_data):
                            clean_cell = row_data[j].replace('\x00', '').strip()
                            clean_row.append(clean_cell)
                        else:
                            clean_row.append('')
                    data_rows.append(clean_row)
            
            self.logger.info(f"📊 Encontradas {len(data_rows)} filas de datos")
            
            if not data_rows:
                self.logger.warning("⚠️ No se encontraron datos en el archivo")
                return pd.DataFrame(columns=headers)
            
            # Crear DataFrame
            df = pd.DataFrame(data_rows, columns=headers)
            
            # Limpiar DataFrame
            df = df.dropna(how='all').reset_index(drop=True)
            df.columns = [col.strip().replace('\n', '').replace('\r', '') for col in df.columns]
            
            self.logger.info(f"✅ DataFrame creado: {df.shape[0]} filas, {df.shape[1]} columnas")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando líneas SAP: {e}")
            return None
    
    def _transformar_para_powerbi(self, df):
        """
        Transforma y limpia los datos para compatibilidad con Power BI
        
        Args:
            df (pd.DataFrame): DataFrame original
            
        Returns:
            pd.DataFrame: DataFrame transformado
        """
        try:
            self.logger.info("🔄 Transformando datos para Power BI...")
            
            df_clean = df.copy()
            
            # Remover filas completamente vacías
            df_clean = df_clean.dropna(how='all')
            df_clean = df_clean[~df_clean.astype(str).eq('').all(axis=1)]
            
            # Limpiar nombres de columnas
            df_clean.columns = df_clean.columns.str.strip()
            df_clean.columns = df_clean.columns.str.replace(r'\s+', ' ', regex=True)
            
            # Convertir columnas de fecha
            date_columns = ['Fe.Entrega', 'Fecha Guía', 'Creado el', 'Fecha', 'FECHA']
            for col in date_columns:
                if col in df_clean.columns:
                    try:
                        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                    except:
                        self.logger.warning(f"⚠️ No se pudo convertir {col} a datetime")
            
            # Convertir columnas de tiempo
            time_columns = ['Hora Guía', 'Hora', 'HORA']
            for col in time_columns:
                if col in df_clean.columns:
                    try:
                        df_clean[col] = pd.to_datetime(df_clean[col], format='%H:%M:%S', errors='coerce').dt.time
                    except:
                        self.logger.warning(f"⚠️ No se pudo convertir {col} a time")
            
            # Convertir columnas numéricas
            numeric_columns = ['Cajas R.S.', 'Cajas Físicas', 'Cajas Equiv.', 'Ruta', 'Entrega', 'Cliente', 'CANTIDAD', 'VALOR']
            for col in numeric_columns:
                if col in df_clean.columns:
                    try:
                        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                    except:
                        self.logger.warning(f"⚠️ No se pudo convertir {col} a numérico")
            
            # Limpiar columnas de texto
            text_columns = ['Centro', 'Nombre del Cliente', 'Estatus', 'Ruta Dist.', 'Camión', 
                           'Guia Entrega', 'Rol Alisto', 'Reprogramado', 'Ped. Clte', 'Ped. SAP',
                           'Tipo Ped.', 'Desc. Tipo', 'Origen', 'Tipo Ruta', 'Fuerza Ventas',
                           'Region', 'Zona Vtas', 'Desc Zona Vtas', 'Zona Superv', 'Desc Zona Superv',
                           'Agente Vtas', 'Nombre', 'CLIENTE', 'ESTADO', 'ZONA']
            
            for col in text_columns:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].astype(str).str.strip()
                    df_clean[col] = df_clean[col].replace('nan', '')
            
            # Agregar columnas calculadas útiles para Power BI
            if 'Fe.Entrega' in df_clean.columns:
                df_clean['Año'] = df_clean['Fe.Entrega'].dt.year
                df_clean['Mes'] = df_clean['Fe.Entrega'].dt.month
                df_clean['Día'] = df_clean['Fe.Entrega'].dt.day
                df_clean['Día_Semana'] = df_clean['Fe.Entrega'].dt.day_name()
                df_clean['Semana'] = df_clean['Fe.Entrega'].dt.isocalendar().week
            
            # Agregar indicadores de rendimiento
            if 'Cajas R.S.' in df_clean.columns and 'Cajas Físicas' in df_clean.columns:
                df_clean['Diferencia_Cajas'] = df_clean['Cajas Físicas'] - df_clean['Cajas R.S.']
                df_clean['Porcentaje_Cumplimiento'] = (df_clean['Cajas Físicas'] / df_clean['Cajas R.S.'] * 100).round(2)
            
            # Agregar categorías de estado
            if 'Estatus' in df_clean.columns:
                df_clean['Estatus_Categoria'] = df_clean['Estatus'].apply(self._categorizar_estado)
            
            # Agregar categorías de tipo de ruta
            if 'Tipo Ruta' in df_clean.columns:
                df_clean['Tipo_Ruta_Categoria'] = df_clean['Tipo Ruta'].apply(self._categorizar_tipo_ruta)
            
            self.logger.info(f"✅ Transformación completada. Forma final: {df_clean.shape}")
            return df_clean
            
        except Exception as e:
            self.logger.error(f"❌ Error transformando datos: {e}")
            return df
    
    def _categorizar_estado(self, estado):
        """
        Categoriza el estado para mejor filtrado en Power BI
        """
        if pd.isna(estado) or estado == '':
            return 'Sin Estado'
        
        estado_str = str(estado).upper()
        
        if 'ENTREGADO' in estado_str or 'COMPLETADO' in estado_str:
            return 'Entregado'
        elif 'PENDIENTE' in estado_str or 'EN PROCESO' in estado_str:
            return 'Pendiente'
        elif 'CANCELADO' in estado_str or 'ANULADO' in estado_str:
            return 'Cancelado'
        elif 'REPROGRAMADO' in estado_str:
            return 'Reprogramado'
        else:
            return 'Otro'
    
    def _categorizar_tipo_ruta(self, tipo_ruta):
        """
        Categoriza el tipo de ruta para mejor análisis
        """
        if pd.isna(tipo_ruta) or tipo_ruta == '':
            return 'Sin Tipo'
        
        tipo_str = str(tipo_ruta).upper()
        
        if 'URBANA' in tipo_str:
            return 'Urbana'
        elif 'RURAL' in tipo_str:
            return 'Rural'
        elif 'MIXTA' in tipo_str:
            return 'Mixta'
        else:
            return 'Otro'
    
    def _guardar_archivos(self, df, output_name):
        """
        Guarda el DataFrame en múltiples formatos para Power BI
        
        Args:
            df (pd.DataFrame): DataFrame a guardar
            output_name (str): Nombre base para los archivos
        """
        try:
            # Crear directorio de salida si no existe
            os.makedirs(self.output_path, exist_ok=True)
            
            # Definir rutas de archivos
            excel_path = os.path.join(self.output_path, f"{output_name}.xlsx")
            csv_path = os.path.join(self.output_path, f"{output_name}.csv")
            parquet_path = os.path.join(self.output_path, f"{output_name}.parquet")
            json_path = os.path.join(self.output_path, f"{output_name}_metadata.json")
            
            # Guardar en Excel
            df.to_excel(excel_path, index=False, engine='openpyxl')
            self.logger.info(f"📊 Excel guardado: {excel_path}")
            
            # Guardar en CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            self.logger.info(f"📊 CSV guardado: {csv_path}")
            
            # Guardar en Parquet (recomendado para Power BI)
            df.to_parquet(parquet_path, index=False)
            self.logger.info(f"📊 Parquet guardado: {parquet_path}")
            
            # Crear metadatos
            self._crear_metadatos(df, json_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error guardando archivos: {e}")
            return False
    
    def _crear_metadatos(self, df, json_path):
        """
        Crea archivo de metadatos para Power BI
        
        Args:
            df (pd.DataFrame): DataFrame
            json_path (str): Ruta del archivo JSON
        """
        try:
            metadata = {
                "informacion_general": {
                    "fecha_procesamiento": datetime.now().isoformat(),
                    "total_filas": len(df),
                    "total_columnas": len(df.columns),
                    "archivo_origen": "SAP"
                },
                "columnas": {
                    "total": len(df.columns),
                    "nombres": list(df.columns),
                    "tipos": df.dtypes.astype(str).to_dict()
                },
                "estadisticas": {
                    "filas_vacias": df.isnull().sum().sum(),
                    "columnas_vacias": df.isnull().all().sum()
                },
                "recomendaciones": {
                    "formato_recomendado": "parquet",
                    "archivo_principal": f"{os.path.splitext(json_path)[0]}.parquet"
                }
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Metadatos guardados: {json_path}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error creando metadatos: {e}")

def main():
    """
    Función principal para procesar archivos SAP
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python procesar_datos_sap.py <archivo_sap> [nombre_salida] [ruta_salida]")
        print("Ejemplo: python procesar_datos_sap.py REP_PLR.xls REP_PLR_PowerBI C:\\data")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else "C:\\data"
    
    # Crear procesador
    procesador = ProcesadorDatosSAP(output_path)
    
    # Procesar archivo
    success = procesador.procesar_archivo_sap(file_path, output_name)
    
    if success:
        print("✅ Archivo procesado exitosamente")
        sys.exit(0)
    else:
        print("❌ Error procesando archivo")
        sys.exit(1)

if __name__ == "__main__":
    main()
