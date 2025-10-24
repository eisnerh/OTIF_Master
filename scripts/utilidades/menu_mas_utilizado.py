import subprocess
import os

scripts_generales = {
    "Convertir XLS a XLSX": "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/to_xlsx/convertir_xls_a_xlsx.py",
    "Reordenar Archivos Excel": "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/to_xlsx/reorder_lists_of_excel_files.py",
    "Consolidar Materiales": "OTIF_Estructurado/ULTIMO_ARCHIVO/consolidado_ultimo_archivo_materiales.py",
    "Proceso Completo": "OTIF_Estructurado/python ejecutar_proceso_completo.py",
    "Consolidar Resguías": "scripts/notebooks/consolidar_zresguias_excel.ipynb",
    "Carga Roadshow": "OTIF_Estructurado/ULTIMO_ARCHIVO/carga_roadshow.py"
}

sap_scripting = {
    "y_dev_45.py": "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_45.py",
    "y_dev_74.py": "OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/scripts_individuales/y_dev_74.py"
}

def mostrar_menu():
    print("\n--- Menú de Scripts Generales ---")
    for i, nombre in enumerate(scripts_generales.keys(), start=1):
        print(f"{i}. {nombre}")
    print("0. Salir")

def ejecutar_script(opcion):
    nombre = list(scripts_generales.keys())[opcion - 1]
    ruta = scripts_generales[nombre]
    print(f"\nEjecutando: {nombre}")
    try:
        resultado = subprocess.run(["python", ruta], check=True, capture_output=True, text=True)
        print(f"Completado: {nombre}")
        print("Salida:\n", resultado.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {nombre}")
        print("Código de salida:", e.returncode)
        print("Salida estándar:\n", e.stdout)
        print("Errores:\n", e.stderr)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    while True:
        mostrar_menu()
        try:
            opcion = int(input("\nSelecciona una opción: "))
            if opcion == 0:
                print("Saliendo del menú.")
                break
            elif 1 <= opcion <= len(scripts_generales):
                ejecutar_script(opcion)
            else:
                print("Opción inválida. Intenta de nuevo.")
        except ValueError:
            print("Entrada no válida. Ingresa un número.")