# Scripts SAP Individuales

## 📋 Descripción

Esta carpeta contiene scripts Python individuales para cada transacción SAP, basados en los scripts VBA originales pero con mejoras significativas en mantenibilidad, logging y manejo de errores.

## 🚀 Características

- **Scripts independientes**: Cada transacción tiene su propio script
- **Clase base común**: Funcionalidad compartida en `base_sap_script.py`
- **Logging detallado**: Cada script genera sus propios logs
- **Manejo de errores robusto**: Validación y recuperación de errores
- **Verificación automática**: Validación de archivos generados
- **Flexibilidad**: Soporte para fechas y rutas personalizadas

## 📁 Estructura de Archivos

```
scripts_individuales/
├── base_sap_script.py          # Clase base común
├── rep_plr.py                  # Script para REP_PLR
├── y_dev_45.py                 # Script para Y_DEV_45
├── y_dev_74.py                 # Script para Y_DEV_74
├── y_dev_82.py                 # Script para Y_DEV_82
├── zhbo.py                     # Script para ZHBO
├── zred.py                     # Script para ZRED
├── z_devo_alv.py               # Script para Z_DEVO_ALV
├── zsd_incidencias.py          # Script para ZSD_INCIDENCIAS (corregido)
├── ejecutar_todos.py           # Script maestro que ejecuta todos
├── procesar_datos_sap.py       # Procesador de DataFrames para Power BI
├── procesar_todos_los_datos.py # Procesa todos los archivos de la carpeta data
├── analizar_estructura_datos.py # Analiza estructura de archivos existentes
└── README.md                   # Esta documentación
```

## 🔧 Scripts Disponibles

### 1. REP_PLR (Reporte de Planeamiento)
- **Archivo**: `rep_plr.py`
- **Transacción**: `zsd_rep_planeamiento`
- **Salida**: `REP_PLR.xls`
- **Características**: Requiere fecha, nodo F00120, fila 11

### 2. Y_DEV_45 (Devoluciones 45)
- **Archivo**: `y_dev_45.py`
- **Transacción**: `y_dev_42000045`
- **Salida**: `y_dev_45.xls`
- **Características**: Nodo F00139, fila 2

### 3. Y_DEV_74 (Devoluciones 74)
- **Archivo**: `y_dev_74.py`
- **Transacción**: `y_dev_42000074`
- **Salida**: `y_dev_74.xls`
- **Características**: Nodo F00139, fila 2

### 4. Y_DEV_82 (Devoluciones 82)
- **Archivo**: `y_dev_82.py`
- **Transacción**: `y_dev_42000082`
- **Salida**: `y_dev_82.xls`
- **Características**: Nodo F00139, fila 2

### 5. ZHBO (Reporte HBO)
- **Archivo**: `zhbo.py`
- **Transacción**: `zhbo`
- **Salida**: `zhbo.xls`
- **Características**: Requiere fecha, fila 11

### 6. ZRED (Reporte de Red)
- **Archivo**: `zred.py`
- **Transacción**: `zred`
- **Salida**: `zred.xls`
- **Características**: Fila 1

### 7. Z_DEVO_ALV (Devoluciones ALV)
- **Archivo**: `z_devo_alv.py`
- **Transacción**: `zsd_devo_alv`
- **Salida**: `z_devo_alv.xls`
- **Características**: Fila 1

### 8. ZSD_INCIDENCIAS (Incidencias - Corregido)
- **Archivo**: `zsd_incidencias.py`
- **Transacción**: `zsd_incidencias`
- **Salida**: `data_incidencias.xls`
- **Características**: Fila 12, selección especial de grilla

## 📊 Procesamiento de Datos

### Scripts de Procesamiento de DataFrames

#### `procesar_datos_sap.py`
Procesa archivos SAP individuales y corrige la estructura de DataFrames:

```bash
# Procesar archivo individual
python procesar_datos_sap.py REP_PLR.xls REP_PLR_PowerBI C:\data

# Procesar con nombre automático
python procesar_datos_sap.py y_dev_45.xls
```

#### `procesar_todos_los_datos.py`
Procesa todos los archivos de la carpeta data:

```bash
# Procesar todos los archivos
python procesar_todos_los_datos.py
```

#### `analizar_estructura_datos.py`
Analiza la estructura de archivos existentes:

```bash
# Analizar estructura de archivos
python analizar_estructura_datos.py
```

### Características del Procesamiento

