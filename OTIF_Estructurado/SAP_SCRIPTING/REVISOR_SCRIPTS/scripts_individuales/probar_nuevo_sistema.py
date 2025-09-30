#!/usr/bin/env python3
"""
Script de prueba para verificar que el nuevo sistema funciona correctamente
Basado en la lógica del entorno Nite
"""

import sys
import os
import time
from datetime import datetime
from zsd_incidencias import ZSDIncidenciasScript

def probar_conexion_sap():
    """
    Prueba la conexión a SAP usando el nuevo método
    """
    print("🔐 Probando conexión a SAP...")
    print("=" * 60)
    
    try:
        script = ZSDIncidenciasScript("C:\\data")
        
        if script.connect_sap():
            print("✅ Conexión SAP establecida correctamente")
            script.cleanup()
            return True
        else:
            print("❌ No se pudo conectar a SAP")
            return False
            
    except Exception as e:
        print(f"❌ Error en conexión SAP: {e}")
        return False

def probar_script_incidencias():
    """
    Prueba el script de incidencias con la nueva lógica
    """
    print("\n📊 Probando script ZSD_INCIDENCIAS...")
    print("=" * 60)
    
    try:
        script = ZSDIncidenciasScript("C:\\data")
        success = script.execute()
        
        if success:
            print("✅ Script ZSD_INCIDENCIAS ejecutado exitosamente")
            return True
        else:
            print("❌ Script ZSD_INCIDENCIAS falló")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")
        return False

def verificar_archivos():
    """
    Verifica que los archivos se hayan generado
    """
    print("\n🔍 Verificando archivos generados...")
    print("=" * 60)
    
    archivos_esperados = [
        "data_incidencias.xls"
    ]
    
    directorio_base = "C:\\data"
    archivos_encontrados = 0
    
    for archivo in archivos_esperados:
        ruta_archivo = os.path.join(directorio_base, archivo)
        if os.path.exists(ruta_archivo):
            tamaño = os.path.getsize(ruta_archivo)
            print(f"✅ {archivo} - {tamaño:,} bytes")
            archivos_encontrados += 1
        else:
            print(f"❌ {archivo} - No encontrado")
    
    print(f"\n📊 Archivos encontrados: {archivos_encontrados}/{len(archivos_esperados)}")
    return archivos_encontrados == len(archivos_esperados)

def main():
    """
    Función principal de prueba
    """
    print("🧪 INICIANDO PRUEBAS DEL NUEVO SISTEMA")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    pruebas = [
        ("Conexión SAP", probar_conexion_sap),
        ("Script Incidencias", probar_script_incidencias),
        ("Verificación Archivos", verificar_archivos)
    ]
    
    exitosos = 0
    fallidos = 0
    
    for nombre, funcion in pruebas:
        print(f"\n🔄 Ejecutando prueba: {nombre}")
        if funcion():
            exitosos += 1
            print(f"✅ {nombre}: EXITOSO")
        else:
            fallidos += 1
            print(f"❌ {nombre}: FALLÓ")
        
        # Esperar entre pruebas
        time.sleep(2)
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 80)
    print(f"✅ Pruebas exitosas: {exitosos}")
    print(f"❌ Pruebas fallidas: {fallidos}")
    print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if fallidos == 0:
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("✅ El nuevo sistema está funcionando correctamente")
        return True
    else:
        print(f"⚠️  {fallidos} PRUEBAS FALLARON")
        print("❌ El nuevo sistema necesita ajustes")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Sistema verificado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Sistema necesita correcciones")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
