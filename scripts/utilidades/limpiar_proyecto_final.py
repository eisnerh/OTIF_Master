#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIMPIEZA FINAL DEL PROYECTO OTIF
Script para limpiar archivos temporales y optimizar el proyecto

Uso: python scripts/utilidades/limpiar_proyecto_final.py
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
        "*.old",
        "*.swp",
        "*.swo",
        "*~"
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

def verificar_estructura_final():
    """Verifica la estructura final del proyecto"""
    print("\nVERIFICACION DE ESTRUCTURA FINAL")
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
    
    archivos_requeridos = [
        "core/menu_principal.py",
        "iniciar_otif.py",
        "config/configuracion_unificada.json",
        "docs/README_UNIFICADO.md",
        "batch/iniciar_otif.bat"
    ]
    
    todos_ok = True
    
    print("DIRECTORIOS:")
    for directorio in directorios_requeridos:
        if os.path.exists(directorio):
            print(f"✓ {directorio}")
        else:
            print(f"✗ {directorio} - FALTANTE")
            todos_ok = False
    
    print("\nARCHIVOS PRINCIPALES:")
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✓ {archivo}")
        else:
            print(f"✗ {archivo} - FALTANTE")
            todos_ok = False
    
    return todos_ok

def contar_archivos_por_tipo():
    """Cuenta archivos por tipo en el proyecto"""
    print("\nCONTEO DE ARCHIVOS POR TIPO")
    print("=" * 50)
    
    contadores = {
        "py": 0, 
        "ipynb": 0, 
        "json": 0, 
        "md": 0, 
        "bat": 0,
        "xls": 0,
        "xlsx": 0,
        "vba": 0,
        "yaml": 0,
        "html": 0,
        "css": 0,
        "js": 0
    }
    
    for root, dirs, files in os.walk("."):
        # Omitir directorios ocultos y __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            extension = file.split(".")[-1].lower()
            if extension in contadores:
                contadores[extension] += 1
    
    print("Archivos por tipo:")
    for tipo, cantidad in contadores.items():
        if cantidad > 0:
            print(f"  {tipo.upper()}: {cantidad} archivos")
    
    return contadores

def mostrar_estructura_final():
    """Muestra la estructura final del proyecto"""
    print("\nESTRUCTURA FINAL DEL PROYECTO")
    print("=" * 50)
    
    for root, dirs, files in os.walk("."):
        # Omitir directorios ocultos y __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:5]:  # Mostrar solo los primeros 5 archivos
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... y {len(files) - 5} más")

def optimizar_archivos():
    """Optimiza archivos del proyecto"""
    print("\nOPTIMIZACION DE ARCHIVOS")
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

# Output files
output/
data/

# Temporary files
*.tmp
*.temp
*.log
*.bak
*.old
*.swp
*.swo
*~

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        with open(".gitignore", 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("✓ Creado .gitignore")
    
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
        print("✓ Creado requirements.txt")

def mostrar_resumen_final():
    """Muestra un resumen final del proyecto"""
    print("\nRESUMEN FINAL DEL PROYECTO")
    print("=" * 50)
    
    contadores = contar_archivos_por_tipo()
    
    total_archivos = sum(contadores.values())
    print(f"Total de archivos: {total_archivos}")
    
    # Mostrar estadísticas por directorio
    print("\nArchivos por directorio:")
    for root, dirs, files in os.walk("."):
        if root == ".":
            continue
        level = root.replace(".", "").count(os.sep)
        if level <= 2:  # Solo mostrar hasta 2 niveles
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/: {len(files)} archivos")

def main():
    """Función principal de limpieza final"""
    print("LIMPIEZA FINAL DEL PROYECTO OTIF")
    print("=" * 60)
    
    # Limpiar archivos temporales
    limpiar_archivos_temporales()
    
    # Verificar estructura
    if verificar_estructura_final():
        print("\n✓ Estructura del proyecto correcta")
    else:
        print("\n✗ Estructura del proyecto con errores")
    
    # Optimizar archivos
    optimizar_archivos()
    
    # Mostrar resumen
    mostrar_resumen_final()
    
    # Mostrar estructura final
    mostrar_estructura_final()
    
    print("\nLIMPIEZA FINAL COMPLETADA EXITOSAMENTE!")
    print("El proyecto está optimizado y listo para usar.")

if __name__ == "__main__":
    main()
