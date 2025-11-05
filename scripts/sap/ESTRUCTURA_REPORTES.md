# Estructura de Reportes SAP - OTIF Master

## Resumen de la Limpieza del Proyecto

Se eliminó la carpeta `Reporte_PLR` para evitar duplicación y mantener solo la versión mejorada en `Reporte_PLR_Nite`.

## Estructura Actual

```
scripts/sap/
 Reporte_Monitor_Guías/          # Reporte de monitoreo de guías por zona
    amalgama_y_dev_74.py        # Script principal con auto-login
    y_dev_74.py                 # Módulo de extracción SAP
    generar_reporte_graficos.py # Generación de gráficos
    ejecutar_monitor_guias.bat  # Ejecutor batch
    configurar_tarea_programada.ps1
    credentials.ini.example
    README_AUTOMATIZACION.md

 Reporte_PLR_Nite/               # Reporte PLR mejorado (VERSIÓN ACTUALIZADA)
    amalgama_y_rep_plr.py       # Script principal con auto-login
    y_rep_plr.py                # Módulo de extracción SAP
    generar_reporte_grafico.py  # Generación de dashboard para WhatsApp
    enviar_whatsapp.py          # Envío automático por WhatsApp
    ejecutar_rep_plr.bat        # Ejecutor batch
    configurar_tarea_programada.ps1
    verificar_instalacion.py    # Verificador de requisitos
    credentials.ini.example
    .gitignore
    INICIO_RAPIDO.md
    README_REPORTE_PLR.md
    README_REPORTES_WHATSAPP.md
    CAMBIOS_Y_CONFIGURACION.md
    RESUMEN_PROYECTO.md

 [Otros scripts individuales]
     automatizacion_reportes_sap.py
     convertir_xls_a_xlsx.py
     y_dev_45.py
     y_dev_82.py
     zhbo.py
     zred.py
     ...
```

## Diferencias Entre los Reportes

### Reporte_Monitor_Guías (Y_DEV_74)

**Propósito**: Monitoreo de guías de entrega por zona y hora

**Características**:
- Transacción: `y_dev_42000074`
- Nodo del árbol: `F00119`
- Fila ALV: 25
- Fecha por defecto: **AYER**
- Agrupación de zonas:
  - RURAL: GUA, NIC, PUN, SCA, CNL, LIM, LIB, SIS, ZTP, ZTN, ZTL
  - VINOS: CT02
  - HA: SPE
  - GAM: Resto
- Gráficos por hora
- Envío por correo electrónico
- Con emojis en logs

**Archivos generados**:
- `Monitor_Guias.txt` (texto tabulado de SAP)
- `Monitor_Guias_DD-MM-YYYY_processed.xlsx` (Excel procesado)
- Gráficos PNG por zona

### Reporte_PLR_Nite (ZSD_REP_PLANEAMIENTO)

**Propósito**: Reporte de planeamiento con dashboard para WhatsApp

**Características**:
- Transacción: `zsd_rep_planeamiento`
- Nodo del árbol: `F00120`
- Fila ALV: 11
- Fecha por defecto: **HOY**
- Procesamiento de datos:
  1. Elimina Columna A
  2. Elimina Fila 5
  3. Elimina primeras 3 filas
- **Sin emojis** (texto plano en logs)
- Dashboard estilo Power BI
- Envío por WhatsApp (múltiples métodos)
- Verificación de instalación

**Archivos generados**:
- `REP_PLR_NITE.txt` (texto tabulado de SAP)
- `REP_PLR_NITE_YYYY-MM-DD_processed.xlsx` (Excel procesado)
- `reporte_grafico_YYYYMMDD_HHMMSS.png` (Dashboard completo)

**Mejoras exclusivas**:
- [OK] Auto-login inteligente
- [OK] Nueva sesión si SAP ya está abierto
- [OK] Logs sin emojis (mejor compatibilidad)
- [OK] Dashboard completo con KPIs
- [OK] Múltiples gráficos: barras, líneas, comparativos
- [OK] Envío por WhatsApp (manual, web, automático)
- [OK] Verificador de instalación
- [OK] Documentación extensa

## Ubicaciones de Archivos

### Archivos de Salida SAP

**Monitor Guías**:
```
C:\data\SAP_Extraction\y_dev_74\
 Monitor_Guias.txt
 Monitor_Guias_DD-MM-YYYY_processed.xlsx
 graficos\
     grafico_todas_zonas.png
     grafico_rural.png
     grafico_gam.png
     grafico_vinos.png
     grafico_ha.png
```

