#!/usr/bin/env python3
"""
Script para remover emojis de los archivos Python y evitar errores de codificación
"""

import re
import os

def remove_emojis_from_file(file_path):
    """
    Remueve emojis de un archivo Python
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar emojis comunes con texto
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
            '🎯': '[OBJETIVO]'
        }
        
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Emojis removidos de: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """
    Remueve emojis de todos los archivos Python en el directorio
    """
    print("Removiendo emojis de archivos Python...")
    
    # Lista de archivos a procesar
    files_to_process = [
        'base_sap_script.py',
        'rep_plr.py',
        'y_dev_45.py',
        'y_dev_74.py',
        'y_dev_82.py',
        'zhbo.py',
        'zred.py',
        'z_devo_alv.py',
        'zsd_incidencias.py',
        'ejecutar_todos.py',
        'procesar_datos_sap.py',
        'procesar_todos_los_datos.py',
        'analizar_estructura_datos.py'
    ]
    
    success_count = 0
    
    for file_name in files_to_process:
        if os.path.exists(file_name):
            if remove_emojis_from_file(file_name):
                success_count += 1
        else:
            print(f"Archivo no encontrado: {file_name}")
    
    print(f"\nProcesamiento completado: {success_count}/{len(files_to_process)} archivos")

if __name__ == "__main__":
    main()
