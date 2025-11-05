# Dashboard Regional por Zonas - Monitor de Guías

## Descripción

Este dashboard genera una visualización completa estilo Power BI con análisis regional segmentado por zonas. Incluye:

- KPIs por región (RURAL, GAM, VINOS, HA, CT01)
- Distribución de guías por zona dentro de cada región
- Tendencias horarias por región
- Comparativo general entre regiones

## Características

- [OK] **Segmentación por regiones**: RURAL, GAM, VINOS (CT02), HA (SPE), CT01
- [OK] **Análisis por zona**: Distribución detallada dentro de cada región
- [OK] **Tendencias horarias**: Gráficos de línea mostrando el comportamiento por hora
- [OK] **KPIs visuales**: Tarjetas con valores y porcentajes
- [OK] **Comparativo**: Vista general de todas las regiones
- [OK] **Alta resolución**: Imagen PNG de 20x28 pulgadas @ 120 DPI
- [OK] **Colores diferenciados**: Cada región tiene su color distintivo

## Configuración de Regiones

```python
RURAL: 
  - Zonas: GUA, NIC, PUN, SCA, CNL, LIM, LIB, SIS, ZTP, ZTN, ZTL
  - Color: Verde (#2E7D32)

GAM:
  - Zonas: Todas las que no están en otras regiones
  - Color: Azul (#1565C0)

VINOS:
  - Zonas: CT02
  - Color: Púrpura (#6A1B9A)

HA:
  - Zonas: SPE
  - Color: Naranja (#F57C00)

CT01:
  - Zonas: CT01
  - Color: Rojo (#C62828)
```

## Estructura del Dashboard

### Fila 1: KPIs Principales
- 5 tarjetas con totales y porcentajes por región
- Colores diferenciados por región
- Valores absolutos y relativos

### Fila 2: Total General
- Tarjeta central con el total de guías procesadas
- Color oscuro destacado

### Fila 3: Distribución por Zona
- **RURAL**: Gráfico de barras horizontales con todas las zonas RURAL
- **GAM**: Top 10 zonas de GAM con mayor volumen

### Fila 4: Tendencia RURAL
- Gráfico de línea con tendencia horaria
- Valores en cada punto
- Área sombreada bajo la curva

### Fila 5: Tendencia GAM
- Gráfico de línea con tendencia horaria
- Valores en cada punto
- Área sombreada bajo la curva

### Fila 6: Otras Regiones
- 3 gráficos de barras para VINOS, HA y CT01
- Distribución por zona (si aplica)

### Fila 7: Comparativo General
- Gráfico de barras con todas las regiones
- Valores absolutos y porcentajes
- Colores diferenciados

## Uso

### Opción 1: Ejecución Automática

El dashboard se genera automáticamente cuando ejecutas el script principal:

```bash
ejecutar_monitor_guias.bat
```

Esto genera:
1. Monitor_Guias.txt (exportación SAP)
2. Monitor_Guias_DD-MM-YYYY_processed.xlsx (Excel procesado)
3. Gráficos individuales por zona
4. **dashboard_regional_YYYYMMDD_HHMMSS.png** (Dashboard completo)

### Opción 2: Generación Manual

Si ya tienes el archivo Excel procesado:

