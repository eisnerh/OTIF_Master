#!/usr/bin/env python3
"""
🚀 SCRIPT MAESTRO DE AUTOMATIZACIÓN SAP
=====================================

Este script automatiza la extracción de 9 reportes de SAP:
- mb51: Reporte de movimientos de material
- rep_plr: Reporte PLR (Planificación Logística)
- y_dev_45: Reporte de desarrollo 45
- y_dev_74: Reporte de desarrollo 74
- y_dev_82: Reporte de desarrollo 82
- z_devo_alv: Reporte de devoluciones ALV
- zhbo: Reporte HBO
- zred: Reporte de red
- zsd_incidencias: Reporte de incidencias SD

Funcionalidades:
✅ Login automático en SAP
✅ Extracción de todos los reportes
✅ Lógica de fechas (sábado-domingo para lunes)
✅ Nombres de archivos con fecha de ejecución
✅ Procesamiento para Power BI
✅ Manejo de errores y logs
"""

import win32com.client
import os
import time
import pandas as pd
import json
from datetime import datetime, timedelta
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automatizacion_sap.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatizacionSAP:
    def __init__(self):
        # Parámetros de conexión SAP
        self.sap_system = "SAP R/3 Productivo [FIFCOR3]"
        self.mandante = "700"
        self.usuario = "elopez21334"
        self.password = "Thunderx.2367"
        
        # Directorio de salida base
        self.output_base_dir = r"C:\Data\SAP_Automatizado"
        os.makedirs(self.output_base_dir, exist_ok=True)
        
        # Variables de conexión SAP
        self.sap_gui_auto = None
        self.application = None
        self.connection = None
        self.session = None
        
        # Fechas de procesamiento
        self.fecha_ejecucion = datetime.now()
        self.fecha_inicio, self.fecha_fin = self.calcular_fechas_procesamiento()
        
        # Configuración de reportes
        self.reportes_config = {
            'mb51': {
                'transaccion': 'mb51',
                'archivo_base': 'mb51_traslado_tical',
                'tiene_fechas': True,
                'campo_fecha_inicio': 'BUDAT-LOW',
                'campo_fecha_fin': 'BUDAT-HIGH'
            },
            'rep_plr': {
                'transaccion': 'zsd_rep_planeamiento',
                'archivo_base': 'rep_plr',
                'tiene_fechas': False,
                'campo_fecha_inicio': None,
                'campo_fecha_fin': None
            },
            'y_dev_45': {
                'transaccion': 'y_dev_45',
                'archivo_base': 'y_dev_45',
                'tiene_fechas': False,
                'campo_fecha_inicio': None,
                'campo_fecha_fin': None
            },
            'y_dev_74': {
                'transaccion': 'y_dev_74',
                'archivo_base': 'y_dev_74',
                'tiene_fechas': True,
                'campo_fecha_inicio': 'SP$00002-LOW',
                'campo_fecha_fin': None
            },
            'y_dev_82': {
                'transaccion': 'y_dev_82',
                'archivo_base': 'y_dev_82',
                'tiene_fechas': True,
                'campo_fecha_inicio': 'SP$00005-LOW',
                'campo_fecha_fin': None
            },
            'z_devo_alv': {
                'transaccion': 'z_devo_alv',
                'archivo_base': 'zsd_devo_alv',
                'tiene_fechas': False,
                'campo_fecha_inicio': None,
                'campo_fecha_fin': None
            },
            'zhbo': {
                'transaccion': 'zhbo',
                'archivo_base': 'zhbo',
                'tiene_fechas': False,
                'campo_fecha_inicio': None,
                'campo_fecha_fin': None
            },
            'zred': {
                'transaccion': 'zred',
                'archivo_base': 'zred',
                'tiene_fechas': True,
                'campo_fecha_inicio': 'SO_FECHA-LOW',
                'campo_fecha_fin': 'SO_FECHA-HIGH'
            },
            'zsd_incidencias': {
                'transaccion': 'zsd_incidencias',
                'archivo_base': 'data_incidencias',
                'tiene_fechas': False,
                'campo_fecha_inicio': None,
                'campo_fecha_fin': None
            }
        }

    def calcular_fechas_procesamiento(self):
        """
        Calcula las fechas de procesamiento según la lógica:
        - Si es lunes: procesar sábado y domingo
        - Si es otro día: procesar el día anterior
        """
        hoy = datetime.now()
        
        if hoy.weekday() == 0:  # Lunes
            # Procesar sábado y domingo
            fecha_fin = hoy - timedelta(days=1)  # Domingo
            fecha_inicio = hoy - timedelta(days=2)  # Sábado
            logger.info(f"📅 Lunes detectado: Procesando sábado ({fecha_inicio.strftime('%d.%m.%Y')}) y domingo ({fecha_fin.strftime('%d.%m.%Y')})")
        else:
            # Procesar el día anterior
            fecha_inicio = hoy - timedelta(days=1)
            fecha_fin = fecha_inicio
            logger.info(f"📅 Día {['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][hoy.weekday()]}: Procesando día anterior ({fecha_inicio.strftime('%d.%m.%Y')})")
        
        return fecha_inicio, fecha_fin

    def conectar_sap(self):
        """
        Establece conexión con SAP GUI
        """
        try:
            logger.info("🔐 Iniciando conexión con SAP...")
            self.sap_gui_auto = win32com.client.GetObject("SAPGUI")
            if not self.sap_gui_auto:
                raise Exception("SAP GUI no está disponible")
            
            self.application = self.sap_gui_auto.GetScriptingEngine
            self.connection = self.application.OpenConnection(self.sap_system, True)
            self.session = self.connection.Children(0)
            
            # Iniciar sesión
            self.session.findById("wnd[0]/usr/txtRSYST-MANDT").text = self.mandante
            self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = self.usuario
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = self.password
            self.session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "ES"
            self.session.findById("wnd[0]").sendVKey(0)
            
            logger.info("✅ Sesión SAP iniciada correctamente")
            time.sleep(2)  # Esperar estabilización
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al conectar con SAP: {e}")
            return False

    def ejecutar_reporte(self, nombre_reporte, config):
        """
        Ejecuta un reporte específico de SAP
        """
        try:
            logger.info(f"📊 Ejecutando reporte: {nombre_reporte}")
            
            # Crear directorio específico para este reporte
            reporte_dir = os.path.join(self.output_base_dir, nombre_reporte)
            os.makedirs(reporte_dir, exist_ok=True)
            logger.info(f"📁 Directorio del reporte: {reporte_dir}")
            
            # Nombre del archivo con fecha
            fecha_str = self.fecha_ejecucion.strftime('%Y%m%d')
            nombre_archivo = f"{config['archivo_base']}_{fecha_str}.xls"
            ruta_completa = os.path.join(reporte_dir, nombre_archivo)
            
            # Eliminar archivo existente si existe
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)
            
            # Maximizar ventana
            self.session.findById("wnd[0]").maximize()
            
            # Ir a la transacción
            self.session.findById("wnd[0]/tbar[0]/okcd").text = config['transaccion']
            self.session.findById("wnd[0]").sendVKey(0)
            
            # Esperar que cargue la transacción
            time.sleep(2)
            
            # Configurar fechas si el reporte las requiere
            if config['tiene_fechas']:
                self.configurar_fechas(config)
            
            # Ejecutar el reporte
            self.session.findById("wnd[0]/tbar[1]/btn[8]").press()
            
            # Esperar que se genere el reporte
            time.sleep(5)
            
            # Exportar a Excel
            self.exportar_a_excel(ruta_completa)
            
            # Verificar que el archivo se creó
            if os.path.exists(ruta_completa):
                tamaño = os.path.getsize(ruta_completa)
                logger.info(f"✅ Reporte {nombre_reporte} exportado exitosamente: {nombre_archivo} ({tamaño:,} bytes)")
                
                # Procesar para Power BI en el mismo directorio
                if self.procesar_archivo_para_powerbi(ruta_completa, reporte_dir):
                    logger.info(f"✅ Archivos Power BI generados para {nombre_reporte}")
                
                return True
            else:
                logger.error(f"❌ No se pudo crear el archivo para {nombre_reporte}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando reporte {nombre_reporte}: {e}")
            return False

    def configurar_fechas(self, config):
        """
        Configura las fechas en el reporte SAP
        """
        try:
            fecha_inicio_str = self.fecha_inicio.strftime('%d.%m.%Y')
            fecha_fin_str = self.fecha_fin.strftime('%d.%m.%Y')
            
            # Configurar fecha de inicio
            if config['campo_fecha_inicio']:
                self.session.findById(f"wnd[0]/usr/ctxt{config['campo_fecha_inicio']}").text = fecha_inicio_str
            
            # Configurar fecha de fin
            if config['campo_fecha_fin']:
                self.session.findById(f"wnd[0]/usr/ctxt{config['campo_fecha_fin']}").text = fecha_fin_str
            
            logger.info(f"📅 Fechas configuradas: {fecha_inicio_str} - {fecha_fin_str}")
            
        except Exception as e:
            logger.error(f"❌ Error configurando fechas: {e}")

    def exportar_a_excel(self, ruta_archivo):
        """
        Exporta el reporte actual a Excel
        """
        try:
            # Ir al menú de exportar
            self.session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
            
            # Seleccionar Excel
            self.session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
            self.session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            
            # Configurar ruta y nombre de archivo
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(ruta_archivo)
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = os.path.basename(ruta_archivo)
            self.session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            
            # Esperar que se complete la exportación
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Error exportando a Excel: {e}")

    def procesar_archivo_para_powerbi(self, ruta_archivo, directorio_destino=None):
        """
        Procesa el archivo exportado para hacerlo compatible con Power BI
        Basado en la estructura específica de los archivos SAP de la carpeta data
        
        Args:
            ruta_archivo: Ruta del archivo original
            directorio_destino: Directorio donde guardar los archivos Power BI (opcional)
        """
        try:
            logger.info(f"📊 Procesando archivo SAP: {os.path.basename(ruta_archivo)}")
            
            # Leer el archivo línea por línea
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
            lines = None
            
            for encoding in encodings_to_try:
                try:
                    with open(ruta_archivo, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    logger.info(f"📄 Archivo leído con encoding: {encoding}")
                    break
                except Exception:
                    continue
            
            if lines is None:
                logger.error(f"❌ No se pudo leer el archivo con ningún encoding")
                return False
            
            logger.info(f"📄 Total de líneas en archivo: {len(lines)}")
            
            # Buscar la línea de encabezados (línea con tabs que contiene títulos de columnas)
            header_line_idx = None
            fecha_reporte = None
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Detectar fecha del reporte (primera línea con formato de fecha)
                if fecha_reporte is None and ('2025' in line_stripped or '2024' in line_stripped):
                    fecha_reporte = line_stripped
                    logger.info(f"📅 Fecha del reporte detectada: {fecha_reporte}")
                
                # Detectar línea de encabezados (contiene tabs y no está vacía)
                if '\t' in line_stripped and line_stripped and not line_stripped.startswith(' '):
                    # Verificar que no sea una línea de datos (no debe empezar con espacios o números)
                    if not line_stripped.startswith('\t') and not any(line_stripped.startswith(str(x)) for x in range(10)):
                        header_line_idx = i
                        logger.info(f"📋 Encabezados encontrados en línea {i+1}")
                        break
            
            if header_line_idx is None:
                logger.error("❌ No se encontró la línea de encabezados")
                return False
            
            # Extraer encabezados
            header_line = lines[header_line_idx].strip()
            headers = [col.strip() for col in header_line.split('\t') if col.strip()]
            logger.info(f"📋 Columnas detectadas: {len(headers)} - {headers[:5]}...")
            
            # Extraer datos (líneas después del encabezado)
            data_rows = []
            for i in range(header_line_idx + 1, len(lines)):
                line = lines[i].strip()
                
                # Saltar líneas vacías o que no contengan datos
                if not line or line.startswith('La lista no contiene datos'):
                    continue
                
                # Procesar línea de datos
                row_data = line.split('\t')
                
                # Asegurar que tenga el mismo número de columnas que los encabezados
                if len(row_data) >= len(headers):
                    # Truncar o completar según sea necesario
                    if len(row_data) > len(headers):
                        row_data = row_data[:len(headers)]
                    else:
                        row_data.extend([''] * (len(headers) - len(row_data)))
                    
                    data_rows.append(row_data)
                else:
                    # Línea con menos columnas, completar con valores vacíos
                    row_data.extend([''] * (len(headers) - len(row_data)))
                    data_rows.append(row_data)
            
            logger.info(f"📊 Filas de datos encontradas: {len(data_rows)}")
            
            if not data_rows:
                logger.warning("⚠️ No se encontraron datos en el archivo")
                # Crear DataFrame vacío con los encabezados
                df = pd.DataFrame(columns=headers)
            else:
                # Crear DataFrame
                df = pd.DataFrame(data_rows, columns=headers)
            
            # Limpiar DataFrame
            df = df.dropna(how='all').reset_index(drop=True)
            
            # Limpiar nombres de columnas (remover espacios extra, caracteres especiales)
            df.columns = [col.strip().replace('\n', '').replace('\r', '') for col in df.columns]
            
            logger.info(f"✅ DataFrame creado: {df.shape[0]} filas, {df.shape[1]} columnas")
            
            # Determinar directorio de destino
            if directorio_destino is None:
                directorio_destino = self.output_base_dir
            
            # Crear archivos Power BI
            base_name = os.path.splitext(os.path.basename(ruta_archivo))[0]
            excel_path = os.path.join(directorio_destino, f"{base_name}_PowerBI.xlsx")
            csv_path = os.path.join(directorio_destino, f"{base_name}_PowerBI.csv")
            parquet_path = os.path.join(directorio_destino, f"{base_name}_PowerBI.parquet")
            
            # Guardar en múltiples formatos
            try:
                df.to_excel(excel_path, index=False, engine='openpyxl')
                logger.info(f"📊 Excel guardado: {excel_path}")
            except Exception as e:
                logger.warning(f"⚠️ Error guardando Excel: {e}")
            
            try:
                df.to_csv(csv_path, index=False, encoding='utf-8')
                logger.info(f"📊 CSV guardado: {csv_path}")
            except Exception as e:
                logger.warning(f"⚠️ Error guardando CSV: {e}")
            
            try:
                df.to_parquet(parquet_path, index=False)
                logger.info(f"📊 Parquet guardado: {parquet_path}")
            except Exception as e:
                logger.warning(f"⚠️ Error guardando Parquet: {e}")
            
            # Crear metadatos detallados
            metadata = {
                'archivo_original': os.path.basename(ruta_archivo),
                'fecha_procesamiento': self.fecha_ejecucion.isoformat(),
                'fecha_datos_inicio': self.fecha_inicio.isoformat(),
                'fecha_datos_fin': self.fecha_fin.isoformat(),
                'fecha_reporte_sap': fecha_reporte,
                'filas': len(df),
                'columnas': len(df.columns),
                'columnas_info': {col: str(df[col].dtype) for col in df.columns},
                'muestra_datos': df.head(3).to_dict('records') if len(df) > 0 else [],
                'estadisticas': {
                    'filas_vacias': df.isnull().all(axis=1).sum(),
                    'columnas_vacias': df.isnull().all(axis=0).sum(),
                    'memoria_uso': df.memory_usage(deep=True).sum()
                }
            }
            
            metadata_path = os.path.join(directorio_destino, f"{base_name}_Metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Archivo Power BI procesado exitosamente: {base_name}")
            logger.info(f"📊 Archivos generados:")
            logger.info(f"   • Excel: {excel_path}")
            logger.info(f"   • CSV: {csv_path}")
            logger.info(f"   • Parquet: {parquet_path}")
            logger.info(f"   • Metadata: {metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando archivo para Power BI: {e}")
            return False

    def ejecutar_todos_los_reportes(self):
        """
        Ejecuta todos los reportes configurados
        """
        logger.info("🚀 INICIANDO AUTOMATIZACIÓN COMPLETA DE REPORTES SAP")
        logger.info("=" * 80)
        logger.info(f"📅 Fecha de ejecución: {self.fecha_ejecucion.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📊 Período de datos: {self.fecha_inicio.strftime('%d.%m.%Y')} - {self.fecha_fin.strftime('%d.%m.%Y')}")
        logger.info(f"📁 Directorio base de salida: {self.output_base_dir}")
        logger.info("=" * 80)
        
        resultados = {}
        
        for nombre_reporte, config in self.reportes_config.items():
            logger.info(f"\n📊 Procesando reporte: {nombre_reporte}")
            logger.info("-" * 50)
            
            # Ejecutar reporte
            exito = self.ejecutar_reporte(nombre_reporte, config)
            
            if exito:
                resultados[nombre_reporte] = "✅ Exitoso"
            else:
                resultados[nombre_reporte] = "❌ Fallido"
            
            # Esperar entre reportes
            time.sleep(2)
        
        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("📋 RESUMEN DE EJECUCIÓN")
        logger.info("=" * 80)
        
        exitosos = 0
        fallidos = 0
        
        for reporte, resultado in resultados.items():
            logger.info(f"{resultado} {reporte}")
            if "✅" in resultado:
                exitosos += 1
            else:
                fallidos += 1
        
        logger.info("-" * 50)
        logger.info(f"📊 Total exitosos: {exitosos}")
        logger.info(f"📊 Total fallidos: {fallidos}")
        logger.info(f"📊 Porcentaje éxito: {(exitosos/(exitosos+fallidos)*100):.1f}%")
        logger.info("=" * 80)
        
        return exitosos == len(self.reportes_config)

    def cerrar_sesion_sap(self):
        """
        Cierra la sesión de SAP
        """
        try:
            if self.session:
                self.session.findById("wnd[0]/tbar[0]/btn[15]").press()
                logger.info("🔐 Sesión SAP cerrada")
        except Exception as e:
            logger.warning(f"⚠️ Error cerrando sesión SAP: {e}")

    def main(self):
        """
        Función principal
        """
        try:
            # Conectar a SAP
            if not self.conectar_sap():
                return False
            
            # Ejecutar todos los reportes
            exito = self.ejecutar_todos_los_reportes()
            
            return exito
            
        except Exception as e:
            logger.error(f"❌ Error en ejecución principal: {e}")
            return False
        
        finally:
            # Cerrar sesión
            self.cerrar_sesion_sap()

if __name__ == "__main__":
    automatizacion = AutomatizacionSAP()
    
    try:
        exito = automatizacion.main()
        if exito:
            print("\n🎉 AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE")
            print("📁 Archivos generados en:", automatizacion.output_base_dir)
        else:
            print("\n❌ AUTOMATIZACIÓN FALLÓ")
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
