import pandas as pd
import os
from datetime import datetime

# ===================== CONFIGURACIÓN =====================
carpeta = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\12-diciembre"
bahias = 'Bahias'

# Modo para nombrar el archivo de salida:
#   - "fecha_max_datos": usa la fecha máxima encontrada en la columna 'Fecha' del Excel
#   - "fecha_sistema": usa la fecha actual del sistema
modo_nombre = "fecha_max_datos"  # <-- cambia a "fecha_sistema" si lo prefieres

# Nombre base (sin fecha) y carpeta de salida
fecha_actual = datetime.now()
mes_nombre = fecha_actual.strftime("%B")  # Nombre del mes en inglés
año = fecha_actual.strftime("%Y")
nombre_base_salida = f"C:\\data\\Vol_Entregas_Portafolio_{mes_nombre}_{año}"

# Crear directorio de salida si no existe
directorio_salida = os.path.dirname(nombre_base_salida)
if not os.path.exists(directorio_salida):
    os.makedirs(directorio_salida, exist_ok=True)
    print(f"📁 Directorio creado: {directorio_salida}")

print(f"📅 Procesando para el mes: {mes_nombre} {año}")
print(f"📁 Nombre base del archivo: {nombre_base_salida}")

# ===================== UTILIDADES =====================
def generar_nombre_unico(nombre_base, fecha_para_nombre: datetime) -> str:
    """
    Genera un nombre único con sufijo de fecha dd-mm-YYYY y contador si existe.
    """
    fecha_str = fecha_para_nombre.strftime("%d-%m-%Y")
    candidato = f"{nombre_base}_{fecha_str}.xlsx"
    contador = 1
    while os.path.exists(candidato):
        candidato = f"{nombre_base}_{fecha_str}_{contador}.xlsx"
        contador += 1
    return candidato

# ===================== PROCESO =====================
archivos_con_errores = 0

# Listar archivos Excel
try:
    archivos_excel = [n for n in os.listdir(carpeta) if n.lower().endswith('.xlsx')]
except FileNotFoundError:
    print(f"❌ Error: La carpeta '{carpeta}' no se encontró.")
    archivos_con_errores += 1
    archivos_excel = []

if archivos_excel:
    # Ordenar por fecha de modificación y tomar el último
    archivos_excel.sort(key=lambda x: os.path.getmtime(os.path.join(carpeta, x)))
    ultimo_archivo = archivos_excel[-1]
    ruta_archivo = os.path.join(carpeta, ultimo_archivo)

    print(f"📖 Leyendo el último archivo: {ultimo_archivo}")
    inicio_lectura = datetime.now()

    try:
        # Leer hoja
        df = pd.read_excel(ruta_archivo, sheet_name=bahias, engine='openpyxl')

        # Validar columnas requeridas
        columnas_requeridas = ['Bahía', 'Familia', 'CJE Conve', 'Cajas', 'Entrega', 'Zona', 'Fecha']
        faltantes = [c for c in columnas_requeridas if c not in df.columns]
        if faltantes:
            raise ValueError(f"Faltan columnas en la hoja '{bahias}': {faltantes}")

        # Normalizar tipo de fecha
        if not pd.api.types.is_datetime64_any_dtype(df['Fecha']):
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)

        # Validar que haya al menos una fecha válida
        if df['Fecha'].notna().sum() == 0:
            # Sin fechas válidas -> si el modo es por fecha de datos, caemos a fecha del sistema
            print("⚠️ No se encontraron fechas válidas en la columna 'Fecha'. Se usará la fecha del sistema para el nombre del archivo.")
            fecha_max_datos = None
        else:
            fecha_max_datos = df['Fecha'].max()

        # Filtrar bahías no válidas
        df = df[~df['Bahía'].astype(str).isin(['00', '0'])]

        # Crear Portafolio según Familia (considerando &amp; de exportes HTML)
        df['Portafolio'] = df['Familia'].replace({
            'CERVEZA &amp; BAS': 'C&amp;B',
            'OTROS': 'OTROS',
            'CARBONATADAS': 'BNA',
            'AGUAS &amp; REFRESCOS': 'BNA',
            'ALIMENTOS': 'ALI',
            'VINOS': 'VYD',
            'DESTILADOS': 'VYD'
        })

        # Renombrar columnas
        df = df.rename(columns={'CJE Conve': 'CJE', 'Cajas': 'CJF'})

        # Agrupar
        datos_agrupados = (
            df.groupby(['Entrega', 'Zona', 'Portafolio', 'Fecha'])[['CJF', 'CJE']]
              .sum()
              .reset_index()
        )

        # Asegurar tipo texto en Entrega
        datos_agrupados['Entrega'] = datos_agrupados['Entrega'].astype(str)

        # Determinar fecha a usar para el nombre
        if modo_nombre == "fecha_max_datos" and fecha_max_datos is not None:
            fecha_para_nombre = fecha_max_datos
            fuente_fecha = "fecha máxima de los datos"
        else:
            fecha_para_nombre = datetime.now()
            fuente_fecha = "fecha del sistema"

        # Generar nombre de salida único
        nombre_archivo_salida = generar_nombre_unico(nombre_base_salida, fecha_para_nombre)

        # Guardar archivo único (SIN copia +1 día)
        datos_agrupados.to_excel(nombre_archivo_salida, index=False)

        # Salidas informativas
        ult_fecha_archivo = datos_agrupados['Fecha'].max()
        ult_fecha_archivo_str = ult_fecha_archivo.strftime("%d-%m-%Y") if pd.notna(ult_fecha_archivo) else "NaT"

        print(f"✅ Archivo generado: {nombre_archivo_salida}")
        print(f"ℹ️  Fecha usada para el nombre ({fuente_fecha}): {fecha_para_nombre.strftime('%d-%m-%Y')}")
        print(f"📊 Registros procesados: {len(datos_agrupados)}")
        print(f"📅 Fecha máxima en datos: {ult_fecha_archivo_str}")
        print(f"📁 Carpeta: {os.path.dirname(nombre_archivo_salida)}")

    except FileNotFoundError:
        print(f"❌ Error: El archivo '{ultimo_archivo}' no se encontró.")
        archivos_con_errores += 1
    except ValueError as ve:
        print(f"❌ Error de datos: {ve}")
        archivos_con_errores += 1
    except Exception as e:
        print(f"❌ Error al procesar '{ultimo_archivo}': {e}")
        archivos_con_errores += 1
    finally:
        fin_lectura = datetime.now()
        tiempo_lectura = fin_lectura - inicio_lectura
        print(f"⏱️  Tiempo de lectura para '{ultimo_archivo}': {tiempo_lectura}")

print(f"Archivos con errores: {archivos_con_errores}")