- **Corrección automática** de estructura de DataFrames
- **Múltiples codificaciones** (UTF-8, Latin-1, UTF-16, etc.)
- **Limpieza de datos** (eliminación de caracteres nulos, espacios)
- **Conversión de tipos** (fechas, números, texto)
- **Columnas calculadas** para Power BI
- **Múltiples formatos** de salida (Excel, CSV, Parquet, JSON)

### Formatos de Salida

Cada archivo procesado genera:

- **`.xlsx`** - Excel con formato para revisión
- **`.csv`** - CSV para importación
- **`.parquet`** - ⭐ **RECOMENDADO** para Power BI
- **`_metadata.json`** - Metadatos y documentación

## 📅 Fechas Dinámicas

### Lógica Automática de Fechas

El sistema implementa fechas dinámicas automáticas según el día de la semana:

- **Lunes** → Ejecuta reporte del **sábado** (2 días atrás)
- **Martes a Domingo** → Ejecuta reporte de **ayer** (1 día atrás)

### Demostración de Fechas

```bash
# Ver cómo funcionan las fechas dinámicas
python demo_fechas_dinamicas.py
```

### Uso de Fechas

```bash
# Fecha dinámica automática (RECOMENDADO)
python rep_plr.py

# Fecha personalizada específica
python rep_plr.py "15.01.2025"

# Todos los scripts con fecha dinámica
python ejecutar_todos.py
```

## 🚀 Uso

### Ejecutar Script Individual

```bash
# Script básico
python rep_plr.py

# Con fecha personalizada (para scripts que la requieren)
python rep_plr.py "15.01.2025"

# Con ruta personalizada
python rep_plr.py "15.01.2025" "C:\\mi_ruta"

# Script sin fecha
python y_dev_45.py "C:\\mi_ruta"
```

### Ejecutar Todos los Scripts

```bash
# Ejecutar todos los scripts con fecha dinámica automática (RECOMENDADO)
python ejecutar_todos.py

# Con fecha dinámica explícita
python ejecutar_todos.py dynamic

# Con fecha personalizada
python ejecutar_todos.py "15.01.2025"

# Con ruta personalizada
python ejecutar_todos.py "15.01.2025" "C:\\mi_ruta"
```

## 🔧 Clase Base (BaseSAPScript)

### Métodos Principales

#### `connect_sap()`
Establece conexión con SAP GUI

#### `navigate_to_transaction(transaction_code)`
Navega a una transacción SAP específica

#### `select_node(node_id)`
Selecciona un nodo en la interfaz

#### `select_row(row_number)`
Selecciona una fila en la lista

#### `set_date_field(field_name, date_value)`
Establece un campo de fecha

#### `execute_report()`
Ejecuta el reporte

#### `export_to_excel(filename)`
Exporta el reporte a Excel

#### `verify_output_file(filename)`
Verifica que el archivo se haya generado

## 📝 Logging

Cada script genera logs detallados:

```
2025-01-15 10:30:15 - INFO - 🔐 Conectando a SAP GUI...
2025-01-15 10:30:16 - INFO - ✅ Conexión SAP establecida correctamente
2025-01-15 10:30:17 - INFO - 📊 Navegando a transacción: zsd_rep_planeamiento
2025-01-15 10:30:25 - INFO - ✅ Archivo exportado: REP_PLR.xls
```

## 🚨 Manejo de Errores

Cada script incluye:

- **Validación de conexión SAP**
- **Verificación de navegación**
- **Manejo de errores en cada paso**
- **Verificación de archivos generados**
- **Limpieza automática de recursos**

## 📊 Ventajas vs Scripts VBA

### ✅ Mejoras Implementadas

- **Mantenibilidad**: Código más limpio y organizado
- **Reutilización**: Clase base común
- **Logging**: Seguimiento detallado de operaciones
- **Manejo de errores**: Recuperación automática
- **Flexibilidad**: Parámetros configurables
- **Verificación**: Validación automática de resultados

### 🔄 Migración Gradual

1. **Fase 1**: Scripts Python creados ✅
2. **Fase 2**: Pruebas en desarrollo 🔄
3. **Fase 3**: Despliegue en producción 📋

## 📞 Soporte

Para soporte técnico:

1. Revisar logs del script específico
2. Verificar configuración de SAP GUI
3. Comprobar permisos de archivos
4. Consultar documentación de la clase base

## 🔄 Actualizaciones

### Versión 1.0
- ✅ Scripts individuales creados
- ✅ Clase base implementada
- ✅ Logging completo
- ✅ Manejo de errores robusto
- ✅ Script maestro para ejecución masiva

## 📄 Licencia

Este proyecto está bajo la licencia del sistema OTIF Master.
