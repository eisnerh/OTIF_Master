#!/usr/bin/env python3
"""
Script para ejecutar transacción Z_DEVO_ALV (Devoluciones ALV)
Basado en z_devo_alv.vba
"""

import sys
import os
from datetime import datetime
from base_sap_script import BaseSAPScript

class ZDevoALVScript(BaseSAPScript):
    """
    Script para transacción Z_DEVO_ALV
    """
    
    def __init__(self, output_path="C:\\data"):
        super().__init__("Z_DEVO_ALV", output_path)
        self.transaction_code = "zsd_devo_alv"
        self.filename = "z_devo_alv.xls"
        self.row_number = 1
    
    def execute(self):
        """
        Ejecuta la transacción Z_DEVO_ALV
        """
        print("INICIANDO SCRIPT Z_DEVO_ALV")
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
                print("❌ FALLO: No se pudo presionar botón de selección")
                return False
            
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
            print("🎉 PROCESO Z_DEVO_ALV COMPLETADO EXITOSAMENTE")
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
    script = ZDevoALVScript(output_path)
    success = script.execute()
    
    if success:
        print("\n✅ Script Z_DEVO_ALV ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Script Z_DEVO_ALV falló")
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
