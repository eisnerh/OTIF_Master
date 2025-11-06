# Sistema de 3 Imágenes - Dashboard Monitor de Guías

## Descripción

El dashboard ahora se genera en **3 imágenes separadas** para facilitar su visualización y distribución por correo.

---

## Las 3 Imágenes Generadas

### Imagen 1: Detalle por Zona
**Archivo**: `dashboard_parte1_detalle.png`  
**Tamaño**: ~2-4 MB  
**Dimensiones**: 2400 x 1920 píxeles (20" x 16" @ 120 DPI)

**Contenido**:
- ✅ KPIs superiores (GAM, RURAL, VYD, SPE, Total)
- ✅ Tabla detallada zona x hora (22 zonas × horas 14:00-23:00)

**Estructura de tabla**:
```
REGIÓN    ZONA   14:00  15:00  16:00  ...  23:00
GAM       ALJ      ##     ##     ##   ...    ##
GAM       CAR      ##     ##     ##   ...    ##
...
RURAL     CNL      ##     ##     ##   ...    ##
RURAL     GUA      ##     ##     ##   ...    ##
...
RURAL 3   ZTL      ##     ##     ##   ...    ##
...
CT01      SPE      ##     ##     ##   ...    ##
CT02      VYD      ##     ##     ##   ...    ##
```

---

### Imagen 2: Resumen por Región
**Archivo**: `dashboard_parte2_resumen.png`  
**Tamaño**: ~1-2 MB  
**Dimensiones**: 2400 x 720 píxeles (20" x 6" @ 120 DPI)

**Contenido**:
- ✅ Tabla resumen por región
- ✅ Suma de todas las zonas por región y hora

**Estructura de tabla**:
```
Región   14:00  15:00  16:00  ...  23:00
GAM       ##     ##     ##   ...    ##
RURAL     ##     ##     ##   ...    ##
CT01      ##     ##     ##   ...    ##
CT02      ##     ##     ##   ...    ##
```

---

### Imagen 3: Gráfico de Tendencias
**Archivo**: `dashboard_parte3_tendencias.png`  
**Tamaño**: ~800 KB - 1.5 MB  
**Dimensiones**: 1920 x 1200 píxeles (16" x 10" @ 120 DPI)

**Contenido**:
- ✅ Gráfico de líneas comparativo
- ✅ 4 líneas de colores (GAM, RURAL, CT01, CT02)
- ✅ Eje X: Horas (14:00 - 23:00)
- ✅ Eje Y: Cantidad de guías
- ✅ Leyenda con regiones
- ✅ Caja de información (VYD, SPE, Total)

---

## Flujo de Generación

```
1. ejecutar_monitor_guias.bat
   ↓
2. amalgama_y_dev_74.py
   ├── Extrae de SAP
   ├── Procesa Excel
   ↓
3. generar_dashboard_regional.py
   ├── Genera 4 archivos:
   │   ├── dashboard_regional_YYYYMMDD_HHMMSS.png (completo)
   │   ├── dashboard_parte1_detalle.png (KPIs + Tabla)
   │   ├── dashboard_parte2_resumen.png (Resumen)
   │   └── dashboard_parte3_tendencias.png (Gráfico)
   ↓
4. [ESPERA 10 SEGUNDOS]
   ↓
5. generar_reporte_graficos.py
   ├── Busca las 3 imágenes (dashboard_parte*.png)
   ├── Crea HTML con resumen
   └── Envía correo con:
       ├── Imagen 1: Detalle
       ├── Imagen 2: Resumen
       ├── Imagen 3: Tendencias
       └── Excel procesado
```

---

## Archivos Adjuntos al Correo

### En el correo recibirás (en orden):

1. **dashboard_parte1_detalle.png**
   - KPIs + Tabla detallada 22 zonas

2. **dashboard_parte2_resumen.png**
   - Tabla resumen 4 regiones

3. **dashboard_parte3_tendencias.png**
   - Gráfico de líneas

4. **Monitor_Guias_DD-MM-YYYY_processed.xlsx**
   - Datos completos

**Total**: 4 archivos (~4-8 MB total)

---

## Nombres de Archivos Fijos

Las 3 imágenes usan nombres fijos que se **SOBREESCRIBEN** en cada ejecución:

- `dashboard_parte1_detalle.png` (siempre mismo nombre)
- `dashboard_parte2_resumen.png` (siempre mismo nombre)
- `dashboard_parte3_tendencias.png` (siempre mismo nombre)

**Ventaja**: No se acumulan archivos antiguos.

---

## Espera de 10 Segundos

El sistema espera 10 segundos antes de buscar las imágenes para asegurar que:
- ✅ Todas las imágenes estén completamente escritas
- ✅ No haya problemas de lectura de archivos
- ✅ El sistema operativo haya liberado los archivos

---

## Logs Durante la Ejecución

