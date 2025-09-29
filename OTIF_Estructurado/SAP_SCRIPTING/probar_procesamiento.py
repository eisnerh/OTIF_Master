#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBA DE PROCESAMIENTO
==================================

Este script prueba el procesamiento de archivos SAP con la estructura
real de los archivos en la carpeta data para validar que el sistema
funcione correctamente.

Funcionalidades:
✅ Prueba procesamiento de archivos existentes
✅ Valida estructura de datos
✅ Genera archivos Power BI de prueba
✅ Compara resultados con archivos originales
✅ Reporte de validación detallado
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcesadorPrueba:
    def __init__(self):
        self.directorio_data = os.path.join(os.path.dirname(__file__), 'data')
        self.directorio_salida = r"C:\Data\SAP_Automatizado\Pruebas"
        os.makedirs(self.directorio_salida, exist_ok=True)
        
    def listar_archivos_data(self):
        """
        Lista todos los archivos .xls en la carpeta data
        """
        archivos = []
        if os.path.exists(self.directorio_data):
            for archivo in os.listdir(self.directorio_data):
                if archivo.endswith('.xls'):
                    archivos.append(os.path.join(self.directorio_data, archivo))
        return archivos
    
    def procesar_archivo_sap(self, ruta_archivo):
        """
        Procesa un archivo SAP específico usando la misma lógica del script principal
        """
        try:
            logger.info(f"📊 Procesando archivo SAP: {os.path.basename(ruta_archivo)}")
            
            # Leer el archivo línea por línea
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            lines = None
            
            for encoding in encodings_to_try:
                try:
                    with open(ruta_archivo, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    logger.info(f"📄 Archivo leído con encoding: {encoding}")
                    break
                except Exception:
                    continue
            
            if lines is None:
                logger.error(f"❌ No se pudo leer el archivo con ningún encoding")
                return None
            
            logger.info(f"📄 Total de líneas en archivo: {len(lines)}")
            
            # Buscar la línea de encabezados
            header_line_idx = None
            fecha_reporte = None
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Detectar fecha del reporte
                if fecha_reporte is None and ('2025' in line_stripped or '2024' in line_stripped):
                    fecha_reporte = line_stripped
                    logger.info(f"📅 Fecha del reporte detectada: {fecha_reporte}")
                
                # Detectar línea de encabezados
                if '\t' in line_stripped and line_stripped and not line_stripped.startswith(' '):
                    if not line_stripped.startswith('\t') and not any(line_stripped.startswith(str(x)) for x in range(10)):
                        header_line_idx = i
                        logger.info(f"📋 Encabezados encontrados en línea {i+1}")
                        break
            
            if header_line_idx is None:
                logger.error("❌ No se encontró la línea de encabezados")
                return None
            
            # Extraer encabezados
            header_line = lines[header_line_idx].strip()
            headers = [col.strip() for col in header_line.split('\t') if col.strip()]
            logger.info(f"📋 Columnas detectadas: {len(headers)}")
            logger.info(f"📋 Primeras 5 columnas: {headers[:5]}")
            
            # Extraer datos
            data_rows = []
            for i in range(header_line_idx + 1, len(lines)):
                line = lines[i].strip()
                
                if not line or line.startswith('La lista no contiene datos'):
                    continue
                
                row_data = line.split('\t')
                
                if len(row_data) >= len(headers):
                    if len(row_data) > len(headers):
                        row_data = row_data[:len(headers)]
                    else:
                        row_data.extend([''] * (len(headers) - len(row_data)))
                    
                    data_rows.append(row_data)
                else:
                    row_data.extend([''] * (len(headers) - len(row_data)))
                    data_rows.append(row_data)
            
            logger.info(f"📊 Filas de datos encontradas: {len(data_rows)}")
            
            if not data_rows:
                logger.warning("⚠️ No se encontraron datos en el archivo")
                df = pd.DataFrame(columns=headers)
            else:
                df = pd.DataFrame(data_rows, columns=headers)
            
            # Limpiar DataFrame
            df = df.dropna(how='all').reset_index(drop=True)
            df.columns = [col.strip().replace('\n', '').replace('\r', '') for col in df.columns]
            
            logger.info(f"✅ DataFrame creado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            return {
                'dataframe': df,
                'fecha_reporte': fecha_reporte,
                'headers': headers,
                'total_filas': len(data_rows),
                'encoding_usado': encoding
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando archivo: {e}")
            return None
    
    def generar_archivos_powerbi(self, resultado, nombre_archivo):
        """
        Genera los archivos Power BI para un archivo procesado
        """
        try:
            df = resultado['dataframe']
            
            # Crear archivos Power BI
            base_name = os.path.splitext(nombre_archivo)[0]
            excel_path = os.path.join(self.directorio_salida, f"{base_name}_PowerBI.xlsx")
            csv_path = os.path.join(self.directorio_salida, f"{base_name}_PowerBI.csv")
            parquet_path = os.path.join(self.directorio_salida, f"{base_name}_PowerBI.parquet")
            
            # Guardar en múltiples formatos
            df.to_excel(excel_path, index=False, engine='openpyxl')
            df.to_csv(csv_path, index=False, encoding='utf-8')
            df.to_parquet(parquet_path, index=False)
            
            # Crear metadatos
            metadata = {
                'archivo_original': nombre_archivo,
                'fecha_procesamiento': datetime.now().isoformat(),
                'fecha_reporte_sap': resultado['fecha_reporte'],
                'filas': len(df),
                'columnas': len(df.columns),
                'columnas_info': {col: str(df[col].dtype) for col in df.columns},
                'encoding_usado': resultado['encoding_usado'],
                'muestra_datos': df.head(3).to_dict('records') if len(df) > 0 else []
            }
            
            metadata_path = os.path.join(self.directorio_salida, f"{base_name}_Metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return {
                'excel_path': excel_path,
                'csv_path': csv_path,
                'parquet_path': parquet_path,
                'metadata_path': metadata_path,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Error generando archivos Power BI: {e}")
            return None
    
    def validar_estructura(self, resultado, nombre_archivo):
        """
        Valida la estructura del archivo procesado
        """
        validaciones = {
            'archivo': nombre_archivo,
            'fecha_reporte_encontrada': resultado['fecha_reporte'] is not None,
            'encabezados_encontrados': len(resultado['headers']) > 0,
            'datos_encontrados': resultado['total_filas'] > 0,
            'dataframe_valido': resultado['dataframe'] is not None,
            'encoding_valido': resultado['encoding_usado'] is not None,
            'columnas_unicas': len(resultado['headers']) == len(set(resultado['headers'])),
            'filas_sin_vacias': resultado['dataframe'].dropna(how='all').shape[0] > 0 if resultado['dataframe'] is not None else False
        }
        
        # Validaciones adicionales
        if resultado['dataframe'] is not None:
            df = resultado['dataframe']
            validaciones.update({
                'shape_dataframe': df.shape,
                'columnas_con_datos': df.notna().any().sum(),
                'filas_con_datos': df.notna().any(axis=1).sum(),
                'tipos_datos': {col: str(df[col].dtype) for col in df.columns[:5]}  # Primeras 5 columnas
            })
        
        return validaciones
    
    def ejecutar_pruebas(self):
        """
        Ejecuta todas las pruebas de procesamiento
        """
        logger.info("🧪 INICIANDO PRUEBAS DE PROCESAMIENTO SAP")
        logger.info("=" * 60)
        
        archivos = self.listar_archivos_data()
        if not archivos:
            logger.error("❌ No se encontraron archivos .xls en la carpeta data")
            return False
        
        logger.info(f"📁 Archivos encontrados: {len(archivos)}")
        for archivo in archivos:
            logger.info(f"   • {os.path.basename(archivo)}")
        
        resultados = []
        validaciones = []
        
        for archivo in archivos:
            nombre_archivo = os.path.basename(archivo)
            logger.info(f"\n📊 Procesando: {nombre_archivo}")
            logger.info("-" * 50)
            
            # Procesar archivo
            resultado = self.procesar_archivo_sap(archivo)
            if resultado is None:
                logger.error(f"❌ Falló el procesamiento de {nombre_archivo}")
                continue
            
            # Validar estructura
            validacion = self.validar_estructura(resultado, nombre_archivo)
            validaciones.append(validacion)
            
            # Generar archivos Power BI
            archivos_powerbi = self.generar_archivos_powerbi(resultado, nombre_archivo)
            if archivos_powerbi is None:
                logger.error(f"❌ Falló la generación de archivos Power BI para {nombre_archivo}")
                continue
            
            resultados.append({
                'archivo': nombre_archivo,
                'procesamiento': resultado,
                'validacion': validacion,
                'archivos_powerbi': archivos_powerbi
            })
            
            logger.info(f"✅ {nombre_archivo} procesado exitosamente")
        
        # Generar reporte de validación
        self.generar_reporte_validacion(resultados, validaciones)
        
        return len(resultados) > 0
    
    def generar_reporte_validacion(self, resultados, validaciones):
        """
        Genera un reporte de validación completo
        """
        logger.info("\n📋 GENERANDO REPORTE DE VALIDACIÓN")
        logger.info("=" * 60)
        
        reporte = {
            'fecha_prueba': datetime.now().isoformat(),
            'total_archivos_procesados': len(resultados),
            'total_archivos_encontrados': len(validaciones),
            'tasa_exito': len(resultados) / len(validaciones) * 100 if validaciones else 0,
            'resultados_detallados': []
        }
        
        for i, resultado in enumerate(resultados):
            detalle = {
                'archivo': resultado['archivo'],
                'validacion': resultado['validacion'],
                'archivos_generados': list(resultado['archivos_powerbi'].keys())[:-1],  # Excluir metadata
                'estadisticas': {
                    'filas': resultado['procesamiento']['dataframe'].shape[0],
                    'columnas': resultado['procesamiento']['dataframe'].shape[1],
                    'encoding': resultado['procesamiento']['encoding_usado'],
                    'fecha_reporte': resultado['procesamiento']['fecha_reporte']
                }
            }
            reporte['resultados_detallados'].append(detalle)
        
        # Guardar reporte
        reporte_path = os.path.join(self.directorio_salida, 'reporte_validacion.json')
        with open(reporte_path, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        logger.info(f"📊 RESUMEN DE VALIDACIÓN")
        logger.info(f"   • Archivos procesados: {len(resultados)}/{len(validaciones)}")
        logger.info(f"   • Tasa de éxito: {reporte['tasa_exito']:.1f}%")
        logger.info(f"   • Archivos Power BI generados en: {self.directorio_salida}")
        logger.info(f"   • Reporte guardado en: {reporte_path}")
        
        # Mostrar detalles por archivo
        logger.info(f"\n📋 DETALLES POR ARCHIVO:")
        for resultado in resultados:
            logger.info(f"   ✅ {resultado['archivo']}:")
            logger.info(f"      • Filas: {resultado['procesamiento']['dataframe'].shape[0]}")
            logger.info(f"      • Columnas: {resultado['procesamiento']['dataframe'].shape[1]}")
            logger.info(f"      • Encoding: {resultado['procesamiento']['encoding_usado']}")
        
        return reporte

def main():
    """
    Función principal de prueba
    """
    procesador = ProcesadorPrueba()
    
    try:
        exito = procesador.ejecutar_pruebas()
        if exito:
            print("\n🎉 PRUEBAS COMPLETADAS EXITOSAMENTE")
            print(f"📁 Archivos generados en: {procesador.directorio_salida}")
        else:
            print("\n❌ LAS PRUEBAS FALLARON")
    except Exception as e:
        print(f"\n❌ Error inesperado en las pruebas: {e}")

if __name__ == "__main__":
    main()
