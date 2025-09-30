# Scripts SAP - Procesamiento de Reportes

## 📁 Estructura de Archivos

### Scripts Principales
- **`script_maestro_nuevo.py`** ⭐ **SCRIPT PRINCIPAL** - Ejecuta todo el flujo completo
- **`loguearse_simple.py`** - Script de login en SAP (sin emojis)
- **`nuevo_rep_plr.py`** - Descarga reporte desde SAP
- **`procesar_sap_simple.py`** - Procesa archivo SAP para Power BI

### Carpeta de Datos
- **`data/`** - Contiene archivos de entrada y salida
  - `REP_PLR_HOY.xls` - Archivo original de SAP
  - `REP_PLR_HOY_PowerBI.*` - Archivos procesados para Power BI

## 🚀 Uso Recomendado

### Para ejecutar todo el flujo completo:
```bash
python script_maestro_nuevo.py
```

### Para procesar solo archivos existentes:
```bash
python procesar_sap_simple.py
```

## 📊 Archivos Generados

Los archivos Power BI se generan en: `C:\Data\Nite\`

- **`REP_PLR_HOY_PowerBI.xlsx`** - Excel con formato
- **`REP_PLR_HOY_PowerBI.csv`** - CSV para importar
- **`REP_PLR_HOY_PowerBI.parquet`** - ⭐ **RECOMENDADO para Power BI**
- **`REP_PLR_HOY_Metadata.json`** - Metadatos y documentación

## 🔧 Funcionalidades

### script_maestro.py
- ✅ Login automático en SAP
- ✅ Descarga de reporte desde SAP
- ✅ Procesamiento para Power BI
- ✅ Verificación de archivos generados
- ✅ Manejo de errores

### procesar_sap_simple.py
- ✅ Procesamiento especializado de archivos SAP
- ✅ Transformación de datos para Power BI
- ✅ Generación de múltiples formatos
- ✅ Creación de metadatos

## 📋 Requisitos

- Python 3.12+
- pandas
- openpyxl
- pyarrow
- win32com (para SAP)

## ⚠️ Notas Importantes

- El script maestro maneja automáticamente los errores de SAP
- Los archivos se generan en `C:\Data\Nite\` (se crea automáticamente)
- El archivo `.parquet` es el recomendado para Power BI por su rendimiento
- Los metadatos incluyen descripciones de todas las columnas
