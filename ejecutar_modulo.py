#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SISTEMA UNIFICADO DE EJECUCIÓN OTIF
Script principal para ejecutar todo el procesamiento OTIF de forma simple y eficiente

Uso:
  python ejecutar_modulo.py [modulo]     # Ejecución directa
  python ejecutar_modulo.py              # Modo interactivo
  python ejecutar_modulo.py help         # Mostrar ayuda
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

def mostrar_banner():
    """Muestra el banner del sistema"""
    print("🎯" + "="*60 + "🎯")
    print("           SISTEMA UNIFICADO DE PROCESAMIENTO OTIF")
    print("🎯" + "="*60 + "🎯")
    print()

def mostrar_ayuda():
    """Muestra la ayuda completa del sistema"""
    mostrar_banner()
    print("📋 OPCIONES DE EJECUCIÓN:")
    print("=" * 50)
    print()
    print("🚀 EJECUCIÓN DIRECTA:")
    print("  python ejecutar_modulo.py [modulo]")
    print()
    print("🖥️  MODO INTERACTIVO:")
    print("  python ejecutar_modulo.py")
    print()
    print("📊 MÓDULOS DISPONIBLES:")
    print("  todo          - Ejecutar TODO el procesamiento")
    print("  no_entregas   - Solo agrupar datos NO ENTREGAS")
    print("  rep_plr       - Solo agrupar datos REP PLR")
    print("  vol_portafolio - Solo agrupar datos VOL PORTAFOLIO")
    print("  unificar      - Solo unificar todos los datos")
    print("  rutas         - Verificar estado de rutas")
    print("  resumen       - Ver resumen de procesamiento")
    print("  web           - Iniciar aplicación web")
    print("  verificar     - Verificar estructura del sistema")
    print()
    print("🎯 EJEMPLOS:")
    print("  python ejecutar_modulo.py todo")
    print("  python ejecutar_modulo.py no_entregas")
    print("  python ejecutar_modulo.py no_entregas rep_plr")
    print("  python ejecutar_modulo.py rutas")
    print("  python ejecutar_modulo.py web")
    print()

def mostrar_menu_interactivo():
    """Muestra el menú interactivo"""
    print("🎯 SISTEMA UNIFICADO OTIF - MENÚ INTERACTIVO")
    print("=" * 50)
    print("1. 🔄 Ejecutar TODO el procesamiento")
    print("2. 📊 Agrupar datos NO ENTREGAS")
    print("3. 📈 Agrupar datos REP PLR")
    print("4. 📋 Agrupar datos VOL PORTAFOLIO")
    print("5. 🔗 Unificar todos los datos")
    print("6. 🔍 Verificar estado de rutas")
    print("7. 📊 Ver resumen de procesamiento")
    print("8. 🌐 Iniciar aplicación web")
    print("9. ✅ Verificar estructura del sistema")
    print("0. ❌ Salir")
    print("=" * 50)

