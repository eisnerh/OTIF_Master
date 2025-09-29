#!/usr/bin/env python3
"""
🎯 DEMO DE PROCESAMIENTO SAP
==========================

Este script demuestra cómo usar el sistema de automatización SAP
procesando los archivos existentes en la carpeta data.

Funcionalidades:
✅ Demo completo del procesamiento
✅ Muestra resultados en tiempo real
✅ Genera archivos de ejemplo
✅ Explica cada paso del proceso
"""

import os
import sys
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('demo_procesamiento.log')
    ]
)
logger = logging.getLogger(__name__)

def mostrar_banner():
    """
    Muestra el banner del demo
    """
    print("=" * 80)
    print("🎯 DEMO DE AUTOMATIZACIÓN SAP - PROCESAMIENTO DE REPORTES")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Directorio: {os.path.dirname(os.path.abspath(__file__))}")
    print("=" * 80)

def verificar_archivos_data():
    """
    Verifica que existan archivos en la carpeta data
    """
    print("\n🔍 PASO 1: Verificando archivos de datos...")
    
    directorio_data = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(directorio_data):
        print("❌ Carpeta 'data' no encontrada")
        return False
    
    archivos = [f for f in os.listdir(directorio_data) if f.endswith('.xls')]
    
    if not archivos:
        print("❌ No se encontraron archivos .xls en la carpeta data")
        return False
    
    print(f"✅ Encontrados {len(archivos)} archivos:")
    for i, archivo in enumerate(archivos, 1):
        print(f"   {i}. {archivo}")
    
    return True

def ejecutar_procesamiento():
    """
    Ejecuta el procesamiento de prueba
    """
    print("\n🚀 PASO 2: Ejecutando procesamiento de prueba...")
    
    try:
        # Importar y ejecutar el procesador de prueba
        from probar_procesamiento import ProcesadorPrueba
        
        procesador = ProcesadorPrueba()
        exito = procesador.ejecutar_pruebas()
        
        if exito:
            print("✅ Procesamiento completado exitosamente")
            return True
        else:
            print("❌ El procesamiento falló")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando módulo: {e}")
        return False
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {e}")
        return False

def mostrar_resultados():
    """
    Muestra los resultados del procesamiento
    """
    print("\n📊 PASO 3: Mostrando resultados...")
    
    directorio_salida = r"C:\Data\SAP_Automatizado\Pruebas"
    
    if not os.path.exists(directorio_salida):
        print("❌ Directorio de salida no encontrado")
        return
    
    archivos_generados = []
    for archivo in os.listdir(directorio_salida):
        if archivo.endswith(('.xlsx', '.csv', '.parquet', '.json')):
            archivos_generados.append(archivo)
    
    print(f"✅ Archivos generados ({len(archivos_generados)}):")
    
    # Agrupar por tipo
    excel_files = [f for f in archivos_generados if f.endswith('.xlsx')]
    csv_files = [f for f in archivos_generados if f.endswith('.csv')]
    parquet_files = [f for f in archivos_generados if f.endswith('.parquet')]
    json_files = [f for f in archivos_generados if f.endswith('.json')]
    
    if excel_files:
        print(f"   📊 Excel ({len(excel_files)}):")
        for archivo in excel_files[:3]:  # Mostrar solo los primeros 3
            print(f"      • {archivo}")
        if len(excel_files) > 3:
            print(f"      • ... y {len(excel_files) - 3} más")
    
    if csv_files:
        print(f"   📄 CSV ({len(csv_files)}):")
        for archivo in csv_files[:3]:
            print(f"      • {archivo}")
        if len(csv_files) > 3:
            print(f"      • ... y {len(csv_files) - 3} más")
    
    if parquet_files:
        print(f"   🚀 Parquet ({len(parquet_files)}):")
        for archivo in parquet_files[:3]:
            print(f"      • {archivo}")
        if len(parquet_files) > 3:
            print(f"      • ... y {len(parquet_files) - 3} más")
    
    if json_files:
        print(f"   📋 Metadata ({len(json_files)}):")
        for archivo in json_files:
            print(f"      • {archivo}")

def mostrar_instrucciones_uso():
    """
    Muestra instrucciones de uso del sistema
    """
    print("\n📚 PASO 4: Instrucciones de uso...")
    print("\n🎯 CÓMO USAR EL SISTEMA COMPLETO:")
    print("=" * 50)
    
    print("\n1️⃣ INSTALACIÓN:")
    print("   python instalar_automatizacion.py")
    
    print("\n2️⃣ EJECUCIÓN DIARIA AUTOMÁTICA:")
    print("   • Se ejecuta automáticamente a las 08:00")
    print("   • Procesa todos los reportes SAP")
    print("   • Genera archivos Power BI")
    
    print("\n3️⃣ EJECUCIÓN MANUAL:")
    print("   python ejecutar_diario.py")
    
    print("\n4️⃣ PRUEBAS:")
    print("   python probar_procesamiento.py")
    
    print("\n5️⃣ CONFIGURACIÓN:")
    print("   • Editar: configuracion_reportes.json")
    print("   • Cambiar credenciales SAP")
    print("   • Activar/desactivar reportes")
    
    print("\n📁 ARCHIVOS GENERADOS:")
    print("   C:\\Data\\SAP_Automatizado\\")
    print("   ├── Reportes originales (.xls)")
    print("   ├── Archivos Power BI (.xlsx, .csv, .parquet)")
    print("   ├── Metadatos (.json)")
    print("   └── Logs de ejecución")

def main():
    """
    Función principal del demo
    """
    mostrar_banner()
    
    print("\n🎯 Este demo procesará los archivos existentes en la carpeta 'data'")
    print("   para demostrar cómo funciona el sistema de automatización SAP.")
    
    input("\n⏸️ Presiona Enter para continuar...")
    
    # Paso 1: Verificar archivos
    if not verificar_archivos_data():
        print("\n❌ Demo no puede continuar - no hay archivos de datos")
        return
    
    input("\n⏸️ Presiona Enter para iniciar el procesamiento...")
    
    # Paso 2: Ejecutar procesamiento
    if not ejecutar_procesamiento():
        print("\n❌ Demo falló durante el procesamiento")
        return
    
    # Paso 3: Mostrar resultados
    mostrar_resultados()
    
    # Paso 4: Mostrar instrucciones
    mostrar_instrucciones_uso()
    
    print("\n" + "=" * 80)
    print("🎉 DEMO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print("📁 Archivos generados en: C:\\Data\\SAP_Automatizado\\Pruebas\\")
    print("📋 Log detallado: demo_procesamiento.log")
    print("🚀 ¡El sistema está listo para usar!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado en el demo: {e}")
