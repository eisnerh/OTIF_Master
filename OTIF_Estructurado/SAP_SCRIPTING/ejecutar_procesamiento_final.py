#!/usr/bin/env python3
"""
Script final que ejecuta solo el procesamiento de archivos para Power BI
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def ejecutar_procesamiento():
    """
    Ejecuta el script de procesamiento simple
    """
    print("PROCESAMIENTO DE ARCHIVOS PARA POWER BI")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "procesar_sap_simple.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Archivo procesado exitosamente para Power BI")
            print("📁 Archivos generados en: C:\\Data\\Nite")
            return True
        else:
            print(f"❌ Error procesando archivo: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando procesar_sap_simple.py: {e}")
        return False

def verificar_archivos_generados():
    """
    Verifica que los archivos Power BI se hayan generado correctamente
    """
    print("\n📋 Verificando archivos generados...")
    print("=" * 60)
    
    data_dir = r"C:\Data\Nite"
    archivos_esperados = [
        "REP_PLR_HOY_PowerBI.xlsx",
        "REP_PLR_HOY_PowerBI.csv", 
        "REP_PLR_HOY_PowerBI.parquet",
        "REP_PLR_HOY_Metadata.json"
    ]
    
    archivos_encontrados = []
    for archivo in archivos_esperados:
        ruta_archivo = os.path.join(data_dir, archivo)
        if os.path.exists(ruta_archivo):
            tamaño = os.path.getsize(ruta_archivo)
            print(f"✅ {archivo} - {tamaño:,} bytes")
            archivos_encontrados.append(archivo)
        else:
            print(f"❌ {archivo} - No encontrado")
    
    if len(archivos_encontrados) == len(archivos_esperados):
        print(f"\n🎉 Todos los archivos se generaron correctamente en: {data_dir}")
        return True
    else:
        print(f"\n⚠️  Solo se generaron {len(archivos_encontrados)} de {len(archivos_esperados)} archivos")
        return False

def main():
    """
    Función principal
    """
    print("🚀 INICIANDO PROCESAMIENTO FINAL")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Ejecutar procesamiento
    if not ejecutar_procesamiento():
        print("\n❌ FALLO: No se pudo procesar el archivo")
        return False
    
    # Verificar archivos generados
    if not verificar_archivos_generados():
        print("\n⚠️  ADVERTENCIA: No todos los archivos se generaron correctamente")
        return False
    
    # Resumen final
    print("\n" + "=" * 80)
    print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("📁 Archivos Power BI generados en: C:\\Data\\Nite")
    print("📊 Archivos disponibles:")
    print("   • REP_PLR_HOY_PowerBI.xlsx - Excel con formato")
    print("   • REP_PLR_HOY_PowerBI.csv - CSV para importar")
    print("   • REP_PLR_HOY_PowerBI.parquet - ⭐ RECOMENDADO para Power BI")
    print("   • REP_PLR_HOY_Metadata.json - Metadatos y documentación")
    print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Script ejecutado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Script falló")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
