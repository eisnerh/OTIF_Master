# Configuración y Cambios - Reporte PLR NITE

## Resumen de Implementación

Este reporte se creó a partir del modelo de **Reporte_Monitor_Guías** con las siguientes características específicas para PLR NITE.

## Características Principales

### 1. Auto-Login Inteligente
- **Si SAP no está abierto**: Inicia SAP automáticamente y hace login
- **Si SAP ya está abierto**: Crea una nueva sesión sin interrumpir el trabajo actual

### 2. Fecha de HOY
- A diferencia de otros scripts que usan AYER, este usa la **fecha actual**

### 3. Procesamiento de Datos Personalizado

El archivo Excel generado tiene el siguiente procesamiento automático:

```
Paso 1: Eliminar Columna A (primera columna)
Paso 2: Eliminar Fila 5 (después de eliminar columna A)
Paso 3: Eliminar las primeras 3 filas (después de eliminar fila 5)
```

### 4. Logs sin Emojis
Todos los mensajes usan texto plano en lugar de emojis:
- `[OK]` en lugar de ✅
- `[ERROR]` en lugar de ❌
- `[ADVERTENCIA]` en lugar de ⚠️
- `[INFO]` en lugar de 📊
- etc.

## Configuración del Sistema

### Archivos de Configuración

**credentials.ini**
```ini
[AUTH]
sap_system = SAP R/3 Productivo [FIFCOR3]
sap_client = 700
sap_user = tu_usuario
sap_password = tu_contraseña
sap_language = ES
```

### Parámetros del Script

Ubicación: `amalgama_y_rep_plr.py` (líneas 70-76)

```python
TCODE       = "zsd_rep_planeamiento"  # Transacción SAP
NODE_KEY    = "F00120"                # Nodo del árbol
ROW_NUMBER  = 11                      # Fila a seleccionar en ALV
OUTPUT_DIR  = Path(r"C:/data/SAP_Extraction/rep_plr_nite")
DATE_STR    = datetime.now().strftime("%d.%m.%Y")  # Fecha HOY
FILENAME    = "REP_PLR_NITE.txt"     # Nombre del archivo TXT
```

## Archivos Generados

El script genera 2 archivos en: `C:\data\SAP_Extraction\rep_plr_nite\`

1. **REP_PLR_NITE.txt**
   - Archivo de texto exportado desde SAP
   - Formato tabulado (TSV)

2. **REP_PLR_NITE_YYYY-MM-DD_processed.xlsx**
   - Archivo Excel procesado
   - Sin columna A
   - Sin fila 5 original
   - Sin las primeras 3 filas
   - Listo para análisis

## Procesamiento Detallado

### Ejemplo de Procesamiento

Si el archivo original tiene esta estructura:

```
Archivo Original (con tabulaciones):
Col_A    Col_B    Col_C    Col_D
Fila_1   Dato1    Dato2    Dato3
Fila_2   Dato4    Dato5    Dato6
Fila_3   Dato7    Dato8    Dato9
Fila_4   Dato10   Dato11   Dato12
Fila_5   Dato13   Dato14   Dato15  <- Esta fila se elimina
Fila_6   Dato16   Dato17   Dato18
...
```

**Después del Paso 1** (Eliminar Columna A):
```
Col_B    Col_C    Col_D
Dato1    Dato2    Dato3
Dato4    Dato5    Dato6
Dato7    Dato8    Dato9
Dato10   Dato11   Dato12
Dato13   Dato14   Dato15  <- Esta fila se elimina en Paso 2
Dato16   Dato17   Dato18
...
```

**Después del Paso 2** (Eliminar Fila 5):
```
Col_B    Col_C    Col_D
Dato1    Dato2    Dato3   <- Estas 3 filas se eliminan en Paso 3
Dato4    Dato5    Dato6   <- 
Dato7    Dato8    Dato9   <-
Dato10   Dato11   Dato12
Dato16   Dato17   Dato18
...
```

**Archivo Final** (Después del Paso 3):
```
Dato10   Dato11   Dato12
Dato16   Dato17   Dato18
...
```

## Logs del Sistema

Durante la ejecución, verás logs como estos:

```
[PROCESO] Procesando archivo: C:\data\SAP_Extraction\rep_plr_nite\REP_PLR_NITE.txt
[INFO] Dimension inicial del archivo: 50 filas x 15 columnas
[OK] Columna A eliminada. Dimensiones: 50 filas x 14 columnas
[OK] Fila 5 eliminada. Dimensiones: 49 filas x 14 columnas
[OK] Primeras 3 filas eliminadas. Dimensiones: 46 filas x 14 columnas
[OK] Archivo procesado y guardado: C:\data\SAP_Extraction\rep_plr_nite\REP_PLR_NITE_2025-11-05_processed.xlsx
```

## Ejecución

### Manual
```batch
ejecutar_rep_plr.bat
```

### Programada (Automática)
```powershell
# Abrir PowerShell como Administrador
cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap\Reporte_PLR_Nite"