```bash
python generar_dashboard_regional.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

### Opción 3: Con ruta de salida personalizada

```bash
python generar_dashboard_regional.py --archivo "archivo.xlsx" --output "C:\reportes\dashboard.png"
```

## Archivo Generado

**Ubicación**: `C:\data\SAP_Extraction\y_dev_74\`

**Nombre**: `dashboard_regional_YYYYMMDD_HHMMSS.png`

**Características**:
- Tamaño: ~3-6 MB
- Resolución: 3000 x 4200 píxeles (20x28" @ 120 DPI)
- Formato: PNG (mejor calidad para gráficos)
- Fondo: Gris claro (#f5f5f5)

## Ejemplos de Uso

### Ver datos de una región específica

El dashboard muestra automáticamente todas las regiones. Para análisis detallado:

- **RURAL**: Ver distribución de guías en zonas rurales (columna izquierda, fila 3)
- **GAM**: Ver top 10 zonas con mayor volumen (columna derecha, fila 3)
- **Tendencias**: Ver comportamiento por hora en filas 4 y 5

### Identificar picos horarios

Las tendencias horarias (filas 4 y 5) muestran:
- Horas con mayor volumen de guías
- Patrones de distribución durante el día
- Comparación entre RURAL y GAM

### Comparar regiones

El gráfico comparativo final (fila 7) permite:
- Ver qué región tiene mayor volumen
- Comparar porcentajes de participación
- Identificar desbalances entre regiones

## Interpretación del Dashboard

### KPIs (Fila 1)
- **Valor superior**: Nombre de la región
- **Valor central**: Cantidad total de guías
- **Valor inferior**: Porcentaje del total

### Gráficos de Barras
- **Altura/longitud**: Cantidad de guías
- **Etiquetas**: Valores numéricos exactos
- **Color**: Identificación de región

### Gráficos de Tendencia
- **Línea**: Tendencia temporal
- **Puntos**: Valores por hora
- **Área sombreada**: Volumen relativo
- **Etiquetas**: Valores exactos en cada hora

## Personalización

### Cambiar Colores

Edita `generar_dashboard_regional.py` (líneas 28-58):

```python
REGIONES_CONFIG = {
    'RURAL': {
        'color': '#2E7D32',  # Cambiar color RURAL
        ...
    },
    ...
}
```

### Modificar Zonas por Región

Edita las listas de zonas en `REGIONES_CONFIG`:

```python
'RURAL': {
    'zonas': ['GUA', 'NIC', 'PUN', ...],  # Agregar/quitar zonas
    ...
}
```

### Cambiar Tamaño de Imagen

Edita línea 247:

```python
fig = plt.figure(figsize=(20, 28), dpi=120)
# figsize: (ancho, alto) en pulgadas
# dpi: resolución (120-150 recomendado)
```

### Top N Zonas GAM

Para cambiar cuántas zonas GAM mostrar, edita línea 267:

```python
datos_gam = stats_por_zona[stats_por_zona['Region'] == 'GAM'].sort_values('Cantidad', ascending=False).head(10)
# Cambiar .head(10) a .head(15) para mostrar 15 zonas
```

## Comparación con Otros Reportes

| Característica | Gráficos Individuales | Dashboard Regional |
|----------------|----------------------|-------------------|
| Segmentación | Por zona agrupada | Por región y zona |
| Visualización | Múltiples PNGs | Un solo PNG |
| Tendencias | Por zona agrupada | Por región |
| KPIs | No | Sí |
| Comparativo | No | Sí |
| Ideal para | Análisis detallado | Vista ejecutiva |

## Integración con Otros Sistemas

### WhatsApp
```bash
# Compartir dashboard por WhatsApp
python enviar_whatsapp.py --imagen "dashboard_regional_20251105_140530.png" --numeros "+50612345678"
```

### Email
El dashboard se puede adjuntar automáticamente al correo generado por `generar_reporte_graficos.py`.

### Power BI / Tableau
La imagen puede importarse como fondo o referencia visual.

## Requisitos

```bash
pip install pandas openpyxl matplotlib seaborn numpy
```

## Archivos del Sistema

```
Reporte_Monitor_Guías/
├── amalgama_y_dev_74.py               # Script principal
├── y_dev_74.py                        # Módulo de extracción SAP
├── generar_reporte_graficos.py        # Gráficos individuales + email
├── generar_dashboard_regional.py      # Dashboard regional (NUEVO)
├── ejecutar_monitor_guias.bat         # Ejecutor
└── README_DASHBOARD_REGIONAL.md       # Esta documentación
```

## Flujo de Ejecución

```
1. ejecutar_monitor_guias.bat
   ↓
2. amalgama_y_dev_74.py
   ↓
3. Extracción de SAP (y_dev_74.py)
   ↓
4. Procesamiento Excel
   ↓
5. generar_reporte_graficos.py
   ├── Gráficos individuales
   └── Envío por email
   ↓
6. generar_dashboard_regional.py (NUEVO)
   └── Dashboard completo
   ↓
7. Archivos generados:
   ├── Monitor_Guias.txt
   ├── Monitor_Guias_DD-MM-YYYY_processed.xlsx
   ├── graficos/
   │   ├── grafico_todas_zonas.png
   │   ├── grafico_rural.png
   │   ├── grafico_gam.png
   │   ├── grafico_vinos.png
   │   └── grafico_ha.png
   └── dashboard_regional_YYYYMMDD_HHMMSS.png
```

## Solución de Problemas

### Dashboard vacío o con errores

**Causa**: Datos insuficientes o formato incorrecto

**Solución**:
```bash
# Verificar que el Excel tiene datos
python generar_dashboard_regional.py --archivo "archivo.xlsx"
# Revisar mensajes de error en consola
```

### Zonas no aparecen en la región correcta

**Causa**: Configuración de zonas incorrecta

**Solución**: Editar `REGIONES_CONFIG` en `generar_dashboard_regional.py`

### Imagen muy grande

**Causa**: DPI muy alto

**Solución**: Reducir DPI de 120 a 100 en línea 247

### Gráficos no se ven bien

**Causa**: Muchas zonas o datos muy dispersos

**Solución**: Ajustar tamaños de fuente o limitar número de zonas mostradas

## Mejores Prácticas

1. **Ejecutar diariamente**: Para tener histórico de dashboards
2. **Nombrar con fecha**: El script ya lo hace automáticamente
3. **Compartir por WhatsApp**: Ideal para comunicación rápida
4. **Guardar histórico**: Crear carpeta de archivo por mes
5. **Revisar tendencias**: Comparar dashboards de diferentes días

## Próximas Mejoras

- [ ] Histórico de comparación (día anterior vs actual)
- [ ] Alertas automáticas si una región baja significativamente
- [ ] Versión interactiva HTML
- [ ] Exportación a PDF
- [ ] Integración con base de datos para análisis temporal

---

**Versión**: 1.0.0  
**Fecha**: 2025-11-05  
**Autor**: Equipo OTIF Master  
**Estado**: [OK] Funcional y Listo para Usar

