#!/usr/bin/env python3
"""
Script de diagnóstico para la transacción ZSD_INCIDENCIAS
Ayuda a identificar qué controles están disponibles en la interfaz
"""

import sys
import os
from datetime import datetime
from base_sap_script import BaseSAPScript

class DiagnosticoIncidencias(BaseSAPScript):
    """
    Script de diagnóstico para ZSD_INCIDENCIAS
    """
    
    def __init__(self, output_path="C:\\data"):
        super().__init__("DIAGNOSTICO_INCIDENCIAS", output_path)
        self.transaction_code = "zsd_incidencias"
    
    def list_all_controls(self):
        """
        Lista todos los controles disponibles en la interfaz actual
        """
        try:
            self.logger.info("Listando todos los controles disponibles...")
            
            # Obtener la ventana principal
            window = self.session.findById("wnd[0]")
            self.logger.info(f"Ventana principal: {window.text}")
            
            # Listar controles de la ventana
            self._list_controls_recursive("wnd[0]", 0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error listando controles: {e}")
            return False
    
    def _list_controls_recursive(self, parent_id, level):
        """
        Lista controles de forma recursiva
        """
        try:
            indent = "  " * level
            parent = self.session.findById(parent_id)
            
            # Intentar obtener hijos
            try:
                children = parent.children
                for i in range(children.count):
                    child = children.item(i)
                    child_id = f"{parent_id}/{child.id}"
                    self.logger.info(f"{indent}{child.id} ({child.type})")
                    
                    # Recursión limitada para evitar bucles infinitos
                    if level < 3:
                        self._list_controls_recursive(child_id, level + 1)
            except:
                pass
                
        except Exception as e:
            self.logger.warning(f"Error en recursión: {e}")
    
    def test_export_methods(self):
        """
        Prueba diferentes métodos de exportación
        """
        try:
            self.logger.info("Probando métodos de exportación...")
            
            methods = [
                ("Menú estándar", self._test_standard_menu),
                ("Menú contextual", self._test_context_menu),
                ("Atajo de teclado", self._test_keyboard_shortcut),
                ("Botón de exportación", self._test_export_button)
            ]
            
            for method_name, method_func in methods:
                self.logger.info(f"Probando: {method_name}")
                try:
                    if method_func():
                        self.logger.info(f"✓ {method_name}: EXITOSO")
                    else:
                        self.logger.info(f"✗ {method_name}: FALLÓ")
                except Exception as e:
                    self.logger.info(f"✗ {method_name}: ERROR - {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error probando métodos: {e}")
            return False
    
    def _test_standard_menu(self):
        """Prueba menú estándar"""
        try:
            self.session.findById("wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select
            return True
        except:
            return False
    
    def _test_context_menu(self):
        """Prueba menú contextual"""
        try:
            grid = self.session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell")
            grid.rightClick()
            return True
        except:
            return False
    
    def _test_keyboard_shortcut(self):
        """Prueba atajo de teclado"""
        try:
            self.session.findById("wnd[0]").sendVKey(5)  # Ctrl+E
            return True
        except:
            return False
    
    def _test_export_button(self):
        """Prueba botón de exportación"""
        try:
            # Buscar botón de exportación en toolbar
            toolbar = self.session.findById("wnd[0]/tbar[1]")
            return True
        except:
            return False
    
    def execute(self):
        """
        Ejecuta el diagnóstico
        """
        print("INICIANDO DIAGNÓSTICO ZSD_INCIDENCIAS")
        print("=" * 60)
        print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Conectar a SAP
            if not self.connect_sap():
                print("FALLO: No se pudo conectar a SAP")
                return False
            
            # Navegar a la transacción
            if not self.navigate_to_transaction(self.transaction_code):
                print("FALLO: No se pudo navegar a la transacción")
                return False
            
            # Presionar botón de selección
            if not self.press_selection_button():
                print("FALLO: No se pudo presionar botón de selección")
                return False
            
            # Limpiar campo de usuario
            self.clear_user_field()
            
            # Seleccionar fila específica
            if not self.select_row(12):
                print("FALLO: No se pudo seleccionar la fila")
                return False
            
            # Ejecutar reporte
            if not self.execute_report():
                print("FALLO: No se pudo ejecutar el reporte")
                return False
            
            # Listar controles disponibles
            print("\n" + "=" * 60)
            print("CONTROLES DISPONIBLES:")
            print("=" * 60)
            self.list_all_controls()
            
            # Probar métodos de exportación
            print("\n" + "=" * 60)
            print("PRUEBAS DE EXPORTACIÓN:")
            print("=" * 60)
            self.test_export_methods()
            
            print("\n" + "=" * 60)
            print("DIAGNÓSTICO COMPLETADO")
            print("=" * 60)
            print(f"Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"Error inesperado: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """
    Función principal
    """
    # Verificar argumentos de línea de comandos
    output_path = "C:\\data"
    
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
        print(f"Usando ruta personalizada: {output_path}")
    
    # Crear y ejecutar script
    script = DiagnosticoIncidencias(output_path)
    success = script.execute()
    
    if success:
        print("\nDiagnóstico completado exitosamente")
        sys.exit(0)
    else:
        print("\nDiagnóstico falló")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnóstico interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
