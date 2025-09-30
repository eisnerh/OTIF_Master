#!/usr/bin/env python3
"""
Script simple para remover emojis de archivos Python
"""

import os
import re

def remove_emojis_from_file(file_path):
    """Remueve emojis de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Lista de emojis a reemplazar
        emojis_to_replace = [
            '🔐', '✅', '❌', '📊', '📋', '🔍', '🔄', '📁', '📅', '📂',
            '🎉', '⚠️', '🧹', '🚀', '⏰', '💡', '🎯', '📈', '📉', '🔧',
            '🎪', '🎨', '🎭', '🎪', '🎯', '🎲', '🎳', '🎴', '🎵', '🎶'
        ]
        
        # Reemplazar emojis con texto simple
        for emoji in emojis_to_replace:
            if emoji == '🔐':
                content = content.replace(emoji, '[CONECTAR]')
            elif emoji == '✅':
                content = content.replace(emoji, '[OK]')
            elif emoji == '❌':
                content = content.replace(emoji, '[ERROR]')
            elif emoji == '📊':
                content = content.replace(emoji, '[DATOS]')
            elif emoji == '📋':
                content = content.replace(emoji, '[LISTA]')
            elif emoji == '🔍':
                content = content.replace(emoji, '[BUSCAR]')
            elif emoji == '🔄':
                content = content.replace(emoji, '[PROCESAR]')
            elif emoji == '📁':
                content = content.replace(emoji, '[ARCHIVO]')
            elif emoji == '📅':
                content = content.replace(emoji, '[FECHA]')
            elif emoji == '📂':
                content = content.replace(emoji, '[CARPETA]')
            elif emoji == '🎉':
                content = content.replace(emoji, '[EXITO]')
            elif emoji == '⚠️':
                content = content.replace(emoji, '[ADVERTENCIA]')
            elif emoji == '🧹':
                content = content.replace(emoji, '[LIMPIAR]')
            elif emoji == '🚀':
                content = content.replace(emoji, '[INICIAR]')
            elif emoji == '⏰':
                content = content.replace(emoji, '[TIEMPO]')
            elif emoji == '💡':
                content = content.replace(emoji, '[INFO]')
            elif emoji == '🎯':
                content = content.replace(emoji, '[OBJETIVO]')
            else:
                content = content.replace(emoji, '[EMOJI]')
        
        # Escribir archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Emojis removidos de: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("Removiendo emojis de archivos Python...")
    
    # Archivos a procesar
    files = [
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
    
    success = 0
    for file_name in files:
        if os.path.exists(file_name):
            if remove_emojis_from_file(file_name):
                success += 1
        else:
            print(f"Archivo no encontrado: {file_name}")
    
    print(f"Procesados: {success}/{len(files)} archivos")

if __name__ == "__main__":
    main()
