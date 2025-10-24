#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EJEMPLO DE USO DEL SISTEMA DE FAVORITOS
Script de ejemplo que muestra como usar el sistema de favoritos
"""

import json
from datetime import datetime

def crear_favoritos_ejemplo():
    """Crea un archivo de favoritos de ejemplo"""
    favoritos_ejemplo = {
        "scripts": [
            {
                "nombre": "Procesar REP PLR",
                "ruta": "scripts/agrupar_datos_rep_plr.py",
                "descripcion": "Script para agrupar datos REP PLR",
                "fecha_agregado": datetime.now().isoformat()
            },
            {
                "nombre": "Procesar No Entregas",
                "ruta": "scripts/agrupar_datos_no_entregas_mejorado.py",
                "descripcion": "Script para agrupar datos No Entregas",
                "fecha_agregado": datetime.now().isoformat()
            },
            {
                "nombre": "Unificar Datos",
                "ruta": "scripts/unificar_datos_completos.py",
                "descripcion": "Script para unificar todos los datos",
                "fecha_agregado": datetime.now().isoformat()
            }
        ],
        "notebooks": [
            {
                "nombre": "Consolidar Zresguias",
                "ruta": "OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_zresguias_excel.ipynb",
                "descripcion": "Notebook para consolidar datos de zresguias",
                "fecha_agregado": datetime.now().isoformat()
            }
        ],
        "carpetas": [
            {
                "nombre": "Carpeta de Salida",
                "ruta": "Data/Output/calculo_otif",
                "descripcion": "Carpeta con archivos de salida del sistema",
                "fecha_agregado": datetime.now().isoformat()
            },
            {
                "nombre": "Scripts SAP",
                "ruta": "OTIF_Estructurado/SAP_SCRIPTING",
                "descripcion": "Carpeta con scripts de automatizacion SAP",
                "fecha_agregado": datetime.now().isoformat()
            }
        ]
    }
    
    try:
        with open("favoritos.json", 'w', encoding='utf-8') as f:
            json.dump(favoritos_ejemplo, f, indent=2, ensure_ascii=False)
        print("Archivo de favoritos de ejemplo creado exitosamente")
        print("Ahora puedes usar el menu completo para gestionar tus favoritos")
        return True
    except Exception as e:
        print(f"ERROR al crear favoritos de ejemplo: {str(e)}")
        return False

def mostrar_favoritos_ejemplo():
    """Muestra los favoritos de ejemplo"""
    try:
        with open("favoritos.json", 'r', encoding='utf-8') as f:
            favoritos = json.load(f)
        
        print("FAVORITOS DE EJEMPLO")
        print("=" * 50)
        
        if favoritos["scripts"]:
            print("\nSCRIPTS FAVORITOS:")
            for i, script in enumerate(favoritos["scripts"], 1):
                print(f"  {i}. {script['nombre']}")
                print(f"     Ruta: {script['ruta']}")
                print(f"     Descripcion: {script['descripcion']}")
                print()
        
        if favoritos["notebooks"]:
            print("\nNOTEBOOKS FAVORITOS:")
            for i, notebook in enumerate(favoritos["notebooks"], 1):
                print(f"  {i}. {notebook['nombre']}")
                print(f"     Ruta: {notebook['ruta']}")
                print(f"     Descripcion: {notebook['descripcion']}")
                print()
        
        if favoritos["carpetas"]:
            print("\nCARPETAS FAVORITAS:")
            for i, carpeta in enumerate(favoritos["carpetas"], 1):
                print(f"  {i}. {carpeta['nombre']}")
                print(f"     Ruta: {carpeta['ruta']}")
                print(f"     Descripcion: {carpeta['descripcion']}")
                print()
        
    except Exception as e:
        print(f"ERROR al mostrar favoritos: {str(e)}")

def main():
    """Funcion principal"""
    print("SISTEMA DE FAVORITOS - EJEMPLO")
    print("=" * 40)
    print()
    print("Este script crea un archivo de favoritos de ejemplo")
    print("para que puedas probar el sistema de favoritos")
    print()
    
    respuesta = input("¿Deseas crear favoritos de ejemplo? (s/n): ").lower()
    
    if respuesta == 's':
        if crear_favoritos_ejemplo():
            print("\nFavoritos de ejemplo creados:")
            mostrar_favoritos_ejemplo()
            print("\nAhora puedes:")
            print("1. Ejecutar: python menu_completo.py")
            print("2. Seleccionar opcion 24 (Gestion de favoritos)")
            print("3. Probar todas las funcionalidades")
        else:
            print("ERROR al crear favoritos de ejemplo")
    else:
        print("Operacion cancelada")

if __name__ == "__main__":
    main()
