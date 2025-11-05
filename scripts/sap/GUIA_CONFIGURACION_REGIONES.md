# Guía de Configuración de Regiones y Zonas

## Descripción

Este documento describe la configuración centralizada de regiones y zonas utilizada en todos los reportes del sistema OTIF Master.

## Archivo Central

**Ubicación**: `scripts/sap/configuracion_regiones.py`

Este archivo contiene:
- Definición de todas las regiones
- Zonas asociadas a cada región
- Colores para visualización
- Funciones de mapeo automático

## Configuración de Regiones

### RURAL (Verde #2E7D32)

**Zonas incluidas**:
- GUA (Guanacaste)
- NIC (Nicoya)
- PUN (Puntarenas)
- SCA (Santa Cruz)
- CNL (Cañas)
- LIM (Limón)
- LIB (Liberia)
- SIS (San Isidro)
- ZTP (Zona Turrialba Pacífico)
- ZTN (Zona Turrialba Norte)
- ZTL (Zona Turrialba Limón)

### GAM (Azul #1565C0)

**Zonas incluidas**: Todas las zonas que NO pertenecen a otras regiones

**Nota**: GAM es la región "por defecto" (catch-all)

### VINOS (Púrpura #6A1B9A)

**Zonas incluidas**:
- CT02 (Centro de Distribución Vinos 02)
- VYD (Viñedos)

**Nota**: Algunos sistemas usan CT02, otros VYD

### HA (Naranja #F57C00)

**Zonas incluidas**:
- SPE (San Pedro - Heredia/Alajuela)

### CT01 (Rojo #C62828)

**Zonas incluidas**:
- CT01 (Centro de Distribución 01)

## Uso en Scripts

### Importar la Configuración

```python
import sys
from pathlib import Path

# Agregar carpeta padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from configuracion_regiones import (
    REGIONES_CONFIG,      # Diccionario completo con toda la info
    REGIONES_ORDEN,       # Lista ordenada de regiones
    mapear_zona_a_region, # Función para mapear zona -> región
    obtener_color_region, # Obtener color de una región
    obtener_nombre_region # Obtener nombre display de región
)
```

### Ejemplo 1: Mapear una Zona a su Región

```python
from configuracion_regiones import mapear_zona_a_region

zona = 'GUA'
region = mapear_zona_a_region(zona)
print(f"{zona} pertenece a {region}")  # GUA pertenece a RURAL
```

### Ejemplo 2: Obtener Información de una Región

```python
from configuracion_regiones import REGIONES_CONFIG, obtener_color_region

region = 'RURAL'
config = REGIONES_CONFIG[region]

print(f"Nombre: {config['nombre']}")
print(f"Color: {config['color']}")
print(f"Zonas: {config['zonas']}")
print(f"Descripción: {config['descripcion']}")
```

### Ejemplo 3: Iterar por Todas las Regiones

```python
from configuracion_regiones import REGIONES_ORDEN, REGIONES_CONFIG

for region in REGIONES_ORDEN:
    config = REGIONES_CONFIG[region]
    print(f"{config['nombre']}: {len(config['zonas'])} zonas")
```

## Scripts que Usan esta Configuración

### Reporte_Monitor_Guías

1. **generar_dashboard_regional.py**
   - Usa para segmentar zonas por región
   - Colores diferenciados por región
   - Tablas zona x hora

2. **generar_reporte_graficos.py**
   - Usa para agrupar zonas
   - Generar gráficos por zona agrupada

3. **amalgama_y_dev_74.py**
   - No usa directamente, pero llama a los scripts que sí

### Reporte_PLR_Nite

1. **generar_dashboard_regional.py**
   - Usa para segmentar datos PLR por región
   - Dashboard con KPIs y gráficos

2. **generar_reporte_grafico.py**
   - Dashboard general para WhatsApp
   - Segmentación por región

3. **amalgama_y_rep_plr.py**
   - No usa directamente, pero llama a los scripts que sí

## Modificar la Configuración

### Agregar una Nueva Región

Edita `configuracion_regiones.py`:

```python
REGIONES_CONFIG = {
    # ... regiones existentes ...
    'NUEVA_REGION': {
        'zonas': ['ZONA1', 'ZONA2', 'ZONA3'],
        'color': '#00FF00',  # Color hex
        'nombre': 'Nueva Region',
        'descripcion': 'Descripcion de la nueva region'
    }
}

# Agregar al orden
REGIONES_ORDEN = ['RURAL', 'GAM', 'VINOS', 'HA', 'CT01', 'NUEVA_REGION']
```

### Agregar Zonas a una Región Existente

```python
'RURAL': {
    'zonas': ['GUA', 'NIC', 'PUN', ..., 'NUEVA_ZONA'],  # Agregar aquí
    ...
}
```

### Cambiar Color de una Región

