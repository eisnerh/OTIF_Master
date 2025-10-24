"""
Script para procesar archivos Excel:
- Quitar contraseña de hojas protegidas (las deja sin protección)
- Actualizar celdas con fecha de mañana: I2=día, J2=mes, K2=año
- Ejecutar la lógica de ReportarHCzona directamente en Python
"""

import os
import win32com.client
from datetime import datetime, timedelta
import time
import math

# Configuración
PASSWORD = "Planruta2019"
FOLDERS = ["MACROZONAS", "RURAL"]
WORKSPACE_PATH = r"C:\data\disponibilidad personal"

# Calcular la fecha de mañana
tomorrow = datetime.now() + timedelta(days=1)

print(f"Fecha de mañana: {tomorrow.strftime('%d/%m/%Y')}")
print("=" * 70)

def reportar_hc_zona(wb, excel):
    """
    Implementa la lógica de la macro ReportarHCzona en Python.
    Guarda los datos de disponibilidad en la tabla RegistroHCdisponible.
    """
    try:
        # 1. Desproteger la hoja Registro
        ws_registro = wb.Worksheets("Registro")
        ws_registro.Unprotect(Password=PASSWORD)
        
        # 2. Obtener la hoja Personal de zona
        ws_personal = wb.Worksheets("Personal de zona")
        
        # 3. Leer valores de rangos nombrados
        print("    - Leyendo valores de rangos nombrados...")
        
        # Función auxiliar para leer rango nombrado
        def get_named_range_value(name):
            try:
                return ws_personal.Range(name).Value
            except:
                return 0
        
        # Función auxiliar para convertir a entero, manejando datetime
        def safe_int(value):
            if value is None:
                return 0
            # Verificar si es un datetime (incluye pywintypes.datetime)
            if hasattr(value, 'day') and hasattr(value, 'month') and hasattr(value, 'year'):
                # Si es un datetime, retornar 0 - se maneja por separado
                return 0
            try:
                return int(value)
            except:
                return 0
        
        HCdisp = safe_int(get_named_range_value("HC_Disponible"))
        CantChoferes = safe_int(get_named_range_value("Cantidad_de_Choferes"))
        CantAux = safe_int(get_named_range_value("Cantidad_De_auxiliares"))
        RutasDisp = safe_int(get_named_range_value("Rutas_disponibles"))
        RutasSoloChofer = safe_int(get_named_range_value("Solo_chofer"))
        Codigo = get_named_range_value("Codigo") or ""
        
        # Manejar fecha de reporte - puede venir como datetime o como valores separados
        dia_val = get_named_range_value("DiaReporte")
        mes_val = get_named_range_value("mesReporte")
        anio_val = get_named_range_value("AAAAReporte")
        
        # Si alguno es datetime (incluye pywintypes.datetime), extraer componentes
        if hasattr(dia_val, 'day') and hasattr(dia_val, 'month') and hasattr(dia_val, 'year'):
            DiaReporte = dia_val.day
            MesReporte = dia_val.month
            AAAAreporte = dia_val.year
        elif hasattr(mes_val, 'day') and hasattr(mes_val, 'month') and hasattr(mes_val, 'year'):
            DiaReporte = mes_val.day
            MesReporte = mes_val.month
            AAAAreporte = mes_val.year
        elif hasattr(anio_val, 'day') and hasattr(anio_val, 'month') and hasattr(anio_val, 'year'):
            DiaReporte = anio_val.day
            MesReporte = anio_val.month
            AAAAreporte = anio_val.year
        else:
            # Son valores numéricos separados
            DiaReporte = safe_int(dia_val)
            MesReporte = safe_int(mes_val)
            AAAAreporte = safe_int(anio_val)
        
        # Condiciones
        CondDisp = safe_int(get_named_range_value("CondDisp"))
        CondTemp = safe_int(get_named_range_value("CondTemp"))
        CondTempAp = safe_int(get_named_range_value("CondTempAp"))
        CondVacaciones = safe_int(get_named_range_value("CondVacaciones"))
        CondCargado = safe_int(get_named_range_value("CondCargado"))
        CondPermiso = safe_int(get_named_range_value("CondPermiso"))
        CondEspecial = safe_int(get_named_range_value("CondEspecial"))
        CondReubicado = safe_int(get_named_range_value("CondReubicado"))
        CondIncapacitado = safe_int(get_named_range_value("CondIncapacitado"))
        CondPrestado = safe_int(get_named_range_value("CondPrestado"))
        
        # Otros valores
        RutaReubicado = safe_int(get_named_range_value("Rutas_Reubicado"))
        RutaPeq = safe_int(get_named_range_value("Rutas_Camión_Peq"))
        UsoLimitado = safe_int(get_named_range_value("Uso_Limitado"))
        PersonalSobrante = safe_int(get_named_range_value("personal_Sobrante"))
        
        print(f"      HC Disponible: {HCdisp}, Choferes: {CantChoferes}, Rutas: {RutasDisp}")
        
        # 4. Validar y crear fecha de reporte
        if DiaReporte == 0 or MesReporte == 0 or AAAAreporte == 0:
            print("    ⚠ Error: Fecha de reporte inválida (día, mes o año es 0)")
            return False
        
        try:
            FechaReporte = datetime(AAAAreporte, MesReporte, DiaReporte)
        except ValueError:
            print(f"    ⚠ Error: Fecha inválida ({DiaReporte}/{MesReporte}/{AAAAreporte})")
            return False
        
        # 5. Obtener fecha/hora actual
        TimeStamp = datetime.now()
        Today = datetime.now().date()
        
        # 6. Validaciones de integridad
        errores = []
        
        # 6.1 - La fecha debe ser máximo 2 días en el futuro
        if FechaReporte.date() > Today + timedelta(days=2):
            errores.append("Error 1: La fecha digitada no es válida. Solo se permite reportar dos días hacia el futuro.")
        
        # 6.2 - No puede haber más rutas que choferes
        if RutasDisp > CantChoferes:
            errores.append("Error 2: No puede haber más rutas que choferes.")
        
        # 6.3 - No puede haber más choferes que HC
        if CantChoferes > HCdisp:
            errores.append("Error 3: No puede haber más choferes que personal.")
        
        # 6.4 - Validar fórmula de rutas disponibles
        CalcTeoRD = min(math.floor((HCdisp - UsoLimitado) / 2), CantChoferes)
        if CalcTeoRD != RutasDisp:
            errores.append(f"Error 4: Rutas disponibles no coincide con la fórmula (esperado: {CalcTeoRD}, actual: {RutasDisp}).")
        
        # 6.5 - Validar fórmula de solo chofer
        if CantChoferes > CantAux:
            CalcTeoSC = math.ceil(((HCdisp - UsoLimitado) / 2) - RutasDisp)
        else:
            CalcTeoSC = 0
        
        if CalcTeoSC != RutasSoloChofer:
            errores.append(f"Error 5: Solo chofer no coincide con la fórmula (esperado: {CalcTeoSC}, actual: {RutasSoloChofer}).")
        
        if errores:
            print("    ⚠ Errores de validación:")
            for error in errores:
                print(f"      - {error}")
            return False
        
        # 7. Acceder a la tabla RegistroHCdisponible
        print("    - Accediendo a tabla RegistroHCdisponible...")
        
        # Buscar la tabla en la hoja Registro
        tabla_registro = None
        for lo in ws_registro.ListObjects:
            if lo.Name == "RegistroHCdisponible":
                tabla_registro = lo
                break
        
        if not tabla_registro:
            print("    ⚠ Error: No se encontró la tabla RegistroHCdisponible")
            return False
        
        # 8. Buscar si ya existe la fecha
        print("    - Verificando si existe registro para esta fecha...")
        fecha_reporte_serial = FechaReporte.toordinal() + 693594  # Conversión a número serial de Excel
        
        PosicionFecha = None
        registros_count = tabla_registro.ListRows.Count
        
        if registros_count > 0:
            # Buscar la fecha en la primera columna
            fecha_col = tabla_registro.ListColumns(1).DataBodyRange
            
            for i in range(1, registros_count + 1):
                try:
                    celda_fecha = fecha_col.Cells(i, 1).Value
                    if celda_fecha and abs(float(celda_fecha) - fecha_reporte_serial) < 1:
                        PosicionFecha = i
                        print(f"      ✓ Registro existente encontrado en fila {i}, será sobrescrito")
                        break
                except:
                    continue
        
        # Si no existe, agregar nueva fila al inicio
        if PosicionFecha is None:
            tabla_registro.ListRows.Add(1)
            PosicionFecha = 1
            print("      ✓ Nueva fila agregada al inicio de la tabla")
        
        # 9. Guardar valores en las columnas correspondientes
        print("    - Guardando datos en la tabla...")
        
        def set_column_value(col_name, value):
            try:
                col = tabla_registro.ListColumns(col_name)
                col.DataBodyRange.Cells(PosicionFecha, 1).Value = value
            except Exception as e:
                print(f"      ⚠ Error al guardar {col_name}: {e}")
        
        set_column_value("Fecha reporte", fecha_reporte_serial)
        set_column_value("Fecha modificación", TimeStamp)
        set_column_value("Zona", Codigo)
        set_column_value("HC Disponible", HCdisp)
        set_column_value("Cantidad de choferes", CantChoferes)
        set_column_value("Cantidad de auxiliares", CantAux)
        set_column_value("Rutas disponibles", RutasDisp)
        set_column_value("Solo Chofer", RutasSoloChofer)
        set_column_value("Disponible", CondDisp)
        set_column_value("Temporal", CondTemp)
        set_column_value("Temporal Curva Ap", CondTempAp)
        set_column_value("Vacaciones", CondVacaciones)
        set_column_value("Cargado", CondCargado)
        set_column_value("Permiso", CondPermiso)
        set_column_value("Especial", CondEspecial)
        set_column_value("Reubicado", CondReubicado)
        set_column_value("Incapacitado", CondIncapacitado)
        set_column_value("Prestado", CondPrestado)
        set_column_value("Rutas Reubicado", RutaReubicado)
        set_column_value("Rutas Camión Peq", RutaPeq)
        set_column_value("Uso Limitado", UsoLimitado)
        set_column_value("Personal Sobrante", PersonalSobrante)
        
        print(f"    ✓ Reporte guardado exitosamente para {FechaReporte.strftime('%d/%m/%Y')}")
        
        return True
        
    except Exception as e:
        print(f"    ⚠ Error en reportar_hc_zona: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # NO proteger la hoja Registro - dejarla sin contraseña
        pass

def process_excel_file(file_path):
    """
    Procesa un archivo Excel individual:
    1. Quita la contraseña de todas las hojas (las deja sin protección)
    2. Actualiza las celdas con fecha de mañana: I2=día, J2=mes, K2=año
    3. Ejecuta la lógica de ReportarHCzona en Python
    """
    print(f"\nProcesando: {os.path.basename(file_path)}")
    
    # Crear instancia de Excel
    excel = None
    wb = None
    
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        # Abrir el archivo
        print(f"  - Abriendo archivo...")
        wb = excel.Workbooks.Open(file_path)
        
        # Procesar cada hoja - quitarles la contraseña permanentemente
        print(f"  - Quitando contraseñas de {wb.Sheets.Count} hoja(s)...")
        hojas_desprotegidas = 0
        for sheet in wb.Sheets:
            try:
                # Intentar desproteger la hoja con la contraseña
                if sheet.ProtectContents:
                    sheet.Unprotect(PASSWORD)
                    hojas_desprotegidas += 1
                    print(f"    ✓ Hoja '{sheet.Name}' desprotegida")
            except Exception as e:
                print(f"    ⚠ Error al desproteger hoja '{sheet.Name}': {e}")
        
        if hojas_desprotegidas > 0:
            print(f"    ✓ {hojas_desprotegidas} hoja(s) quedaron SIN CONTRASEÑA")
        
        # Actualizar fechas en la hoja "Personal de zona"
        print(f"  - Buscando hoja 'Personal de zona'...")
        
        try:
            target_sheet = wb.Sheets("Personal de zona")
            print(f"    ✓ Hoja encontrada")
            
            # I2 = día, J2 = mes, K2 = año
            target_sheet.Range("I2").Value = tomorrow.day
            target_sheet.Range("J2").Value = tomorrow.month
            target_sheet.Range("K2").Value = tomorrow.year
            print(f"    ✓ Celdas actualizadas - I2 (día): {tomorrow.day}, J2 (mes): {tomorrow.month}, K2 (año): {tomorrow.year}")
        except Exception as e:
            print(f"    ⚠ Error al actualizar fechas en 'Personal de zona': {e}")
        
        # Ejecutar la lógica de ReportarHCzona en Python
        print(f"  - Ejecutando lógica de ReportarHCzona...")
        try:
            resultado = reportar_hc_zona(wb, excel)
            if resultado:
                print(f"    ✓ ReportarHCzona ejecutado exitosamente")
            else:
                print(f"    ⚠ ReportarHCzona completado con advertencias")
        except Exception as e:
            print(f"    ⚠ Error al ejecutar ReportarHCzona: {e}")
        
        # Guardar cambios
        print(f"  - Guardando archivo...")
        wb.Save()
        print(f"  ✓ Archivo guardado exitosamente")
        
    except Exception as e:
        print(f"  ✗ Error procesando archivo: {e}")
        
    finally:
        # Cerrar el archivo y Excel
        try:
            if wb is not None:
                wb.Close(SaveChanges=False)
        except:
            pass
        
        try:
            if excel is not None:
                excel.Quit()
        except:
            pass

def main():
    """Función principal"""
    print("Iniciando procesamiento de archivos Excel...")
    print("=" * 70)
    
    total_files = 0
    processed_files = 0
    
    # Procesar archivos en cada carpeta
    for folder in FOLDERS:
        folder_path = os.path.join(WORKSPACE_PATH, folder)
        
        if not os.path.exists(folder_path):
            print(f"\n⚠ Carpeta no encontrada: {folder_path}")
            continue
        
        print(f"\n{'=' * 70}")
        print(f"Procesando carpeta: {folder}")
        print(f"{'=' * 70}")
        
        # Buscar archivos .xlsm
        for filename in os.listdir(folder_path):
            if filename.endswith(".xlsm"):
                total_files += 1
                file_path = os.path.join(folder_path, filename)
                
                try:
                    process_excel_file(file_path)
                    processed_files += 1
                    # Pequeña pausa entre archivos
                    time.sleep(1)
                except Exception as e:
                    print(f"✗ Error general: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Total de archivos encontrados: {total_files}")
    print(f"Archivos procesados exitosamente: {processed_files}")
    print("=" * 70)
    print("\n✓ Proceso completado!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n✗ Error crítico: {e}")
        import traceback
        traceback.print_exc()

