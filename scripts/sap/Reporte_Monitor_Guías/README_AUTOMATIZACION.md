# Automatización de Monitor Guías

Este documento explica cómo configurar la ejecución automática del script `amalgama_y_dev_74.py` cada hora.

## 📋 Requisitos Previos

1. **Python instalado** y disponible en el PATH
2. **Archivo `credentials.ini`** configurado correctamente
3. **SAP GUI** instalado y configurado
4. **Permisos de administrador** para crear tareas programadas (solo la primera vez)

## 🚀 Opción 1: Configuración Automática (Recomendada)

### Paso 1: Ejecutar el script de configuración

Abre PowerShell como **Administrador** y ejecuta:

```powershell
cd "C:\Users\eisne\OneDrive\Documents\GitHub\OTIF_Master\scripts\sap\Reporte_Monitor_Guías"
.\configurar_tarea_programada.ps1
```

### Configuración por defecto

- **Horario**: Cada hora entre las 14:00 y 22:00
- **Frecuencia**: Una vez por hora

### Personalizar el horario

Si quieres cambiar el horario, puedes ejecutar:

```powershell
# Ejecutar cada hora entre las 8:00 y 18:00
.\configurar_tarea_programada.ps1 -HoraInicio "08:00" -HoraFin "18:00"

# Ejecutar cada hora las 24 horas del día
.\configurar_tarea_programada.ps1 -SoloHorarioLaboral:$false
```

## 🛠️ Opción 2: Configuración Manual

### Paso 1: Abrir el Programador de Tareas

1. Presiona `Win + R`
2. Escribe `taskschd.msc` y presiona Enter
3. O busca "Programador de Tareas" en el menú Inicio

### Paso 2: Crear la tarea

1. En el panel derecho, haz clic en **"Crear tarea básica"**
2. **Nombre**: `OTIF_Monitor_Guias_Hourly`
3. **Descripción**: `Ejecuta Monitor Guías cada hora`

### Paso 3: Configurar el trigger (desencadenador)

1. Selecciona **"Diariamente"**
2. Establece la **hora de inicio** (ej: 14:00)
3. En **"Repetir cada"**, selecciona **"1 hora"**
4. En **"Durante"**, selecciona **"8 horas"** (para que termine a las 22:00)
   - O selecciona **"Indefinidamente"** si quieres que se ejecute 24 horas

### Paso 4: Configurar la acción

1. Selecciona **"Iniciar un programa"**
2. **Programa o script**: 
   ```
   C:\Users\eisne\OneDrive\Documents\GitHub\OTIF_Master\scripts\sap\Reporte_Monitor_Guías\ejecutar_monitor_guias.bat
   ```
3. **Iniciar en**:
   ```
   C:\Users\eisne\OneDrive\Documents\GitHub\OTIF_Master\scripts\sap\Reporte_Monitor_Guías
   ```

### Paso 5: Configurar condiciones y opciones

En la pestaña **"Condiciones"**:
- ✅ Marca **"Iniciar la tarea solo si el equipo está conectado a la alimentación de CA"** (opcional)
- ✅ Marca **"Activar la tarea si el equipo está en modo de suspensión"** (opcional)

En la pestaña **"Configuración"**:
- ✅ Marca **"Permitir ejecutar la tarea a petición"**
- ✅ Marca **"Si la tarea ya se está ejecutando, aplicar la regla siguiente"** → Selecciona **"No iniciar una nueva instancia"**

### Paso 6: Guardar

1. Haz clic en **"Aceptar"**
2. Ingresa tu contraseña de Windows si se solicita

## 📝 Ejecución Manual

Si quieres ejecutar el script manualmente sin esperar a la tarea programada:

```batch
ejecutar_monitor_guias.bat
```

O directamente con Python:

```bash
python amalgama_y_dev_74.py
```

## 🔍 Verificar la Tarea Programada

### Desde el Programador de Tareas

1. Abre el Programador de Tareas
2. Busca la tarea `OTIF_Monitor_Guias_Hourly`
3. Verifica que esté **"Habilitada"**
4. Revisa el **"Historial"** para ver las ejecuciones anteriores

### Desde PowerShell

```powershell
Get-ScheduledTask -TaskName "OTIF_Monitor_Guias_Hourly"
```

## 🗑️ Eliminar la Tarea Programada

### Desde PowerShell

```powershell
Unregister-ScheduledTask -TaskName "OTIF_Monitor_Guias_Hourly" -Confirm:$false
```

### Desde el Programador de Tareas

1. Abre el Programador de Tareas
2. Busca la tarea `OTIF_Monitor_Guias_Hourly`
3. Haz clic derecho → **"Eliminar"**

## 📊 Verificar Logs

El script genera logs automáticamente. Revisa la consola o los archivos de salida para verificar que la ejecución fue exitosa.

## ⚠️ Notas Importantes

1. **SAP GUI debe estar instalado**: El script requiere SAP GUI para funcionar
2. **El equipo debe estar encendido**: La tarea programada solo se ejecuta si el equipo está encendido
3. **Credenciales**: Asegúrate de que `credentials.ini` esté configurado correctamente
4. **Permisos**: La primera ejecución del script de configuración requiere permisos de administrador

## 🐛 Solución de Problemas

### La tarea no se ejecuta

1. Verifica que la tarea esté **"Habilitada"** en el Programador de Tareas
2. Revisa el **"Historial"** para ver si hay errores
3. Asegúrate de que el equipo esté encendido a la hora programada
4. Verifica que el archivo `ejecutar_monitor_guias.bat` exista en la ubicación correcta

### Error: "Python no está instalado"

1. Verifica que Python esté instalado: `python --version`
2. Asegúrate de que Python esté en el PATH del sistema
3. Puedes agregar la ruta completa a Python en el archivo batch

### Error: "No se encontró credentials.ini"

1. Verifica que el archivo `credentials.ini` exista en el mismo directorio que el script
2. Si no existe, copia `credentials.ini.example` y renómbralo a `credentials.ini`
3. Completa los valores en `credentials.ini`

## 📞 Soporte

Si tienes problemas con la automatización, revisa:
- Los logs del script
- El historial del Programador de Tareas
- La configuración de `credentials.ini`

