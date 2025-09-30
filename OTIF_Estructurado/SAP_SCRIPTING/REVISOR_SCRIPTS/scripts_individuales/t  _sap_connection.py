#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión SAP y identificar problemas
ia
"""

import sys
import os
import time
from datetime import datetime

def test_sap_connection():
    """Prueba la conexión básica a SAP"""
    try:
        print("=== PRUEBA DE CONEXIÓN SAP ===")
        print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Importar módulos
        print("1. Importando módulos...")
        from base_sap_script import BaseSAPScript
        print("   ✓ Módulos importados correctamente")
        
        # Crear instancia
        print("2. Creando instancia de script...")
        script = BaseSAPScript("TEST_SAP", "C:\\data")
        print("   ✓ Instancia creada")
        
        # Probar conexión
        print("3. Probando conexión a SAP...")
        if script.connect_sap():
            print("   ✓ Conexión SAP establecida")
            
            # Probar navegación básica
            print("4. Probando navegación básica...")
            if script.navigate_to_transaction("zsd_incidencias"):
                print("   ✓ Navegación a transacción exitosa")
                
                # Esperar un momento
                print("5. Esperando 3 segundos...")
                time.sleep(3)
                
                # Probar selección de fila con método mejorado
                print("6. Probando selección de fila...")
                if script.select_row(1):
                    print("   ✓ Selección de fila exitosa")
                else:
                    print("   ⚠ Selección de fila falló, pero continuando...")
                
                print("7. Limpieza...")
                script.cleanup()
                print("   ✓ Limpieza completada")
                
                print("\n=== RESULTADO ===")
                print("✓ CONEXIÓN SAP EXITOSA")
                print("✓ El script puede conectarse y navegar")
                print("✓ Los errores de selección de fila se manejan correctamente")
                return True
            else:
                print("   ✗ Error navegando a transacción")
                return False
        else:
            print("   ✗ Error conectando a SAP")
            return False
            
    except Exception as e:
        print(f"   ✗ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("SCRIPT DE PRUEBA SAP")
    print("=" * 50)
    
    # Verificar que SAP esté abierto
    print("IMPORTANTE: Asegúrate de que SAP GUI esté abierto y logueado")
    print("Presiona Enter para continuar...")
    input()
    
    # Ejecutar prueba
    success = test_sap_connection()
    
    if success:
        print("\n✓ PRUEBA EXITOSA")
        print("Los scripts están listos para usar")
    else:
        print("\n✗ PRUEBA FALLÓ")
        print("Revisa la conexión SAP y vuelve a intentar")
    
    print("\n=== INSTRUCCIONES ===")
    print("1. Para procesar archivos existentes:")
    print("   python analizar_estructura_datos.py")
    print("   python procesar_todos_los_datos.py")
    print()
    print("2. Para generar nuevos reportes:")
    print("   python rep_plr.py")
    print("   python zsd_incidencias.py")
    print()
    print("3. Para ejecutar todos los scripts:")
    print("   python ejecutar_todos.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrueba interrumpida por el usuario")
    except Exception as e:
        print(f"\nError inesperado: {e}")
