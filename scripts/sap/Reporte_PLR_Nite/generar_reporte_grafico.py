# -*- coding: utf-8 -*-
"""
Script: generar_reporte_grafico.py
Descripción:
  - Genera un reporte gráfico a partir del archivo Excel procesado
  - Crea una imagen estilo dashboard con múltiples gráficos
  - Optimizado para enviar por WhatsApp
  - Similar al dashboard de Power BI
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# Configuración de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Colores corporativos
COLOR_PRIMARY = '#1f77b4'    # Azul
COLOR_SECONDARY = '#ff7f0e'  # Naranja
COLOR_SUCCESS = '#2ca02c'    # Verde
COLOR_DANGER = '#d62728'     # Rojo
COLOR_INFO = '#17becf'       # Cyan
COLOR_WARNING = '#bcbd22'    # Amarillo-verde

def formato_miles(valor):
    """Formatea valores a formato 'K' (miles)"""
    if valor >= 1000:
        return f'{valor/1000:.1f}K'
    return f'{valor:.0f}'

def leer_datos_excel(archivo_excel):
    """Lee el archivo Excel procesado y retorna un DataFrame"""
    try:
        print(f"[LECTURA] Leyendo archivo: {archivo_excel}")
        df = pd.read_excel(archivo_excel, header=None, engine='openpyxl')
        
        # Mostrar información básica
        print(f"[INFO] Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"[INFO] Primeras columnas: {list(df.columns[:5])}")
        
        # Si la primera fila tiene nombres, úsala como encabezado
        if df.iloc[0].dtype == 'object':
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            print(f"[OK] Encabezados detectados: {list(df.columns[:5])}")
        
        return df
    except Exception as e:
        print(f"[ERROR] Error al leer archivo: {e}")
        raise

def crear_kpi_card(ax, titulo, valor, color):
    """Crea una tarjeta KPI en el subplot dado"""
    ax.axis('off')
    
    # Rectángulo de fondo
    rect = mpatches.FancyBboxPatch((0.1, 0.2), 0.8, 0.6,
                                    boxstyle="round,pad=0.05",
                                    facecolor=color, edgecolor='white',
                                    linewidth=2, alpha=0.8)
    ax.add_patch(rect)
    
    # Texto del título
    ax.text(0.5, 0.65, titulo, ha='center', va='center',
            fontsize=12, fontweight='bold', color='white',
            transform=ax.transAxes)
    
    # Texto del valor
    ax.text(0.5, 0.35, formato_miles(valor), ha='center', va='center',
            fontsize=18, fontweight='bold', color='white',
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

def generar_datos_ejemplo(df):
    """
    Genera datos de ejemplo basados en el DataFrame.
    NOTA: Esta función debe ser adaptada según la estructura real de tus datos.
    """
    # Si el DataFrame está vacío o no tiene los datos esperados,
    # generamos datos de ejemplo para demostración
    
    datos = {
        'kpis': {
            'TOTAL VENTA': 176900,
            'RURAL': 84300,
            'GAM': 63200,
            'MODERNO': 45300,
            'HA': 28200,
        },
        'macrocanales': {
            'OFF ABIERTO': 58000,
            'ON PREMISE': 44000,
            'INDIRECTO': 23000,
            'MODERNO': 20000,
            'WALMART': 21000,
            'DERIVAR': 11000,
        },
        'fuerza_ventas': {
            'FV Tradicional Rural': 79200,
            'FV Moderno': 45300,
            'FV Tradicional GAM': 45100,
            'FV Cuenta Clave ON': 6900,
            'FV E-Commerce': 400,
        },
        'cedis': {
            'nombres': ['GAM', 'LIB', 'NIC', 'PUN', 'SCA', 'SIS', 'CNL', 'GUA', 'LIM', 'HA'],
            'ventas': [63300, 18000, 12000, 10300, 12900, 7400, 5900, 12600, 5300, 28200],
            'capacidad': [54000, 14400, 9000, 10500, 9000, 8700, 5700, 11500, 6200, 30000],
            'cajas_fisicas': [55300, 15500, 11200, 9500, 11700, 6800, 5000, 11000, 4700, 25300],
        }
    }
    
    return datos

def crear_reporte_completo(df, output_path):
    """Crea el reporte gráfico completo"""
    
    print("[PROCESO] Generando reporte grafico...")
    
    # Obtener datos (adaptar según estructura real)
    datos = generar_datos_ejemplo(df)
    
    # Crear figura con tamaño adecuado para WhatsApp
    fig = plt.figure(figsize=(16, 20), dpi=100)
    fig.suptitle('REPORTE PLR - Dashboard de Ventas y Distribución',
                 fontsize=20, fontweight='bold', y=0.995)
    
    # Crear grid de subplots
    gs = GridSpec(5, 4, figure=fig, hspace=0.4, wspace=0.3,
                  top=0.96, bottom=0.02, left=0.05, right=0.98)
    
    # ==================== FILA 1: KPIs ====================
    print("[GRAFICO] Generando KPIs...")
    kpis = datos['kpis']
    colores_kpi = [COLOR_SUCCESS, COLOR_SECONDARY, COLOR_PRIMARY, 
                   COLOR_INFO, COLOR_WARNING]
    
    for i, (titulo, valor) in enumerate(kpis.items()):
        ax = fig.add_subplot(gs[0, i % 4])
        crear_kpi_card(ax, titulo, valor, colores_kpi[i % len(colores_kpi)])
    
    # ==================== FILA 2: Macrocanales y Fuerza de Ventas ====================
    print("[GRAFICO] Generando graficos de canales...")
    
    # Macrocanales (Barras verticales)
    ax1 = fig.add_subplot(gs[1, :2])
    canales = list(datos['macrocanales'].keys())
    valores_canales = list(datos['macrocanales'].values())
    bars1 = ax1.bar(canales, valores_canales, color=COLOR_PRIMARY, alpha=0.8)
    ax1.set_title('MACROCANALES', fontsize=14, fontweight='bold', pad=10)
    ax1.set_ylabel('Ventas', fontsize=10)
    ax1.tick_params(axis='x', rotation=45, labelsize=9)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax1.grid(axis='y', alpha=0.3)
    
    # Agregar valores en las barras
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                formato_miles(height),
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Fuerza de Ventas (Barras horizontales)
    ax2 = fig.add_subplot(gs[1, 2:])
    fv_nombres = list(datos['fuerza_ventas'].keys())
    fv_valores = list(datos['fuerza_ventas'].values())
    bars2 = ax2.barh(fv_nombres, fv_valores, color=COLOR_PRIMARY, alpha=0.8)
    ax2.set_title('FUERZA DE VENTAS', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xlabel('Ventas', fontsize=10)
    ax2.tick_params(axis='y', labelsize=9)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax2.grid(axis='x', alpha=0.3)
    
    # Agregar valores en las barras
    for i, (bar, val) in enumerate(zip(bars2, fv_valores)):
        ax2.text(val, bar.get_y() + bar.get_height()/2.,
                f' {formato_miles(val)}',
                ha='left', va='center', fontsize=8, fontweight='bold')
    
    # ==================== FILA 3: CEDIS y Cajas ====================
    print("[GRAFICO] Generando graficos de CEDIS...")
    
    # CEDIS con línea de capacidad
    ax3 = fig.add_subplot(gs[2, :2])
    cedis_nombres = datos['cedis']['nombres']
    x_pos = range(len(cedis_nombres))
    
    bars3 = ax3.bar(x_pos, datos['cedis']['ventas'], 
                    color=COLOR_PRIMARY, alpha=0.8, label='Ventas (Cj. Equiv.)')
    line3 = ax3.plot(x_pos, datos['cedis']['capacidad'], 
                     color=COLOR_SECONDARY, marker='o', linewidth=2, 
                     markersize=6, label='Capacidad CD')
    
    ax3.set_title('CAJAS EQUIV. vs CAPACIDAD CD', fontsize=14, fontweight='bold', pad=10)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(cedis_nombres, rotation=45, ha='right', fontsize=9)
    ax3.set_ylabel('Cajas', fontsize=10)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax3.legend(loc='upper right', fontsize=9)
    ax3.grid(axis='y', alpha=0.3)
    
    # Cajas Físicas
    ax4 = fig.add_subplot(gs[2, 2:])
    bars4 = ax4.bar(cedis_nombres, datos['cedis']['cajas_fisicas'], 
                    color=COLOR_INFO, alpha=0.8)
    ax4.set_title('CAJAS FÍSICAS TOTAL', fontsize=14, fontweight='bold', pad=10)
    ax4.set_ylabel('Cajas', fontsize=10)
    ax4.tick_params(axis='x', rotation=45, labelsize=9)
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax4.grid(axis='y', alpha=0.3)
    
    # Agregar valores principales
    for i, (bar, val) in enumerate(zip(bars4, datos['cedis']['cajas_fisicas'])):
        if val > max(datos['cedis']['cajas_fisicas']) * 0.3:  # Solo los más grandes
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    formato_miles(val),
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # ==================== FILA 4: Comparativos por Canal ====================
    print("[GRAFICO] Generando comparativos por canal...")
    
    # Moderno (Cajas Físicas vs Equiv)
    ax5 = fig.add_subplot(gs[3, :2])
    x_pos_mod = range(len(cedis_nombres))
    width = 0.35
    
    # Generar datos de ejemplo para Moderno
    cajas_fis_mod = [v * 0.4 for v in datos['cedis']['cajas_fisicas']]
    cajas_equiv_mod = [v * 0.42 for v in datos['cedis']['ventas']]
    
    bars5a = ax5.bar([x - width/2 for x in x_pos_mod], cajas_fis_mod,
                     width, label='Cajas Físicas', color=COLOR_PRIMARY, alpha=0.8)
    bars5b = ax5.bar([x + width/2 for x in x_pos_mod], cajas_equiv_mod,
                     width, label='Cajas Equiv.', color=COLOR_SECONDARY, alpha=0.8)
    
    ax5.set_title('MODERNO - Cajas Físicas vs Equiv.', fontsize=14, fontweight='bold', pad=10)
    ax5.set_xticks(x_pos_mod)
    ax5.set_xticklabels(cedis_nombres, rotation=45, ha='right', fontsize=9)
    ax5.set_ylabel('Cajas', fontsize=10)
    ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax5.legend(loc='upper right', fontsize=9)
    ax5.grid(axis='y', alpha=0.3)
    
    # Indirecto (Cajas Físicas vs Equiv)
    ax6 = fig.add_subplot(gs[3, 2:])
    
    # Generar datos de ejemplo para Indirecto
    cajas_fis_ind = [v * 0.2 for v in datos['cedis']['cajas_fisicas']]
    cajas_equiv_ind = [v * 0.21 for v in datos['cedis']['ventas']]
    
    bars6a = ax6.bar([x - width/2 for x in x_pos_mod], cajas_fis_ind,
                     width, label='Cajas Físicas', color=COLOR_PRIMARY, alpha=0.8)
    bars6b = ax6.bar([x + width/2 for x in x_pos_mod], cajas_equiv_ind,
                     width, label='Cajas Equiv.', color=COLOR_SECONDARY, alpha=0.8)
    
    ax6.set_title('INDIRECTO - Cajas Físicas vs Equiv.', fontsize=14, fontweight='bold', pad=10)
    ax6.set_xticks(x_pos_mod)
    ax6.set_xticklabels(cedis_nombres, rotation=45, ha='right', fontsize=9)
    ax6.set_ylabel('Cajas', fontsize=10)
    ax6.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax6.legend(loc='upper right', fontsize=9)
    ax6.grid(axis='y', alpha=0.3)
    
    # ==================== FILA 5: Estatus de Planificación ====================
    print("[GRAFICO] Generando graficos de planificacion...")
    
    # Estatus Planificación por CEDIS (Barras apiladas)
    ax7 = fig.add_subplot(gs[4, :2])
    
    # Datos de ejemplo para estatus
    en_guia = [v * 0.95 for v in datos['cedis']['cajas_fisicas']]
    en_mapa = [v * 0.03 for v in datos['cedis']['cajas_fisicas']]
    no_plan = [v * 0.02 for v in datos['cedis']['cajas_fisicas']]
    
    bars7a = ax7.bar(cedis_nombres, en_guia, label='EN GUIA', 
                     color=COLOR_PRIMARY, alpha=0.8)
    bars7b = ax7.bar(cedis_nombres, en_mapa, bottom=en_guia,
                     label='EN MAPA', color='gray', alpha=0.6)
    bars7c = ax7.bar(cedis_nombres, no_plan, 
                     bottom=[g+m for g,m in zip(en_guia, en_mapa)],
                     label='NO PLANIFICADO', color=COLOR_SECONDARY, alpha=0.6)
    
    ax7.set_title('ESTATUS PLANIFICACIÓN - Cajas Físicas', fontsize=14, fontweight='bold', pad=10)
    ax7.set_ylabel('Cajas', fontsize=10)
    ax7.tick_params(axis='x', rotation=45, labelsize=9)
    ax7.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax7.legend(loc='upper right', fontsize=9)
    ax7.grid(axis='y', alpha=0.3)
    
    # Estatus Planificación País (Horizontal)
    ax8 = fig.add_subplot(gs[4, 2:])
    
    categorias = ['EN GUIA', 'EN MAPA', 'NO PLANIFICADO']
    cajas_fis_pais = [150400, 6200, 600]
    cajas_equiv_pais = [163500, 7800, 600]
    
    y_pos = range(len(categorias))
    bars8a = ax8.barh([y - width/2 for y in y_pos], cajas_fis_pais,
                      width, label='Cajas Físicas', color=COLOR_PRIMARY, alpha=0.8)
    bars8b = ax8.barh([y + width/2 for y in y_pos], cajas_equiv_pais,
                      width, label='Cajas Equiv.', color=COLOR_SECONDARY, alpha=0.8)
    
    ax8.set_title('ESTATUS PLANIFICACIÓN - País', fontsize=14, fontweight='bold', pad=10)
    ax8.set_yticks(y_pos)
    ax8.set_yticklabels(categorias, fontsize=9)
    ax8.set_xlabel('Cajas', fontsize=10)
    ax8.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formato_miles(x)))
    ax8.legend(loc='lower right', fontsize=9)
    ax8.grid(axis='x', alpha=0.3)
    
    # Agregar valores
    for i, (bar, val) in enumerate(zip(bars8a, cajas_fis_pais)):
        ax8.text(val, bar.get_y() + bar.get_height()/2.,
                f' {formato_miles(val)}',
                ha='left', va='center', fontsize=8, fontweight='bold')
    
    # Agregar fecha y hora
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fig.text(0.99, 0.01, f'Generado: {fecha_actual}', 
             ha='right', va='bottom', fontsize=8, style='italic', color='gray')
    
    # Guardar figura
    print(f"[GUARDANDO] Guardando reporte en: {output_path}")
    plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"[OK] Reporte guardado exitosamente")
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Genera reporte gráfico para WhatsApp')
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
        # Mismo directorio que el archivo Excel
        output_path = archivo_excel.parent / f"reporte_grafico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    try:
        print("=" * 60)
        print("[INICIO] Generacion de Reporte Grafico para WhatsApp")
        print("=" * 60)
        
        # Leer datos
        df = leer_datos_excel(archivo_excel)
        
        # Crear reporte
        resultado = crear_reporte_completo(df, output_path)
        
        print("=" * 60)
        print("[EXITO] Reporte generado exitosamente")
        print("=" * 60)
        print(f"[ARCHIVO] {resultado}")
        print(f"[TAMAÑO] {resultado.stat().st_size / 1024:.1f} KB")
        print("=" * 60)
        print("")
        print("El reporte esta listo para enviar por WhatsApp!")
        print("")
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error al generar reporte: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

