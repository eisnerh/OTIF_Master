#!/usr/bin/env python3
"""
Script maestro que ejecuta todos los scripts SAP individuales
Basado en el patrón del script maestro de Nite
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def ejecutar_script(script_name, script_path, *args):
    """
    Ejecuta un script Python específico
    
    Args:
        script_name (str): Nombre del script para logging
        script_path (str): Ruta al script
        *args: Argumentos adicionales para el script
    """
    print(f"🚀 Ejecutando {script_name}...")
    print("=" * 60)
    
    try:
        # Construir comando
        cmd = [sys.executable, script_path] + list(args)
        
        # Ejecutar script
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print(f"✅ {script_name} ejecutado exitosamente")
            return True
        else:
            print(f"❌ Error en {script_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando {script_name}: {e}")
        return False

def main():
    """
    Función principal que ejecuta todos los scripts
    """
    print("🚀 INICIANDO EJECUCIÓN DE TODOS LOS SCRIPTS SAP")
    print("=" * 80)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Lista de scripts a ejecutar
    scripts = [
        ("REP_PLR", "y_rep_plr.py"),
        ("Y_DEV_45", "y_dev_45.py"),
        ("Y_DEV_74", "y_dev_74.py"),
        ("Y_DEV_82", "y_dev_82.py"),
        ("ZHBO", "zhbo.py"),
        ("ZRED", "zred.py"),
        ("Z_DEVO_ALV", "z_devo_alv.py"),
        ("ZSD_INCIDENCIAS", "zsd_incidencias.py")
    ]
    
    # Verificar argumentos de línea de comandos
    custom_date = None
    output_path = "C:\\data"
    use_dynamic_date = True
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "dynamic":
            use_dynamic_date = True
            print("📅 Usando fecha dinámica automática")
        else:
            custom_date = sys.argv[1]
            use_dynamic_date = False
            print(f"📅 Usando fecha personalizada: {custom_date}")
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        print(f"📂 Usando ruta personalizada: {output_path}")
    
    # Mostrar lógica de fechas
    if use_dynamic_date:
        today = datetime.now()
        weekday = today.weekday()
        if weekday == 0:  # Lunes
            print("📅 Lógica: Es lunes - ejecutando reportes del sábado")
        else:
            print("📅 Lógica: Ejecutando reportes de ayer")
    
    results = {}
    total_scripts = len(scripts)
    
    print(f"\n📊 Ejecutando {total_scripts} scripts...")
    print("=" * 80)
    
    for i, (script_name, script_file) in enumerate(scripts, 1):
        print(f"\n📋 Procesando {i}/{total_scripts}: {script_name}")
        
        # Preparar argumentos
        args = [output_path]
        if script_name in ["REP_PLR", "ZHBO"]:
            if use_dynamic_date:
                # Los scripts usarán fecha dinámica automáticamente
                args = [output_path]
            elif custom_date:
                args = [custom_date, output_path]
        
        # Ejecutar script
        success = ejecutar_script(script_name, script_file, *args)
        results[script_name] = success
        
        # Pausa entre scripts
        if i < total_scripts:
            print(f"⏳ Esperando 3 segundos antes del siguiente script...")
            time.sleep(3)
    
    # Resumen final
    successful = sum(1 for success in results.values() if success)
    
    print("\n" + "=" * 80)
    print("📋 RESUMEN FINAL")
    print("=" * 80)
    print(f"✅ Scripts exitosos: {successful}/{total_scripts}")
    print(f"❌ Scripts fallidos: {total_scripts - successful}/{total_scripts}")
    print("\n📊 Detalle por script:")
    
    for script_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {script_name}")
    
    print(f"\n⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return successful == total_scripts

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Todos los scripts ejecutados exitosamente")
            sys.exit(0)
        else:
            print("\n⚠️  Algunos scripts fallaron")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Ejecución interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
