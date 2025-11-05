# Automatización de Reporte PLR

Este documento explica cómo usar y configurar el reporte automático de PLR (Planeamiento).

## [LISTA] Descripción

El script `amalgama_y_rep_plr.py` automatiza la extracción del reporte PLR desde SAP con las siguientes características:

- [OK] **Auto-login**: Si SAP no está abierto, lo inicia y hace login automáticamente
- [OK] **Nueva sesión**: Si SAP ya está abierto, crea una nueva sesión sin interferir con tu trabajo actual
- [OK] **Fecha de hoy**: Usa la fecha actual (no ayer) para la extracción
- [OK] **Datos limpios**: Procesa y limpia automáticamente los datos exportados
- [OK] **Formato Excel**: Convierte el archivo de texto a Excel (.xlsx)

## [INICIO] Requisitos Previos

1. **Python 3.7+** instalado y en el PATH del sistema
2. **SAP GUI** instalado y configurado
3. **Dependencias Python**:
   ```bash
   pip install pandas openpyxl pywin32
   ```
4. **Archivo de credenciales** configurado (ver sección Configuración)

## [CONFIG] Configuración

### Paso 1: Configurar Credenciales

1. Copia el archivo `credentials.ini.example` a `credentials.ini`:
   ```bash
   copy credentials.ini.example credentials.ini
   ```

2. Edita `credentials.ini` con tus credenciales SAP:
   ```ini
   [AUTH]
   sap_system = SAP R/3 Productivo [FIFCOR3]
   sap_client = 700
   sap_user = tu_usuario
   sap_password = tu_contraseña
   sap_language = ES
   ```

   **[ADVERTENCIA] IMPORTANTE**: 
   - El nombre del sistema (`sap_system`) debe coincidir EXACTAMENTE con el nombre que aparece en SAP Logon
   - NO subas el archivo `credentials.ini` a repositorios públicos

### Paso 2: Ajustar Parámetros (Opcional)

Si necesitas ajustar los parámetros del reporte, edita las constantes en `amalgama_y_rep_plr.py`:

```python
TCODE       = "zsd_rep_planeamiento"  # Código de transacción
NODE_KEY    = "F00120"                # Nodo del árbol
ROW_NUMBER  = 11                      # Fila a seleccionar en el ALV
OUTPUT_DIR  = Path(r"C:/data/SAP_Extraction/rep_plr")  # Carpeta de salida
```

## [OBJETIVO] Uso

### Ejecución Manual

#### Opción 1: Usar el archivo batch (Recomendado)
```batch
ejecutar_rep_plr.bat
```

#### Opción 2: Ejecutar directamente con Python
```bash
python amalgama_y_rep_plr.py
```

### Ejecución Automática (Programada)

Para ejecutar el reporte automáticamente cada hora:

#### Windows - Programador de Tareas

1. Abre PowerShell como **Administrador**
2. Navega a la carpeta del script:
   ```powershell
   cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap\Reporte_PLR"
   ```
3. Ejecuta el script de configuración:
   ```powershell
   .\configurar_tarea_programada.ps1
   ```

**Personalizar horario:**
```powershell
# Ejecutar entre 8:00 y 18:00
.\configurar_tarea_programada.ps1 -HoraInicio "08:00" -HoraFin "18:00"

# Ejecutar 24 horas al día
.\configurar_tarea_programada.ps1 -SoloHorarioLaboral:$false
```

## [DASHBOARD] Archivos Generados

El script genera dos archivos en la carpeta de salida (por defecto: `C:\data\SAP_Extraction\rep_plr`):

1. **REP_PLR.txt**: Archivo de texto exportado desde SAP
2. **REP_PLR_YYYY-MM-DD_processed.xlsx**: Archivo Excel procesado y limpio

### Procesamiento de Datos

El archivo Excel procesado tiene las siguientes transformaciones:
- [OK] Conversión de formato tabulado (TXT) a Excel (XLSX)
- [OK] Eliminación de las primeras 5 filas (encabezados/títulos de SAP)
- [OK] Formato limpio listo para análisis

## [BUSCAR] Verificación

### Logs
El script muestra información detallada en la consola:
- Estado de conexión a SAP
- Progreso de la extracción
- Ubicación de archivos generados
- Errores (si los hay)

### Verificar Tarea Programada

**Ver estado de la tarea:**
```powershell
Get-ScheduledTask -TaskName "OTIF_Reporte_PLR_Hourly"
```

**Ver historial de ejecuciones:**
1. Abre el Programador de Tareas (`taskschd.msc`)
2. Busca la tarea `OTIF_Reporte_PLR_Hourly`
3. Ve a la pestaña "Historial"

## [ELIMINAR] Desinstalar Tarea Programada

```powershell
Unregister-ScheduledTask -TaskName "OTIF_Reporte_PLR_Hourly" -Confirm:$false
```

## [ERROR] Solución de Problemas

