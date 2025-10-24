#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MENU COMPLETO OTIF - VERSION CMD
Sistema de menu completo con todas las funcionalidades del proyecto OTIF

Uso: python menu_completo.py
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
    print("           SISTEMA OTIF MASTER - MENU COMPLETO")
    print("="*70)
    print()

def mostrar_menu_principal():
    """Muestra el menu principal completo"""
    print("PROCESAMIENTO DE DATOS OTIF:")
    print("  1. Ejecutar TODO el procesamiento OTIF")
    print("  2. Procesar solo NO ENTREGAS")
    print("  3. Procesar solo REP PLR")
    print("  4. Procesar solo VOL PORTAFOLIO")
    print("  5. Unificar todos los datos")
    print()
    print("SCRIPTS ESTRUCTURADOS:")
    print("  6. Scripts estructurados (Submenu)")
    print()
    print("AUTOMATIZACION SAP:")
    print("  7. Automatizacion reportes SAP")
    print("  8. Ejecutar proceso completo SAP")
    print("  9. Scripts individuales SAP (Submenu)")
    print("  10. Convertir XLS a XLSX")
    print("  11. Reordenar archivos Excel")
    print()
    print("SCRIPTS ULTIMO ARCHIVO:")
    print("  12. Scripts ultimo archivo (Submenu)")
    print()
    print("JUPYTER NOTEBOOKS:")
    print("  13. Ejecutar notebook consolidar zresguias")
    print("  14. Buscar notebooks disponibles")
    print()
    print("VERIFICACION Y MONITOREO:")
    print("  15. Verificar estado de rutas")
    print("  16. Ver resumen de procesamiento")
    print("  17. Verificar estructura del sistema")
    print("  18. Ver archivos generados")
    print()
    print("INTERFAZ WEB:")
    print("  19. Iniciar aplicacion web")
    print()
    print("HERRAMIENTAS:")
    print("  20. Ver informacion del sistema")
    print("  21. Limpiar archivos temporales")
    print("  22. Ver estadisticas de rendimiento")
    print("  23. Menu mas utilizado")
    print()
    print("FAVORITOS:")
    print("  24. Gestion de favoritos (Submenu)")
    print()
    print("SALIR:")
    print("  0. Salir del sistema")
    print("=" * 70)

