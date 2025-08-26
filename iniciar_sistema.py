#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SISTEMA DE INICIO OTIF - VERSIÓN SIMPLIFICADA
Script de inicio que redirige al sistema unificado
"""

import sys
import subprocess

def main():
    """Función principal - redirige al sistema unificado"""
    print("🎯 SISTEMA DE INICIO OTIF")
    print("=" * 40)
    print("🔄 Redirigiendo al sistema unificado...")
    print()
    
    try:
        # Ejecutar el sistema unificado
        subprocess.run([sys.executable, "ejecutar_modulo.py"])
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Alternativa: ejecuta directamente:")
        print("   python ejecutar_modulo.py")

if __name__ == "__main__":
    main()
