"""
Script para extraer datos de múltiples fuentes ODBC, filtrar por mes actual y guardar en C:\data
"""

import pandas as pd
import pyodbc
from pathlib import Path
from datetime import datetime

# ===== CONFIGURACIÓN =====
# Lista de nombres de fuentes ODBC a conectar
FUENTES_ODBC = ["RS01", "RS03", "RS04", "RS06", "RS07", "RS08", "RS10", "RS13", "RS14"]

# Nombre de la tabla o consulta en cada fuente ODBC
# La tabla se llama "ROUTES" en todas las fuentes ODBC
# El prefijo dbo_ROUTES_RS01 es solo para identificación, no es parte del nombre real
TABLA_O_CONSULTA = "ROUTES"  # Nombre real de la tabla en la base de datos

# Nombre de la columna de fecha para filtrar por mes actual
COLUMNA_FECHA = "DISPATCH_DATE"  # <-- CAMBIA SI ES NECESARIO

# Carpeta de salida
CARPETA_SALIDA = Path("C:/data")

# ===== CONSULTA SQL (opcional - si quieres una consulta personalizada) =====
# Si defines CONSULTA_SQL, se usará en lugar de leer directamente la tabla
# El filtro de fecha se agregará automáticamente
CONSULTA_SQL = None  # Ejemplo: "SELECT * FROM Tabla WHERE Campo = 'Valor'"

# ===== CONFIGURACIÓN DE COLUMNAS (opcional) =====
# Si quieres seleccionar columnas específicas, descomenta y ajusta:
# COLUMNAS_SELECCIONADAS = ["Campo1", "Campo2", "Campo3"]
COLUMNAS_SELECCIONADAS = None  # None = todas las columnas

def conectar_odbc(nombre_fuente):
    """
    Conecta a una fuente de datos ODBC por nombre
    """
    # String de conexión para ODBC DSN
    conn_str = f"DSN={nombre_fuente};"
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a ODBC '{nombre_fuente}': {str(e)}")

# def obtener_mes_actual():
#     """
#     Obtiene el año y mes actual
#     """
#     ahora = datetime.now()
#     return ahora.year, ahora.month


def obtener_mes_actual():
    """
    Obtiene el año y mes del período deseado:
    - Mes pasado respecto a hoy
    """
    ahora = datetime.now()
    # Retroceder un mes con manejo de cambio de año
    if ahora.month == 1:
        año = ahora.year - 1
        mes = 12
    else:
        año = ahora.year
        mes = ahora.month - 1
    return año, mes



def construir_consulta(tabla_o_consulta, columna_fecha, año, mes, columnas=None):
    """
    Construye la consulta SQL con filtro por mes actual
    Prueba múltiples variaciones del nombre de tabla
    """
    # Si hay una consulta SQL personalizada, usarla
    if CONSULTA_SQL:
        # Agregar filtro de fecha a la consulta personalizada
        if "WHERE" in CONSULTA_SQL.upper():
            filtro_fecha = f" AND YEAR({columna_fecha}) = {año} AND MONTH({columna_fecha}) = {mes}"
            consulta = CONSULTA_SQL + filtro_fecha
        else:
            filtro_fecha = f" WHERE YEAR({columna_fecha}) = {año} AND MONTH({columna_fecha}) = {mes}"
            consulta = CONSULTA_SQL + filtro_fecha
        return consulta
    
    # Generar variaciones del nombre de tabla
    variaciones_tabla = []
    
    # 1. Nombre original
    variaciones_tabla.append(tabla_o_consulta)
    
    # 2. Sin prefijo dbo_ si existe
    if tabla_o_consulta.startswith("dbo_"):
        variaciones_tabla.append(tabla_o_consulta.replace("dbo_", "", 1))
    
    # 3. Con esquema explícito dbo.
    if not tabla_o_consulta.startswith("dbo.") and "dbo_" in tabla_o_consulta:
        variaciones_tabla.append(tabla_o_consulta.replace("dbo_", "dbo.", 1))
    
    # 4. Solo el nombre sin esquema ni prefijo
    nombre_simple = tabla_o_consulta
    if "." in nombre_simple:
        nombre_simple = nombre_simple.split(".")[-1]
    if nombre_simple.startswith("dbo_"):
        nombre_simple = nombre_simple.replace("dbo_", "", 1)
    if nombre_simple not in variaciones_tabla:
        variaciones_tabla.append(nombre_simple)
    
    # Construir consultas con todas las variaciones
    consultas = {}
    filtro1 = f" WHERE YEAR({columna_fecha}) = {año} AND MONTH({columna_fecha}) = {mes}"
    filtro2 = f" WHERE YEAR([{columna_fecha}]) = {año} AND MONTH([{columna_fecha}]) = {mes}"
    
    if columnas:
        columnas_str = ", ".join(columnas)
        select_part = f"SELECT {columnas_str} FROM"
    else:
        select_part = "SELECT * FROM"
    
    # Generar todas las combinaciones
    for i, tabla_var in enumerate(variaciones_tabla):
        # Sin corchetes
        consultas[f'var{i}_sin_corchetes'] = f"{select_part} {tabla_var}{filtro1}"
        consultas[f'var{i}_sin_corchetes_col'] = f"{select_part} {tabla_var}{filtro2}"
        # Con corchetes
        consultas[f'var{i}_con_corchetes'] = f"{select_part} [{tabla_var}]{filtro1}"
        consultas[f'var{i}_con_corchetes_col'] = f"{select_part} [{tabla_var}]{filtro2}"
    
    return consultas

