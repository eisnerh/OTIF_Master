#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICACION DE REESTRUCTURACION
Script para verificar que la reestructuración se completó correctamente

Uso: python scripts/utilidades/verificar_reestructuracion.py
"""

import os
import json
from pathlib import Path

def verificar_estructura_directorios():
    """Verifica que todos los directorios necesarios existan"""
    print("VERIFICACION DE DIRECTORIOS")
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
    
    todos_ok = True
    
    for directorio in directorios_requeridos:
        if os.path.exists(directorio):
            print(f"✓ {directorio}")
        else:
            print(f"✗ {directorio} - FALTANTE")
            todos_ok = False
    
    return todos_ok

def verificar_archivos_principales():
    """Verifica que los archivos principales existan"""
    print("\nVERIFICACION DE ARCHIVOS PRINCIPALES")
    print("=" * 50)
    
    archivos_requeridos = [
        "core/menu_principal.py",
        "iniciar_otif.py",
        "config/configuracion_unificada.json",
        "docs/README_UNIFICADO.md",
        "batch/iniciar_otif.bat"
    ]
    
    todos_ok = True
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✓ {archivo}")
        else:
            print(f"✗ {archivo} - FALTANTE")
            todos_ok = False
    
    return todos_ok

def verificar_scripts_organizados():
    """Verifica que los scripts estén en sus directorios correctos"""
    print("\nVERIFICACION DE SCRIPTS ORGANIZADOS")
    print("=" * 50)
    
    scripts_procesamiento = [
        "scripts/procesamiento/agrupar_datos_no_entregas_mejorado.py",
        "scripts/procesamiento/agrupar_datos_rep_plr.py",
        "scripts/procesamiento/agrupar_datos_vol_portafolio.py",
        "scripts/procesamiento/unificar_datos_completos.py"
    ]
    
    scripts_utilidades = [
        "scripts/utilidades/configuracion_sistema.py",
        "scripts/utilidades/verificar_estructura.py",
        "scripts/utilidades/unificador_principal.py",
        "scripts/utilidades/menu_mas_utilizado.py",
        "scripts/utilidades/ejecutar_notebook.py",
        "scripts/utilidades/ejemplo_favoritos.py",
        "scripts/utilidades/limpiar_proyecto.py",
        "scripts/utilidades/verificar_reestructuracion.py"
    ]
    
    scripts_notebooks = [
        "scripts/notebooks/consolidar_zresguias_excel.ipynb"
    ]
    
    todos_ok = True
    
    print("Scripts de procesamiento:")
    for script in scripts_procesamiento:
        if os.path.exists(script):
            print(f"✓ {script}")
        else:
            print(f"✗ {script} - FALTANTE")
            todos_ok = False
    
    print("\nScripts de utilidades:")
    for script in scripts_utilidades:
        if os.path.exists(script):
            print(f"✓ {script}")
        else:
            print(f"✗ {script} - FALTANTE")
            todos_ok = False
    
    print("\nNotebooks:")
    for notebook in scripts_notebooks:
        if os.path.exists(notebook):
            print(f"✓ {notebook}")
        else:
            print(f"✗ {notebook} - FALTANTE")
            todos_ok = False
    
    return todos_ok

def verificar_archivos_eliminados():
    """Verifica que los archivos redundantes hayan sido eliminados"""
    print("\nVERIFICACION DE ARCHIVOS ELIMINADOS")
    print("=" * 50)
    
    archivos_eliminados = [
        "menu_cmd.py",
        "menu_completo.py",
        "ejecutar_modulo.py",
        "iniciar_menu.py",
        "iniciar_sistema.py",
        "procesar_todo.py",
        "procesamiento_maestro.py",
        "demo-menu-recursivo.html"
    ]
    
    todos_eliminados = True
    
    for archivo in archivos_eliminados:
        if not os.path.exists(archivo):
            print(f"✓ {archivo} - ELIMINADO")
        else:
            print(f"✗ {archivo} - AUN EXISTE")
            todos_eliminados = False
    
    return todos_eliminados

def verificar_configuracion():
    """Verifica que la configuración sea válida"""
    print("\nVERIFICACION DE CONFIGURACION")
    print("=" * 50)
    
    try:
        with open("config/configuracion_unificada.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Verificar estructura básica
        if "sistema" in config and "rutas" in config and "scripts_principales" in config:
            print("✓ Estructura de configuración válida")
            
            # Verificar rutas
            rutas = config["rutas"]
            for nombre, ruta in rutas.items():
                if os.path.exists(ruta):
                    print(f"✓ Ruta {nombre}: {ruta}")
                else:
                    print(f"✗ Ruta {nombre}: {ruta} - NO EXISTE")
            
            return True
        else:
            print("✗ Estructura de configuración inválida")
            return False
            
    except Exception as e:
        print(f"✗ Error al cargar configuración: {str(e)}")
        return False

def mostrar_resumen():
    """Muestra un resumen de la verificación"""
    print("\nRESUMEN DE VERIFICACION")
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
    
    # Mostrar estructura final
    print("\nEstructura final del proyecto:")
    for root, dirs, files in os.walk("."):
        # Omitir directorios ocultos y __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        level = root.replace(".", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files[:3]:  # Mostrar solo los primeros 3 archivos
            print(f"{subindent}{file}")
        if len(files) > 3:
            print(f"{subindent}... y {len(files) - 3} más")

def main():
    """Función principal de verificación"""
    print("VERIFICACION DE REESTRUCTURACION OTIF")
    print("=" * 60)
    
    # Verificaciones
    dirs_ok = verificar_estructura_directorios()
    archivos_ok = verificar_archivos_principales()
    scripts_ok = verificar_scripts_organizados()
    eliminados_ok = verificar_archivos_eliminados()
    config_ok = verificar_configuracion()
    
    # Resumen final
    print("\nRESULTADO FINAL")
    print("=" * 50)
    
    if dirs_ok and archivos_ok and scripts_ok and eliminados_ok and config_ok:
        print("✓ REESTRUCTURACION COMPLETADA EXITOSAMENTE")
        print("✓ Todos los directorios están en su lugar")
        print("✓ Todos los archivos principales existen")
        print("✓ Scripts organizados correctamente")
        print("✓ Archivos redundantes eliminados")
        print("✓ Configuración válida")
        print("\nEl sistema está listo para usar!")
        print("Ejecuta: python iniciar_otif.py")
    else:
        print("✗ REESTRUCTURACION INCOMPLETA")
        if not dirs_ok:
            print("✗ Faltan directorios")
        if not archivos_ok:
            print("✗ Faltan archivos principales")
        if not scripts_ok:
            print("✗ Scripts no organizados correctamente")
        if not eliminados_ok:
            print("✗ Archivos redundantes no eliminados")
        if not config_ok:
            print("✗ Configuración inválida")
    
    mostrar_resumen()

if __name__ == "__main__":
    main()
