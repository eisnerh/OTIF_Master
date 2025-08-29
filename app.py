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
import tkinter as tk
from tkinter import filedialog
import tempfile

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
    'error': None,
    'archivo_actual': '',
    'lineas_procesadas': 0,
    'total_lineas': 0
}

def seleccionar_carpeta(titulo="Seleccionar carpeta"):
    """
    Abre un explorador de archivos para seleccionar una carpeta.
    Retorna la ruta seleccionada o None si se cancela.
    """
    try:
        # Crear una ventana temporal de tkinter (oculta)
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal
        root.attributes('-topmost', True)  # Mantener en primer plano
        
        # Abrir el explorador de carpetas
        carpeta_seleccionada = filedialog.askdirectory(
            title=titulo,
            initialdir=os.getcwd()
        )
        
        root.destroy()  # Cerrar la ventana de tkinter
        
        if carpeta_seleccionada:
            # Convertir a ruta relativa si es posible
            try:
                carpeta_relativa = os.path.relpath(carpeta_seleccionada, os.getcwd())
                return carpeta_relativa
            except ValueError:
                # Si no se puede hacer relativa, usar la ruta absoluta
                return carpeta_seleccionada
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error al abrir explorador de carpetas: {str(e)}")
        return None

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

@app.route('/actualizar_progreso_archivo', methods=['POST'])
def actualizar_progreso_archivo():
    """Actualiza el progreso de lectura de un archivo específico."""
    datos = request.json
    if datos:
        procesamiento_status['archivo_actual'] = datos.get('archivo', '')
        procesamiento_status['lineas_procesadas'] = datos.get('lineas_procesadas', 0)
        procesamiento_status['total_lineas'] = datos.get('total_lineas', 0)
        
        # Agregar mensaje al log
        if datos.get('mensaje'):
            procesamiento_status['mensajes'].append(datos.get('mensaje'))
        
        # Calcular progreso general si es posible
        if procesamiento_status['total_lineas'] > 0:
            procesamiento_status['progreso'] = min(99, int((procesamiento_status['lineas_procesadas'] / procesamiento_status['total_lineas']) * 100))
    
    return jsonify({'success': True})

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

@app.route('/seleccionar_carpeta/<tipo_ruta>', methods=['POST'])
def seleccionar_carpeta_ruta(tipo_ruta):
    """Permite seleccionar una carpeta usando el explorador de archivos."""
    try:
        # Mapear tipos de ruta a títulos descriptivos
        titulos = {
            'rep_plr': 'Seleccionar carpeta de datos Rep PLR',
            'no_entregas': 'Seleccionar carpeta de datos No Entregas',
            'vol_portafolio': 'Seleccionar carpeta de datos Vol Portafolio',
            'output_unificado': 'Seleccionar carpeta de salida unificada',
            'output_final': 'Seleccionar carpeta de salida final'
        }
        
        titulo = titulos.get(tipo_ruta, f'Seleccionar carpeta para {tipo_ruta}')
        
        # Abrir explorador de carpetas
        carpeta_seleccionada = seleccionar_carpeta(titulo)
        
        if carpeta_seleccionada:
            # Actualizar configuración
            config_actual = cargar_configuracion()
            config_actual['rutas_archivos'][tipo_ruta] = carpeta_seleccionada
            guardar_configuracion(config_actual)
            
            return jsonify({
                'success': True,
                'ruta': carpeta_seleccionada,
                'message': f'Carpeta seleccionada: {carpeta_seleccionada}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No se seleccionó ninguna carpeta'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al seleccionar carpeta: {str(e)}'
        }), 400

@app.route('/verificar_rutas')
def verificar_rutas():
    """Verifica las rutas configuradas."""
    return jsonify(verificar_rutas_configuracion())

# ===== NUEVAS RUTAS PARA EL MENÚ UNIFICADO =====

