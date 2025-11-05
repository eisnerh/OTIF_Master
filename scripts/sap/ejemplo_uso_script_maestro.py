#!/usr/bin/env python3
"""
Ejemplos de uso del Script Maestro SAP Python
Este archivo muestra diferentes formas de utilizar el automatizador SAP
"""

from script_maestro_sap_python import SAPAutomation
from datetime import datetime, timedelta
import json

def ejemplo_1_ejecutar_todas_las_transacciones():
    """
    Ejemplo 1: Ejecutar todas las transacciones configuradas
    """
    print(" Ejemplo 1: Ejecutar todas las transacciones")
    print("-" * 50)
    
    # Crear instancia del automatizador
    sap_auto = SAPAutomation()
    
    # Ejecutar todas las transacciones con fecha de hoy
    today_date = sap_auto.get_today_date()
    results = sap_auto.execute_all_transactions(today_date)
    
    # Mostrar resultados
    for transaction, success in results.items():
        status = "[OK]" if success else "[ERROR]"
        print(f"{status} {transaction}")
    
    return results

def ejemplo_2_ejecutar_transacciones_especificas():
    """
    Ejemplo 2: Ejecutar solo transacciones específicas
    """
    print("\n Ejemplo 2: Ejecutar transacciones específicas")
    print("-" * 50)
    
    # Lista de transacciones específicas
    transacciones_especificas = [
        "rep_plr",
        "y_dev_45",
        "zred"
    ]
    
    sap_auto = SAPAutomation()
    today_date = sap_auto.get_today_date()
    
    # Ejecutar solo las transacciones especificadas
    results = sap_auto.execute_specific_transactions(
        transacciones_especificas, 
        today_date
    )
    
    # Mostrar resultados
    for transaction, success in results.items():
        status = "[OK]" if success else "[ERROR]"
        print(f"{status} {transaction}")
    
    return results

def ejemplo_3_fecha_personalizada():
    """
    Ejemplo 3: Ejecutar con fecha personalizada
    """
    print("\n Ejemplo 3: Ejecutar con fecha personalizada")
    print("-" * 50)
    
    # Fecha personalizada (hace 7 días)
    fecha_personalizada = (datetime.now() - timedelta(days=7)).strftime("%d.%m.%Y")
    print(f"[FECHA] Fecha personalizada: {fecha_personalizada}")
    
    sap_auto = SAPAutomation()
    
    # Ejecutar solo transacciones que requieren fecha
    transacciones_con_fecha = ["rep_plr", "zhbo"]
    results = sap_auto.execute_specific_transactions(
        transacciones_con_fecha, 
        fecha_personalizada
    )
    
    return results

def ejemplo_4_verificar_archivos():
    """
    Ejemplo 4: Solo verificar archivos existentes
    """
    print("\n Ejemplo 4: Verificar archivos generados")
    print("-" * 50)
    
    sap_auto = SAPAutomation()
    
    # Verificar archivos sin ejecutar transacciones
    archivos_ok = sap_auto.verify_output_files()
    
    if archivos_ok:
        print("[OK] Todos los archivos están presentes")
    else:
        print("[ERROR] Algunos archivos faltan")
    
    return archivos_ok

def ejemplo_5_configuracion_personalizada():
    """
    Ejemplo 5: Usar configuración personalizada
    """
    print("\n Ejemplo 5: Configuración personalizada")
    print("-" * 50)
    
    # Crear configuración personalizada
    config_personalizada = {
        "output_path": "C:\\data\\custom",
        "encoding": "0000",
        "date_format": "%d.%m.%Y",
        "transactions": {
            "rep_plr": {
                "transaction": "zsd_rep_planeamiento",
                "filename": "REP_PLR_CUSTOM.xls",
                "node": "F00120",
                "row": 11,
                "date_field": "P_LFDAT-LOW"
            }
        }
    }
    
    # Guardar configuración temporal
    with open("configuracion_temporal.json", "w", encoding="utf-8") as f:
        json.dump(config_personalizada, f, indent=2, ensure_ascii=False)
    
    # Usar configuración personalizada
    sap_auto = SAPAutomation("configuracion_temporal.json")
    
    # Ejecutar con configuración personalizada
    results = sap_auto.execute_specific_transactions(["rep_plr"])
    
    # Limpiar archivo temporal
    import os
    os.remove("configuracion_temporal.json")
    
    return results

def ejemplo_6_solo_conectar():
    """
    Ejemplo 6: Solo conectar a SAP sin ejecutar transacciones
    """
    print("\n Ejemplo 6: Solo conectar a SAP")
    print("-" * 50)
    
    sap_auto = SAPAutomation()
    
    # Solo conectar
    if sap_auto.connect_sap():
        print("[OK] Conexión SAP establecida")
        print(" Puedes usar sap_auto.session para interactuar manualmente")
        return True
    else:
        print("[ERROR] No se pudo conectar a SAP")
        return False

def menu_principal():
    """
    Menú principal con opciones de ejemplo
    """
    print("[INICIO] EJEMPLOS DE USO - SCRIPT MAESTRO SAP")
    print("=" * 60)
    print("1. Ejecutar todas las transacciones")
    print("2. Ejecutar transacciones específicas")
    print("3. Ejecutar con fecha personalizada")
    print("4. Verificar archivos generados")
    print("5. Usar configuración personalizada")
    print("6. Solo conectar a SAP")
    print("7. Salir")
    print("=" * 60)
    
    while True:
        try:
            opcion = input("\n Selecciona una opción (1-7): ").strip()
            
            if opcion == "1":
                ejemplo_1_ejecutar_todas_las_transacciones()
            elif opcion == "2":
                ejemplo_2_ejecutar_transacciones_especificas()
            elif opcion == "3":
                ejemplo_3_fecha_personalizada()
            elif opcion == "4":
                ejemplo_4_verificar_archivos()
            elif opcion == "5":
                ejemplo_5_configuracion_personalizada()
            elif opcion == "6":
                ejemplo_6_solo_conectar()
            elif opcion == "7":
                print(" ¡Hasta luego!")
                break
            else:
                print("[ERROR] Opción inválida. Selecciona 1-7.")
                
        except KeyboardInterrupt:
            print("\n ¡Hasta luego!")
            break
        except Exception as e:
            print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    # Ejecutar menú principal
    menu_principal()
