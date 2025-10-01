#!/usr/bin/env python3
"""
Script ZSD_INCIDENCIAS replicando exactamente la funcionalidad del entorno NITE
Basado en nuevo_rep_plr.py que funciona correctamente
"""

import win32com.client
from datetime import datetime
import os
import time

def ejecutar_zsd_incidencias():
    """
    Ejecuta la transacción ZSD_INCIDENCIAS usando el método del entorno NITE
    """
    print("INICIANDO SCRIPT ZSD_INCIDENCIAS - ESTILO NITE")
    print("=" * 60)
    print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # File path and name
    fecha_actual = datetime.now().strftime('%d-%m-%Y')
    file_name = f"zsd_incidencias_{fecha_actual}.xls"
    saved_path = os.path.join("C:/data/zsd_incidencias", file_name)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(saved_path), exist_ok=True)
    
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
        print("Navegando a transacción: zsd_incidencias")
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "zsd_incidencias"
        session.findById("wnd[0]").sendVKey(0)
        
        print("Presionando botón de selección...")
        session.findById("wnd[0]/tbar[1]/btn[17]").press()
        
        print("Limpiando campo de usuario...")
        session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
        session.findById("wnd[1]/usr/txtENAME-LOW").setFocus()
        session.findById("wnd[1]/usr/txtENAME-LOW").caretPosition = 0
        session.findById("wnd[1]/tbar[0]/btn[8]").press()
        
        print("Seleccionando fila 12...")
        session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").currentCellRow = 12
        session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = "12"
        session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").doubleClickCurrentCell()
        
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
            
            print("\n" + "=" * 60)
            print("PROCESO ZSD_INCIDENCIAS COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            print(f"Archivo generado: {file_name}")
            print(f"Ubicación: {saved_path}")
            print(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            return True
        else:
            print("ERROR: El archivo no se generó correctamente")
            return False
        
    except Exception as e:
        print(f"Error during SAP automation: {e}")
        return False

def main():
    """
    Función principal
    """
    try:
        success = ejecutar_zsd_incidencias()
        
        if success:
            print("\nScript ZSD_INCIDENCIAS ejecutado exitosamente")
            return True
        else:
            print("\nScript ZSD_INCIDENCIAS falló")
            return False
            
    except Exception as e:
        print(f"\nError inesperado: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nScript completado exitosamente")
            exit(0)
        else:
            print("\nScript falló")
            exit(1)
    except KeyboardInterrupt:
        print("\nScript interrumpido por el usuario")
        exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        exit(1)
