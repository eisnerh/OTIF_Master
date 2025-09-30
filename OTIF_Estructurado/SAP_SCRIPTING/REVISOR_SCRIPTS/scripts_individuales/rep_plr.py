#!/usr/bin/env python3
"""
Script para ejecutar transacción REP_PLR (Reporte de Planeamiento)
Basado en rep_plr.vba
"""

import sys
import os
from datetime import datetime
from base_sap_script import BaseSAPScript

class REPPLRScript(BaseSAPScript):
    """
    Script para transacción REP_PLR
    """
    
    def __init__(self, output_path="C:\\data"):
        super().__init__("REP_PLR", output_path)
        self.transaction_code = "zsd_rep_planeamiento"
        self.filename = "REP_PLR.xls"
        self.node_id = "F00120"
        self.row_number = 11
        self.date_field = "P_LFDAT-LOW"
    
    def execute(self, custom_date=None):
        """
        Ejecuta la transacción REP_PLR
        
        Args:
            custom_date (str): Fecha personalizada (opcional)
        """
        print("🚀 INICIANDO SCRIPT REP_PLR")
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
            
            # Configurar fecha (usar fecha dinámica por defecto)
            date_to_use = custom_date if custom_date else self.get_dynamic_date()
            print(f"📅 Fecha configurada: {date_to_use}")
            if not self.set_date_field(self.date_field, date_to_use):
                print("❌ FALLO: No se pudo configurar la fecha")
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
            
            # Procesar para Power BI
            print("\n🔄 Procesando archivo para Power BI...")
            if not self.process_for_powerbi(self.filename):
                print("⚠️  ADVERTENCIA: No se pudo procesar para Power BI")
            
            print("\n" + "=" * 60)
            print("🎉 PROCESO REP_PLR COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"📁 Archivo generado: {self.filename}")
            print(f"📊 Archivos Power BI:")
            print(f"   • {os.path.splitext(self.filename)[0]}_PowerBI.xlsx")
            print(f"   • {os.path.splitext(self.filename)[0]}_PowerBI.csv")
            print(f"   • {os.path.splitext(self.filename)[0]}_PowerBI.parquet ⭐")
            print(f"   • {os.path.splitext(self.filename)[0]}_PowerBI_metadata.json")
            print(f"📂 Ubicación: {self.output_path}")
            print(f"📅 Fecha utilizada: {date_to_use}")
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
    custom_date = None
    output_path = "C:\\data"
    
    if len(sys.argv) > 1:
        custom_date = sys.argv[1]
        print(f"📅 Usando fecha personalizada: {custom_date}")
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        print(f"📂 Usando ruta personalizada: {output_path}")
    
    # Crear y ejecutar script
    script = REPPLRScript(output_path)
    success = script.execute(custom_date)
    
    if success:
        print("\n✅ Script REP_PLR ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Script REP_PLR falló")
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
