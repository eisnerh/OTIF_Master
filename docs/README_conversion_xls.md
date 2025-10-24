# Script de Conversión XLS a XLSX

## Descripción
Este script convierte automáticamente todos los archivos XLS encontrados en la carpeta `Data/SAP_Extraction` a formato XLSX. El script es inteligente y puede manejar diferentes tipos de archivos que tienen extensión .xls pero en realidad son archivos de texto (CSV) con diferentes encodings.

## Características
- **Detección automática de formato**: Identifica si el archivo es realmente XLS o un archivo de texto con extensión .xls
- **Múltiples encodings**: Maneja UTF-16, UTF-8, Latin1, CP1252, etc.
- **Separadores automáticos**: Detecta automáticamente el separador correcto (coma, punto y coma, tabulación, etc.)
- **Lectura robusta**: Incluye métodos de respaldo para archivos problemáticos
- **Estructura consistente**: Mantiene la estructura de columnas de los archivos "final.xlsx" existentes
- **Organización automática**: Mueve los archivos XLS convertidos a una carpeta separada
- **Logging detallado**: Genera logs completos del proceso
- **Resumen de resultados**: Muestra estadísticas detalladas del procesamiento

## Archivos generados
- `convertir_xls_a_xlsx.py`: Script principal de conversión
- `ejecutar_conversion.py`: Script simplificado para ejecución fácil
- `conversion_xls.log`: Log detallado del proceso
- `resumen_conversion_xls.json`: Resumen en formato JSON
- `README_conversion_xls.md`: Este archivo de documentación
- `Data/SAP_Extraction/XLS_Convertidos/`: Carpeta con archivos XLS convertidos organizados por subcarpetas

## Uso

### Ejecución básica
```bash
python convertir_xls_a_xlsx.py
```

### Requisitos
- Python 3.6+
- pandas
- openpyxl
- xlrd (opcional, para archivos XLS reales)

### Instalación de dependencias
```bash
pip install pandas openpyxl xlrd
```

## Resultados del último procesamiento

### Resumen de conversión exitosa:
- **Total de carpetas procesadas**: 8
- **Total de archivos encontrados**: 19
- **Conversiones exitosas**: 19 (100%)
- **Conversiones fallidas**: 0
- **Archivos XLS movidos**: 19 (organizados en subcarpetas)

### Detalle por carpeta:
- `rep_plr`: 2/2 exitosos
- `y_dev_45`: 2/2 exitosos  
- `y_dev_74`: 2/2 exitosos
- `y_dev_82`: 2/2 exitosos
- `zhbo`: 3/3 exitosos
- `zred`: 3/3 exitosos
- `zsd_incidencias`: 3/3 exitosos
- `z_devo_alv`: 2/2 exitosos

## Tipos de archivos procesados

### Archivos convertidos exitosamente:
1. **REP_PLR-2025-10-03.xls** → **REP_PLR-2025-10-03.xlsx** (3,966 filas, 36 columnas)
2. **REP_PLR.xls** → **REP_PLR.xlsx** (3,966 filas, 36 columnas)
3. **y_dev_45_02-10-2025.xls** → **y_dev_45_02-10-2025.xlsx**
4. **y_dev_45_03-10-2025.xls** → **y_dev_45_03-10-2025.xlsx**
5. **y_dev_74_02-10-2025.xls** → **y_dev_74_02-10-2025.xlsx**
6. **y_dev_74_03-10-2025.xls** → **y_dev_74_03-10-2025.xlsx**
7. **y_dev_82_02-10-2025.xls** → **y_dev_82_02-10-2025.xlsx**
8. **y_dev_82_03-10-2025.xls** → **y_dev_82_03-10-2025.xlsx**
9. **zhbo_01-10-2025.xls** → **zhbo_01-10-2025.xlsx** (4,620 filas, 27 columnas)
10. **zhbo_02-10-2025.xls** → **zhbo_02-10-2025.xlsx** (4,237 filas, 27 columnas)
11. **zhbo_03-10-2025.xls** → **zhbo_03-10-2025.xlsx** (1,643 filas, 27 columnas)
12. **zred_01-10-2025.xls** → **zred_01-10-2025.xlsx** (610 filas, 6 columnas)
13. **zred_02-10-2025.xls** → **zred_02-10-2025.xlsx** (627 filas, 6 columnas)
14. **zred_03-10-2025.xls** → **zred_03-10-2025.xlsx** (540 filas, 6 columnas)
15. **zsd_incidencias_01-10-2025.xls** → **zsd_incidencias_01-10-2025.xlsx** (151 filas, 20 columnas)
16. **zsd_incidencias_02-10-2025.xls** → **zsd_incidencias_02-10-2025.xlsx** (132 filas, 20 columnas)
17. **zsd_incidencias_03-10-2025.xls** → **zsd_incidencias_03-10-2025.xlsx** (193 filas, 20 columnas)
18. **z_devo_alv_02-10-2025.xls** → **z_devo_alv_02-10-2025.xlsx** (3,509 filas, 27 columnas)
19. **z_devo_alv_03-10-2025.xls** → **z_devo_alv_03-10-2025.xlsx** (3,625 filas, 27 columnas)

## Formato detectado
Todos los archivos procesados eran en realidad archivos de texto con formato UTF-16 (CSV) que tenían extensión .xls. El script detectó automáticamente este formato y los procesó correctamente.

## Estructura mantenida
Los archivos XLSX generados mantienen la misma estructura de columnas que los archivos "final.xlsx" correspondientes:
- **y_dev_45**: 13 columnas (adaptado de 16 originales)
- **y_dev_74**: 25 columnas (adaptado de 28 originales)  
- **y_dev_82**: 18 columnas (adaptado de 21 originales)
- **zhbo**: 27 columnas (estructura idéntica)
- **zred**: 6 columnas (estructura idéntica)
- **zsd_incidencias**: 20 columnas (estructura idéntica)
- **z_devo_alv**: 27 columnas (estructura idéntica)
- **rep_plr**: 36 columnas (sin archivo final de referencia, mantuvo estructura original)

## Logs y monitoreo
- El script genera logs detallados en `conversion_xls.log`
- Un resumen JSON se guarda en `resumen_conversion_xls.json`
- Los logs incluyen información sobre el formato detectado, número de filas/columnas, y cualquier error encontrado

## Notas técnicas
- Los archivos XLS originales se mueven a `Data/SAP_Extraction/XLS_Convertidos/` organizados por subcarpetas
- Los archivos XLSX se crean en la misma carpeta que los archivos "final.xlsx" correspondientes
- El script mantiene automáticamente la estructura de columnas de los archivos "final.xlsx"
- Si no existe archivo "final.xlsx", mantiene la estructura original del archivo convertido
- El script maneja automáticamente diferentes encodings y separadores
- Incluye métodos de respaldo para archivos problemáticos
- Genera warnings para tipos de datos mixtos pero continúa el procesamiento

## Solución de problemas
Si encuentras problemas:
1. Verifica que pandas y openpyxl estén instalados
2. Revisa el archivo `conversion_xls.log` para detalles del error
3. Asegúrate de que los archivos XLS no estén abiertos en Excel
4. Verifica que tengas permisos de escritura en las carpetas de destino
