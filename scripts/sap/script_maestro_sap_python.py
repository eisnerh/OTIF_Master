#!/usr/bin/env python3
"""
Script maestro en Python que integra toda la lógica de los scripts VBA de data_script_sap
Este script automatiza la ejecución de múltiples transacciones SAP y exporta los reportes
"""

import win32com.client
import time
import os
import json
from datetime import datetime, timedelta
import logging

class SAPAutomation:
    """
    Clase principal para automatización de SAP GUI
    """
    
    def __init__(self, config_file="configuracion_sap.json"):
        """
        Inicializa la conexión con SAP GUI
        
        Args:
            config_file (str): Ruta al archivo de configuración
        """
        self.application = None
        self.connection = None
        self.session = None
        self.config = self._load_config(config_file)
        self._setup_logging()
        
    def _load_config(self, config_file):
        """
        Carga la configuración desde archivo JSON
        """
        default_config = {
            "output_path": "C:\\data",
            "encoding": "0000",
            "date_format": "%d.%m.%Y",
            "transactions": {
                "rep_plr": {
                    "transaction": "zsd_rep_planeamiento",
                    "filename": "REP_PLR.xls",
                    "node": "F00120",
                    "row": 11,
                    "date_field": "P_LFDAT-LOW"
                },
                "y_dev_45": {
                    "transaction": "y_dev_42000045",
                    "filename": "y_dev_45.xls",
                    "node": "F00139",
                    "row": 2
                },
                "y_dev_74": {
                    "transaction": "y_dev_42000074",
                    "filename": "y_dev_74.xls",
                    "node": "F00139",
                    "row": 2
                },
                "y_dev_82": {
                    "transaction": "y_dev_42000082",
                    "filename": "y_dev_82.xls",
                    "node": "F00139",
                    "row": 2
                },
                "zred": {
                    "transaction": "zred",
                    "filename": "zred.xls",
                    "row": 1
                },
                "zhbo": {
                    "transaction": "zhbo",
                    "filename": "zhbo.xls",
                    "row": 11,
                    "date_field": "FECHA-LOW"
                },
                "z_devo_alv": {
                    "transaction": "zsd_devo_alv",
                    "filename": "z_devo_alv.xls",
                    "row": 1
                },
                "zsd_incidencias": {
                    "transaction": "zsd_incidencias",
                    "filename": "data_incidencias.xls",
                    "row": 12,
                    "grid_selection": True
                }
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge con configuración por defecto
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"No se pudo cargar configuración: {e}")
        
        return default_config
    
    def _setup_logging(self):
        """
        Configura el sistema de logging
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sap_automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def connect_sap(self):
        """
        Establece conexión con SAP GUI
        """
        try:
            self.logger.info("[SEGURIDAD] Conectando a SAP GUI...")
            
            # Obtener objeto SAP GUI
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            self.application = sap_gui_auto.GetScriptingEngine
            
            # Obtener conexión y sesión
            self.connection = self.application.Children(0)
            self.session = self.connection.Children(0)
            
            # Maximizar ventana
            self.session.findById("wnd[0]").maximize
            
            self.logger.info("[OK] Conexión SAP establecida correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error conectando a SAP: {e}")
            return False
    
    def execute_transaction(self, transaction_name, custom_date=None):
        """
        Ejecuta una transacción SAP específica
        
        Args:
            transaction_name (str): Nombre de la transacción
            custom_date (str): Fecha personalizada (opcional)
        """
        if transaction_name not in self.config["transactions"]:
            self.logger.error(f"[ERROR] Transacción '{transaction_name}' no encontrada en configuración")
            return False
        
        config = self.config["transactions"][transaction_name]
        
        try:
            self.logger.info(f"[DASHBOARD] Ejecutando transacción: {transaction_name}")
            
            # Navegar a la transacción
            self.session.findById("wnd[0]/tbar[0]/okcd").text = config["transaction"]
            self.session.findById("wnd[0]").sendVKey(0)
            
            # Si hay nodo específico, hacer doble click
            if "node" in config:
                self.session.findById("wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell").doubleClickNode(config["node"])
            
            # Presionar botón de selección
            self.session.findById("wnd[0]/tbar[1]/btn[17]").press
            
            # Limpiar campo de usuario si existe
            try:
                self.session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
                self.session.findById("wnd[1]/usr/txtENAME-LOW").setFocus
                self.session.findById("wnd[1]/usr/txtENAME-LOW").caretPosition = 0
                self.session.findById("wnd[1]/tbar[0]/btn[8]").press
            except:
                pass  # Campo puede no existir en todas las transacciones
            
            # Seleccionar fila específica
            if "row" in config:
                self.session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").currentCellRow = config["row"]
                self.session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = str(config["row"])
                self.session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").doubleClickCurrentCell
            
            # Configurar fecha si es necesario
            if "date_field" in config and custom_date:
                date_field = f"wnd[0]/usr/ctxt{config['date_field']}"
                self.session.findById(date_field).text = custom_date
                self.session.findById(date_field).setFocus
                self.session.findById(date_field).caretPosition = 2
            
            # Ejecutar reporte
            self.session.findById("wnd[0]/tbar[1]/btn[8]").press
            
            # Manejo especial para zsd_incidencias
            if transaction_name == "zsd_incidencias" and config.get("grid_selection", False):
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(4, "ZONA")
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "4"
                self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").contextMenu
            
            # Exportar a Excel
            self._export_to_excel(config["filename"])
            
            self.logger.info(f"[OK] Transacción {transaction_name} ejecutada correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error ejecutando transacción {transaction_name}: {e}")
            return False
    
    def _export_to_excel(self, filename):
        """
        Exporta el reporte actual a Excel
        
        Args:
            filename (str): Nombre del archivo de salida
        """
        try:
            # Ir al menú de exportación
            self.session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select
            
            # Seleccionar formato Excel
            self.session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select
            self.session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press
            
            # Configurar ruta y nombre de archivo
            self.session.findById("wnd[1]/usr/ctxtDY_PATH").text = self.config["output_path"]
            self.session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = filename
            self.session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = self.config["encoding"]
            self.session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").setFocus
            self.session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").caretPosition = 4
            
            # Confirmar exportación
            self.session.findById("wnd[1]/tbar[0]/btn[11]").press
            
            # Cerrar ventanas
            self.session.findById("wnd[0]/tbar[0]/btn[3]").press
            self.session.findById("wnd[0]/tbar[0]/btn[15]").press
            
            self.logger.info(f"[CARPETA] Archivo exportado: {filename}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error exportando archivo {filename}: {e}")
            raise
    
    def execute_all_transactions(self, custom_date=None):
        """
        Ejecuta todas las transacciones configuradas
        
        Args:
            custom_date (str): Fecha personalizada para transacciones que la requieren
        """
        if not self.connect_sap():
            return False
        
        results = {}
        total_transactions = len(self.config["transactions"])
        
        self.logger.info(f"[INICIO] Iniciando ejecución de {total_transactions} transacciones")
        
        for i, (transaction_name, config) in enumerate(self.config["transactions"].items(), 1):
            self.logger.info(f"[DASHBOARD] Procesando {i}/{total_transactions}: {transaction_name}")
            
            try:
                success = self.execute_transaction(transaction_name, custom_date)
                results[transaction_name] = success
                
                if success:
                    self.logger.info(f"[OK] {transaction_name} completada")
                else:
                    self.logger.error(f"[ERROR] {transaction_name} falló")
                
                # Pausa entre transacciones
                if i < total_transactions:
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Error inesperado en {transaction_name}: {e}")
                results[transaction_name] = False
        
        # Resumen final
        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"[LISTA] Resumen: {successful}/{total_transactions} transacciones exitosas")
        
        return results
    
    def execute_specific_transactions(self, transaction_list, custom_date=None):
        """
        Ejecuta solo las transacciones especificadas
        
        Args:
            transaction_list (list): Lista de nombres de transacciones
            custom_date (str): Fecha personalizada
        """
        if not self.connect_sap():
            return False
        
        results = {}
        
        for transaction_name in transaction_list:
            if transaction_name not in self.config["transactions"]:
                self.logger.error(f"[ERROR] Transacción '{transaction_name}' no encontrada")
                results[transaction_name] = False
                continue
            
            try:
                success = self.execute_transaction(transaction_name, custom_date)
                results[transaction_name] = success
                
                if success:
                    self.logger.info(f"[OK] {transaction_name} completada")
                else:
                    self.logger.error(f"[ERROR] {transaction_name} falló")
                
                time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Error inesperado en {transaction_name}: {e}")
                results[transaction_name] = False
        
        return results
    
    def get_today_date(self):
        """
        Obtiene la fecha de hoy en formato SAP
        """
        return datetime.now().strftime(self.config["date_format"])
    
    def verify_output_files(self):
        """
        Verifica que los archivos de salida se hayan generado correctamente
        """
        output_path = self.config["output_path"]
        missing_files = []
        
        for transaction_name, config in self.config["transactions"].items():
            filename = config["filename"]
            file_path = os.path.join(output_path, filename)
            
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.logger.info(f"[OK] {filename} - {size:,} bytes")
            else:
                self.logger.error(f"[ERROR] {filename} - No encontrado")
                missing_files.append(filename)
        
        if missing_files:
            self.logger.warning(f"[ADVERTENCIA]  Archivos faltantes: {missing_files}")
            return False
        else:
            self.logger.info("[EXITO] Todos los archivos generados correctamente")
            return True

def main():
    """
    Función principal del script
    """
    print("[INICIO] SCRIPT MAESTRO SAP - AUTOMATIZACIÓN COMPLETA")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Crear instancia del automatizador
    sap_auto = SAPAutomation()
    
    # Obtener fecha de hoy
    today_date = sap_auto.get_today_date()
    print(f"[FECHA] Fecha configurada: {today_date}")
    
    try:
        # Ejecutar todas las transacciones
        results = sap_auto.execute_all_transactions(today_date)
        
        # Verificar archivos generados
        print("\n[LISTA] Verificando archivos generados...")
        sap_auto.verify_output_files()
        
        # Resumen final
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print("\n" + "=" * 80)
        print("[EXITO] PROCESO COMPLETADO")
        print("=" * 80)
        print(f"[DASHBOARD] Transacciones exitosas: {successful}/{total}")
        print(f"[CARPETA] Archivos generados en: {sap_auto.config['output_path']}")
        print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return successful == total
        
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n[OK] Script ejecutado exitosamente")
            exit(0)
        else:
            print("\n[ERROR] Script falló")
            exit(1)
    except KeyboardInterrupt:
        print("\n[ADVERTENCIA]  Script interrumpido por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        exit(1)
