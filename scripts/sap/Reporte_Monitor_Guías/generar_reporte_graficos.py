# -*- coding: utf-8 -*-
"""
Script: generar_reporte_graficos.py
Descripción:
  - Lee el archivo Excel procesado (_processed.xlsx)
  - Agrupa zonas según reglas de negocio
  - Cuenta líneas por zona agrupada y por hora
  - Genera gráficos de tendencia por hora
  - Envía correo con gráficos y resumen
"""

from __future__ import annotations

import os
import sys
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para generar gráficos sin interfaz gráfica
import seaborn as sns
import configparser

# Configuración de zonas
ZONAS_RURAL = ['GUA', 'NIC', 'PUN', 'SCA', 'CNL', 'LIM', 'LIB', 'SIS', 'ZTP', 'ZTN', 'ZTL']
ZONA_VINOS = 'CT02'
ZONA_HA = 'SPE'

def mapear_zona(zona: str) -> str:
    """Mapea una zona individual a su grupo correspondiente."""
    if pd.isna(zona) or zona == '':
        return 'SIN_ZONA'
    zona_upper = str(zona).strip().upper()
    if zona_upper in ZONAS_RURAL:
        return 'RURAL'
    elif zona_upper == ZONA_VINOS:
        return 'VINOS'
    elif zona_upper == ZONA_HA:
        return 'HA'
    else:
        return 'GAM'

def cargar_configuracion_email() -> dict:
    """Carga configuración de email desde credentials.ini o variables de entorno."""
    config = configparser.ConfigParser()
    creds_path = Path(__file__).parent / "credentials.ini"
    
    email_config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'email_from': os.getenv('EMAIL_FROM', ''),
        'email_password': os.getenv('EMAIL_PASSWORD', ''),
        'email_to': os.getenv('EMAIL_TO', '').split(',') if os.getenv('EMAIL_TO') else [],
    }
    
    if creds_path.exists():
        config.read(creds_path, encoding="utf-8")
        if "EMAIL" in config:
            email_section = config["EMAIL"]
            email_config['smtp_server'] = email_section.get('smtp_server', email_config['smtp_server'])
            email_config['smtp_port'] = int(email_section.get('smtp_port', email_config['smtp_port']))
            email_config['email_from'] = email_section.get('email_from', email_config['email_from'])
            email_config['email_password'] = email_section.get('email_password', email_config['email_password'])
            email_to_str = email_section.get('email_to', '')
            if email_to_str:
                email_config['email_to'] = [e.strip() for e in email_to_str.split(',')]
    
    return email_config

def leer_excel_procesado(xlsx_path: Path) -> pd.DataFrame:
    """Lee el archivo Excel procesado y prepara los datos."""
    try:
        # Leer Excel sin header ya que se eliminaron las primeras 5 filas
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        
        if df.empty:
            raise ValueError("El archivo Excel está vacío")
        
        # La zona está en la columna 0 (primera columna después del procesamiento)
        # Renombrar columnas para facilitar el trabajo
        num_cols = len(df.columns)
        df.columns = [f'Col_{i}' for i in range(num_cols)]
        
        # Columna de zona (columna 1 original = índice 0 después de eliminar columnas A y C)
        columna_zona = 'Col_0'
        
        # Buscar columna de hora - nombres comunes o patrones
        nombres_posibles_hora = ['Hora', 'Hora Guía', 'Creado el', 'F. Creado', 'Carga HHD']
        columna_hora = None
        
        # Primero buscar por nombres comunes (si el archivo tiene headers)
        for i, col in enumerate(df.columns):
            # Verificar si alguna fila tiene estos nombres
            sample = df[col].astype(str).str.strip().head(10)
            if any(nombre.lower() in str(val).lower() for nombre in nombres_posibles_hora for val in sample):
                columna_hora = col
                break
        
        # Si no encontramos por nombre, buscar por patrones de hora
        if columna_hora is None:
            for col in df.columns:
                sample_values = df[col].dropna().head(50).astype(str)
                # Buscar patrones de hora (HH:MM o HH:MM:SS) o fecha/hora
                hora_count = sum(1 for v in sample_values if ':' in str(v) and len(str(v)) > 0)
                if hora_count > len(sample_values) * 0.3:  # Al menos 30% tiene formato de hora
                    columna_hora = col
                    break
        
        # Extraer hora
        if columna_hora:
            # Intentar parsear como datetime
            df['Hora'] = pd.to_datetime(df[columna_hora], errors='coerce').dt.strftime('%H:00')
            # Si no funciona, intentar extraer hora de string
            if df['Hora'].isna().all():
                # Buscar patrones HH:MM en strings
                def extraer_hora(val):
                    if pd.isna(val):
                        return None
                    val_str = str(val)
                    match = re.search(r'(\d{1,2}):(\d{2})', val_str)
                    if match:
                        return f"{int(match.group(1)):02d}:00"
                    return None
                df['Hora'] = df[columna_hora].apply(extraer_hora)
            
            df['Hora'] = df['Hora'].fillna(datetime.now().strftime('%H:00'))
        else:
            # Si no encontramos hora, usar la hora actual
            print("⚠️  No se encontró columna de hora, se usará la hora actual")
            df['Hora'] = datetime.now().strftime('%H:00')
        
        # Mapear zona
        df['Zona_Grupo'] = df[columna_zona].apply(mapear_zona)
        
        # Limpiar datos - eliminar filas sin zona válida
        df = df[df['Zona_Grupo'] != 'SIN_ZONA'].copy()
        
        # Filtrar horas válidas
        df = df[df['Hora'].notna()].copy()
        
        return df
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo Excel: {e}")

