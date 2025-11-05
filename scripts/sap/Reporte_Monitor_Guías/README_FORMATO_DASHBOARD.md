# Formato del Dashboard - Tablero de Monitor de Guías

## Estructura del Dashboard

El dashboard sigue el formato exacto mostrado en la especificación, con 4 secciones principales:

### 1. KPIs Superiores (Fila 1)

Cinco cajas de colores con:
- **GAM** (Azul): Total de guías en GAM
- **RURAL** (Verde): Total de guías en RURAL
- **VYD** (Púrpura): Total de guías en CT02 (mostrado como VYD)
- **SPE** (Naranja): Total de guías en CT01 (mostrado como SPE)
- **Total** (Gris oscuro): Total general de guías

### 2. Tabla Detallada "Horas" (Fila 2)

**Columnas**:
- REGIÓN: Nombre de la región
- ZONA: Código de zona
- 14:00, 15:00, 16:00, ... 23:00: Cantidad de guías por hora

**Filas** (agrupadas por región):
- **GAM**: ALJ, CAR, CMN, CMT, COG, SJE, SJO, SUP, ZTO
- **RURAL**: CNL, GUA, LIB, LIM, NIC, PUN, SCA, SIS
- **RURAL 3**: ZTL, ZTN, ZTP
- **CT01**: SPE
- **CT02**: VYD

**Características**:
- Encabezados en verde (#4CAF50)
- Columna REGIÓN con fondo verde claro
- Columna ZONA con fondo verde muy claro
- Filas alternas en gris claro
- Valores numéricos centrados

### 3. Tabla Resumen por Región (Fila 3)

**Columnas**:
- Región: GAM, RURAL, CT01, CT02
- 14:00, 15:00, 16:00, ... hasta 00:00 (todas las horas)

**Características**:
- Encabezados en azul (#2196F3)
- Suma de todas las zonas de cada región por hora
- Valores totalizados

### 4. Gráfico de Tendencias (Fila 4)

**Título**: "Tendencias por Región"

**Líneas**:
- GAM (Azul)
- RURAL (Naranja/Verde)
- CT01 (Verde)
- CT02 (Cyan/Púrpura)

**Características**:
- Eje X: Horas (14:00 - 00:00)
- Eje Y: Cantidad de guías
- Marcadores en cada punto
- Grid de fondo
- Leyenda en esquina superior izquierda
- Caja de información con VYD, SPE y Total

## Detalles de Implementación

### Separación de RURAL y RURAL 3

Las zonas rurales se dividen en dos grupos en la tabla:

**RURAL**:
- CNL, GUA, LIB, LIM, NIC, PUN, SCA, SIS

**RURAL 3**:
- ZTL, ZTN, ZTP

Pero en los KPIs y gráficos se tratan como una sola región RURAL.

### Mapeo de Nombres

En los KPIs se muestran:
- VYD (en lugar de CT02)
- SPE (en lugar de CT01)

Pero en las tablas se muestra el nombre de región (CT01, CT02).

### Orden de las Zonas

Las zonas aparecen en el orden de la configuración dentro de cada región.

## Dimensiones

- **Ancho**: 20 pulgadas (2400 píxeles @ 120 DPI)
- **Alto**: 24 pulgadas (2880 píxeles @ 120 DPI)
- **Formato**: PNG
- **Tamaño**: ~4-8 MB
- **Fondo**: Blanco
- **Resolución**: 150 DPI

## Colores Usados

```
KPIs:
- GAM:   #1565C0 (Azul)
- RURAL: #2E7D32 (Verde)
- VYD:   #6A1B9A (Púrpura)
- SPE:   #F57C00 (Naranja)
- Total: #424242 (Gris oscuro)

Tablas:
- Encabezados tabla detallada: #4CAF50 (Verde)
- Encabezados tabla resumen: #2196F3 (Azul)
- Columna Región: #E8F5E9 (Verde muy claro)
- Columna Zona: #F1F8E9 (Verde ultraclaro)
- Filas alternas: #FAFAFA (Gris muy claro)

Gráfico:
- GAM: #1565C0 (Azul)
- RURAL: #2E7D32 (Verde)
- CT01: #F57C00 (Naranja)
- CT02: #6A1B9A (Púrpura)
```

## Uso

### Generación Automática

```bash
cd "Reporte_Monitor_Guías"
ejecutar_monitor_guias.bat
```

El dashboard se genera automáticamente y se adjunta al correo.

### Generación Manual

```bash
python generar_dashboard_regional.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

### Con Ruta Personalizada

```bash
python generar_dashboard_regional.py --archivo "archivo.xlsx" --output "C:\reportes\mi_dashboard.png"
```

## Interpretación

### Tabla Detallada
- Cada fila = Una zona específica
- Cada columna (hora) = Cantidad de guías en esa hora
- Permite ver el detalle exacto por zona y hora

### Tabla Resumen
- Cada fila = Una región completa
- Valores = Suma de todas las zonas de esa región
- Permite ver totales regionales por hora

### Gráfico de Tendencias
- Visualiza la tabla resumen
- Permite identificar picos horarios
- Permite comparar comportamiento entre regiones
- Muestra evolución temporal

## Ejemplo de Análisis

Si en el dashboard ves:

**Tabla Detallada**:
```
REGIÓN  ZONA  14:00  15:00  16:00
GAM     SJO    15     23     35   ← Pico de SJO en 16:00
GAM     CAR     8     12     18
```

**Tabla Resumen**:
```
Región  14:00  15:00  16:00
GAM      34     45     67   ← Suma de todas las zonas GAM
```

**Gráfico**:
- Línea azul (GAM) sube de 34 a 67 entre 14:00 y 16:00

**Conclusión**: GAM tiene un incremento significativo en la tarde, principalmente debido a SJO.

---

**Versión**: 1.0.0  
**Formato**: Según especificación oficial  
**Estado**: [OK] Implementado correctamente

