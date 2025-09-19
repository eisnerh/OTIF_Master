#!/usr/bin/env python3
"""
Script que ejecuta solo el procesamiento de archivos para Power BI
(sin conexión a SAP)
"""

import os
import sys
from datetime import datetime

def main():
    """
    Ejecuta el procesamiento de archivos directamente
    """
    print("PROCESAMIENTO DE ARCHIVOS PARA POWER BI")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Importar y ejecutar directamente el procesamiento
        from procesar_sap_especial import process_sap_file, transform_data_for_powerbi, save_powerbi_files
        
        print("Ejecutando procesamiento de archivo SAP...")
        
        # Ejecutar el procesamiento
        success = process_sap_file()
        
        if success:
            print("\nPROCESAMIENTO COMPLETADO EXITOSAMENTE")
            print("Archivos generados en: C:\\Data\\Nite")
            print("Archivos disponibles:")
            print("  - REP_PLR_HOY_PowerBI.xlsx")
            print("  - REP_PLR_HOY_PowerBI.csv") 
            print("  - REP_PLR_HOY_PowerBI.parquet")
            print("  - REP_PLR_HOY_Metadata.json")
        else:
            print("\nFALLO EN EL PROCESAMIENTO")
            
        print(f"Hora de finalizacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        return success
        
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nProcesamiento interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
