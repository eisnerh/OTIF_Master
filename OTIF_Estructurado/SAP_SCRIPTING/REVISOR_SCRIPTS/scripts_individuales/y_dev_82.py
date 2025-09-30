#!/usr/bin/env python3
"""
Script para ejecutar transacción Y_DEV_82 (Devoluciones 82)
Basado en y_dev_82.vba
"""

import sys
import os
from datetime import datetime
from base_sap_script import BaseSAPScript

class YDev82Script(BaseSAPScript):
    """
    Script para transacción Y_DEV_82
    """
    
    def __init__(self, output_path="C:\\data"):
        super().__init__("Y_DEV_82", output_path)
        self.transaction_code = "y_dev_42000082"
        self.filename = "y_dev_82.xls"
        self.node_id = "F00139"
        self.row_number = 2
    
    def execute(self):
        """
        Ejecuta la transacción Y_DEV_82
        """
        print("🚀 INICIANDO SCRIPT Y_DEV_82")
        print("=" * 60)
        print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Conectar a SAP
            if not self.connect_sap():
                print("❌ FALLO: No se pudo conectar a SAP")
                return False
            
            # Navegar a la transacción
            if not self.navigate_to_transaction(self.transaction_code):
                print("❌ FALLO: No se pudo navegar a la transacción")
                return False
            
            # Seleccionar nodo
            if not self.select_node(self.node_id):
                print("❌ FALLO: No se pudo seleccionar el nodo")
                return False
            
            # Presionar botón de selección
            if not self.press_selection_button():
                print("❌ FALLO: No se pudo presionar botón de selección")
                return False
            
            # Limpiar campo de usuario
            self.clear_user_field()
            
            # Seleccionar fila específica
            if not self.select_row(self.row_number):
                print("❌ FALLO: No se pudo seleccionar la fila")
                return False
            
            # Ejecutar reporte
            if not self.execute_report():
                print("❌ FALLO: No se pudo ejecutar el reporte")
                return False
            
            # Exportar a Excel
            if not self.export_to_excel(self.filename):
                print("❌ FALLO: No se pudo exportar a Excel")
                return False
            
            # Verificar archivo generado
            if not self.verify_output_file(self.filename):
                print("❌ FALLO: Archivo no se generó correctamente")
                return False
            
            print("\n" + "=" * 60)
            print("🎉 PROCESO Y_DEV_82 COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"📁 Archivo generado: {self.filename}")
            print(f"📂 Ubicación: {self.output_path}")
            print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
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
        print(f"📂 Usando ruta personalizada: {output_path}")
    
    # Crear y ejecutar script
    script = YDev82Script(output_path)
    success = script.execute()
    
    if success:
        print("\n✅ Script Y_DEV_82 ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Script Y_DEV_82 falló")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Script interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
