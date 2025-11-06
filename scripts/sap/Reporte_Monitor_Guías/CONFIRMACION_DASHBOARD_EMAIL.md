# Confirmación - Dashboard Regional se Adjunta al Correo

## [OK] Dashboard Configurado para Adjuntarse Automáticamente

---

## Flujo Completo Verificado

### 1. Generación del Dashboard (amalgama_y_dev_74.py)

```python
# Líneas 303-332
logger.info("Generando dashboard regional por zonas...")
script_dashboard = Path(__file__).parent / "generar_dashboard_regional.py"
result = subprocess.run([sys.executable, str(script_dashboard), "--archivo", str(xlsx_path)])

if result.returncode == 0:
    logger.info("[OK] Dashboard regional generado exitosamente")
    time.sleep(2)  # ESPERA 2 SEGUNDOS
    dashboard_png = list(xlsx_path.parent.glob("dashboard_regional_*.png"))
    if dashboard_png:
        dashboard_mas_reciente = max(dashboard_png, key=lambda p: p.stat().st_mtime)
        logger.info(f"[ARCHIVO] Dashboard: {dashboard_mas_reciente.name}")
        logger.info(f"[INFO] Tamaño: {dashboard_mas_reciente.stat().st_size / 1024:.1f} KB")
```

**Resultado**: 
- ✅ Dashboard se genera
- ✅ Se espera 2 segundos para que se complete
- ✅ Se verifica que existe
- ✅ Se muestra información en logs

---

### 2. Búsqueda del Dashboard (generar_reporte_graficos.py)

```python
# Líneas 417-444
print("Esperando dashboard regional...")
max_intentos = 10
dashboard_path = None

for intento in range(max_intentos):
    time.sleep(1)  # Esperar 1 segundo entre intentos
    dashboard_regional = list(xlsx_path.parent.glob("dashboard_regional_*.png"))
    if dashboard_regional:
        ahora = time.time()
        dashboards_recientes = [
            d for d in dashboard_regional 
            if (ahora - d.stat().st_mtime) < 300  # Últimos 5 minutos
        ]
        if dashboards_recientes:
            dashboard_path = max(dashboards_recientes, key=lambda p: p.stat().st_mtime)
            print(f"OK: Dashboard regional encontrado: {dashboard_path.name}")
            print(f"    Tamaño: {dashboard_path.stat().st_size / 1024:.1f} KB")
            print(f"    Generado hace: {int(ahora - dashboard_path.stat().st_mtime)} segundos")
            break

if dashboard_path:
    rutas_graficos.insert(0, dashboard_path)  # INSERTAR AL INICIO
else:
    print("ADVERTENCIA: No se encontró dashboard regional reciente...")
```

**Resultado**:
- ✅ Busca dashboard hasta 10 segundos
- ✅ Filtra solo dashboards recientes (últimos 5 minutos)
- ✅ Obtiene el MÁS RECIENTE
- ✅ **Lo inserta en POSICIÓN 0** (primer adjunto)

---

### 3. Adjuntar al Correo (generar_reporte_graficos.py)

```python
# Líneas 338-357
# Adjuntar gráficos
total_adjuntos = 0
for i, ruta_grafico in enumerate(rutas_graficos):
    if ruta_grafico.exists():
        with open(ruta_grafico, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-Disposition', 'attachment', 
                         filename=ruta_grafico.name)
            msg.attach(img)
        
        # Log especial para dashboard
        if 'dashboard_regional' in ruta_grafico.name:
            print(f"OK: [DASHBOARD] {ruta_grafico.name} adjuntado (posicion {i+1}, tamaño: {ruta_grafico.stat().st_size / 1024:.1f} KB)")
        else:
            print(f"OK: Grafico adjuntado: {ruta_grafico.name}")
        
        total_adjuntos += 1

print(f"OK: Total de imagenes adjuntadas: {total_adjuntos}")
```

**Resultado**:
- ✅ Dashboard se adjunta PRIMERO (posición 1)
- ✅ Log especial indica que es el DASHBOARD
- ✅ Muestra posición y tamaño
- ✅ Cuenta total de adjuntos

---

## Logs Durante la Ejecución

### Lo que verás en la consola:

```
===============================================================
INICIO | Amalgama Y_DEV_74
===============================================================
...
Generando dashboard regional por zonas...
[OK] Dashboard regional generado exitosamente
[ARCHIVO] Dashboard: dashboard_regional_20251105_152030.png
[INFO] Tamaño: 4235.8 KB
...
Generando reporte con gráficos...
OK: Gráficos generados: 4 archivos
Esperando dashboard regional...
OK: Dashboard regional encontrado: dashboard_regional_20251105_152030.png
    Tamaño: 4235.8 KB
    Generado hace: 5 segundos
OK: Conteo realizado para 47 combinaciones zona/hora
...
OK: [DASHBOARD] dashboard_regional_20251105_152030.png adjuntado (posicion 1, tamaño: 4235.8 KB)
OK: Grafico adjuntado: grafico_rural.png
OK: Grafico adjuntado: grafico_gam.png
OK: Grafico adjuntado: grafico_ct01.png
OK: Grafico adjuntado: grafico_ct02.png
OK: Total de imagenes adjuntadas: 5
OK: Correo enviado exitosamente a: destinatario@example.com
```

