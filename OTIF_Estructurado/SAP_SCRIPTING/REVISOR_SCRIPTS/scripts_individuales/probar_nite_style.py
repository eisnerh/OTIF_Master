#!/usr/bin/env python3
"""
Script de prueba para verificar que el nuevo sistema estilo NITE funciona correctamente
"""

import sys
import os
import time
from datetime import datetime

def probar_script_incidencias_nite():
    """
    Prueba el script de incidencias en estilo NITE
    """
    print("🧪 Probando script ZSD_INCIDENCIAS - Estilo NITE...")
    print("=" * 60)
    
    try:
        # Ejecutar el script
        result = os.system(f'python zsd_incidencias_nite_style.py')
        
        if result == 0:
            print("✅ Script ZSD_INCIDENCIAS ejecutado exitosamente")
            
            # Verificar archivo generado
            archivo_esperado = "C:\\data\\data_incidencias.xls"
            if os.path.exists(archivo_esperado):
                tamaño = os.path.getsize(archivo_esperado)
                print(f"✅ Archivo generado: data_incidencias.xls - {tamaño:,} bytes")
                return True
            else:
                print("❌ Archivo no se generó correctamente")
                return False
        else:
            print("❌ Script ZSD_INCIDENCIAS falló")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")
        return False

def probar_script_maestro_nite():
    """
    Prueba el script maestro en estilo NITE
    """
    print("\n🧪 Probando script maestro - Estilo NITE...")
    print("=" * 60)
    
    try:
        # Ejecutar el script maestro
        result = os.system(f'python script_maestro_nite_exacto.py')
        
        if result == 0:
            print("✅ Script maestro ejecutado exitosamente")
            return True
        else:
            print("❌ Script maestro falló")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando script maestro: {e}")
        return False

def verificar_archivos():
    """
    Verifica que los archivos se hayan generado
    """
    print("\n🔍 Verificando archivos generados...")
    print("=" * 60)
    
    archivos_esperados = [
        "data_incidencias.xls",
        "data_mb51.xls"
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
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA ESTILO NITE")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    pruebas = [
        ("Script Incidencias NITE", probar_script_incidencias_nite),
        ("Script Maestro NITE", probar_script_maestro_nite),
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
        time.sleep(3)
    
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
        print("✅ El sistema estilo NITE está funcionando correctamente")
        return True
    else:
        print(f"⚠️  {fallidos} PRUEBAS FALLARON")
        print("❌ El sistema necesita ajustes")
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
