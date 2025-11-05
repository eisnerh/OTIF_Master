# -*- coding: utf-8 -*-
"""
Script: generar_dashboard_regional.py
Descripción:
  - Genera un dashboard completo por regiones (RURAL, GAM, VINOS, HA)
  - Incluye gráficos segmentados por zona
  - Crea una imagen estilo Power BI lista para compartir
  - Incluye KPIs, tendencias y distribución por zona
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
import sys
from pathlib import Path
# Agregar carpeta padre al path para importar configuracion_regiones
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
    print(f"[ERROR] No se pudo importar configuracion_regiones: {e}")
    print("[INFO] Usando configuracion local como fallback")
    
    # Configuración local como fallback
    REGIONES_CONFIG = {
        'GAM': {
            'zonas': ['ALJ', 'CAR', 'CMN', 'CMT', 'COG', 'SJE', 'SJO', 'SUP', 'ZTO'],
            'color': '#1565C0',
            'nombre': 'GAM'
        },
        'RURAL': {
            'zonas': ['CNL', 'GUA', 'LIB', 'LIM', 'NIC', 'PUN', 'SCA', 'SIS', 'ZTL', 'ZTN', 'ZTP'],
            'color': '#2E7D32',
            'nombre': 'RURAL'
        },
        'CT01': {
            'zonas': ['SPE'],
            'color': '#F57C00',
            'nombre': 'CT01'
        },
        'CT02': {
            'zonas': ['VYD'],
            'color': '#6A1B9A',
            'nombre': 'CT02'
        }
    }
    REGIONES_ORDEN = ['RURAL', 'GAM', 'CT01', 'CT02']
    
    def mapear_zona_a_region(zona: str) -> str:
        """Mapea una zona a su región correspondiente"""
        if pd.isna(zona) or zona == '':
            return 'SIN_ZONA'
        zona_upper = str(zona).strip().upper()
        for region, config in REGIONES_CONFIG.items():
            if zona_upper in config['zonas']:
                return region
        return 'GAM'

def leer_excel_procesado(xlsx_path: Path) -> pd.DataFrame:
    """Lee el archivo Excel procesado y prepara los datos"""
    try:
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        
        if df.empty:
            raise ValueError("El archivo Excel está vacío")
        
        if len(df.columns) < 9:
            raise ValueError(f"El archivo tiene menos de 9 columnas. Columnas encontradas: {len(df.columns)}")
        
        # Columnas importantes
        columna_zona_idx = 1  # Columna B
        columna_hora_idx = 8  # Columna I
        columna_viaje_idx = 5  # Columna F
        
        # Extraer zona
        df['Zona'] = df.iloc[:, columna_zona_idx]
        
        # Extraer hora
        import re
        def extraer_hora(val):
            if pd.isna(val):
                return None
            val_str = str(val).strip()
            if not val_str or val_str == 'nan':
                return None
            
            try:
                dt = pd.to_datetime(val_str, errors='coerce')
                if pd.notna(dt):
                    return dt.strftime('%H:00')
            except:
                pass
            
            match = re.search(r'(\d{1,2}):(\d{2})', val_str)
            if match:
                hora = int(match.group(1))
                if 0 <= hora <= 23:
                    return f"{hora:02d}:00"
            return None
        
        df['Hora'] = df.iloc[:, columna_hora_idx].apply(extraer_hora)
        df = df[df['Hora'].notna()].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas con hora válida")
        
        # Filtro columna F: solo valores que inicien con '1'
        columna_f = df.iloc[:, columna_viaje_idx]
        df = df[columna_f.apply(lambda val: str(val).strip().startswith('1') if pd.notna(val) else False)].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas donde la columna F inicie con '1'")
        
        # Mapear zona a región
        df['Region'] = df['Zona'].apply(mapear_zona_a_region)
        df = df[df['Region'] != 'SIN_ZONA'].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas con zona válida")
        
        return df
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo Excel: {e}")

def crear_kpi_card(ax, titulo, valor, porcentaje, color):
    """Crea una tarjeta KPI"""
    ax.axis('off')
    
    # Rectángulo de fondo
    rect = mpatches.FancyBboxPatch((0.05, 0.15), 0.9, 0.7,
                                    boxstyle="round,pad=0.08",
                                    facecolor=color, edgecolor='white',
                                    linewidth=3, alpha=0.9)
    ax.add_patch(rect)
    
    # Título
    ax.text(0.5, 0.7, titulo, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white',
            transform=ax.transAxes)
    
    # Valor
    ax.text(0.5, 0.45, f'{valor:,}', ha='center', va='center',
            fontsize=20, fontweight='bold', color='white',
            transform=ax.transAxes)
    
    # Porcentaje
    ax.text(0.5, 0.25, f'{porcentaje:.1f}%', ha='center', va='center',
            fontsize=12, color='white', style='italic',
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

def generar_dashboard(df: pd.DataFrame, output_path: Path):
    """Genera el dashboard completo"""
    
    print("[PROCESO] Generando dashboard regional...")
    
    # Calcular estadísticas
    total_guias = len(df)
    stats_por_region = df.groupby('Region').size().to_dict()
    stats_por_zona = df.groupby(['Region', 'Zona']).size().reset_index(name='Cantidad')
    stats_por_hora = df.groupby(['Region', 'Hora']).size().reset_index(name='Cantidad')
    
    # Crear matriz de zona x hora por región
    stats_zona_hora = df.groupby(['Region', 'Zona', 'Hora']).size().reset_index(name='Cantidad')
    
    # Crear figura (optimizada para tablas)
    fig = plt.figure(figsize=(24, 28), dpi=120, facecolor='#f5f5f5')
    fig.suptitle('DASHBOARD MONITOR DE GUIAS - ANALISIS REGIONAL POR ZONA',
                 fontsize=24, fontweight='bold', y=0.995, color='#333')
    
    # Crear grid de subplots (4 regiones)
    gs = GridSpec(7, 4, figure=fig, hspace=0.6, wspace=0.4,
                  top=0.97, bottom=0.02, left=0.04, right=0.98)
    
    # ==================== FILA 1: KPIs PRINCIPALES ====================
    print("[GRAFICO] Generando KPIs principales...")
    
    # Usar solo las 4 regiones reales
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
    ax_total.text(0.5, 0.7, 'TOTAL GUIAS PROCESADAS', ha='center', va='center',
                  fontsize=16, fontweight='bold', color='white',
                  transform=ax_total.transAxes)
    ax_total.text(0.5, 0.35, f'{total_guias:,}', ha='center', va='center',
                  fontsize=32, fontweight='bold', color='#4CAF50',
                  transform=ax_total.transAxes)
    ax_total.set_xlim(0, 1)
    ax_total.set_ylim(0, 1)
    
    # ==================== FILAS 7-11: TABLAS ZONA x HORA POR REGIÓN ====================
    print("[TABLA] Generando tablas zona x hora por region...")
    
    # Función para crear tabla heatmap
    def crear_tabla_heatmap(ax, region_name, df_region_data, color_region):
        """Crea una tabla heatmap de zona x hora"""
        if df_region_data.empty:
            ax.text(0.5, 0.5, f'No hay datos para {region_name}',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='gray')
            ax.axis('off')
            return
        
        # Crear pivot table: zonas en filas, horas en columnas
        pivot_table = df_region_data.pivot_table(
            values='Cantidad',
            index='Zona',
            columns='Hora',
            fill_value=0,
            aggfunc='sum'
        )
        
        # Ordenar columnas (horas)
        try:
            cols_ordenadas = sorted(pivot_table.columns, key=lambda h: int(h.split(':')[0]))
            pivot_table = pivot_table[cols_ordenadas]
        except:
            pass
        
        # Ordenar filas (zonas) por total descendente
        pivot_table['Total'] = pivot_table.sum(axis=1)
        pivot_table = pivot_table.sort_values('Total', ascending=False)
        pivot_table_sin_total = pivot_table.drop('Total', axis=1)
        
        # Crear heatmap
        sns.heatmap(pivot_table_sin_total, annot=True, fmt='.0f', cmap='YlOrRd',
                   cbar_kws={'label': 'Cantidad de Guías'},
                   linewidths=0.5, linecolor='white',
                   ax=ax, vmin=0, square=False)
        
        ax.set_title(f'{region_name} - Distribución por Zona y Hora',
                    fontsize=14, fontweight='bold', pad=15, color='#333',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=color_region, alpha=0.3))
        ax.set_xlabel('Hora del Día', fontsize=11, fontweight='bold')
        ax.set_ylabel('Zona', fontsize=11, fontweight='bold')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        plt.setp(ax.get_yticklabels(), rotation=0, fontsize=9)
    
    # ==================== FILAS 3-7: TABLAS ZONA x HORA POR REGIÓN ====================
    print("[TABLA] Generando tablas zona x hora por region...")
    
    # Función para crear tabla heatmap
    def crear_tabla_heatmap(ax, region_name, df_region_data, color_region):
        """Crea una tabla heatmap de zona x hora"""
        if df_region_data.empty:
            ax.text(0.5, 0.5, f'No hay datos para {region_name}',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='gray')
            ax.axis('off')
            return
        
        # Crear pivot table: zonas en filas, horas en columnas
        pivot_table = df_region_data.pivot_table(
            values='Cantidad',
            index='Zona',
            columns='Hora',
            fill_value=0,
            aggfunc='sum'
        )
        
        # Ordenar columnas (horas)
        try:
            cols_ordenadas = sorted(pivot_table.columns, key=lambda h: int(h.split(':')[0]))
            pivot_table = pivot_table[cols_ordenadas]
        except:
            pass
        
        # Ordenar filas (zonas) por total descendente
        pivot_table['Total'] = pivot_table.sum(axis=1)
        pivot_table = pivot_table.sort_values('Total', ascending=False)
        pivot_table_sin_total = pivot_table.drop('Total', axis=1)
        
        # Crear heatmap
        sns.heatmap(pivot_table_sin_total, annot=True, fmt='.0f', cmap='YlOrRd',
                   cbar_kws={'label': 'Cantidad de Guias'},
                   linewidths=0.5, linecolor='white',
                   ax=ax, vmin=0, square=False, cbar=True)
        
        ax.set_title(f'{region_name} - Distribucion por Zona y Hora',
                    fontsize=14, fontweight='bold', pad=15, color='#333',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=color_region, alpha=0.3))
        ax.set_xlabel('Hora del Dia', fontsize=11, fontweight='bold')
        ax.set_ylabel('Zona', fontsize=11, fontweight='bold')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        plt.setp(ax.get_yticklabels(), rotation=0, fontsize=9)
    
    # RURAL - Tabla (filas 3-4)
    ax_rural_tabla = fig.add_subplot(gs[2:4, :])
    datos_rural_tabla = stats_zona_hora[stats_zona_hora['Region'] == 'RURAL']
    crear_tabla_heatmap(ax_rural_tabla, 'RURAL', datos_rural_tabla, REGIONES_CONFIG['RURAL']['color'])
    
    # GAM - Tabla (filas 5-6)
    ax_gam_tabla = fig.add_subplot(gs[4:6, :])
    datos_gam_tabla = stats_zona_hora[stats_zona_hora['Region'] == 'GAM']
    # Limitar a top 15 zonas para que quepa
    if not datos_gam_tabla.empty:
        top_zonas_gam = datos_gam_tabla.groupby('Zona')['Cantidad'].sum().nlargest(15).index
        datos_gam_tabla = datos_gam_tabla[datos_gam_tabla['Zona'].isin(top_zonas_gam)]
    crear_tabla_heatmap(ax_gam_tabla, 'GAM (Top 15 Zonas)', datos_gam_tabla, REGIONES_CONFIG['GAM']['color'])
    
    # CT01 - Tabla (fila 7 - izquierda)
    ax_ct01_tabla = fig.add_subplot(gs[6, :2])
    datos_ct01_tabla = stats_zona_hora[stats_zona_hora['Region'] == 'CT01']
    crear_tabla_heatmap(ax_ct01_tabla, REGIONES_CONFIG['CT01']['nombre'], 
                       datos_ct01_tabla, REGIONES_CONFIG['CT01']['color'])
    
    # CT02 - Tabla (fila 7 - derecha)
    ax_ct02_tabla = fig.add_subplot(gs[6, 2:])
    datos_ct02_tabla = stats_zona_hora[stats_zona_hora['Region'] == 'CT02']
    crear_tabla_heatmap(ax_ct02_tabla, REGIONES_CONFIG['CT02']['nombre'], 
                       datos_ct02_tabla, REGIONES_CONFIG['CT02']['color'])
    
    # ==================== FILA 8: COMPARATIVO TODAS LAS REGIONES ====================
    print("[GRAFICO] Generando comparativo global...")
    
    ax_comparativo = fig.add_subplot(gs[5, :])
    
    # Preparar datos para comparativo
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
        # Gráfico de barras comparativo
        x_pos = np.arange(len(regiones_labels))
        bars = ax_comparativo.bar(x_pos, regiones_vals, color=regiones_colors, alpha=0.85, width=0.6)
        
        ax_comparativo.set_title('COMPARATIVO GENERAL - Todas las Regiones',
                                fontsize=16, fontweight='bold', pad=20, color='#333')
        ax_comparativo.set_ylabel('Cantidad de Guías', fontsize=12, fontweight='bold')
        ax_comparativo.set_xticks(x_pos)
        ax_comparativo.set_xticklabels(regiones_labels, fontsize=12, fontweight='bold')
        ax_comparativo.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Agregar valores y porcentajes
        for i, (bar, val) in enumerate(zip(bars, regiones_vals)):
            height = bar.get_height()
            porcentaje = (val / total_guias * 100) if total_guias > 0 else 0
            ax_comparativo.text(bar.get_x() + bar.get_width()/2., height,
                               f'{val:,}\n({porcentaje:.1f}%)',
                               ha='center', va='bottom',
                               fontsize=11, fontweight='bold')
    
    # Agregar fecha y hora de generación
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
    parser = argparse.ArgumentParser(description='Genera dashboard regional por zonas')
    parser.add_argument('--archivo', required=True, help='Ruta al archivo Excel procesado')
    parser.add_argument('--output', help='Ruta de salida para la imagen (opcional)')
    
    args = parser.parse_args()
    
    # Verificar que existe el archivo
    archivo_excel = Path(args.archivo)
    if not archivo_excel.exists():
        print(f"[ERROR] No se encontro el archivo: {archivo_excel}")
        return 1
    
    # Determinar ruta de salida
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = archivo_excel.parent / f"dashboard_regional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    try:
        print("=" * 70)
        print("[INICIO] Generacion de Dashboard Regional por Zonas")
        print("=" * 70)
        
        # Leer datos
        df = leer_excel_procesado(archivo_excel)
        print(f"[OK] Datos cargados: {len(df)} guias")
        
        # Generar dashboard
        resultado = generar_dashboard(df, output_path)
        
        print("=" * 70)
        print("[EXITO] Dashboard generado exitosamente")
        print("=" * 70)
        print(f"[ARCHIVO] {resultado}")
        print(f"[TAMAÑO] {resultado.stat().st_size / 1024:.1f} KB")
        print("=" * 70)
        print("")
        print("El dashboard esta listo para compartir!")
        print("")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error al generar dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

