#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 PROCESAMIENTO RÁPIDO OTIF
Script simple para ejecutar todo el procesamiento OTIF de forma rápida

Uso: python procesar_todo.py
"""

import subprocess
import sys

def main():
    """Ejecuta todo el procesamiento OTIF"""
    print("🚀 PROCESAMIENTO RÁPIDO OTIF")
    print("=" * 40)
    print("🔄 Ejecutando todo el procesamiento...")
    print()
    
    try:
        # Ejecutar todo el procesamiento
        result = subprocess.run([sys.executable, "ejecutar_modulo.py", "todo"])
        
        if result.returncode == 0:
            print("\n🎉 ¡Procesamiento completado exitosamente!")
        else:
            print("\n❌ El procesamiento falló")
            
    except KeyboardInterrupt:
        print("\n🛑 Procesamiento interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
