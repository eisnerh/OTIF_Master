#!/usr/bin/env python3
"""
Script maestro que ejecuta todos los reportes usando la lógica del entorno Nite
Replica la funcionalidad exitosa del entorno Nite en todos los scripts
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def ejecutar_script_incidencias():
    """
    Ejecuta el script de incidencias
    """
    print("📊 Ejecutando ZSD_INCIDENCIAS...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "zsd_incidencias.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ ZSD_INCIDENCIAS ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en ZSD_INCIDENCIAS: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando ZSD_INCIDENCIAS: {e}")
        return False

def ejecutar_script_mb51():
    """
    Ejecuta el script MB51
    """
    print("\n📊 Ejecutando MB51...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "mb51.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ MB51 ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en MB51: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando MB51: {e}")
        return False

def ejecutar_script_rep_plr():
    """
    Ejecuta el script REP_PLR
    """
    print("\n📊 Ejecutando REP_PLR...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "rep_plr.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ REP_PLR ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en REP_PLR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando REP_PLR: {e}")
        return False

def ejecutar_script_y_dev_45():
    """
    Ejecuta el script Y_DEV_45
    """
    print("\n📊 Ejecutando Y_DEV_45...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "y_dev_45.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Y_DEV_45 ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en Y_DEV_45: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Y_DEV_45: {e}")
        return False

def ejecutar_script_y_dev_74():
    """
    Ejecuta el script Y_DEV_74
    """
    print("\n📊 Ejecutando Y_DEV_74...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "y_dev_74.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Y_DEV_74 ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en Y_DEV_74: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Y_DEV_74: {e}")
        return False

def ejecutar_script_y_dev_82():
    """
    Ejecuta el script Y_DEV_82
    """
    print("\n📊 Ejecutando Y_DEV_82...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "y_dev_82.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Y_DEV_82 ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en Y_DEV_82: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Y_DEV_82: {e}")
        return False

def ejecutar_script_z_devo_alv():
    """
    Ejecuta el script Z_DEVO_ALV
    """
    print("\n📊 Ejecutando Z_DEVO_ALV...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "z_devo_alv.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Z_DEVO_ALV ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en Z_DEVO_ALV: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Z_DEVO_ALV: {e}")
        return False

def ejecutar_script_zhbo():
    """
    Ejecuta el script ZHBO
    """
    print("\n📊 Ejecutando ZHBO...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "zhbo.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ ZHBO ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en ZHBO: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando ZHBO: {e}")
        return False

def ejecutar_script_zred():
    """
    Ejecuta el script ZRED
    """
    print("\n📊 Ejecutando ZRED...")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "zred.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ ZRED ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en ZRED: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando ZRED: {e}")
        return False

def verificar_archivos_generados():
    """
    Verifica que los archivos se hayan generado correctamente
    """
    print("\n🔍 Verificando archivos generados...")
    print("=" * 60)
    
    # Lista de archivos esperados
    archivos_esperados = [
        "data_incidencias.xls",
        "data_mb51.xls", 
        "data_rep_plr.xls",
        "data_y_dev_45.xls",
        "data_y_dev_74.xls", 
        "data_y_dev_82.xls",
        "data_z_devo_alv.xls",
        "data_zhbo.xls",
        "data_zred.xls"
    ]
    
    archivos_encontrados = 0
    directorio_base = "C:\\data"
    
    for archivo in archivos_esperados:
        ruta_archivo = os.path.join(directorio_base, archivo)
        if os.path.exists(ruta_archivo):
            tamaño = os.path.getsize(ruta_archivo)
            print(f"✅ {archivo} - {tamaño:,} bytes")
            archivos_encontrados += 1
        else:
            print(f"❌ {archivo} - No encontrado")
    
    print(f"\n📊 Archivos generados: {archivos_encontrados}/{len(archivos_esperados)}")
    
    if archivos_encontrados == len(archivos_esperados):
        print("🎉 Todos los archivos se generaron correctamente")
        return True
    else:
        print("⚠️  Algunos archivos no se generaron")
        return False

def main():
    """
    Función principal que ejecuta todo el flujo
    """
    print("🚀 INICIANDO SCRIPT MAESTRO - ESTILO NITE")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Lista de scripts a ejecutar
    scripts = [
        ("ZSD_INCIDENCIAS", ejecutar_script_incidencias),
        ("MB51", ejecutar_script_mb51),
        ("REP_PLR", ejecutar_script_rep_plr),
        ("Y_DEV_45", ejecutar_script_y_dev_45),
        ("Y_DEV_74", ejecutar_script_y_dev_74),
        ("Y_DEV_82", ejecutar_script_y_dev_82),
        ("Z_DEVO_ALV", ejecutar_script_z_devo_alv),
        ("ZHBO", ejecutar_script_zhbo),
        ("ZRED", ejecutar_script_zred)
    ]
    
    exitosos = 0
    fallidos = 0
    
    # Ejecutar cada script
    for nombre, funcion in scripts:
        print(f"\n🔄 Ejecutando {nombre}...")
        if funcion():
            exitosos += 1
            print(f"✅ {nombre} completado exitosamente")
        else:
            fallidos += 1
            print(f"❌ {nombre} falló")
        
        # Esperar entre scripts para evitar conflictos
        print("⏳ Esperando 3 segundos antes del siguiente script...")
        time.sleep(3)
    
    # Verificar archivos generados
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN FINAL")
    print("=" * 80)
    verificar_archivos_generados()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Scripts exitosos: {exitosos}")
    print(f"❌ Scripts fallidos: {fallidos}")
    print(f"📁 Archivos generados en: C:\\data")
    print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if fallidos == 0:
        print("🎉 TODOS LOS SCRIPTS COMPLETADOS EXITOSAMENTE")
        return True
    else:
        print(f"⚠️  {fallidos} SCRIPTS FALLARON")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Proceso completado exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Proceso completado con errores")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