@app.route('/ejecutar_modulo/<modulo>', methods=['POST'])
def ejecutar_modulo_web(modulo):
    """Ejecuta un módulo específico desde la web."""
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
    
    # Mapeo de módulos a scripts
    modulos = {
        'todo': {
            'scripts': [
                'agrupar_datos_no_entregas_mejorado.py',
                'agrupar_datos_rep_plr.py', 
                'agrupar_datos_vol_portafolio.py',
                'unificar_datos_completos.py'
            ],
            'descripcion': 'TODO el procesamiento OTIF'
        },
        'no_entregas': {
            'scripts': ['agrupar_datos_no_entregas_mejorado.py'],
            'descripcion': 'Agrupación de datos NO ENTREGAS'
        },
        'rep_plr': {
            'scripts': ['agrupar_datos_rep_plr.py'],
            'descripcion': 'Agrupación de datos REP PLR'
        },
        'vol_portafolio': {
            'scripts': ['agrupar_datos_vol_portafolio.py'],
            'descripcion': 'Agrupación de datos VOL PORTAFOLIO'
        },
        'unificar': {
            'scripts': ['unificar_datos_completos.py'],
            'descripcion': 'Unificación de todos los datos'
        }
    }
    
    if modulo not in modulos:
        return jsonify({'error': f'Módulo "{modulo}" no reconocido'})
    
    def ejecutar_modulo_thread():
        """Ejecuta el módulo en un hilo separado."""
        global procesamiento_status
        
        try:
            procesamiento_status['en_proceso'] = True
            procesamiento_status['completado'] = False
            procesamiento_status['error'] = None
            procesamiento_status['mensajes'] = []
            procesamiento_status['progreso'] = 0
            
            config_modulo = modulos[modulo]
            scripts = config_modulo['scripts']
            descripcion = config_modulo['descripcion']
            
            procesamiento_status['mensajes'].append(f"🚀 EJECUTANDO: {descripcion}")
            procesamiento_status['mensajes'].append(f"📋 Scripts a ejecutar: {len(scripts)}")
            
            exitosos = 0
            
            for i, script in enumerate(scripts, 1):
                procesamiento_status['paso_actual'] = f'Paso {i}/{len(scripts)}: {script}'
                progreso_paso = (i / len(scripts)) * 100
                procesamiento_status['progreso'] = progreso_paso
                
                procesamiento_status['mensajes'].append(f"\n📋 PASO {i}/{len(scripts)}: {script}")
                
                if not ejecutar_script(script):
                    procesamiento_status['mensajes'].append(f"❌ Error en {script}")
                else:
                    exitosos += 1
                    procesamiento_status['mensajes'].append(f"✅ {script} completado exitosamente")
            
            # Resumen final
            procesamiento_status['mensajes'].append(f"\n📊 RESUMEN: {exitosos}/{len(scripts)} scripts exitosos")
            
            if exitosos == len(scripts):
                procesamiento_status['mensajes'].append("🎉 ¡Módulo completado exitosamente!")
                procesamiento_status['completado'] = True
            else:
                procesamiento_status['mensajes'].append("⚠️ Algunos scripts fallaron")
            
            procesamiento_status['progreso'] = 100
            
        except Exception as e:
            procesamiento_status['error'] = str(e)
            procesamiento_status['mensajes'].append(f"❌ Error general: {str(e)}")
        finally:
            procesamiento_status['en_proceso'] = False
    
    # Iniciar procesamiento en hilo separado
    thread = threading.Thread(target=ejecutar_modulo_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': f'Módulo "{modulo}" iniciado'})

@app.route('/verificar_estructura')
def verificar_estructura_web():
    """Verifica la estructura del sistema desde la web."""
    try:
        result = subprocess.run([sys.executable, "scripts/verificar_estructura.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'output': result.stdout,
                'error': result.stderr if result.stderr else None
            })
        else:
            return jsonify({
                'success': False,
                'output': result.stdout,
                'error': result.stderr
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al verificar estructura: {str(e)}'
        })

@app.route('/ver_archivos_generados')
def ver_archivos_generados_web():
    """Muestra los archivos generados por el sistema."""
    directorios = [
        ("Data/Output/calculo_otif", "📊 Archivos finales"),
        ("Data/Output_Unificado", "🔗 Archivos unificados"),
        ("Data/Rep PLR/Output", "📈 Archivos REP PLR"),
        ("Data/No Entregas/Output", "📦 Archivos No Entregas"),
        ("Data/Vol_Portafolio/Output", "📋 Archivos Vol Portafolio")
    ]
    
    resultado = {}
    
    for directorio, descripcion in directorios:
        resultado[directorio] = {
            'descripcion': descripcion,
            'existe': os.path.exists(directorio),
            'archivos': []
        }
        
        if os.path.exists(directorio):
            archivos = [f for f in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, f))]
            for archivo in archivos:
                ruta_completa = os.path.join(directorio, archivo)
                tamaño = os.path.getsize(ruta_completa)
                tamaño_mb = tamaño / (1024 * 1024)
                resultado[directorio]['archivos'].append({
                    'nombre': archivo,
                    'tamaño_mb': tamaño_mb
                })
    
    return jsonify(resultado)

@app.route('/informacion_sistema')
def informacion_sistema_web():
    """Muestra información completa del sistema."""
    info = {
        'version': 'Sistema OTIF Master v2.5',
        'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'scripts_disponibles': [],
        'configuracion': {},
        'logs': {}
    }
    
    # Scripts disponibles
    scripts_dir = "scripts"
    if os.path.exists(scripts_dir):
        scripts = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
        info['scripts_disponibles'] = scripts
    
    # Configuración
    try:
        config = cargar_configuracion()
        info['configuracion'] = {
            'archivo': 'configuracion_rutas.json',
            'ultima_actualizacion': config.get('ultima_actualizacion', 'No disponible')
        }
    except:
        info['configuracion'] = {'error': 'No se pudo cargar la configuración'}
    
    # Logs
    if os.path.exists("procesamiento_maestro.log"):
        tamaño = os.path.getsize("procesamiento_maestro.log")
        tamaño_kb = tamaño / 1024
        info['logs'] = {
            'log_principal': f'procesamiento_maestro.log ({tamaño_kb:.1f} KB)'
        }
    else:
        info['logs'] = {'log_principal': 'No encontrado'}
    
    return jsonify(info)

@app.route('/estadisticas_rendimiento')
def estadisticas_rendimiento_web():
    """Muestra estadísticas de rendimiento del sistema."""
    stats = {
        'tiempos_estimados': {
            'rep_plr': '1-2 minutos',
            'no_entregas': '2-3 minutos',
            'vol_portafolio': '1-2 minutos',
            'unificacion': '1-2 minutos',
            'total_completo': '5-10 minutos'
        },
        'requisitos_sistema': {
            'ram': 'Mínimo 8 GB (recomendado 16 GB)',
            'cpu': 'Mínimo 4 núcleos',
            'disco': 'Suficiente espacio para archivos temporales'
        },
        'archivos_principales_generados': [
            'rep_plr.parquet',
            'no_entregas.parquet',
            'vol_portafolio.parquet',
            'datos_completos_con_no_entregas.parquet'
        ]
    }
    
    return jsonify(stats)

@app.route('/limpiar_archivos_temporales', methods=['POST'])
def limpiar_archivos_temporales_web():
    """Limpia archivos temporales del sistema."""
    try:
        # Por ahora solo retorna un mensaje de que la función está en desarrollo
        return jsonify({
            'success': True,
            'message': 'Función de limpieza en desarrollo. Los archivos temporales se limpiarán automáticamente.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al limpiar archivos: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
