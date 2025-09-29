# REVISOR_SCRIPTS - Sistema de Automatización SAP

## 📋 Descripción

Esta carpeta contiene todos los scripts de automatización SAP organizados en dos categorías principales:

1. **Scripts VBA originales** (`data_script_sap/`)
2. **Scripts Python modernos** (`python_script/`)

## 📁 Estructura de Carpetas

```
REVISOR_SCRIPTS/
├── data_script_sap/           # Scripts VBA originales
│   ├── rep_plr.vba
│   ├── y_dev_45.vba
│   ├── y_dev_74.vba
│   ├── y_dev_82.vba
│   ├── z_devo_alv.vba
│   ├── zhbo.vba
│   ├── zred.vba
│   └── zsd_incidencias.vba
└── python_script/             # Scripts Python modernos
    ├── script_maestro_sap_python.py
    ├── configuracion_sap.json
    ├── ejemplo_uso_script_maestro.py
    ├── instalar_dependencias.py
    └── README_SCRIPT_MAESTRO.md
```

## 🔄 Migración de Scripts

### Scripts VBA → Python

Los scripts VBA originales han sido migrados a Python para ofrecer:

- ✅ **Mejor mantenibilidad**
- ✅ **Configuración centralizada**
- ✅ **Logging detallado**
- ✅ **Manejo robusto de errores**
- ✅ **Verificación automática de archivos**

### Mapeo de Scripts

| Script VBA | Script Python | Descripción |
|------------|---------------|-------------|
| `rep_plr.vba` | `script_maestro_sap_python.py` | Reporte de Planeamiento |
| `y_dev_45.vba` | `script_maestro_sap_python.py` | Devoluciones 45 |
| `y_dev_74.vba` | `script_maestro_sap_python.py` | Devoluciones 74 |
| `y_dev_82.vba` | `script_maestro_sap_python.py` | Devoluciones 82 |
| `zred.vba` | `script_maestro_sap_python.py` | Reporte de Red |
| `zhbo.vba` | `script_maestro_sap_python.py` | Reporte HBO |
| `z_devo_alv.vba` | `script_maestro_sap_python.py` | Devoluciones ALV |
| `zsd_incidencias.vba` | `script_maestro_sap_python.py` | Incidencias |

## 🚀 Uso Recomendado

### Para Nuevos Proyectos
**Usar los scripts Python** en `python_script/`:

```bash
cd python_script
python script_maestro_sap_python.py
```

### Para Mantenimiento
Los scripts VBA se mantienen como referencia histórica y para casos específicos donde Python no esté disponible.

## 📊 Ventajas del Sistema Python

### 🔧 Configuración Centralizada
- Un solo archivo JSON para todas las transacciones
- Fácil modificación de parámetros
- Configuración por entorno

### 📝 Logging Avanzado
- Logs detallados de cada operación
- Seguimiento de errores específicos
- Historial de ejecuciones

### 🛡️ Manejo de Errores
- Reintentos automáticos
- Validación de archivos generados
- Notificaciones de estado

### ⚡ Rendimiento
- Ejecución paralela de transacciones
- Optimización de tiempos de espera
- Verificación automática de resultados

## 🔄 Migración Gradual

### Fase 1: Implementación
- ✅ Scripts Python creados
- ✅ Configuración centralizada
- ✅ Documentación completa

### Fase 2: Pruebas
- 🔄 Validación en entorno de desarrollo
- 🔄 Pruebas de integración
- 🔄 Optimización de rendimiento

### Fase 3: Producción
- 📋 Despliegue en producción
- 📋 Monitoreo y ajustes
- 📋 Capacitación del equipo

## 📞 Soporte

Para soporte técnico:

1. **Scripts Python**: Ver `python_script/README_SCRIPT_MAESTRO.md`
2. **Scripts VBA**: Consultar documentación original
3. **Migración**: Contactar al equipo de desarrollo

## 🔄 Actualizaciones

### Versión 2.0 (Actual)
- ✅ Migración completa a Python
- ✅ Sistema de configuración JSON
- ✅ Logging avanzado
- ✅ Verificación automática

### Versión 1.0 (Legacy)
- Scripts VBA individuales
- Configuración manual
- Logging básico

## 📄 Licencia

Este proyecto está bajo la licencia del sistema OTIF Master.