# Configurar tarea programada (ejecutar cada hora entre 14:00 y 22:00)
.\configurar_tarea_programada.ps1
```

### Verificar Configuración
```bash
python verificar_instalacion.py
```

## Diferencias con Otros Reportes

| Característica | Monitor Guías | Reporte PLR | **Reporte PLR NITE** |
|----------------|---------------|-------------|----------------------|
| Transacción | y_dev_42000074 | zsd_rep_planeamiento | zsd_rep_planeamiento |
| Nodo | F00119 | F00120 | F00120 |
| Fila ALV | 25 | 11 | 11 |
| Fecha | AYER | HOY | HOY |
| Logs | Con emojis | Con emojis | **Texto plano** |
| Carpeta salida | y_dev_74 | rep_plr | **rep_plr_nite** |
| Archivo | Monitor_Guias.txt | REP_PLR.txt | **REP_PLR_NITE.txt** |
| Procesar Columna A | No | No | **Sí (elimina)** |
| Procesar Fila 5 | No | No | **Sí (elimina)** |
| Filas a eliminar | 5 | 5 | **3 (después de limpiezas)** |

## Mantenimiento

### Cambiar Parámetros

Edita `amalgama_y_rep_plr.py`:

```python
# Para cambiar la transacción
TCODE = "otra_transaccion"

# Para cambiar el nodo del árbol
NODE_KEY = "F00999"

# Para cambiar la fila a seleccionar
ROW_NUMBER = 15

# Para cambiar la carpeta de salida
OUTPUT_DIR = Path(r"C:/otra/ruta")
```

### Modificar Procesamiento de Datos

Si necesitas cambiar qué columnas o filas se eliminan, edita la función `process_tab_file()` en `amalgama_y_rep_plr.py` (líneas 257-292).

## Solución de Problemas

### El archivo Excel está vacío
**Causa**: Se eliminaron demasiadas filas/columnas

**Solución**: Verifica los logs para ver las dimensiones del archivo en cada paso. Ajusta el procesamiento si es necesario.

### Las columnas no son las esperadas
**Causa**: El archivo de SAP cambió su estructura

**Solución**: 
1. Revisa el archivo TXT original
2. Ajusta el procesamiento en `process_tab_file()`
3. Considera cambiar qué columnas se eliminan

### Los logs muestran dimensiones incorrectas
**Causa**: El archivo de entrada tiene una estructura diferente

**Solución**: Ejecuta el script manualmente y revisa los logs detallados

## Estructura de Archivos

```
Reporte_PLR_Nite/
├── amalgama_y_rep_plr.py           # Script principal
├── y_rep_plr.py                    # Módulo de extracción SAP
├── ejecutar_rep_plr.bat            # Ejecutar manualmente
├── configurar_tarea_programada.ps1 # Configurar automatización
├── verificar_instalacion.py        # Verificar requisitos
├── credentials.ini.example         # Plantilla de credenciales
├── credentials.ini                 # Credenciales (NO SUBIR A GIT)
├── .gitignore                      # Protección de archivos
├── INICIO_RAPIDO.md               # Guía de inicio rápido
├── README_REPORTE_PLR.md          # Documentación completa
├── RESUMEN_PROYECTO.md            # Resumen del proyecto
└── CAMBIOS_Y_CONFIGURACION.md     # Este archivo
```

## Notas Importantes

1. **Credenciales**: NUNCA subir `credentials.ini` a Git
2. **Orden de procesamiento**: El orden es importante:
   - Primero columna A
   - Luego fila 5
   - Finalmente primeras 3 filas
3. **Logs**: Todos los logs son en texto plano para mejor compatibilidad
4. **Fecha**: Siempre usa HOY, no ayer

## Próximos Pasos

Para usar el sistema:

1. ✅ Configurar `credentials.ini` con tus datos SAP
2. ✅ Ejecutar `verificar_instalacion.py` para verificar requisitos
3. ✅ Probar manualmente con `ejecutar_rep_plr.bat`
4. ✅ Revisar el archivo Excel generado
5. ✅ Configurar automatización (opcional)

---

**Versión**: 1.0.0  
**Fecha**: 2025-11-05  
**Estado**: Listo para usar


