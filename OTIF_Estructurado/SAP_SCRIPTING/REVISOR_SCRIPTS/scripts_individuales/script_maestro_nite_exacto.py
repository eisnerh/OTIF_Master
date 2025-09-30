#!/usr/bin/env python3
"""
Script maestro que ejecuta todos los reportes replicando exactamente la funcionalidad del entorno NITE
Basado en script_maestro_nuevo.py que funciona correctamente
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def ejecutar_script_incidencias():
    """
    Ejecuta el script de incidencias usando el método del entorno NITE
    """
    print("📊 Ejecutando ZSD_INCIDENCIAS - Estilo NITE...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "zsd_incidencias_nite_style.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ ZSD_INCIDENCIAS ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en ZSD_INCIDENCIAS: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando ZSD_INCIDENCIAS: {e}")
        return False

def ejecutar_script_mb51():
    """
    Ejecuta el script MB51 usando el método del entorno NITE
    """
    print("\n📊 Ejecutando MB51 - Estilo NITE...")
    print("=" * 60)
    
    try:
        # Crear script MB51 en estilo NITE si no existe
        if not os.path.exists("mb51_nite_style.py"):
            crear_script_mb51_nite()
        
        result = subprocess.run([sys.executable, "mb51_nite_style.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ MB51 ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en MB51: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando MB51: {e}")
        return False

def crear_script_mb51_nite():
    """
    Crea el script MB51 en estilo NITE
    """
    script_content = '''#!/usr/bin/env python3
"""
Script MB51 replicando exactamente la funcionalidad del entorno NITE
"""

import win32com.client
from datetime import datetime
import os
import time

def ejecutar_mb51():
    """
    Ejecuta la transacción MB51 usando el método del entorno NITE
    """
    print("INICIANDO SCRIPT MB51 - ESTILO NITE")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # File path and name
    file_name = "data_mb51.xls"
    saved_path = os.path.join("C:/data", file_name)
    
    # Remove file if it already exists
    if os.path.exists(saved_path):
        os.remove(saved_path)
    
    # Connect to SAP GUI (método del entorno NITE)
    try:
        print("Conectando a SAP GUI...")
        sap_gui_auto = win32com.client.GetObject("SAPGUI")
        application = sap_gui_auto.GetScriptingEngine
        connection = application.Children(0)
        session = connection.Children(0)
        print("Conexión SAP establecida correctamente")
    except Exception as e:
        print(f"Error connecting to SAP: {e}")
        return False
        
    # SAP automation (replicando el flujo del entorno NITE)
    try:
        print("Navegando a transacción: mb51")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "mb51"
        session.findById("wnd[0]").sendVKey(0)
        
        print("Ejecutando reporte...")
        session.findById("wnd[0]/tbar[1]/btn[8]").press()
        
        # Wait for the report to generate
        print("Esperando a que se genere el reporte...")
        time.sleep(5)
        
        print("Exportando a Excel...")
        session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
        session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
        session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        
        # Configurar ruta y nombre de archivo (método del entorno NITE)
        session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(saved_path)
        session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
        session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
        session.findById("wnd[1]").sendVKey(4)
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = file_name
        session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").text = "0000"
        session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = len(file_name)
        session.findById("wnd[2]/tbar[0]/btn[0]").press()
        session.findById("wnd[1]/tbar[0]/btn[0]").press()
        
        print(f"Script ejecutado correctamente. Archivo guardado en: {saved_path}")
        
        # Wait for file to be completely written
        time.sleep(3)
        
        # Verificar que el archivo se generó
        if os.path.exists(saved_path):
            size = os.path.getsize(saved_path)
            print(f"Archivo generado exitosamente: {file_name} - {size:,} bytes")
            return True
        else:
            print("ERROR: El archivo no se generó correctamente")
            return False
        
    except Exception as e:
        print(f"Error during SAP automation: {e}")
        return False

if __name__ == "__main__":
    try:
        success = ejecutar_mb51()
        if success:
            print("Script completado exitosamente")
            exit(0)
        else:
            print("Script falló")
            exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        exit(1)
'''
    
    with open("mb51_nite_style.py", "w", encoding="utf-8") as f:
        f.write(script_content)

def verificar_archivos_generados():
    """
    Verifica que los archivos se hayan generado correctamente
    """
    print("\n🔍 Verificando archivos generados...")
    print("=" * 60)
    
    # Lista de archivos esperados
    archivos_esperados = [
        "data_incidencias.xls",
        "data_mb51.xls"
    ]
    
    archivos_encontrados = 0
    directorio_base = "C:\\data"
    
    for archivo in archivos_esperados:
        ruta_archivo = os.path.join(directorio_base, archivo)
        if os.path.exists(ruta_archivo):
            tamaño = os.path.getsize(ruta_archivo)
            print(f"✅ {archivo} - {tamaño:,} bytes")
            archivos_encontrados += 1
        else:
            print(f"❌ {archivo} - No encontrado")
    
    print(f"\n📊 Archivos generados: {archivos_encontrados}/{len(archivos_esperados)}")
    
    if archivos_encontrados == len(archivos_esperados):
        print("🎉 Todos los archivos se generaron correctamente")
        return True
    else:
        print("⚠️  Algunos archivos no se generaron")
        return False

def main():
    """
    Función principal que ejecuta todo el flujo
    """
    print("🚀 INICIANDO SCRIPT MAESTRO - ESTILO NITE EXACTO")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Lista de scripts a ejecutar
    scripts = [
        ("ZSD_INCIDENCIAS", ejecutar_script_incidencias),
        ("MB51", ejecutar_script_mb51)
    ]
    
    exitosos = 0
    fallidos = 0
    
    # Ejecutar cada script
    for nombre, funcion in scripts:
        print(f"\n🔄 Ejecutando {nombre}...")
        if funcion():
            exitosos += 1
            print(f"✅ {nombre} completado exitosamente")
        else:
            fallidos += 1
            print(f"❌ {nombre} falló")
        
        # Esperar entre scripts para evitar conflictos
        print("⏳ Esperando 5 segundos antes del siguiente script...")
        time.sleep(5)
    
    # Verificar archivos generados
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN FINAL")
    print("=" * 80)
    verificar_archivos_generados()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Scripts exitosos: {exitosos}")
    print(f"❌ Scripts fallidos: {fallidos}")
    print(f"📁 Archivos generados en: C:\\data")
    print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if fallidos == 0:
        print("🎉 TODOS LOS SCRIPTS COMPLETADOS EXITOSAMENTE")
        return True
    else:
        print(f"⚠️  {fallidos} SCRIPTS FALLARON")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Proceso completado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Proceso completado con errores")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
