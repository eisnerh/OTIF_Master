#!/usr/bin/env python3
"""
🛠️ SCRIPT DE INSTALACIÓN Y CONFIGURACIÓN
========================================

Este script automatiza la instalación y configuración del sistema
de automatización de reportes SAP.

Funcionalidades:
✅ Verificación de requisitos del sistema
✅ Instalación de dependencias
✅ Configuración de directorios
✅ Creación de tarea programada en Windows
✅ Configuración de permisos
✅ Pruebas de conectividad SAP
"""

import os
import sys
import json
import subprocess
import win32com.client
import win32api
import win32con
from datetime import datetime

class InstaladorAutomatizacion:
    def __init__(self):
        self.directorio_base = r"C:\Data\SAP_Automatizado"
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        
    def verificar_python(self):
        """
        Verifica la versión de Python
        """
        print("🐍 Verificando Python...")
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.8+")
            return False
    
    def instalar_dependencias(self):
        """
        Instala las dependencias requeridas
        """
        print("📦 Instalando dependencias...")
        
        dependencias = [
            'pandas>=1.5.0',
            'openpyxl>=3.0.0',
            'pyarrow>=10.0.0',
            'pywin32>=305'
        ]
        
        for dep in dependencias:
            try:
                print(f"   Instalando {dep}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                print(f"   ✅ {dep} instalado correctamente")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Error instalando {dep}: {e}")
                return False
        
        return True
    
    def crear_directorios(self):
        """
        Crea la estructura de directorios necesaria
        """
        print("📁 Creando estructura de directorios...")
        
        directorios = [
            self.directorio_base,
            os.path.join(self.directorio_base, 'Logs'),
            os.path.join(self.directorio_base, 'Backup'),
            os.path.join(self.directorio_base, 'Reportes'),
            os.path.join(self.directorio_base, 'PowerBI')
        ]
        
        for directorio in directorios:
            try:
                os.makedirs(directorio, exist_ok=True)
                print(f"   ✅ Directorio creado: {directorio}")
            except Exception as e:
                print(f"   ❌ Error creando directorio {directorio}: {e}")
                return False
        
        return True
    
    def copiar_archivos(self):
        """
        Copia los archivos necesarios al directorio de instalación
        """
        print("📋 Copiando archivos de configuración...")
        
        archivos_copiar = [
            'automatizacion_reportes_sap.py',
            'ejecutar_diario.py',
            'configuracion_reportes.json'
        ]
        
        for archivo in archivos_copiar:
            try:
                origen = os.path.join(self.script_path, archivo)
                destino = os.path.join(self.directorio_base, archivo)
                
                if os.path.exists(origen):
                    import shutil
                    shutil.copy2(origen, destino)
                    print(f"   ✅ Archivo copiado: {archivo}")
                else:
                    print(f"   ⚠️ Archivo no encontrado: {archivo}")
            except Exception as e:
                print(f"   ❌ Error copiando {archivo}: {e}")
                return False
        
        return True
    
    def verificar_sap_gui(self):
        """
        Verifica que SAP GUI esté disponible
        """
        print("🔍 Verificando SAP GUI...")
        
        try:
            sap_gui_auto = win32com.client.GetObject("SAPGUI")
            if sap_gui_auto:
                print("   ✅ SAP GUI detectado y disponible")
                return True
            else:
                print("   ❌ SAP GUI no está disponible")
                return False
        except Exception as e:
            print(f"   ❌ Error verificando SAP GUI: {e}")
            return False
    
    def crear_tarea_programada(self):
        """
        Crea una tarea programada en Windows
        """
        print("⏰ Configurando tarea programada...")
        
        try:
            # Comando para crear la tarea
            script_ejecutar = os.path.join(self.directorio_base, 'ejecutar_diario.py')
            
            # Crear comando de PowerShell para la tarea programada
            ps_script = f"""
$Action = New-ScheduledTaskAction -Execute 'python' -Argument '{script_ejecutar}' -WorkingDirectory '{self.directorio_base}'
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId '{os.getenv('USERNAME')}' -LogonType InteractiveToken
Register-ScheduledTask -TaskName 'SAP_Reportes_Automaticos' -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description 'Extracción automática diaria de reportes SAP'
"""
            
            # Ejecutar PowerShell
            result = subprocess.run(['powershell', '-Command', ps_script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Tarea programada creada exitosamente")
                print("   📅 Programada para ejecutarse diariamente a las 08:00")
                return True
            else:
                print(f"   ❌ Error creando tarea programada: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error configurando tarea programada: {e}")
            return False
    
    def crear_script_inicio_rapido(self):
        """
        Crea un script para ejecución manual rápida
        """
        print("🚀 Creando script de inicio rápido...")
        
        script_content = f'''@echo off
echo 🚀 Iniciando extracción de reportes SAP...
echo.
cd /d "{self.directorio_base}"
python ejecutar_diario.py
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
'''
        
        try:
            script_path = os.path.join(self.directorio_base, 'ejecutar_ahora.bat')
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            print(f"   ✅ Script creado: {script_path}")
            return True
        except Exception as e:
            print(f"   ❌ Error creando script: {e}")
            return False
    
    def crear_documentacion(self):
        """
        Crea documentación de uso
        """
        print("📚 Creando documentación...")
        
        doc_content = f"""# 🚀 AUTOMATIZACIÓN DE REPORTES SAP

## 📋 Descripción
Sistema automatizado para la extracción diaria de 9 reportes de SAP con procesamiento para Power BI.

## 📁 Estructura de Archivos
```
{self.directorio_base}/
├── automatizacion_reportes_sap.py    # Script principal
├── ejecutar_diario.py                # Script de ejecución diaria
├── configuracion_reportes.json       # Configuración
├── ejecutar_ahora.bat                # Ejecución manual
├── Logs/                             # Archivos de log
├── Backup/                           # Respaldos
├── Reportes/                         # Reportes originales
└── PowerBI/                          # Archivos para Power BI
```

## 🕐 Ejecución Automática
- **Programada**: Diariamente a las 08:00
- **Lógica de fechas**: 
  - Lunes: Procesa sábado y domingo
  - Otros días: Procesa día anterior

## 🚀 Ejecución Manual
1. Doble clic en `ejecutar_ahora.bat`
2. O ejecutar: `python ejecutar_diario.py`

## 📊 Reportes Incluidos
1. **mb51** - Movimientos de material
2. **rep_plr** - Planificación logística
3. **y_dev_45** - Desarrollo 45
4. **y_dev_74** - Desarrollo 74
5. **y_dev_82** - Desarrollo 82
6. **z_devo_alv** - Devoluciones ALV
7. **zhbo** - HBO
8. **zred** - Red
9. **zsd_incidencias** - Incidencias SD

## 📁 Archivos Generados
Para cada reporte se generan:
- `[reporte]_[fecha].xls` - Archivo original SAP
- `[reporte]_[fecha]_PowerBI.xlsx` - Excel para Power BI
- `[reporte]_[fecha]_PowerBI.csv` - CSV para Power BI
- `[reporte]_[fecha]_PowerBI.parquet` - Parquet (recomendado)
- `[reporte]_[fecha]_Metadata.json` - Metadatos

## 🔧 Configuración
Editar `configuracion_reportes.json` para:
- Cambiar credenciales SAP
- Modificar directorios
- Activar/desactivar reportes
- Ajustar tiempos de espera

## 📋 Logs
Los logs se guardan en: `{self.directorio_base}\\Logs\\`

## ❗ Requisitos
- Python 3.8+
- SAP GUI
- Windows (Task Scheduler)
- Dependencias Python instaladas

## 🆘 Soporte
Para problemas o consultas, revisar los logs en la carpeta Logs.
"""
        
        try:
            doc_path = os.path.join(self.directorio_base, 'README.md')
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            print(f"   ✅ Documentación creada: {doc_path}")
            return True
        except Exception as e:
            print(f"   ❌ Error creando documentación: {e}")
            return False
    
    def realizar_prueba(self):
        """
        Realiza una prueba básica del sistema
        """
        print("🧪 Realizando prueba básica...")
        
        try:
            # Importar y probar el módulo principal
            sys.path.append(self.directorio_base)
            from automatizacion_reportes_sap import AutomatizacionSAP
            
            # Crear instancia
            automatizacion = AutomatizacionSAP()
            print("   ✅ Módulo principal importado correctamente")
            
            # Verificar configuración
            if automatizacion.reportes_config:
                print(f"   ✅ Configuración cargada: {len(automatizacion.reportes_config)} reportes")
            else:
                print("   ❌ Error en configuración")
                return False
            
            print("   ✅ Prueba básica completada")
            return True
            
        except Exception as e:
            print(f"   ❌ Error en prueba básica: {e}")
            return False
    
    def instalar(self):
        """
        Ejecuta la instalación completa
        """
        print("🛠️ INICIANDO INSTALACIÓN DE AUTOMATIZACIÓN SAP")
        print("=" * 60)
        
        pasos = [
            ("Verificar Python", self.verificar_python),
            ("Instalar dependencias", self.instalar_dependencias),
            ("Crear directorios", self.crear_directorios),
            ("Copiar archivos", self.copiar_archivos),
            ("Verificar SAP GUI", self.verificar_sap_gui),
            ("Crear tarea programada", self.crear_tarea_programada),
            ("Crear script inicio rápido", self.crear_script_inicio_rapido),
            ("Crear documentación", self.crear_documentacion),
            ("Realizar prueba", self.realizar_prueba)
        ]
        
        exitosos = 0
        fallidos = 0
        
        for paso, funcion in pasos:
            print(f"\n📋 {paso}...")
            try:
                if funcion():
                    exitosos += 1
                else:
                    fallidos += 1
            except Exception as e:
                print(f"   ❌ Error inesperado: {e}")
                fallidos += 1
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE INSTALACIÓN")
        print("=" * 60)
        print(f"✅ Pasos exitosos: {exitosos}")
        print(f"❌ Pasos fallidos: {fallidos}")
        print(f"📈 Porcentaje éxito: {(exitosos/(exitosos+fallidos)*100):.1f}%")
        
        if fallidos == 0:
            print("\n🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📁 Directorio de instalación: {self.directorio_base}")
            print("🚀 Puedes ejecutar 'ejecutar_ahora.bat' para probar")
        else:
            print(f"\n⚠️ INSTALACIÓN COMPLETADA CON {fallidos} ERRORES")
            print("Revisa los mensajes anteriores para más detalles")
        
        print("=" * 60)

if __name__ == "__main__":
    instalador = InstaladorAutomatizacion()
    instalador.instalar()
