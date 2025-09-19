#!/usr/bin/env python3
"""
Script simple sin emojis para ejecutar la secuencia:
1. loguearse.py
2. nuevo_rep_plr.py  
3. procesar_sap_especial.py
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def ejecutar_script(nombre_script, descripcion):
    """
    Ejecuta un script y muestra el resultado
    """
    print(f"\nEjecutando: {descripcion}")
    print("-" * 60)
    
    try:
        # Ejecutar el script
        result = subprocess.run([sys.executable, nombre_script], 
                              cwd=os.path.dirname(__file__),
                              capture_output=True, 
                              text=True,
                              encoding='utf-8')
        
        # Mostrar salida
        if result.stdout:
            print("Salida:")
            print(result.stdout)
        
        if result.stderr:
            print("Errores/Advertencias:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"EXITOSO - {descripcion}")
            return True
        else:
            print(f"FALLO - {descripcion} (codigo: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"Error ejecutando {nombre_script}: {e}")
        return False

def main():
    """
    Función principal
    """
    print("EJECUTANDO SECUENCIA DE SCRIPTS")
    print("=" * 80)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Lista de scripts a ejecutar
    scripts = [
        ("loguearse.py", "Iniciando sesion en SAP"),
        ("nuevo_rep_plr.py", "Descargando reporte desde SAP"),
        ("procesar_sap_especial.py", "Procesando archivo para Power BI")
    ]
    
    resultados = []
    
    # Ejecutar cada script
    for script, descripcion in scripts:
        if os.path.exists(script):
            resultado = ejecutar_script(script, descripcion)
            resultados.append((script, resultado))
            
            # Esperar entre scripts
            if resultado:
                print(f"\nEsperando 3 segundos antes del siguiente script...")
                time.sleep(3)
        else:
            print(f"Script no encontrado: {script}")
            resultados.append((script, False))
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE EJECUCION")
    print("=" * 80)
    
    exitosos = 0
    for script, resultado in resultados:
        estado = "EXITOSO" if resultado else "FALLO"
        print(f"{estado} - {script}")
        if resultado:
            exitosos += 1
    
    print(f"\nResultado: {exitosos}/{len(resultados)} scripts ejecutados exitosamente")
    
    if exitosos == len(resultados):
        print("\nTODOS LOS SCRIPTS SE EJECUTARON EXITOSAMENTE")
        print("Verifica los archivos en: C:\\Data\\Nite")
    else:
        print(f"\n{len(resultados) - exitosos} script(s) fallaron")
    
    print(f"Hora de finalizacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return exitosos == len(resultados)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
