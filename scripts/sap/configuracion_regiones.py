# -*- coding: utf-8 -*-
"""
Configuración centralizada de regiones y zonas
----------------------------------------------
Este archivo define la segmentación de zonas por regiones
para todos los reportes del sistema OTIF Master.

Se importa desde todos los scripts para mantener consistencia.
"""

# Configuración de regiones y sus zonas (actualizada según datos reales)
REGIONES_CONFIG = {
    'GAM': {
        'zonas': ['ALJ', 'CAR', 'CMN', 'CMT', 'COG', 'SJE', 'SJO', 'SUP', 'ZTO'],
        'color': '#1565C0',  # Azul
        'nombre': 'GAM',
        'descripcion': 'Gran Area Metropolitana'
    },
    'RURAL': {
        'zonas': ['CNL', 'GUA', 'LIB', 'LIM', 'NIC', 'PUN', 'SCA', 'SIS', 'ZTL', 'ZTN', 'ZTP'],
        'color': '#2E7D32',  # Verde
        'nombre': 'RURAL',
        'descripcion': 'Zonas rurales'
    },
    'CT01': {
        'zonas': ['SPE'],
        'color': '#F57C00',  # Naranja (antes era HA)
        'nombre': 'CT01',
        'descripcion': 'Centro 01 - San Pedro'
    },
    'CT02': {
        'zonas': ['VYD'],
        'color': '#6A1B9A',  # Púrpura
        'nombre': 'CT02',
        'descripcion': 'Centro 02 - Vinos'
    }
}

# Listas simples para compatibilidad con scripts antiguos
ZONAS_RURAL = REGIONES_CONFIG['RURAL']['zonas']
ZONAS_GAM = REGIONES_CONFIG['GAM']['zonas']
ZONAS_CT02 = REGIONES_CONFIG['CT02']['zonas']  # Antes VINOS
ZONA_CT01 = REGIONES_CONFIG['CT01']['zonas'][0]  # SPE

# Alias para compatibilidad
ZONAS_VINOS = ZONAS_CT02  # Alias
ZONA_HA = ZONA_CT01       # Alias (antes SPE era HA, ahora es CT01)

# Orden de regiones para reportes
REGIONES_ORDEN = ['RURAL', 'GAM', 'CT01', 'CT02']

def mapear_zona_a_region(zona: str) -> str:
    """
    Mapea una zona individual a su región correspondiente.
    
    Args:
        zona: Código de zona (ej: 'GUA', 'VYD', 'SPE', 'AL')
    
    Returns:
        Región a la que pertenece: 'RURAL', 'GAM', 'CT01', 'CT02', o 'SIN_ZONA'
    """
    import pandas as pd
    
    if pd.isna(zona) or zona == '':
        return 'SIN_ZONA'
    
    zona_upper = str(zona).strip().upper()
    
    # Verificar cada región
    for region_key, region_config in REGIONES_CONFIG.items():
        if zona_upper in region_config['zonas']:
            return region_key
    
    # Si no está en ninguna región, retornar SIN_ZONA
    # (ya no usamos GAM como fallback)
    return 'SIN_ZONA'

def obtener_color_region(region: str) -> str:
    """Obtiene el color asociado a una región"""
    return REGIONES_CONFIG.get(region, {}).get('color', '#666666')

def obtener_nombre_region(region: str) -> str:
    """Obtiene el nombre display de una región"""
    return REGIONES_CONFIG.get(region, {}).get('nombre', region)

def obtener_todas_zonas_de_region(region: str) -> list:
    """Obtiene la lista de zonas de una región específica"""
    return REGIONES_CONFIG.get(region, {}).get('zonas', [])

def listar_regiones() -> list:
    """Retorna la lista ordenada de regiones"""
    return REGIONES_ORDEN

def obtener_info_region(region: str) -> dict:
    """Obtiene toda la información de una región"""
    return REGIONES_CONFIG.get(region, {})

# Para compatibilidad con scripts antiguos que usan mapear_zona()
def mapear_zona(zona: str) -> str:
    """Alias para compatibilidad con scripts antiguos"""
    return mapear_zona_a_region(zona)

if __name__ == "__main__":
    # Prueba del módulo
    print("=" * 60)
    print("Configuracion de Regiones y Zonas")
    print("=" * 60)
    
    for region in REGIONES_ORDEN:
        config = REGIONES_CONFIG[region]
        print(f"\n{config['nombre']} ({region}):")
        print(f"  Color: {config['color']}")
        print(f"  Descripcion: {config['descripcion']}")
        if config['zonas']:
            print(f"  Zonas ({len(config['zonas'])}): {', '.join(config['zonas'])}")
        else:
            print(f"  Zonas: [Todas las demas]")
    
    print("\n" + "=" * 60)
    print("Pruebas de mapeo:")
    print("=" * 60)
    
    zonas_prueba = ['GUA', 'VYD', 'SPE', 'AL', 'ZXY', 'NIC', 'SJO', 'CAR']
    for zona in zonas_prueba:
        region = mapear_zona_a_region(zona)
        color = obtener_color_region(region)
        print(f"  {zona:10s} -> {region:10s} ({color})")
    
    print("\n" + "=" * 60)

