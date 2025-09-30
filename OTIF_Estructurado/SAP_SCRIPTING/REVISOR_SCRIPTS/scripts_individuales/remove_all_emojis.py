#!/usr/bin/env python3
"""
Script para remover TODOS los emojis de todos los archivos Python
"""

import os
import re

def remove_emojis_from_file(file_path):
    """Remueve emojis de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista completa de emojis a reemplazar
        emoji_replacements = {
            '🔐': '[CONECTAR]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '📊': '[DATOS]',
            '📋': '[LISTA]',
            '🔍': '[BUSCAR]',
            '🔄': '[PROCESAR]',
            '📁': '[ARCHIVO]',
            '📅': '[FECHA]',
            '📂': '[CARPETA]',
            '🎉': '[EXITO]',
            '⚠️': '[ADVERTENCIA]',
            '🧹': '[LIMPIAR]',
            '🚀': '[INICIAR]',
            '⏰': '[TIEMPO]',
            '💡': '[INFO]',
            '🎯': '[OBJETIVO]',
            '📈': '[CRECIMIENTO]',
            '📉': '[DECRECIMIENTO]',
            '🔧': '[HERRAMIENTA]',
            '🎪': '[CIRCO]',
            '🎨': '[ARTE]',
            '🎭': '[TEATRO]',
            '🎲': '[DADO]',
            '🎳': '[BOLICHE]',
            '🎴': '[CARTAS]',
            '🎵': '[MUSICA]',
            '🎶': '[NOTAS]'
        }
        
        # Reemplazar emojis
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Emojis removidos de: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("=== REMOVIENDO EMOJIS DE TODOS LOS ARCHIVOS ===")
    print()
    
    # Lista de archivos a procesar
    files_to_process = [
        'y_dev_45.py',
        'y_dev_74.py', 
        'y_dev_82.py',
        'zred.py',
        'z_devo_alv.py',
        'ejecutar_todos.py',
        'procesar_datos_sap.py',
        'procesar_todos_los_datos.py',
        'analizar_estructura_datos.py'
    ]
    
    success_count = 0
    total_count = len(files_to_process)
    
    for file_name in files_to_process:
        if os.path.exists(file_name):
            if remove_emojis_from_file(file_name):
                success_count += 1
        else:
            print(f"⚠ Archivo no encontrado: {file_name}")
    
    print()
    print("=== RESULTADO ===")
    print(f"✓ Archivos procesados: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("✓ TODOS LOS EMOJIS REMOVIDOS EXITOSAMENTE")
        print("✓ Los scripts ahora funcionarán sin errores de codificación")
    else:
        print("⚠ Algunos archivos no pudieron ser procesados")
    
    print()
    print("=== INSTRUCCIONES DE USO ===")
    print("1. Para procesar archivos existentes:")
    print("   python analizar_estructura_datos.py")
    print("   python procesar_todos_los_datos.py")
    print()
    print("2. Para generar nuevos reportes SAP:")
    print("   python rep_plr.py")
    print("   python zhbo.py")
    print("   python ejecutar_todos.py")

if __name__ == "__main__":
    main()