def listar_tablas_disponibles(conn, fuente_nombre):
    """
    Lista todas las tablas y consultas disponibles en la fuente ODBC
    """
    tablas = []
    try:
        cursor = conn.cursor()
        for row in cursor.tables(tableType='TABLE'):
            tablas.append(row.table_name)
        
        if tablas:
            print(f"  {fuente_nombre}: {len(tablas)} tablas encontradas")
            for i, tabla in enumerate(tablas[:5], 1):  # Mostrar solo las primeras 5
                print(f"    {i}. {tabla}")
            if len(tablas) > 5:
                print(f"    ... y {len(tablas) - 5} más")
        
        return tablas
    except Exception as e:
        print(f"  [ADVERTENCIA] {fuente_nombre}: No se pudieron listar las tablas: {str(e)}")
        return []

def extraer_datos(conn, fuente_nombre, tabla_o_consulta, columna_fecha, año, mes, columnas=None):
    """
    Extrae datos de una fuente ODBC filtrando por mes actual
    """
    print(f"\n  [EXTRAYENDO] {fuente_nombre}:")
    
    # La tabla se llama "ROUTES" en todas las fuentes ODBC
    # No necesita ajuste según la fuente, todas usan el mismo nombre
    tabla_ajustada = tabla_o_consulta
    
    print(f"     Tabla: {tabla_ajustada} (Fuente ODBC: {fuente_nombre})")
    print(f"     Filtro: Mes {mes:02d}/{año}")
    
    try:
        # Construir consulta con la tabla ajustada
        resultado_consulta = construir_consulta(tabla_ajustada, columna_fecha, año, mes, columnas)
        
        # Si CONSULTA_SQL está definida, usar directamente (es un string)
        if CONSULTA_SQL:
            consulta = resultado_consulta
            df = pd.read_sql(consulta, conn)
        else:
            # Probar diferentes formatos en orden de preferencia
            # Orden: primero sin corchetes, luego con corchetes
            formatos_ordenados = sorted([k for k in resultado_consulta.keys()], 
                                       key=lambda x: ('con_corchetes' not in x, x))
            
            df = None
            ultimo_error = None
            consulta_exitosa = None
            
            for formato in formatos_ordenados:
                try:
                    consulta = resultado_consulta[formato]
                    df = pd.read_sql(consulta, conn)
                    consulta_exitosa = formato
                    print(f"     [OK] Consulta exitosa con formato: {formato}")
                    break
                except Exception as e_intento:
                    ultimo_error = e_intento
                    continue
            
            if df is None:
                raise ultimo_error if ultimo_error else Exception("No se pudo ejecutar ninguna variante de la consulta")
        
        # Agregar columna con el nombre de la fuente
        df['Fuente_ODBC'] = fuente_nombre
        
        print(f"     [OK] {len(df)} filas extraídas")
        
        return df
        
    except Exception as e:
        error_msg = str(e)
        print(f"     [ERROR] {error_msg}")
        
        # Intentar listar tablas disponibles para ayudar al diagnóstico
        try:
            print(f"     [DIAGNOSTICO] Buscando tablas disponibles...")
            cursor = conn.cursor()
            tablas_encontradas = []
            for row in cursor.tables(tableType='TABLE'):
                nombre_tabla = row.table_name
                if 'ROUTE' in nombre_tabla.upper() or 'RS' in nombre_tabla.upper():
                    tablas_encontradas.append(nombre_tabla)
            
            if tablas_encontradas:
                print(f"     [DIAGNOSTICO] Tablas similares encontradas:")
                for tabla in tablas_encontradas[:10]:  # Mostrar máximo 10
                    print(f"       - {tabla}")
        except:
            pass
        
        # Retornar DataFrame vacío en lugar de fallar completamente
        return pd.DataFrame()

