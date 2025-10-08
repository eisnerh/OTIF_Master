import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import shutil
from datetime import datetime, timedelta

# Ejecutar script externo
def ejecutar_script(ruta_script):
    try:
        subprocess.run(["python", ruta_script], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo ejecutar el script:\n{ruta_script}\n\n{e}")

# Copiar y renombrar el último archivo TorreControl
def copiar_y_renombrar_archivo():
    carpeta = r"C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\10-octubre"
    try:
        archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))]
        if not archivos:
            messagebox.showinfo("Información", "No se encontraron archivos en la carpeta.")
            return

        archivo_mas_reciente = max(archivos, key=os.path.getmtime)
        nombre_original = os.path.basename(archivo_mas_reciente)

        fecha_nueva = (datetime.now() + timedelta(days=-1)).strftime("%d-%m-%Y")
        nuevo_nombre = f"torreControl_{fecha_nueva}.xlsx"
        nueva_ruta = os.path.join(carpeta, nuevo_nombre)

        shutil.copy2(archivo_mas_reciente, nueva_ruta)
        messagebox.showinfo("Éxito", f"Archivo copiado como:\n{nuevo_nombre}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error:\n{e}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Menú de Ejecución de Scripts")
ventana.geometry("800x600")

tk.Label(ventana, text="Menú Principal", font=("Arial", 16)).pack(pady=10)

# Función para crear botones en dos columnas
def crear_botones_en_columnas(frame, lista_scripts):
    col1 = tk.Frame(frame)
    col2 = tk.Frame(frame)
    col1.pack(side="left", fill="both", expand=True, padx=5)
    col2.pack(side="right", fill="both", expand=True, padx=5)

    mitad = len(lista_scripts) // 2 + len(lista_scripts) % 2
    for i, ruta in enumerate(lista_scripts):
        nombre = os.path.basename(ruta)
        boton = tk.Button(col1 if i < mitad else col2, text=nombre, command=lambda r=ruta: ejecutar_script(r))
        boton.pack(fill="x", pady=2)

# Scripts Generales
frame_generales = tk.LabelFrame(ventana, text="Scripts Generales", padx=10, pady=10)
frame_generales.pack(fill="both", expand=True, padx=20, pady=10)

scripts_generales = [
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\convertir_xls_a_xlsx.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\reorder_lists_of_excel_files.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\consolidado_ultimo_archivo_materiales.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\python ejecutar_proceso_completo.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\consolidar_zresguias_excel.ipynb",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\carga_roadshow.py"
]

crear_botones_en_columnas(frame_generales, scripts_generales)

# Botón adicional
tk.Button(frame_generales, text="Copiar y Renombrar Último Archivo TorreControl", command=copiar_y_renombrar_archivo).pack(fill="x", pady=5)

# SAP Scripting
frame_sap = tk.LabelFrame(ventana, text="SAP Scripting", padx=10, pady=10)
frame_sap.pack(fill="both", expand=True, padx=20, pady=10)

scripts_sap = [
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_dev_45.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_dev_74.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_dev_82.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_rep_plr.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\z_devo_alv.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zhbo.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zred.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zresguias.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zsd_incidencias.py"
]

crear_botones_en_columnas(frame_sap, scripts_sap)

ventana.mainloop()