```
[INICIO] Generacion de Dashboard Tablero de Monitor de Guias
[OK] Datos cargados: 637 guias
[PROCESO] Generando dashboard Tablero de Monitor de Guias...
[KPI] Generando KPIs...
[TABLA] Generando tabla detallada zona x hora...
[TABLA] Generando tabla resumen por region...
[GRAFICO] Generando grafico de tendencias...
[GUARDANDO] Guardando dashboard completo en: dashboard_regional_20251105_154530.png
[OK] Dashboard completo guardado: dashboard_regional_20251105_154530.png
[PROCESO] Generando imagenes separadas...
[IMAGEN 1] KPIs + Tabla detallada...
[OK] Imagen 1 guardada: dashboard_parte1_detalle.png
[IMAGEN 2] Tabla resumen...
[OK] Imagen 2 guardada: dashboard_parte2_resumen.png
[IMAGEN 3] Grafico de tendencias...
[OK] Imagen 3 guardada: dashboard_parte3_tendencias.png
[EXITO] 3 imagenes generadas exitosamente
Archivos generados: 4
  1. dashboard_regional_20251105_154530.png (4235.8 KB)
  2. dashboard_parte1_detalle.png (2156.3 KB)
  3. dashboard_parte2_resumen.png (876.5 KB)
  4. dashboard_parte3_tendencias.png (1024.2 KB)
---
Procesando archivo: Monitor_Guias_05-11-2025_processed.xlsx
OK: Archivo leído: 637 líneas
OK: Conteo realizado para 47 combinaciones zona/hora
Esperando 10 segundos para que se generen las imagenes del dashboard...
[BUSCAR] Buscando imagenes del dashboard...
OK: Encontrado: dashboard_parte1_detalle.png (2156.3 KB)
OK: Encontrado: dashboard_parte2_resumen.png (876.5 KB)
OK: Encontrado: dashboard_parte3_tendencias.png (1024.2 KB)
OK: 3 imagenes del dashboard listas para adjuntar
---
OK: [DASHBOARD PARTE 1] dashboard_parte1_detalle.png adjuntado (2156.3 KB)
OK: [DASHBOARD PARTE 2] dashboard_parte2_resumen.png adjuntado (876.5 KB)
OK: [DASHBOARD PARTE 3] dashboard_parte3_tendencias.png adjuntado (1024.2 KB)
OK: Total de imagenes adjuntadas: 3
OK: Excel adjuntado: Monitor_Guias_05-11-2025_processed.xlsx
OK: Correo enviado exitosamente a: destinatario@example.com
```

---

## Ventajas de las 3 Imágenes

### 1. Tamaño Reducido
- **Antes**: 1 imagen de ~6-8 MB
- **Ahora**: 3 imágenes de ~1-2.5 MB cada una
- **Ventaja**: Más fácil de enviar/recibir por correo

### 2. Visualización Flexible
- Puedes ver solo la parte que te interesa
- Mejor para compartir por WhatsApp (imágenes más pequeñas)
- Más fácil de imprimir por separado

### 3. Sobreescritura Automática
- Nombres fijos siempre iguales
- No se acumulan archivos antiguos
- Fácil de encontrar

### 4. Mejor para Email
- Algunas aplicaciones de correo tienen límite por imagen
- 3 imágenes pequeñas son más confiables que 1 grande
- Mejor compatibilidad con clientes de correo

---

## Archivos en el Sistema

### Ubicación:
`C:\data\SAP_Extraction\y_dev_74\`

### Archivos generados:

**Dashboard completo** (para archivo local):
- `dashboard_regional_YYYYMMDD_HHMMSS.png` (fecha y hora en nombre)

**3 partes para correo** (nombres fijos, se sobreescriben):
- `dashboard_parte1_detalle.png`
- `dashboard_parte2_resumen.png`
- `dashboard_parte3_tendencias.png`

---

## Eliminado

❌ Ya NO se generan gráficos individuales por zona:
- ~~grafico_todas_zonas.png~~
- ~~grafico_rural.png~~
- ~~grafico_gam.png~~
- ~~grafico_ct01.png~~
- ~~grafico_ct02.png~~

✅ Ahora solo las 3 partes del dashboard

---

## Uso

### Ejecución Completa:
```bash
cd "Reporte_Monitor_Guías"
ejecutar_monitor_guias.bat
```

Esto genera:
1. 4 archivos PNG (1 completo + 3 partes)
2. Espera 10 segundos
3. Adjunta las 3 partes al correo
4. Envía el correo

### Solo Generar Dashboard:
```bash
python generar_dashboard_regional.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

### Solo Enviar Correo (si ya están las imágenes):
```bash
python generar_reporte_graficos.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

---

## Resumen

✅ **3 imágenes separadas** del dashboard  
✅ **Nombres fijos** (se sobreescriben)  
✅ **Espera de 10 segundos** antes de adjuntar  
✅ **Fuentes grandes y negritas** en todas las imágenes  
✅ **Se adjuntan automáticamente** al correo  
✅ **Sin gráficos individuales** por zona  

---

**Versión**: 3.0.0  
**Fecha**: 2025-11-05  
**Formato**: 3 imágenes PNG  
**Estado**: [OK] Listo para usar

