#!/usr/bin/env python3
"""
Script simple para remover TODOS los emojis de todos los archivos
"""

import os
import re

def remove_emojis_from_file(file_path):
    """Remueve TODOS los emojis de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón regex para encontrar emojis Unicode
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & pictographs
            "\U0001F680-\U0001F6FF"  # Transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # Flags (iOS)
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed characters
            "]+", flags=re.UNICODE)
        
        # Reemplazar emojis con texto simple
        content = emoji_pattern.sub('', content)
        
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
    print("=== REMOVIENDO TODOS LOS EMOJIS ===")
    print()
    
    # Lista de archivos a procesar
    files_to_process = [
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
    
    for file_name in files_to_process:
        if os.path.exists(file_name):
            if remove_emojis_from_file(file_name):
                success_count += 1
        else:
            print(f"⚠ Archivo no encontrado: {file_name}")
    
    print()
    print(f"✓ Archivos procesados: {success_count}")
    print("✓ TODOS LOS EMOJIS REMOVIDOS")
    print()
    print("=== INSTRUCCIONES ===")
    print("1. Para procesar archivos existentes:")
    print("   python analizar_estructura_datos.py")
    print("   python procesar_todos_los_datos.py")
    print()
    print("2. Para generar nuevos reportes:")
    print("   python rep_plr.py")
    print("   python zhbo.py")
    print("   python ejecutar_todos.py")

if __name__ == "__main__":
    main()
