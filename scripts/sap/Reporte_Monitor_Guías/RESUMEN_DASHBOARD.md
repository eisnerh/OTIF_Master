# Resumen del Dashboard Regional - Monitor de Guías

## Estructura del Dashboard

El dashboard ha sido simplificado para enfocarse en lo más importante:

### Componentes del Dashboard

1. **Fila 1: KPIs por Región (5 tarjetas)**
   - RURAL (Verde): Cantidad total y porcentaje
   - GAM (Azul): Cantidad total y porcentaje
   - VINOS/CT02 (Púrpura): Cantidad total y porcentaje
   - HA/SPE (Naranja): Cantidad total y porcentaje
   - CT01 (Rojo): Cantidad total y porcentaje

2. **Fila 2: Total General**
   - Tarjeta grande central con el total de guías procesadas

3. **Filas 3-7: Tablas Zona x Hora (Heatmaps)**
   - **RURAL**: Tabla completa con todas las zonas rurales
   - **GAM**: Top 15 zonas con mayor volumen
   - **VINOS, HA, CT01**: Tablas individuales

4. **Fila 8: Gráfico Comparativo**
   - Barras comparativas entre todas las regiones
   - Muestra valores absolutos y porcentajes

## Formato de las Tablas

Cada tabla zona x hora muestra:

```
          06:00  07:00  08:00  09:00  10:00  ...  20:00
Zona A      15     23     45     67     89   ...     12
Zona B       8     12     34     56     78   ...      9
Zona C       3      5     12     23     34   ...      4
...
```

- **Filas**: Zonas (ordenadas por total descendente)
- **Columnas**: Horas del día
- **Celdas**: Cantidad de guías en esa zona a esa hora
- **Colores**: 
  - Amarillo claro = Bajo volumen
  - Naranja = Volumen medio
  - Rojo = Alto volumen

## Regiones y Zonas

### RURAL (Verde)
Zonas: GUA, NIC, PUN, SCA, CNL, LIM, LIB, SIS, ZTP, ZTN, ZTL

### GAM (Azul)
Zonas: Todas las que no pertenecen a otras regiones
Nota: Se muestran las top 15 zonas con mayor volumen

### VINOS (Púrpura)
Zonas: CT02

### HA (Naranja)
Zonas: SPE

### CT01 (Rojo)
Zonas: CT01

## Archivos Generados

### Al ejecutar `ejecutar_monitor_guias.bat`:

1. **Monitor_Guias.txt**
   - Archivo de texto exportado de SAP

2. **Monitor_Guias_DD-MM-YYYY_processed.xlsx**
   - Excel procesado con datos limpios

3. **graficos/**
   - `grafico_todas_zonas.png` - Tendencia combinada
   - `grafico_rural.png` - Tendencia RURAL
   - `grafico_gam.png` - Tendencia GAM
   - `grafico_vinos.png` - Tendencia VINOS (si hay datos)
   - `grafico_ha.png` - Tendencia HA (si hay datos)

4. **dashboard_regional_YYYYMMDD_HHMMSS.png** ⭐ **PRINCIPAL**
   - Dashboard completo con KPIs y tablas
   - Tamaño: ~4-8 MB
   - Resolución: 2880 x 3360 píxeles

## Envío por Correo

### Asunto del Correo
```
Dashboard Monitor de Guias - Analisis Regional - YYYY-MM-DD HH:MM
```

### Contenido HTML
- Total de guías procesadas
- Tabla resumen por zona agrupada
- Descripción de archivos adjuntos
- Guía para leer el dashboard

### Archivos Adjuntos (en orden)
1. **dashboard_regional_*.png** (primero, más importante)
2. Gráficos individuales por zona
3. Archivo Excel procesado

## Ventajas del Nuevo Dashboard

✅ **Vista ejecutiva**: Todo en una sola imagen  
✅ **Tablas detalladas**: Zona x hora con código de colores  
✅ **Fácil de leer**: Información organizada y clara  
✅ **Comparación rápida**: KPIs y gráfico comparativo  
✅ **Listo para WhatsApp/Email**: Tamaño optimizado  
✅ **Profesional**: Sin emojis, texto plano  

## Interpretación Rápida

### Cómo usar el Dashboard

1. **Ver KPIs (arriba)**: Identificar qué región tiene más guías
2. **Revisar tablas**: Ver distribución horaria por zona
3. **Identificar picos**: Celdas rojas = horas con mayor volumen
4. **Comparar regiones**: Gráfico final muestra ranking

### Ejemplo de Análisis

Si en la tabla RURAL ves:
```
          14:00  15:00  16:00
GUA         45     67     89  ← Pico en GUA a las 16:00
NIC         12     23     34
PUN          5      8     12
```

Conclusión: GUA tiene el mayor volumen y su pico es a las 16:00 horas.

## Configuración

### Cambiar Zonas por Región

Edita `generar_dashboard_regional.py`:

```python
REGIONES_CONFIG = {
    'RURAL': {
        'zonas': ['GUA', 'NIC', ...],  # Agregar/quitar zonas
        'color': '#2E7D32',
        'nombre': 'RURAL'
    },
    ...
}
```

### Cambiar Top N Zonas GAM

Línea 325:

```python
top_zonas_gam = datos_gam_tabla.groupby('Zona')['Cantidad'].sum().nlargest(15).index
# Cambiar 15 por otro número
```

### Modificar Tamaño

Línea 181:

```python
fig = plt.figure(figsize=(24, 28), dpi=120)
# figsize: (ancho, alto) en pulgadas
# dpi: 100-150 recomendado
```

## Flujo Completo

```
ejecutar_monitor_guias.bat
  ↓
amalgama_y_dev_74.py
  ↓
[Extracción SAP] → Monitor_Guias.txt
  ↓
[Procesamiento] → Monitor_Guias_processed.xlsx
  ↓
generar_dashboard_regional.py → dashboard_regional_*.png
  ↓
generar_reporte_graficos.py
  ├── Genera gráficos individuales
  ├── Busca dashboard regional
  ├── Crea HTML con resumen
  └── Envía correo con TODOS los adjuntos
```

## Requisitos

```bash
pip install pandas openpyxl matplotlib seaborn numpy
```

## Solución de Problemas

### Dashboard vacío o con pocas zonas
**Causa**: Datos insuficientes en el archivo Excel

**Solución**: Verificar que el archivo Excel tiene datos en las columnas B (zona) e I (hora)

### Tabla muy grande (muchas zonas)
**Causa**: Región GAM tiene muchas zonas

**Solución**: Ya está limitado a top 15. Si necesitas más, edita línea 325

### Colores no se ven bien
**Causa**: Paleta de colores del heatmap

**Solución**: Cambiar `cmap='YlOrRd'` a otra paleta:
- `'RdYlGn_r'` - Verde a Rojo
- `'Blues'` - Solo azules
- `'Reds'` - Solo rojos

### Error al enviar correo
**Causa**: Dashboard muy grande

**Solución**: Reducir DPI de 120 a 100 en línea 181

---

**Versión**: 2.0.0  
**Última actualización**: 2025-11-05  
**Estado**: [OK] Completado y Funcional