def guardar_resultado(df, año, mes):
    """
    Guarda el resultado en C:\data
    """
    print("\n" + "=" * 60)
    print("GUARDANDO RESULTADO")
    print("=" * 60)
    
    # Crear carpeta si no existe
    try:
        CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Carpeta de salida: {CARPETA_SALIDA}")
    except Exception as e:
        raise ValueError(f"No se pudo crear la carpeta C:\\data: {str(e)}")
    
    # Nombre del archivo con fecha
    fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"Extraccion_Access_{año}{mes:02d}.xlsx"
    archivo_salida = CARPETA_SALIDA / nombre_archivo
    
    try:
        # Guardar en Excel
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
        
        print(f"  [OK] Archivo guardado: {archivo_salida}")
        print(f"  [OK] Total de filas: {len(df)}")
        print(f"  [OK] Total de columnas: {len(df.columns)}")
        
        # También guardar en CSV
        archivo_csv = CARPETA_SALIDA / nombre_archivo.replace('.xlsx', '.csv')
        df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
        print(f"  [OK] Archivo CSV guardado: {archivo_csv}")
        
        return archivo_salida
        
    except Exception as e:
        raise ValueError(f"Error guardando archivo: {str(e)}")

def main():
    """
    Función principal
    """
    conexiones = []
    try:
        # Obtener mes actual
        año, mes = obtener_mes_actual()
        print("=" * 60)
        print("EXTRACCIÓN DE DATOS DE MÚLTIPLES FUENTES ODBC")
        print("=" * 60)
        print(f"Filtro: Mes actual = {mes:02d}/{año}")
        print(f"Fuentes ODBC: {', '.join(FUENTES_ODBC)}")
        print(f"Tabla/Consulta: {TABLA_O_CONSULTA}")
        print(f"Columna de fecha: {COLUMNA_FECHA}\n")
        
        # Lista para almacenar todos los DataFrames
        dataframes = []
        fuentes_exitosas = []
        fuentes_fallidas = []
        
        # Conectar y extraer de cada fuente ODBC
        print("=" * 60)
        print("CONECTANDO Y EXTRAYENDO DATOS")
        print("=" * 60)
        
        for fuente in FUENTES_ODBC:
            conn = None
            try:
                # Conectar
                print(f"\n[CONECTANDO] {fuente}...")
                conn = conectar_odbc(fuente)
                conexiones.append((fuente, conn))
                print(f"  [OK] Conectado a {fuente}")
                
                # Listar tablas (solo para la primera fuente, como referencia)
                if fuente == FUENTES_ODBC[0]:
                    print("\n  Tablas disponibles (solo primera fuente como referencia):")
                    listar_tablas_disponibles(conn, fuente)
                
                # Extraer datos
                df = extraer_datos(
                    conn,
                    fuente,
                    TABLA_O_CONSULTA,
                    COLUMNA_FECHA,
                    año,
                    mes,
                    COLUMNAS_SELECCIONADAS
                )
                
                if not df.empty:
                    dataframes.append(df)
                    fuentes_exitosas.append(fuente)
                else:
                    fuentes_fallidas.append(fuente)
                    print(f"  [ADVERTENCIA] {fuente}: No se extrajeron datos")
                    
            except Exception as e:
                fuentes_fallidas.append(fuente)
                print(f"  [ERROR] {fuente}: Error - {str(e)}")
                # Continuar con la siguiente fuente
                continue
        
        # Combinar todos los DataFrames
        print("\n" + "=" * 60)
        print("COMBINANDO RESULTADOS")
        print("=" * 60)
        
        if not dataframes:
            raise ValueError("No se pudo extraer datos de ninguna fuente ODBC")
        
        df_final = pd.concat(dataframes, ignore_index=True)
        
        print(f"  [OK] Total de fuentes exitosas: {len(fuentes_exitosas)}")
        print(f"    {', '.join(fuentes_exitosas)}")
        
        if fuentes_fallidas:
            print(f"  [ADVERTENCIA] Fuentes con problemas: {len(fuentes_fallidas)}")
            print(f"    {', '.join(fuentes_fallidas)}")
        
        print(f"\n  [OK] Total de filas combinadas: {len(df_final)}")
        print(f"  [OK] Total de columnas: {len(df_final.columns)}")
        
        # Resumen por fuente
        if 'Fuente_ODBC' in df_final.columns:
            print("\n  Resumen por fuente:")
            resumen = df_final['Fuente_ODBC'].value_counts().sort_index()
            for fuente, cantidad in resumen.items():
                print(f"    {fuente}: {cantidad} filas")
        
        # Guardar resultado
        archivo = guardar_resultado(df_final, año, mes)
        
        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Archivo guardado en: {archivo}")
        print(f"Total de registros: {len(df_final)}")
        print(f"Fuentes procesadas: {len(fuentes_exitosas)}/{len(FUENTES_ODBC)}")
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR EN EL PROCESO")
        print("=" * 60)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cerrar todas las conexiones
        for fuente, conn in conexiones:
            try:
                conn.close()
            except:
                pass
        if conexiones:
            print("\n  [OK] Todas las conexiones cerradas")

if __name__ == "__main__":
    exit(main())


