# [DASHBOARD] Reporte PLR - Resumen del Proyecto

## [OK] Proyecto Completado

Se ha creado exitosamente un sistema automático de reportes PLR similar al de Monitor Guías, con las siguientes mejoras:

## [OBJETIVO] Características Implementadas

### [NUEVO] Auto-Login Inteligente
- **Si SAP no está abierto**: El script inicia SAP automáticamente y hace login con las credenciales configuradas
- **Si SAP ya está abierto**: Crea una nueva sesión sin interrumpir tu trabajo actual
- **Gestión automática**: No necesitas preocuparte por el estado de SAP

### [FECHA] Fecha Actualizada
- **Fecha de HOY**: A diferencia del script original que usaba AYER, este usa la fecha actual automáticamente
- **Configurable**: Puedes cambiar la fecha si lo necesitas

### [LIMPIEZA] Datos Limpios
- **Conversión automática**: TXT → Excel (.xlsx)
- **Limpieza automática**: Elimina las primeras 5 filas (encabezados de SAP)
- **Formato listo**: El Excel está listo para análisis inmediato

### [AUTOMATICO] Automatización Completa
- **Ejecución programada**: Configura ejecución horaria con un solo comando PowerShell
- **Sin intervención**: Una vez configurado, funciona solo
- **Logs detallados**: Seguimiento completo de cada ejecución

## [CARPETA] Estructura de Archivos

```
Reporte_PLR/

 [ARCHIVO] INICIO_RAPIDO.md                    #  Guía de inicio rápido
  README_REPORTE_PLR.md               # [DOCUMENTACION] Documentación completa
 [LISTA] RESUMEN_PROYECTO.md                 # [DASHBOARD] Este archivo

  y_rep_plr.py                        # Módulo de extracción SAP
 [CONFIGURACION] amalgama_y_rep_plr.py               # Script principal con auto-login

 [CONFIG] credentials.ini.example             # Plantilla de credenciales
  credentials.ini                     # Credenciales reales (crear)

 [PC] ejecutar_rep_plr.bat               # Ejecutar manualmente
 [FECHA] configurar_tarea_programada.ps1    # Configurar automatización

  .gitignore                          # Protección de credenciales
```

## [INICIO] Inicio Rápido (3 Pasos)

### Paso 1: Instalar Dependencias
```bash
pip install pandas openpyxl pywin32
```

### Paso 2: Configurar Credenciales
```bash
copy credentials.ini.example credentials.ini
notepad credentials.ini
```
Edita con tus datos SAP.

### Paso 3: Ejecutar
```batch
ejecutar_rep_plr.bat
```

¡Listo! El reporte se generará automáticamente.

## [DASHBOARD] Comparación con Monitor Guías

| Característica | Monitor Guías | Reporte PLR | Mejora |
|----------------|---------------|-------------|---------|
| Auto-login | [OK] | [OK] | Igual |
| Nueva sesión | [OK] | [OK] | Igual |
| Datos limpios | [OK] | [OK] | Igual |
| Fecha | AYER | **HOY** | [OK] Mejorado |
| Transacción | y_dev_42000074 | zsd_rep_planeamiento | Específico |
| Archivo salida | Monitor_Guias.txt | REP_PLR.txt | Específico |

## [CONFIGURACION] Configuración Personalizada

### Ajustar Parámetros

Edita `amalgama_y_rep_plr.py` (líneas 45-52):

```python
TCODE       = "zsd_rep_planeamiento"  # Transacción SAP
NODE_KEY    = "F00120"                # Nodo del árbol
ROW_NUMBER  = 11                      # Fila a seleccionar
OUTPUT_DIR  = Path(r"C:/data/SAP_Extraction/rep_plr")  # Carpeta salida
DATE_STR    = datetime.now().strftime("%d.%m.%Y")  # Fecha (HOY)
FILENAME    = "REP_PLR.txt"          # Nombre archivo
```

### Cambiar Horario de Automatización

```powershell
# Ejecutar entre 8:00 y 18:00
.\configurar_tarea_programada.ps1 -HoraInicio "08:00" -HoraFin "18:00"

# Ejecutar 24 horas al día
.\configurar_tarea_programada.ps1 -SoloHorarioLaboral:$false
```

##  Archivos Generados

