#!/usr/bin/env python3
"""
🎯 OTIF MASTER - SISTEMA DE INICIO
==================================

Script principal para iniciar OTIF Master.
Permite elegir entre:
1. Ejecutar procesamiento maestro (línea de comandos)
2. Iniciar aplicación web
3. Ver información del sistema

Autor: OTIF Master
Fecha: 2025
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

def mostrar_banner():
    """Muestra el banner del sistema."""
    print("🎯 OTIF MASTER - SISTEMA COMPLETO")
    print("=" * 60)
    print("Sistema de procesamiento y análisis de datos OTIF")
    print("Versión: 2.0 - Interfaz Web + Scripts Organizados")
    print("=" * 60)

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas."""
    print("🔍 Verificando dependencias...")
    
    dependencias = ['flask', 'pandas', 'openpyxl', 'pyarrow']
    faltantes = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            faltantes.append(dep)
    
    if faltantes:
        print(f"\n⚠️ Dependencias faltantes: {', '.join(faltantes)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def verificar_estructura():
    """Verifica que la estructura de carpetas esté correcta."""
    print("\n🔍 Verificando estructura de carpetas...")
    
    carpetas_requeridas = [
        "scripts",
        "Data/Rep PLR",
        "Data/No Entregas/2025",
        "Data/Vol_Portafolio"
    ]
    
    for carpeta in carpetas_requeridas:
        if Path(carpeta).exists():
            print(f"✅ {carpeta}")
        else:
            print(f"❌ {carpeta}")
            return False
    
    print("✅ Estructura de carpetas correcta")
    return True

def mostrar_menu():
    """Muestra el menú principal."""
    print("\n📋 OPCIONES DISPONIBLES:")
    print("1. 🚀 Ejecutar OTIF Master (Optimizado)")
    print("2. 🌐 Iniciar Aplicación Web (Modo Producción)")
    print("3. 🌐 Iniciar Aplicación Web (Servidor Simple)")
    print("4. 🧪 Probar Sistema (Sin archivos de datos)")
    print("5. 📊 Ver Información del Sistema")
    print("6. ❌ Salir")
    print("-" * 60)

def ejecutar_procesamiento_maestro():
    """Ejecuta el procesamiento maestro."""
    print("\n🚀 EJECUTANDO OTIF MASTER")
    print("=" * 60)
    
    if not Path("procesamiento_maestro.py").exists():
        print("❌ Error: No se encontró procesamiento_maestro.py (OTIF Master)")
        return False
    
    try:
        import subprocess
        resultado = subprocess.run([sys.executable, "procesamiento_maestro.py"])
        return resultado.returncode == 0
    except Exception as e:
        print(f"❌ Error al ejecutar OTIF Master: {e}")
        return False



def iniciar_aplicacion_web():
    """Inicia la aplicación web en modo producción."""
    print("\n🌐 INICIANDO APLICACIÓN WEB (MODO PRODUCCIÓN)")
    print("=" * 60)
    
    if not Path("app.py").exists():
        print("❌ Error: No se encontró app.py")
        return False
    
    print("📋 Información de la aplicación:")
    print("  • URL: http://localhost:5000")
    print("  • Puerto: 5000")
    print("  • Modo: Producción (sin debug)")
    print("  • Para detener: Ctrl+C")
    
    print("\n🌐 Abriendo navegador automáticamente...")
    
    # Abrir navegador después de un pequeño delay
    def abrir_navegador():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
    
    thread = threading.Thread(target=abrir_navegador)
    thread.daemon = True
    thread.start()
    
    try:
        from app import app
        print("\n✅ Aplicación iniciada correctamente!")
        print("Presiona Ctrl+C para detener la aplicación")
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
        return True
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación detenida por el usuario")
        return True
    except Exception as e:
        print(f"\n❌ Error al iniciar la aplicación: {e}")
        return False

def iniciar_aplicacion_web_simple():
    """Inicia la aplicación web con servidor WSGI simple."""
    print("\n🌐 INICIANDO APLICACIÓN WEB (SERVIDOR SIMPLE)")
    print("=" * 60)
    
    if not Path("app.py").exists():
        print("❌ Error: No se encontró app.py")
        return False
    
    print("📋 Información de la aplicación:")
    print("  • URL: http://localhost:5000")
    print("  • Puerto: 5000")
    print("  • Servidor: WSGI Simple Server")
    print("  • Para detener: Ctrl+C")
    
    print("\n🌐 Abriendo navegador automáticamente...")
    
    # Abrir navegador después de un pequeño delay
    def abrir_navegador():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
    
    thread = threading.Thread(target=abrir_navegador)
    thread.daemon = True
    thread.start()
    
    try:
        from wsgiref.simple_server import make_server
        from app import app
        
        print("\n✅ Aplicación iniciada correctamente!")
        print("Presiona Ctrl+C para detener la aplicación")
        
        # Crear servidor WSGI
        httpd = make_server('0.0.0.0', 5000, app)
        httpd.serve_forever()
        
        return True
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación detenida por el usuario")
        return True
    except Exception as e:
        print(f"\n❌ Error al iniciar la aplicación: {e}")
        return False

def mostrar_informacion_sistema():
    """Muestra información del sistema."""
    print("\n📊 INFORMACIÓN DEL SISTEMA")
    print("=" * 60)
    
    # Estructura de archivos
    print("📁 ESTRUCTURA DE ARCHIVOS:")
    print("  • scripts/ - Scripts de procesamiento")
    print("    - agrupar_datos_rep_plr.py")
    print("    - agrupar_datos_no_entregas_mejorado.py")
    print("    - agrupar_datos_vol_portafolio.py")
    print("    - unificar_datos_completos.py")
    print("  • app.py - Aplicación web OTIF Master")
    print("  • procesamiento_maestro.py - Script maestro OTIF Master")
    print("  • templates/index.html - Interfaz web")
    print("  • Data/ - Datos de entrada y salida")
    
    # Verificar archivos de scripts
    print("\n🔍 SCRIPTS DISPONIBLES:")
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            print(f"  ✅ {script.name}")
    else:
        print("  ❌ Carpeta scripts no encontrada")
    
    # Verificar archivos de datos
    print("\n📂 CARPETAS DE DATOS:")
    data_carpetas = [
        "Data/Rep PLR",
        "Data/No Entregas/2025", 
        "Data/Vol_Portafolio",
        "Data/Output/calculo_otif"
    ]
    
    for carpeta in data_carpetas:
        if Path(carpeta).exists():
            archivos = list(Path(carpeta).glob("*"))
            print(f"  ✅ {carpeta} ({len(archivos)} elementos)")
        else:
            print(f"  ❌ {carpeta}")
    
    print("\n📋 ARCHIVOS DE SALIDA:")
    output_dir = Path("Data/Output/calculo_otif")
    if output_dir.exists():
        archivos_parquet = list(output_dir.glob("*.parquet"))
        if archivos_parquet:
            for archivo in archivos_parquet:
                tamaño_mb = archivo.stat().st_size / (1024*1024)
                print(f"  📄 {archivo.name} ({tamaño_mb:.2f} MB)")
        else:
            print("  ⚠️ No hay archivos parquet generados")
    else:
        print("  ❌ Carpeta de salida no existe")

def main():
    """Función principal."""
    mostrar_banner()
    
    # Verificar dependencias y estructura
    if not verificar_dependencias():
        print("\n❌ Error: Dependencias faltantes")
        return 1
    
    if not verificar_estructura():
        print("\n❌ Error: Estructura de carpetas incorrecta")
        return 1
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (1-6): ").strip()
            
            if opcion == "1":
                if ejecutar_procesamiento_maestro():
                    print("\n✅ Procesamiento maestro completado")
                else:
                    print("\n❌ Error en el procesamiento maestro")
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "2":
                iniciar_aplicacion_web()
                break  # Salir después de cerrar la aplicación web
                
            elif opcion == "3":
                iniciar_aplicacion_web_simple()
                break  # Salir después de cerrar la aplicación web
                
            elif opcion == "4":
                # Opción para probar el sistema sin archivos de datos
                print("\n🧪 PROBANDO SISTEMA (SIN ARCHIVOS DE DATOS)")
                print("=" * 60)
                print("Esta opción ejecuta una prueba completa del sistema")
                print("creando archivos parquet vacíos si no encuentra datos.")
                print("Ideal para verificar que todo funciona correctamente.")
                
                if not Path("probar_sistema.py").exists():
                    print("❌ Error: No se encontró probar_sistema.py")
                    input("\nPresiona Enter para continuar...")
                    continue
                
                try:
                    import subprocess
                    resultado = subprocess.run([sys.executable, "probar_sistema.py"])
                    if resultado.returncode == 0:
                        print("\n✅ Prueba del sistema completada exitosamente")
                    else:
                        print("\n❌ La prueba del sistema falló")
                except Exception as e:
                    print(f"\n❌ Error al ejecutar la prueba: {e}")
                
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "5":
                mostrar_informacion_sistema()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "6":
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("\n❌ Opción no válida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
