#!/usr/bin/env python3
"""
Script para ejecutar transacción ZHBO (Reporte HBO)
Basado en zhbo.vba
"""

import sys
import os
from datetime import datetime
from base_sap_script import BaseSAPScript

class ZHBOScript(BaseSAPScript):
    """
    Script para transacción ZHBO
    """
    
    def __init__(self, output_path="C:\\data"):
        super().__init__("ZHBO", output_path)
        self.transaction_code = "zhbo"
        self.filename = "zhbo.xls"
        self.row_number = 11
        self.date_field = "FECHA-LOW"
    
    def execute(self, custom_date=None):
        """
        Ejecuta la transacción ZHBO
        
        Args:
            custom_date (str): Fecha personalizada (opcional)
        """
        print("INICIANDO SCRIPT ZHBO")
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
            
            # Configurar fecha (usar fecha dinámica por defecto)
            date_to_use = custom_date if custom_date else self.get_dynamic_date()
            print(f"Fecha configurada: {date_to_use}")
            if not self.set_date_field(self.date_field, date_to_use):
                print("FALLO: No se pudo configurar la fecha")
                return False
            
            # Ejecutar reporte
            if not self.execute_report():
                print("FALLO: No se pudo ejecutar el reporte")
                return False
            
            # Exportar a Excel
            if not self.export_to_excel(self.filename):
                print("FALLO: No se pudo exportar a Excel")
                return False
            
            # Verificar archivo generado
            if not self.verify_output_file(self.filename):
                print("FALLO: Archivo no se generó correctamente")
                return False
            
            print("\n" + "=" * 60)
            print("PROCESO ZHBO COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Archivo generado: {self.filename}")
            print(f"Ubicación: {self.output_path}")
            print(f"Fecha utilizada: {date_to_use}")
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
    custom_date = None
    output_path = "C:\\data"
    
    if len(sys.argv) > 1:
        custom_date = sys.argv[1]
        print(f"Usando fecha personalizada: {custom_date}")
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        print(f"Usando ruta personalizada: {output_path}")
    
    # Crear y ejecutar script
    script = ZHBOScript(output_path)
    success = script.execute(custom_date)
    
    if success:
        print("\nScript ZHBO ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\nScript ZHBO falló")
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
