#!/usr/bin/env python3
"""
Script maestro que ejecuta todos los scripts SAP individuales
Sincronizado con los scripts individuales: y_dev_45, y_dev_74, y_dev_82, y_rep_plr, 
z_devo_alv, zred, zhbo, zsd_incidencias
"""

import subprocess
import sys
import os
import time
from datetime import datetime, timedelta

def ejecutar_script(script_name, script_path, *args):
    """
    Ejecuta un script Python específico y limpia la sesión SAP después
    
    Args:
        script_name (str): Nombre del script para logging
        script_path (str): Ruta al script
        *args: Argumentos adicionales para el script
    """
    print(f"Ejecutando {script_name}...")
    print("=" * 60)
    
    try:
        # Construir comando
        cmd = [sys.executable, script_path] + list(args)
        
        # Ejecutar script
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"OK: {script_name} ejecutado exitosamente")
            if result.stdout:
                print(f"Salida: {result.stdout.strip()}")
            
            # Limpiar sesión SAP después del script exitoso
            print("🧹 Limpiando sesión SAP...")
            try:
                cleanup_cmd = [sys.executable, "limpiar_sesion_sap.py"]
                cleanup_result = subprocess.run(cleanup_cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
                if cleanup_result.returncode == 0:
                    print("✅ Sesión SAP limpiada correctamente")
                else:
                    print(f"⚠️ Advertencia: Error limpiando sesión SAP: {cleanup_result.stderr.strip()}")
            except Exception as cleanup_error:
                print(f"⚠️ Advertencia: No se pudo limpiar la sesión SAP: {cleanup_error}")
            
            return True
        else:
            print(f"ERROR: {script_name}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            if result.stdout:
                print(f"Salida: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        print(f"ERROR ejecutando {script_name}: {e}")
        return False

def crear_carpetas_salida(base_output_path, scripts_config):
    """
    Crea las carpetas de salida necesarias para todos los scripts
    
    Args:
        base_output_path (str): Ruta base para las carpetas
        scripts_config (list): Lista de configuración de scripts
    """
    print("Verificando y creando carpetas de salida...")
    
    for script_config in scripts_config:
        output_path = os.path.join(base_output_path, script_config["output_subdir"])
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path, exist_ok=True)
                print(f"Carpeta creada: {output_path}")
            except Exception as e:
                print(f"ERROR: No se pudo crear la carpeta {output_path}: {e}")
        else:
            print(f"Carpeta ya existe: {output_path}")
    
    print("Verificacion de carpetas completada.")
    print("-" * 60)

def main():
    """
    Función principal que ejecuta todos los scripts SAP individuales
    """
    print("INICIANDO EJECUCION DE TODOS LOS SCRIPTS SAP")
    print("=" * 80)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Configuración de scripts con sus parámetros específicos
    scripts_config = [
        {
            "name": "Y_REP_PLR",
            "file": "y_rep_plr.py",
            "needs_date": True,
            "default_row": 11,
            "output_subdir": "rep_plr"
        },
        {
            "name": "Y_DEV_45", 
            "file": "y_dev_45.py",
            "needs_date": False,
            "default_row": 2,
            "output_subdir": "y_dev_45"
        },
        {
            "name": "Y_DEV_74",
            "file": "y_dev_74.py", 
            "needs_date": True,
            "default_row": 25,
            "output_subdir": "y_dev_74"
        },
        {
            "name": "Y_DEV_82",
            "file": "y_dev_82.py",
            "needs_date": False,
            "default_row": 2,
            "output_subdir": "y_dev_82"
        },
        {
            "name": "ZHBO",
            "file": "zhbo.py",
            "needs_date": True,
            "default_row": 1,
            "output_subdir": "zhbo"
        },
        {
            "name": "ZRED",
            "file": "zred.py",
            "needs_date": False,
            "default_row": 1,
            "output_subdir": "zred"
        },
        {
            "name": "Z_DEVO_ALV",
            "file": "z_devo_alv.py",
            "needs_date": False,
            "default_row": 1,
            "output_subdir": "z_devo_alv"
        },
        {
            "name": "ZSD_INCIDENCIAS",
            "file": "zsd_incidencias.py",
            "needs_date": False,
            "default_row": 12,
            "output_subdir": "zsd_incidencias"
        }
    ]
    
    # Procesar argumentos de línea de comandos
    custom_date = None
    base_output_path = "C:\\data"
    use_dynamic_date = True
    debug_mode = False
    custom_row = None
    connection_index = -1
    session_index = -1
    
    # Parsear argumentos
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i].lower()
        if arg == "dynamic":
            use_dynamic_date = True
            print("Usando fecha dinamica automatica")
        elif arg == "--date" and i + 1 < len(sys.argv):
            custom_date = sys.argv[i + 1]
            use_dynamic_date = False
            print(f"Usando fecha personalizada: {custom_date}")
            i += 1
        elif arg == "--output" and i + 1 < len(sys.argv):
            base_output_path = sys.argv[i + 1]
            print(f"Usando ruta base personalizada: {base_output_path}")
            i += 1
        elif arg == "--debug":
            debug_mode = True
            print("Modo debug activado")
        elif arg == "--row" and i + 1 < len(sys.argv):
            custom_row = int(sys.argv[i + 1])
            print(f"Usando fila personalizada: {custom_row}")
            i += 1
        elif arg == "--conn" and i + 1 < len(sys.argv):
            connection_index = int(sys.argv[i + 1])
            print(f"Usando conexion: {connection_index}")
            i += 1
        elif arg == "--sess" and i + 1 < len(sys.argv):
            session_index = int(sys.argv[i + 1])
            print(f"Usando sesion: {session_index}")
            i += 1
        i += 1
    
    # Calcular fecha para scripts que la necesitan
    if use_dynamic_date:
        today = datetime.now()
        weekday = today.weekday()
        if weekday == 0:  # Lunes
            date_str = (today - timedelta(days=2)).strftime("%d.%m.%Y")  # Sábado
            print("Logica: Es lunes - ejecutando reportes del sabado")
        else:
            date_str = (today - timedelta(days=1)).strftime("%d.%m.%Y")  # Ayer
            print("Logica: Ejecutando reportes de ayer")
    else:
        date_str = custom_date or (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")
    
    print(f"Fecha calculada: {date_str}")
    print(f"Ruta base: {base_output_path}")
    print(f"Debug: {'ON' if debug_mode else 'OFF'}")
    print(f"Conexion: {connection_index} (auto)" if connection_index == -1 else f"Conexion: {connection_index}")
    print(f"Sesion: {session_index} (auto)" if session_index == -1 else f"Sesion: {session_index}")
    
    # Crear carpetas de salida
    crear_carpetas_salida(base_output_path, scripts_config)
    
    results = {}
    total_scripts = len(scripts_config)
    
    print(f"\nEjecutando {total_scripts} scripts...")
    print("=" * 80)
    
    for i, script_config in enumerate(scripts_config, 1):
        script_name = script_config["name"]
        script_file = script_config["file"]
        print(f"\nProcesando {i}/{total_scripts}: {script_name}")
        
        # Preparar argumentos específicos para cada script
        output_path = os.path.join(base_output_path, script_config["output_subdir"])
        row_number = custom_row if custom_row is not None else script_config["default_row"]
        
        args = [
            "--output", output_path,
            "--row", str(row_number),
            "--conn", str(connection_index),
            "--sess", str(session_index)
        ]
        
        # Agregar fecha si el script la necesita
        if script_config["needs_date"]:
            args.extend(["--date", date_str])
        
        # Agregar debug si está activado
        if debug_mode:
            args.append("--debug")
        
        # Ejecutar script
        success = ejecutar_script(script_name, script_file, *args)
        results[script_name] = success
        
        # Pausa entre scripts
        if i < total_scripts:
            print(f"Esperando 3 segundos antes del siguiente script...")
            time.sleep(3)
    
    # Resumen final
    successful = sum(1 for success in results.values() if success)
    
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"Scripts exitosos: {successful}/{total_scripts}")
    print(f"Scripts fallidos: {total_scripts - successful}/{total_scripts}")
    print("\nDetalle por script:")
    
    for script_name, success in results.items():
        status = "OK" if success else "ERROR"
        print(f"  {status}: {script_name}")
    
    print(f"\nHora de finalizacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return successful == total_scripts

def mostrar_ayuda():
    """
    Muestra la ayuda del script
    """
    print("""
EJECUTAR TODOS LOS SCRIPTS SAP - AYUDA
======================================

Este script ejecuta todos los scripts SAP individuales de forma sincronizada:
- y_dev_45.py
- y_dev_74.py  
- y_dev_82.py
- y_rep_plr.py
- z_devo_alv.py
- zred.py
- zhbo.py
- zsd_incidencias.py

USO:
    python ejecutar_todos.py [OPCIONES]

OPCIONES:
    dynamic                    Usar fecha dinamica automatica (por defecto)
    --date DD.MM.YYYY         Usar fecha especifica para scripts que la requieren
    --output RUTA             Ruta base para archivos de salida (por defecto: C:\\data)
    --row NUMERO              Fila especifica para todos los scripts (sobrescribe valores por defecto)
    --conn NUMERO             Indice de conexion SAP (por defecto: -1 = auto)
    --sess NUMERO             Indice de sesion SAP (por defecto: -1 = auto)
    --debug                   Activar modo debug para todos los scripts
    --help, -h                Mostrar esta ayuda

EJEMPLOS:
    # Ejecucion basica con fecha dinamica
    python ejecutar_todos.py
    
    # Con fecha especifica
    python ejecutar_todos.py --date 15.01.2025
    
    # Con ruta personalizada y debug
    python ejecutar_todos.py --output "D:\\SAP_Data" --debug
    
    # Con parametros especificos
    python ejecutar_todos.py --date 15.01.2025 --row 5 --conn 0 --sess 0

CONFIGURACION POR SCRIPT:
    Y_REP_PLR:     Fila 11, requiere fecha, subdir: rep_plr
    Y_DEV_45:      Fila 2,  no requiere fecha, subdir: y_dev_45
    Y_DEV_74:      Fila 25, requiere fecha, subdir: y_dev_74
    Y_DEV_82:      Fila 2,  no requiere fecha, subdir: y_dev_82
    ZHBO:          Fila 1,  requiere fecha, subdir: zhbo
    ZRED:          Fila 1,  no requiere fecha, subdir: zred
    Z_DEVO_ALV:    Fila 1,  no requiere fecha, subdir: z_devo_alv
    ZSD_INCIDENCIAS: Fila 12, no requiere fecha, subdir: zsd_incidencias

CARPETAS:
    El script crea automaticamente las carpetas de salida si no existen.

REQUISITOS:
    - SAP Logon abierto y sesion activa
    - SAP GUI Scripting habilitado
    - pywin32 instalado (pip install pywin32)
    - Todos los scripts individuales en el mismo directorio
""")

if __name__ == "__main__":
    try:
        # Verificar si se solicita ayuda
        if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
            mostrar_ayuda()
            sys.exit(0)
        
        success = main()
        if success:
            print("\nTodos los scripts ejecutados exitosamente")
            sys.exit(0)
        else:
            print("\nAlgunos scripts fallaron")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
