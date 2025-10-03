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
    script_principal = Path("convertir_xls_a_xlsx.py")
    if not script_principal.exists():
        print("❌ Error: No se encontró el script 'convertir_xls_a_xlsx.py'")
        print("   Asegúrate de que esté en el mismo directorio.")
        return 1
    
    # Verificar que la carpeta de datos existe
    carpeta_datos = Path("Data/SAP_Extraction")
    if not carpeta_datos.exists():
        print("❌ Error: No se encontró la carpeta 'Data/SAP_Extraction'")
        print("   Asegúrate de ejecutar el script desde el directorio raíz del proyecto.")
        return 1
    
    print("✅ Verificaciones completadas")
    print("📁 Carpeta de datos encontrada:", carpeta_datos)
    print("🚀 Iniciando conversión...")
    print()
    
    try:
        # Importar y ejecutar el script principal
        import convertir_xls_a_xlsx
        
        # Crear instancia del convertidor
        convertidor = convertir_xls_a_xlsx.ConvertidorXLS()
        
        # Procesar todos los archivos
        resumen = convertidor.procesar_todos()
        
        print()
        print("🎉 ¡Conversión completada!")
        print(f"📊 Archivos procesados: {resumen['total_archivos']}")
        print(f"✅ Exitosos: {resumen['total_exitosos']}")
        print(f"❌ Fallidos: {resumen['total_fallidos']}")
        
        if resumen['total_fallidos'] > 0:
            print("\n⚠️  Algunos archivos fallaron. Revisa el log para más detalles.")
            return 1
        else:
            print("\n🎯 ¡Todos los archivos se convirtieron exitosamente!")
            return 0
            
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