def ejecutar_modulo(modulo):
    """Ejecuta un módulo específico"""
    
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
    
    # Casos especiales
    if modulo == 'rutas':
        print("🔍 VERIFICANDO ESTADO DE RUTAS")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "verificar_estado_rutas.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("⚠️  ADVERTENCIAS:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        return
    
    if modulo == 'resumen':
        print("📊 RESUMEN DE PROCESAMIENTO")
        print("=" * 40)
        try:
            archivos_resumen = [
                "Data/Output/calculo_otif/resumen_procesamiento.json",
                "resumen_procesamiento.json"
            ]
            
            for archivo in archivos_resumen:
                if os.path.exists(archivo):
                    with open(archivo, 'r', encoding='utf-8') as f:
                        resumen = json.load(f)
                    
                    print(f"📁 Archivo: {archivo}")
                    print(f"📅 Fecha: {resumen.get('fecha_procesamiento', 'No disponible')}")
                    print(f"⏱️  Tiempo total: {resumen.get('tiempo_total', 'No disponible')}")
                    
                    if 'estadisticas' in resumen:
                        print("\n📈 ESTADÍSTICAS:")
                        for key, value in resumen['estadisticas'].items():
                            print(f"   • {key}: {value}")
                    break
            else:
                print("❌ No se encontró ningún archivo de resumen")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        return
    
    if modulo == 'web':
        print("🌐 INICIANDO APLICACIÓN WEB")
        print("=" * 40)
        try:
            print("🚀 Iniciando servidor web...")
            print("📱 La aplicación estará disponible en: http://localhost:5000")
            print("🛑 Presiona Ctrl+C para detener el servidor")
            print()
            subprocess.run([sys.executable, "app.py"])
        except KeyboardInterrupt:
            print("\n🛑 Servidor web detenido")
        except Exception as e:
            print(f"❌ Error al iniciar aplicación web: {str(e)}")
        return
    
    if modulo == 'verificar':
        print("✅ VERIFICANDO ESTRUCTURA DEL SISTEMA")
        print("=" * 40)
        try:
            result = subprocess.run([sys.executable, "scripts/verificar_estructura.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("⚠️  ADVERTENCIAS:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        return
    
    # Verificar si el módulo existe
    if modulo not in modulos:
        print(f"❌ Error: Módulo '{modulo}' no reconocido")
        mostrar_ayuda()
        return
    
    # Ejecutar el módulo
    config_modulo = modulos[modulo]
    scripts = config_modulo['scripts']
    descripcion = config_modulo['descripcion']
    
    print(f"🚀 EJECUTANDO: {descripcion}")
    print(f"📋 Scripts a ejecutar: {len(scripts)}")
    print("=" * 50)
    
    start_time = time.time()
    exitosos = 0
    
    for i, script in enumerate(scripts, 1):
        print(f"\n📋 PASO {i}/{len(scripts)}: {script}")
        print("-" * 40)
        
        # Verificar si el script existe
        if not os.path.exists(f"scripts/{script}"):
            print(f"❌ Error: No se encontró el script {script}")
            continue
        
        try:
            # Ejecutar el script
            result = subprocess.run(
                [sys.executable, f"scripts/{script}"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # Mostrar salida
            if result.stdout:
                print("📤 SALIDA:")
                print(result.stdout)
            
            if result.stderr:
                print("⚠️  ADVERTENCIAS/ERRORES:")
                print(result.stderr)
            
            # Verificar resultado
            if result.returncode == 0:
                print(f"✅ {script} completado exitosamente")
                exitosos += 1
            else:
                print(f"❌ Error en {script} (código: {result.returncode})")
                
        except Exception as e:
            print(f"❌ Error inesperado en {script}: {str(e)}")
    
    # Resumen final
    end_time = time.time()
    tiempo_total = end_time - start_time
    
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE EJECUCIÓN")
    print(f"{'='*50}")
    print(f"✅ Scripts exitosos: {exitosos}/{len(scripts)}")
    print(f"⏱️  Tiempo total: {tiempo_total:.2f} segundos")
    
    if exitosos == len(scripts):
        print("🎉 ¡Módulo completado exitosamente!")
    else:
        print("⚠️  Algunos scripts fallaron")

def modo_interactivo():
    """Ejecuta el modo interactivo"""
    while True:
        mostrar_menu_interactivo()
        
        try:
            opcion = input("\n🔢 Selecciona una opción: ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                ejecutar_modulo("todo")
            elif opcion == "2":
                ejecutar_modulo("no_entregas")
            elif opcion == "3":
                ejecutar_modulo("rep_plr")
            elif opcion == "4":
                ejecutar_modulo("vol_portafolio")
            elif opcion == "5":
                ejecutar_modulo("unificar")
            elif opcion == "6":
                ejecutar_modulo("rutas")
            elif opcion == "7":
                ejecutar_modulo("resumen")
            elif opcion == "8":
                ejecutar_modulo("web")
            elif opcion == "9":
                ejecutar_modulo("verificar")
            else:
                print("❌ Opción inválida. Por favor selecciona una opción válida.")
            
            if opcion in ["1", "2", "3", "4", "5"]:
                input("\n⏸️  Presiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n🛑 Procesamiento interrumpido por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            input("Presiona Enter para continuar...")

def main():
    """Función principal"""
    # Si no hay argumentos, mostrar menú interactivo
    if len(sys.argv) < 2:
        modo_interactivo()
        return
    
    modulo = sys.argv[1].lower()
    
    # Mostrar ayuda si se solicita
    if modulo in ['help', '--help', '-h', 'ayuda']:
        mostrar_ayuda()
        return
    
    # Ejecutar módulos múltiples si se especifican
    if len(sys.argv) > 2:
        print("🔄 EJECUTANDO MÚLTIPLES MÓDULOS")
        print("=" * 40)
        for mod in sys.argv[1:]:
            print(f"\n📋 EJECUTANDO: {mod}")
            print("-" * 30)
            ejecutar_modulo(mod.lower())
    else:
        ejecutar_modulo(modulo)

if __name__ == "__main__":
    main()
