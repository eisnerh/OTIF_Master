# Flujo Completo de Generación y Envío por Email

## Descripción

Este documento explica el flujo completo desde la extracción de SAP hasta el envío del dashboard por correo electrónico.

---

## Flujo Automático Completo

```
1. Usuario ejecuta: ejecutar_monitor_guias.bat
   ↓
2. amalgama_y_dev_74.py
   ├── Auto-login a SAP (si no está abierto)
   ├── Crea nueva sesión (si SAP está abierto)
   ↓
3. y_dev_74.py
   ├── Extrae datos de SAP
   ├── Exporta a Monitor_Guias.txt
   ↓
4. Procesamiento de datos
   ├── Convierte TXT → Excel
   ├── Elimina primeras 5 filas
   ├── Guarda Monitor_Guias_DD-MM-YYYY_processed.xlsx
   ↓
5. generar_dashboard_regional.py
   ├── Lee el Excel procesado
   ├── Mapea zonas a regiones (22 zonas → 4 regiones)
   ├── Genera tabla detallada zona x hora
   ├── Genera tabla resumen por región
   ├── Genera gráfico de tendencias
   ├── Guarda dashboard_regional_YYYYMMDD_HHMMSS.png
   ↓
6. generar_reporte_graficos.py
   ├── Lee el Excel procesado
   ├── Genera gráficos individuales por zona
   ├── BUSCA el dashboard regional generado
   ├── Crea HTML con resumen y descripción
   ├── ADJUNTA todos los archivos:
   │   ├── 1. dashboard_regional_*.png (PRIMERO - Principal)
   │   ├── 2. grafico_todas_zonas.png
   │   ├── 3. grafico_rural.png
   │   ├── 4. grafico_gam.png
   │   ├── 5. grafico_ct01.png (si hay datos)
   │   ├── 6. grafico_ct02.png (si hay datos)
   │   └── 7. Monitor_Guias_*.xlsx (Excel procesado)
   └── ENVÍA CORREO
```

---

## Estructura del Correo

### Asunto:
```
Dashboard Monitor de Guias - Analisis Regional - YYYY-MM-DD HH:MM
```

### Cuerpo HTML:

**Sección 1: Encabezado**
- Título: "Reporte de Monitor de Guias por Zona"
- Fecha de generación

**Sección 2: Total de Guías**
- Valor destacado en grande

**Sección 3: Tabla Resumen por Zona**
- Columnas: Zona, Total de Guías, Porcentaje
- Ordenado por cantidad descendente

**Sección 4: Archivos Adjuntos**
- Lista de archivos incluidos
- Descripción del dashboard regional
- Descripción de gráficos individuales

**Sección 5: Guía de Lectura**
- Cómo leer el Dashboard Regional
- Explicación de KPIs
- Explicación de tablas zona x hora
- Explicación del gráfico de tendencias

### Archivos Adjuntos (en orden):

1. **dashboard_regional_YYYYMMDD_HHMMSS.png** ⭐ **PRINCIPAL**
   - Tablero completo con:
     - KPIs: GAM, RURAL, VYD, SPE, Total
     - Tabla detallada: REGIÓN, ZONA, horas 14:00-23:00
     - Tabla resumen: Por región
     - Gráfico: Tendencias por región
   
2. **grafico_todas_zonas.png**
   - Tendencia de todas las zonas combinadas

3. **grafico_rural.png**
   - Tendencia solo RURAL

4. **grafico_gam.png**
   - Tendencia solo GAM

5. **grafico_ct01.png** (si hay datos)
   - Tendencia solo CT01

6. **grafico_ct02.png** (si hay datos)
   - Tendencia solo CT02

7. **Monitor_Guias_DD-MM-YYYY_processed.xlsx**
   - Datos completos para análisis adicional

---

## Configuración de Email

### Archivo: `credentials.ini`