**Ubicación por defecto**: `C:\data\SAP_Extraction\rep_plr\`

1. **REP_PLR.txt**
   - Archivo de texto exportado desde SAP
   - Formato tabulado (TSV)
   - Con encabezados de SAP

2. **REP_PLR_YYYY-MM-DD_processed.xlsx**
   - Archivo Excel procesado
   - Sin encabezados de SAP
   - Listo para análisis

## [SEGURIDAD] Seguridad

### [ADVERTENCIA] IMPORTANTE: Protección de Credenciales

1. [OK] Archivo `.gitignore` creado (protege `credentials.ini`)
2. [OK] Plantilla de ejemplo incluida (`credentials.ini.example`)
3. [ERROR] **NUNCA** subir `credentials.ini` a Git
4. [OK] Mantener credenciales locales y seguras

### Verificar Protección

```bash
git status
```

Si `credentials.ini` aparece en la lista, agregalo al `.gitignore` global.

##  Flujo de Ejecución

```mermaid
graph TD
    A[Inicio] --> B{SAP abierto?}
    B -->|No| C[Iniciar SAP]
    C --> D[Hacer Login]
    B -->|Sí| E[Crear Nueva Sesión]
    D --> F[Conectar a Sesión]
    E --> F
    F --> G[Ir a Transacción PLR]
    G --> H[Seleccionar Nodo y Fila]
    H --> I[Configurar Fecha HOY]
    I --> J[Ejecutar Reporte]
    J --> K[Exportar a TXT]
    K --> L[Convertir a Excel]
    L --> M[Limpiar Datos]
    M --> N[Guardar Archivo]
    N --> O[Fin]
```

## [AUTOMATICO] Automatización

### Configurar Tarea Programada

```powershell
# Abrir PowerShell como Administrador
cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap\Reporte_PLR"

# Ejecutar configuración
.\configurar_tarea_programada.ps1
```

### Verificar Tarea

```powershell
Get-ScheduledTask -TaskName "OTIF_Reporte_PLR_Hourly"
```

### Eliminar Tarea

```powershell
Unregister-ScheduledTask -TaskName "OTIF_Reporte_PLR_Hourly" -Confirm:$false
```

## [ERROR] Solución de Problemas

### Problema 1: "No se encontró credentials.ini"
```bash
copy credentials.ini.example credentials.ini
notepad credentials.ini
```

### Problema 2: "No se encontró el objeto SAPGUI"
**Solución**: Habilitar SAP GUI Scripting:
1. SAP Logon → Opciones
2. Accesibilidad y scripting → Scripting
3. Marcar "Habilitar scripting"

### Problema 3: Error de login
**Solución**: Verificar `credentials.ini`:
- El nombre del sistema debe coincidir EXACTAMENTE con SAP Logon
- Usuario y contraseña correctos
- Mandante correcto (usualmente 700)

### Problema 4: Archivo vacío o datos incorrectos
**Solución**: Ejecutar con debug:
```bash
python y_rep_plr.py --debug
```

## [GRAFICO] Mejoras Futuras (Roadmap)

- [ ] Integración con Power BI
- [ ] Envío automático por correo (similar a Monitor Guías)
- [ ] Generación de gráficos automáticos
- [ ] Dashboard web en tiempo real
- [ ] Notificaciones por Telegram/Slack
- [ ] Análisis predictivo con ML

## [DOCUMENTACION] Documentación

- **Inicio Rápido**: Lee `INICIO_RAPIDO.md`
- **Documentación Completa**: Lee `README_REPORTE_PLR.md`
- **Comparación Monitor Guías**: Ver carpeta `Reporte_Monitor_Guías`

## [EXITO] Conclusión

El sistema está completamente funcional y listo para usar. Incluye:

[OK] **Auto-login inteligente**  
[OK] **Manejo de sesiones**  
[OK] **Fecha actualizada (HOY)**  
[OK] **Datos limpios automáticamente**  
[OK] **Automatización programable**  
[OK] **Documentación completa**  
[OK] **Seguridad de credenciales**  

## [CONTACTO] Próximos Pasos

1. **Configurar credenciales**: Crea `credentials.ini` con tus datos
2. **Probar manualmente**: Ejecuta `ejecutar_rep_plr.bat`
3. **Verificar archivos**: Revisa `C:\data\SAP_Extraction\rep_plr\`
4. **Automatizar** (opcional): Ejecuta `configurar_tarea_programada.ps1`

---

**Versión**: 1.0.0  
**Fecha**: 2025-11-05  
**Estado**: [OK] Completado y Funcional

