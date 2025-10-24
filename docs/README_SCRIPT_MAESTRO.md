# Script Maestro SAP Python

## 📋 Descripción

Este script maestro en Python integra toda la lógica de los scripts VBA de `data_script_sap` para automatizar la ejecución de múltiples transacciones SAP y exportar los reportes correspondientes.

## 🚀 Características

- **Automatización completa**: Ejecuta todas las transacciones SAP configuradas
- **Configuración flexible**: Sistema de configuración JSON personalizable
- **Manejo de errores**: Logging detallado y manejo robusto de errores
- **Verificación de archivos**: Valida que los archivos se generen correctamente
- **Fechas personalizables**: Soporte para fechas específicas en transacciones
- **Ejecución selectiva**: Posibilidad de ejecutar solo transacciones específicas

## 📁 Archivos del Sistema

```
OTIF_Estructurado/SAP_SCRIPTING/REVISOR_SCRIPTS/python_script/
├── script_maestro_sap_python.py      # Script principal
├── configuracion_sap.json            # Configuración del sistema
├── ejemplo_uso_script_maestro.py     # Ejemplos de uso
├── instalar_dependencias.py          # Instalador de dependencias
└── README_SCRIPT_MAESTRO.md          # Esta documentación
```

## 🛠️ Instalación

### 1. Instalar Dependencias

```bash
# Ejecutar el instalador automático
python instalar_dependencias.py

# O instalar manualmente
pip install pywin32 python-dateutil
```

### 2. Verificar SAP GUI

Asegúrate de que SAP GUI esté instalado y funcionando en tu sistema.

## ⚙️ Configuración

### Archivo de Configuración (`configuracion_sap.json`)

```json
{
  "output_path": "C:\\data",
  "encoding": "0000",
  "date_format": "%d.%m.%Y",
  "transactions": {
    "rep_plr": {
      "transaction": "zsd_rep_planeamiento",
      "filename": "REP_PLR.xls",
      "node": "F00120",
      "row": 11,
      "date_field": "P_LFDAT-LOW"
    }
  }
}
```

### Parámetros de Configuración

- **output_path**: Ruta donde se guardan los archivos exportados
- **encoding**: Codificación de archivos (0000 = UTF-8)
- **date_format**: Formato de fecha para transacciones
- **transactions**: Configuración de cada transacción SAP

## 🚀 Uso

### Uso Básico - Ejecutar Todas las Transacciones

```python
from script_maestro_sap_python import SAPAutomation

# Crear instancia
sap_auto = SAPAutomation()

# Ejecutar todas las transacciones
results = sap_auto.execute_all_transactions()
```

### Uso Avanzado - Transacciones Específicas

```python
# Ejecutar solo transacciones específicas
transacciones = ["rep_plr", "y_dev_45", "zred"]
results = sap_auto.execute_specific_transactions(transacciones)
```

### Uso con Fecha Personalizada

```python
# Ejecutar con fecha específica
fecha_personalizada = "15.01.2025"
results = sap_auto.execute_all_transactions(fecha_personalizada)
```

## 📊 Transacciones Soportadas

| Transacción | Descripción | Archivo de Salida |
|-------------|-------------|-------------------|
| `rep_plr` | Reporte de Planeamiento | REP_PLR.xls |
| `y_dev_45` | Devoluciones 45 | y_dev_45.xls |
| `y_dev_74` | Devoluciones 74 | y_dev_74.xls |
| `y_dev_82` | Devoluciones 82 | y_dev_82.xls |
| `zred` | Reporte de Red | zred.xls |
| `zhbo` | Reporte HBO | zhbo.xls |
| `z_devo_alv` | Devoluciones ALV | z_devo_alv.xls |
| `zsd_incidencias` | Incidencias | data_incidencias.xls |

## 🔧 Clase SAPAutomation

### Métodos Principales

#### `__init__(config_file)`
Inicializa la conexión con SAP GUI y carga la configuración.

#### `connect_sap()`
Establece conexión con SAP GUI.

#### `execute_transaction(transaction_name, custom_date=None)`
Ejecuta una transacción SAP específica.

#### `execute_all_transactions(custom_date=None)`
Ejecuta todas las transacciones configuradas.

#### `execute_specific_transactions(transaction_list, custom_date=None)`
Ejecuta solo las transacciones especificadas.

#### `verify_output_files()`
Verifica que los archivos de salida se hayan generado correctamente.

## 📝 Logging

El sistema genera logs detallados en `sap_automation.log`:

```
2025-01-15 10:30:15 - INFO - 🔐 Conectando a SAP GUI...
2025-01-15 10:30:16 - INFO - ✅ Conexión SAP establecida correctamente
2025-01-15 10:30:17 - INFO - 📊 Ejecutando transacción: rep_plr
2025-01-15 10:30:25 - INFO - ✅ Transacción rep_plr ejecutada correctamente
```

## 🎯 Ejemplos de Uso

### Ejemplo 1: Ejecución Completa

```python
# Ejecutar script completo
python script_maestro_sap_python.py
```

### Ejemplo 2: Uso Programático

```python
from script_maestro_sap_python import SAPAutomation

# Crear automatizador
sap_auto = SAPAutomation()

# Conectar a SAP
if sap_auto.connect_sap():
    # Ejecutar transacciones específicas
    results = sap_auto.execute_specific_transactions([
        "rep_plr", 
        "y_dev_45"
    ])
    
    # Verificar archivos
    sap_auto.verify_output_files()
```

### Ejemplo 3: Configuración Personalizada

```python
# Usar configuración personalizada
sap_auto = SAPAutomation("mi_configuracion.json")

# Ejecutar con fecha específica
results = sap_auto.execute_all_transactions("01.01.2025")
```

## 🚨 Manejo de Errores

El sistema incluye manejo robusto de errores:

- **Conexión SAP**: Verifica que SAP GUI esté disponible
- **Transacciones**: Maneja errores en transacciones individuales
- **Archivos**: Verifica que los archivos se generen correctamente
- **Logging**: Registra todos los errores para diagnóstico

## 📋 Requisitos del Sistema

- **Python**: 3.7 o superior
- **SAP GUI**: Instalado y configurado
- **Windows**: Sistema operativo Windows
- **Dependencias**: pywin32, python-dateutil

## 🔍 Solución de Problemas

### Error: "No se puede conectar a SAP"
- Verificar que SAP GUI esté abierto
- Comprobar que la sesión SAP esté activa
- Revisar permisos de usuario

### Error: "Transacción no encontrada"
- Verificar que la transacción esté en la configuración
- Comprobar que el código de transacción sea correcto

### Error: "Archivo no generado"
- Verificar permisos de escritura en la carpeta de salida
- Comprobar que la transacción se ejecutó correctamente
- Revisar logs para errores específicos

## 📞 Soporte

Para soporte técnico o reportar problemas:

1. Revisar los logs en `sap_automation.log`
2. Verificar la configuración en `configuracion_sap.json`
3. Comprobar que SAP GUI esté funcionando correctamente

## 🔄 Actualizaciones

### Versión 1.0
- Implementación inicial
- Soporte para 8 transacciones SAP
- Sistema de configuración JSON
- Logging completo
- Verificación de archivos

## 📄 Licencia

Este proyecto está bajo la licencia del sistema OTIF Master.
