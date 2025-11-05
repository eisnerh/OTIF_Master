# Aplicación de Configuración de Zonas - Actualización Completa

## Fecha: 2025-11-05

## [EXITO] Configuración Actualizada en Todos los Scripts

Se ha aplicado la segmentación real de zonas en todos los scripts de reportes.

---

## Datos Aplicados

Según la tabla oficial proporcionada:

### Zonas por Región:

**GAM (9 zonas)**:
- AL, CAR, CMN, CMT, COG, SJE, SJO, SUP, ZTO

**RURAL (11 zonas)**:
- CNL, GUA, LIB, LIM, NIC, PUN, SCA, SIS, ZTL, ZTN, ZTP

**CT01 (1 zona)**:
- SPE

**CT02 (1 zona)**:
- VYD

**Total**: 22 zonas definidas

---

## Archivos Actualizados

### 1. Configuración Central

**scripts/sap/configuracion_regiones.py**
- ✅ 4 regiones configuradas (RURAL, GAM, CT01, CT02)
- ✅ 22 zonas asignadas correctamente
- ✅ GAM ya NO es fallback (tiene 9 zonas específicas)
- ✅ Zonas no listadas retornan SIN_ZONA
- ✅ Función de mapeo actualizada
- ✅ Alias para compatibilidad con scripts antiguos

### 2. Reporte_Monitor_Guías

**generar_dashboard_regional.py**
- ✅ Usa configuración centralizada
- ✅ 4 tarjetas KPI (RURAL, GAM, CT01, CT02)
- ✅ Tablas zona x hora para cada región
- ✅ Colores actualizados
- ✅ Orden de regiones actualizado

**generar_reporte_graficos.py**
- ✅ Usa configuración centralizada
- ✅ Mapeo actualizado
- ✅ Fallback con configuración correcta
- ✅ Adjunta dashboard al correo

### 3. Reporte_PLR_Nite

**generar_dashboard_regional.py**
- ✅ Usa configuración centralizada  
- ✅ 4 regiones en dashboards
- ✅ Colores actualizados
- ✅ Fallback con configuración correcta

**amalgama_y_rep_plr.py**
- ✅ Genera dashboard automáticamente
- ✅ Dashboard usa configuración actualizada

---

## Estructura del Dashboard Actualizada

### Fila 1: KPIs (4 tarjetas)
1. RURAL (Verde) - 11 zonas
2. GAM (Azul) - 9 zonas
3. CT01 (Naranja) - SPE
4. CT02 (Púrpura) - VYD

### Fila 2: Total General
- Tarjeta central con total de guías/registros

### Filas 3-4: Tabla RURAL
- Heatmap zona x hora
- 11 zonas ordenadas por volumen

### Filas 5-6: Tabla GAM
- Heatmap zona x hora
- Top 15 zonas (o todas las 9 si hay menos)

### Fila 7: Tablas CT01 y CT02
- CT01 (izquierda): SPE por hora
- CT02 (derecha): VYD por hora

### Fila 8: Comparativo General
- Gráfico de barras
- Las 4 regiones comparadas
- Valores y porcentajes

---

## Cambios Importantes

### Antes:
- 5 regiones: RURAL, GAM, VINOS, HA, CT01
- GAM era "catch-all" (todas las zonas no definidas)
- SPE estaba en HA
- VYD estaba en VINOS

### Ahora:
- 4 regiones: RURAL, GAM, CT01, CT02
- GAM tiene 9 zonas específicas
- SPE está en CT01
- VYD está en CT02
- Zonas no listadas retornan SIN_ZONA (no se incluyen)

---

## Compatibilidad con Scripts Antiguos

Se mantiene compatibilidad mediante alias:

```python
# En configuracion_regiones.py
ZONAS_VINOS = ZONAS_CT02  # Alias de VYD
ZONA_HA = ZONA_CT01       # Alias de SPE
```

Scripts antiguos que usen `ZONAS_VINOS` o `ZONA_HA` seguirán funcionando.

---

## Verificación

### Probar Configuración:

```bash
cd "scripts/sap"
python configuracion_regiones.py
```

### Probar Dashboard Monitor Guías:

```bash
cd "Reporte_Monitor_Guías"

# Si tienes un archivo Excel de prueba
python generar_dashboard_regional.py --archivo "Monitor_Guias_05-11-2025_processed.xlsx"
```

### Probar Dashboard PLR NITE:

```bash
cd "Reporte_PLR_Nite"

# Si tienes un archivo Excel de prueba
python generar_dashboard_regional.py --archivo "REP_PLR_NITE_2025-11-05_processed.xlsx"
```

---

## Validación de Zonas

Todas las zonas de la tabla oficial están mapeadas:

