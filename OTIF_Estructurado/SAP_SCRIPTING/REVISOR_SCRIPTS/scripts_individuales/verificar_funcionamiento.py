#!/usr/bin/env python3
"""
Script de verificación simple para comprobar que los archivos funcionan correctamente
"""

import os
import sys
from datetime import datetime

def verificar_archivos_existentes():
    """
    Verifica que todos los archivos necesarios existen
    """
    print("🔍 VERIFICANDO ARCHIVOS EXISTENTES")
    print("=" * 60)
    
    archivos_requeridos = [
        "zsd_incidencias_nite_style.py",
        "script_maestro_nite_exacto.py", 
        "probar_nite_style.py",
        "generar_scripts_nite.py"
    ]
    
    archivos_encontrados = 0
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            tamaño = os.path.getsize(archivo)
            print(f"✅ {archivo} - {tamaño:,} bytes")
            archivos_encontrados += 1
        else:
            print(f"❌ {archivo} - No encontrado")
    
    print(f"\n📊 Archivos encontrados: {archivos_encontrados}/{len(archivos_requeridos)}")
    return archivos_encontrados == len(archivos_requeridos)

def verificar_sintaxis_python():
    """
    Verifica que los archivos Python tienen sintaxis correcta
    """
    print("\n🐍 VERIFICANDO SINTAXIS PYTHON")
    print("=" * 60)
    
    archivos_python = [
        "zsd_incidencias_nite_style.py",
        "script_maestro_nite_exacto.py",
        "probar_nite_style.py",
        "generar_scripts_nite.py"
    ]
    
    archivos_correctos = 0
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            # Compilar para verificar sintaxis
            compile(codigo, archivo, 'exec')
            print(f"✅ {archivo} - Sintaxis correcta")
            archivos_correctos += 1
            
        except SyntaxError as e:
            print(f"❌ {archivo} - Error de sintaxis: {e}")
        except Exception as e:
            print(f"❌ {archivo} - Error: {e}")
    
    print(f"\n📊 Archivos con sintaxis correcta: {archivos_correctos}/{len(archivos_python)}")
    return archivos_correctos == len(archivos_python)

def verificar_importaciones():
    """
    Verifica que las importaciones necesarias están disponibles
    """
    print("\n📦 VERIFICANDO IMPORTACIONES")
    print("=" * 60)
    
    importaciones_requeridas = [
        ("win32com.client", "Para conexión SAP"),
        ("datetime", "Para manejo de fechas"),
        ("os", "Para operaciones de archivos"),
        ("time", "Para delays"),
        ("subprocess", "Para ejecutar scripts"),
        ("sys", "Para argumentos del sistema")
    ]
    
    importaciones_exitosas = 0
    
    for modulo, descripcion in importaciones_requeridas:
        try:
            __import__(modulo)
            print(f"✅ {modulo} - {descripcion}")
            importaciones_exitosas += 1
        except ImportError as e:
            print(f"❌ {modulo} - No disponible: {e}")
    
    print(f"\n📊 Importaciones exitosas: {importaciones_exitosas}/{len(importaciones_requeridas)}")
    return importaciones_exitosas == len(importaciones_requeridas)

def verificar_estructura_scripts():
    """
    Verifica que los scripts tienen la estructura correcta
    """
    print("\n🏗️ VERIFICANDO ESTRUCTURA DE SCRIPTS")
    print("=" * 60)
    
    # Verificar script de incidencias
    try:
        with open("zsd_incidencias_nite_style.py", 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        elementos_requeridos = [
            "def ejecutar_zsd_incidencias()",
            "win32com.client.GetObject",
            "session.findById",
            "if __name__ == \"__main__\":"
        ]
        
        elementos_encontrados = 0
        for elemento in elementos_requeridos:
            if elemento in contenido:
                print(f"✅ Elemento encontrado: {elemento}")
                elementos_encontrados += 1
            else:
                print(f"❌ Elemento faltante: {elemento}")
        
        print(f"\n📊 Elementos encontrados: {elementos_encontrados}/{len(elementos_requeridos)}")
        return elementos_encontrados == len(elementos_requeridos)
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def main():
    """
    Función principal de verificación
    """
    print("🧪 INICIANDO VERIFICACIÓN DEL SISTEMA")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    verificaciones = [
        ("Archivos Existentes", verificar_archivos_existentes),
        ("Sintaxis Python", verificar_sintaxis_python),
        ("Importaciones", verificar_importaciones),
        ("Estructura Scripts", verificar_estructura_scripts)
    ]
    
    exitosos = 0
    fallidos = 0
    
    for nombre, funcion in verificaciones:
        print(f"\n🔄 Ejecutando verificación: {nombre}")
        if funcion():
            exitosos += 1
            print(f"✅ {nombre}: EXITOSO")
        else:
            fallidos += 1
            print(f"❌ {nombre}: FALLÓ")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 80)
    print(f"✅ Verificaciones exitosas: {exitosos}")
    print(f"❌ Verificaciones fallidas: {fallidos}")
    print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if fallidos == 0:
        print("🎉 TODAS LAS VERIFICACIONES COMPLETADAS EXITOSAMENTE")
        print("✅ El sistema está listo para usar")
        return True
    else:
        print(f"⚠️  {fallidos} VERIFICACIONES FALLARON")
        print("❌ El sistema necesita ajustes")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Verificación completada exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Verificación completada con errores")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
