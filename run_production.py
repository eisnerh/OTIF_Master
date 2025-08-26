#!/usr/bin/env python3
"""
Script para ejecutar OTIF Master en modo producción
Usa un servidor WSGI más robusto que el servidor de desarrollo de Flask
"""

import os
import sys
from app import app

def main():
    """Función principal para ejecutar la aplicación en modo producción."""
    
    print("🚀 Iniciando OTIF Master en modo producción...")
    print("=" * 60)
    print("📋 Información del servidor:")
    print(f"  • Host: 0.0.0.0 (accesible desde cualquier IP)")
    print(f"  • Puerto: 5000")
    print(f"  • Modo: Producción (sin debug)")
    print(f"  • Servidor: Werkzeug WSGI")
    print("=" * 60)
    print("🌐 URLs de acceso:")
    print("  • Local: http://localhost:5000")
    print("  • Red: http://[IP-DE-TU-COMPUTADORA]:5000")
    print("=" * 60)
    print("💡 Para detener el servidor, presiona Ctrl+C")
    print("=" * 60)
    
    try:
        # Configurar variables de entorno para producción
        os.environ['FLASK_ENV'] = 'production'
        os.environ['FLASK_DEBUG'] = '0'
        
        # Ejecutar la aplicación
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        print("💡 Verifica que el puerto 5000 no esté en uso")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
