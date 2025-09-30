#!/usr/bin/env python3
"""
Script para ejecutar transacción ZSD_INCIDENCIAS (Reporte de Incidencias)
Basado en la configuración encontrada en el sistema
"""

import sys
import os
from datetime import datetime
from base_sap_script import BaseSAPScript

class ZSDIncidenciasScript(BaseSAPScript):
    """
    Script para transacción ZSD_INCIDENCIAS
    """
    
    def __init__(self, output_path="C:\\data"):
        super().__init__("ZSD_INCIDENCIAS", output_path)
        self.transaction_code = "zsd_incidencias"
        self.filename = "data_incidencias.xls"
        self.row_number = 12
    
    def select_grid_cell(self):
        """
        Selecciona una celda específica en la grilla (paso especial para incidencias)
        """
        try:
            self.logger.info("Seleccionando celda en grilla...")
            self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").setCurrentCell(4, "ZONA")
            self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").selectedRows = "4"
            self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell").contextMenu
            return True
        except Exception as e:
            self.logger.error(f"Error seleccionando celda en grilla: {e}")
            return False
    
    def execute(self):
        """
        Ejecuta la transacción ZSD_INCIDENCIAS
        """
        print("INICIANDO SCRIPT ZSD_INCIDENCIAS")
        print("=" * 60)
        print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Conectar a SAP
            if not self.connect_sap():
                print("FALLO: No se pudo conectar a SAP")
                return False
            
            # Navegar a la transacción
            if not self.navigate_to_transaction(self.transaction_code):
                print("FALLO: No se pudo navegar a la transacción")
                return False
            
            # Presionar botón de selección
            if not self.press_selection_button():
                print("FALLO: No se pudo presionar botón de selección")
                return False
            
            # Limpiar campo de usuario
            self.clear_user_field()
            
            # Seleccionar fila específica
            if not self.select_row(self.row_number):
                print("FALLO: No se pudo seleccionar la fila")
                return False
            
            # Ejecutar reporte
            if not self.execute_report():
                print("FALLO: No se pudo ejecutar el reporte")
                return False
            
            # Paso especial: Seleccionar celda en grilla
            if not self.select_grid_cell():
                print("ADVERTENCIA: No se pudo seleccionar celda en grilla, continuando...")
            
            # Exportar a Excel
            if not self.export_to_excel(self.filename):
                print("FALLO: No se pudo exportar a Excel")
                return False
            
            # Verificar archivo generado
            if not self.verify_output_file(self.filename):
                print("FALLO: Archivo no se generó correctamente")
                return False
            
            print("\n" + "=" * 60)
            print("PROCESO ZSD_INCIDENCIAS COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Archivo generado: {self.filename}")
            print(f"Ubicación: {self.output_path}")
            print(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """
    Función principal
    """
    # Verificar argumentos de línea de comandos
    output_path = "C:\\data"
    
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
        print(f"Usando ruta personalizada: {output_path}")
    
    # Crear y ejecutar script
    script = ZSDIncidenciasScript(output_path)
    success = script.execute()
    
    if success:
        print("\nScript ZSD_INCIDENCIAS ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\nScript ZSD_INCIDENCIAS falló")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