```python
'RURAL': {
    ...
    'color': '#FF0000',  # Nuevo color en formato hexadecimal
    ...
}
```

## Colores Recomendados

```python
# Verdes
'#2E7D32'  # Verde oscuro (actual RURAL)
'#43A047'  # Verde medio
'#66BB6A'  # Verde claro

# Azules
'#1565C0'  # Azul oscuro (actual GAM)
'#1976D2'  # Azul medio
'#42A5F5'  # Azul claro

# Púrpuras
'#6A1B9A'  # Púrpura oscuro (actual VINOS)
'#7B1FA2'  # Púrpura medio
'#9C27B0'  # Púrpura claro

# Naranjas
'#F57C00'  # Naranja oscuro (actual HA)
'#FB8C00'  # Naranja medio
'#FFA726'  # Naranja claro

# Rojos
'#C62828'  # Rojo oscuro (actual CT01)
'#D32F2F'  # Rojo medio
'#E53935'  # Rojo claro
```

## Ventajas de la Configuración Centralizada

1. **Consistencia**: Todos los reportes usan las mismas regiones
2. **Mantenimiento**: Cambios en un solo lugar
3. **Escalabilidad**: Fácil agregar nuevas regiones
4. **Reutilización**: Múltiples scripts usan el mismo código
5. **Documentación**: Todo en un solo archivo

## Verificar la Configuración

Ejecuta el módulo directamente:

```bash
cd "D:\Users\eisne\OneDrive - Distribuidora La Florida S.A\65-Gestión\LogiRoute_CR\OTIF_Master\scripts\sap"
python configuracion_regiones.py
```

Esto mostrará:
- Todas las regiones configuradas
- Zonas de cada región
- Colores asignados
- Pruebas de mapeo de zonas

## Ejemplo de Salida

```
============================================================
Configuracion de Regiones y Zonas
============================================================

RURAL (RURAL):
  Color: #2E7D32
  Descripcion: Zonas rurales
  Zonas (11): GUA, NIC, PUN, SCA, CNL, LIM, LIB, SIS, ZTP, ZTN, ZTL

GAM (GAM):
  Color: #1565C0
  Descripcion: Gran Area Metropolitana
  Zonas: [Todas las demas]

VINOS (VINOS):
  Color: #6A1B9A
  Descripcion: Centro de Distribucion de Vinos
  Zonas (2): CT02, VYD

...

============================================================
Pruebas de mapeo:
============================================================
  GUA        -> RURAL      (#2E7D32)
  CT02       -> VINOS      (#6A1B9A)
  SPE        -> HA         (#F57C00)
  ...
```

## Solución de Problemas

### Error: "No module named 'configuracion_regiones'"

**Causa**: El script no encuentra el archivo `configuracion_regiones.py`

**Solución**: 
```python
# Asegúrate de agregar el path correcto
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Zona no se mapea correctamente

**Causa**: La zona no está en ninguna lista o está mal escrita

**Solución**:
1. Verifica que la zona esté en `configuracion_regiones.py`
2. Verifica que esté en MAYÚSCULAS
3. Si es una zona nueva, agrégala a la región correspondiente

### Colores no se ven bien

**Causa**: Conflicto de colores o colores no accesibles

**Solución**: Usa colores con buen contraste. Consulta la sección "Colores Recomendados"

## Compatibilidad

### Scripts Antiguos

Los scripts que usan la configuración antigua seguirán funcionando porque:
1. Cada script tiene un "fallback" con la configuración embebida
2. La función `mapear_zona()` existe en ambos (alias de `mapear_zona_a_region()`)
3. Las constantes `ZONAS_RURAL`, `ZONA_VINOS`, etc. se exportan para compatibilidad

### Scripts Nuevos

Los scripts nuevos deben usar la configuración centralizada:
```python
from configuracion_regiones import mapear_zona_a_region
# En lugar de tener su propia función mapear_zona()
```

## Actualización de Scripts Existentes

Para actualizar un script antiguo:

1. Eliminar la configuración local de zonas
2. Importar desde `configuracion_regiones`
3. Usar las funciones de mapeo centralizadas
4. Mantener fallback para compatibilidad

## Estructura de Archivos

```
scripts/sap/
├── configuracion_regiones.py          ← CONFIGURACIÓN CENTRAL
│
├── Reporte_Monitor_Guías/
│   ├── generar_dashboard_regional.py  ← Usa config central
│   ├── generar_reporte_graficos.py    ← Usa config central
│   └── ...
│
└── Reporte_PLR_Nite/
    ├── generar_dashboard_regional.py  ← Usa config central
    ├── generar_reporte_grafico.py     ← Puede usar config central
    └── ...
```

---

**Versión**: 1.0.0  
**Fecha**: 2025-11-05  
**Mantenedor**: Equipo OTIF Master

