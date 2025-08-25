#!/usr/bin/env python3
"""
🧹 SCRIPT DE LIMPIEZA - PROYECTO OTIF
=====================================

Este script limpia archivos temporales y mantiene solo los archivos principales
del proyecto para una estructura más limpia.

Autor: Sistema de Procesamiento OTIF
Fecha: 2025
"""

import os
import shutil
from pathlib import Path

def limpiar_archivos_temporales():
    """Elimina archivos temporales y mantiene solo los principales."""
    print("🧹 LIMPIANDO PROYECTO OTIF")
    print("=" * 50)
    
    # Archivos a mantener (principales)
    archivos_principales = [
        "iniciar_sistema.py",
        "procesamiento_maestro.py", 
        "app.py",
        "requirements.txt",
        "README_ESTRUCTURA_MEJORADA.md"
    ]
    
    # Archivos a eliminar (temporales o duplicados)
    archivos_a_eliminar = [
        "iniciar_app.py",
        "procesamiento_completo_otif.py",
        "copiar_archivos_finales.py",
        "README_WEB.md",
        "README_Procesamiento.md",
        "procesamiento_maestro.log"
    ]
    
    # Carpetas a mantener
    carpetas_principales = [
        "scripts",
        "templates", 
        "Data"
    ]
    
    # Carpetas a eliminar
    carpetas_a_eliminar = [
        "__pycache__",
        ".vscode"
    ]
    
    print("📁 Archivos principales a mantener:")
    for archivo in archivos_principales:
        if Path(archivo).exists():
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} (no encontrado)")
    
    print("\n🗑️ Archivos temporales a eliminar:")
    for archivo in archivos_a_eliminar:
        if Path(archivo).exists():
            try:
                Path(archivo).unlink()
                print(f"  🗑️ Eliminado: {archivo}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {archivo}: {e}")
        else:
            print(f"  ⚠️ {archivo} (no encontrado)")
    
    print("\n📁 Carpetas principales a mantener:")
    for carpeta in carpetas_principales:
        if Path(carpeta).exists():
            print(f"  ✅ {carpeta}")
        else:
            print(f"  ❌ {carpeta} (no encontrada)")
    
    print("\n🗑️ Carpetas temporales a eliminar:")
    for carpeta in carpetas_a_eliminar:
        if Path(carpeta).exists():
            try:
                shutil.rmtree(carpeta)
                print(f"  🗑️ Eliminada: {carpeta}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {carpeta}: {e}")
        else:
            print(f"  ⚠️ {carpeta} (no encontrada)")
    
    # Limpiar archivos __pycache__ en subcarpetas
    print("\n🧹 Limpiando archivos __pycache__:")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(cache_path)
                print(f"  🗑️ Eliminado: {cache_path}")
            except Exception as e:
                print(f"  ❌ Error al eliminar {cache_path}: {e}")
    
    print("\n✅ Limpieza completada!")
    print("📁 Estructura final del proyecto:")
    mostrar_estructura_final()

def mostrar_estructura_final():
    """Muestra la estructura final del proyecto."""
    estructura = """
Procesamiento_Portafolio_No_Entregas/
├── 📁 scripts/                          # Scripts de procesamiento
│   ├── agrupar_datos_rep_plr.py
│   ├── agrupar_datos_no_entregas_mejorado.py
│   ├── agrupar_datos_vol_portafolio.py
│   └── unificar_datos_completos.py
├── 📁 templates/                         # Interfaz web
│   └── index.html
├── 📁 Data/                             # Datos de entrada y salida
│   ├── Rep PLR/
│   ├── No Entregas/2025/
│   ├── Vol_Portafolio/
│   └── Output/calculo_otif/
├── 🎮 iniciar_sistema.py                # Script principal
├── 🚀 procesamiento_maestro.py          # Script maestro
├── 🌐 app.py                            # Aplicación web
├── 📋 requirements.txt                  # Dependencias
└── 📖 README_ESTRUCTURA_MEJORADA.md     # Documentación
"""
    print(estructura)

def verificar_archivos_principales():
    """Verifica que los archivos principales estén presentes."""
    print("\n🔍 VERIFICANDO ARCHIVOS PRINCIPALES:")
    
    archivos_requeridos = [
        "iniciar_sistema.py",
        "procesamiento_maestro.py",
        "app.py", 
        "requirements.txt",
        "scripts/agrupar_datos_rep_plr.py",
        "scripts/agrupar_datos_no_entregas_mejorado.py",
        "scripts/agrupar_datos_vol_portafolio.py",
        "scripts/unificar_datos_completos.py",
        "templates/index.html"
    ]
    
    todos_presentes = True
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} (FALTANTE)")
            todos_presentes = False
    
    if todos_presentes:
        print("\n🎉 ¡Todos los archivos principales están presentes!")
    else:
        print("\n⚠️ Algunos archivos principales están faltantes.")
    
    return todos_presentes

def main():
    """Función principal."""
    print("🧹 SCRIPT DE LIMPIEZA - PROYECTO OTIF")
    print("=" * 50)
    
    # Preguntar confirmación
    respuesta = input("\n¿Estás seguro de que quieres limpiar el proyecto? (s/N): ").strip().lower()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        limpiar_archivos_temporales()
        verificar_archivos_principales()
        print("\n🎯 PROYECTO LIMPIO Y ORGANIZADO")
        print("=" * 50)
        print("✅ Estructura optimizada")
        print("✅ Archivos temporales eliminados")
        print("✅ Solo archivos principales mantenidos")
        print("\n🚀 Para usar el sistema:")
        print("   python iniciar_sistema.py")
    else:
        print("\n❌ Limpieza cancelada")

if __name__ == "__main__":
    main()
