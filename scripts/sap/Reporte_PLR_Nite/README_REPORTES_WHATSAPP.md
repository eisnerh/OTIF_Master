# Sistema de Reportes Gráficos para WhatsApp

## Descripción

Este sistema genera automáticamente reportes gráficos tipo dashboard a partir de los datos de SAP y los prepara para enviar por WhatsApp.

## Características

- [OK] **Generación automática** de reportes gráficos
- [OK] **Estilo dashboard** similar a Power BI
- [OK] **Optimizado para WhatsApp** (tamaño y calidad)
- [OK] **Múltiples gráficos**: KPIs, barras, líneas, comparativos
- [OK] **Envío automático** o manual por WhatsApp
- [OK] **Sin emojis** (texto plano para mayor compatibilidad)

## Estructura del Reporte

El reporte incluye:

### 1. KPIs Principales (Fila Superior)
- TOTAL VENTA
- RURAL
- GAM
- MODERNO
- HA

### 2. Gráficos de Análisis
- **MACROCANALES**: Distribución de ventas por canal
- **FUERZA DE VENTAS**: Rendimiento por equipo
- **CEDIS**: Cajas equivalentes vs capacidad
- **CAJAS FÍSICAS**: Distribución por centro

### 3. Comparativos por Canal
- MODERNO: Cajas físicas vs equivalentes
- INDIRECTO: Cajas físicas vs equivalentes

### 4. Estado de Planificación
- Por CEDIS
- A nivel país
- Cajas físicas y equivalentes

## Instalación

### 1. Instalar Dependencias

```bash
pip install matplotlib seaborn pandas openpyxl
```

### 2. Para Envío Automático por WhatsApp (Opcional)

```bash
pip install pywhatkit
```

## Uso

### Opción 1: Ejecución Automática (Recomendado)

El reporte se genera automáticamente cuando ejecutas el script principal:

```batch
ejecutar_rep_plr.bat
```

Esto hará:
1. Extraer datos de SAP
2. Procesar el archivo Excel
3. **Generar el reporte gráfico automáticamente**
4. Guardar todos los archivos

### Opción 2: Generar Reporte Manualmente

Si ya tienes el archivo Excel procesado:

```bash
python generar_reporte_grafico.py --archivo "ruta/al/archivo_processed.xlsx"
```

**Ejemplo:**
```bash
python generar_reporte_grafico.py --archivo "C:\data\SAP_Extraction\rep_plr_nite\REP_PLR_NITE_2025-11-05_processed.xlsx"
```

### Opción 3: Especificar Ruta de Salida

```bash
python generar_reporte_grafico.py --archivo "archivo.xlsx" --output "C:\reportes\mi_reporte.png"
```

## Envío por WhatsApp

### Método 1: Manual (Por Defecto)

El script muestra la ubicación del archivo PNG generado. Simplemente:

1. Abre WhatsApp en tu teléfono o WhatsApp Web
2. Selecciona el contacto o grupo
3. Adjunta la imagen generada
4. Envía

**Archivo generado**: `C:\data\SAP_Extraction\rep_plr_nite\reporte_grafico_YYYYMMDD_HHMMSS.png`

### Método 2: Script de Envío

```bash
python enviar_whatsapp.py --imagen "reporte_grafico_20251105_140530.png" --numeros "+50612345678"
```

**Con múltiples destinatarios:**
```bash
python enviar_whatsapp.py --imagen "reporte.png" --numeros "+50612345678,+50687654321"
```

**Con mensaje personalizado:**
```bash
python enviar_whatsapp.py --imagen "reporte.png" --numeros "+50612345678" --mensaje "Reporte PLR del dia"
```

### Método 3: WhatsApp Web Automático

```bash
python enviar_whatsapp.py --imagen "reporte.png" --numeros "+50612345678" --metodo web
```

Abre WhatsApp Web automáticamente con el contacto seleccionado.

### Método 4: PyWhatKit (Envío Totalmente Automático)

**Requisito**: `pip install pywhatkit`

```bash
python enviar_whatsapp.py --imagen "reporte.png" --numeros "+50612345678" --metodo pywhatkit
```

**Nota**: Este método abre WhatsApp Web y envía automáticamente el mensaje.

