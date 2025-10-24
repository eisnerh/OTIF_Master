#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MENU INTERACTIVO OTIF - VERSION CMD
Sistema de menu simple y eficiente para CMD sin dependencias de tkinter

Uso: python menu_cmd.py
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

def limpiar_pantalla():
    """Limpia la pantalla del CMD"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    """Muestra el banner del sistema"""
    print("="*60)
    print("           SISTEMA OTIF MASTER - MENU INTERACTIVO")
    print("="*60)
    print()

def mostrar_menu_principal():
    """Muestra el menu principal"""
    print("PROCESAMIENTO DE DATOS:")
    print("  1. Ejecutar TODO el procesamiento OTIF")
    print("  2. Procesar solo NO ENTREGAS")
    print("  3. Procesar solo REP PLR")
    print("  4. Procesar solo VOL PORTAFOLIO")
    print("  5. Unificar todos los datos")
    print()
    print("VERIFICACION Y MONITOREO:")
    print("  6. Verificar estado de rutas")
    print("  7. Ver resumen de procesamiento")
    print("  8. Verificar estructura del sistema")
    print("  9. Ver archivos generados")
    print()
    print("INTERFAZ WEB:")
    print("  10. Iniciar aplicacion web")
    print()
    print("HERRAMIENTAS:")
    print("  11. Ver informacion del sistema")
    print("  12. Limpiar archivos temporales")
    print("  13. Ver estadisticas de rendimiento")
    print()
    print("SALIR:")
    print("  0. Salir del sistema")
    print("=" * 60)

def ejecutar_script(script_name, descripcion=""):
    """Ejecuta un script y muestra el progreso"""
    print(f"EJECUTANDO: {descripcion or script_name}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Verificar si el script existe
        script_path = f"scripts/{script_name}"
        if not os.path.exists(script_path):
            print(f"ERROR: No se encontro el script {script_name}")
            return False
        
        # Ejecutar el script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Mostrar salida
        if result.stdout:
            print("SALIDA:")
            print(result.stdout)
        
        if result.stderr:
            print("ADVERTENCIAS/ERRORES:")
            print(result.stderr)
        
        # Verificar resultado
        end_time = time.time()
        tiempo = end_time - start_time
        
        if result.returncode == 0:
            print(f"OK {script_name} completado exitosamente ({tiempo:.2f}s)")
            return True
        else:
            print(f"ERROR en {script_name} (codigo: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"ERROR inesperado en {script_name}: {str(e)}")
        return False

def ejecutar_todo():
    """Ejecuta todo el procesamiento OTIF"""
    print("EJECUTANDO TODO EL PROCESAMIENTO OTIF")
    print("=" * 50)
    
    scripts = [
        ("agrupar_datos_no_entregas_mejorado.py", "Agrupacion de datos NO ENTREGAS"),
        ("agrupar_datos_rep_plr.py", "Agrupacion de datos REP PLR"),
        ("agrupar_datos_vol_portafolio.py", "Agrupacion de datos VOL PORTAFOLIO"),
        ("unificar_datos_completos.py", "Unificacion de todos los datos")
    ]
    
    exitosos = 0
    total = len(scripts)
    
    for i, (script, descripcion) in enumerate(scripts, 1):
        print(f"\nPASO {i}/{total}: {descripcion}")
        print("-" * 40)
        
        if ejecutar_script(script, descripcion):
            exitosos += 1
        
        if i < total:
            print("\nContinuando con el siguiente paso...")
            time.sleep(1)
    
    # Resumen final
    print(f"\n{'='*50}")
    print("RESUMEN DE EJECUCION")
    print(f"{'='*50}")
    print(f"Scripts exitosos: {exitosos}/{total}")
    
    if exitosos == total:
        print("PROCESAMIENTO COMPLETADO EXITOSAMENTE!")
    else:
        print("ALGUNOS SCRIPTS FALLARON")
    
    return exitosos == total

def verificar_rutas():
    """Verifica el estado de las rutas"""
    print("VERIFICANDO ESTADO DE RUTAS")
    print("=" * 40)
    
    try:
        if os.path.exists("verificar_estado_rutas.py"):
            result = subprocess.run([sys.executable, "verificar_estado_rutas.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("ADVERTENCIAS:")
                print(result.stderr)
        else:
            print("Script de verificacion no encontrado")
    except Exception as e:
        print(f"ERROR: {str(e)}")

def ver_resumen():
    """Muestra el resumen de procesamiento"""
    print("RESUMEN DE PROCESAMIENTO")
    print("=" * 40)
    
    archivos_resumen = [
        "Data/Output/calculo_otif/resumen_procesamiento.json",
        "resumen_procesamiento.json"
    ]
    
    for archivo in archivos_resumen:
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    resumen = json.load(f)
                
                print(f"Archivo: {archivo}")
                print(f"Fecha: {resumen.get('fecha_procesamiento', 'No disponible')}")
                print(f"Tiempo total: {resumen.get('tiempo_total', 'No disponible')}")
                
                if 'estadisticas' in resumen:
                    print("\nESTADISTICAS:")
                    for key, value in resumen['estadisticas'].items():
                        print(f"   - {key}: {value}")
                break
            except Exception as e:
                print(f"ERROR al leer resumen: {str(e)}")
    else:
        print("No se encontro ningun archivo de resumen")

def verificar_estructura():
    """Verifica la estructura del sistema"""
    print("VERIFICANDO ESTRUCTURA DEL SISTEMA")
    print("=" * 40)
    
    try:
        if os.path.exists("scripts/verificar_estructura.py"):
            result = subprocess.run([sys.executable, "scripts/verificar_estructura.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("ADVERTENCIAS:")
                print(result.stderr)
        else:
            print("Script de verificacion no encontrado")
    except Exception as e:
        print(f"ERROR: {str(e)}")

def ver_archivos_generados():
    """Muestra los archivos generados por el sistema"""
    print("ARCHIVOS GENERADOS POR EL SISTEMA")
    print("=" * 50)
    
    directorios = [
        ("Data/Output/calculo_otif", "Archivos finales"),
        ("Data/Output_Unificado", "Archivos unificados"),
        ("Data/Rep PLR/Output", "Archivos REP PLR"),
        ("Data/No Entregas/Output", "Archivos No Entregas"),
        ("Data/Vol_Portafolio/Output", "Archivos Vol Portafolio")
    ]
    
    for directorio, descripcion in directorios:
        print(f"\n{descripcion} ({directorio}):")
        if os.path.exists(directorio):
            archivos = [f for f in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, f))]
            if archivos:
                for archivo in archivos:
                    ruta_completa = os.path.join(directorio, archivo)
                    if os.path.isfile(ruta_completa):
                        tamaño = os.path.getsize(ruta_completa)
                        tamaño_mb = tamaño / (1024 * 1024)
                        print(f"   - {archivo} ({tamaño_mb:.2f} MB)")
            else:
                print("   No hay archivos")
        else:
            print("   Directorio no existe")

def iniciar_web():
    """Inicia la aplicacion web"""
    print("INICIANDO APLICACION WEB")
    print("=" * 40)
    
    try:
        print("Iniciando servidor web...")
        print("La aplicacion estara disponible en: http://localhost:5000")
        print("Presiona Ctrl+C para detener el servidor")
        print()
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nServidor web detenido")
    except Exception as e:
        print(f"ERROR al iniciar aplicacion web: {str(e)}")

def ver_informacion_sistema():
    """Muestra informacion del sistema"""
    print("INFORMACION DEL SISTEMA OTIF")
    print("=" * 50)
    
    print("VERSION: Sistema OTIF Master v2.5")
    print("FECHA: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Scripts disponibles
    print("SCRIPTS DISPONIBLES:")
    scripts_dir = "scripts"
    if os.path.exists(scripts_dir):
        scripts = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
        for script in scripts:
            print(f"   - {script}")
    else:
        print("   Carpeta scripts no encontrada")
    
    print()
    
    # Configuracion
    print("CONFIGURACION:")
    if os.path.exists("configuracion_rutas.json"):
        try:
            with open("configuracion_rutas.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"   Archivo de configuracion: configuracion_rutas.json")
            print(f"   Ultima actualizacion: {config.get('ultima_actualizacion', 'No disponible')}")
        except:
            print("   Error al leer configuracion")
    else:
        print("   Archivo de configuracion no encontrado")

def limpiar_archivos_temporales():
    """Limpia archivos temporales"""
    print("LIMPIANDO ARCHIVOS TEMPORALES")
    print("=" * 40)
    
    print("Esta funcion limpiara archivos temporales del sistema.")
    print("Archivos que se eliminaran:")
    print("   - __pycache__")
    print("   - *.pyc")
    print("   - *.pyo")
    print("   - *.tmp")
    
    respuesta = input("\nDeseas continuar? (s/n): ").lower()
    if respuesta != 's':
        print("Limpieza cancelada")
        return
    
    print("Limpieza completada (funcion en desarrollo)")

def ver_estadisticas_rendimiento():
    """Muestra estadisticas de rendimiento"""
    print("ESTADISTICAS DE RENDIMIENTO")
    print("=" * 40)
    
    print("TIEMPOS ESTIMADOS DE PROCESAMIENTO:")
    print("   - Rep PLR: 1-2 minutos")
    print("   - No Entregas: 2-3 minutos")
    print("   - Vol Portafolio: 1-2 minutos")
    print("   - Unificacion: 1-2 minutos")
    print("   - Total completo: 5-10 minutos")
    print()
    
    print("REQUISITOS DEL SISTEMA:")
    print("   - RAM: Minimo 8 GB (recomendado 16 GB)")
    print("   - CPU: Minimo 4 nucleos")
    print("   - Disco: Suficiente espacio para archivos temporales")
    print()
    
    print("ARCHIVOS PRINCIPALES GENERADOS:")
    print("   - rep_plr.parquet")
    print("   - no_entregas.parquet")
    print("   - vol_portafolio.parquet")
    print("   - datos_completos_con_no_entregas.parquet")

def pausa():
    """Pausa para que el usuario pueda leer la informacion"""
    input("\nPresiona Enter para continuar...")

def main():
    """Funcion principal del menu"""
    while True:
        limpiar_pantalla()
        mostrar_banner()
        mostrar_menu_principal()
        
        try:
            opcion = input("\nSelecciona una opcion: ").strip()
            
            if opcion == "0":
                print("Hasta luego!")
                break
            elif opcion == "1":
                ejecutar_todo()
                pausa()
            elif opcion == "2":
                ejecutar_script("agrupar_datos_no_entregas_mejorado.py", "Agrupacion de datos NO ENTREGAS")
                pausa()
            elif opcion == "3":
                ejecutar_script("agrupar_datos_rep_plr.py", "Agrupacion de datos REP PLR")
                pausa()
            elif opcion == "4":
                ejecutar_script("agrupar_datos_vol_portafolio.py", "Agrupacion de datos VOL PORTAFOLIO")
                pausa()
            elif opcion == "5":
                ejecutar_script("unificar_datos_completos.py", "Unificacion de todos los datos")
                pausa()
            elif opcion == "6":
                verificar_rutas()
                pausa()
            elif opcion == "7":
                ver_resumen()
                pausa()
            elif opcion == "8":
                verificar_estructura()
                pausa()
            elif opcion == "9":
                ver_archivos_generados()
                pausa()
            elif opcion == "10":
                iniciar_web()
            elif opcion == "11":
                ver_informacion_sistema()
                pausa()
            elif opcion == "12":
                limpiar_archivos_temporales()
                pausa()
            elif opcion == "13":
                ver_estadisticas_rendimiento()
                pausa()
            else:
                print("Opcion invalida. Por favor selecciona una opcion valida.")
                pausa()
                
        except KeyboardInterrupt:
            print("\n\nSistema interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\nERROR inesperado: {str(e)}")
            pausa()

if __name__ == "__main__":
    main()