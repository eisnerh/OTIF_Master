import pandas as pd
import os
from datetime import datetime

# Rutas y configuraciones
carpeta = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\10-Octubre"
bahias = 'Bahias'

# Generar nombre base automáticamente basado en la fecha actual
fecha_actual = datetime.now()
mes_nombre = fecha_actual.strftime("%B")  # Nombre del mes en inglés
mes_numero = fecha_actual.strftime("%m")  # Número del mes
año = fecha_actual.strftime("%Y")

# Crear nombre base dinámico
nombre_base_salida = f"C:\\data\\Vol_Entregas_Portafolio_{mes_nombre}_{año}"

# Crear directorio de salida si no existe
directorio_salida = os.path.dirname(nombre_base_salida)
if not os.path.exists(directorio_salida):
    os.makedirs(directorio_salida, exist_ok=True)
    print(f"📁 Directorio creado: {directorio_salida}")

# Mostrar información del nombre generado
print(f"📅 Procesando para el mes: {mes_nombre} {año}")
print(f"📁 Nombre base del archivo: {nombre_base_salida}")

# Inicialización de variables
archivos_con_errores = 0

# Obtener la lista de archivos en la carpeta
try:
    archivos_excel = [nombre_archivo for nombre_archivo in os.listdir(carpeta) if nombre_archivo.endswith('.xlsx')]
except FileNotFoundError:
    print(f"Error: La carpeta '{carpeta}' no se encontró.")
    archivos_con_errores += 1
    archivos_excel = []

if archivos_excel:
    # Ordenar archivos por fecha de modificación y seleccionar el último
    archivos_excel.sort(key=lambda x: os.path.getmtime(os.path.join(carpeta, x)))
    ultimo_archivo = archivos_excel[-1]

    # Procesar el último archivo
    ruta_archivo = os.path.join(carpeta, ultimo_archivo)
    print(f"Leyendo el último archivo: {ultimo_archivo}")  # Mostrar el nombre del archivo
    inicio_lectura = datetime.now()  # Registrar el tiempo de inicio de lectura
    try:
        df = pd.read_excel(ruta_archivo, sheet_name=bahias, engine='openpyxl')    
        # Filtrar registros donde la bahía no sea '00' ni '0'
        df = df[~df['Bahía'].isin(['00', '0'])]
        # Verificar si las columnas existen
        if all(col in df.columns for col in ['Familia', 'CJE Conve']):
            # Crear columna 'Portafolio' basada en 'Familia'
            df['Portafolio'] = df['Familia'].replace({
                'CERVEZA & BAS': 'C&B',
                'OTROS': 'OTROS',
                'CARBONATADAS': 'BNA',
                'AGUAS & REFRESCOS': 'BNA',
                'ALIMENTOS': 'ALI',
                'VINOS': 'VYD',
                'DESTILADOS': 'VYD'
            })

            # Renombrar las columnas
            df = df.rename(columns={'CJE Conve': 'CJE', 'Cajas': 'CJF'})

            # Agrupar datos
            datos_agrupados = df.groupby(['Entrega', 'Zona', 'Portafolio', 'Fecha'])[['CJF','CJE']].sum().reset_index()
            
            # Convertir la columna 'Entrega' a texto (string)
            datos_agrupados['Entrega'] = datos_agrupados['Entrega'].astype(str)
            
            # Obtener la fecha del último archivo procesado
            ult_fecha_archivo = datos_agrupados['Fecha'].max().strftime("%d-%m-%Y")

            # Función para generar un nombre de archivo único
            def generar_nombre_unico(nombre_base):
                contador = 1
                # Usar fecha del archivo procesado en lugar de fecha actual
                fecha_archivo = datos_agrupados['Fecha'].max().strftime("%d-%m-%Y")
                nombre_archivo = f"{nombre_base}_{fecha_archivo}.xlsx"
                
                while os.path.exists(nombre_archivo):
                    nombre_archivo = f"{nombre_base}_{fecha_archivo}_{contador}.xlsx"
                    contador += 1
                return nombre_archivo
            
            # Generar un nombre de archivo único
            nombre_archivo_salida = generar_nombre_unico(nombre_base_salida)
            
            # Guardar el archivo final
            datos_agrupados.to_excel(nombre_archivo_salida, index=False)
            
            # Mensajes de salida mejorados
            print(f"✅ Archivo generado exitosamente: {nombre_archivo_salida}")
            print(f"📊 Total de registros procesados: {len(datos_agrupados)}")
            print(f"📅 Fecha del archivo procesado: {ult_fecha_archivo}")
            print(f"📁 Ubicación: {os.path.dirname(nombre_archivo_salida)}")
        else:
            print(f"Error: Las columnas necesarias no se encontraron en '{ultimo_archivo}'.")
            archivos_con_errores += 1
    except FileNotFoundError:
        print(f"Error: El archivo '{ultimo_archivo}' no se encontró.")
        archivos_con_errores += 1
    except ValueError:
        print(f"Error: La hoja '{bahias}' no se encontró en el archivo '{ultimo_archivo}'.")
        archivos_con_errores += 1
    except Exception as e:
        print(f"Error al procesar '{ultimo_archivo}': {e}")
        archivos_con_errores += 1
    finally:
        fin_lectura = datetime.now()  # Registrar el tiempo de fin de lectura
        tiempo_lectura = fin_lectura - inicio_lectura
        print(f"Tiempo de lectura para '{ultimo_archivo}': {tiempo_lectura}")

print(f"Archivos con errores: {archivos_con_errores}")
