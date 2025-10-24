#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INICIADOR PRINCIPAL OTIF MASTER
Script de inicio unificado para el sistema OTIF

Uso: python iniciar_otif.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def verificar_estructura():
    """Verifica que la estructura del proyecto esté correcta"""
    print("Verificando estructura del proyecto...")
    
    directorios_requeridos = [
        "core",
        "scripts/procesamiento",
        "scripts/sap", 
        "scripts/notebooks",
        "scripts/utilidades",
        "data",
        "output",
        "config",
        "docs"
    ]
    
    archivos_requeridos = [
        "core/menu_principal.py",
        "config/configuracion_unificada.json"
    ]
    
    errores = []
    
    for directorio in directorios_requeridos:
        if not os.path.exists(directorio):
            errores.append(f"Directorio faltante: {directorio}")
    
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            errores.append(f"Archivo faltante: {archivo}")
    
    if errores:
        print("ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  - {error}")
        return False
    else:
        print("OK: Estructura del proyecto correcta")
        return True

def cargar_configuracion():
    """Carga la configuración del sistema"""
    try:
        with open("config/configuracion_unificada.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR al cargar configuración: {str(e)}")
        return None

def mostrar_banner():
    """Muestra el banner del sistema"""
    print("="*70)
    print("           SISTEMA OTIF MASTER - INICIADOR UNIFICADO")
    print("="*70)
    print()

def mostrar_opciones():
    """Muestra las opciones de inicio"""
    print("OPCIONES DE INICIO:")
    print("  1. Menu principal (Recomendado)")
    print("  2. Menu CMD (Version anterior)")
    print("  3. Menu completo (Version anterior)")
    print("  4. Aplicacion web")
    print("  5. Verificar sistema")
    print("  6. Ver configuracion")
    print("  0. Salir")
    print("=" * 50)

def ejecutar_menu_principal():
    """Ejecuta el menu principal unificado"""
    try:
        subprocess.run([sys.executable, "core/menu_principal.py"])
    except Exception as e:
        print(f"ERROR al ejecutar menu principal: {str(e)}")

def ejecutar_menu_cmd():
    """Ejecuta el menu CMD anterior"""
    try:
        if os.path.exists("menu_cmd.py"):
            subprocess.run([sys.executable, "menu_cmd.py"])
        else:
            print("ERROR: menu_cmd.py no encontrado")
    except Exception as e:
        print(f"ERROR al ejecutar menu CMD: {str(e)}")

def ejecutar_menu_completo():
    """Ejecuta el menu completo anterior"""
    try:
        if os.path.exists("menu_completo.py"):
            subprocess.run([sys.executable, "menu_completo.py"])
        else:
            print("ERROR: menu_completo.py no encontrado")
    except Exception as e:
        print(f"ERROR al ejecutar menu completo: {str(e)}")

def ejecutar_aplicacion_web():
    """Ejecuta la aplicación web"""
    try:
        if os.path.exists("app.py"):
            print("Iniciando aplicación web...")
            subprocess.run([sys.executable, "app.py"])
        else:
            print("ERROR: app.py no encontrado")
    except Exception as e:
        print(f"ERROR al ejecutar aplicación web: {str(e)}")

def verificar_sistema():
    """Verifica el estado del sistema"""
    print("VERIFICACION COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    # Verificar estructura
    if verificar_estructura():
        print("✓ Estructura del proyecto: OK")
    else:
        print("✗ Estructura del proyecto: ERROR")
    
    # Verificar Python
    print(f"✓ Python: {sys.version}")
    
    # Verificar dependencias básicas
    dependencias = ["os", "sys", "subprocess", "json", "pathlib"]
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✓ {dep}: OK")
        except ImportError:
            print(f"✗ {dep}: ERROR")
    
    # Verificar archivos de configuración
    if os.path.exists("config/configuracion_unificada.json"):
        print("✓ Configuración: OK")
    else:
        print("✗ Configuración: ERROR")

def ver_configuracion():
    """Muestra la configuración del sistema"""
    config = cargar_configuracion()
    if config:
        print("CONFIGURACION DEL SISTEMA")
        print("=" * 50)
        print(f"Sistema: {config['sistema']['nombre']} v{config['sistema']['version']}")
        print(f"Descripción: {config['sistema']['descripcion']}")
        print(f"Fecha: {config['sistema']['fecha_creacion']}")
        print()
        print("RUTAS:")
        for nombre, ruta in config['rutas'].items():
            print(f"  {nombre}: {ruta}")
        print()
        print("SCRIPTS PRINCIPALES:")
        for categoria, scripts in config['scripts_principales'].items():
            print(f"  {categoria}: {len(scripts)} scripts")

def main():
    """Función principal del iniciador"""
    mostrar_banner()
    
    # Verificar estructura básica
    if not verificar_estructura():
        print("\nERROR: La estructura del proyecto no es correcta")
        print("Por favor, ejecuta el script de reestructuración primero")
        return
    
    while True:
        mostrar_opciones()
        
        try:
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == "0":
                print("Hasta luego!")
                break
            elif opcion == "1":
                ejecutar_menu_principal()
            elif opcion == "2":
                ejecutar_menu_cmd()
            elif opcion == "3":
                ejecutar_menu_completo()
            elif opcion == "4":
                ejecutar_aplicacion_web()
            elif opcion == "5":
                verificar_sistema()
                input("\nPresiona Enter para continuar...")
            elif opcion == "6":
                ver_configuracion()
                input("\nPresiona Enter para continuar...")
            else:
                print("Opción inválida. Por favor selecciona una opción válida.")
                
        except KeyboardInterrupt:
            print("\n\nSistema interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\nERROR inesperado: {str(e)}")

if __name__ == "__main__":
    main()
