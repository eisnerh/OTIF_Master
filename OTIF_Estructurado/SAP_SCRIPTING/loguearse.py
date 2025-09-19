import win32com.client
import time

# Parámetros de conexión
sap_system = "SAP R/3 Productivo [FIFCOR3]"  # Nombre del sistema en SAP Logon
mandante = "700"
usuario = "elopez21334"
password = "Thunderx.2367"

try:
    # Conectar al SAP GUI
    SapGuiAuto = win32com.client.GetObject("SAPGUI")
    if not SapGuiAuto:
        print("SAP GUI no está disponible.")
        exit()

    application = SapGuiAuto.GetScriptingEngine
    connection = application.OpenConnection(sap_system, True)
    session = connection.Children(0)

    # Iniciar sesión
    session.findById("wnd[0]/usr/txtRSYST-MANDT").text = mandante
    session.findById("wnd[0]/usr/txtRSYST-BNAME").text = usuario
    session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
    session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "ES"  # Idioma
    session.findById("wnd[0]").sendVKey(0)

    print("✅ Sesión iniciada correctamente en SAP")

except Exception as e:
    print(f"❌ Error al iniciar sesión en SAP: {e}")
