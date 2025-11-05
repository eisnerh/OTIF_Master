# -*- coding: utf-8 -*-
"""
Script: enviar_whatsapp.py
Descripción:
  - Envía el reporte gráfico por WhatsApp
  - Soporta múltiples métodos de envío
  - Configuración de destinatarios
"""
import sys
import argparse
import configparser
from pathlib import Path
from datetime import datetime
import time

def load_whatsapp_config():
    """Carga la configuración de WhatsApp desde credentials.ini"""
    config = configparser.ConfigParser()
    creds_path = Path(__file__).parent / "credentials.ini"
    
    if not creds_path.exists():
        print("[ADVERTENCIA] No se encontro credentials.ini")
        return None
    
    config.read(creds_path, encoding="utf-8")
    
    if "WHATSAPP" not in config:
        print("[ADVERTENCIA] No hay seccion [WHATSAPP] en credentials.ini")
        return None
    
    whatsapp = config["WHATSAPP"]
    return {
        'metodo': whatsapp.get('metodo', 'pywhatkit').strip(),
        'numeros': [n.strip() for n in whatsapp.get('numeros', '').split(',') if n.strip()],
        'mensaje': whatsapp.get('mensaje', 'Reporte PLR NITE').strip(),
    }

def enviar_con_pywhatkit(imagen_path, numero, mensaje):
    """Envía imagen por WhatsApp usando pywhatkit"""
    try:
        import pywhatkit as kit
        
        print(f"[WHATSAPP] Enviando a {numero} usando pywhatkit...")
        print("[INFO] Se abrira WhatsApp Web automaticamente...")
        print("[INFO] Espera 15 segundos para que cargue...")
        
        # Obtener hora actual + 1 minuto
        ahora = datetime.now()
        hora = ahora.hour
        minuto = ahora.minute + 1
        
        if minuto >= 60:
            minuto -= 60
            hora += 1
        
        # Enviar imagen
        kit.sendwhats_image(
            receiver=numero,
            img_path=str(imagen_path),
            caption=mensaje,
            wait_time=15,
            tab_close=True
        )
        
        print(f"[OK] Mensaje enviado a {numero}")
        return True
        
    except ImportError:
        print("[ERROR] pywhatkit no esta instalado")
        print("[INFO] Instalar con: pip install pywhatkit")
        return False
    except Exception as e:
        print(f"[ERROR] Error al enviar con pywhatkit: {e}")
        return False

def enviar_con_whatsapp_web(imagen_path, numero, mensaje):
    """
    Abre WhatsApp Web con el número especificado.
    El usuario debe enviar manualmente la imagen.
    """
    try:
        import webbrowser
        
        print(f"[WHATSAPP] Abriendo WhatsApp Web para {numero}...")
        
        # Crear URL de WhatsApp Web
        # Formato: https://web.whatsapp.com/send?phone=NUMERO&text=MENSAJE
        numero_limpio = numero.replace('+', '').replace(' ', '').replace('-', '')
        url = f"https://web.whatsapp.com/send?phone={numero_limpio}&text={mensaje}"
        
        webbrowser.open(url)
        
        print("[INFO] WhatsApp Web abierto en el navegador")
        print(f"[INFO] Adjunta manualmente la imagen: {imagen_path}")
        print("[INFO] Presiona ENTER cuando hayas enviado el mensaje...")
        input()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al abrir WhatsApp Web: {e}")
        return False

def enviar_manual(imagen_path, numeros, mensaje):
    """Muestra instrucciones para envío manual"""
    print("=" * 60)
    print("[MANUAL] Instrucciones para envio manual por WhatsApp")
    print("=" * 60)
    print(f"\n1. Abre WhatsApp en tu telefono o WhatsApp Web")
    print(f"2. Envia la siguiente imagen a los contactos:")
    print(f"   {imagen_path}")
    print(f"\n3. Destinatarios:")
    for numero in numeros:
        print(f"   - {numero}")
    print(f"\n4. Mensaje:")
    print(f"   {mensaje}")
    print("\n" + "=" * 60)
    print("[INFO] Presiona ENTER cuando hayas terminado...")
    input()
    return True

def main():
    parser = argparse.ArgumentParser(description='Enviar reporte por WhatsApp')
    parser.add_argument('--imagen', required=True, help='Ruta a la imagen del reporte')
    parser.add_argument('--numeros', help='Numeros separados por coma (ej: +50612345678,+50687654321)')
    parser.add_argument('--mensaje', default='Reporte PLR NITE', help='Mensaje a enviar')
    parser.add_argument('--metodo', choices=['pywhatkit', 'web', 'manual'], 
                       default='manual', help='Metodo de envio')
    
    args = parser.parse_args()
    
    # Verificar que existe la imagen
    imagen_path = Path(args.imagen)
    if not imagen_path.exists():
        print(f"[ERROR] No se encontro la imagen: {imagen_path}")
        return 1
    
    print("=" * 60)
    print("[INICIO] Envio de Reporte por WhatsApp")
    print("=" * 60)
    print(f"[IMAGEN] {imagen_path}")
    print(f"[TAMAÑO] {imagen_path.stat().st_size / 1024:.1f} KB")
    
    # Cargar configuración
    config = load_whatsapp_config()
    
    # Determinar números
    if args.numeros:
        numeros = [n.strip() for n in args.numeros.split(',')]
    elif config and config['numeros']:
        numeros = config['numeros']
    else:
        print("[ERROR] No se especificaron numeros de telefono")
        print("[INFO] Usa --numeros o configura [WHATSAPP] en credentials.ini")
        return 1
    
    # Determinar método
    metodo = args.metodo
    if config and not args.numeros:  # Si viene de config, usar su método
        metodo = config.get('metodo', 'manual')
    
    mensaje = args.mensaje
    if config and config['mensaje']:
        mensaje = config['mensaje']
    
    print(f"[METODO] {metodo}")
    print(f"[DESTINATARIOS] {len(numeros)} numero(s)")
    print("=" * 60)
    
    # Enviar según método
    exitos = 0
    for numero in numeros:
        if metodo == 'pywhatkit':
            if enviar_con_pywhatkit(imagen_path, numero, mensaje):
                exitos += 1
                time.sleep(5)  # Esperar entre envíos
        elif metodo == 'web':
            if enviar_con_whatsapp_web(imagen_path, numero, mensaje):
                exitos += 1
        elif metodo == 'manual':
            if enviar_manual(imagen_path, [numero], mensaje):
                exitos += 1
    
    print("=" * 60)
    if exitos == len(numeros):
        print(f"[EXITO] Reporte enviado a {exitos} destinatario(s)")
    else:
        print(f"[PARCIAL] Enviado a {exitos} de {len(numeros)} destinatario(s)")
    print("=" * 60)
    
    return 0 if exitos > 0 else 1

if __name__ == "__main__":
    sys.exit(main())

