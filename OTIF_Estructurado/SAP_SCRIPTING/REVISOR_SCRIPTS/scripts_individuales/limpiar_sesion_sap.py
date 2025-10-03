#!/usr/bin/env python3
"""
Script independiente para limpiar la sesión SAP
Se ejecuta después de cada script para asegurar que no queden datos residuales
"""

import sys
import time
from z_devo_alv import attach_to_sap

def limpiar_sesion_sap(session):
    """
    Limpia la sesión SAP después de ejecutar un script.
    - Cierra ventanas abiertas
    - Regresa al menú principal
    - Espera a que la sesión esté lista
    """
    try:
        # Ir al menú principal
        session.findById("wnd[0]").sendVKey(0)  # Enter
        session.findById("wnd[0]").sendCommand("/n")  # Comando para ir al menú principal
        session.findById("wnd[0]").sendVKey(0)  # Enter

        # Cerrar ventanas adicionales si existen
        for i in range(1, 10):  # Máximo 10 ventanas
            try:
                session.findById(f"wnd[{i}]").close()
            except:
                break  # No hay más ventanas

        # Esperar a que la sesión esté lista
        while not session.findById("wnd[0]/usr").Text:
            time.sleep(0.5)

        print("✅ Sesión SAP limpiada correctamente.")
        return True
    except Exception as e:
        print(f"⚠️ Error al limpiar la sesión SAP: {e}")
        return False

def main():
    """Función principal para limpiar la sesión SAP"""
    try:
        # Conectar a SAP
        _, _, session = attach_to_sap(-1, -1)
        
        # Limpiar sesión
        success = limpiar_sesion_sap(session)
        
        if success:
            print("🧹 Limpieza de sesión SAP completada exitosamente")
            sys.exit(0)
        else:
            print("❌ Error en la limpieza de sesión SAP")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
