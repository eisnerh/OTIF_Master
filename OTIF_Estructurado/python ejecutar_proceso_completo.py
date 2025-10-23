import subprocess
import sys
import os
import time

def ejecutar_script(nombre_script):
    """
    Ejecuta un script de Python usando el mismo intérprete que este script.
    Se detiene si el script ejecutado devuelve un error.
    """
    # Construye la ruta completa al script para evitar problemas de directorio
    script_path = os.path.join(os.path.dirname(__file__), nombre_script)
    
    print(f"\n{'='*20}\nIniciando ejecución de: {nombre_script}\n{'='*20}")
    
    start_time = time.time()  # ⏲️ Record the start time
    
    try:
        # sys.executable es la ruta al intérprete de Python actual
        # check=True hace que se lance una excepción si el script falla
        proceso = subprocess.run(
            [sys.executable, script_path], 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        end_time = time.time()  # 🏁 Record the end time
        time_elapsed = end_time - start_time
        
        # Imprime la salida estándar del script ejecutado
        print("Salida del script:")
        print(proceso.stdout)
        
        # Si hubo alguna salida de error (incluso si no detuvo el script), la muestra
        if proceso.stderr:
            print("Salida de error del script (advertencias):")
            print(proceso.stderr)
            
        print(f"--- {nombre_script} finalizado exitosamente. ---")
        print(f"--- Tiempo de ejecución para {nombre_script}: {time_elapsed:.2f} segundos. ---")
        return True
        
    except FileNotFoundError:
        print(f"ERROR: El script '{nombre_script}' no fue encontrado en la ruta '{script_path}'.")
        return False
    except subprocess.CalledProcessError as e:
        # Este bloque se ejecuta si el script devuelve un código de salida de error
        print(f"ERROR: Falló la ejecución de {nombre_script}.")
        print("Código de retorno:", e.returncode)
        print("\n--- Salida Estándar ---")
        print(e.stdout)
        print("\n--- Salida de Error ---")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"Ocurrió un error inesperado al intentar ejecutar {nombre_script}: {e}")
        return False

def main():
    """
    Función principal que define el orden de ejecución de los scripts.
    """
    scripts_en_orden = [
        "volumen_procesado_familia.py",
        "vol_no_entregas.py",
        "reporte_plr.py",
        "consolidar_datos.py"
    ]
        
    print(">>> INICIANDO PROCESO DE CONSOLIDACIÓN DE DATOS <<<")
    
    total_start_time = time.time()  # ⏱️ Record the total process start time
    
    for script in scripts_en_orden:
        if not ejecutar_script(script):
            print(f"\n>>> El proceso se detuvo debido a un error en '{script}'. <<<")
            break
    else:
        total_end_time = time.time()  # 🛑 Record the total process end time
        total_time_elapsed = (total_end_time - total_start_time)/60  # Convert to minutes
        print(f"\n>>> Tiempo total del proceso: {total_time_elapsed:.2f} segundos. <<<")
        print("\n>>> TODOS LOS SCRIPTS SE HAN EJECUTADO CORRECTAMENTE. PROCESO FINALIZADO. <<<")

if __name__ == "__main__":
    main()