def contar_por_zona_y_hora(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta las líneas por zona agrupada y por hora."""
    conteo = df.groupby(['Zona_Grupo', 'Hora']).size().reset_index(name='Cantidad')
    return conteo

def generar_graficos(conteo_df: pd.DataFrame, output_dir: Path) -> List[Path]:
    """Genera gráficos de tendencia por hora para cada zona."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rutas_graficos = []
    
    zonas = conteo_df['Zona_Grupo'].unique()
    
    # Configurar estilo
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10
    
    # Gráfico combinado - todas las zonas
    fig, ax = plt.subplots(figsize=(14, 8))
    for zona in sorted(zonas):
        datos_zona = conteo_df[conteo_df['Zona_Grupo'] == zona].copy()
        if not datos_zona.empty:
            # Ordenar por hora
            datos_zona = datos_zona.sort_values('Hora')
            ax.plot(datos_zona['Hora'], datos_zona['Cantidad'], 
                   marker='o', linewidth=2, markersize=8, label=zona)
    
    ax.set_xlabel('Hora', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cantidad de Líneas', fontsize=12, fontweight='bold')
    ax.set_title('Tendencia de Líneas por Hora - Todas las Zonas', 
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(title='Zona', title_fontsize=11, fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    ruta_combinado = output_dir / 'grafico_todas_zonas.png'
    plt.savefig(ruta_combinado, dpi=300, bbox_inches='tight')
    plt.close()
    rutas_graficos.append(ruta_combinado)
    
    # Gráficos individuales por zona
    for zona in sorted(zonas):
        datos_zona = conteo_df[conteo_df['Zona_Grupo'] == zona].copy()
        if datos_zona.empty:
            continue
        
        datos_zona = datos_zona.sort_values('Hora')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(datos_zona['Hora'], datos_zona['Cantidad'], 
               marker='o', linewidth=2.5, markersize=10, 
               color=sns.color_palette("husl", len(zonas))[list(zonas).index(zona)])
        ax.fill_between(datos_zona['Hora'], datos_zona['Cantidad'], alpha=0.3)
        
        ax.set_xlabel('Hora', fontsize=11, fontweight='bold')
        ax.set_ylabel('Cantidad de Líneas', fontsize=11, fontweight='bold')
        ax.set_title(f'Tendencia de Líneas por Hora - Zona {zona}', 
                    fontsize=13, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        ruta_individual = output_dir / f'grafico_{zona.lower()}.png'
        plt.savefig(ruta_individual, dpi=300, bbox_inches='tight')
        plt.close()
        rutas_graficos.append(ruta_individual)
    
    return rutas_graficos

def crear_resumen_html(conteo_df: pd.DataFrame) -> str:
    """Crea un resumen HTML con estadísticas."""
    total_lineas = conteo_df['Cantidad'].sum()
    resumen_por_zona = conteo_df.groupby('Zona_Grupo')['Cantidad'].sum().sort_values(ascending=False)
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
            h2 {{ color: #666; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; font-weight: bold; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .total {{ font-size: 18px; font-weight: bold; color: #4CAF50; margin-top: 20px; }}
            .fecha {{ color: #888; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Reporte de Monitor de Guías por Zona</h1>
            <p class="fecha">Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="total">Total de líneas procesadas: {total_lineas:,}</div>
            
            <h2>Resumen por Zona</h2>
            <table>
                <tr>
                    <th>Zona</th>
                    <th>Total de Líneas</th>
                    <th>Porcentaje</th>
                </tr>
    """
    
    for zona, cantidad in resumen_por_zona.items():
        porcentaje = (cantidad / total_lineas * 100) if total_lineas > 0 else 0
        html += f"""
                <tr>
                    <td><strong>{zona}</strong></td>
                    <td>{cantidad:,}</td>
                    <td>{porcentaje:.2f}%</td>
                </tr>
        """
    
    html += """
            </table>
            
            <h2>Detalle por Hora</h2>
            <p>Los gráficos adjuntos muestran la tendencia de líneas por hora para cada zona.</p>
        </div>
    </body>
    </html>
    """
    
    return html

def enviar_correo(email_config: dict, rutas_graficos: List[Path], resumen_html: str) -> bool:
    """Envía correo con gráficos adjuntos."""
    if not email_config.get('email_from') or not email_config.get('email_to'):
        print("⚠️  Configuración de email incompleta. No se enviará correo.")
        return False
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('related')
        msg['From'] = email_config['email_from']
        msg['To'] = ', '.join(email_config['email_to'])
        msg['Subject'] = f"Reporte Monitor Guías - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Agregar HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(resumen_html, 'html'))
        
        # Adjuntar gráficos
        for ruta_grafico in rutas_graficos:
            if ruta_grafico.exists():
                with open(ruta_grafico, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', 
                                 filename=ruta_grafico.name)
                    msg.attach(img)
        
        # Enviar correo
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['email_from'], email_config['email_password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Correo enviado exitosamente a: {', '.join(email_config['email_to'])}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False

def main(xlsx_path: Optional[Path] = None, enviar_email: bool = True) -> int:
    """Función principal."""
    try:
        # Determinar ruta del archivo Excel
        if xlsx_path is None:
            # Buscar el archivo más reciente en OUTPUT_DIR
            output_dir = Path(r"C:/data/SAP_Extraction/y_dev_74")
            archivos_xlsx = list(output_dir.glob("*_processed.xlsx"))
            if not archivos_xlsx:
                print(f"❌ No se encontraron archivos *_processed.xlsx en {output_dir}")
                return 1
            xlsx_path = max(archivos_xlsx, key=lambda p: p.stat().st_mtime)
        
        print(f"📄 Procesando archivo: {xlsx_path}")
        
        # Leer datos
        df = leer_excel_procesado(xlsx_path)
        print(f"✅ Archivo leído: {len(df)} líneas")
        
        # Contar por zona y hora
        conteo_df = contar_por_zona_y_hora(df)
        print(f"✅ Conteo realizado para {len(conteo_df)} combinaciones zona/hora")
        
        # Generar gráficos
        graficos_dir = xlsx_path.parent / "graficos"
        rutas_graficos = generar_graficos(conteo_df, graficos_dir)
        print(f"✅ Gráficos generados: {len(rutas_graficos)} archivos")
        
        # Crear resumen HTML
        resumen_html = crear_resumen_html(conteo_df)
        
        # Enviar correo
        if enviar_email:
            email_config = cargar_configuracion_email()
            enviar_correo(email_config, rutas_graficos, resumen_html)
        
        print("✅ Proceso completado exitosamente")
        return 0
        
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Genera reporte con gráficos por zona y hora")
    parser.add_argument("--archivo", type=str, help="Ruta al archivo Excel procesado")
    parser.add_argument("--no-email", action="store_true", help="No enviar correo")
    args = parser.parse_args()
    
    xlsx_path = Path(args.archivo) if args.archivo else None
    sys.exit(main(xlsx_path, enviar_email=not args.no_email))

