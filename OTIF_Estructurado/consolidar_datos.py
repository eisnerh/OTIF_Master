import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

# --- 1. Definir Rutas de Archivos ---
# Rutas de los archivos de entrada (fuente)
path_vol_procesado = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\volumen_procesado_familia.parquet"
path_vol_no_procesado = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\volumen_no_procesado_familia.parquet"
# Asumimos la ruta para el reporte PLR, ajústala si es necesario.
path_reporte_plr = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\reporte_plr.parquet"

# Ruta del archivo de salida
path_salida_consolidado = r"C:\Users\elopez21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\Data\OTIF_Resultado.parquet"

try:
    # --- 2. Cargar los DataFrames desde los archivos Parquet ---
    print("Cargando archivos Parquet...")
    volumen_procesado = pd.read_parquet(path_vol_procesado)
    volumen_no_procesado = pd.read_parquet(path_vol_no_procesado)
    reporte_plr = pd.read_parquet(path_reporte_plr)
    print("Archivos cargados exitosamente.")

    # --- 3. Primera Unión (Left Join) ---
    # Equivalente a: Table.NestedJoin(volumen_procesado_familia, {"Entrega", "Familia"}, volumen_no_procesado_familia, {"Entrega", "Segmento"}, ..., JoinKind.LeftOuter)
    print("Realizando la primera unión...")
    consolidado_1 = pd.merge(
        volumen_procesado,
        volumen_no_procesado,
        left_on=["Entrega", "Familia"],
        right_on=["Entrega", "Segmento"],
        how="left"
    )
    # El paso "Expandir" de Power Query es automático en pandas.
    # Eliminamos la columna 'Segmento' duplicada que viene de la tabla derecha.
    if 'Segmento' in consolidado_1.columns:
        consolidado_1 = consolidado_1.drop(columns=['Segmento'])

    # --- 4. Segunda Unión (Left Join) ---
    # Equivalente a: Table.NestedJoin(..., {"Entrega"}, reporte_plr, {"Entrega"}, ..., JoinKind.LeftOuter)
    print("Realizando la segunda unión...")
    consolidado_2 = pd.merge(
        consolidado_1,
        reporte_plr,
        on="Entrega",
        how="left"
    )
    # El paso "Expandir" también es automático aquí.

    # --- 5. Reordenar Columnas ---
    # Define el orden final de las columnas como en Power Query.
    # Las columnas que no existan en el DataFrame serán ignoradas.
    columnas_reordenadas = [
        "Centro", "Zona", "Entrega", "Cliente", "Nombre del Cliente", "Viaje", 
        "Guia Entrega", "Origen", "Fuerza Ventas", "Region", "Fe.Entrega", 
        "Cajas Equiv.", "Macro Canal", "Clasificación Clt", "Tipo Negocio", 
        "Provincia", "Cantón", "Distrito", "Latitud", "Longitud", "Familia", 
        "Fecha", "Cajas fisicas", "Cajas Equiv", "Entregas", "Descrip Cod Rechazo", 
        "Estado Entregas", "Cajas Eq. No Entregadas", "No Entregas"
    ]
    
    # Filtra la lista de reordenamiento para incluir solo las columnas que existen en el DataFrame final
    columnas_existentes_ordenadas = [col for col in columnas_reordenadas if col in consolidado_2.columns]
    
    # Aplica el nuevo orden
    consolidado_final = consolidado_2[columnas_existentes_ordenadas]
    print("Columnas reordenadas.")

    # --- 6. Guardar el resultado ---
    print(f"Guardando el archivo consolidado en: {path_salida_consolidado}")
    # Asegurarse de que el directorio de salida exista
    os.makedirs(os.path.dirname(path_salida_consolidado), exist_ok=True)
    
    # Convertir a tabla PyArrow y escribir en Parquet
    tabla_final = pa.Table.from_pandas(consolidado_final)
    pq.write_table(tabla_final, path_salida_consolidado)
    
    print("Proceso completado exitosamente.")

except FileNotFoundError as e:
    print(f"Error: No se pudo encontrar el archivo. Verifica las rutas. {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")
