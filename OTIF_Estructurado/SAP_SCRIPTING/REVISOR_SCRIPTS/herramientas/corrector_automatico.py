#!/usr/bin/env python3
"""
🔧 CORRECTOR AUTOMÁTICO DE SCRIPTS SAP
=====================================

Esta herramienta automatiza la corrección de scripts VBScript que usan favoritos
para convertirlos al enfoque directo de transacciones.
"""

import os
import re
from datetime import datetime

class CorrectorScriptsSAP:
    def __init__(self):
        self.script_dir = "../data_script_sap"
        self.output_dir = "scripts_corregidos"
        self.analisis_dir = "analisis_por_script"
        
        # Mapeo de transacciones
        self.transacciones = {
            'rep_plr': 'zsd_rep_planeamiento',
            'y_dev_45': 'y_dev_45',
            'y_dev_74': 'y_dev_74', 
            'y_dev_82': 'y_dev_82',
            'z_devo_alv': 'z_devo_alv',
            'zhbo': 'zhbo'
        }
        
        # Mapeo de nodos favoritos a transacciones
        self.nodos_favoritos = {
            'F00120': 'zsd_rep_planeamiento',  # rep_plr
            'F00139': 'y_dev_45',              # y_dev_45
            'F00119': 'y_dev_74',              # y_dev_74
            'F00123': 'y_dev_82',              # y_dev_82
            'F00072': 'z_devo_alv',            # z_devo_alv
            'F00118': 'zhbo'                   # zhbo
        }

    def analizar_script(self, nombre_script):
        """Analiza un script y identifica problemas"""
        ruta_script = os.path.join(self.script_dir, nombre_script)
        
        if not os.path.exists(ruta_script):
            return None
            
        with open(ruta_script, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        problemas = []
        
        # Buscar navegación por favoritos
        if 'doubleClickNode' in contenido:
            problemas.append("❌ Usa navegación por favoritos")
            
        # Buscar fechas hardcodeadas
        if re.search(r'\d{2}\.\d{2}\.\d{4}', contenido):
            problemas.append("❌ Fecha hardcodeada encontrada")
            
        # Buscar rutas hardcodeadas
        if 'C:\\data' in contenido:
            problemas.append("❌ Ruta hardcodeada encontrada")
            
        # Buscar clics duplicados
        if contenido.count('btn[15]').press') > 1:
            problemas.append("❌ Clics duplicados en btn[15]")
            
        return problemas

    def corregir_script(self, nombre_script):
        """Corrige un script específico"""
        ruta_script = os.path.join(self.script_dir, nombre_script)
        
        if not os.path.exists(ruta_script):
            return False
            
        with open(ruta_script, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Identificar transacción
        transaccion = None
        for nodo, trans in self.nodos_favoritos.items():
            if nodo in contenido:
                transaccion = trans
                break
                
        if not transaccion:
            return False
            
        # Aplicar correcciones
        contenido_corregido = self._aplicar_correcciones(contenido, transaccion, nombre_script)
        
        # Guardar script corregido
        ruta_corregido = os.path.join(self.output_dir, f"{nombre_script}_CORREGIDO")
        with open(ruta_corregido, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
            
        return True

    def _aplicar_correcciones(self, contenido, transaccion, nombre_script):
        """Aplica las correcciones al contenido del script"""
        
        # 1. Reemplazar navegación por favoritos con transacción directa
        patron_favoritos = r'session\.findById\("wnd\[0\]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont\[0\]/shell"\)\.doubleClickNode "[^"]*"'
        reemplazo_transaccion = f'''session.findById("wnd[0]/tbar[0]/okcd").text = "{transaccion}"
session.findById("wnd[0]").sendVKey 0'''
        
        contenido = re.sub(patron_favoritos, reemplazo_transaccion, contenido)
        
        # 2. Reemplazar fechas hardcodeadas con fechas dinámicas
        patron_fecha = r'session\.findById\("wnd\[0\]/usr/ctxt[^"]*"\)\.text = "\d{2}\.\d{2}\.\d{4}"'
        reemplazo_fecha = '''Dim fechaHoy
fechaHoy = Day(Date) & "." & Month(Date) & "." & Year(Date)
session.findById("wnd[0]/usr/ctxtP_LFDAT-LOW").text = fechaHoy'''
        
        contenido = re.sub(patron_fecha, reemplazo_fecha, contenido)
        
        # 3. Reemplazar rutas hardcodeadas
        contenido = contenido.replace('"C:\\data"', f'"C:\\Data\\SAP_Automatizado\\{nombre_script}"')
        
        # 4. Eliminar clics duplicados en btn[15]
        contenido = re.sub(r'(session\.findById\("wnd\[0\]/tbar\[0\]/btn\[15\]"\)\.press\s*\n)+', 
                          'session.findById("wnd[0]/tbar[0]/btn[15]").press\n', contenido)
        
        return contenido

    def generar_reporte(self):
        """Genera un reporte de todas las correcciones"""
        reporte = []
        reporte.append("# 📊 REPORTE DE CORRECCIONES AUTOMÁTICAS")
        reporte.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        reporte.append("")
        
        for script in self.transacciones.keys():
            problemas = self.analizar_script(script)
            if problemas:
                reporte.append(f"## {script}")
                reporte.append("**Problemas encontrados:**")
                for problema in problemas:
                    reporte.append(f"- {problema}")
                reporte.append("")
                
                # Intentar corrección
                if self.corregir_script(script):
                    reporte.append("✅ **Script corregido exitosamente**")
                else:
                    reporte.append("❌ **Error en la corrección**")
                reporte.append("")
            else:
                reporte.append(f"## {script}")
                reporte.append("✅ **Sin problemas detectados**")
                reporte.append("")
        
        return "\n".join(reporte)

def main():
    """Función principal"""
    corrector = CorrectorScriptsSAP()
    
    print("🔧 Iniciando corrección automática de scripts SAP...")
    
    # Generar reporte
    reporte = corrector.generar_reporte()
    
    # Guardar reporte
    with open("REPORTE_CORRECCIONES_AUTOMATICAS.md", 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("✅ Corrección completada")
    print("📄 Reporte guardado en: REPORTE_CORRECCIONES_AUTOMATICAS.md")

if __name__ == "__main__":
    main()
