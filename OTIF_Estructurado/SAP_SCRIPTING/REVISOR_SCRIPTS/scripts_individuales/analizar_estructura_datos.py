#!/usr/bin/env python3
"""
Script para analizar la estructura de los archivos en la carpeta data
y determinar qué correcciones necesitan los DataFrames
"""

import os
import pandas as pd
from datetime import datetime
import json

def analizar_archivo_sap(file_path):
    """
    Analiza un archivo SAP y determina su estructura
    
    Args:
        file_path (str): Ruta al archivo
        
    Returns:
        dict: Información sobre la estructura del archivo
    """
    try:
        print(f"🔍 Analizando: {os.path.basename(file_path)}")
        
        # Intentar leer con diferentes métodos
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16', 'utf-16le']
        lines = None
        encoding_used = None
        
        # Método 1: Leer como texto
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                encoding_used = encoding
                print(f"  ✅ Leído con codificación: {encoding}")
                break
            except:
                continue
        
        # Método 2: Leer como binario
        if lines is None:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                try:
                    content_str = content.decode('utf-16')
                    lines = content_str.splitlines()
                    encoding_used = 'utf-16-binary'
                    print(f"  ✅ Leído como UTF-16 binario")
                except:
                    content_str = content.decode('utf-16le')
                    lines = content_str.splitlines()
                    encoding_used = 'utf-16le-binary'
                    print(f"  ✅ Leído como UTF-16LE binario")
            except Exception as e:
                print(f"  ❌ Error leyendo archivo: {e}")
                return None
        
        if lines is None:
            print(f"  ❌ No se pudo leer el archivo")
            return None
        
        # Analizar estructura
        info = {
            'archivo': os.path.basename(file_path),
            'tamaño_bytes': os.path.getsize(file_path),
            'total_lineas': len(lines),
            'codificacion': encoding_used,
            'estructura': {}
        }
        
        # Buscar patrones en las líneas
        info['estructura']['lineas_vacias'] = sum(1 for line in lines if not line.strip())
        info['estructura']['lineas_con_datos'] = sum(1 for line in lines if line.strip() and not line.startswith('La lista no contiene datos'))
        
        # Buscar encabezados (generalmente en línea 7)
        if len(lines) > 6:
            header_line = lines[6].strip()
            if header_line:
                headers = [col.strip() for col in header_line.split('\t')]
                info['estructura']['encabezados'] = {
                    'linea': 7,
                    'total_columnas': len(headers),
                    'nombres': headers[:10]  # Primeros 10 para no saturar
                }
        
        # Buscar datos
        data_start = 7
        data_rows = 0
        for i in range(data_start, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('La lista no contiene datos'):
                data_rows += 1
        
        info['estructura']['filas_datos'] = data_rows
        
        # Detectar problemas comunes
        problemas = []
        
        if info['estructura']['filas_datos'] == 0:
            problemas.append("Sin datos")
        
        if info['estructura']['lineas_vacias'] > len(lines) * 0.5:
            problemas.append("Muchas líneas vacías")
        
        if info['estructura']['total_columnas'] == 0:
            problemas.append("Sin encabezados")
        
        info['problemas_detectados'] = problemas
        
        print(f"  📊 Líneas: {info['total_lineas']}, Datos: {info['estructura']['filas_datos']}, Columnas: {info['estructura']['total_columnas']}")
        
        if problemas:
            print(f"  ⚠️  Problemas: {', '.join(problemas)}")
        
        return info
        
    except Exception as e:
        print(f"  ❌ Error analizando archivo: {e}")
        return None

def analizar_todos_los_archivos():
    """
    Analiza todos los archivos en la carpeta data
    """
    print("🔍 ANÁLISIS DE ESTRUCTURA DE DATOS")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Definir carpeta de datos
    data_dir = "OTIF_Estructurado/SAP_SCRIPTING/data"
    
    if not os.path.exists(data_dir):
        print(f"❌ Carpeta no encontrada: {data_dir}")
        return False
    
    # Listar archivos
    archivos = [f for f in os.listdir(data_dir) if f.endswith('.xls')]
    
    if not archivos:
        print("❌ No se encontraron archivos .xls en la carpeta")
        return False
    
    print(f"📁 Encontrados {len(archivos)} archivos en {data_dir}")
    print("=" * 80)
    
    # Analizar cada archivo
    resultados = []
    
    for i, archivo in enumerate(archivos, 1):
        print(f"\n📋 Analizando {i}/{len(archivos)}: {archivo}")
        file_path = os.path.join(data_dir, archivo)
        
        info = analizar_archivo_sap(file_path)
        if info:
            resultados.append(info)
    
    # Generar reporte
    generar_reporte(resultados)
    
    return True

def generar_reporte(resultados):
    """
    Genera un reporte detallado del análisis
    
    Args:
        resultados (list): Lista de resultados del análisis
    """
    print("\n" + "=" * 80)
    print("📋 REPORTE DE ANÁLISIS")
    print("=" * 80)
    
    # Estadísticas generales
    total_archivos = len(resultados)
    archivos_con_datos = sum(1 for r in resultados if r['estructura']['filas_datos'] > 0)
    archivos_con_problemas = sum(1 for r in resultados if r['problemas_detectados'])
    
    print(f"📊 Estadísticas Generales:")
    print(f"   • Total archivos analizados: {total_archivos}")
    print(f"   • Archivos con datos: {archivos_con_datos}")
    print(f"   • Archivos con problemas: {archivos_con_problemas}")
    
    # Detalle por archivo
    print(f"\n📋 Detalle por Archivo:")
    for resultado in resultados:
        archivo = resultado['archivo']
        datos = resultado['estructura']['filas_datos']
        columnas = resultado['estructura']['total_columnas']
        problemas = resultado['problemas_detectados']
        
        status = "✅" if not problemas else "⚠️"
        print(f"  {status} {archivo}")
        print(f"      📊 Datos: {datos} filas, {columnas} columnas")
        if problemas:
            print(f"      ⚠️  Problemas: {', '.join(problemas)}")
    
    # Recomendaciones
    print(f"\n💡 Recomendaciones:")
    
    if archivos_con_problemas > 0:
        print("   • Algunos archivos necesitan corrección de estructura")
        print("   • Usar el script procesar_datos_sap.py para corregir")
    
    if archivos_con_datos < total_archivos:
        print("   • Algunos archivos no contienen datos")
        print("   • Verificar que los reportes SAP se ejecuten correctamente")
    
    print("   • Usar formato Parquet para mejor rendimiento en Power BI")
    print("   • Revisar metadatos generados para documentación")
    
    # Guardar reporte en JSON
    reporte_path = "analisis_estructura_datos.json"
    try:
        with open(reporte_path, 'w', encoding='utf-8') as f:
            json.dump({
                'fecha_analisis': datetime.now().isoformat(),
                'total_archivos': total_archivos,
                'archivos_con_datos': archivos_con_datos,
                'archivos_con_problemas': archivos_con_problemas,
                'resultados': resultados
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte detallado guardado en: {reporte_path}")
        
    except Exception as e:
        print(f"\n⚠️  Error guardando reporte: {e}")
    
    print(f"\n⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def main():
    """
    Función principal
    """
    try:
        success = analizar_todos_los_archivos()
        
        if success:
            print("\n✅ Análisis completado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Error en el análisis")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Análisis interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
