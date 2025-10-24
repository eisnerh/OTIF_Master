#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 INICIADOR RÁPIDO DEL MENÚ OTIF
Script simple para iniciar el menú interactivo sin tkinter

Uso: python iniciar_menu.py
"""

import os
import sys

def main():
    """Función principal - inicia el menú"""
    print("🚀 INICIANDO SISTEMA OTIF")
    print("=" * 40)
    print("🔄 Cargando menú interactivo...")
    print()
    
    try:
        # Verificar que el archivo del menú existe
        if not os.path.exists("menu_cmd.py"):
            print("❌ Error: No se encontró menu_cmd.py")
            print("💡 Asegúrate de estar en el directorio correcto")
            return
        
        # Importar y ejecutar el menú
        import menu_cmd
        menu_cmd.main()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Alternativas:")
        print("   python menu_cmd.py")
        print("   python ejecutar_modulo.py")

if __name__ == "__main__":
    main()
