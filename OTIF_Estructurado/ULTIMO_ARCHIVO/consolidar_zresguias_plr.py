import pandas as pd
from datetime import datetime
import os

# ==========================
# PARAMETROS
# ==========================
# Ruta del archivo Excel origen
ruta_archivo = r'C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Planeamientos de Rutas - 1. Dashboard Planeamiento\ZRESGUIAS\ZRESGUIAS.xlsx'

# Carpeta y archivo de salida
carpeta_salida = r"c:\data\PLR"
os.makedirs(carpeta_salida, exist_ok=True)
archivo_salida = os.path.join(carpeta_salida, "zresguias_ag.parquet")

# Columnas por las que quieres agrupar (ajústalas si lo necesitas)
columnas_agrupacion = [
    "Zona",
    "Ruta Dist",
    "Guía",
    "Centro",
    "Tipo de Guía",
    "Viaje",
    "Cod.",
    "Nombre del cliente",
    "Fecha",
    "Cap. Real"
]

# Columnas que se deben sumar
columnas_a_sumar = ["Cajas Equivalentes", "Cajas RS", "Cajas Fisicas"]

# Año que quieres procesar (actual)
anio_objetivo = datetime.now().year

# ==========================
# CARGA Y LIMPIEZA
# ==========================
# Lee Excel (hoja PEGAR)
df = pd.read_excel(ruta_archivo, sheet_name="PEGAR", engine="openpyxl")

# Asegura Fecha en datetime
if "Fecha" not in df.columns:
    raise ValueError("La columna 'Fecha' no existe en la hoja PEGAR.")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# Filtra por el año objetivo
df = df[df["Fecha"].dt.year == anio_objetivo].copy()

# Asegura que las columnas a sumar sean numéricas
for c in columnas_a_sumar:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    else:
        # Si falta alguna columna, créala en 0 para evitar errores al agrupar
        df[c] = 0.0

# Verifica que todas las columnas de agrupación existan
faltantes = [c for c in columnas_agrupacion if c not in df.columns]
if faltantes:
    raise ValueError(f"Faltan columnas para agrupar en el Excel: {faltantes}")

# ==========================
# AGREGACION NUEVA
# ==========================
# Sumas
df_sumas = (
    df.groupby(columnas_agrupacion, dropna=False)[columnas_a_sumar]
      .sum(min_count=1)  # respeta NaN si todo es NaN
      .reset_index()
)

# Conteo de registros
df_count = (
    df.groupby(columnas_agrupacion, dropna=False)
      .size()
      .reset_index(name="Cantidad")
)

# Une sumas + conteo
df_nuevo = df_sumas.merge(df_count, on=columnas_agrupacion, how="left")

print(f"✅ Filas agregadas (nuevo cálculo): {len(df_nuevo)}")

# ==========================
# ACTUALIZACION DEL PARQUET
# ==========================
def normaliza_fecha_serie(s):
    """Devuelve la fecha a nivel día (sin hora) para comparación."""
    return pd.to_datetime(s, errors="coerce").dt.normalize()

if os.path.exists(archivo_salida):
    try:
        df_existente = pd.read_parquet(archivo_salida)
        # Normaliza Fecha
        if "Fecha" in df_existente.columns:
            df_existente["Fecha"] = pd.to_datetime(df_existente["Fecha"], errors="coerce")
        else:
            # Si por alguna razón no está, la creamos nula para no romper
            df_existente["Fecha"] = pd.NaT

        # Fechas presentes en el nuevo cálculo (a nivel de día)
        fechas_nuevas = pd.Series(df_nuevo["Fecha"]).pipe(normaliza_fecha_serie).unique()

        # Filtra del existente todo lo que NO esté en las fechas nuevas (para no duplicar)
        mask_keep = ~normaliza_fecha_serie(df_existente["Fecha"]).isin(fechas_nuevas)
        df_existente_filtrado = df_existente.loc[mask_keep].copy()

        # Concatena existente (filtrado) + nuevo
        df_concat = pd.concat([df_existente_filtrado, df_nuevo], ignore_index=True)

        # Reagrega por seguridad por si hay claves repetidas
        agg_dict = {c: "sum" for c in columnas_a_sumar}
        agg_dict["Cantidad"] = "sum"
        df_final = (
            df_concat.groupby(columnas_agrupacion, dropna=False, as_index=False)
                     .agg(agg_dict)
        )

        print(f"🔄 Actualización: {len(df_existente)} → {len(df_final)} filas (tras consolidar).")
    except Exception as e:
        print(f"⚠️ No se pudo leer/actualizar el Parquet existente ({e}). Se sobrescribirá con el cálculo nuevo.")
        df_final = df_nuevo.copy()
else:
    # No existe el Parquet: usamos directamente el nuevo agregado
    df_final = df_nuevo.copy()

# ==========================
# GUARDAR SALIDA
# ==========================
try:
    df_final.to_parquet(archivo_salida, index=False)
    print(f"📁 Archivo Parquet guardado en: {archivo_salida}")
except Exception as e:
    print(f"⚠️ Error al guardar Parquet ({e}).\n    Sugerencia: instala 'pyarrow' o 'fastparquet'.\n    Guardando CSV como alternativa.")
    archivo_csv = archivo_salida.replace(".parquet", ".csv")
    df_final.to_csv(archivo_csv, index=False, encoding="utf-8-sig")
    print(f"📄 Archivo CSV guardado en: {archivo_csv}")
