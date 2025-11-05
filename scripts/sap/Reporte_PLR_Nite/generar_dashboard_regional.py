# -*- coding: utf-8 -*-
"""
Script: generar_dashboard_regional.py (Para Reporte PLR NITE)
Descripción:
  - Genera un dashboard completo por regiones (RURAL, GAM, VINOS, HA, CT01)
  - Incluye tablas zona x hora con heatmaps
  - Crea una imagen estilo Power BI lista para compartir
  - Adaptado para datos de PLR NITE
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Importar configuración centralizada de regiones
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from configuracion_regiones import (
        REGIONES_CONFIG,
        REGIONES_ORDEN,
        mapear_zona_a_region,
        obtener_color_region,
        obtener_nombre_region
    )
    print("[OK] Configuracion de regiones cargada correctamente")
except ImportError as e:
    print(f"[ADVERTENCIA] No se pudo importar configuracion_regiones: {e}")
    print("[INFO] Usando configuracion local")
    
    # Configuración local como fallback
    REGIONES_CONFIG = {
        'GAM': {'zonas': ['AL', 'CAR', 'CMN', 'CMT', 'COG', 'SJE', 'SJO', 'SUP', 'ZTO'], 'color': '#1565C0', 'nombre': 'GAM'},
        'RURAL': {'zonas': ['CNL', 'GUA', 'LIB', 'LIM', 'NIC', 'PUN', 'SCA', 'SIS', 'ZTL', 'ZTN', 'ZTP'], 'color': '#2E7D32', 'nombre': 'RURAL'},
        'CT01': {'zonas': ['SPE'], 'color': '#F57C00', 'nombre': 'CT01'},
        'CT02': {'zonas': ['VYD'], 'color': '#6A1B9A', 'nombre': 'CT02'}
    }
    REGIONES_ORDEN = ['RURAL', 'GAM', 'CT01', 'CT02']
    
    def mapear_zona_a_region(zona):
        if pd.isna(zona) or zona == '':
            return 'SIN_ZONA'
        zona_upper = str(zona).strip().upper()
        for region, config in REGIONES_CONFIG.items():
            if region != 'GAM' and zona_upper in config['zonas']:
                return region
        return 'GAM'

def leer_excel_procesado(xlsx_path: Path) -> pd.DataFrame:
    """Lee el archivo Excel procesado de PLR NITE"""
    try:
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        
        if df.empty:
            raise ValueError("El archivo Excel esta vacio")
        
        print(f"[INFO] Dimensiones del archivo: {df.shape[0]} filas x {df.shape[1]} columnas")
        
        # Intentar detectar columnas de zona
        # Para PLR_NITE, necesitas identificar qué columnas contienen zona/cedis
        # Ajustar según la estructura real de tu archivo
        
        # Por ahora, asumimos estructura similar a Monitor de Guías
        # Deberás ajustar estos índices según tus datos reales
        
        if len(df.columns) < 3:
            raise ValueError(f"El archivo tiene muy pocas columnas: {len(df.columns)}")
        
        # Intentar usar primera columna como zona (ajustar según necesidad)
        df['Zona'] = df.iloc[:, 0]  # Ajustar índice según tus datos
        
        # Si no hay columna de hora, crear una por defecto
        if len(df.columns) > 1:
            df['Hora'] = '12:00'  # Por defecto, ajustar si tienes columna de hora
        
        # Mapear zona a región
        df['Region'] = df['Zona'].apply(mapear_zona_a_region)
        df = df[df['Region'] != 'SIN_ZONA'].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas con zona valida")
        
        return df
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo Excel: {e}")

def crear_kpi_card(ax, titulo, valor, porcentaje, color):
    """Crea una tarjeta KPI"""
    ax.axis('off')
    
    rect = mpatches.FancyBboxPatch((0.05, 0.15), 0.9, 0.7,
                                    boxstyle="round,pad=0.08",
                                    facecolor=color, edgecolor='white',
                                    linewidth=3, alpha=0.9)
    ax.add_patch(rect)
    
    ax.text(0.5, 0.7, titulo, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white',
            transform=ax.transAxes)
    
    ax.text(0.5, 0.45, f'{valor:,}', ha='center', va='center',
            fontsize=20, fontweight='bold', color='white',
            transform=ax.transAxes)
    
    ax.text(0.5, 0.25, f'{porcentaje:.1f}%', ha='center', va='center',
            fontsize=12, color='white', style='italic',
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

def generar_dashboard(df: pd.DataFrame, output_path: Path):
    """Genera el dashboard completo para PLR NITE"""
    
    print("[PROCESO] Generando dashboard regional PLR NITE...")
    
    # Calcular estadísticas
    total_guias = len(df)
    stats_por_region = df.groupby('Region').size().to_dict()
    stats_por_zona = df.groupby(['Region', 'Zona']).size().reset_index(name='Cantidad')
    
    # Si hay columna de hora, calcular stats por hora
    if 'Hora' in df.columns:
        stats_por_hora = df.groupby(['Region', 'Hora']).size().reset_index(name='Cantidad')
        stats_zona_hora = df.groupby(['Region', 'Zona', 'Hora']).size().reset_index(name='Cantidad')
    else:
        stats_por_hora = pd.DataFrame()
        stats_zona_hora = pd.DataFrame()
    
    # Crear figura
    fig = plt.figure(figsize=(24, 20), dpi=120, facecolor='#f5f5f5')
    fig.suptitle('DASHBOARD PLR NITE - ANALISIS REGIONAL POR ZONA',
                 fontsize=24, fontweight='bold', y=0.995, color='#333')
    
    # Grid de subplots (4 regiones)
    gs = GridSpec(6, 4, figure=fig, hspace=0.6, wspace=0.4,
                  top=0.97, bottom=0.02, left=0.04, right=0.98)
    
    # ==================== FILA 1: KPIs ====================
    print("[GRAFICO] Generando KPIs principales...")
    
    for i, region in enumerate(REGIONES_ORDEN):
        ax = fig.add_subplot(gs[0, i])
        cantidad = stats_por_region.get(region, 0)
        porcentaje = (cantidad / total_guias * 100) if total_guias > 0 else 0
        color = REGIONES_CONFIG[region]['color']
        nombre = REGIONES_CONFIG[region]['nombre']
        crear_kpi_card(ax, nombre, cantidad, porcentaje, color)
    
    # ==================== FILA 2: TOTAL ====================
    ax_total = fig.add_subplot(gs[1, :])
    ax_total.axis('off')
    
    rect_total = mpatches.FancyBboxPatch((0.3, 0.2), 0.4, 0.6,
                                          boxstyle="round,pad=0.05",
                                          facecolor='#424242', edgecolor='white',
                                          linewidth=3, alpha=0.95)
    ax_total.add_patch(rect_total)
    ax_total.text(0.5, 0.7, 'TOTAL REGISTROS PROCESADOS', ha='center', va='center',
                  fontsize=16, fontweight='bold', color='white',
                  transform=ax_total.transAxes)
    ax_total.text(0.5, 0.35, f'{total_guias:,}', ha='center', va='center',
                  fontsize=32, fontweight='bold', color='#4CAF50',
                  transform=ax_total.transAxes)
    ax_total.set_xlim(0, 1)
    ax_total.set_ylim(0, 1)
    
    # ==================== FILAS 3-5: DISTRIBUCIÓN POR ZONA ====================
    print("[TABLA] Generando distribucion por zona...")
    
    # Función para crear gráfico de barras por zona
    def crear_grafico_zona(ax, region_name, df_region_data, color_region):
        if df_region_data.empty:
            ax.text(0.5, 0.5, f'No hay datos para {region_name}',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='gray')
            ax.axis('off')
            return
        
        df_sorted = df_region_data.sort_values('Cantidad', ascending=True)
        bars = ax.barh(df_sorted['Zona'], df_sorted['Cantidad'],
                      color=color_region, alpha=0.8)
        
        ax.set_title(f'{region_name} - Distribucion por Zona',
                    fontsize=14, fontweight='bold', pad=15, color='#333',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=color_region, alpha=0.3))
        ax.set_xlabel('Cantidad', fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Agregar valores
        for bar, val in zip(bars, df_sorted['Cantidad']):
            ax.text(val, bar.get_y() + bar.get_height()/2.,
                   f' {val:,}', ha='left', va='center',
                   fontsize=10, fontweight='bold')
    
    # RURAL
    ax_rural = fig.add_subplot(gs[2, :2])
    datos_rural = stats_por_zona[stats_por_zona['Region'] == 'RURAL']
    crear_grafico_zona(ax_rural, 'RURAL', datos_rural, REGIONES_CONFIG['RURAL']['color'])
    
    # GAM (Top 15)
    ax_gam = fig.add_subplot(gs[2, 2:])
    datos_gam = stats_por_zona[stats_por_zona['Region'] == 'GAM'].sort_values('Cantidad', ascending=False).head(15)
    crear_grafico_zona(ax_gam, 'GAM (Top 15)', datos_gam, REGIONES_CONFIG['GAM']['color'])
    
    # CT01 y CT02
    otras_regiones = ['CT01', 'CT02']
    for i, region in enumerate(otras_regiones):
        ax = fig.add_subplot(gs[3, i*2:(i*2)+2])
        datos_region = stats_por_zona[stats_por_zona['Region'] == region]
        crear_grafico_zona(ax, REGIONES_CONFIG[region]['nombre'], 
                          datos_region, REGIONES_CONFIG[region]['color'])
    
    # ==================== FILA 6: COMPARATIVO ====================
    print("[GRAFICO] Generando comparativo global...")
    
    ax_comparativo = fig.add_subplot(gs[4:, :])
    
    regiones_vals = []
    regiones_labels = []
    regiones_colors = []
    
    for region in REGIONES_ORDEN:
        cant = stats_por_region.get(region, 0)
        if cant > 0:
            regiones_vals.append(cant)
            regiones_labels.append(REGIONES_CONFIG[region]['nombre'])
            regiones_colors.append(REGIONES_CONFIG[region]['color'])
    
    if regiones_vals:
        x_pos = np.arange(len(regiones_labels))
        bars = ax_comparativo.bar(x_pos, regiones_vals, color=regiones_colors, alpha=0.85, width=0.6)
        
        ax_comparativo.set_title('COMPARATIVO GENERAL - Todas las Regiones',
                                fontsize=16, fontweight='bold', pad=20, color='#333')
        ax_comparativo.set_ylabel('Cantidad de Registros', fontsize=12, fontweight='bold')
        ax_comparativo.set_xticks(x_pos)
        ax_comparativo.set_xticklabels(regiones_labels, fontsize=12, fontweight='bold')
        ax_comparativo.grid(axis='y', alpha=0.3, linestyle='--')
        
        for i, (bar, val) in enumerate(zip(bars, regiones_vals)):
            height = bar.get_height()
            porcentaje = (val / total_guias * 100) if total_guias > 0 else 0
            ax_comparativo.text(bar.get_x() + bar.get_width()/2., height,
                               f'{val:,}\n({porcentaje:.1f}%)',
                               ha='center', va='bottom',
                               fontsize=11, fontweight='bold')
    
    # Fecha de generación
    fecha_gen = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.99, 0.005, f'Generado: {fecha_gen}',
             ha='right', va='bottom', fontsize=9, style='italic', color='#666',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    # Guardar
    print(f"[GUARDANDO] Guardando dashboard en: {output_path}")
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='#f5f5f5', edgecolor='none')
    plt.close()
    
    print(f"[OK] Dashboard guardado exitosamente")
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Genera dashboard regional para PLR NITE')
    parser.add_argument('--archivo', required=True, help='Ruta al archivo Excel procesado')
    parser.add_argument('--output', help='Ruta de salida para la imagen (opcional)')
    
    args = parser.parse_args()
    
    archivo_excel = Path(args.archivo)
    if not archivo_excel.exists():
        print(f"[ERROR] No se encontro el archivo: {archivo_excel}")
        return 1
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = archivo_excel.parent / f"dashboard_regional_plr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    try:
        print("=" * 70)
        print("[INICIO] Generacion de Dashboard Regional PLR NITE")
        print("=" * 70)
        
        df = leer_excel_procesado(archivo_excel)
        print(f"[OK] Datos cargados: {len(df)} registros")
        
        resultado = generar_dashboard(df, output_path)
        
        print("=" * 70)
        print("[EXITO] Dashboard generado exitosamente")
        print("=" * 70)
        print(f"[ARCHIVO] {resultado}")
        print(f"[TAMAÑO] {resultado.stat().st_size / 1024:.1f} KB")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error al generar dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