```ini
[EMAIL]
smtp_server = smtp.gmail.com
smtp_port = 587
email_from = tu_email@gmail.com
email_password = tu_app_password_de_gmail
email_to = destinatario1@example.com, destinatario2@example.com
```

### Para Gmail:

1. Ir a [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Activar verificación en 2 pasos
3. Ir a "Contraseñas de aplicaciones"
4. Generar una contraseña para "Correo"
5. Usar esa contraseña en `email_password`

---

## Contenido del HTML del Correo

### Tabla de Resumen Incluida:

```html
<table>
  <tr>
    <th>Zona</th>
    <th>Total de Guías</th>
    <th>Porcentaje</th>
  </tr>
  <tr>
    <td>RURAL</td>
    <td>563</td>
    <td>51.7%</td>
  </tr>
  <tr>
    <td>GAM</td>
    <td>446</td>
    <td>41.0%</td>
  </tr>
  ...
</table>
```

### Descripción de Archivos Adjuntos:

```html
<h2>Archivos Adjuntos</h2>
<ul>
  <li><strong>Dashboard Regional</strong>: Vista completa por regiones (RURAL, GAM, CT01, CT02)
    <ul>
      <li>KPIs por región con valores</li>
      <li>Tabla detallada zona x hora</li>
      <li>Tabla resumen por región</li>
      <li>Gráfico de tendencias</li>
    </ul>
  </li>
  <li><strong>Gráficos por Zona Agrupada</strong>: Tendencias horarias</li>
  <li><strong>Archivo Excel</strong>: Datos procesados completos</li>
</ul>
```

### Guía para Leer el Dashboard:

```html
<h2>Cómo leer el Dashboard Regional</h2>
<p>
  <strong>KPIs Superiores:</strong> Muestran el total de guías por región.<br>
  <strong>Tabla Detallada:</strong> Cada celda muestra la cantidad de guías por zona en cada hora.<br>
  <strong>Tabla Resumen:</strong> Suma de todas las zonas de cada región por hora.<br>
  <strong>Gráfico de Tendencias:</strong> Visualiza el comportamiento de cada región a lo largo del día.
</p>
```

---

## Verificación del Envío

### Código que Adjunta el Dashboard:

En `generar_reporte_graficos.py` (líneas 398-418):

```python
# Buscar dashboard regional si existe
dashboard_regional = list(xlsx_path.parent.glob("dashboard_regional_*.png"))
if dashboard_regional:
    # Agregar el más reciente a la lista de gráficos
    dashboard_path = max(dashboard_regional, key=lambda p: p.stat().st_mtime)
    rutas_graficos.append(dashboard_path)
    print(f"OK: Dashboard regional encontrado: {dashboard_path.name}")
```

### Código que Prioriza el Dashboard en el Correo:

```python
# Adjuntar gráficos (priorizar dashboard regional primero)
graficos_ordenados = []
dashboard_regional = None

for ruta_grafico in rutas_graficos:
    if 'dashboard_regional' in ruta_grafico.name:
        dashboard_regional = ruta_grafico
    else:
        graficos_ordenados.append(ruta_grafico)

# Adjuntar dashboard regional primero
if dashboard_regional and dashboard_regional.exists():
    with open(dashboard_regional, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-Disposition', 'attachment', 
                     filename=dashboard_regional.name)
        msg.attach(img)
    print(f"OK: Dashboard regional adjuntado: {dashboard_regional.name}")
```

---

## Prueba Manual

### Paso 1: Generar Dashboard

```bash
cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap\Reporte_Monitor_Guías"

# Si ya tienes el Excel procesado
python generar_dashboard_regional.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

### Paso 2: Enviar Email con Dashboard

```bash
# Esto busca automáticamente el dashboard y lo adjunta
python generar_reporte_graficos.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

### Paso 3: Sin Email (Solo Generar)

```bash
python generar_reporte_graficos.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx" --no-email
```

---

## Ejecución Automática

```bash
ejecutar_monitor_guias.bat
```

Esto hace TODO automáticamente:
1. Extrae de SAP
2. Procesa datos
3. **Genera dashboard regional**
4. Genera gráficos individuales
5. **Adjunta dashboard al correo**
6. **Envía email**

---

## Logs Durante la Ejecución

```
[INICIO] Amalgama Y_DEV_74
[CONEXION] Conectando a SAP...
[OK] SAP GUI iniciado correctamente
[OK] Login completado
[OK] Exportacion completada
[PROCESO] Procesando archivo
[OK] Archivo procesado
Generando dashboard regional por zonas...
[OK] Dashboard regional generado exitosamente
[ARCHIVO] Dashboard: dashboard_regional_20251105_143025.png
Generando reporte con gráficos...
OK: Dashboard regional encontrado: dashboard_regional_20251105_143025.png
OK: Gráficos generados: 6 archivos
OK: Dashboard regional adjuntado: dashboard_regional_20251105_143025.png
OK: Correo enviado exitosamente a: destinatario@example.com
```

---

## Destinatarios del Correo

El correo se envía a todos los destinatarios configurados en `credentials.ini`:

```ini
[EMAIL]
email_to = jefe@empresa.com, equipo@empresa.com, analisis@empresa.com
```

Puedes agregar múltiples destinatarios separados por coma.

---

## Tamaño de Archivos Adjuntos

**Estimado total por correo**:
- Dashboard regional: ~4-8 MB
- Gráficos individuales: ~1-2 MB cada uno (5 gráficos = 5-10 MB)
- Excel: ~0.5-2 MB
- **Total**: ~10-20 MB

**Nota**: La mayoría de servidores de correo permiten hasta 25 MB por email.

---

## Formato del Dashboard Adjuntado

El dashboard incluye exactamente:

### Sección 1: KPIs
```
[GAM: 446] [RURAL: 563] [VYD: 42] [SPE: 38] [Total: 1089]
```

### Sección 2: Tabla Detallada "Horas"
```
REGIÓN    ZONA   14:00  15:00  16:00  ...  23:00
GAM       ALJ      8      9      10   ...    12
GAM       CAR      5      6       8   ...     7
...
RURAL     GUA     12     15      18   ...    14
...
RURAL 3   ZTL      2      3       4   ...     3
...
CT01      SPE      4      5       6   ...     5
CT02      VYD      3      4       5   ...     4
```

### Sección 3: Tabla Resumen
```
Región   14:00  15:00  16:00  ...  23:00
GAM       34     45     67   ...    50
RURAL     60     72     85   ...    64
CT01       4      5      6   ...     5
CT02       3      4      5   ...     4
```

### Sección 4: Gráfico de Tendencias
- 4 líneas de colores (GAM, RURAL, CT01, CT02)
- Muestra evolución por hora
- Incluye caja de información con VYD, SPE y Total

---

## Verificar que el Dashboard se Adjunta

### En el log verás:

```
OK: Dashboard regional encontrado: dashboard_regional_20251105_143025.png
OK: Dashboard regional adjuntado: dashboard_regional_20251105_143025.png
OK: Correo enviado exitosamente a: destinatario@example.com
```

### El dashboard será el PRIMER archivo adjunto en el correo

Por la configuración en `generar_reporte_graficos.py`, el dashboard se adjunta primero, antes que los demás gráficos.

---

## Resumen

✅ **Dashboard se genera** automáticamente al ejecutar `ejecutar_monitor_guias.bat`  
✅ **Dashboard se busca** automáticamente en `generar_reporte_graficos.py`  
✅ **Dashboard se adjunta** como primer archivo al correo  
✅ **HTML describe** el dashboard y cómo interpretarlo  
✅ **Formato exacto** según imagen de especificación  

---

**Estado**: [OK] Completamente Configurado  
**Dashboard**: Formato "Tablero de Monitor de Guías"  
**Distribución**: Email automático con dashboard adjunto  
**Prioridad**: Dashboard es el PRIMER adjunto

