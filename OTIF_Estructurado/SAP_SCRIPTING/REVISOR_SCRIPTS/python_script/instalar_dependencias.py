#!/usr/bin/env python3
"""
Script de instalación de dependencias para el Script Maestro SAP Python
"""

import subprocess
import sys
import os

def instalar_dependencia(paquete):
    """
    Instala una dependencia usando pip
    
    Args:
        paquete (str): Nombre del paquete a instalar
    """
    try:
        print(f"📦 Instalando {paquete}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
        print(f"✅ {paquete} instalado correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {paquete}: {e}")
        return False

def verificar_dependencia(paquete):
    """
    Verifica si una dependencia está instalada
    
    Args:
        paquete (str): Nombre del paquete a verificar
    """
    try:
        __import__(paquete)
        print(f"✅ {paquete} ya está instalado")
        return True
    except ImportError:
        print(f"❌ {paquete} no está instalado")
        return False

def main():
    """
    Función principal de instalación
    """
    print("🚀 INSTALADOR DE DEPENDENCIAS - SCRIPT MAESTRO SAP")
    print("=" * 60)
    
    # Lista de dependencias requeridas
    dependencias = [
        ("pywin32", "win32com.client"),
        ("datetime", "datetime"),
        ("json", "json"),
        ("logging", "logging"),
        ("os", "os"),
        ("time", "time")
    ]
    
    dependencias_faltantes = []
    
    # Verificar dependencias existentes
    print("🔍 Verificando dependencias...")
    for paquete, modulo in dependencias:
        if not verificar_dependencia(modulo):
            dependencias_faltantes.append(paquete)
    
    # Instalar dependencias faltantes
    if dependencias_faltantes:
        print(f"\n📦 Instalando {len(dependencias_faltantes)} dependencias faltantes...")
        
        for paquete in dependencias_faltantes:
            if not instalar_dependencia(paquete):
                print(f"❌ No se pudo instalar {paquete}")
                return False
    else:
        print("✅ Todas las dependencias ya están instaladas")
    
    # Verificar instalación final
    print("\n🔍 Verificación final...")
    todas_instaladas = True
    
    for paquete, modulo in dependencias:
        if not verificar_dependencia(modulo):
            todas_instaladas = False
    
    if todas_instaladas:
        print("\n🎉 ¡Todas las dependencias están instaladas correctamente!")
        print("✅ El Script Maestro SAP está listo para usar")
        return True
    else:
        print("\n❌ Algunas dependencias no se pudieron instalar")
        return False

def crear_requirements_txt():
    """
    Crea archivo requirements.txt con las dependencias
    """
    requirements_content = """# Dependencias para Script Maestro SAP Python
pywin32>=306
python-dateutil>=2.8.0
"""
    
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)
        print("📄 Archivo requirements.txt creado")
        return True
    except Exception as e:
        print(f"❌ Error creando requirements.txt: {e}")
        return False

def instalar_desde_requirements():
    """
    Instala dependencias desde requirements.txt
    """
    if os.path.exists("requirements.txt"):
        try:
            print("📦 Instalando desde requirements.txt...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencias instaladas desde requirements.txt")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando desde requirements.txt: {e}")
            return False
    else:
        print("❌ Archivo requirements.txt no encontrado")
        return False

if __name__ == "__main__":
    try:
        print("🚀 Iniciando instalación de dependencias...")
        
        # Crear requirements.txt
        crear_requirements_txt()
        
        # Instalar dependencias
        success = main()
        
        if success:
            print("\n✅ Instalación completada exitosamente")
            print("💡 Ahora puedes ejecutar el Script Maestro SAP")
            print("📖 Ejecuta: python script_maestro_sap_python.py")
        else:
            print("\n❌ Instalación falló")
            print("💡 Revisa los errores anteriores e intenta nuevamente")
            
    except KeyboardInterrupt:
        print("\n⚠️  Instalación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
