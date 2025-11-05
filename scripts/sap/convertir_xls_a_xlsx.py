#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir archivos XLS a XLSX en la carpeta SAP_Extraction
Autor: Sistema OTIF
Fecha: 2025
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict
import glob

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('conversion_xls.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ConvertidorXLS:
    """Clase para convertir archivos XLS a XLSX"""
    
    def __init__(self, ruta_base: str = r"C:\data\SAP_Extraction"):
        """
        Inicializar el convertidor
        
        Args:
            ruta_base (str): Ruta base donde están las carpetas con archivos XLS
        """
        self.ruta_base = Path(ruta_base)
        self.archivos_procesados = []
        self.errores = []
        self.archivos_movidos = []
        
        # Crear carpeta para archivos XLS convertidos
        self.carpeta_xls_convertidos = self.ruta_base / "XLS_Convertidos"
        self.carpeta_xls_convertidos.mkdir(exist_ok=True)
        
    def encontrar_archivos_xls(self) -> Dict[str, List[Path]]:
        """
        Encontrar todos los archivos XLS en las subcarpetas
        
        Returns:
            Dict[str, List[Path]]: Diccionario con carpeta como clave y lista de archivos XLS
        """
        archivos_por_carpeta = {}
        
        if not self.ruta_base.exists():
            logging.error(f"La ruta base {self.ruta_base} no existe")
            return archivos_por_carpeta
            
        # Buscar en cada subcarpeta
        for carpeta in self.ruta_base.iterdir():
            if carpeta.is_dir():
                archivos_xls = list(carpeta.glob("*.xls"))
                if archivos_xls:
                    archivos_por_carpeta[carpeta.name] = archivos_xls
                    logging.info(f"Encontrados {len(archivos_xls)} archivos XLS en {carpeta.name}")
        
        return archivos_por_carpeta
    
    def obtener_estructura_archivo_final(self, carpeta: str) -> Dict:
        """
        Obtener la estructura del archivo final.xlsx de una carpeta
        
        Args:
            carpeta (str): Nombre de la carpeta
            
        Returns:
            Dict: Información sobre la estructura del archivo final
        """
        carpeta_path = self.ruta_base / carpeta
        
        # Buscar archivos final.xlsx
        archivos_final = list(carpeta_path.glob("*final.xlsx"))
        
        if not archivos_final:
            logging.warning(f"No se encontró archivo final.xlsx en {carpeta}")
            return None
        
        archivo_final = archivos_final[0]  # Tomar el primero encontrado
        
        try:
            df_final = pd.read_excel(archivo_final)
            estructura = {
                'archivo': str(archivo_final),
                'columnas': list(df_final.columns),
                'num_columnas': len(df_final.columns),
                'tipos_datos': df_final.dtypes.to_dict(),
                'ejemplo_fila': df_final.iloc[0].to_dict() if len(df_final) > 0 else {}
            }
            logging.info(f"Estructura obtenida de {archivo_final.name}: {len(estructura['columnas'])} columnas")
            return estructura
            
        except Exception as e:
            logging.error(f"Error leyendo archivo final {archivo_final.name}: {str(e)}")
            return None
    
    def adaptar_dataframe_a_estructura(self, df: pd.DataFrame, estructura_final: Dict) -> pd.DataFrame:
        """
        Adaptar un DataFrame a la estructura del archivo final
        
        Args:
            df (pd.DataFrame): DataFrame a adaptar
            estructura_final (Dict): Estructura del archivo final
            
        Returns:
            pd.DataFrame: DataFrame adaptado
        """
        if not estructura_final:
            return df
        
        columnas_final = estructura_final['columnas']
        df_adaptado = df.copy()
        
        # Si el DataFrame tiene las mismas columnas, mantenerlas
        if list(df.columns) == columnas_final:
            logging.info("DataFrame ya tiene la estructura correcta")
            return df_adaptado
        
        # Si el DataFrame tiene más columnas que el final, tomar las primeras
        if len(df.columns) >= len(columnas_final):
            df_adaptado = df.iloc[:, :len(columnas_final)]
            df_adaptado.columns = columnas_final
            logging.info(f"DataFrame adaptado: {len(df.columns)} -> {len(columnas_final)} columnas")
        
        # Si el DataFrame tiene menos columnas, agregar columnas vacías
        elif len(df.columns) < len(columnas_final):
            columnas_faltantes = columnas_final[len(df.columns):]
            for col in columnas_faltantes:
                df_adaptado[col] = ''
            df_adaptado = df_adaptado[columnas_final]  # Reordenar columnas
            logging.info(f"DataFrame adaptado: {len(df.columns)} -> {len(columnas_final)} columnas (agregadas {len(columnas_faltantes)} vacías)")
        
        return df_adaptado
    
    def mover_archivo_xls(self, archivo_xls: Path, carpeta_origen: str) -> bool:
        """
        Mover archivo XLS convertido a la carpeta de archivos convertidos
        
        Args:
            archivo_xls (Path): Ruta del archivo XLS
            carpeta_origen (str): Nombre de la carpeta de origen
            
        Returns:
            bool: True si se movió exitosamente
        """
        try:
            # Crear subcarpeta con el nombre de la carpeta de origen
            subcarpeta = self.carpeta_xls_convertidos / carpeta_origen
            subcarpeta.mkdir(exist_ok=True)
            
            # Mover el archivo
            destino = subcarpeta / archivo_xls.name
            archivo_xls.rename(destino)
            
            logging.info(f"Archivo XLS movido: {archivo_xls.name} -> {destino}")
            self.archivos_movidos.append({
                'archivo': str(archivo_xls),
                'destino': str(destino),
                'carpeta_origen': carpeta_origen
            })
            
            return True
            
        except Exception as e:
            logging.error(f"Error moviendo archivo {archivo_xls.name}: {str(e)}")
            return False
    
    def detectar_formato_archivo(self, archivo_path: Path) -> str:
        """
        Detectar el formato real del archivo
        
        Args:
            archivo_path (Path): Ruta del archivo
            
        Returns:
            str: Formato detectado ('xls', 'csv', 'html', 'unknown')
        """
        try:
            with open(archivo_path, 'rb') as f:
                # Leer los primeros bytes para detectar el formato
                header = f.read(1024)
                
                # Detectar formato XLS real
                if header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                    return 'xls'
                
                # Detectar UTF-16 (archivos de texto con BOM)
                if header.startswith(b'\xff\xfe') or header.startswith(b'\xfe\xff'):
                    return 'csv_utf16'
                
                # Detectar UTF-8
                if header.startswith(b'\xef\xbb\xbf'):
                    return 'csv_utf8'
                
                # Detectar HTML
                if b'<html' in header.lower() or b'<table' in header.lower():
                    return 'html'
                
                # Intentar leer como texto para detectar CSV
                try:
                    with open(archivo_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                        if ',' in first_line or ';' in first_line or '\t' in first_line:
                            return 'csv_utf8'
                except:
                    pass
                
                # Intentar con diferentes encodings
                for encoding in ['latin1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(archivo_path, 'r', encoding=encoding) as f:
                            first_line = f.readline()
                            if ',' in first_line or ';' in first_line or '\t' in first_line:
                                return f'csv_{encoding}'
                    except:
                        continue
                
                return 'unknown'
                
        except Exception as e:
            logging.warning(f"Error detectando formato de {archivo_path.name}: {str(e)}")
            return 'unknown'
    
    def leer_archivo_como_dataframe(self, archivo_path: Path) -> pd.DataFrame:
        """
        Leer archivo como DataFrame independientemente del formato
        
        Args:
            archivo_path (Path): Ruta del archivo
            
        Returns:
            pd.DataFrame: DataFrame con los datos
        """
        formato = self.detectar_formato_archivo(archivo_path)
        logging.info(f"Formato detectado para {archivo_path.name}: {formato}")
        
        if formato == 'xls':
            # Archivo XLS real
            for motor in ['xlrd', 'openpyxl']:
                try:
                    return pd.read_excel(archivo_path, engine=motor)
                except Exception as e:
                    logging.warning(f"Error con motor {motor}: {str(e)}")
                    continue
            raise Exception("No se pudo leer el archivo XLS con ningún motor")
        
        elif formato.startswith('csv_'):
            # Archivo CSV con diferentes encodings
            encoding = formato.split('_')[1]
            separadores = [',', ';', '\t', '|']
            
            for sep in separadores:
                try:
                    df = pd.read_csv(archivo_path, encoding=encoding, sep=sep, low_memory=False, on_bad_lines='skip')
                    if len(df.columns) > 1:  # Si tiene más de una columna, probablemente es el separador correcto
                        logging.info(f"CSV leído con separador '{sep}' y encoding '{encoding}'")
                        return df
                except Exception as e:
                    logging.warning(f"Error con separador '{sep}': {str(e)}")
                    continue
            
            # Intentar con parámetros más permisivos
            try:
                df = pd.read_csv(archivo_path, encoding=encoding, sep=None, engine='python', 
                               on_bad_lines='skip', low_memory=False)
                logging.info(f"CSV leído con separador automático y encoding '{encoding}'")
                return df
            except Exception as e:
                logging.warning(f"Error con separador automático: {str(e)}")
            
            # Intentar leer línea por línea para archivos problemáticos
            try:
                logging.info("Intentando lectura línea por línea...")
                with open(archivo_path, 'r', encoding=encoding, errors='ignore') as f:
                    lines = f.readlines()
                
                # Crear DataFrame manualmente
                data = []
                for i, line in enumerate(lines):
                    if i < 10:  # Solo mostrar las primeras 10 líneas para debug
                        logging.info(f"Línea {i+1}: {line.strip()[:100]}...")
                    
                    # Intentar dividir por diferentes separadores
                    for sep in ['\t', ',', ';', '|']:
                        if sep in line:
                            parts = line.strip().split(sep)
                            if len(parts) > 1:
                                data.append(parts)
                                break
                    else:
                        # Si no encuentra separador, agregar como una sola columna
                        data.append([line.strip()])
                
                if data:
                    # Crear DataFrame con el número máximo de columnas encontradas
                    max_cols = max(len(row) for row in data)
                    for row in data:
                        while len(row) < max_cols:
                            row.append('')
                    
                    df = pd.DataFrame(data)
                    logging.info(f"DataFrame creado manualmente con {len(df)} filas y {len(df.columns)} columnas")
                    return df
                else:
                    raise Exception("No se pudieron extraer datos del archivo")
                    
            except Exception as e:
                raise Exception(f"No se pudo leer el CSV con encoding {encoding}: {str(e)}")
        
        elif formato == 'html':
            # Archivo HTML con tablas
            try:
                dfs = pd.read_html(archivo_path)
                if dfs:
                    logging.info(f"HTML leído, encontradas {len(dfs)} tablas")
                    return dfs[0]  # Retornar la primera tabla
                else:
                    raise Exception("No se encontraron tablas en el archivo HTML")
            except Exception as e:
                raise Exception(f"Error leyendo HTML: {str(e)}")
        
        else:
            # Intentar métodos alternativos
            try:
                # Intentar como Excel con diferentes motores
                for motor in ['xlrd', 'openpyxl']:
                    try:
                        return pd.read_excel(archivo_path, engine=motor)
                    except:
                        continue
                
                # Intentar como CSV con diferentes encodings
                for encoding in ['utf-8', 'latin1', 'cp1252', 'utf-16']:
                    try:
                        return pd.read_csv(archivo_path, encoding=encoding)
                    except:
                        continue
                
                raise Exception("No se pudo leer el archivo con ningún método")
                
            except Exception as e:
                raise Exception(f"Error en métodos alternativos: {str(e)}")

    def convertir_archivo(self, archivo_xls: Path, carpeta_destino: Path, carpeta_nombre: str) -> bool:
        """
        Convertir un archivo XLS a XLSX
        
        Args:
            archivo_xls (Path): Ruta del archivo XLS
            carpeta_destino (Path): Carpeta donde guardar el XLSX
            carpeta_nombre (str): Nombre de la carpeta de origen
            
        Returns:
            bool: True si la conversión fue exitosa
        """
        try:
            # Crear nombre del archivo XLSX
            nombre_xlsx = archivo_xls.stem + ".xlsx"
            ruta_xlsx = carpeta_destino / nombre_xlsx
            
            logging.info(f"Convirtiendo {archivo_xls.name} a {nombre_xlsx}")
            
            # Leer el archivo usando el método mejorado
            df = self.leer_archivo_como_dataframe(archivo_xls)
            
            # Obtener estructura del archivo final
            estructura_final = self.obtener_estructura_archivo_final(carpeta_nombre)
            
            # Adaptar DataFrame a la estructura del archivo final
            if estructura_final:
                df_adaptado = self.adaptar_dataframe_a_estructura(df, estructura_final)
                logging.info(f"DataFrame adaptado a estructura de archivo final: {len(df_adaptado.columns)} columnas")
            else:
                df_adaptado = df
                logging.warning("No se pudo obtener estructura del archivo final, manteniendo estructura original")
            
            # Guardar como XLSX
            df_adaptado.to_excel(ruta_xlsx, index=False, engine='openpyxl')
            
            logging.info(f"Archivo convertido exitosamente: {ruta_xlsx}")
            self.archivos_procesados.append({
                'original': str(archivo_xls),
                'convertido': str(ruta_xlsx),
                'filas': len(df_adaptado),
                'columnas': len(df_adaptado.columns),
                'formato_detectado': self.detectar_formato_archivo(archivo_xls),
                'estructura_adaptada': estructura_final is not None
            })
            
            # Mover archivo XLS a carpeta de convertidos
            self.mover_archivo_xls(archivo_xls, carpeta_nombre)
            
            return True
            
        except Exception as e:
            error_msg = f"Error convirtiendo {archivo_xls.name}: {str(e)}"
            logging.error(error_msg)
            self.errores.append({
                'archivo': str(archivo_xls),
                'error': str(e)
            })
            return False
    
    def procesar_carpeta(self, nombre_carpeta: str, archivos_xls: List[Path]) -> Dict:
        """
        Procesar todos los archivos XLS de una carpeta
        
        Args:
            nombre_carpeta (str): Nombre de la carpeta
            archivos_xls (List[Path]): Lista de archivos XLS a procesar
            
        Returns:
            Dict: Resumen del procesamiento
        """
        carpeta_path = self.ruta_base / nombre_carpeta
        exitosos = 0
        fallidos = 0
        
        logging.info(f"Procesando carpeta: {nombre_carpeta}")
        
        for archivo_xls in archivos_xls:
            if self.convertir_archivo(archivo_xls, carpeta_path, nombre_carpeta):
                exitosos += 1
            else:
                fallidos += 1
        
        return {
            'carpeta': nombre_carpeta,
            'exitosos': exitosos,
            'fallidos': fallidos,
            'total': len(archivos_xls)
        }
    
    def procesar_todos(self) -> Dict:
        """
        Procesar todos los archivos XLS encontrados
        
        Returns:
            Dict: Resumen completo del procesamiento
        """
        logging.info("Iniciando conversión de archivos XLS a XLSX")
        
        archivos_por_carpeta = self.encontrar_archivos_xls()
        
        if not archivos_por_carpeta:
            logging.warning("No se encontraron archivos XLS para procesar")
            return {'total_carpetas': 0, 'total_archivos': 0}
        
        resumen_carpetas = []
        total_archivos = 0
        total_exitosos = 0
        total_fallidos = 0
        
        for nombre_carpeta, archivos_xls in archivos_por_carpeta.items():
            resumen = self.procesar_carpeta(nombre_carpeta, archivos_xls)
            resumen_carpetas.append(resumen)
            
            total_archivos += resumen['total']
            total_exitosos += resumen['exitosos']
            total_fallidos += resumen['fallidos']
        
        resumen_final = {
            'total_carpetas': len(resumen_carpetas),
            'total_archivos': total_archivos,
            'total_exitosos': total_exitosos,
            'total_fallidos': total_fallidos,
            'total_movidos': len(self.archivos_movidos),
            'carpetas': resumen_carpetas,
            'archivos_procesados': self.archivos_procesados,
            'archivos_movidos': self.archivos_movidos,
            'errores': self.errores
        }
        
        self.mostrar_resumen(resumen_final)
        return resumen_final
    
    def mostrar_resumen(self, resumen: Dict):
        """
        Mostrar resumen del procesamiento
        
        Args:
            resumen (Dict): Resumen del procesamiento
        """
        print("\n" + "="*60)
        print("RESUMEN DE CONVERSIÓN XLS A XLSX")
        print("="*60)
        print(f"Total de carpetas procesadas: {resumen['total_carpetas']}")
        print(f"Total de archivos encontrados: {resumen['total_archivos']}")
        print(f"Conversiones exitosas: {resumen['total_exitosos']}")
        print(f"Conversiones fallidas: {resumen['total_fallidos']}")
        
        if resumen['carpetas']:
            print("\nDetalle por carpeta:")
            for carpeta in resumen['carpetas']:
                print(f"  {carpeta['carpeta']}: {carpeta['exitosos']}/{carpeta['total']} exitosos")
        
        if resumen['errores']:
            print(f"\nErrores encontrados ({len(resumen['errores'])}):")
            for error in resumen['errores']:
                print(f"  - {error['archivo']}: {error['error']}")
        
        if self.archivos_movidos:
            print(f"\nArchivos XLS movidos ({len(self.archivos_movidos)}):")
            for movido in self.archivos_movidos:
                print(f"  - {Path(movido['archivo']).name} -> {movido['carpeta_origen']}/")
        
        print("="*60)

def main():
    """Función principal"""
    try:
        # Verificar que pandas esté instalado
        import pandas as pd
        print("Pandas disponible [ok]")
        
        # Verificar que openpyxl esté disponible
        try:
            import openpyxl
            print("OpenPyXL disponible [ok]")
        except ImportError:
            print("[ADVERTENCIA]  OpenPyXL no está instalado. Instalando...")
            os.system("pip install openpyxl")
        
        # Crear instancia del convertidor
        convertidor = ConvertidorXLS()
        
        # Procesar todos los archivos
        resumen = convertidor.procesar_todos()
        
        # Guardar resumen en archivo JSON
        import json
        with open('resumen_conversion_xls.json', 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        
        print(f"\nResumen guardado en: resumen_conversion_xls.json")
        print(f"Log detallado guardado en: conversion_xls.log")
        
    except Exception as e:
        logging.error(f"Error en la función principal: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
