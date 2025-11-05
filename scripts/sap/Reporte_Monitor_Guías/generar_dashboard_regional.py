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

# Configuración de zonas por región
REGIONES_CONFIG = {
    'RURAL': {
        'zonas': ['GUA', 'NIC', 'PUN', 'SCA', 'CNL', 'LIM', 'LIB', 'SIS', 'ZTP', 'ZTN', 'ZTL'],
        'color': '#2E7D32',  # Verde
        'nombre': 'RURAL'
    },
    'GAM': {
        'zonas': ['ALJ', 'CAR', 'CMN', 'CMT', 'COG', 'SJE', 'SJO', 'SUP', 'ZTO'],  # Se llenará con zonas que no sean de otras regiones
        'color': '#1565C0',  # Azul
        'nombre': 'GAM'
    },
    'VINOS': {
        'zonas': ['VYD'],
        'color': '#6A1B9A',  # Púrpura
        'nombre': 'VINOS (CT02)'
    },
    'HA': {
        'zonas': ['SPE'],
        'color': '#F57C00',  # Naranja
        'nombre': 'HA (SPE)'
    }
}

def mapear_zona_a_region(zona: str) -> str:
    """Mapea una zona a su región correspondiente"""
    if pd.isna(zona) or zona == '':
        return 'SIN_ZONA'
    
    zona_upper = str(zona).strip().upper()
    
    # Verificar cada región
    for region, config in REGIONES_CONFIG.items():
        if zona_upper in config['zonas']:
            return region
    
    # Si no está en ninguna región específica, es GAM
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
    
    # Crear figura
    fig = plt.figure(figsize=(20, 28), dpi=120, facecolor='#f5f5f5')
    fig.suptitle('DASHBOARD MONITOR DE GUIAS - ANALISIS REGIONAL POR ZONA',
                 fontsize=24, fontweight='bold', y=0.995, color='#333')
    
    # Crear grid de subplots
    gs = GridSpec(7, 5, figure=fig, hspace=0.5, wspace=0.4,
                  top=0.97, bottom=0.02, left=0.04, right=0.98)
    
    # ==================== FILA 1: KPIs PRINCIPALES ====================
    print("[GRAFICO] Generando KPIs principales...")
    
    regiones_orden = ['RURAL', 'GAM', 'VINOS', 'HA']
    for i, region in enumerate(regiones_orden):
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
    
    # ==================== FILA 3: DISTRIBUCIÓN POR ZONA - RURAL y GAM ====================
    print("[GRAFICO] Generando distribución por zona...")
    
    # RURAL - Distribución por zona
    ax_rural_zonas = fig.add_subplot(gs[2, :3])
    datos_rural = stats_por_zona[stats_por_zona['Region'] == 'RURAL'].sort_values('Cantidad', ascending=False)
    
    if not datos_rural.empty:
        bars = ax_rural_zonas.barh(datos_rural['Zona'], datos_rural['Cantidad'],
                                    color=REGIONES_CONFIG['RURAL']['color'], alpha=0.8)
        ax_rural_zonas.set_title('RURAL - Distribución por Zona',
                                 fontsize=14, fontweight='bold', pad=15, color='#333')
        ax_rural_zonas.set_xlabel('Cantidad de Guías', fontsize=11, fontweight='bold')
        ax_rural_zonas.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Agregar valores
        for i, (bar, val) in enumerate(zip(bars, datos_rural['Cantidad'])):
            ax_rural_zonas.text(val, bar.get_y() + bar.get_height()/2.,
                               f' {val:,}', ha='left', va='center',
                               fontsize=10, fontweight='bold')
    else:
        ax_rural_zonas.text(0.5, 0.5, 'No hay datos', ha='center', va='center',
                           transform=ax_rural_zonas.transAxes, fontsize=14)
    
    # GAM - Distribución por zona (top zonas)
    ax_gam_zonas = fig.add_subplot(gs[2, 3:])
    datos_gam = stats_por_zona[stats_por_zona['Region'] == 'GAM'].sort_values('Cantidad', ascending=False).head(10)
    
    if not datos_gam.empty:
        bars = ax_gam_zonas.barh(datos_gam['Zona'], datos_gam['Cantidad'],
                                 color=REGIONES_CONFIG['GAM']['color'], alpha=0.8)
        ax_gam_zonas.set_title('GAM - Top 10 Zonas',
                              fontsize=14, fontweight='bold', pad=15, color='#333')
        ax_gam_zonas.set_xlabel('Cantidad de Guías', fontsize=11, fontweight='bold')
        ax_gam_zonas.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Agregar valores
        for i, (bar, val) in enumerate(zip(bars, datos_gam['Cantidad'])):
            ax_gam_zonas.text(val, bar.get_y() + bar.get_height()/2.,
                             f' {val:,}', ha='left', va='center',
                             fontsize=10, fontweight='bold')
    else:
        ax_gam_zonas.text(0.5, 0.5, 'No hay datos', ha='center', va='center',
                         transform=ax_gam_zonas.transAxes, fontsize=14)
    
    # ==================== FILA 4: TENDENCIA POR HORA - RURAL ====================
    print("[GRAFICO] Generando tendencias por hora...")
    
    ax_rural_hora = fig.add_subplot(gs[3, :])
    datos_rural_hora = stats_por_hora[stats_por_hora['Region'] == 'RURAL'].copy()
    
    if not datos_rural_hora.empty:
        # Ordenar por hora
        horas_orden = sorted(datos_rural_hora['Hora'].unique(), key=lambda h: int(h.split(':')[0]))
        datos_rural_hora['Hora'] = pd.Categorical(datos_rural_hora['Hora'], categories=horas_orden, ordered=True)
        datos_rural_hora = datos_rural_hora.sort_values('Hora')
        
        ax_rural_hora.plot(datos_rural_hora['Hora'], datos_rural_hora['Cantidad'],
                          marker='o', linewidth=3, markersize=10,
                          color=REGIONES_CONFIG['RURAL']['color'], label='RURAL')
        ax_rural_hora.fill_between(datos_rural_hora['Hora'], datos_rural_hora['Cantidad'],
                                   alpha=0.3, color=REGIONES_CONFIG['RURAL']['color'])
        
        # Agregar valores en puntos clave
        for _, row in datos_rural_hora.iterrows():
            ax_rural_hora.text(row['Hora'], row['Cantidad'], f" {int(row['Cantidad'])}",
                              fontsize=9, ha='left', va='bottom', fontweight='bold')
        
        ax_rural_hora.set_title('RURAL - Tendencia de Guías por Hora',
                               fontsize=14, fontweight='bold', pad=15, color='#333')
        ax_rural_hora.set_xlabel('Hora', fontsize=11, fontweight='bold')
        ax_rural_hora.set_ylabel('Cantidad de Guías', fontsize=11, fontweight='bold')
        ax_rural_hora.grid(True, alpha=0.3, linestyle='--')
        plt.setp(ax_rural_hora.xaxis.get_majorticklabels(), rotation=45, ha='right')
    else:
        ax_rural_hora.text(0.5, 0.5, 'No hay datos RURAL', ha='center', va='center',
                          transform=ax_rural_hora.transAxes, fontsize=14)
    
    # ==================== FILA 5: TENDENCIA POR HORA - GAM ====================
    ax_gam_hora = fig.add_subplot(gs[4, :])
    datos_gam_hora = stats_por_hora[stats_por_hora['Region'] == 'GAM'].copy()
    
    if not datos_gam_hora.empty:
        # Ordenar por hora
        horas_orden = sorted(datos_gam_hora['Hora'].unique(), key=lambda h: int(h.split(':')[0]))
        datos_gam_hora['Hora'] = pd.Categorical(datos_gam_hora['Hora'], categories=horas_orden, ordered=True)
        datos_gam_hora = datos_gam_hora.sort_values('Hora')
        
        ax_gam_hora.plot(datos_gam_hora['Hora'], datos_gam_hora['Cantidad'],
                        marker='s', linewidth=3, markersize=10,
                        color=REGIONES_CONFIG['GAM']['color'], label='GAM')
        ax_gam_hora.fill_between(datos_gam_hora['Hora'], datos_gam_hora['Cantidad'],
                                alpha=0.3, color=REGIONES_CONFIG['GAM']['color'])
        
        # Agregar valores en puntos clave
        for _, row in datos_gam_hora.iterrows():
            ax_gam_hora.text(row['Hora'], row['Cantidad'], f" {int(row['Cantidad'])}",
                            fontsize=9, ha='left', va='bottom', fontweight='bold')
        
        ax_gam_hora.set_title('GAM - Tendencia de Guías por Hora',
                             fontsize=14, fontweight='bold', pad=15, color='#333')
        ax_gam_hora.set_xlabel('Hora', fontsize=11, fontweight='bold')
        ax_gam_hora.set_ylabel('Cantidad de Guías', fontsize=11, fontweight='bold')
        ax_gam_hora.grid(True, alpha=0.3, linestyle='--')
        plt.setp(ax_gam_hora.xaxis.get_majorticklabels(), rotation=45, ha='right')
    else:
        ax_gam_hora.text(0.5, 0.5, 'No hay datos GAM', ha='center', va='center',
                        transform=ax_gam_hora.transAxes, fontsize=14)
    
    # ==================== FILA 6: OTRAS REGIONES ====================
    print("[GRAFICO] Generando gráficos de otras regiones...")
    
    otras_regiones = ['VINOS', 'HA', 'CT01']
    for i, region in enumerate(otras_regiones):
        ax = fig.add_subplot(gs[5, i])
        datos_region = stats_por_zona[stats_por_zona['Region'] == region]
        
        if not datos_region.empty:
            # Si tiene zonas, mostrar barras
            bars = ax.bar(datos_region['Zona'], datos_region['Cantidad'],
                         color=REGIONES_CONFIG[region]['color'], alpha=0.8)
            ax.set_title(f'{REGIONES_CONFIG[region]["nombre"]} - Por Zona',
                        fontsize=12, fontweight='bold', pad=10, color='#333')
            ax.set_ylabel('Cantidad', fontsize=10, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
            
            # Agregar valores
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom',
                       fontsize=10, fontweight='bold')
        else:
            ax.text(0.5, 0.5, f'No hay datos\n{region}', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, color='gray')
            ax.axis('off')
    
    # ==================== FILA 7: COMPARATIVO TODAS LAS REGIONES ====================
    print("[GRAFICO] Generando comparativo global...")
    
    ax_comparativo = fig.add_subplot(gs[6, :])
    
    # Preparar datos para comparativo
    regiones_vals = []
    regiones_labels = []
    regiones_colors = []
    
    for region in regiones_orden:
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

