#!/usr/bin/env python3
"""
Script simple para ejecutar OTIF Master
Usa el servidor WSGI básico sin Flask
"""

import os
import sys
from wsgiref.simple_server import make_server
from app import app

def main():
    """Función principal para ejecutar la aplicación."""
    
    print("🚀 Iniciando OTIF Master...")
    print("=" * 50)
    print("📋 Información del servidor:")
    print(f"  • Host: 0.0.0.0")
    print(f"  • Puerto: 5000")
    print(f"  • Servidor: WSGI Simple Server")
    print("=" * 50)
    print("🌐 URL de acceso: http://localhost:5000")
    print("=" * 50)
    print("💡 Para detener el servidor, presiona Ctrl+C")
    print("=" * 50)
    
    try:
        # Crear servidor WSGI
        httpd = make_server('0.0.0.0', 5000, app)
        print("✅ Servidor iniciado correctamente")
        print("🌐 Abre tu navegador en: http://localhost:5000")
        
        # Mantener el servidor ejecutándose
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        print("💡 Verifica que el puerto 5000 no esté en uso")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
