import os
import shutil
import re
from datetime import datetime, timedelta

# Diccionario meses_en -> meses_es
meses_es = {
    'January': 'enero',    'February': 'febrero', 'March': 'marzo',
    'April': 'abril',      'May': 'mayo',         'June': 'junio',
    'July': 'julio',       'August': 'agosto',    'September': 'septiembre',
    'October': 'octubre',  'November': 'noviembre','December': 'diciembre'
}

# Fecha de ayer en formato dd-mm-YYYY
ayer = (datetime.now() - timedelta(days=1)).strftime('%d-%m-%Y')

# Carpeta del mes actual (ej: "11-noviembre")
mes_num = datetime.now().strftime('%m')
mes_nombre_en = datetime.now().strftime('%B')
mes_nombre_es = meses_es[mes_nombre_en]
nombre_carpeta = f"{mes_num}-{mes_nombre_es}"

# Ruta base
ruta_base = r"C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025"
ruta_carpeta = os.path.join(ruta_base, nombre_carpeta)

if not os.path.isdir(ruta_carpeta):
    raise FileNotFoundError(f"No existe la carpeta: {ruta_carpeta}")

# Buscar el Excel más reciente
archivo_excel = None
fecha_modificacion_reciente = None

for archivo in os.listdir(ruta_carpeta):
    if archivo.lower().endswith(('.xlsx', '.xls')):
        ruta_archivo = os.path.join(ruta_carpeta, archivo)
        fecha_modificacion = os.path.getmtime(ruta_archivo)
        if (fecha_modificacion_reciente is None) or (fecha_modificacion > fecha_modificacion_reciente):
            fecha_modificacion_reciente = fecha_modificacion
            archivo_excel = archivo

# Copiar el archivo más reciente agregando _dd-mm-YYYY
if archivo_excel:
    ruta_original = os.path.join(ruta_carpeta, archivo_excel)
    nombre, extension = os.path.splitext(archivo_excel)

    # Quitar fecha previa si ya viene en el nombre (acepta dd-mm-YYYY o YYYY-mm-dd)
    nombre_sin_fecha = re.sub(r'_(\d{2}-\d{2}-\d{4}|\d{4}-\d{2}-\d{2})$', '', nombre, flags=re.IGNORECASE)

    nuevo_nombre = f"{nombre_sin_fecha}_{ayer}{extension}"
    ruta_nueva = os.path.join(ruta_carpeta, nuevo_nombre)

    shutil.copy(ruta_original, ruta_nueva)
    print(f"Archivo copiado como: {nuevo_nombre}")
else:
    print("No se encontró ningún archivo Excel en la carpeta.")
