import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime

def verificar_estado_rutas():
    """
    Verifica el estado de las rutas configuradas y cuenta archivos en cada directorio
    """
    print("🔍 VERIFICANDO ESTADO DE RUTAS Y CONTANDO ARCHIVOS")
    print("=" * 60)
    
    # Cargar configuración
    try:
        with open('configuracion_rutas.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo configuracion_rutas.json")
        return
    except json.JSONDecodeError:
        print("❌ Error: El archivo configuracion_rutas.json tiene formato inválido")
        return
    
    rutas = config.get('rutas_archivos', {})
    archivos_principales = config.get('archivos_principales', [])
    
    print(f"📅 Última actualización: {config.get('ultima_actualizacion', 'No disponible')}")
    print()
    
    # Verificar cada ruta
    for nombre_ruta, ruta in rutas.items():
        print(f"📁 RUTA: {nombre_ruta.upper()}")
        print(f"   📂 Directorio: {ruta}")
        
        # Verificar si la ruta existe
        if os.path.exists(ruta):
            print(f"   ✅ Estado: EXISTE")
            
            # Contar archivos en el directorio
            try:
                archivos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]
                print(f"   📊 Total archivos: {len(archivos)}")
                
                # Mostrar algunos archivos como ejemplo
                if archivos:
                    print(f"   📋 Ejemplos de archivos:")
                    for i, archivo in enumerate(archivos[:5]):  # Mostrar solo los primeros 5
                        print(f"      • {archivo}")
                    if len(archivos) > 5:
                        print(f"      ... y {len(archivos) - 5} archivos más")
                else:
                    print(f"   ⚠️  El directorio está vacío")
                    
            except PermissionError:
                print(f"   ❌ Error: Sin permisos para acceder al directorio")
            except Exception as e:
                print(f"   ❌ Error al listar archivos: {str(e)}")
                
        else:
            print(f"   ❌ Estado: NO EXISTE")
            print(f"   ⚠️  La ruta no es accesible")
        
        print()
    
    # Verificar archivos principales en el directorio actual
    print("📋 ARCHIVOS PRINCIPALES EN DIRECTORIO ACTUAL")
    print("-" * 40)
    
    archivos_existentes = []
    archivos_faltantes = []
    
    for archivo in archivos_principales:
        if os.path.exists(archivo):
            archivos_existentes.append(archivo)
            # Obtener información del archivo
            stat = os.stat(archivo)
            tamaño_mb = stat.st_size / (1024 * 1024)
            fecha_mod = datetime.fromtimestamp(stat.st_mtime)
            print(f"   ✅ {archivo}")
            print(f"      📏 Tamaño: {tamaño_mb:.2f} MB")
            print(f"      📅 Modificado: {fecha_mod.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            archivos_faltantes.append(archivo)
            print(f"   ❌ {archivo} - NO ENCONTRADO")
        print()
    
    # Resumen final
    print("📊 RESUMEN FINAL")
    print("=" * 40)
    print(f"   📁 Rutas configuradas: {len(rutas)}")
    print(f"   ✅ Archivos principales existentes: {len(archivos_existentes)}")
    print(f"   ❌ Archivos principales faltantes: {len(archivos_faltantes)}")
    
    if archivos_faltantes:
        print(f"\n⚠️  ARCHIVOS FALTANTES:")
        for archivo in archivos_faltantes:
            print(f"   • {archivo}")
    
    # Verificar archivos en Data/Output
    print(f"\n📂 ARCHIVOS EN Data/Output:")
    ruta_output = "Data/Output"
    if os.path.exists(ruta_output):
        archivos_output = [f for f in os.listdir(ruta_output) if os.path.isfile(os.path.join(ruta_output, f))]
        print(f"   📊 Total archivos: {len(archivos_output)}")
        for archivo in archivos_output:
            print(f"   • {archivo}")
    else:
        print(f"   ❌ El directorio {ruta_output} no existe")

if __name__ == "__main__":
    verificar_estado_rutas()
