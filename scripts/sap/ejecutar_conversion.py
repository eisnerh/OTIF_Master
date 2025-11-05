#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para ejecutar la conversión de archivos XLS a XLSX
"""

import sys
import os
from pathlib import Path

def main():
    """Función principal simplificada"""
    print("="*60)
    print("CONVERSOR DE ARCHIVOS XLS A XLSX")
    print("Sistema OTIF - Extracciones SAP")
    print("="*60)
    
    # Verificar que el script principal existe
    script_principal = Path(r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\convertir_xls_a_xlsx.py")
    if not script_principal.exists():
        print("[ERROR] Error: No se encontró el script 'convertir_xls_a_xlsx.py'")
        print("   Asegúrate de que esté en el mismo directorio.")
        return 1
    
    # Verificar que la carpeta de datos existe
    carpeta_datos = Path(r"C:\data\SAP_Extraction")
    if not carpeta_datos.exists():
        print("[ERROR] Error: No se encontró la carpeta 'C:\data\SAP_Extraction'")
        print("   Asegúrate de ejecutar el script desde el directorio raíz del proyecto.")
        return 1
    
    print("[OK] Verificaciones completadas")
    print("[CARPETA] Carpeta de datos encontrada:", carpeta_datos)
    print("[INICIO] Iniciando conversión...")
    print()
    
    try:
        # Importar y ejecutar el script principal
        import convertir_xls_a_xlsx
        
        # Crear instancia del convertidor
        convertidor = convertir_xls_a_xlsx.ConvertidorXLS()
        
        # Procesar todos los archivos
        resumen = convertidor.procesar_todos()
        
        print()
        print("[EXITO] ¡Conversión completada!")
        print(f"[DASHBOARD] Archivos procesados: {resumen['total_archivos']}")
        print(f"[OK] Exitosos: {resumen['total_exitosos']}")
        print(f"[ERROR] Fallidos: {resumen['total_fallidos']}")
        
        if resumen['total_fallidos'] > 0:
            print("\n[ADVERTENCIA]  Algunos archivos fallaron. Revisa el log para más detalles.")
            return 1
        else:
            print("\n[OBJETIVO] ¡Todos los archivos se convirtieron exitosamente!")
            return 0
            
    except Exception as e:
        print(f"[ERROR] Error durante la conversión: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