✅ AL → GAM  
✅ CAR → GAM  
✅ CMN → GAM  
✅ CMT → GAM  
✅ COG → GAM  
✅ SJE → GAM  
✅ SJO → GAM  
✅ SUP → GAM  
✅ ZTO → GAM  
✅ CNL → RURAL  
✅ GUA → RURAL  
✅ LIB → RURAL  
✅ LIM → RURAL  
✅ NIC → RURAL  
✅ PUN → RURAL  
✅ SCA → RURAL  
✅ SIS → RURAL  
✅ ZTL → RURAL  
✅ ZTN → RURAL  
✅ ZTP → RURAL  
✅ SPE → CT01  
✅ VYD → CT02  

**Total**: 22 zonas mapeadas correctamente

---

## Scripts que Usan la Configuración

### Directamente (importan configuracion_regiones.py):
1. ✅ Reporte_Monitor_Guías/generar_dashboard_regional.py
2. ✅ Reporte_Monitor_Guías/generar_reporte_graficos.py
3. ✅ Reporte_PLR_Nite/generar_dashboard_regional.py

### Indirectamente (llaman a los scripts anteriores):
1. ✅ Reporte_Monitor_Guías/amalgama_y_dev_74.py
2. ✅ Reporte_PLR_Nite/amalgama_y_rep_plr.py

---

## Flujo Completo

### Monitor de Guías:

```
ejecutar_monitor_guias.bat
  ↓
amalgama_y_dev_74.py
  ↓
y_dev_74.py → Extrae de SAP
  ↓
Procesa datos
  ↓
generar_dashboard_regional.py
  ├── Usa configuracion_regiones.py
  ├── Mapea 22 zonas a 4 regiones
  ├── Genera tablas zona x hora
  └── Crea dashboard_regional_*.png
  ↓
generar_reporte_graficos.py
  ├── Usa configuracion_regiones.py
  ├── Genera gráficos por zona
  ├── Adjunta dashboard al correo
  └── Envía email
```

### PLR NITE:

```
ejecutar_rep_plr.bat
  ↓
amalgama_y_rep_plr.py
  ↓
y_rep_plr.py → Extrae de SAP
  ↓
Procesa datos (elimina col A, fila 5, 3 filas)
  ↓
generar_dashboard_regional.py
  ├── Usa configuracion_regiones.py
  ├── Mapea zonas a 4 regiones
  └── Crea dashboard_regional_plr_*.png
```

---

## Colores por Región

```python
RURAL:  #2E7D32  ████ Verde oscuro
GAM:    #1565C0  ████ Azul
CT01:   #F57C00  ████ Naranja
CT02:   #6A1B9A  ████ Púrpura
```

---

## Mantenimiento Futuro

### Para Agregar una Nueva Zona:

Edita `scripts/sap/configuracion_regiones.py`:

```python
'RURAL': {
    'zonas': ['CNL', 'GUA', ..., 'NUEVA_ZONA'],  # Agregar aquí
    ...
}
```

### Para Cambiar una Zona de Región:

1. Quítala de la región actual
2. Agrégala a la región nueva
3. Los dashboards se actualizarán automáticamente

### Para Agregar una Nueva Región:

```python
REGIONES_CONFIG = {
    ...
    'NUEVA_REGION': {
        'zonas': ['Z1', 'Z2'],
        'color': '#00FF00',
        'nombre': 'Nueva Region',
        'descripcion': 'Descripcion'
    }
}

REGIONES_ORDEN = ['RURAL', 'GAM', 'CT01', 'CT02', 'NUEVA_REGION']
```

---

## Beneficios de esta Implementación

1. **Precisión**: Usa datos reales oficiales
2. **Consistencia**: Todos los reportes usan la misma configuración
3. **Mantenimiento**: Cambios en un solo lugar
4. **Validación**: Zonas no listadas se detectan (SIN_ZONA)
5. **Documentación**: Tabla de referencia clara
6. **Escalabilidad**: Fácil agregar zonas/regiones

---

## Diferencias con Configuración Anterior

### Zonas Agregadas a GAM:
- AL (Alajuela)
- CAR (Cartago)
- CMN (Carmen)
- CMT (Cimet)
- COG (Coguar)
- SJE (San José Este)
- SJO (San José)
- SUP (Superior)
- ZTO (Zona Oeste)

### Cambios de Región:
- SPE: HA → CT01
- VYD: VINOS → CT02

### Regiones Renombradas:
- HA → CT01
- VINOS → CT02

---

**Versión**: 2.0  
**Basado en**: Tabla oficial de zonas  
**Estado**: [OK] Aplicado en todos los scripts  
**Validado**: Sí (22/22 zonas)

