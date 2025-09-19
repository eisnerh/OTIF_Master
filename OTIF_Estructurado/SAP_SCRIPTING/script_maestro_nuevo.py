#!/usr/bin/env python3
"""
Script maestro que ejecuta todo el flujo:
1. Loguearse en SAP
2. Ejecutar nuevo_rep_plr.py (descargar reporte)
3. Ejecutar procesar_sap_simple.py (procesar para Power BI)
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def loguearse_sap():
    """
    Ejecuta el script de login en SAP
    """
    print("🔐 Paso 1: Iniciando sesión en SAP...")
    print("=" * 60)
    
    try:
        # Ejecutar el script de login
        result = subprocess.run([sys.executable, "loguearse.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Sesión SAP iniciada correctamente")
            return True
        else:
            print(f"❌ Error al iniciar sesión en SAP: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error al iniciar sesión en SAP: {e}")
        return False

def ejecutar_nuevo_rep_plr():
    """
    Ejecuta el script nuevo_rep_plr.py para descargar el reporte
    """
    print("\n📊 Paso 2: Descargando reporte desde SAP...")
    print("=" * 60)
    
    try:
        # Verificar si es después de las 2 PM
        current_hour = datetime.now().hour
        if current_hour < 14:
            print("⚠️  Advertencia: Son menos de las 2 PM. El script principal no se ejecutará automáticamente.")
            print("🔄 Ejecutando función de procesamiento de archivo existente...")
            
            # Ejecutar el script de procesamiento simple
            result = subprocess.run([sys.executable, "procesar_sap_simple.py"], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                print("✅ Archivo existente procesado exitosamente")
                return True
            else:
                print(f"❌ Error procesando archivo existente: {result.stderr}")
                return False
        else:
            # Ejecutar el script principal
            result = subprocess.run([sys.executable, "nuevo_rep_plr.py"], 
                                  capture_output=True, text=True, cwd=os.path.dirname(__file__))
            
            if result.returncode == 0:
                print("✅ Reporte descargado exitosamente desde SAP")
                return True
            else:
                print(f"❌ Error al descargar reporte: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Error ejecutando nuevo_rep_plr.py: {e}")
        return False

def ejecutar_procesar_sap_simple():
    """
    Ejecuta el script procesar_sap_simple.py para procesar el archivo
    """
    print("\n🔄 Paso 3: Procesando archivo para Power BI...")
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
    Función principal que ejecuta todo el flujo
    """
    print("🚀 INICIANDO SCRIPT MAESTRO - PROCESAMIENTO COMPLETO")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Paso 1: Loguearse en SAP
    if not loguearse_sap():
        print("\n❌ FALLO: No se pudo iniciar sesión en SAP")
        return False
    
    # Esperar un momento para que la sesión se estabilice
    print("\n⏳ Esperando 3 segundos para estabilizar la sesión...")
    time.sleep(3)
    
    # Paso 2: Ejecutar nuevo_rep_plr.py
    if not ejecutar_nuevo_rep_plr():
        print("\n❌ FALLO: No se pudo descargar el reporte")
        return False
    
    # Esperar un momento entre procesos
    print("\n⏳ Esperando 2 segundos entre procesos...")
    time.sleep(2)
    
    # Paso 3: Ejecutar procesar_sap_simple.py
    if not ejecutar_procesar_sap_simple():
        print("\n❌ FALLO: No se pudo procesar el archivo")
        return False
    
    # Paso 4: Verificar archivos generados
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
            print("\n✅ Script maestro ejecutado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Script maestro falló")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
