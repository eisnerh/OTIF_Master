#!/usr/bin/env python3
"""
Script que genera automáticamente todos los scripts individuales en estilo NITE
Replicando la funcionalidad exitosa del entorno NITE
"""

import os
from datetime import datetime

def generar_script_nite(transaccion, nombre_archivo, descripcion):
    """
    Genera un script individual en estilo NITE
    """
    script_content = f'''#!/usr/bin/env python3
"""
Script {transaccion} replicando exactamente la funcionalidad del entorno NITE
{descripcion}
"""

import win32com.client
from datetime import datetime
import os
import time

def ejecutar_{transaccion.lower()}():
    """
    Ejecuta la transacción {transaccion} usando el método del entorno NITE
    """
    print("INICIANDO SCRIPT {transaccion} - ESTILO NITE")
    print("=" * 60)
    print(f"Hora de inicio: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
    print("=" * 60)
    
    # File path and name
    file_name = "{nombre_archivo}"
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
        print(f"Error connecting to SAP: {{e}}")
        return False
        
    # SAP automation (replicando el flujo del entorno NITE)
    try:
        print("Navegando a transacción: {transaccion.lower()}")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "{transaccion.lower()}"
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
        
        print(f"Script ejecutado correctamente. Archivo guardado en: {{saved_path}}")
        
        # Wait for file to be completely written
        time.sleep(3)
        
        # Verificar que el archivo se generó
        if os.path.exists(saved_path):
            size = os.path.getsize(saved_path)
            print(f"Archivo generado exitosamente: {{file_name}} - {{size:,}} bytes")
            
            print("\\n" + "=" * 60)
            print("PROCESO {transaccion} COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Archivo generado: {{file_name}}")
            print(f"Ubicación: {{saved_path}}")
            print(f"Hora de finalización: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
            print("=" * 60)
            return True
        else:
            print("ERROR: El archivo no se generó correctamente")
            return False
        
    except Exception as e:
        print(f"Error during SAP automation: {{e}}")
        return False

def main():
    """
    Función principal
    """
    try:
        success = ejecutar_{transaccion.lower()}()
        
        if success:
            print("\\nScript {transaccion} ejecutado exitosamente")
            return True
        else:
            print("\\nScript {transaccion} falló")
            return False
            
    except Exception as e:
        print(f"\\nError inesperado: {{e}}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\\nScript completado exitosamente")
            exit(0)
        else:
            print("\\nScript falló")
            exit(1)
    except KeyboardInterrupt:
        print("\\nScript interrumpido por el usuario")
        exit(1)
    except Exception as e:
        print(f"\\nError inesperado: {{e}}")
        exit(1)
'''
    
    with open(f"{transaccion.lower()}_nite_style.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"✅ Script generado: {transaccion.lower()}_nite_style.py")

def main():
    """
    Función principal que genera todos los scripts
    """
    print("🚀 GENERANDO SCRIPTS EN ESTILO NITE")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Lista de scripts a generar
    scripts = [
        ("ZSD_INCIDENCIAS", "data_incidencias.xls", "Reporte de Incidencias"),
        ("MB51", "data_mb51.xls", "Reporte de Movimientos de Material"),
        ("REP_PLR", "data_rep_plr.xls", "Reporte de Planeamiento"),
        ("Y_DEV_45", "data_y_dev_45.xls", "Reporte Y_DEV_45"),
        ("Y_DEV_74", "data_y_dev_74.xls", "Reporte Y_DEV_74"),
        ("Y_DEV_82", "data_y_dev_82.xls", "Reporte Y_DEV_82"),
        ("Z_DEVO_ALV", "data_z_devo_alv.xls", "Reporte Z_DEVO_ALV"),
        ("ZHBO", "data_zhbo.xls", "Reporte ZHBO"),
        ("ZRED", "data_zred.xls", "Reporte ZRED")
    ]
    
    generados = 0
    
    for transaccion, archivo, descripcion in scripts:
        print(f"\n🔄 Generando script: {transaccion}")
        try:
            generar_script_nite(transaccion, archivo, descripcion)
            generados += 1
        except Exception as e:
            print(f"❌ Error generando {transaccion}: {e}")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE GENERACIÓN")
    print("=" * 80)
    print(f"✅ Scripts generados: {generados}")
    print(f"📁 Ubicación: {os.getcwd()}")
    print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if generados == len(scripts):
        print("🎉 TODOS LOS SCRIPTS GENERADOS EXITOSAMENTE")
        print("✅ Los scripts están listos para usar")
        return True
    else:
        print(f"⚠️  {len(scripts) - generados} SCRIPTS NO SE GENERARON")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Generación completada exitosamente")
            exit(0)
        else:
            print("\n❌ Generación completada con errores")
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Generación interrumpida por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        exit(1)
