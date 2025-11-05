# Mapa de Zonas y Regiones - OTIF Master

## Configuración Actualizada con Datos Reales

### RURAL (Verde #2E7D32) - 11 Zonas

| Zona | Nombre |
|------|--------|
| CNL  | Cañas |
| GUA  | Guanacaste |
| LIB  | Liberia |
| LIM  | Limón |
| NIC  | Nicoya |
| PUN  | Puntarenas |
| SCA  | Santa Cruz |
| SIS  | San Isidro |
| ZTL  | Zona Turrialba Limón |
| ZTN  | Zona Turrialba Norte |
| ZTP  | Zona Turrialba Pacífico |

**Total zonas RURAL**: 11

---

### GAM (Azul #1565C0) - 9 Zonas

| Zona | Nombre |
|------|--------|
| AL   | Alajuela |
| CAR  | Cartago |
| CMN  | Carmen |
| CMT  | Cimet |
| COG  | Coguar |
| SJE  | San José Este |
| SJO  | San José |
| SUP  | Superior |
| ZTO  | Zona Oeste |

**Total zonas GAM**: 9

---

### CT01 (Naranja #F57C00) - 1 Zona

| Zona | Nombre |
|------|--------|
| SPE  | San Pedro |

**Total zonas CT01**: 1

---

### CT02 (Púrpura #6A1B9A) - 1 Zona

| Zona | Nombre |
|------|--------|
| VYD  | Viñedos (Vinos) |

**Total zonas CT02**: 1

---

## Resumen Total

- **RURAL**: 11 zonas (50%)
- **GAM**: 9 zonas (41%)
- **CT01**: 1 zona (4.5%)
- **CT02**: 1 zona (4.5%)
- **TOTAL**: 22 zonas

---

## Tabla de Referencia Rápida

| ZONA | REGIÓN | COLOR |
|------|--------|-------|
| AL   | GAM    | Azul |
| CAR  | GAM    | Azul |
| CMN  | GAM    | Azul |
| CMT  | GAM    | Azul |
| COG  | GAM    | Azul |
| SJE  | GAM    | Azul |
| SJO  | GAM    | Azul |
| SUP  | GAM    | Azul |
| ZTO  | GAM    | Azul |
| CNL  | RURAL  | Verde |
| GUA  | RURAL  | Verde |
| LIB  | RURAL  | Verde |
| LIM  | RURAL  | Verde |
| NIC  | RURAL  | Verde |
| PUN  | RURAL  | Verde |
| SCA  | RURAL  | Verde |
| SIS  | RURAL  | Verde |
| ZTL  | RURAL  | Verde |
| ZTN  | RURAL  | Verde |
| ZTP  | RURAL  | Verde |
| SPE  | CT01   | Naranja |
| VYD  | CT02   | Púrpura |

---

## Uso en Scripts

### Importar Configuración:

```python
from configuracion_regiones import mapear_zona_a_region

zona = 'GUA'
region = mapear_zona_a_region(zona)
print(region)  # Output: RURAL
```

### Obtener Zonas de una Región:

```python
from configuracion_regiones import REGIONES_CONFIG

zonas_rural = REGIONES_CONFIG['RURAL']['zonas']
print(zonas_rural)  # ['CNL', 'GUA', 'LIB', ...]
```

### Iterar por Todas las Regiones:

```python
from configuracion_regiones import REGIONES_ORDEN, REGIONES_CONFIG

for region in REGIONES_ORDEN:
    config = REGIONES_CONFIG[region]
    print(f"{config['nombre']}: {len(config['zonas'])} zonas")
```

---

## Archivos que Usan esta Configuración

### Scripts Actualizados:

1. **scripts/sap/configuracion_regiones.py** - Configuración central
2. **Reporte_Monitor_Guías/generar_dashboard_regional.py** - Dashboard con tablas
3. **Reporte_Monitor_Guías/generar_reporte_graficos.py** - Reportes con gráficos
4. **Reporte_PLR_Nite/generar_dashboard_regional.py** - Dashboard PLR

### Todos Usan:
- 4 regiones: RURAL, GAM, CT01, CT02
- 22 zonas totales
- Colores diferenciados
- Mapeo automático zona → región

---

## Cambios Respecto a Configuración Anterior

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Número de regiones | 5 (RURAL, GAM, VINOS, HA, CT01) | 4 (RURAL, GAM, CT01, CT02) |
| Zonas GAM | Indefinidas (fallback) | 9 zonas específicas: AL, CAR, CMN, CMT, COG, SJE, SJO, SUP, ZTO |
| SPE | HA | CT01 |
| VYD | VINOS | CT02 |
| GAM como fallback | Sí | No (ahora es SIN_ZONA si no está en lista) |

---

## Verificación

Para verificar la configuración:

```bash
cd "scripts/sap"
python configuracion_regiones.py
```

Esto mostrará:
- Todas las regiones configuradas
- Zonas de cada región  
- Colores asignados
- Pruebas de mapeo

---

## Notas Importantes

1. **GAM ya NO es fallback**: Ahora tiene zonas específicas
2. **Zonas no listadas** retornan `SIN_ZONA` (no GAM)
3. **CT01 y CT02** reemplazan a HA y VINOS
4. **SPE es CT01**, no HA
5. **VYD es CT02**, no VINOS
6. **Compatibilidad**: Hay alias ZONAS_VINOS y ZONA_HA para scripts antiguos

---

**Fecha de actualización**: 2025-11-05  
**Fuente de datos**: Tabla oficial de zonas  
**Aplicado en**: Monitor_Guías y PLR_Nite  
**Estado**: [OK] Actualizado y Verificado

