# Sistema de Reportes SAP - OTIF Master

## Estructura del Proyecto

### Configuración Central
- **configuracion_regiones.py** - Configuración de 22 zonas en 4 regiones (RURAL, GAM, CT01, CT02)
- **GUIA_CONFIGURACION_REGIONES.md** - Guía de uso de la configuración
- **MAPA_ZONAS_REGIONES.md** - Tabla de referencia de zonas
- **SISTEMA_COMPLETO_LISTO.md** - Guía completa del sistema
- **ESTRUCTURA_REPORTES.md** - Estructura del proyecto

### Reporte_Monitor_Guías
**Propósito**: Monitoreo de guías de entrega por zona y hora

**Scripts**:
- `amalgama_y_dev_74.py` - Script principal con auto-login
- `y_dev_74.py` - Extracción SAP (transacción y_dev_42000074)
- `generar_dashboard_regional.py` - Genera 3 imágenes del dashboard
- `generar_reporte_graficos.py` - Envía correo con imágenes
- `ejecutar_monitor_guias.bat` - Ejecutor manual
- `configurar_tarea_programada.ps1` - Automatización horaria

**Documentación**:
- `README_AUTOMATIZACION.md` - Guía de automatización
- `README_3_IMAGENES.md` - Formato de las 3 imágenes del dashboard

**Uso**:
```bash
cd "Reporte_Monitor_Guías"
ejecutar_monitor_guias.bat
```

**Archivos generados**:
- `dashboard_parte1_detalle.png` (KPIs + Tabla detallada)
- `dashboard_parte2_resumen.png` (Tabla resumen)
- `dashboard_parte3_tendencias.png` (Gráfico de tendencias)
- `Monitor_Guias_DD-MM-YYYY_processed.xlsx`

**Distribución**: Email automático con las 3 imágenes

---

### Reporte_PLR_Nite
**Propósito**: Reporte de planeamiento con fecha de HOY

**Scripts**:
- `amalgama_y_rep_plr.py` - Script principal con auto-login
- `y_rep_plr.py` - Extracción SAP (transacción zsd_rep_planeamiento)
- `generar_dashboard_regional.py` - Dashboard para WhatsApp
- `generar_reporte_grafico.py` - Dashboard general
- `enviar_whatsapp.py` - Envío por WhatsApp
- `verificar_instalacion.py` - Verificar requisitos
- `ejecutar_rep_plr.bat` - Ejecutor manual
- `configurar_tarea_programada.ps1` - Automatización horaria

**Documentación**:
- `INICIO_RAPIDO.md` - Guía de inicio rápido
- `README_REPORTE_PLR.md` - Documentación completa
- `README_REPORTES_WHATSAPP.md` - Guía de reportes para WhatsApp

**Uso**:
```bash
cd "Reporte_PLR_Nite"
ejecutar_rep_plr.bat
```

**Archivos generados**:
- `REP_PLR_NITE_YYYY-MM-DD_processed.xlsx`
- `dashboard_regional_plr_YYYYMMDD_HHMMSS.png`

**Distribución**: WhatsApp (manual, web o automático)

---

## Regiones y Zonas

### GAM (9 zonas):
ALJ, CAR, CMN, CMT, COG, SJE, SJO, SUP, ZTO

### RURAL (11 zonas):
CNL, GUA, LIB, LIM, NIC, PUN, SCA, SIS, ZTL, ZTN, ZTP

### CT01 (1 zona):
SPE

### CT02 (1 zona):
VYD

**Total**: 22 zonas

---

## Características del Sistema

### Auto-Login SAP
- ✅ Inicia SAP si no está abierto
- ✅ Crea nueva sesión si SAP está abierto
- ✅ Login automático con credenciales

### Dashboard de Monitor de Guías (3 Imágenes)
- ✅ **Imagen 1**: KPIs + Tabla detallada (22 zonas × horas)
- ✅ **Imagen 2**: Tabla resumen (4 regiones × horas)
- ✅ **Imagen 3**: Gráfico de tendencias por región
- ✅ Fuentes grandes y negritas para mejor legibilidad
- ✅ Nombres fijos (se sobreescriben)

### Distribución
- ✅ **Monitor Guías**: Email automático con 3 imágenes + Excel
- ✅ **PLR NITE**: WhatsApp con dashboard

### Formato de Logs
- ✅ Sin emojis (texto plano)
- ✅ Formato estandarizado: [OK], [ERROR], [ADVERTENCIA], [INFO]

---

## Instalación Rápida

### 1. Instalar dependencias:
```bash
pip install pandas openpyxl pywin32 matplotlib seaborn numpy
```

### 2. Configurar credenciales:

**Monitor de Guías**:
```bash
cd "Reporte_Monitor_Guías"
copy credentials.ini.example credentials.ini
notepad credentials.ini
```

**PLR NITE**:
```bash
cd "Reporte_PLR_Nite"
copy credentials.ini.example credentials.ini
notepad credentials.ini
```

### 3. Ejecutar:

**Monitor de Guías**:
```bash
cd "Reporte_Monitor_Guías"
ejecutar_monitor_guias.bat
```

**PLR NITE**:
```bash
cd "Reporte_PLR_Nite"
ejecutar_rep_plr.bat
```

---

## Scripts Individuales SAP

Además de los reportes automatizados, hay scripts individuales disponibles:

- `y_dev_45.py`, `y_dev_74.py`, `y_dev_82.py`
- `y_rep_plr.py`
- `zhbo.py`, `zred.py`, `zresguias.py`
- `z_devo_alv.py`, `zsd_incidencias.py`
- Y otros...

Todos pueden ejecutarse manualmente con Python.

---

## Documentación Completa

Ver archivos específicos:
- **SISTEMA_COMPLETO_LISTO.md** - Resumen ejecutivo
- **GUIA_CONFIGURACION_REGIONES.md** - Configuración de zonas
- **MAPA_ZONAS_REGIONES.md** - Tabla de referencia
- **ESTRUCTURA_REPORTES.md** - Estructura del proyecto

---

**Versión**: 3.0.0  
**Última actualización**: 2025-11-05  
**Estado**: [OK] Sistema completo y optimizado

