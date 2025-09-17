import win32com.client
from datetime import datetime
import os

# Verificar si la hora actual es después de las 2 PM
hora_actual = datetime.now().hour
if hora_actual >= 14:
    fecha_hoy = datetime.today().strftime('%Y%m%d')

    # Ruta y nombre del archivo
    nombre_archivo = "REP_PLR_HOY.xls"
    ruta_guardado = os.path.join(os.environ["USERPROFILE"], "Documents", nombre_archivo)

    # Eliminar archivo si ya existe
    if os.path.exists(ruta_guardado):
        os.remove(ruta_guardado)

    # Conexión con SAP GUI
    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    application = SapGuiAuto.GetScriptingEngine
    connection = application.Children(0)
    session = connection.Children(0)

    # Automatización SAP
    session.findById("wnd[0]").maximize()
    session.findById("wnd[0]/tbar[0]/okcd").text = "zsd_rep_planeamiento"
    session.findById("wnd[0]").sendVKey(0)

    session.findById("wnd[0]/tbar[1]/btn[17]").press()
    session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
    session.findById("wnd[1]/usr/txtENAME-LOW").setFocus()
    session.findById("wnd[1]/usr/txtENAME-LOW").caretPosition = 0
    session.findById("wnd[1]/tbar[0]/btn[8]").press()

    session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").currentCellRow = 11
    session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = "11"
    session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").doubleClickCurrentCell()

    session.findById("wnd[0]/usr/ctxtP_LFDAT-LOW").setFocus()
    session.findById("wnd[0]/usr/ctxtP_LFDAT-LOW").caretPosition = 1
    session.findById("wnd[0]").sendVKey(4)
    session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell").focusDate = fecha_hoy
    session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell").selectionInterval = f"{fecha_hoy},{fecha_hoy}"

    session.findById("wnd[0]/tbar[1]/btn[8]").press()

    session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()

    session.findById("wnd[1]/usr/ctxtDY_PATH").text = os.path.dirname(ruta_guardado)
    session.findById("wnd[1]/usr/ctxtDY_PATH").setFocus()
    session.findById("wnd[1]/usr/ctxtDY_PATH").caretPosition = 0
    session.findById("wnd[1]").sendVKey(4)
    session.findById("wnd[2]/usr/ctxtDY_FILENAME").text = nombre_archivo
    session.findById("wnd[2]/usr/ctxtDY_FILE_ENCODING").text = "0000"
    session.findById("wnd[2]/usr/ctxtDY_FILENAME").caretPosition = len(nombre_archivo)
    session.findById("wnd[2]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()

    print("Script ejecutado correctamente con la fecha de hoy. Archivo guardado en:", ruta_guardado)
else:
    print("La hora actual es antes de las 2 PM. El script no se ejecuta.")
