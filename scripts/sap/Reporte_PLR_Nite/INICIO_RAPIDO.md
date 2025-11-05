# [INICIO] Inicio Rápido - Reporte PLR

##  Configuración en 4 Pasos

### 1. Instalar Dependencias
```bash
pip install pandas openpyxl pywin32
```

### 2. Configurar Credenciales
```bash
copy credentials.ini.example credentials.ini
```
Luego edita `credentials.ini` con tus datos SAP.

### 3. Verificar Instalación (Opcional pero Recomendado)
```bash
python verificar_instalacion.py
```
Este script verifica que todo esté configurado correctamente.

### 4. Ejecutar
```batch
ejecutar_rep_plr.bat
```

## [LISTA] Credenciales SAP

Edita `credentials.ini`:
```ini
[AUTH]
sap_system = SAP R/3 Productivo [FIFCOR3]
sap_client = 700
sap_user = TU_USUARIO
sap_password = TU_CONTRASEÑA
sap_language = ES
```

## [NUEVO] Características Principales

[OK] **Auto-login**: Si SAP no está abierto, se inicia automáticamente  
[OK] **Nueva sesión**: Si SAP ya está abierto, crea una sesión nueva  
[OK] **Fecha de hoy**: Usa la fecha actual automáticamente  
[OK] **Excel limpio**: Genera archivo `.xlsx` procesado y listo para usar  

## [CARPETA] Archivos Generados

Los archivos se guardan en: `C:\data\SAP_Extraction\rep_plr\`

- `REP_PLR.txt` - Archivo exportado de SAP
- `REP_PLR_YYYY-MM-DD_processed.xlsx` - Excel procesado y limpio

## [AUTOMATICO] Automatización (Opcional)

Para ejecutar automáticamente cada hora:

1. Abre PowerShell como **Administrador**
2. Navega a esta carpeta
3. Ejecuta:
```powershell
.\configurar_tarea_programada.ps1
```

## [ERROR] Problemas Comunes

### [ERROR] "No se encontró credentials.ini"
**Solución**: Crea el archivo copiando el ejemplo y configurándolo.

### [ERROR] "No se encontró el objeto SAPGUI"
**Solución**: Habilita SAP GUI Scripting en SAP Logon:
- Opciones → Accesibilidad y scripting → Scripting → Habilitar

### [ERROR] Error de login
**Solución**: Verifica que el nombre del sistema en `credentials.ini` coincida EXACTAMENTE con el de SAP Logon.

## [DOCUMENTACION] Documentación Completa

Lee `README_REPORTE_PLR.md` para documentación detallada.

---

¿Preguntas? Revisa los logs del script o el historial del Programador de Tareas.

