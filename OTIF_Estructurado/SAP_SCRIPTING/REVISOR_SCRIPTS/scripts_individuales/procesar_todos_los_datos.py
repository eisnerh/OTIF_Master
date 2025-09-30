#!/usr/bin/env python3
"""
Script para procesar todos los archivos de la carpeta data y corregir sus DataFrames
"""

import os
import sys
from datetime import datetime
from procesar_datos_sap import ProcesadorDatosSAP

def procesar_archivos_data():
    """
    Procesa todos los archivos de la carpeta data
    """
    print("🚀 PROCESANDO TODOS LOS ARCHIVOS DE LA CARPETA DATA")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Definir rutas
    data_dir = "OTIF_Estructurado/SAP_SCRIPTING/data"
    output_dir = "C:\\data\\PowerBI"
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Lista de archivos a procesar
    archivos_data = [
        "REP_PLR.xls",
        "y_dev_45.xls", 
        "y_dev_74.xls",
        "y_dev_82.xls",
        "zhbo.xls",
        "zred.xls",
        "zsd_devo_alv.xls",
        "data_incidencias.xls"
    ]
    
    # Crear procesador
    procesador = ProcesadorDatosSAP(output_dir)
    
    results = {}
    total_archivos = len(archivos_data)
    
    print(f"📊 Procesando {total_archivos} archivos...")
    print("=" * 80)
    
    for i, archivo in enumerate(archivos_data, 1):
        print(f"\n📋 Procesando {i}/{total_archivos}: {archivo}")
        
        # Ruta completa del archivo
        file_path = os.path.join(data_dir, archivo)
        
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            results[archivo] = False
            continue
        
        try:
            # Procesar archivo
            output_name = os.path.splitext(archivo)[0] + "_PowerBI"
            success = procesador.procesar_archivo_sap(file_path, output_name)
            
            if success:
                print(f"✅ {archivo} procesado exitosamente")
                results[archivo] = True
            else:
                print(f"❌ Error procesando {archivo}")
                results[archivo] = False
                
        except Exception as e:
            print(f"❌ Error inesperado procesando {archivo}: {e}")
            results[archivo] = False
    
    # Resumen final
    successful = sum(1 for success in results.values() if success)
    
    print("\n" + "=" * 80)
    print("📋 RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Archivos procesados exitosamente: {successful}/{total_archivos}")
    print(f"❌ Archivos con errores: {total_archivos - successful}/{total_archivos}")
    print("\n📊 Detalle por archivo:")
    
    for archivo, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {archivo}")
    
    print(f"\n📂 Archivos Power BI generados en: {output_dir}")
    print("📊 Formatos disponibles:")
    print("   • .xlsx - Excel con formato")
    print("   • .csv - CSV para importar")
    print("   • .parquet - ⭐ RECOMENDADO para Power BI")
    print("   • _metadata.json - Metadatos y documentación")
    
    print(f"\n⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return successful == total_archivos

def main():
    """
    Función principal
    """
    try:
        success = procesar_archivos_data()
        
        if success:
            print("\n🎉 Todos los archivos procesados exitosamente")
            sys.exit(0)
        else:
            print("\n⚠️  Algunos archivos tuvieron errores")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Procesamiento interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
