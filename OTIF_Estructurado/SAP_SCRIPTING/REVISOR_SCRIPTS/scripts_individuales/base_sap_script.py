#!/usr/bin/env python3
"""
Script base para automatización SAP
Contiene la funcionalidad común para todos los scripts SAP
"""

import win32com.client
import time
import os
from datetime import datetime, timedelta
import logging

class BaseSAPScript:
    """
    Clase base para scripts de automatización SAP
    """
    
    def __init__(self, script_name, output_path="C:\\data"):
        """
        Inicializa el script SAP
        
        Args:
            script_name (str): Nombre del script para logging
            output_path (str): Ruta donde guardar los archivos
        """
        self.script_name = script_name
        self.output_path = output_path
        self.application = None
        self.connection = None
        self.session = None
        self._setup_logging()
        
    def _setup_logging(self):
        """
        Configura el sistema de logging
        """
        log_file = f"{self.script_name}_automation.log"
        
        # Configurar handler para archivo con UTF-8
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Configurar handler para consola sin emojis
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato sin emojis para consola
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Configurar logger
        self.logger = logging.getLogger(self.script_name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def connect_sap(self):
        """
        Establece conexión con SAP GUI usando el método del entorno Nite
        """
        try:
            self.logger.info("Conectando a SAP GUI...")
            
            # Método 1: Intentar conexión directa (como en Nite)
            if self._try_direct_connection():
                return True
            
            # Método 2: Intentar conexión a sesión existente
            if self._try_existing_connection():
                return True
            
            # Método 3: Intentar conexión con credenciales
            if self._try_credential_connection():
                return True
            
            self.logger.error("No se pudo establecer conexión con SAP")
            return False
            
        except Exception as e:
            self.logger.error(f"Error conectando a SAP: {e}")
            return False
    
    def _try_direct_connection(self):
        """
        Intenta conexión directa como en el entorno Nite
        """
        try:
            self.logger.info("Intentando conexión directa...")
            
            # Obtener objeto SAP GUI
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            self.application = sap_gui_auto.GetScriptingEngine
            
            # Obtener conexión y sesión
            self.connection = self.application.Children(0)
            self.session = self.connection.Children(0)
            
            # Maximizar ventana
            self.session.findById("wnd[0]").maximize()
            
            self.logger.info("Conexión directa establecida correctamente")
            return True
            
        except Exception as e:
            self.logger.warning(f"Conexión directa falló: {e}")
            return False
    
    def _try_existing_connection(self):
        """
        Intenta usar conexión existente
        """
        try:
            self.logger.info("Intentando usar conexión existente...")
            
            # Obtener objeto SAP GUI
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            self.application = sap_gui_auto.GetScriptingEngine
            
            # Obtener conexión y sesión
            self.connection = self.application.Children(0)
            self.session = self.connection.Children(0)
            
            # Verificar que la sesión esté activa
            self.session.findById("wnd[0]").maximize()
            
            self.logger.info("Conexión existente establecida correctamente")
            return True
            
        except Exception as e:
            self.logger.warning(f"Conexión existente falló: {e}")
            return False
    
    def _try_credential_connection(self):
        """
        Intenta conexión con credenciales (como en loguearse_simple.py)
        """
        try:
            self.logger.info("Intentando conexión con credenciales...")
            
            # Parámetros de conexión (del entorno Nite)
            sap_system = "SAP R/3 Productivo [FIFCOR3]"
            mandante = "700"
            usuario = "elopez21334"
            password = "Thunderx.2367"
            
            # Conectar al SAP GUI
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            if not sap_gui_auto:
                self.logger.error("SAP GUI no está disponible")
                return False
            
            self.application = sap_gui_auto.GetScriptingEngine
            self.connection = self.application.OpenConnection(sap_system, True)
            self.session = self.connection.Children(0)
            
            # Iniciar sesión
            self.session.findById("wnd[0]/usr/txtRSYST-MANDT").text = mandante
            self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = usuario
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
            self.session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "ES"
            self.session.findById("wnd[0]").sendVKey(0)
            
            # Maximizar ventana
            self.session.findById("wnd[0]").maximize()
            
            self.logger.info("Conexión con credenciales establecida correctamente")
            return True
            
        except Exception as e:
            self.logger.warning(f"Conexión con credenciales falló: {e}")
            return False
    
    def navigate_to_transaction(self, transaction_code):
        """
        Navega a una transacción SAP específica
        
        Args:
            transaction_code (str): Código de la transacción SAP
        """
        try:
            self.logger.info(f"Navegando a transacción: {transaction_code}")
            self.session.findById("wnd[0]/tbar[0]/okcd").text = transaction_code
            self.session.findById("wnd[0]").sendVKey(0)
            return True
        except Exception as e:
            self.logger.error(f"Error navegando a transacción {transaction_code}: {e}")
            return False
    
    def select_node(self, node_id):
        """
        Selecciona un nodo específico en la interfaz
        
        Args:
            node_id (str): ID del nodo a seleccionar
        """
        try:
            self.logger.info(f"Seleccionando nodo: {node_id}")
            self.session.findById("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode(node_id)
            return True
        except Exception as e:
            self.logger.error(f"Error seleccionando nodo {node_id}: {e}")
            return False
    
    def press_selection_button(self):
        """
        Presiona el botón de selección
        """
        try:
            self.session.findById("wnd[0]/tbar[1]/btn[17]").press
            return True
        except Exception as e:
            self.logger.error(f"Error presionando botón de selección: {e}")
            return False
    
    def clear_user_field(self):
        """
        Limpia el campo de usuario si existe
        """
        try:
            self.session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
            self.session.findById("wnd[1]/usr/txtENAME-LOW").setFocus
            self.session.findById("wnd[1]/usr/txtENAME-LOW").caretPosition = 0
            self.session.findById("wnd[1]/tbar[0]/btn[8]").press
            return True
        except:
            # Campo puede no existir en todas las transacciones
            return True
    
    def select_row(self, row_number):
        """
        Selecciona una fila específica en la lista
        
        Args:
            row_number (int): Número de fila a seleccionar
        """
        try:
            self.logger.info(f"Seleccionando fila: {row_number}")
            
            # Intentar diferentes métodos de selección
            try:
                # Método 1: Selección directa
                shell = self.session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
                shell.currentCellRow = row_number
                shell.selectedRows = str(row_number)
                shell.doubleClickCurrentCell()
                return True
            except:
                try:
                    # Método 2: Selección alternativa
                    shell = self.session.findById("wnd[0]/usr/cntlALV_CONTAINER_1/shellcont/shell")
                    shell.currentCellRow = row_number
                    shell.selectedRows = str(row_number)
                    shell.doubleClickCurrentCell()
                    return True
                except:
                    try:
                        # Método 3: Selección con grid
                        grid = self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
                        grid.setCurrentCell(row_number, "ZONA")
                        grid.selectedRows = str(row_number)
                        grid.doubleClickCurrentCell()
                        return True
                    except:
                        # Método 4: Selección simple
                        self.session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = str(row_number)
                        return True
            
        except Exception as e:
            self.logger.error(f"Error seleccionando fila {row_number}: {e}")
            # Intentar continuar sin selección específica
            self.logger.info("Intentando continuar sin selección específica...")
            return True
    
    def set_date_field(self, field_name, date_value):
        """
        Establece un campo de fecha
        
        Args:
            field_name (str): Nombre del campo de fecha
            date_value (str): Valor de la fecha
        """
        try:
            self.logger.info(f"Estableciendo fecha {field_name}: {date_value}")
            date_field = f"wnd[0]/usr/ctxt{field_name}"
            self.session.findById(date_field).text = date_value
            self.session.findById(date_field).setFocus
            self.session.findById(date_field).caretPosition = 2
            return True
        except Exception as e:
            self.logger.error(f"Error estableciendo fecha {field_name}: {e}")
            return False
    
    def execute_report(self):
        """
        Ejecuta el reporte
        """
        try:
            self.logger.info("Ejecutando reporte...")
            self.session.findById("wnd[0]/tbar[1]/btn[8]").press
            return True
        except Exception as e:
            self.logger.error(f"Error ejecutando reporte: {e}")
            return False
    
    def export_to_excel(self, filename):
        """
        Exporta el reporte a Excel con múltiples métodos alternativos
        
        Args:
            filename (str): Nombre del archivo de salida
        """
        try:
            self.logger.info(f"Exportando a Excel: {filename}")
            
            # Método 1: Intentar exportación estándar
            if self._try_standard_export(filename):
                return True
            
            # Método 2: Intentar exportación desde grilla
            if self._try_grid_export(filename):
                return True
            
            # Método 3: Intentar exportación desde menú contextual
            if self._try_context_menu_export(filename):
                return True
            
            # Método 4: Intentar exportación con atajo de teclado
            if self._try_keyboard_export(filename):
                return True
            
            self.logger.error("Todos los métodos de exportación fallaron")
            return False
            
        except Exception as e:
            self.logger.error(f"Error exportando archivo {filename}: {e}")
            return False
    
    def _try_standard_export(self, filename):
        """
        Intenta exportación estándar desde menú (método del entorno Nite)
        """
        try:
            self.logger.info("Intentando exportación estándar...")
            
            # Crear directorio de salida si no existe
            os.makedirs(self.output_path, exist_ok=True)
            
            # Ir al menú de exportación
            self.session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
            
            # Seleccionar formato Excel
            self.session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
            self.session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            
            # Configurar ruta y nombre de archivo (método del entorno Nite)
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = self.output_path
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
            self.session.findById("wnd[1]").sendVKey(4)  # F4 para explorar
            self.session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = filename
            self.session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").text = "0000"
            self.session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = len(filename)
            self.session.findById("wnd[2]/tbar[0]/btn[0]").press()
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()
            
            # Esperar a que se complete la exportación
            time.sleep(3)
            
            self.logger.info(f"Archivo exportado con método estándar: {filename}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Exportación estándar falló: {e}")
            return False
    
    def _try_grid_export(self, filename):
        """
        Intenta exportación desde la grilla
        """
        try:
            self.logger.info("Intentando exportación desde grilla...")
            
            # Seleccionar toda la grilla
            grid = self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
            grid.selectAll()
            
            # Menú contextual
            grid.contextMenu()
            
            # Seleccionar exportar
            self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&XXL")
            
            # Configurar archivo
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = self.output_path
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = filename
            self.session.findById("wnd[1]/tbar[0]/btn[11]").press
            
            self.logger.info(f"Archivo exportado desde grilla: {filename}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Exportación desde grilla falló: {e}")
            return False
    
    def _try_context_menu_export(self, filename):
        """
        Intenta exportación desde menú contextual
        """
        try:
            self.logger.info("Intentando exportación desde menú contextual...")
            
            # Hacer clic derecho en la grilla
            grid = self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
            grid.rightClick()
            
            # Buscar opción de exportación
            try:
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&EXPORT")
            except:
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectContextMenuItem("&EXCEL")
            
            # Configurar archivo
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = self.output_path
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = filename
            self.session.findById("wnd[1]/tbar[0]/btn[11]").press
            
            self.logger.info(f"Archivo exportado desde menú contextual: {filename}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Exportación desde menú contextual falló: {e}")
            return False
    
    def _try_keyboard_export(self, filename):
        """
        Intenta exportación usando atajos de teclado
        """
        try:
            self.logger.info("Intentando exportación con atajos de teclado...")
            
            # Usar Ctrl+E para exportar
            self.session.findById("wnd[0]").sendVKey(5)  # Ctrl+E
            
            # Configurar archivo
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = self.output_path
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = filename
            self.session.findById("wnd[1]/tbar[0]/btn[11]").press
            
            self.logger.info(f"Archivo exportado con atajo de teclado: {filename}")
            return True
            
        except Exception as e:
            self.logger.warning(f"Exportación con atajo de teclado falló: {e}")
            return False
    
    def verify_output_file(self, filename):
        """
        Verifica que el archivo se haya generado correctamente
        
        Args:
            filename (str): Nombre del archivo a verificar
        """
        file_path = os.path.join(self.output_path, filename)
        
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            self.logger.info(f"{filename} - {size:,} bytes")
            return True
        else:
            self.logger.error(f"{filename} - No encontrado")
            return False
    
    def process_for_powerbi(self, filename):
        """
        Procesa el archivo generado para Power BI
        
        Args:
            filename (str): Nombre del archivo a procesar
        """
        try:
            self.logger.info(f"Procesando {filename} para Power BI...")
            
            # Importar el procesador de datos
            from procesar_datos_sap import ProcesadorDatosSAP
            
            # Crear procesador
            procesador = ProcesadorDatosSAP(self.output_path)
            
            # Procesar archivo
            file_path = os.path.join(self.output_path, filename)
            output_name = os.path.splitext(filename)[0] + "_PowerBI"
            
            success = procesador.procesar_archivo_sap(file_path, output_name)
            
            if success:
                self.logger.info(f"{filename} procesado para Power BI")
                return True
            else:
                self.logger.error(f"Error procesando {filename} para Power BI")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en procesamiento Power BI: {e}")
            return False
    
    def get_today_date(self):
        """
        Obtiene la fecha de hoy en formato SAP (DD.MM.YYYY)
        """
        return datetime.now().strftime("%d.%m.%Y")
    
    def get_dynamic_date(self):
        """
        Obtiene la fecha dinámica según la lógica de negocio:
        - Si es lunes: ejecutar sábado y domingo (fecha del sábado)
        - Para otros días: un día atrás
        """
        today = datetime.now()
        weekday = today.weekday()  # 0=Lunes, 1=Martes, ..., 6=Domingo
        
        if weekday == 0:  # Lunes
            # Si es lunes, ejecutar sábado (2 días atrás)
            target_date = today - timedelta(days=2)
            self.logger.info("Es lunes - ejecutando reporte del sábado")
        else:
            # Para otros días, un día atrás
            target_date = today - timedelta(days=1)
            self.logger.info(f"Día {today.strftime('%A')} - ejecutando reporte de ayer")
        
        return target_date.strftime("%d.%m.%Y")
    
    def cleanup(self):
        """
        Limpia recursos y cierra conexiones
        """
        try:
            if self.session:
                self.session.findById("wnd[0]/tbar[0]/btn[15]").press
            self.logger.info("Limpieza completada")
        except:
            pass
