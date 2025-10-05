If Not IsObject(application) Then
   Set SapGuiAuto  = GetObject("SAPGUI")
   Set application = SapGuiAuto.GetScriptingEngine
End If
If Not IsObject(connection) Then
   Set connection = application.Children(0)
End If
If Not IsObject(session) Then
   Set session    = connection.Children(0)
End If
If IsObject(WScript) Then
   WScript.ConnectObject session,     "on"
   WScript.ConnectObject application, "on"
End If
session.findById("wnd[0]").maximize
session.findById("wnd[0]/tbar[0]/okcd").text = "zresguias"
session.findById("wnd[0]").sendVKey 0
session.findById("wnd[0]/tbar[1]/btn[17]").press
session.findById("wnd[1]/usr/txtENAME-LOW").text = ""
session.findById("wnd[1]/usr/txtENAME-LOW").setFocus
session.findById("wnd[1]/usr/txtENAME-LOW").caretPosition = 0
session.findById("wnd[1]/tbar[0]/btn[8]").press
session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").currentCellRow = 26
session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").firstVisibleRow = 12
session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").selectedRows = "26"
session.findById("wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell").doubleClickCurrentCell
session.findById("wnd[0]/usr/ctxtPFECHA-LOW").caretPosition = 1
session.findById("wnd[0]").sendVKey 4
session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell").focusDate = "20251004"
session.findById("wnd[1]/usr/cntlCONTAINER/shellcont/shell").selectionInterval = "20251004,20251004"
session.findById("wnd[0]/tbar[1]/btn[8]").press
session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select
session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").setFocus
session.findById("wnd[1]/tbar[0]/btn[0]").press
session.findById("wnd[1]/usr/ctxtDY_PATH").text = "C:\data\SAP_Extraction\Zresguias"
session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = "Zresguias_05-10-2025"
session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").text = "0000"
session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").setFocus
session.findById("wnd[1]/usr/ctxtDY_FILE_ENCODING").caretPosition = 4
session.findById("wnd[1]/tbar[0]/btn[11]").press
session.findById("wnd[0]/tbar[0]/btn[3]").press
session.findById("wnd[0]/tbar[0]/btn[3]").press