def ejecutar_script(script_name, descripcion="", ruta_completa=None):
    """Ejecuta un script y muestra el progreso"""
    print(f"EJECUTANDO: {descripcion or script_name}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Determinar la ruta del script
        if ruta_completa:
            script_path = ruta_completa
        else:
            script_path = f"scripts/{script_name}"
        
        # Verificar si el script existe
        if not os.path.exists(script_path):
            print(f"ERROR: No se encontro el script {script_path}")
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

def ejecutar_notebook(notebook_path, descripcion=""):
    """Ejecuta un notebook de Jupyter"""
    print(f"EJECUTANDO NOTEBOOK: {descripcion or notebook_path}")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Verificar si el notebook existe
        if not os.path.exists(notebook_path):
            print(f"ERROR: No se encontro el notebook {notebook_path}")
            return False
        
        # Verificar si jupyter está instalado
        try:
            subprocess.run(["jupyter", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: Jupyter no esta instalado o no esta en el PATH")
            print("Instala jupyter con: pip install jupyter")
            return False
        
        # Ejecutar el notebook usando nbconvert
        result = subprocess.run(
            ["jupyter", "nbconvert", "--execute", "--to", "notebook", "--inplace", notebook_path],
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

def ejecutar_scripts_estructurados():
    """Ejecuta scripts de la carpeta OTIF_Estructurado"""
    print("SCRIPTS ESTRUCTURADOS")
    print("=" * 40)
    
    scripts = [
        ("OTIF_Estructurado/consolidar_datos.py", "Consolidar datos"),
        ("OTIF_Estructurado/reporte_plr.py", "Reporte PLR"),
        ("OTIF_Estructurado/vol_no_entregas.py", "Volumen no entregas"),
        ("OTIF_Estructurado/volumen_procesado_familia.py", "Volumen procesado familia"),
        ("OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_archivo_plr_2_parquet.py", "Consolidar archivo PLR a Parquet")
    ]
    
    for script, descripcion in scripts:
        print(f"\nEjecutando: {descripcion}")
        ejecutar_script("", descripcion, script)
        time.sleep(1)

def ejecutar_automatizacion_sap():
    """Ejecuta scripts de automatizacion SAP"""
    print("AUTOMATIZACION SAP")
    print("=" * 40)
    
    scripts = [
        ("OTIF_Estructurado/SAP_SCRIPTING/automatizacion_reportes_sap.py", "Automatizacion reportes SAP"),
        ("OTIF_Estructurado/SAP_SCRIPTING/ejecutar_diario.py", "Ejecutar diario SAP"),
        ("OTIF_Estructurado/SAP_SCRIPTING/instalar_automatizacion.py", "Instalar automatizacion SAP")
    ]
    
    for script, descripcion in scripts:
        print(f"\nEjecutando: {descripcion}")
        ejecutar_script("", descripcion, script)
        time.sleep(1)

def ejecutar_scripts_individuales_sap():
    """Ejecuta scripts individuales de SAP"""
    print("SCRIPTS INDIVIDUALES SAP")
    print("=" * 40)
    
    scripts = [
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_45.py", "Y_DEV_45"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_74.py", "Y_DEV_74"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_82.py", "Y_DEV_82"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_rep_plr.py", "Y_REP_PLR"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/z_devo_alv.py", "Z_DEVO_ALV"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zhbo.py", "ZHBO"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zred.py", "ZRED"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zresguias.py", "ZRESGUIAS"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zsd_incidencias.py", "ZSD_INCIDENCIAS")
    ]
    
    for script, descripcion in scripts:
        print(f"\nEjecutando: {descripcion}")
        ejecutar_script("", descripcion, script)
        time.sleep(1)

def ejecutar_conversion_xls():
    """Ejecuta scripts de conversion XLS a XLSX"""
    print("CONVERSION XLS A XLSX")
    print("=" * 40)
    
    scripts = [
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/to_xlsx/convertir_xls_a_xlsx.py", "Convertir XLS a XLSX"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/to_xlsx/ejecutar_conversion.py", "Ejecutar conversion"),
        ("OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/to_xlsx/reorder_lists_of_excel_files.py", "Reordenar archivos Excel")
    ]
    
    for script, descripcion in scripts:
        print(f"\nEjecutando: {descripcion}")
        ejecutar_script("", descripcion, script)
        time.sleep(1)

def ejecutar_ultimo_archivo():
    """Ejecuta scripts de la carpeta ULTIMO_ARCHIVO"""
    print("SCRIPTS ULTIMO ARCHIVO")
    print("=" * 40)
    
    scripts = [
        ("OTIF_Estructurado/ULTIMO_ARCHIVO/consolidado_ultimo_archivo_materiales.py", "Consolidado ultimo archivo materiales"),
        ("OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_zresguias_plr.py", "Consolidar zresguias PLR"),
        ("OTIF_Estructurado/ULTIMO_ARCHIVO/carga_roadshow.py", "Carga roadshow"),
        ("OTIF_Estructurado/ULTIMO_ARCHIVO/consolidad_mes_plr.py", "Consolidar mes PLR")
    ]
    
    for script, descripcion in scripts:
        print(f"\nEjecutando: {descripcion}")
        ejecutar_script("", descripcion, script)
        time.sleep(1)

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
        ("Data/Vol_Portafolio/Output", "Archivos Vol Portafolio"),
        ("OTIF_Estructurado/SAP_SCRIPTING/data", "Datos SAP"),
        ("OTIF_Estructurado/ULTIMO_ARCHIVO", "Ultimo archivo")
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
    
    # Scripts estructurados
    print("SCRIPTS ESTRUCTURADOS:")
    if os.path.exists("OTIF_Estructurado"):
        print("   - consolidar_datos.py")
        print("   - reporte_plr.py")
        print("   - vol_no_entregas.py")
        print("   - volumen_procesado_familia.py")
    
    print()
    
    # Scripts SAP
    print("SCRIPTS SAP:")
    if os.path.exists("OTIF_Estructurado/SAP_SCRIPTING"):
        print("   - automatizacion_reportes_sap.py")
        print("   - ejecutar_diario.py")
        print("   - instalar_automatizacion.py")
    
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
    print("   - Automatizacion SAP: 10-15 minutos")
    print("   - Scripts individuales: 2-5 minutos cada uno")
    print()
    
    print("REQUISITOS DEL SISTEMA:")
    print("   - RAM: Minimo 8 GB (recomendado 16 GB)")
    print("   - CPU: Minimo 4 nucleos")
    print("   - Disco: Suficiente espacio para archivos temporales")
    print("   - SAP: Conexion activa para scripts SAP")
    print()
    
    print("ARCHIVOS PRINCIPALES GENERADOS:")
    print("   - rep_plr.parquet")
    print("   - no_entregas.parquet")
    print("   - vol_portafolio.parquet")
    print("   - datos_completos_con_no_entregas.parquet")
    print("   - Archivos Excel de SAP")
    print("   - Archivos de consolidacion")

def ejecutar_menu_mas_utilizado():
    """Ejecuta el menu mas utilizado"""
    print("MENU MAS UTILIZADO")
    print("=" * 40)
    
    try:
        if os.path.exists("scripts/menu_mas_utilizado.py"):
            subprocess.run([sys.executable, "scripts/menu_mas_utilizado.py"])
        else:
            print("Script menu_mas_utilizado.py no encontrado")
    except Exception as e:
        print(f"ERROR: {str(e)}")

def buscar_notebooks():
    """Busca y lista todos los notebooks de Jupyter disponibles"""
    print("BUSCANDO NOTEBOOKS DE JUPYTER")
    print("=" * 40)
    
    notebooks_encontrados = []
    
    # Buscar en el directorio actual y subdirectorios
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.ipynb'):
                ruta_completa = os.path.join(root, file)
                notebooks_encontrados.append(ruta_completa)
    
    if notebooks_encontrados:
        print(f"Se encontraron {len(notebooks_encontrados)} notebook(s):")
        for i, notebook in enumerate(notebooks_encontrados, 1):
            print(f"  {i}. {notebook}")
        
        print("\nPara ejecutar un notebook, usa la opcion 20 del menu principal")
    else:
        print("No se encontraron notebooks de Jupyter (.ipynb)")
    
    return notebooks_encontrados

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
                ejecutar_script("", "Y_DEV_45", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_45.py")
                pausa()
            elif opcion == "2":
                ejecutar_script("", "Y_DEV_74", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_74.py")
                pausa()
            elif opcion == "3":
                ejecutar_script("", "Y_DEV_82", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_82.py")
                pausa()
            elif opcion == "4":
                ejecutar_script("", "Y_REP_PLR", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_rep_plr.py")
                pausa()
            elif opcion == "5":
                ejecutar_script("", "Z_DEVO_ALV", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/z_devo_alv.py")
                pausa()
            elif opcion == "6":
                ejecutar_script("", "ZHBO", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zhbo.py")
                pausa()
            elif opcion == "7":
                ejecutar_script("", "ZRED", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zred.py")
                pausa()
            elif opcion == "8":
                ejecutar_script("", "ZRESGUIAS", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zresguias.py")
                pausa()
            elif opcion == "9":
                ejecutar_script("", "ZSD_INCIDENCIAS", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/zsd_incidencias.py")
                pausa()
            elif opcion == "10":
                ejecutar_scripts_individuales_sap()
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

def mostrar_submenu_estructurados():
    """Muestra el submenu de scripts estructurados"""
    print("SCRIPTS ESTRUCTURADOS")
    print("=" * 40)
    print("  1. Consolidar datos")
    print("  2. Reporte PLR")
    print("  3. Volumen procesado familia")
    print("  4. Volumen no entregas")
    print("  5. Consolidar archivo PLR a Parquet")
    print("  6. Ejecutar TODOS los scripts estructurados")
    print("  0. Volver al menu principal")
    print("=" * 40)

def ejecutar_submenu_estructurados():
    """Ejecuta el submenu de scripts estructurados"""
    while True:
        limpiar_pantalla()
        mostrar_submenu_estructurados()
        
        try:
            opcion = input("\nSelecciona una opcion: ").strip()
            
            if opcion == "0":
                break
            elif opcion == "1":
                ejecutar_script("", "Consolidar datos", "OTIF_Estructurado/consolidar_datos.py")
                pausa()
            elif opcion == "2":
                ejecutar_script("", "Reporte PLR", "OTIF_Estructurado/reporte_plr.py")
                pausa()
            elif opcion == "3":
                ejecutar_script("", "Volumen procesado familia", "OTIF_Estructurado/volumen_procesado_familia.py")
                pausa()
            elif opcion == "4":
                ejecutar_script("", "Volumen no entregas", "OTIF_Estructurado/vol_no_entregas.py")
                pausa()
            elif opcion == "5":
                ejecutar_script("", "Consolidar archivo PLR a Parquet", "OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_archivo_plr_2_parquet.py")
                pausa()
            elif opcion == "6":
                ejecutar_scripts_estructurados()
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

def mostrar_submenu_ultimo_archivo():
    """Muestra el submenu de scripts ultimo archivo"""
    print("SCRIPTS ULTIMO ARCHIVO")
    print("=" * 40)
    print("  1. Consolidado ultimo archivo materiales")
    print("  2. Consolidar zresguias")
    print("  3. Carga roadshow")
    print("  4. Consolidar mes PLR")
    print("  5. Ejecutar TODOS los scripts ultimo archivo")
    print("  0. Volver al menu principal")
    print("=" * 40)

def ejecutar_submenu_ultimo_archivo():
    """Ejecuta el submenu de scripts ultimo archivo"""
    while True:
        limpiar_pantalla()
        mostrar_submenu_ultimo_archivo()
        
        try:
            opcion = input("\nSelecciona una opcion: ").strip()
            
            if opcion == "0":
                break
            elif opcion == "1":
                ejecutar_script("", "Consolidado ultimo archivo materiales", "OTIF_Estructurado/ULTIMO_ARCHIVO/consolidado_ultimo_archivo_materiales.py")
                pausa()
            elif opcion == "2":
                ejecutar_script("", "Consolidar zresguias", "OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_zresguias_plr.py")
                pausa()
            elif opcion == "3":
                ejecutar_script("", "Carga roadshow", "OTIF_Estructurado/ULTIMO_ARCHIVO/carga_roadshow.py")
                pausa()
            elif opcion == "4":
                ejecutar_script("", "Consolidar mes PLR", "OTIF_Estructurado/ULTIMO_ARCHIVO/consolidad_mes_plr.py")
                pausa()
            elif opcion == "5":
                ejecutar_ultimo_archivo()
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

def pausa():
    """Pausa para que el usuario pueda leer la informacion"""
    input("\nPresiona Enter para continuar...")

def cargar_favoritos():
    """Carga los favoritos desde el archivo JSON"""
    try:
        if os.path.exists("favoritos.json"):
            with open("favoritos.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"scripts": [], "notebooks": [], "carpetas": []}
    except Exception as e:
        print(f"ERROR al cargar favoritos: {str(e)}")
        return {"scripts": [], "notebooks": [], "carpetas": []}

def guardar_favoritos(favoritos):
    """Guarda los favoritos en el archivo JSON"""
    try:
        with open("favoritos.json", 'w', encoding='utf-8') as f:
            json.dump(favoritos, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"ERROR al guardar favoritos: {str(e)}")
        return False

def agregar_favorito(tipo, nombre, ruta, descripcion=""):
    """Agrega un favorito"""
    favoritos = cargar_favoritos()
    
    # Verificar si ya existe
    for item in favoritos[tipo]:
        if item["ruta"] == ruta:
            print("Este favorito ya existe")
            return False
    
    # Agregar nuevo favorito
    nuevo_favorito = {
        "nombre": nombre,
        "ruta": ruta,
        "descripcion": descripcion,
        "fecha_agregado": datetime.now().isoformat()
    }
    
    favoritos[tipo].append(nuevo_favorito)
    
    if guardar_favoritos(favoritos):
        print(f"Favorito agregado: {nombre}")
        return True
    else:
        print("ERROR al agregar favorito")
        return False

def mostrar_favoritos():
    """Muestra todos los favoritos"""
    favoritos = cargar_favoritos()
    
    print("MIS FAVORITOS")
    print("=" * 50)
    
    if favoritos["scripts"]:
        print("\nSCRIPTS FAVORITOS:")
        for i, script in enumerate(favoritos["scripts"], 1):
            print(f"  {i}. {script['nombre']}")
            print(f"     Ruta: {script['ruta']}")
            print(f"     Descripcion: {script['descripcion']}")
            print(f"     Agregado: {script['fecha_agregado']}")
            print()
    
    if favoritos["notebooks"]:
        print("\nNOTEBOOKS FAVORITOS:")
        for i, notebook in enumerate(favoritos["notebooks"], 1):
            print(f"  {i}. {notebook['nombre']}")
            print(f"     Ruta: {notebook['ruta']}")
            print(f"     Descripcion: {notebook['descripcion']}")
            print(f"     Agregado: {notebook['fecha_agregado']}")
            print()
    
    if favoritos["carpetas"]:
        print("\nCARPETAS FAVORITAS:")
        for i, carpeta in enumerate(favoritos["carpetas"], 1):
            print(f"  {i}. {carpeta['nombre']}")
            print(f"     Ruta: {carpeta['ruta']}")
            print(f"     Descripcion: {carpeta['descripcion']}")
            print(f"     Agregado: {carpeta['fecha_agregado']}")
            print()
    
    if not favoritos["scripts"] and not favoritos["notebooks"] and not favoritos["carpetas"]:
        print("No tienes favoritos guardados")
        print("Usa la opcion 'Agregar favorito' para guardar tus scripts preferidos")

def mostrar_menu_favoritos():
    """Muestra el menu de favoritos"""
    print("GESTION DE FAVORITOS")
    print("=" * 40)
    print("  1. Ver todos los favoritos")
    print("  2. Agregar script favorito")
    print("  3. Agregar notebook favorito")
    print("  4. Agregar carpeta favorita")
    print("  5. Ejecutar favorito")
    print("  6. Eliminar favorito")
    print("  7. Buscar scripts disponibles")
    print("  0. Volver al menu principal")
    print("=" * 40)

def ejecutar_menu_favoritos():
    """Ejecuta el menu de favoritos"""
    while True:
        limpiar_pantalla()
        mostrar_menu_favoritos()
        
        try:
            opcion = input("\nSelecciona una opcion: ").strip()
            
            if opcion == "0":
                break
            elif opcion == "1":
                mostrar_favoritos()
                pausa()
            elif opcion == "2":
                agregar_script_favorito()
            elif opcion == "3":
                agregar_notebook_favorito()
            elif opcion == "4":
                agregar_carpeta_favorita()
            elif opcion == "5":
                ejecutar_favorito()
            elif opcion == "6":
                eliminar_favorito()
            elif opcion == "7":
                buscar_scripts_disponibles()
            else:
                print("Opcion invalida. Por favor selecciona una opcion valida.")
                pausa()
                
        except KeyboardInterrupt:
            print("\n\nMenu de favoritos interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\nERROR inesperado: {str(e)}")
            pausa()

def agregar_script_favorito():
    """Agrega un script a favoritos"""
    print("AGREGAR SCRIPT FAVORITO")
    print("=" * 40)
    
    # Buscar scripts disponibles
    scripts_disponibles = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.py') and not file.startswith('menu_'):
                ruta_completa = os.path.join(root, file)
                scripts_disponibles.append(ruta_completa)
    
    if not scripts_disponibles:
        print("No se encontraron scripts disponibles")
        pausa()
        return
    
    print("Scripts disponibles:")
    for i, script in enumerate(scripts_disponibles[:20], 1):  # Mostrar solo los primeros 20
        print(f"  {i}. {script}")
    
    try:
        opcion = int(input("\nSelecciona el numero del script (0 para cancelar): "))
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(scripts_disponibles):
            script_seleccionado = scripts_disponibles[opcion - 1]
            nombre = input("Nombre para el favorito: ").strip()
            descripcion = input("Descripcion (opcional): ").strip()
            
            if agregar_favorito("scripts", nombre, script_seleccionado, descripcion):
                print("Script agregado a favoritos exitosamente")
            else:
                print("ERROR al agregar script a favoritos")
        else:
            print("Opcion invalida")
    except ValueError:
        print("Por favor ingresa un numero valido")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    pausa()

def agregar_notebook_favorito():
    """Agrega un notebook a favoritos"""
    print("AGREGAR NOTEBOOK FAVORITO")
    print("=" * 40)
    
    # Buscar notebooks disponibles
    notebooks_disponibles = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.ipynb'):
                ruta_completa = os.path.join(root, file)
                notebooks_disponibles.append(ruta_completa)
    
    if not notebooks_disponibles:
        print("No se encontraron notebooks disponibles")
        pausa()
        return
    
    print("Notebooks disponibles:")
    for i, notebook in enumerate(notebooks_disponibles, 1):
        print(f"  {i}. {notebook}")
    
    try:
        opcion = int(input("\nSelecciona el numero del notebook (0 para cancelar): "))
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(notebooks_disponibles):
            notebook_seleccionado = notebooks_disponibles[opcion - 1]
            nombre = input("Nombre para el favorito: ").strip()
            descripcion = input("Descripcion (opcional): ").strip()
            
            if agregar_favorito("notebooks", nombre, notebook_seleccionado, descripcion):
                print("Notebook agregado a favoritos exitosamente")
            else:
                print("ERROR al agregar notebook a favoritos")
        else:
            print("Opcion invalida")
    except ValueError:
        print("Por favor ingresa un numero valido")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    pausa()

def agregar_carpeta_favorita():
    """Agrega una carpeta a favoritos"""
    print("AGREGAR CARPETA FAVORITA")
    print("=" * 40)
    
    ruta = input("Ruta de la carpeta: ").strip()
    if not os.path.exists(ruta):
        print("La carpeta no existe")
        pausa()
        return
    
    nombre = input("Nombre para el favorito: ").strip()
    descripcion = input("Descripcion (opcional): ").strip()
    
    if agregar_favorito("carpetas", nombre, ruta, descripcion):
        print("Carpeta agregada a favoritos exitosamente")
    else:
        print("ERROR al agregar carpeta a favoritos")
    
    pausa()

def ejecutar_favorito():
    """Ejecuta un favorito"""
    favoritos = cargar_favoritos()
    
    print("EJECUTAR FAVORITO")
    print("=" * 40)
    
    todos_favoritos = []
    
    # Combinar todos los favoritos
    for i, script in enumerate(favoritos["scripts"], 1):
        todos_favoritos.append(("script", i, script))
    
    for i, notebook in enumerate(favoritos["notebooks"], 1):
        todos_favoritos.append(("notebook", i, notebook))
    
    for i, carpeta in enumerate(favoritos["carpetas"], 1):
        todos_favoritos.append(("carpeta", i, carpeta))
    
    if not todos_favoritos:
        print("No tienes favoritos guardados")
        pausa()
        return
    
    print("Favoritos disponibles:")
    for i, (tipo, _, item) in enumerate(todos_favoritos, 1):
        print(f"  {i}. [{tipo.upper()}] {item['nombre']}")
        print(f"     {item['descripcion']}")
    
    try:
        opcion = int(input("\nSelecciona el numero del favorito (0 para cancelar): "))
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(todos_favoritos):
            tipo, _, item = todos_favoritos[opcion - 1]
            
            if tipo == "script":
                ejecutar_script("", item['nombre'], item['ruta'])
            elif tipo == "notebook":
                ejecutar_notebook(item['ruta'], item['nombre'])
            elif tipo == "carpeta":
                print(f"Abriendo carpeta: {item['ruta']}")
                os.startfile(item['ruta'])  # Abrir carpeta en explorador
        else:
            print("Opcion invalida")
    except ValueError:
        print("Por favor ingresa un numero valido")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    pausa()

def eliminar_favorito():
    """Elimina un favorito"""
    favoritos = cargar_favoritos()
    
    print("ELIMINAR FAVORITO")
    print("=" * 40)
    
    todos_favoritos = []
    
    # Combinar todos los favoritos
    for i, script in enumerate(favoritos["scripts"]):
        todos_favoritos.append(("scripts", i, script))
    
    for i, notebook in enumerate(favoritos["notebooks"]):
        todos_favoritos.append(("notebooks", i, notebook))
    
    for i, carpeta in enumerate(favoritos["carpetas"]):
        todos_favoritos.append(("carpetas", i, carpeta))
    
    if not todos_favoritos:
        print("No tienes favoritos guardados")
        pausa()
        return
    
    print("Favoritos disponibles:")
    for i, (tipo, _, item) in enumerate(todos_favoritos, 1):
        print(f"  {i}. [{tipo.upper()}] {item['nombre']}")
        print(f"     {item['descripcion']}")
    
    try:
        opcion = int(input("\nSelecciona el numero del favorito a eliminar (0 para cancelar): "))
        if opcion == 0:
            return
        
        if 1 <= opcion <= len(todos_favoritos):
            tipo, indice, item = todos_favoritos[opcion - 1]
            
            # Eliminar del array
            favoritos[tipo].pop(indice)
            
            if guardar_favoritos(favoritos):
                print(f"Favorito eliminado: {item['nombre']}")
            else:
                print("ERROR al eliminar favorito")
        else:
            print("Opcion invalida")
    except ValueError:
        print("Por favor ingresa un numero valido")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    
    pausa()

def buscar_scripts_disponibles():
    """Busca y muestra scripts disponibles en el sistema"""
    print("BUSCAR SCRIPTS DISPONIBLES")
    print("=" * 40)
    
    scripts_encontrados = []
    
    # Buscar scripts Python
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.py') and not file.startswith('menu_'):
                ruta_completa = os.path.join(root, file)
                tamaño = os.path.getsize(ruta_completa)
                scripts_encontrados.append((ruta_completa, tamaño))
    
    # Buscar notebooks
    notebooks_encontrados = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.ipynb'):
                ruta_completa = os.path.join(root, file)
                tamaño = os.path.getsize(ruta_completa)
                notebooks_encontrados.append((ruta_completa, tamaño))
    
    print(f"SCRIPTS PYTHON ENCONTRADOS: {len(scripts_encontrados)}")
    for script, tamaño in scripts_encontrados[:10]:  # Mostrar solo los primeros 10
        tamaño_kb = tamaño / 1024
        print(f"  - {script} ({tamaño_kb:.1f} KB)")
    
    if len(scripts_encontrados) > 10:
        print(f"  ... y {len(scripts_encontrados) - 10} mas")
    
    print(f"\nNOTEBOOKS ENCONTRADOS: {len(notebooks_encontrados)}")
    for notebook, tamaño in notebooks_encontrados:
        tamaño_kb = tamaño / 1024
        print(f"  - {notebook} ({tamaño_kb:.1f} KB)")
    
    pausa()

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
                ejecutar_submenu_estructurados()
            elif opcion == "7":
                ejecutar_automatizacion_sap()
                pausa()
            elif opcion == "8":
                ejecutar_script("", "Ejecutar proceso completo SAP", "OTIF_Estructurado/python ejecutar_proceso_completo.py")
                pausa()
            elif opcion == "9":
                ejecutar_submenu_sap_individuales()
            elif opcion == "10":
                ejecutar_conversion_xls()
                pausa()
            elif opcion == "11":
                ejecutar_script("", "Reordenar archivos Excel", "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/to_xlsx/reorder_lists_of_excel_files.py")
                pausa()
            elif opcion == "12":
                ejecutar_submenu_ultimo_archivo()
            elif opcion == "13":
                ejecutar_notebook("OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_zresguias_excel.ipynb", "Consolidar zresguias Excel")
                pausa()
            elif opcion == "14":
                buscar_notebooks()
                pausa()
            elif opcion == "15":
                verificar_rutas()
                pausa()
            elif opcion == "16":
                ver_resumen()
                pausa()
            elif opcion == "17":
                verificar_estructura()
                pausa()
            elif opcion == "18":
                ver_archivos_generados()
                pausa()
            elif opcion == "19":
                iniciar_web()
            elif opcion == "20":
                ver_informacion_sistema()
                pausa()
            elif opcion == "21":
                limpiar_archivos_temporales()
                pausa()
            elif opcion == "22":
                ver_estadisticas_rendimiento()
                pausa()
            elif opcion == "23":
                ejecutar_menu_mas_utilizado()
            elif opcion == "24":
                ejecutar_menu_favoritos()
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
