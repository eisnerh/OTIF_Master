# -*- coding: utf-8 -*-
"""
Script: generar_dashboard_regional.py
Descripción:
  - Genera un dashboard estilo "Tablero de Monitor de Guías"
  - Incluye KPIs, tabla detallada zona x hora, resumen por región y gráfico de tendencias
  - Formato exacto según especificaciones
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
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Importar configuración centralizada de regiones
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from configuracion_regiones import (
        REGIONES_CONFIG, 
        REGIONES_ORDEN,
        mapear_zona_a_region
    )
    print("[OK] Configuracion de regiones cargada correctamente")
except ImportError as e:
    print(f"[ERROR] No se pudo importar configuracion_regiones: {e}")
    print("[INFO] Usando configuracion local como fallback")
    
    REGIONES_CONFIG = {
        'GAM': {'zonas': ['ALJ', 'CAR', 'CMN', 'CMT', 'COG', 'SJE', 'SJO', 'SUP', 'ZTO'], 'color': '#1565C0', 'nombre': 'GAM'},
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
            if zona_upper in config['zonas']:
                return region
        return 'SIN_ZONA'

def leer_excel_procesado(xlsx_path: Path) -> pd.DataFrame:
    """Lee el archivo Excel procesado y prepara los datos"""
    try:
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        
        if df.empty:
            raise ValueError("El archivo Excel está vacío")
        
        if len(df.columns) < 9:
            raise ValueError(f"El archivo tiene menos de 9 columnas. Columnas encontradas: {len(df.columns)}")
        
        # Columnas: B=zona (idx 1), I=hora (idx 8), F=viaje (idx 5)
        columna_zona_idx = 1
        columna_hora_idx = 8
        columna_viaje_idx = 5
        
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

def generar_dashboard(df: pd.DataFrame, output_path: Path):
    """Genera el dashboard estilo Tablero de Monitor de Guías"""
    
    print("[PROCESO] Generando dashboard Tablero de Monitor de Guias...")
    
    # Calcular estadísticas
    total_guias = len(df)
    stats_por_region = df.groupby('Region').size().to_dict()
    
    # Crear matriz zona x hora
    stats_zona_hora = df.groupby(['Region', 'Zona', 'Hora']).size().reset_index(name='Cantidad')
    
    # Crear pivot table completa
    pivot_detallado = stats_zona_hora.pivot_table(
        values='Cantidad',
        index=['Region', 'Zona'],
        columns='Hora',
        fill_value=0,
        aggfunc='sum'
    )
    
    # Ordenar columnas (horas)
    try:
        cols_ordenadas = sorted(pivot_detallado.columns, key=lambda h: int(h.split(':')[0]))
        pivot_detallado = pivot_detallado[cols_ordenadas]
    except:
        pass
    
    # Crear pivot por región (resumen)
    pivot_region = stats_zona_hora.groupby(['Region', 'Hora'])['Cantidad'].sum().reset_index()
    pivot_region_tabla = pivot_region.pivot_table(
        values='Cantidad',
        index='Region',
        columns='Hora',
        fill_value=0
    )
    
    # Ordenar columnas
    try:
        cols_ordenadas = sorted(pivot_region_tabla.columns, key=lambda h: int(h.split(':')[0]))
        pivot_region_tabla = pivot_region_tabla[cols_ordenadas]
    except:
        pass
    
    # Crear figura
    fig = plt.figure(figsize=(20, 24), dpi=120, facecolor='white')
    fig.suptitle('Tablero de Monitor de Guias', fontsize=20, fontweight='bold', y=0.99, color='#333')
    
    # Grid
    gs = GridSpec(4, 1, figure=fig, hspace=0.3, height_ratios=[0.08, 0.50, 0.15, 0.27],
                  top=0.96, bottom=0.02, left=0.05, right=0.97)
    
    # ==================== FILA 1: KPIs ====================
    print("[KPI] Generando KPIs...")
    
    ax_kpis = fig.add_subplot(gs[0, 0])
    ax_kpis.axis('off')
    
    # Calcular valores para mostrar (GAM, RURAL, VYD, SPE, Total)
    kpis_valores = {
        'GAM': stats_por_region.get('GAM', 0),
        'RURAL': stats_por_region.get('RURAL', 0),
        'VYD': stats_por_region.get('CT02', 0),  # VYD es CT02
        'SPE': stats_por_region.get('CT01', 0),  # SPE es CT01
        'Total': total_guias
    }
    
    # Dibujar cajas KPI
    num_kpis = len(kpis_valores)
    box_width = 0.18
    box_height = 0.7
    spacing = 0.205
    start_x = 0.02
    
    colores_kpi = {
        'GAM': '#1565C0',
        'RURAL': '#2E7D32',
        'VYD': '#6A1B9A',
        'SPE': '#F57C00',
        'Total': '#424242'
    }
    
    for i, (label, valor) in enumerate(kpis_valores.items()):
        x_pos = start_x + (i * spacing)
        
        rect = mpatches.FancyBboxPatch((x_pos, 0.15), box_width, box_height,
                                        boxstyle="round,pad=0.02",
                                        facecolor=colores_kpi[label],
                                        edgecolor='white', linewidth=2, alpha=0.9,
                                        transform=ax_kpis.transAxes)
        ax_kpis.add_patch(rect)
        
        # Texto
        ax_kpis.text(x_pos + box_width/2, 0.7, label,
                    ha='center', va='center', fontsize=14, fontweight='bold',
                    color='white', transform=ax_kpis.transAxes)  # Aumentado de 12 a 14
        ax_kpis.text(x_pos + box_width/2, 0.4, str(valor),
                    ha='center', va='center', fontsize=22, fontweight='bold',
                    color='white', transform=ax_kpis.transAxes)  # Aumentado de 18 a 22
    
    # ==================== FILA 2: TABLA DETALLADA ZONA x HORA ====================
    print("[TABLA] Generando tabla detallada zona x hora...")
    
    ax_tabla = fig.add_subplot(gs[1, 0])
    ax_tabla.axis('off')
    
    # Preparar datos para tabla
    tabla_data = []
    headers = ['REGIÓN', 'ZONA'] + list(pivot_detallado.columns)
    
    # Agrupar por región y ordenar
    for region in REGIONES_ORDEN:
        if region not in pivot_detallado.index.get_level_values('Region'):
            continue
        
        # Obtener zonas de esta región
        zonas_region = pivot_detallado.loc[region]
        
        # Si es una serie (solo una zona), convertir a DataFrame
        if isinstance(zonas_region, pd.Series):
            zonas_region = pd.DataFrame([zonas_region])
            zonas_region.index = [zonas_region.index.name if hasattr(zonas_region.index, 'name') else 'Zona']
        
        # Nombre de región a mostrar
        if region == 'CT01':
            nombre_region = 'CT01'
        elif region == 'CT02':
            nombre_region = 'CT02'
        elif region == 'RURAL' and 'ZTL' in zonas_region.index:
            # Separar RURAL en RURAL y RURAL 3
            zonas_rural_3 = ['ZTL', 'ZTN', 'ZTP']
            zonas_rural_normal = [z for z in zonas_region.index if z not in zonas_rural_3]
            
            # RURAL normal
            for zona in zonas_rural_normal:
                if zona in zonas_region.index:
                    fila = ['RURAL', zona] + list(zonas_region.loc[zona].values)
                    tabla_data.append(fila)
            
            # RURAL 3
            for zona in zonas_rural_3:
                if zona in zonas_region.index:
                    fila = ['RURAL 3', zona] + list(zonas_region.loc[zona].values)
                    tabla_data.append(fila)
            continue
        else:
            nombre_region = region
        
        # Agregar filas normales
        for zona in zonas_region.index:
            fila = [nombre_region, zona] + list(zonas_region.loc[zona].values)
            tabla_data.append(fila)
    
    # Crear tabla
    if tabla_data:
        tabla = ax_tabla.table(cellText=tabla_data,
                              colLabels=headers,
                              cellLoc='center',
                              loc='upper center',
                              bbox=[0, 0, 1, 1])
        
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(10)  # Aumentado de 8 a 10
        tabla.scale(1, 1.8)  # Aumentado de 1.5 a 1.8
        
        # Estilo de encabezados
        for i in range(len(headers)):
            cell = tabla[(0, i)]
            cell.set_facecolor('#4CAF50')
            cell.set_text_props(weight='bold', color='white', fontsize=11)  # Aumentado de 9 a 11
        
        # Estilo de celdas
        for i in range(1, len(tabla_data) + 1):
            # Columna Región
            tabla[(i, 0)].set_facecolor('#E8F5E9')
            tabla[(i, 0)].set_text_props(weight='bold', fontsize=10)  # Añadido fontsize
            # Columna Zona
            tabla[(i, 1)].set_facecolor('#F1F8E9')
            tabla[(i, 1)].set_text_props(weight='bold', fontsize=10)  # Añadido weight y fontsize
            # Valores numéricos - NEGRITAS Y MÁS GRANDES
            for j in range(2, len(headers)):
                tabla[(i, j)].set_text_props(weight='bold', fontsize=11)  # Valores en negrita y más grandes
                # Alternar color de filas
                if i % 2 == 0:
                    tabla[(i, j)].set_facecolor('#FAFAFA')
    
    ax_tabla.text(0.5, 1.02, 'Horas', ha='center', va='bottom',
                 fontsize=16, fontweight='bold', transform=ax_tabla.transAxes)  # Aumentado de 14 a 16
    
    # ==================== FILA 3: TABLA RESUMEN POR REGIÓN ====================
    print("[TABLA] Generando tabla resumen por region...")
    
    ax_resumen = fig.add_subplot(gs[2, 0])
    ax_resumen.axis('off')
    
    # Preparar datos para resumen
    resumen_data = []
    headers_resumen = ['Región'] + list(pivot_region_tabla.columns)
    
    for region in REGIONES_ORDEN:
        if region in pivot_region_tabla.index:
            nombre_mostrar = region
            if region == 'CT01':
                nombre_mostrar = 'CT01'
            elif region == 'CT02':
                nombre_mostrar = 'CT02'
            
            fila = [nombre_mostrar] + list(pivot_region_tabla.loc[region].values)
            resumen_data.append(fila)
    
    # Crear tabla resumen
    if resumen_data:
        tabla_resumen = ax_resumen.table(cellText=resumen_data,
                                        colLabels=headers_resumen,
                                        cellLoc='center',
                                        loc='upper center',
                                        bbox=[0, 0.3, 1, 0.7])
        
        tabla_resumen.auto_set_font_size(False)
        tabla_resumen.set_fontsize(11)  # Aumentado de 9 a 11
        tabla_resumen.scale(1, 2.2)  # Aumentado de 2 a 2.2
        
        # Estilo de encabezados
        for i in range(len(headers_resumen)):
            cell = tabla_resumen[(0, i)]
            cell.set_facecolor('#2196F3')
            cell.set_text_props(weight='bold', color='white', fontsize=12)  # Aumentado de 10 a 12
        
        # Estilo de celdas de datos
        for i in range(1, len(resumen_data) + 1):
            # Primera columna (Región)
            tabla_resumen[(i, 0)].set_facecolor('#E3F2FD')
            tabla_resumen[(i, 0)].set_text_props(weight='bold', fontsize=11)  # Añadido fontsize
            
            # Resto de columnas - VALORES EN NEGRITA Y MÁS GRANDES
            for j in range(1, len(headers_resumen)):
                tabla_resumen[(i, j)].set_text_props(weight='bold', fontsize=12)  # Valores negritas y grandes
                if i % 2 == 0:
                    tabla_resumen[(i, j)].set_facecolor('#F5F5F5')
    
    # ==================== FILA 4: GRÁFICO DE TENDENCIAS ====================
    print("[GRAFICO] Generando grafico de tendencias...")
    
    ax_grafico = fig.add_subplot(gs[3, 0])
    
    # Excluir CT02 del gráfico
    regiones_para_grafico = [r for r in REGIONES_ORDEN if r != 'CT02']
    
    # Preparar datos para gráfico
    for region in regiones_para_grafico:
        if region in pivot_region_tabla.index:
            horas = pivot_region_tabla.columns
            valores = pivot_region_tabla.loc[region].values
            color = REGIONES_CONFIG[region]['color']
            
            # Dibujar línea
            ax_grafico.plot(horas, valores, marker='o', linewidth=2, markersize=6,
                          color=color, label=region, alpha=0.9)
            
            # Agregar valores en cada punto
            for i, (hora, valor) in enumerate(zip(horas, valores)):
                ax_grafico.text(i, valor, str(int(valor)), 
                              ha='center', va='bottom', fontsize=9, 
                              fontweight='bold', color=color)
    
    ax_grafico.set_xlabel('Hora', fontsize=13, fontweight='bold')
    ax_grafico.set_ylabel('Cantidad', fontsize=13, fontweight='bold')
    ax_grafico.set_title('Tendencias por Región (GAM, RURAL, CT01)', fontsize=16, fontweight='bold', pad=15)
    ax_grafico.legend(loc='upper left', fontsize=12, framealpha=0.9, prop={'weight': 'bold'})
    ax_grafico.grid(True, alpha=0.3, linestyle='--')
    plt.setp(ax_grafico.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=11, weight='bold')
    plt.setp(ax_grafico.yaxis.get_majorticklabels(), fontsize=11, weight='bold')
    
    # Agregar margen superior para que los valores no se corten
    ylim = ax_grafico.get_ylim()
    ax_grafico.set_ylim(ylim[0], ylim[1] * 1.1)
    
    # Agregar cajas de información en el gráfico
    info_text = f"VYD {stats_por_region.get('CT02', 0)}\nSPE {stats_por_region.get('CT01', 0)}\nTotal {total_guias}"
    ax_grafico.text(0.02, 0.05, info_text,
                   transform=ax_grafico.transAxes,
                   fontsize=11, fontweight='bold', verticalalignment='bottom',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    # Guardar figura completa
    print(f"[GUARDANDO] Guardando dashboard completo en: {output_path}")
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"[OK] Dashboard completo guardado: {output_path.name}")
    
    # ==================== GENERAR 3 IMÁGENES SEPARADAS ====================
    print("[PROCESO] Generando imagenes separadas...")
    
    archivos_generados = [output_path]
    output_dir = output_path.parent
    
    # IMAGEN 1: KPIs + Tabla Detallada
    print("[IMAGEN 1] KPIs + Tabla detallada...")
    fig1 = plt.figure(figsize=(20, 16), dpi=120, facecolor='white')
    fig1.suptitle('Tablero de Monitor de Guias - Detalle por Zona', 
                  fontsize=20, fontweight='bold', y=0.98, color='#333')
    gs1 = GridSpec(2, 1, figure=fig1, hspace=0.2, height_ratios=[0.12, 0.88],
                   top=0.96, bottom=0.02, left=0.05, right=0.97)
    
    # KPIs
    ax1_kpis = fig1.add_subplot(gs1[0, 0])
    ax1_kpis.axis('off')
    for i, (label, valor) in enumerate(kpis_valores.items()):
        x_pos = start_x + (i * spacing)
        rect = mpatches.FancyBboxPatch((x_pos, 0.15), box_width, box_height,
                                        boxstyle="round,pad=0.02",
                                        facecolor=colores_kpi[label],
                                        edgecolor='white', linewidth=2, alpha=0.9,
                                        transform=ax1_kpis.transAxes)
        ax1_kpis.add_patch(rect)
        ax1_kpis.text(x_pos + box_width/2, 0.7, label,
                     ha='center', va='center', fontsize=14, fontweight='bold',
                     color='white', transform=ax1_kpis.transAxes)
        ax1_kpis.text(x_pos + box_width/2, 0.4, str(valor),
                     ha='center', va='center', fontsize=22, fontweight='bold',
                     color='white', transform=ax1_kpis.transAxes)
    
    # Tabla Detallada
    ax1_tabla = fig1.add_subplot(gs1[1, 0])
    ax1_tabla.axis('off')
    if tabla_data:
        tabla1 = ax1_tabla.table(cellText=tabla_data, colLabels=headers,
                                cellLoc='center', loc='upper center', bbox=[0, 0, 1, 1])
        tabla1.auto_set_font_size(False)
        tabla1.set_fontsize(10)
        tabla1.scale(1, 1.8)
        for i in range(len(headers)):
            tabla1[(0, i)].set_facecolor('#4CAF50')
            tabla1[(0, i)].set_text_props(weight='bold', color='white', fontsize=11)
        for i in range(1, len(tabla_data) + 1):
            tabla1[(i, 0)].set_facecolor('#E8F5E9')
            tabla1[(i, 0)].set_text_props(weight='bold', fontsize=10)
            tabla1[(i, 1)].set_facecolor('#F1F8E9')
            tabla1[(i, 1)].set_text_props(weight='bold', fontsize=10)
            for j in range(2, len(headers)):
                tabla1[(i, j)].set_text_props(weight='bold', fontsize=11)
                if i % 2 == 0:
                    tabla1[(i, j)].set_facecolor('#FAFAFA')
    ax1_tabla.text(0.5, 1.02, 'Horas', ha='center', va='bottom',
                  fontsize=16, fontweight='bold', transform=ax1_tabla.transAxes)
    
    imagen1_path = output_dir / "dashboard_parte1_detalle.png"
    plt.savefig(imagen1_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    archivos_generados.append(imagen1_path)
    print(f"[OK] Imagen 1 guardada: {imagen1_path.name}")
    
    # IMAGEN 2A: Tabla Resumen - GAM, CT01 y CT02
    print("[IMAGEN 2A] Tabla resumen - GAM, CT01 y CT02...")
    fig2a = plt.figure(figsize=(20, 6), dpi=120, facecolor='white')
    fig2a.suptitle('Tablero de Monitor de Guias - Resumen GAM, CT01 y CT02', 
                  fontsize=20, fontweight='bold', y=0.95, color='#333')
    ax2a = fig2a.add_subplot(111)
    ax2a.axis('off')
    
    # Filtrar GAM, CT01 y CT02
    resumen_data_parte1 = [fila for fila in resumen_data if fila[0] in ['GAM', 'CT01', 'CT02']]
    
    if resumen_data_parte1:
        tabla2a = ax2a.table(cellText=resumen_data_parte1, colLabels=headers_resumen,
                          cellLoc='center', loc='center', bbox=[0, 0, 1, 0.8])
        tabla2a.auto_set_font_size(False)
        tabla2a.set_fontsize(11)
        tabla2a.scale(1, 2.8)
        for i in range(len(headers_resumen)):
            tabla2a[(0, i)].set_facecolor('#2196F3')
            tabla2a[(0, i)].set_text_props(weight='bold', color='white', fontsize=12)
        for i in range(1, len(resumen_data_parte1) + 1):
            tabla2a[(i, 0)].set_facecolor('#E3F2FD')
            tabla2a[(i, 0)].set_text_props(weight='bold', fontsize=11)
            for j in range(1, len(headers_resumen)):
                tabla2a[(i, j)].set_text_props(weight='bold', fontsize=12)
                if i % 2 == 0:
                    tabla2a[(i, j)].set_facecolor('#F5F5F5')
    
    imagen2a_path = output_dir / "dashboard_parte2a_resumen_gam_ct.png"
    plt.savefig(imagen2a_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    archivos_generados.append(imagen2a_path)
    print(f"[OK] Imagen 2A guardada: {imagen2a_path.name}")
    
    # IMAGEN 2B: Tabla Resumen - RURAL
    print("[IMAGEN 2B] Tabla resumen - RURAL...")
    fig2b = plt.figure(figsize=(20, 4), dpi=120, facecolor='white')
    fig2b.suptitle('Tablero de Monitor de Guias - Resumen RURAL', 
                  fontsize=20, fontweight='bold', y=0.95, color='#333')
    ax2b = fig2b.add_subplot(111)
    ax2b.axis('off')
    
    # Filtrar solo RURAL
    resumen_data_parte2 = [fila for fila in resumen_data if fila[0] in ['RURAL']]
    
    if resumen_data_parte2:
        tabla2b = ax2b.table(cellText=resumen_data_parte2, colLabels=headers_resumen,
                          cellLoc='center', loc='center', bbox=[0, 0, 1, 0.8])
        tabla2b.auto_set_font_size(False)
        tabla2b.set_fontsize(11)
        tabla2b.scale(1, 3.5)
        for i in range(len(headers_resumen)):
            tabla2b[(0, i)].set_facecolor('#2196F3')
            tabla2b[(0, i)].set_text_props(weight='bold', color='white', fontsize=12)
        for i in range(1, len(resumen_data_parte2) + 1):
            tabla2b[(i, 0)].set_facecolor('#E3F2FD')
            tabla2b[(i, 0)].set_text_props(weight='bold', fontsize=11)
            for j in range(1, len(headers_resumen)):
                tabla2b[(i, j)].set_text_props(weight='bold', fontsize=12)
                if i % 2 == 0:
                    tabla2b[(i, j)].set_facecolor('#F5F5F5')
    
    imagen2b_path = output_dir / "dashboard_parte2b_resumen_rural.png"
    plt.savefig(imagen2b_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    archivos_generados.append(imagen2b_path)
    print(f"[OK] Imagen 2B guardada: {imagen2b_path.name}")
    
    # IMAGEN 3: Gráfico de Tendencias
    print("[IMAGEN 3] Grafico de tendencias...")
    fig3 = plt.figure(figsize=(16, 10), dpi=120, facecolor='white')
    fig3.suptitle('Tablero de Monitor de Guias - Tendencias', 
                  fontsize=20, fontweight='bold', y=0.96, color='#333')
    ax3 = fig3.add_subplot(111)
    
    # Excluir CT02 del gráfico
    regiones_para_grafico = [r for r in REGIONES_ORDEN if r != 'CT02']
    
    for region in regiones_para_grafico:
        if region in pivot_region_tabla.index:
            horas = pivot_region_tabla.columns
            valores = pivot_region_tabla.loc[region].values
            color = REGIONES_CONFIG[region]['color']
            
            # Dibujar línea
            ax3.plot(horas, valores, marker='o', linewidth=2, markersize=6,
                    color=color, label=region, alpha=0.9)
            
            # Agregar valores en cada punto
            for i, (hora, valor) in enumerate(zip(horas, valores)):
                ax3.text(i, valor, str(int(valor)), 
                        ha='center', va='bottom', fontsize=9, 
                        fontweight='bold', color=color)
    
    ax3.set_xlabel('Hora', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Cantidad', fontsize=13, fontweight='bold')
    ax3.set_title('Tendencias por Región (GAM, RURAL, CT01)', fontsize=16, fontweight='bold', pad=15)
    ax3.legend(loc='upper left', fontsize=12, framealpha=0.9, prop={'weight': 'bold'})
    ax3.grid(True, alpha=0.3, linestyle='--')
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=11, weight='bold')
    plt.setp(ax3.yaxis.get_majorticklabels(), fontsize=11, weight='bold')
    
    # Agregar margen superior para que los valores no se corten
    ylim = ax3.get_ylim()
    ax3.set_ylim(ylim[0], ylim[1] * 1.1)
    
    info_text = f"VYD {stats_por_region.get('CT02', 0)}\nSPE {stats_por_region.get('CT01', 0)}\nTotal {total_guias}"
    ax3.text(0.02, 0.05, info_text, transform=ax3.transAxes,
            fontsize=11, fontweight='bold', verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    imagen3_path = output_dir / "dashboard_parte3_tendencias.png"
    plt.savefig(imagen3_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    archivos_generados.append(imagen3_path)
    print(f"[OK] Imagen 3 guardada: {imagen3_path.name}")
    
    print("[EXITO] 4 imagenes generadas exitosamente")
    return archivos_generados

def main():
    parser = argparse.ArgumentParser(description='Genera dashboard Tablero de Monitor de Guías')
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
        output_path = archivo_excel.parent / f"dashboard_regional_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    try:
        print("=" * 70)
        print("[INICIO] Generacion de Dashboard Tablero de Monitor de Guias")
        print("=" * 70)
        
        df = leer_excel_procesado(archivo_excel)
        print(f"[OK] Datos cargados: {len(df)} guias")
        
        archivos_generados = generar_dashboard(df, output_path)
        
        print("=" * 70)
        print("[EXITO] Dashboard generado exitosamente")
        print("=" * 70)
        print(f"Archivos generados: {len(archivos_generados)}")
        for i, archivo in enumerate(archivos_generados, 1):
            print(f"  {i}. {archivo.name} ({archivo.stat().st_size / 1024:.1f} KB)")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error al generar dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
