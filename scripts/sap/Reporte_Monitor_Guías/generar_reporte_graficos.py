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
from email.mime.application import MIMEApplication
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Para generar gráficos sin interfaz gráfica
import matplotlib.pyplot as plt
import seaborn as sns
import configparser

# Importar configuración centralizada de regiones
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from configuracion_regiones import (
        REGIONES_CONFIG,
        ZONAS_RURAL,
        mapear_zona_a_region as mapear_zona
    )
    print("[OK] Configuracion de regiones cargada")
except ImportError:
    # Fallback si no se encuentra el módulo
    ZONAS_RURAL = ['CNL', 'GUA', 'LIB', 'LIM', 'NIC', 'PUN', 'SCA', 'SIS', 'ZTL', 'ZTN', 'ZTP']
    ZONAS_GAM = ['ALJ', 'CAR', 'CMN', 'CMT', 'COG', 'SJE', 'SJO', 'SUP', 'ZTO']
    
    def mapear_zona(zona: str) -> str:
        """Mapea una zona individual a su grupo correspondiente."""
        if pd.isna(zona) or zona == '':
            return 'SIN_ZONA'
        zona_upper = str(zona).strip().upper()
        if zona_upper in ZONAS_RURAL:
            return 'RURAL'
        elif zona_upper in ZONAS_GAM:
            return 'GAM'
        elif zona_upper == 'SPE':
            return 'CT01'
        elif zona_upper == 'VYD':
            return 'CT02'
        else:
            return 'SIN_ZONA'

def cargar_configuracion_email() -> dict:
    """Carga configuración de email desde credentials.ini o variables de entorno."""
    config = configparser.ConfigParser()
    creds_path = Path(__file__).parent / "credentials.ini"
    
    # Valores por defecto (se pueden sobrescribir con credentials.ini o variables de entorno)
    email_config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'email_from': os.getenv('EMAIL_FROM', ''),
        'email_password': os.getenv('EMAIL_PASSWORD', ''),
        'email_to': [],
    }
    
    # Cargar desde credentials.ini si existe (prioridad más alta)
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
    
    # Si no hay email_to desde credentials.ini, usar variable de entorno
    if not email_config['email_to']:
        email_to_env = os.getenv('EMAIL_TO', '')
        if email_to_env:
            email_config['email_to'] = [e.strip() for e in email_to_env.split(',')]
    
    return email_config

def leer_excel_procesado(xlsx_path: Path) -> pd.DataFrame:
    """Lee el archivo Excel procesado y prepara los datos."""
    try:
        # Leer Excel sin header ya que se eliminaron las primeras 5 filas
        df = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
        
        if df.empty:
            raise ValueError("El archivo Excel está vacío")
        
        # Verificar que tenemos suficientes columnas
        if len(df.columns) < 9:
            raise ValueError(f"El archivo tiene menos de 9 columnas. Columnas encontradas: {len(df.columns)}")
        
        # Columna B = índice 1 (zona)
        # Columna I = índice 8 (hora)
        columna_zona_idx = 1  # Columna B
        columna_hora_idx = 8  # Columna I
        columna_viaje_idx = 5  # Columna F
        
        # Extraer zona
        df['Zona'] = df.iloc[:, columna_zona_idx]
        
        # Extraer hora de la columna I
        def extraer_hora(val):
            """Extrae la hora de diferentes formatos posibles."""
            if pd.isna(val):
                return None
            val_str = str(val).strip()
            if not val_str or val_str == 'nan':
                return None
            
            # Intentar parsear como datetime
            try:
                dt = pd.to_datetime(val_str, errors='coerce')
                if pd.notna(dt):
                    return dt.strftime('%H:00')
            except:
                pass
            
            # Buscar patrones HH:MM o HH:MM:SS en strings
            match = re.search(r'(\d{1,2}):(\d{2})', val_str)
            if match:
                hora = int(match.group(1))
                if 0 <= hora <= 23:
                    return f"{hora:02d}:00"
            
            return None
        
        df['Hora'] = df.iloc[:, columna_hora_idx].apply(extraer_hora)
        
        # Filtrar filas con hora válida
        df = df[df['Hora'].notna()].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas con hora válida en la columna I")
        
        # Filtro columna F: solo valores que inicien con '1'
        # Normalizar y comparar inicio con '1' (manejo de números y strings)
        def inicia_con_uno(val) -> bool:
            """Verifica si el valor inicia con '1'."""
            if pd.isna(val):
                return False
            val_str = str(val).strip()
            return val_str.startswith('1')
        
        # Aplicar filtro de columna F
        columna_f = df.iloc[:, columna_viaje_idx]
        df = df[columna_f.apply(inicia_con_uno)].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas donde la columna F inicie con '1'")
        
        # Mapear zona
        df['Zona_Grupo'] = df['Zona'].apply(mapear_zona)
        
        # Limpiar datos - eliminar filas sin zona válida
        df = df[df['Zona_Grupo'] != 'SIN_ZONA'].copy()
        
        if df.empty:
            raise ValueError("No se encontraron filas con zona válida en la columna B")
        
        return df
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo Excel: {e}")

