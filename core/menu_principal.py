#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MENU PRINCIPAL OTIF - VERSION UNIFICADA
Sistema de menu unificado que reemplaza todos los menus anteriores

Uso: python core/menu_principal.py
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json
import shutil

def limpiar_pantalla():
    """Limpia la pantalla del CMD"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    """Muestra el banner del sistema"""
    print("="*70)
    print("           SISTEMA OTIF MASTER - MENU PRINCIPAL UNIFICADO")
    print("="*70)
    print()
    print("   1. Ejecutar notebook consolidar zresguias")
    print("   2. Carga roadshow")
    print("   3. Consolidado ultimo archivo materiales")
    print("   4. Ejecutar proceso completo SAP")
    print("   5. Reordenar archivos Excel")

def mostrar_menu_principal():
    """Muestra el menu principal unificado"""
    print("  12. Agrupacion de datos VOL PORTAFOLIO")
    print("  15. Unificacion de todos los datos")
    print()
    print("SCRIPTS ESTRUCTURADOS:")
    print("  6. Consolidar datos")
    print("  7. Reporte PLR")
    print("  8. Volumen procesado familia")
    print("  9. Volumen no entregas")
    print("  10. Consolidar archivo PLR a Parquet")
    print()
    print("AUTOMATIZACION SAP:")
    print("  11. Automatizacion reportes SAP")

    print("  13. Scripts individuales SAP (Submenu)")
    print("  14. Convertir XLS a XLSX")

    print()
    print("SCRIPTS ULTIMO ARCHIVO:")
    print("  16. Consolidado ultimo archivo materiales")
    print("  17. Consolidar zresguias")
    print("  18. Carga roadshow")
    print("  19. Consolidar mes PLR")
    print()
    print("JUPYTER NOTEBOOKS:")

    print("  21. Buscar notebooks disponibles")
    print()
    print("VERIFICACION Y MONITOREO:")
    print("  22. Verificar estado de rutas")
    print("  23. Ver resumen de procesamiento")
    print("  24. Verificar estructura del sistema")
    print("  25. Ver archivos generados")
    print()
    print("INTERFAZ WEB:")
    print("  26. Iniciar aplicacion web")
    print()
    print("HERRAMIENTAS:")
    print("  27. Ver informacion del sistema")
    print("  28. Limpiar archivos temporales")
    print("  29. Ver estadisticas de rendimiento")
    print("  30. Gestion de favoritos (Submenu)")
    print()
    print("SALIR:")
    print("  0. Salir del sistema")
    print("=" * 70)

def ejecutar_script(script_name, descripcion, ruta_completa=None):
    """Ejecuta un script Python"""
    print(f"EJECUTANDO: {descripcion}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        if ruta_completa:
            script_path = ruta_completa
        else:
            script_path = f"scripts/procesamiento/{script_name}"
        
        if not os.path.exists(script_path):
            print(f"ERROR: No se encontro el script {script_path}")
            return False
        
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print("SALIDA:")
            print(result.stdout)
        
        if result.stderr:
            print("ERRORES:")
            print(result.stderr)
        
        end_time = time.time()
        tiempo = end_time - start_time
        
        if result.returncode == 0:
            print(f"OK Script ejecutado exitosamente ({tiempo:.2f}s)")
            return True
        else:
            print(f"ERROR en script (codigo: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"ERROR inesperado en script: {str(e)}")
        return False

def ejecutar_notebook(notebook_path, descripcion=""):
    """Ejecuta un notebook de Jupyter"""
    print(f"EJECUTANDO NOTEBOOK: {descripcion or notebook_path}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        if not os.path.exists(notebook_path):
            print(f"ERROR: No se encontro el notebook {notebook_path}")
            return False
        
        # Verificar si jupyter esta instalado
        try:
            subprocess.run(["jupyter", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: Jupyter no esta instalado o no esta en el PATH")
            print("Instala jupyter con: pip install jupyter")
            return False
        
        result = subprocess.run(
            ["jupyter", "nbconvert", "--execute", "--to", "notebook", "--inplace", notebook_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print("SALIDA:")
            print(result.stdout)
        
        if result.stderr:
            print("ADVERTENCIAS/ERRORES:")
            print(result.stderr)
        
        end_time = time.time()
        tiempo = end_time - start_time
        
        if result.returncode == 0:
            print(f"OK Notebook ejecutado exitosamente ({tiempo:.2f}s)")
            return True
        else:
            print(f"ERROR en notebook (codigo: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"ERROR inesperado en notebook: {str(e)}")
        return False

def ejecutar_todo():
    """Ejecuta todo el procesamiento OTIF"""
    print("EJECUTANDO PROCESAMIENTO COMPLETO OTIF")
    print("=" * 50)
    
    scripts_orden = [
        ("agrupar_datos_no_entregas_mejorado.py", "Agrupacion de datos NO ENTREGAS"),
        ("agrupar_datos_rep_plr.py", "Agrupacion de datos REP PLR"),
        ("agrupar_datos_vol_portafolio.py", "Agrupacion de datos VOL PORTAFOLIO"),
        ("unificar_datos_completos.py", "Unificacion de todos los datos")
    ]
    
    exitosos = 0
    fallidos = 0
    
    for script, descripcion in scripts_orden:
        print(f"\n--- {descripcion} ---")
        if ejecutar_script(script, descripcion):
            exitosos += 1
        else:
            fallidos += 1
        print()
    
    print(f"RESUMEN: {exitosos} exitosos, {fallidos} fallidos")
    return exitosos > 0

def mostrar_submenu_sap_individuales():
    """Muestra el submenu de scripts individuales SAP"""
    print("SCRIPTS INDIVIDUALES SAP")
    print("=" * 40)
    print("  1. Y_DEV_45 - Devoluciones 45")
    print("  2. Y_DEV_74 - Devoluciones 74")
    print("  3. Y_DEV_82 - Devoluciones 82")
    print("  4. Y_REP_PLR - Reporte PLR")
    print("  5. Z_DEVO_ALV - Devoluciones ALV")
    print("  6. ZHBO - Reporte HBO")
    print("  7. ZRED - Reporte de Red")
    print("  8. ZRESGUIAS - Resguías")
    print("  9. ZSD_INCIDENCIAS - Incidencias")
    print("  10. Ejecutar TODOS los scripts individuales")
    print("  0. Volver al menu principal")
    print("=" * 40)

def ejecutar_submenu_sap_individuales():
    """Ejecuta el submenu de scripts individuales SAP"""
    while True:
        limpiar_pantalla()
        mostrar_submenu_sap_individuales()
        
        try:
            opcion = input("\nSelecciona una opcion: ").strip()
            
            if opcion == "0":
                break
            elif opcion == "1":
                ejecutar_script("", "Y_DEV_45", "scripts/sap/y_dev_45.py")
                pausa()
            elif opcion == "2":
                ejecutar_script("", "Y_DEV_74", "scripts/sap/y_dev_74.py")
                pausa()
            elif opcion == "3":
                ejecutar_script("", "Y_DEV_82", "scripts/sap/y_dev_82.py")
                pausa()
            elif opcion == "4":
                ejecutar_script("", "Y_REP_PLR", "scripts/sap/y_rep_plr.py")
                pausa()
            elif opcion == "5":
                ejecutar_script("", "Z_DEVO_ALV", "scripts/sap/z_devo_alv.py")
                pausa()
            elif opcion == "6":
                ejecutar_script("", "ZHBO", "scripts/sap/zhbo.py")
                pausa()
            elif opcion == "7":
                ejecutar_script("", "ZRED", "scripts/sap/zred.py")
                pausa()
            elif opcion == "8":
                ejecutar_script("", "ZRESGUIAS", "scripts/sap/zresguias.py")
                pausa()
            elif opcion == "9":
                ejecutar_script("", "ZSD_INCIDENCIAS", "scripts/sap/zsd_incidencias.py")
                pausa()
            elif opcion == "10":
                ejecutar_todos_sap_individuales()
                pausa()
            else:
                print("Opcion invalida. Por favor selecciona una opcion valida.")
                pausa()
                
        except KeyboardInterrupt:
            print("\n\nSubmenu interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\nERROR inesperado: {str(e)}")
            pausa()

def ejecutar_todos_sap_individuales():
    """Ejecuta todos los scripts individuales SAP"""
    print("EJECUTANDO TODOS LOS SCRIPTS INDIVIDUALES SAP")
    print("=" * 50)
    
    scripts_sap = [
        ("y_dev_45.py", "Y_DEV_45"),
        ("y_dev_74.py", "Y_DEV_74"),
        ("y_dev_82.py", "Y_DEV_82"),
        ("y_rep_plr.py", "Y_REP_PLR"),
        ("z_devo_alv.py", "Z_DEVO_ALV"),
        ("zhbo.py", "ZHBO"),
        ("zred.py", "ZRED"),
        ("zresguias.py", "ZRESGUIAS"),
        ("zsd_incidencias.py", "ZSD_INCIDENCIAS")
    ]
    
    exitosos = 0
    fallidos = 0
    
    for script, descripcion in scripts_sap:
        ruta = f"scripts/sap/{script}"
        print(f"\n--- {descripcion} ---")
        if ejecutar_script("", descripcion, ruta):
            exitosos += 1
        else:
            fallidos += 1
        print()
    
    print(f"RESUMEN SAP: {exitosos} exitosos, {fallidos} fallidos")

def buscar_notebooks():
    """Busca y muestra notebooks disponibles"""
    print("BUSCANDO NOTEBOOKS DISPONIBLES")
    print("=" * 50)
    
    notebooks_encontrados = []
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.ipynb'):
                ruta_completa = os.path.join(root, file)
                tamaño = os.path.getsize(ruta_completa)
                notebooks_encontrados.append((ruta_completa, tamaño))
    
    if notebooks_encontrados:
        print(f"NOTEBOOKS ENCONTRADOS: {len(notebooks_encontrados)}")
        for i, (notebook, tamaño) in enumerate(notebooks_encontrados, 1):
            tamaño_kb = tamaño / 1024
            print(f"  {i}. {notebook} ({tamaño_kb:.1f} KB)")
    else:
        print("No se encontraron notebooks")
    
    return notebooks_encontrados

def verificar_rutas():
    """Verifica el estado de las rutas del sistema"""
    print("VERIFICANDO ESTADO DE RUTAS")
    print("=" * 50)
    
    rutas_importantes = [
        "scripts/procesamiento",
        "scripts/sap", 
        "scripts/notebooks",
        "scripts/utilidades",
        "data",
        "output",
        "config"
    ]
    
    for ruta in rutas_importantes:
        if os.path.exists(ruta):
            print(f"OK: {ruta}")
        else:
            print(f"ERROR: {ruta} no existe")

def ver_resumen():
    """Muestra un resumen del procesamiento"""
    print("RESUMEN DE PROCESAMIENTO")
    print("=" * 50)
    
    # Verificar archivos de salida
    if os.path.exists("output"):
        archivos = os.listdir("output")
        print(f"Archivos en output: {len(archivos)}")
        for archivo in archivos[:10]:  # Mostrar solo los primeros 10
            print(f"  - {archivo}")
        if len(archivos) > 10:
            print(f"  ... y {len(archivos) - 10} mas")
    else:
        print("Directorio output no existe")

def verificar_estructura():
    """Verifica la estructura del sistema"""
    print("VERIFICANDO ESTRUCTURA DEL SISTEMA")
    print("=" * 50)
    
    estructura_esperada = [
        "core/menu_principal.py",
        "scripts/procesamiento",
        "scripts/sap",
        "scripts/notebooks", 
        "scripts/utilidades",
        "data",
        "output",
        "config",
        "docs"
    ]
    
    for elemento in estructura_esperada:
        if os.path.exists(elemento):
            print(f"OK: {elemento}")
        else:
            print(f"FALTA: {elemento}")

def ver_archivos_generados():
    """Muestra los archivos generados"""
    print("ARCHIVOS GENERADOS")
    print("=" * 50)
    
    directorios_salida = ["output", "data"]
    
    for directorio in directorios_salida:
        if os.path.exists(directorio):
            archivos = os.listdir(directorio)
            print(f"\n{directorio.upper()}:")
            for archivo in archivos:
                ruta_completa = os.path.join(directorio, archivo)
                tamaño = os.path.getsize(ruta_completa)
                tamaño_kb = tamaño / 1024
                print(f"  - {archivo} ({tamaño_kb:.1f} KB)")

def iniciar_web():
    """Inicia la aplicacion web"""
    print("INICIANDO APLICACION WEB")
    print("=" * 50)
    
    try:
        if os.path.exists("app.py"):
            print("Iniciando Flask...")
            subprocess.run([sys.executable, "app.py"])
        else:
            print("ERROR: app.py no encontrado")
    except Exception as e:
        print(f"ERROR al iniciar web: {str(e)}")

def ver_informacion_sistema():
    """Muestra informacion del sistema"""
    print("INFORMACION DEL SISTEMA")
    print("=" * 50)
    
    print(f"Python: {sys.version}")
    print(f"Directorio actual: {os.getcwd()}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar dependencias
    dependencias = ["pandas", "numpy", "openpyxl", "jupyter"]
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"OK: {dep}")
        except ImportError:
            print(f"FALTA: {dep}")

def limpiar_archivos_temporales():
    """Limpia archivos temporales"""
    print("LIMPIANDO ARCHIVOS TEMPORALES")
    print("=" * 50)
    
    patrones_temporales = ["*.tmp", "*.temp", "__pycache__", "*.pyc"]
    archivos_eliminados = 0
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if any(file.endswith(patron.replace("*", "")) for patron in patrones_temporales):
                try:
                    os.remove(os.path.join(root, file))
                    archivos_eliminados += 1
                    print(f"Eliminado: {file}")
                except:
                    pass
    
    print(f"Archivos temporales eliminados: {archivos_eliminados}")

def ver_estadisticas_rendimiento():
    """Muestra estadisticas de rendimiento"""
    print("ESTADISTICAS DE RENDIMIENTO")
    print("=" * 50)
    
    # Contar archivos por tipo
    contadores = {"py": 0, "ipynb": 0, "xlsx": 0, "xls": 0, "json": 0}
    
    for root, dirs, files in os.walk("."):
        for file in files:
            extension = file.split(".")[-1].lower()
            if extension in contadores:
                contadores[extension] += 1
    
    for tipo, cantidad in contadores.items():
        print(f"{tipo.upper()}: {cantidad} archivos")

def pausa():
    """Pausa hasta que el usuario presione Enter"""
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
            elif opcion == "20":
                ejecutar_todo()
                pausa()
            elif opcion == "18":
                ejecutar_script("agrupar_datos_no_entregas_mejorado.py", "Agrupacion de datos NO ENTREGAS")
                pausa()
            elif opcion == "16":
                ejecutar_script("agrupar_datos_rep_plr.py", "Agrupacion de datos REP PLR")
                pausa()
            elif opcion == "12":
                ejecutar_script("agrupar_datos_vol_portafolio.py", "Agrupacion de datos VOL PORTAFOLIO")
                pausa()
            elif opcion == "15":
                ejecutar_script("unificar_datos_completos.py", "Unificacion de todos los datos")
                pausa()
            elif opcion == "6":
                ejecutar_script("", "Consolidar datos", "scripts/procesamiento/consolidar_datos.py")
                pausa()
            elif opcion == "7":
                ejecutar_script("", "Reporte PLR", "scripts/procesamiento/reporte_plr.py")
                pausa()
            elif opcion == "8":
                ejecutar_script("", "Volumen procesado familia", "scripts/procesamiento/volumen_procesado_familia.py")
                pausa()
            elif opcion == "9":
                ejecutar_script("", "Volumen no entregas", "scripts/procesamiento/vol_no_entregas.py")
                pausa()
            elif opcion == "10":
                ejecutar_script("", "Consolidar archivo PLR a Parquet", "scripts/procesamiento/consolidar_archivo_plr_2_parquet.py")
                pausa()
            elif opcion == "11":
                ejecutar_script("", "Automatizacion reportes SAP", "scripts/sap/automatizacion_reportes_sap.py")
                pausa()
            elif opcion == "4":
                ejecutar_script("", "Ejecutar proceso completo SAP", "scripts/procesamiento/ejecutar_proceso_completo.py")
                pausa()
            elif opcion == "13":
                ejecutar_submenu_sap_individuales()
            elif opcion == "14":
                ejecutar_script("", "Convertir XLS a XLSX", "scripts/sap/convertir_xls_a_xlsx.py")
                pausa()
            elif opcion == "5":
                ejecutar_script("", "Reordenar archivos Excel", "scripts/sap/reorder_lists_of_excel_files.py")
                pausa()
            elif opcion == "3":
                ejecutar_script("", "Consolidado ultimo archivo materiales", "scripts/procesamiento/consolidado_ultimo_archivo_materiales.py")
                pausa()
            elif opcion == "17":
                ejecutar_script("", "Consolidar zresguias", "scripts/procesamiento/consolidar_zresguias_plr.py")
                pausa()
            elif opcion == "2":
                ejecutar_script("", "Carga roadshow", "scripts/procesamiento/carga_roadshow.py")
                pausa()
            elif opcion == "19":
                ejecutar_script("", "Consolidar mes PLR", "scripts/procesamiento/consolidad_mes_plr.py")
                pausa()
            elif opcion == "1":
                ejecutar_notebook("scripts/notebooks/consolidar_zresguias_excel.ipynb", "Consolidar zresguias Excel")
                pausa()
            elif opcion == "21":
                buscar_notebooks()
                pausa()
            elif opcion == "22":
                verificar_rutas()
                pausa()
            elif opcion == "23":
                ver_resumen()
                pausa()
            elif opcion == "24":
                verificar_estructura()
                pausa()
            elif opcion == "25":
                ver_archivos_generados()
                pausa()
            elif opcion == "26":
                iniciar_web()
            elif opcion == "27":
                ver_informacion_sistema()
                pausa()
            elif opcion == "28":
                limpiar_archivos_temporales()
                pausa()
            elif opcion == "29":
                ver_estadisticas_rendimiento()
                pausa()
            elif opcion == "30":
                print("Sistema de favoritos - En desarrollo")
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
