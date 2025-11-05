# -*- coding: utf-8 -*-
"""
Script de Verificación de Instalación - Reporte PLR
---------------------------------------------------
Verifica que todos los requisitos estén instalados y configurados correctamente.
"""
import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_check(text, passed):
    symbol = "✅" if passed else "❌"
    print(f"{symbol} {text}")

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    required = (3, 7)
    passed = version >= required
    print_check(f"Python {version.major}.{version.minor}.{version.micro} (requerido: {required[0]}.{required[1]}+)", passed)
    return passed

def check_dependencies():
    """Verifica las dependencias de Python"""
    dependencies = {
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "win32com.client": "pywin32"
    }
    
    all_passed = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print_check(f"Paquete '{package}' instalado", True)
        except ImportError:
            print_check(f"Paquete '{package}' NO instalado", False)
            print(f"   Instalar con: pip install {package}")
            all_passed = False
    
    return all_passed

def check_credentials_file():
    """Verifica el archivo de credenciales"""
    creds_path = Path(__file__).parent / "credentials.ini"
    example_path = Path(__file__).parent / "credentials.ini.example"
    
    if creds_path.exists():
        print_check("Archivo credentials.ini encontrado", True)
        
        # Verificar que tenga contenido válido
        try:
            with open(creds_path, 'r', encoding='utf-8') as f:
                content = f.read()
                has_auth = "[AUTH]" in content
                has_user = "sap_user" in content and "tu_usuario" not in content
                has_pass = "sap_password" in content and "tu_contraseña" not in content
                
                if has_auth and has_user and has_pass:
                    print_check("Credenciales configuradas", True)
                    return True
                else:
                    print_check("Credenciales SIN configurar (usar plantilla)", False)
                    print(f"   Edita el archivo: {creds_path}")
                    return False
        except Exception as e:
            print_check(f"Error leyendo credentials.ini: {e}", False)
            return False
    else:
        print_check("Archivo credentials.ini NO encontrado", False)
        if example_path.exists():
            print(f"   Copia el ejemplo: copy credentials.ini.example credentials.ini")
        return False

def check_sap_gui():
    """Verifica SAP GUI"""
    candidates = [
        r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
        r"C:\Program Files\SAP\FrontEnd\SAPgui\saplogon.exe",
    ]
    
    for exe in candidates:
        if os.path.isfile(exe):
            print_check(f"SAP GUI encontrado: {exe}", True)
            return True
    
    print_check("SAP GUI NO encontrado en ubicaciones comunes", False)
    print("   Verifica que SAP GUI esté instalado")
    return False

def check_output_directory():
    """Verifica/crea el directorio de salida"""
    output_dir = Path(r"C:\data\SAP_Extraction\rep_plr")
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print_check(f"Directorio de salida accesible: {output_dir}", True)
        return True
    except Exception as e:
        print_check(f"Error creando directorio de salida: {e}", False)
        return False

def check_script_files():
    """Verifica que existan los archivos necesarios"""
    script_dir = Path(__file__).parent
    required_files = [
        "y_rep_plr.py",
        "amalgama_y_rep_plr.py",
        "ejecutar_rep_plr.bat",
        "credentials.ini.example"
    ]
    
    all_passed = True
    for filename in required_files:
        filepath = script_dir / filename
        exists = filepath.exists()
        print_check(f"Archivo '{filename}' encontrado", exists)
        if not exists:
            all_passed = False
    
    return all_passed

def main():
    print_header("Verificación de Instalación - Reporte PLR")
    
    print("\n🔍 Verificando versión de Python...")
    py_ok = check_python_version()
    
    print("\n🔍 Verificando dependencias de Python...")
    deps_ok = check_dependencies()
    
    print("\n🔍 Verificando archivos del proyecto...")
    files_ok = check_script_files()
    
    print("\n🔍 Verificando credenciales SAP...")
    creds_ok = check_credentials_file()
    
    print("\n🔍 Verificando SAP GUI...")
    sap_ok = check_sap_gui()
    
    print("\n🔍 Verificando directorio de salida...")
    output_ok = check_output_directory()
    
    # Resumen final
    print_header("Resumen de Verificación")
    
    all_checks = [
        ("Python", py_ok),
        ("Dependencias", deps_ok),
        ("Archivos", files_ok),
        ("Credenciales", creds_ok),
        ("SAP GUI", sap_ok),
        ("Directorio", output_ok)
    ]
    
    passed_count = sum(1 for _, passed in all_checks if passed)
    total_count = len(all_checks)
    
    print(f"\n✅ Verificaciones pasadas: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n" + "🎉" * 20)
        print("¡TODO LISTO! El sistema está configurado correctamente.")
        print("Ejecuta 'ejecutar_rep_plr.bat' para generar el reporte.")
        print("🎉" * 20)
        return 0
    else:
        print("\n" + "⚠️ " * 20)
        print("HAY PROBLEMAS. Revisa los mensajes anteriores y corrige los errores.")
        print("⚠️ " * 20)
        
        # Mostrar pasos sugeridos
        print("\n📝 Pasos sugeridos:")
        if not deps_ok:
            print("1. Instalar dependencias: pip install pandas openpyxl pywin32")
        if not creds_ok:
            print("2. Configurar credenciales: copy credentials.ini.example credentials.ini")
            print("   Luego editar credentials.ini con tus datos SAP")
        if not sap_ok:
            print("3. Instalar SAP GUI desde el portal corporativo")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        sys.exit(1)