def contar_por_zona_y_hora(df: pd.DataFrame) -> pd.DataFrame:
    """Cuenta las líneas por zona agrupada y por hora."""
    conteo = df.groupby(['Zona_Grupo', 'Hora']).size().reset_index(name='Cantidad')
    return conteo

# Función eliminada - ya no se generan gráficos individuales
# Los gráficos ahora vienen del generar_dashboard_regional.py

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
            <h1>Reporte de Monitor de Guias por Zona</h1>
            <p class="fecha">Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="total">Total de Guías procesadas: {total_lineas:,}</div>
            
            <h2>Resumen por Zona</h2>
            <table>
                <tr>
                    <th>Zona</th>
                    <th>Total de Guías</th>
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
            
            <h2> </h2>
            <ul>
                <li><strong></strong>
                    <ul>
                    </ul>
                </li>
        </div>
    </body>
    </html>
    """
    
    return html

def enviar_correo(email_config: dict, rutas_graficos: List[Path], resumen_html: str, excel_path: Optional[Path] = None) -> bool:
    """Envía correo con gráficos adjuntos."""
    if not email_config.get('email_from'):
        print("ERROR: No se configuró 'email_from' en credentials.ini")
        print("Por favor agrega en la sección [EMAIL]:")
        print("  email_from = tu_email@gmail.com")
        return False
    
    if not email_config.get('email_to'):
        print("ERROR: No se configuró 'email_to' en credentials.ini")
        print("Por favor agrega en la sección [EMAIL]:")
        print("  email_to = destinatario@correo.com")
        return False
    
    if not email_config.get('email_password'):
        print("ERROR: No se configuró 'email_password' en credentials.ini")
        print("Por favor agrega en la sección [EMAIL]:")
        print("  email_password = tu_app_password")
        return False
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('related')
        msg['From'] = email_config['email_from']
        msg['To'] = ', '.join(email_config['email_to'])
        msg['Subject'] = f"Dashboard Monitor de Guias - Analisis Regional - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Agregar HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(resumen_html, 'html'))
        
        # Adjuntar gráficos
        # El dashboard ya está al inicio de rutas_graficos si existe
        total_adjuntos = 0
        for i, ruta_grafico in enumerate(rutas_graficos):
            if ruta_grafico.exists():
                with open(ruta_grafico, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', 'attachment', 
                                 filename=ruta_grafico.name)
                    msg.attach(img)
                
                # Log para dashboards
                if 'dashboard_parte' in ruta_grafico.name:
                    print(f"OK: [DASHBOARD PARTE {i+1}] {ruta_grafico.name} adjuntado ({ruta_grafico.stat().st_size / 1024:.1f} KB)")
                else:
                    print(f"OK: Imagen adjuntada: {ruta_grafico.name}")
                
                total_adjuntos += 1
        
        print(f"OK: Total de imagenes adjuntadas: {total_adjuntos}")
        
        # Adjuntar Excel procesado si existe
        if excel_path and excel_path.exists():
            with open(excel_path, 'rb') as f:
                part = MIMEApplication(
                    f.read(),
                    _subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                part.add_header('Content-Disposition', 'attachment', filename=excel_path.name)
                msg.attach(part)
            print(f"OK: Excel adjuntado: {excel_path.name}")
        
        # Enviar correo
        print(f"[EMAIL] Conectando al servidor SMTP: {email_config['smtp_server']}:{email_config['smtp_port']}")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        
        print("[EMAIL] Iniciando TLS...")
        server.starttls()
        
        print(f"[EMAIL] Autenticando con: {email_config['email_from']}")
        server.login(email_config['email_from'], email_config['email_password'])
        
        print("[EMAIL] Enviando mensaje...")
        server.send_message(msg)
        server.quit()
        
        print(f"[EMAIL] ✓ Correo enviado exitosamente a: {', '.join(email_config['email_to'])}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] ERROR: Error de autenticación SMTP")
        print(f"  Verifica que el email_password sea correcto (App Password de Gmail)")
        print(f"  Error detallado: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL] ERROR: Error SMTP al enviar correo")
        print(f"  Error detallado: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL] ERROR: Error inesperado al enviar correo")
        print(f"  Tipo de error: {type(e).__name__}")
        print(f"  Mensaje: {e}")
        import traceback
        traceback.print_exc()
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
                print(f"ERROR: No se encontraron archivos *_processed.xlsx en {output_dir}")
                return 1
            xlsx_path = max(archivos_xlsx, key=lambda p: p.stat().st_mtime)
        
        print(f"Procesando archivo: {xlsx_path}")
        
        # Leer datos
        df = leer_excel_procesado(xlsx_path)
        print(f"OK: Archivo leído: {len(df)} líneas")
        
        # Contar por zona y hora
        conteo_df = contar_por_zona_y_hora(df)
        print(f"OK: Conteo realizado para {len(conteo_df)} combinaciones zona/hora")
        
        # Esperar 10 segundos para que se generen las imágenes del dashboard
        print("Esperando 10 segundos para que se generen las imagenes del dashboard...")
        import time
        time.sleep(10)
        
        # Buscar las 4 imágenes del dashboard
        rutas_graficos = []
        nombres_dashboard = [
            "dashboard_parte1a_detalle_gam.png",
            "dashboard_parte1b_detalle_rural_ct.png",
            "dashboard_parte2_resumen.png",
            "dashboard_parte3_tendencias.png"
        ]
        
        print("[BUSCAR] Buscando imagenes del dashboard...")
        for nombre in nombres_dashboard:
            dashboard_path = xlsx_path.parent / nombre
            if dashboard_path.exists():
                rutas_graficos.append(dashboard_path)
                print(f"OK: Encontrado: {nombre} ({dashboard_path.stat().st_size / 1024:.1f} KB)")
            else:
                print(f"ADVERTENCIA: No encontrado: {nombre}")
        
        if not rutas_graficos:
            print("ADVERTENCIA: No se encontraron imagenes del dashboard")
            print("CONTINUANDO: Se enviara correo solo con resumen y Excel")
        else:
            print(f"OK: {len(rutas_graficos)} imagenes del dashboard listas para adjuntar")
        
        # Crear resumen HTML
        resumen_html = crear_resumen_html(conteo_df)
        
        # Enviar correo
        if enviar_email:
            print("\n[EMAIL] Preparando envío de correo...")
            email_config = cargar_configuracion_email()
            
            print(f"[EMAIL] Configuración cargada:")
            print(f"  SMTP Server: {email_config.get('smtp_server')}")
            print(f"  SMTP Port: {email_config.get('smtp_port')}")
            print(f"  From: {email_config.get('email_from')}")
            print(f"  To: {', '.join(email_config.get('email_to', []))}")
            print(f"  Imágenes adjuntas: {len(rutas_graficos)}")
            print(f"  Excel adjunto: {'Sí' if xlsx_path and xlsx_path.exists() else 'No'}")
            
            resultado_email = enviar_correo(email_config, rutas_graficos, resumen_html, excel_path=xlsx_path)
            
            if resultado_email:
                print("[EMAIL] ✓ Correo enviado exitosamente")
            else:
                print("[EMAIL] ✗ No se pudo enviar el correo")
        else:
            print("[EMAIL] Envío de email deshabilitado (--no-email)")
        
        print("\n[PROCESO] ✓ Proceso completado exitosamente")
        return 0
        
    except Exception as e:
        print(f"ERROR: Error en el proceso: {e}")
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

