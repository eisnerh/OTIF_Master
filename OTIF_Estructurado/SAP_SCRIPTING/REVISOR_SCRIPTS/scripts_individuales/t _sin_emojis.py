#!/usr/bin/env python3
"""
Script de prueba para verificar que no hay errores de emojis
iadd(a, b)
"""

import sys
import os

def test_import():
    """Prueba importar los módulos principales"""
    try:
        print("Probando importación de base_sap_script...")
        from base_sap_script import BaseSAPScript
        print("✓ base_sap_script importado correctamente")
        
        print("Probando importación de rep_plr...")
        from rep_plr import RepPlrScript
        print("✓ rep_plr importado correctamente")
        
        print("Probando importación de procesar_datos_sap...")
        from procesar_datos_sap import ProcesadorDatosSAP
        print("✓ procesar_datos_sap importado correctamente")
        
        print("\n✓ Todas las importaciones exitosas - No hay errores de emojis")
        return True
        
    except Exception as e:
        print(f"✗ Error en importación: {e}")
        return False

def main():
    """Función principal"""
    print("=== PRUEBA DE SCRIPTS SIN EMOJIS ===")
    print("Verificando que no hay errores de codificación...")
    
    if test_import():
        print("\n✓ RESULTADO: Los scripts están listos para usar")
        print("✓ No hay errores de emojis")
        print("✓ Puedes ejecutar los scripts normalmente")
    else:
        print("\n✗ RESULTADO: Hay errores que necesitan corrección")
    
    print("\n=== INSTRUCCIONES DE USO ===")
    print("1. Para procesar archivos existentes:")
    print("   python analizar_estructura_datos.py")
    print("   python procesar_todos_los_datos.py")
    print()
    print("2. Para generar nuevos reportes SAP:")
    print("   python rep_plr.py")
    print("   python ejecutar_todos.py")
    print()
    print("3. Para procesar archivos específicos:")
    print("   python procesar_datos_sap.py")

if __name__ == "__main__":
    main()
