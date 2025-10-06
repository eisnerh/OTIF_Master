import pandas as pd
import os
import time

# --- P A S O S ---

## 1. Definir las rutas de tus archivos
# La 'r' al principio de la cadena de texto es para evitar problemas con las barras invertidas
ruta_archivo1 = r"C:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\OTIF ENT CD01\YTD\2025\REP PLR ESTATUS ENTREGAS v25 - 1 Semestre.xlsx"
ruta_archivo2 = r"C:\Users\eisne\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\OTIF ENT CD01\YTD\2025\REP PLR ESTATUS ENTREGAS v25.xlsx"

## 2. Leer el primer archivo y medir el tiempo
print(f"⌛️ Leyendo el archivo: {os.path.basename(ruta_archivo1)}...")
inicio_lectura1 = time.time()
df1 = pd.read_excel(ruta_archivo1, sheet_name='REP PLR')
fin_lectura1 = time.time()
tiempo_lectura1 = round(fin_lectura1 - inicio_lectura1, 2)
print(f"✅ ¡Lectura completa en {tiempo_lectura1} segundos!")
print("-" * 50) 

## 3. Leer el segundo archivo y medir el tiempo
print(f"⌛️ Leyendo el archivo: {os.path.basename(ruta_archivo2)}...")
inicio_lectura2 = time.time()
df2 = pd.read_excel(ruta_archivo2, sheet_name='REP PLR')
fin_lectura2 = time.time()
tiempo_lectura2 = round(fin_lectura2 - inicio_lectura2, 2)
print(f"✅ ¡Lectura completa en {tiempo_lectura2} segundos!")
print("-" * 50)

## 4. Combinar los archivos
print("⏳ Uniendo los dos archivos de Excel...")
df_concatenado = pd.concat([df1, df2], ignore_index=True)
print("✔️ ¡Archivos unidos con éxito!")
print("-" * 50)

## 5. Formatear la columna de fecha (usando 'Fe.Entrega')
nombre_columna_fecha = 'Fe.Entrega'

# Verificar si la columna existe antes de formatearla
if nombre_columna_fecha in df_concatenado.columns:
    print(f"🗓️ Convirtiendo la columna '{nombre_columna_fecha}' a formato de fecha...")
    df_concatenado[nombre_columna_fecha] = pd.to_datetime(df_concatenado[nombre_columna_fecha], errors='coerce')
    print("✔️ ¡Columna de fecha formateada!")
else:
    print(f"⚠️ ¡Advertencia! No se encontró la columna '{nombre_columna_fecha}'. No se realizará el formateo de fecha.")

print("-" * 50)

## 6. Guardar el resultado en un archivo Parquet
nombre_archivo_salida = ruta_archivo1.replace('.xlsx', '.parquet')
print(f"💾 Guardando el archivo combinado en formato Parquet: {os.path.basename(nombre_archivo_salida)}...")
inicio_guardado = time.time()
df_concatenado.to_parquet(nombre_archivo_salida, index=False)
fin_guardado = time.time()
tiempo_guardado = round(fin_guardado - inicio_guardado, 2)
print(f"🎉 ¡Proceso finalizado! Archivo guardado en {tiempo_guardado} segundos.")
print("¡Todo listo! ✨")