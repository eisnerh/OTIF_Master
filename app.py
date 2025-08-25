from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import shutil
from pathlib import Path
import logging
import subprocess
import sys
import json
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.config['APP_NAME'] = 'OTIF Master'

# Configurar logging con nivel más alto para reducir operaciones innecesarias
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Solo configurar nivel INFO para el logger de la aplicación
logger.setLevel(logging.INFO)

# Variable global para el estado del procesamiento
procesamiento_status = {
    'en_proceso': False,
    'paso_actual': '',
    'progreso': 0,
    'mensajes': [],
    'completado': False,
    'error': None
}

def cargar_configuracion():
    """Carga la configuración de rutas desde el archivo JSON."""
    try:
        with open('configuracion_rutas.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Configuración por defecto
        config_default = {
            "rutas_archivos": {
                "rep_plr": "Data/Rep PLR",
                "no_entregas": "Data/No Entregas/2025",
                "vol_portafolio": "Data/Vol_Portafolio",
                "output_unificado": "Data/Output_Unificado",
                "output_final": "Data/Output/calculo_otif"
            },
            "archivos_principales": [
                "rep_plr.parquet",
                "no_entregas.parquet", 
                "vol_portafolio.parquet",
                "datos_completos_con_no_entregas.parquet"
            ],
            "ultima_actualizacion": None
        }
        guardar_configuracion(config_default)
        return config_default

def guardar_configuracion(config):
    """Guarda la configuración en el archivo JSON."""
    config["ultima_actualizacion"] = datetime.now().isoformat()
    with open('configuracion_rutas.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def ejecutar_script(script_name):
    """Ejecuta un script Python y retorna True si fue exitoso."""
    try:
        script_path = Path("scripts") / script_name
        procesamiento_status['mensajes'].append(f"Ejecutando: {script_name}")
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        
        if result.returncode == 0:
            procesamiento_status['mensajes'].append(f"✅ {script_name} completado")
            return True
        else:
            procesamiento_status['mensajes'].append(f"❌ Error en {script_name}: {result.stderr}")
            return False
            
    except Exception as e:
        procesamiento_status['mensajes'].append(f"❌ Error al ejecutar {script_name}: {str(e)}")
        return False

def copiar_archivos_a_destino():
    """Copia solo los archivos principales a la carpeta de destino."""
    config = cargar_configuracion()
    carpeta_destino = Path(config["rutas_archivos"]["output_final"])
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    
    procesamiento_status['mensajes'].append(f"Copiando archivos principales a: {carpeta_destino}")
    
    # Solo copiar los archivos principales
    archivos_a_copiar = []
    for archivo in config["archivos_principales"]:
        ruta_origen = Path(config["rutas_archivos"]["output_unificado"]) / archivo
        if ruta_origen.exists():
            archivos_a_copiar.append(str(ruta_origen))
        else:
            procesamiento_status['mensajes'].append(f"⚠️ Archivo no encontrado: {archivo}")
    
    archivos_copiados = []
    
    for archivo_origen in archivos_a_copiar:
        origen = Path(archivo_origen)
        if origen.exists():
            destino = carpeta_destino / origen.name
            try:
                shutil.copy2(origen, destino)
                archivos_copiados.append(archivo_origen)
                procesamiento_status['mensajes'].append(f"✅ Copiado: {origen.name}")
            except Exception as e:
                procesamiento_status['mensajes'].append(f"❌ Error al copiar {archivo_origen}: {str(e)}")
        else:
            procesamiento_status['mensajes'].append(f"⚠️ Archivo no encontrado: {archivo_origen}")
    
    return archivos_copiados

def crear_resumen_final():
    """Crea un archivo de resumen con información de los archivos principales."""
    config = cargar_configuracion()
    carpeta_destino = Path(config["rutas_archivos"]["output_final"])
    
    resumen = {
        "archivos_generados": [],
        "estadisticas": {},
        "fecha_procesamiento": datetime.now().isoformat(),
        "configuracion_utilizada": config
    }
    
    # Solo analizar los archivos principales
    archivos_principales = config["archivos_principales"]
    
    for archivo in archivos_principales:
        ruta_archivo = carpeta_destino / archivo
        if ruta_archivo.exists():
            try:
                df = pd.read_parquet(ruta_archivo)
                info_archivo = {
                    "nombre": archivo,
                    "filas": len(df),
                    "columnas": len(df.columns),
                    "tamaño_mb": ruta_archivo.stat().st_size / (1024*1024)
                }
                resumen["archivos_generados"].append(info_archivo)
                
                if "REP_PLR" in archivo:
                    resumen["estadisticas"]["rep_plr"] = {
                        "total_registros": len(df),
                        "centros_unicos": df['Centro'].nunique() if 'Centro' in df.columns else 0
                    }
                elif "No_Entregas" in archivo:
                    resumen["estadisticas"]["no_entregas"] = {
                        "total_registros": len(df),
                        "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0
                    }
                elif "Vol_Portafolio" in archivo:
                    resumen["estadisticas"]["vol_portafolio"] = {
                        "total_registros": len(df),
                        "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0,
                        "zonas_unicas": df['Zona'].nunique() if 'Zona' in df.columns else 0
                    }
                elif "rep_plr" in archivo:
                    resumen["estadisticas"]["rep_plr_final"] = {
                        "total_registros": len(df),
                        "centros_unicos": df['Centro'].nunique() if 'Centro' in df.columns else 0
                    }
                elif "no_entregas" in archivo:
                    resumen["estadisticas"]["no_entregas_final"] = {
                        "total_registros": len(df),
                        "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0
                    }
                elif "vol_portafolio" in archivo and "unido" not in archivo:
                    resumen["estadisticas"]["vol_portafolio_final"] = {
                        "total_registros": len(df),
                        "familias_unicas": df['Familia'].nunique() if 'Familia' in df.columns else 0
                    }
                elif "rep_plr_vol_portafolio_unido" in archivo:
                    resumen["estadisticas"]["rep_plr_vol_portafolio_unido"] = {
                        "total_registros": len(df),
                        "columnas_totales": len(df.columns),
                        "registros_con_match": len(df.dropna(subset=[col for col in df.columns if 'vol_portafolio' in col]))
                    }
                elif "datos_completos_con_no_entregas" in archivo:
                    resumen["estadisticas"]["datos_completos_con_no_entregas"] = {
                        "total_registros": len(df),
                        "columnas_totales": len(df.columns),
                        "registros_con_match": len(df.dropna(subset=[col for col in df.columns if 'no_entregas' in col]))
                    }
                    
            except Exception as e:
                procesamiento_status['mensajes'].append(f"Error al leer {archivo}: {str(e)}")
    
    archivo_resumen = carpeta_destino / "resumen_procesamiento.json"
    with open(archivo_resumen, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    
    procesamiento_status['mensajes'].append(f"✅ Resumen guardado en: {archivo_resumen}")
    return resumen

def verificar_rutas_configuracion():
    """Verifica que las rutas configuradas existan."""
    config = cargar_configuracion()
    rutas_verificadas = {}
    
    for nombre, ruta in config["rutas_archivos"].items():
        path = Path(ruta)
        if path.exists():
            rutas_verificadas[nombre] = {"existe": True, "ruta": str(path)}
            procesamiento_status['mensajes'].append(f"✅ Ruta verificada: {nombre} -> {ruta}")
        else:
            rutas_verificadas[nombre] = {"existe": False, "ruta": str(path)}
            procesamiento_status['mensajes'].append(f"⚠️ Ruta no encontrada: {nombre} -> {ruta}")
    
    return rutas_verificadas

def procesamiento_completo_otif():
    """Ejecuta el procesamiento completo de todos los scripts en orden."""
    global procesamiento_status
    
    try:
        procesamiento_status['en_proceso'] = True
        procesamiento_status['completado'] = False
        procesamiento_status['error'] = None
        procesamiento_status['mensajes'] = []
        procesamiento_status['progreso'] = 0
        
        # Paso 1: Procesar Rep PLR
        procesamiento_status['paso_actual'] = 'Procesando datos Rep PLR'
        procesamiento_status['progreso'] = 10
        if not ejecutar_script("agrupar_datos_rep_plr.py"):
            procesamiento_status['error'] = "Falló el procesamiento de Rep PLR"
            return
        
        # Paso 2: Procesar No Entregas
        procesamiento_status['paso_actual'] = 'Procesando datos No Entregas'
        procesamiento_status['progreso'] = 30
        if not ejecutar_script("agrupar_datos_no_entregas_mejorado.py"):
            procesamiento_status['error'] = "Falló el procesamiento de No Entregas"
            return
        
        # Paso 3: Procesar Vol Portafolio
        procesamiento_status['paso_actual'] = 'Procesando datos Vol Portafolio'
        procesamiento_status['progreso'] = 50
        if not ejecutar_script("agrupar_datos_vol_portafolio.py"):
            procesamiento_status['error'] = "Falló el procesamiento de Vol Portafolio"
            return
        
        # Paso 4: Unificar datos
        procesamiento_status['paso_actual'] = 'Unificando datos'
        procesamiento_status['progreso'] = 60
        if not ejecutar_script("unificar_datos_completos.py"):
            procesamiento_status['mensajes'].append("⚠️ Falló la unificación de datos, continuando...")
        
        # Paso 5: Copiar archivos a carpeta de destino
        procesamiento_status['paso_actual'] = 'Copiando archivos a carpeta de destino'
        procesamiento_status['progreso'] = 70
        archivos_copiados = copiar_archivos_a_destino()
        
        # Paso 6: Crear resumen final
        procesamiento_status['paso_actual'] = 'Creando resumen final'
        procesamiento_status['progreso'] = 85
        resumen = crear_resumen_final()
        
        # Paso 7: Verificar rutas de configuración
        procesamiento_status['paso_actual'] = 'Verificando configuración de rutas'
        procesamiento_status['progreso'] = 95
        verificar_rutas_configuracion()
        
        # Completado
        procesamiento_status['paso_actual'] = 'Procesamiento completado'
        procesamiento_status['progreso'] = 100
        procesamiento_status['completado'] = True
        procesamiento_status['mensajes'].append("✅ ¡PROCESAMIENTO COMPLETO FINALIZADO EXITOSAMENTE!")
        
    except Exception as e:
        procesamiento_status['error'] = str(e)
        procesamiento_status['mensajes'].append(f"❌ Error general: {str(e)}")
    finally:
        procesamiento_status['en_proceso'] = False

@app.route('/')
def index():
    """Página principal de la aplicación."""
    return render_template('index.html', app_name=app.config['APP_NAME'])

@app.route('/iniciar_procesamiento', methods=['POST'])
def iniciar_procesamiento():
    """Inicia el procesamiento en un hilo separado."""
    global procesamiento_status
    
    if procesamiento_status['en_proceso']:
        return jsonify({'error': 'Ya hay un procesamiento en curso'})
    
    # Reiniciar estado
    procesamiento_status = {
        'en_proceso': False,
        'paso_actual': '',
        'progreso': 0,
        'mensajes': [],
        'completado': False,
        'error': None
    }
    
    # Iniciar procesamiento en hilo separado
    thread = threading.Thread(target=procesamiento_completo_otif)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Procesamiento iniciado'})

@app.route('/estado_procesamiento')
def estado_procesamiento():
    """Retorna el estado actual del procesamiento."""
    return jsonify(procesamiento_status)

@app.route('/archivos_generados')
def archivos_generados():
    """Retorna información sobre los archivos principales generados."""
    config = cargar_configuracion()
    carpeta_destino = Path(config["rutas_archivos"]["output_final"])
    
    if not carpeta_destino.exists():
        return jsonify({'archivos': [], 'error': 'Carpeta de destino no existe'})
    
    archivos = []
    # Solo mostrar los archivos principales
    for archivo_nombre in config["archivos_principales"]:
        archivo_path = carpeta_destino / archivo_nombre
        if archivo_path.exists():
            try:
                df = pd.read_parquet(archivo_path)
                archivos.append({
                    'nombre': archivo_path.name,
                    'filas': len(df),
                    'columnas': len(df.columns),
                    'tamaño_mb': archivo_path.stat().st_size / (1024*1024),
                    'fecha_modificacion': datetime.fromtimestamp(archivo_path.stat().st_mtime).isoformat(),
                    'es_principal': True
                })
            except Exception as e:
                archivos.append({
                    'nombre': archivo_path.name,
                    'error': str(e),
                    'es_principal': True
                })
        else:
            archivos.append({
                'nombre': archivo_nombre,
                'error': 'Archivo no encontrado',
                'es_principal': True
            })
    
    return jsonify({'archivos': archivos})

@app.route('/descargar_archivo/<nombre_archivo>')
def descargar_archivo(nombre_archivo):
    """Permite descargar un archivo específico."""
    config = cargar_configuracion()
    carpeta_destino = Path(config["rutas_archivos"]["output_final"])
    archivo = carpeta_destino / nombre_archivo
    
    if archivo.exists():
        return send_file(archivo, as_attachment=True)
    else:
        return jsonify({'error': 'Archivo no encontrado'}), 404

@app.route('/ver_resumen')
def ver_resumen():
    """Retorna el resumen del procesamiento."""
    config = cargar_configuracion()
    archivo_resumen = Path(config["rutas_archivos"]["output_final"]) / "resumen_procesamiento.json"
    
    if archivo_resumen.exists():
        with open(archivo_resumen, 'r', encoding='utf-8') as f:
            resumen = json.load(f)
        return jsonify(resumen)
    else:
        return jsonify({'error': 'Resumen no encontrado'}), 404

@app.route('/configuracion')
def obtener_configuracion():
    """Retorna la configuración actual."""
    return jsonify(cargar_configuracion())

@app.route('/configuracion', methods=['POST'])
def actualizar_configuracion():
    """Actualiza la configuración de rutas."""
    try:
        nueva_config = request.get_json()
        config_actual = cargar_configuracion()
        
        # Actualizar solo las rutas proporcionadas
        if 'rutas_archivos' in nueva_config:
            config_actual['rutas_archivos'].update(nueva_config['rutas_archivos'])
        
        # Actualizar archivos principales si se proporcionan
        if 'archivos_principales' in nueva_config:
            config_actual['archivos_principales'] = nueva_config['archivos_principales']
        
        guardar_configuracion(config_actual)
        return jsonify({'message': 'Configuración actualizada correctamente', 'config': config_actual})
    except Exception as e:
        return jsonify({'error': f'Error al actualizar configuración: {str(e)}'}), 400

@app.route('/verificar_rutas')
def verificar_rutas():
    """Verifica las rutas configuradas."""
    return jsonify(verificar_rutas_configuracion())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
