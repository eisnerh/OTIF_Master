#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIMPIEZA DEL PROYECTO OTIF
Script para limpiar archivos temporales y organizar el proyecto

Uso: python scripts/utilidades/limpiar_proyecto.py
"""

import os
import shutil
import glob
from pathlib import Path

def limpiar_archivos_temporales():
    """Limpia archivos temporales del proyecto"""
    print("LIMPIEZA DE ARCHIVOS TEMPORALES")
    print("=" * 50)
    
    patrones_temporales = [
        "*.tmp",
        "*.temp", 
        "*.log",
        "*.pyc",
        "__pycache__",
        "*.bak",
        "*.old"
    ]
    
    archivos_eliminados = 0
    directorios_eliminados = 0
    
    for patron in patrones_temporales:
        # Buscar archivos
        for archivo in glob.glob(f"**/{patron}", recursive=True):
            try:
                if os.path.isfile(archivo):
                    os.remove(archivo)
                    archivos_eliminados += 1
                    print(f"Eliminado archivo: {archivo}")
                elif os.path.isdir(archivo):
                    shutil.rmtree(archivo)
                    directorios_eliminados += 1
                    print(f"Eliminado directorio: {archivo}")
            except Exception as e:
                print(f"Error al eliminar {archivo}: {str(e)}")
    
    print(f"\nResumen: {archivos_eliminados} archivos, {directorios_eliminados} directorios eliminados")

def verificar_estructura():
    """Verifica y crea la estructura del proyecto"""
    print("\nVERIFICACION DE ESTRUCTURA")
    print("=" * 50)
    
    directorios_requeridos = [
        "core",
        "scripts/procesamiento",
        "scripts/sap",
        "scripts/notebooks", 
        "scripts/utilidades",
        "data",
        "output",
        "config",
        "docs",
        "batch"
    ]
    
    for directorio in directorios_requeridos:
        if not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
            print(f"Creado directorio: {directorio}")
        else:
            print(f"OK: {directorio}")

def organizar_archivos_sueltos():
    """Organiza archivos que puedan estar sueltos en el directorio raíz"""
    print("\nORGANIZACION DE ARCHIVOS")
    print("=" * 50)
    
    # Archivos que deberían estar en utilidades
    archivos_utilidades = [
        "verificar_estado_rutas.py",
        "test_menu.py",
        "ejecutar_notebook.py",
        "ejemplo_favoritos.py"
    ]
    
    for archivo in archivos_utilidades:
        if os.path.exists(archivo):
            destino = f"scripts/utilidades/{archivo}"
            try:
                shutil.move(archivo, destino)
                print(f"Movido: {archivo} -> {destino}")
            except Exception as e:
                print(f"Error al mover {archivo}: {str(e)}")
    
    # Archivos de configuración
    archivos_config = [
        "resumen_conversion_xls.json"
    ]
    
    for archivo in archivos_config:
        if os.path.exists(archivo):
            destino = f"config/{archivo}"
            try:
                shutil.move(archivo, destino)
                print(f"Movido: {archivo} -> {destino}")
            except Exception as e:
                print(f"Error al mover {archivo}: {str(e)}")

def crear_archivos_faltantes():
    """Crea archivos que puedan faltar"""
    print("\nCREACION DE ARCHIVOS FALTANTES")
    print("=" * 50)
    
    # Crear .gitignore si no existe
    if not os.path.exists(".gitignore"):
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints

# Data files
*.xlsx
*.xls
*.csv
*.json

# Output files
output/
data/

# Temporary files
*.tmp
*.temp
*.log
*.bak
*.old
"""
        with open(".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("Creado: .gitignore")
    
    # Crear archivo de requisitos si no existe
    if not os.path.exists("requirements.txt"):
        requirements_content = """# Dependencias básicas
pandas>=1.3.0
numpy>=1.21.0
openpyxl>=3.0.0

# Dependencias opcionales
jupyter>=1.0.0
flask>=2.0.0

# Dependencias de desarrollo
pytest>=6.0.0
"""
        with open("requirements.txt", 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        print("Creado: requirements.txt")

def mostrar_resumen():
    """Muestra un resumen del proyecto"""
    print("\nRESUMEN DEL PROYECTO")
    print("=" * 50)
    
    # Contar archivos por tipo
    contadores = {"py": 0, "ipynb": 0, "json": 0, "md": 0, "bat": 0}
    
    for root, dirs, files in os.walk("."):
        for file in files:
            extension = file.split(".")[-1].lower()
            if extension in contadores:
                contadores[extension] += 1
    
    print("Archivos por tipo:")
    for tipo, cantidad in contadores.items():
        print(f"  {tipo.upper()}: {cantidad} archivos")
    
    # Mostrar estructura
    print("\nEstructura del proyecto:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:5]:  # Mostrar solo los primeros 5 archivos
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... y {len(files) - 5} más")

def main():
    """Función principal de limpieza"""
    print("LIMPIEZA Y ORGANIZACION DEL PROYECTO OTIF")
    print("=" * 60)
    
    # Limpiar archivos temporales
    limpiar_archivos_temporales()
    
    # Verificar estructura
    verificar_estructura()
    
    # Organizar archivos
    organizar_archivos_sueltos()
    
    # Crear archivos faltantes
    crear_archivos_faltantes()
    
    # Mostrar resumen
    mostrar_resumen()
    
    print("\nLimpieza completada exitosamente!")

if __name__ == "__main__":
    main()
