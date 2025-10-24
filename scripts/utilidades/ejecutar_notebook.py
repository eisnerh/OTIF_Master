#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EJECUTOR DE NOTEBOOKS JUPYTER
Script para ejecutar notebooks de Jupyter desde la línea de comandos

Uso: python ejecutar_notebook.py <notebook_path>
"""

import sys
import os
import subprocess
import json
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

def ejecutar_notebook(notebook_path):
    """Ejecuta un notebook de Jupyter"""
    print(f"EJECUTANDO NOTEBOOK: {notebook_path}")
    print("=" * 50)
    
    try:
        # Verificar si el notebook existe
        if not os.path.exists(notebook_path):
            print(f"ERROR: No se encontro el notebook {notebook_path}")
            return False
        
        # Verificar si jupyter está instalado
        try:
            subprocess.run(["jupyter", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: Jupyter no esta instalado o no esta en el PATH")
            print("Instala jupyter con: pip install jupyter")
            return False
        
        # Cargar el notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Configurar el ejecutor
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        
        # Ejecutar el notebook
        print("Ejecutando celdas del notebook...")
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        
        # Guardar el notebook ejecutado
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        print("OK Notebook ejecutado exitosamente")
        return True
        
    except Exception as e:
        print(f"ERROR inesperado: {str(e)}")
        return False

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python ejecutar_notebook.py <notebook_path>")
        print("Ejemplo: python ejecutar_notebook.py OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_zresguias_excel.ipynb")
        return
    
    notebook_path = sys.argv[1]
    ejecutar_notebook(notebook_path)

if __name__ == "__main__":
    main()