## Configuración de WhatsApp

Puedes configurar los destinatarios y método de envío en `credentials.ini`:

```ini
[WHATSAPP]
# Método: pywhatkit, web, manual
metodo = manual

# Números (con código de país, separados por coma)
numeros = +50612345678,+50687654321

# Mensaje predeterminado
mensaje = Reporte PLR NITE - Dashboard de Ventas
```

## Personalización del Reporte

### Modificar Colores

Edita `generar_reporte_grafico.py` (líneas 19-24):

```python
COLOR_PRIMARY = '#1f77b4'    # Azul
COLOR_SECONDARY = '#ff7f0e'  # Naranja
COLOR_SUCCESS = '#2ca02c'    # Verde
COLOR_DANGER = '#d62728'     # Rojo
COLOR_INFO = '#17becf'       # Cyan
COLOR_WARNING = '#bcbd22'    # Amarillo-verde
```

### Modificar Tamaño de Imagen

Edita la línea 93:

```python
fig = plt.figure(figsize=(16, 20), dpi=100)
```

- `figsize`: Tamaño en pulgadas (ancho, alto)
- `dpi`: Resolución (100-150 recomendado para WhatsApp)

### Agregar/Quitar Gráficos

Edita las secciones de gráficos en `generar_reporte_grafico.py`:
- Fila 1 (línea 101): KPIs
- Fila 2 (línea 112): Macrocanales y Fuerza de Ventas
- Fila 3 (línea 161): CEDIS
- Fila 4 (línea 205): Comparativos por Canal
- Fila 5 (línea 247): Estatus de Planificación

## Adaptación a Datos Reales

El script actual usa datos de ejemplo. Para usar tus datos reales, modifica la función `generar_datos_ejemplo()` en `generar_reporte_grafico.py`.

**Pasos:**

1. Analiza la estructura de tu archivo Excel procesado
2. Mapea las columnas a las categorías del reporte
3. Modifica `generar_datos_ejemplo()` para leer los datos reales

**Ejemplo:**

```python
def generar_datos_ejemplo(df):
    """Lee datos reales del DataFrame"""
    
    # Suponiendo que tu DataFrame tiene estas columnas:
    # ['CEDIS', 'CANAL', 'VENTAS', 'CAJAS_FISICAS', ...]
    
    datos = {
        'kpis': {
            'TOTAL VENTA': df['VENTAS'].sum(),
            'RURAL': df[df['ZONA'] == 'RURAL']['VENTAS'].sum(),
            # ... etc
        },
        'macrocanales': df.groupby('CANAL')['VENTAS'].sum().to_dict(),
        # ... etc
    }
    
    return datos
```

## Archivos Generados

Por cada ejecución se generan:

1. **REP_PLR_NITE.txt**: Exportación de SAP (texto tabulado)
2. **REP_PLR_NITE_YYYY-MM-DD_processed.xlsx**: Excel procesado
3. **reporte_grafico_YYYYMMDD_HHMMSS.png**: Reporte gráfico (2-5 MB aprox.)

**Ubicación**: `C:\data\SAP_Extraction\rep_plr_nite\`

## Tamaño y Calidad

- **Tamaño de imagen**: ~2-5 MB (óptimo para WhatsApp)
- **Resolución**: 1600x2000 píxeles @ 100 DPI
- **Formato**: PNG (mejor calidad que JPG para gráficos)

Si necesitas reducir el tamaño:

```python
# Reducir DPI (línea 93)
fig = plt.figure(figsize=(16, 20), dpi=75)