---

## Orden de Archivos Adjuntos en el Correo

### Email recibido contendrá (en este orden):

1. **dashboard_regional_20251105_152030.png** ⭐ **PRIMERO**
   - Tablero completo de Monitor de Guías
   - KPIs + Tabla detallada + Tabla resumen + Gráfico tendencias
   - ~4-8 MB

2. **grafico_rural.png**
   - Tendencia RURAL por hora
   - ~200-400 KB

3. **grafico_gam.png**
   - Tendencia GAM por hora
   - ~200-400 KB

4. **grafico_ct01.png** (si hay datos)
   - Tendencia CT01 por hora
   - ~150-300 KB

5. **grafico_ct02.png** (si hay datos)
   - Tendencia CT02 por hora
   - ~150-300 KB

6. **Monitor_Guias_DD-MM-YYYY_processed.xlsx**
   - Excel con datos completos
   - ~100-500 KB

**Total estimado**: 5-10 MB por correo

---

## Cómo Verificar que el Dashboard se Adjunta

### Opción 1: Ver Logs

Ejecuta:
```bash
ejecutar_monitor_guias.bat
```

Busca en los logs:
```
OK: [DASHBOARD] dashboard_regional_*.png adjuntado (posicion 1, tamaño: #### KB)
```

Si ves este mensaje, el dashboard **SÍ se adjuntó**.

### Opción 2: Revisar el Correo

El correo tendrá:
- **Asunto**: Dashboard Monitor de Guias - Analisis Regional - YYYY-MM-DD HH:MM
- **Primer adjunto**: dashboard_regional_YYYYMMDD_HHMMSS.png

### Opción 3: Prueba Manual

```bash
cd "Reporte_Monitor_Guías"

# Genera dashboard
python generar_dashboard_regional.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"

# Espera 3 segundos
timeout /t 3

# Envía email (buscará y adjuntará el dashboard)
python generar_reporte_graficos.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

---

## Sistema de Búsqueda del Dashboard

El sistema busca el dashboard de forma inteligente:

1. **Espera hasta 10 segundos** (1 segundo por intento, 10 intentos)
2. **Busca archivos**: `dashboard_regional_*.png`
3. **Filtra por tiempo**: Solo últimos 5 minutos
4. **Selecciona**: El MÁS RECIENTE
5. **Inserta**: En posición 0 (primer adjunto)
6. **Verifica**: Que el archivo existe antes de adjuntar

---

## Confirmación Visual en el Correo

### HTML del Correo Incluye:

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
  <li><strong>Gráficos por Zona Agrupada</strong>: Tendencias horarias (RURAL, GAM, CT01, CT02)</li>
  <li><strong>Archivo Excel</strong>: Datos procesados completos</li>
</ul>

<h2>Cómo leer el Dashboard Regional</h2>
<p>
  <strong>KPIs Superiores:</strong> Muestran el total de guías por región.<br>
  <strong>Tabla Detallada:</strong> Cada celda muestra la cantidad de guías por zona en cada hora.<br>
  <strong>Tabla Resumen:</strong> Suma de todas las zonas de cada región por hora.<br>
  <strong>Gráfico de Tendencias:</strong> Visualiza el comportamiento de cada región.
</p>
```

---

## Prueba Rápida

Para verificar que todo funciona:

```bash
cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap\Reporte_Monitor_Guías"

# 1. Asegúrate de tener credentials.ini configurado
# 2. Ejecuta
ejecutar_monitor_guias.bat

# 3. Revisa los logs, deberías ver:
#    [DASHBOARD] dashboard_regional_*.png adjuntado (posicion 1, ...)

# 4. Revisa tu correo
#    El primer adjunto debe ser el dashboard
```

---

## Resumen

### El Dashboard SE ADJUNTA Automáticamente ✅

**Cuándo**: Al ejecutar `ejecutar_monitor_guias.bat`

**Dónde**: Como PRIMER archivo adjunto en el correo

**Qué incluye el dashboard**:
- KPIs: GAM, RURAL, VYD, SPE, Total
- Tabla detallada: 22 zonas × horas (14:00-23:00)
- Tabla resumen: 4 regiones × horas
- Gráfico: Tendencias por región

**Cómo verificar**: 
- Ver logs: `[DASHBOARD] dashboard_regional_*.png adjuntado`
- Revisar correo: Primer adjunto es el dashboard

---

**Estado**: [OK] Confirmado - Dashboard se adjunta automáticamente  
**Posición**: Primer adjunto (más importante)  
**Formato**: PNG, ~4-8 MB  
**Contenido**: Tablero completo de Monitor de Guías

