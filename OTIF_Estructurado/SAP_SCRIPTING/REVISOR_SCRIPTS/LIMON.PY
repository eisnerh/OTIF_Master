
import os
import datetime
import openpyxl
# Rutas de las carpetas que contienen los archivos Excel
folder1 = r'C:\data\disponibilidad personal\MACROZONAS'
folder2 = r'C:\data\disponibilidad personal\MACROZONAS'

# Contraseña usada para proteger las hojas
password = 'Planruta2019'

# Fecha del día siguiente
tomorrow_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date()

def process_excel_file(file_path):
    try:
        wb = openpyxl.load_workbook(file_path)

        for sheet in wb.worksheets:
            # Eliminar protección de la hoja si está protegida
            if sheet.protection.sheet:
                sheet.protection.set_password(password)
                sheet.protection.sheet = False

        # Modificar solo la hoja "Personal de zona"
        if "Personal de zona" in wb.sheetnames:
            sheet = wb["Personal de zona"]
            sheet['I2'] = tomorrow_date
            sheet['J2'] = tomorrow_date
            sheet['K2'] = tomorrow_date

        wb.save(file_path)
        print(f"Procesado: {file_path}")
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")

# Procesar archivos en ambas carpetas
for folder in [folder1, folder2]:
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.endswith('.xlsx'):
                file_path = os.path.join(folder, filename)
                process_excel_file(file_path)
    else:
        print(f"La carpeta no existe: {folder}")