**Reporte PLR Nite**:
```
C:\data\SAP_Extraction\rep_plr_nite\
 REP_PLR_NITE.txt
 REP_PLR_NITE_YYYY-MM-DD_processed.xlsx
 reporte_grafico_YYYYMMDD_HHMMSS.png
```

## Uso Recomendado

### Para Monitoreo de Guías por Zona y Hora
```bash
cd "scripts\sap\Reporte_Monitor_Guías"
ejecutar_monitor_guias.bat
```

### Para Reporte PLR con Dashboard WhatsApp
```bash
cd "scripts\sap\Reporte_PLR_Nite"
ejecutar_rep_plr.bat
```

## Configuración

Ambos reportes usan el mismo formato de `credentials.ini`:

```ini
[AUTH]
sap_system = SAP R/3 Productivo [FIFCOR3]
sap_client = 700
sap_user = tu_usuario
sap_password = tu_contraseña
sap_language = ES

[EMAIL]  # Solo para Monitor_Guías
smtp_server = smtp.gmail.com
smtp_port = 587
email_from = tu_email@gmail.com
email_password = tu_contraseña_o_app_password
email_to = destinatario1@example.com, destinatario2@example.com

[WHATSAPP]  # Solo para Reporte_PLR_Nite
metodo = manual
numeros = +50612345678
mensaje = Reporte PLR NITE - Dashboard de Ventas
```

## Automatización

Ambos reportes pueden programarse para ejecución automática:

```powershell
# Monitor Guías - cada hora entre 14:00 y 22:00
cd "Reporte_Monitor_Guías"
.\configurar_tarea_programada.ps1

# Reporte PLR Nite - cada hora entre 14:00 y 22:00
cd "Reporte_PLR_Nite"
.\configurar_tarea_programada.ps1
```

## Dependencias

### Comunes
```bash
pip install pandas openpyxl pywin32
```

### Monitor Guías (adicional)
```bash
pip install matplotlib seaborn
```

### Reporte PLR Nite (adicional)
```bash
pip install matplotlib seaborn pywhatkit  # pywhatkit es opcional
```

## Scripts Individuales Disponibles

Además de los reportes automatizados, hay scripts individuales para ejecución manual:

- `y_dev_45.py` - Reporte Y_DEV_45
- `y_dev_82.py` - Reporte Y_DEV_82
- `zhbo.py` - Reporte ZHBO
- `zred.py` - Reporte ZRED
- `zresguias.py` - Reporte ZRESGUIAS
- `zsd_incidencias.py` - Reporte de Incidencias
- Y otros...

Todos estos scripts pueden ejecutarse individualmente con Python.

## Ventajas de la Estructura Limpia

1. [OK] **Sin duplicación**: Solo una versión de cada reporte
2. [OK] **Clara separación**: Cada reporte en su carpeta
3. [OK] **Fácil mantenimiento**: Cambios en un solo lugar
4. [OK] **Mejor organización**: Documentación junto al código
5. [OK] **Escalable**: Fácil agregar nuevos reportes

## Próximos Pasos

Para usar los reportes:

1. **Configurar credenciales**:
   - Copia `credentials.ini.example` a `credentials.ini`
   - Edita con tus datos SAP

2. **Verificar instalación** (solo Reporte_PLR_Nite):
   ```bash
   python verificar_instalacion.py
   ```

3. **Ejecutar manualmente**:
   ```bash
   ejecutar_monitor_guias.bat  # o ejecutar_rep_plr.bat
   ```

4. **Programar ejecución automática** (opcional):
   ```powershell
   .\configurar_tarea_programada.ps1
   ```

## Soporte

Para más información:

- **Monitor Guías**: Ver `README_AUTOMATIZACION.md` en su carpeta
- **Reporte PLR Nite**: Ver documentación en su carpeta:
  - `INICIO_RAPIDO.md` - Guía de inicio rápido
  - `README_REPORTE_PLR.md` - Documentación completa
  - `README_REPORTES_WHATSAPP.md` - Guía de reportes gráficos
  - `CAMBIOS_Y_CONFIGURACION.md` - Configuración detallada

---

**Última actualización**: 2025-11-05  
**Estado**: Estructura limpia y optimizada [OK]