# O comprimir después
plt.savefig(output_path, dpi=100, quality=85)  # Solo para JPG
```

## Programación Automática

Para generar y enviar reportes automáticamente cada hora:

### 1. Configurar Tarea Programada

```powershell
# Abrir PowerShell como Administrador
cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap\Reporte_PLR_Nite"
.\configurar_tarea_programada.ps1
```

### 2. El Reporte se Genera Automáticamente

La tarea programada:
1. Extrae datos de SAP
2. Procesa el Excel
3. **Genera el reporte gráfico**
4. (Opcional) Envía por WhatsApp si está configurado

## Solución de Problemas

### Error: "No module named 'matplotlib'"

```bash
pip install matplotlib seaborn
```

### Error: "No module named 'pywhatkit'"

```bash
pip install pywhatkit
```

### El reporte se ve pixelado

Aumenta el DPI:

```python
fig = plt.figure(figsize=(16, 20), dpi=150)  # Aumentar a 150
```

### Los gráficos están vacíos

Los datos de ejemplo no se están leyendo correctamente. 
Verifica:
1. Que el archivo Excel existe
2. Que tiene datos
3. Que la función `generar_datos_ejemplo()` lee correctamente las columnas

### Error de envío por WhatsApp

**PyWhatKit**:
- Asegúrate de tener WhatsApp Web abierto
- Verifica que el número tiene código de país (+506...)
- Dale tiempo suficiente (wait_time=15)

**Manual**:
- Busca el archivo PNG en la carpeta de salida
- Envíalo manualmente por WhatsApp

## Ejemplos Completos

### Ejemplo 1: Generación y Envío Manual

```batch
# 1. Ejecutar extracción de SAP
ejecutar_rep_plr.bat

# 2. El reporte se genera automáticamente

# 3. Buscar el archivo PNG en:
# C:\data\SAP_Extraction\rep_plr_nite\reporte_grafico_*.png

# 4. Enviar por WhatsApp manualmente
```

### Ejemplo 2: Generación Manual y Envío Automático

```bash
# 1. Si ya tienes el Excel procesado
python generar_reporte_grafico.py --archivo "REP_PLR_NITE_2025-11-05_processed.xlsx"

# 2. Enviar por WhatsApp Web
python enviar_whatsapp.py --imagen "reporte_grafico_20251105_140530.png" --numeros "+50612345678" --metodo web
```

### Ejemplo 3: Todo Automático con Configuración

```ini
# credentials.ini
[WHATSAPP]
metodo = pywhatkit
numeros = +50612345678,+50687654321
mensaje = Reporte PLR NITE del dia
```

```bash
# Ejecutar (genera y puede enviar automáticamente)
ejecutar_rep_plr.bat
```

## Mejoras Futuras

Posibles mejoras a implementar:

- [ ] Lectura automática de estructura de datos reales
- [ ] Detección automática de columnas
- [ ] Más tipos de gráficos (torta, radar, etc.)
- [ ] Exportación a PDF además de PNG
- [ ] Envío por email
- [ ] Envío por Telegram
- [ ] Dashboard interactivo HTML
- [ ] Alertas automáticas basadas en umbrales
- [ ] Comparación con períodos anteriores

## Soporte

### Ver Logs

Durante la ejecución verás logs como:

```
[GRAFICO] Generando reporte grafico para WhatsApp...
[LECTURA] Leyendo archivo: REP_PLR_NITE_2025-11-05_processed.xlsx
[INFO] Dimensiones: 46 filas x 14 columnas
[PROCESO] Generando reporte grafico...
[GRAFICO] Generando KPIs...
[GRAFICO] Generando graficos de canales...
[GRAFICO] Generando graficos de CEDIS...
[GRAFICO] Generando comparativos por canal...
[GRAFICO] Generando graficos de planificacion...
[GUARDANDO] Guardando reporte en: reporte_grafico_20251105_140530.png
[OK] Reporte guardado exitosamente
[EXITO] Reporte generado exitosamente
```

### Archivos de Log

Los logs se muestran en consola. Para guardarlos en archivo:

```bash
python generar_reporte_grafico.py --archivo "archivo.xlsx" > reporte.log 2>&1
```

## Preguntas Frecuentes

**¿Puedo enviar a grupos de WhatsApp?**
- Sí, pero necesitas el ID del grupo (no el nombre). Usa `pywhatkit` con el ID del grupo.

**¿El envío automático funciona 24/7?**
- Sí, si configuras la tarea programada. Pero WhatsApp Web debe estar activo.

**¿Puedo personalizar completamente los gráficos?**
- Sí, edita `generar_reporte_grafico.py`. Usa matplotlib para cualquier tipo de gráfico.

**¿Funciona sin internet?**
- La generación del reporte sí. El envío por WhatsApp requiere internet.

---

**Versión**: 1.0.0  
**Fecha**: 2025-11-05  
**Autor**: Equipo OTIF Master