### Error: "No se encontró credentials.ini"
**Solución**: Crea el archivo `credentials.ini` copiando `credentials.ini.example` y configura tus credenciales.

### Error: "No se encontró el objeto SAPGUI"
**Causas posibles**:
- SAP GUI no está instalado
- SAP GUI Scripting no está habilitado

**Solución**: 
1. Verifica que SAP GUI esté instalado
2. Habilita SAP GUI Scripting:
   - Abre SAP Logon
   - Ve a Opciones → Accesibilidad y scripting → Scripting
   - Marca "Habilitar scripting"

### Error: "No se pudo obtener el motor de scripting"
**Solución**: Habilita SAP GUI Scripting (ver arriba)

### Error: "Fallo al abrir conexión o hacer login"
**Causas posibles**:
- Credenciales incorrectas
- Nombre del sistema SAP incorrecto
- Problemas de red

**Solución**:
1. Verifica las credenciales en `credentials.ini`
2. Asegúrate de que el nombre del sistema coincida exactamente con el de SAP Logon
3. Prueba hacer login manualmente en SAP GUI

### El archivo Excel está vacío o con datos incorrectos
**Causas posibles**:
- El número de fila (`ROW_NUMBER`) es incorrecto
- El nodo del árbol (`NODE_KEY`) es incorrecto
- La fecha no tiene datos

**Solución**:
1. Ejecuta el script con el parámetro `--debug`:
   ```bash
   python y_rep_plr.py --debug
   ```
2. Revisa los mensajes de depuración
3. Ajusta los parámetros en `amalgama_y_rep_plr.py` si es necesario

### "No se encontró el control"
**Causa**: La estructura de SAP cambió o los IDs de controles son diferentes

**Solución**:
1. Ejecuta con `--debug` para ver los controles disponibles
2. Reporta el problema para actualizar el script

## [NOTA] Diferencias con Monitor Guías

| Característica | Monitor Guías (Y_DEV_74) | Reporte PLR (Y_REP_PLR) |
|----------------|--------------------------|-------------------------|
| Transacción | `y_dev_42000074` | `zsd_rep_planeamiento` |
| Nodo del árbol | `F00119` | `F00120` |
| Fila ALV | 25 | 11 |
| Campo de fecha | `SP$00002-LOW` | `P_LFDAT-LOW` |
| Fecha por defecto | Ayer | **Hoy** |
| Archivo salida | `Monitor_Guias.txt` | `REP_PLR.txt` |

##  Seguridad

### Protección de Credenciales

1. **NUNCA** subas el archivo `credentials.ini` a repositorios públicos
2. Agrega `credentials.ini` a tu `.gitignore`:
   ```
   credentials.ini
   ```
3. Protege el acceso a la carpeta que contiene `credentials.ini`
4. Cambia regularmente tu contraseña SAP

### Buenas Prácticas

- Ejecuta el script con tu usuario de Windows (no como administrador)
- Revisa regularmente los logs de ejecución
- Mantén actualizadas las dependencias Python

## [CONTACTO] Soporte

Si tienes problemas:

1. Revisa esta documentación
2. Verifica los logs del script
3. Ejecuta con `--debug` para obtener más información
4. Verifica el historial del Programador de Tareas (si usas ejecución automática)

## [DOCUMENTACION] Archivos del Proyecto

```
Reporte_PLR/
 amalgama_y_rep_plr.py       # Script principal con auto-login
 y_rep_plr.py                # Módulo de extracción SAP
 ejecutar_rep_plr.bat        # Script batch para ejecución manual
 configurar_tarea_programada.ps1  # Script PowerShell para automatización
 credentials.ini.example     # Plantilla de credenciales
 credentials.ini            # Credenciales SAP (NO SUBIR A GIT)
 README_REPORTE_PLR.md      # Esta documentación
```

##  Cómo Funciona

1. **Inicio**: El script verifica si SAP está abierto
2. **Conexión**:
   - Si SAP no está abierto: lo inicia y hace login
   - Si SAP ya está abierto: crea una nueva sesión
3. **Extracción**:
   - Navega a la transacción PLR
   - Selecciona el nodo y la fila correcta
   - Configura la fecha (HOY)
   - Exporta los datos a archivo de texto
4. **Procesamiento**:
   - Espera a que el archivo esté disponible
   - Convierte TXT a Excel
   - Elimina las primeras 5 filas (encabezados SAP)
   - Guarda el archivo limpio
5. **Finalización**: Vuelve a SAP Easy Access

## [NUEVO] Actualizaciones Futuras

Posibles mejoras:
- [ ] Integración con Power BI
- [ ] Envío automático por correo
- [ ] Generación de gráficos automáticos
- [ ] Dashboard web en tiempo real
- [ ] Notificaciones por Telegram/Slack

---

**Versión**: 1.0.0  
**Última actualización**: 2025-11-05  
**Autor**: Equipo OTIF Master

