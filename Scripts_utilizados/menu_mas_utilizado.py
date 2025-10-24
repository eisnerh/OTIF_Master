# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import shutil
from datetime import datetime, timedelta
import threading
import sys

# Diccionario de nombres amigables para los scripts
NOMBRES_AMIGABLES = {
    "convertir_xls_a_xlsx.py": "📄 Convertir XLS a XLSX",
    "reorder_lists_of_excel_files.py": "🔄 Reordenar Archivos Excel",
    "consolidado_ultimo_archivo_materiales.py": "📊 Consolidar Materiales",
    "ejecutar_proceso_completo.py": "⚙️ Proceso Completo",
    "consolidar_zresguias_excel.ipynb": "📋 Consolidar ZRESGUIAS",
    "carga_roadshow.py": "🚀 Carga Roadshow",
    "y_dev_45.py": "📦 Y_DEV_45 - ",
    "y_dev_74.py": "📦 Y_DEV_74 - ",
    "y_dev_82.py": "📦 Y_DEV_82 - ",
    "y_rep_plr.py": "📈 Reporte PLR",
    "z_devo_alv.py": "📋 Devoluciones NE",
    "zhbo.py": "📊 ZHBO - ",
    "zred.py": "🔴 ZRED - ",
    "zresguias.py": "📄 ZRESGUIAS",
    "zsd_incidencias.py": "⚠️ Incidencias"
}  # [1](https://florida1-my.sharepoint.com/personal/elopez21334_fifco_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/menu_mas_utilizado.py)


class MenuAplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Sistema OTIF - Menú Principal")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Variables de estado
        self.script_ejecutandose = False

        # Configurar estilo
        self.configurar_estilos()

        # Crear interfaz
        self.crear_interfaz()

    def configurar_estilos(self):
        """Configurar estilos personalizados para la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para frames
        style.configure("Card.TFrame", background="white", relief="raised", borderwidth=2)

        # Estilo para botones
        style.configure("Action.TButton",
                        font=("Segoe UI", 10),
                        padding=10,
                        background="#4CAF50",
                        foreground="white")
        style.map("Action.TButton", background=[("active", "#45a049")])

        style.configure("SAP.TButton",
                        font=("Segoe UI", 10),
                        padding=10,
                        background="#2196F3",
                        foreground="white")
        style.map("SAP.TButton", background=[("active", "#1976D2")])

        style.configure("Special.TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=10,
                        background="#FF9800",
                        foreground="white")
        style.map("Special.TButton", background=[("active", "#F57C00")])

    def crear_interfaz(self):
        """Crear la interfaz principal"""
        # Frame principal con scroll
        main_container = tk.Frame(self.root, bg="#f0f0f0")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas para scroll
        canvas = tk.Canvas(main_container, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        self.crear_header(scrollable_frame)

        # Barra de estado
        self.status_var = tk.StringVar(value="✅ Sistema Listo")
        self.crear_barra_estado(scrollable_frame)

        # Scripts Generales
        self.crear_seccion_generales(scrollable_frame)

        # SAP Scripting
        self.crear_seccion_sap(scrollable_frame)

        # Botón especial Torre Control
        self.crear_seccion_torre_control(scrollable_frame)

        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configurar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def crear_header(self, parent):
        """Crear encabezado de la aplicación"""
        header_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=(0, 20))

        titulo = tk.Label(
            header_frame,
            text="🎯 Sistema OTIF - Centro de Control",
            font=("Segoe UI", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        titulo.pack(pady=10)

        subtitulo = tk.Label(
            header_frame,
            text="Gestión de Reportes y Automatización SAP",
            font=("Segoe UI", 11),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitulo.pack()

    def crear_barra_estado(self, parent):
        """Crear barra de estado"""
        status_frame = tk.Frame(parent, bg="#34495e", height=30)
        status_frame.pack(fill="x", pady=(0, 15))

        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg="#34495e",
            fg="white",
            anchor="w",
            padx=10
        )
        self.status_label.pack(fill="x")

    def crear_seccion_generales(self, parent):
        """Crear sección de scripts generales"""
        container = ttk.Frame(parent, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        titulo = tk.Label(
            container,
            text="📁 Scripts Generales",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        titulo.pack(anchor="w", padx=15, pady=(15, 10))

        desc = tk.Label(
            container,
            text="Herramientas de procesamiento y consolidación de datos",
            font=("Segoe UI", 9),
            bg="white",
            fg="#7f8c8d"
        )
        desc.pack(anchor="w", padx=15, pady=(0, 10))

        botones_frame = tk.Frame(container, bg="white")
        botones_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        scripts_generales = [
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\convertir_xls_a_xlsx.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\reorder_lists_of_excel_files.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\consolidado_ultimo_archivo_materiales.py",
            # NOTA: En tu archivo original esta ruta tenía "python ejecutar_proceso_completo.py" dentro del path.
            # La función de ejecución intentará corregirlo si detecta ese patrón.
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\python ejecutar_proceso_completo.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\consolidar_zresguias_excel.ipynb",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\carga_roadshow.py",
        ]  # [1](https://florida1-my.sharepoint.com/personal/elopez21334_fifco_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/menu_mas_utilizado.py)

        self.crear_grid_botones(botones_frame, scripts_generales, "Action.TButton", 2)

    def crear_seccion_sap(self, parent):
        """Crear sección de SAP Scripting"""
        container = ttk.Frame(parent, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        titulo = tk.Label(
            container,
            text="🔷 SAP Scripting",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        titulo.pack(anchor="w", padx=15, pady=(15, 10))

        desc = tk.Label(
            container,
            text="Automatización de reportes y extracción de datos SAP",
            font=("Segoe UI", 9),
            bg="white",
            fg="#7f8c8d"
        )
        desc.pack(anchor="w", padx=15, pady=(0, 10))

        botones_frame = tk.Frame(container, bg="white")
        botones_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        scripts_sap = [
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_dev_45.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_dev_74.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_dev_82.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\y_rep_plr.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\z_devo_alv.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zhbo.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zred.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zresguias.py",
            r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zsd_incidencias.py",
        ]  # [1](https://florida1-my.sharepoint.com/personal/elopez21334_fifco_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/menu_mas_utilizado.py)

        self.crear_grid_botones(botones_frame, scripts_sap, "SAP.TButton", 3)

    def crear_seccion_torre_control(self, parent):
        """Crear sección especial para Torre de Control"""
        container = ttk.Frame(parent, style="Card.TFrame")
        container.pack(fill="both", padx=10, pady=10)

        titulo = tk.Label(
            container,
            text="🏢 Torre de Control",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        titulo.pack(anchor="w", padx=15, pady=(15, 10))

        boton_frame = tk.Frame(container, bg="white")
        boton_frame.pack(fill="x", padx=15, pady=(0, 15))

        btn = tk.Button(
            boton_frame,
            text="📋 Copiar y Renombrar Último Archivo TorreControl",
            command=self.copiar_y_renombrar_archivo,
            font=("Segoe UI", 11, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=15,
            cursor="hand2"
        )
        btn.pack(fill="x")

    def crear_grid_botones(self, parent, scripts, estilo, columnas):
        """Crear una cuadrícula de botones"""
        for i, ruta in enumerate(scripts):
            nombre_archivo = os.path.basename(ruta)
            nombre_amigable = NOMBRES_AMIGABLES.get(nombre_archivo, nombre_archivo)
            fila = i // columnas
            columna = i % columnas

            btn = tk.Button(
                parent,
                text=nombre_amigable,
                command=lambda r=ruta, n=nombre_amigable: self.ejecutar_script_async(r, n),
                font=("Segoe UI", 10),
                bg="#2196F3" if "SAP" in estilo else "#4CAF50",
                fg="white",
                activebackground="#1976D2" if "SAP" in estilo else "#45a049",
                activeforeground="white",
                relief="flat",
                padx=15,
                pady=12,
                cursor="hand2",
                anchor="w"
            )
            btn.grid(row=fila, column=columna, padx=5, pady=5, sticky="ew")

            # Efecto hover
            def on_enter(e, button=btn):
                button['background'] = "#1976D2" if "SAP" in estilo else "#45a049"

            def on_leave(e, button=btn):
                button['background'] = "#2196F3" if "SAP" in estilo else "#4CAF50"

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        # Configurar columnas para que se expandan uniformemente
        for col in range(columnas):
            parent.grid_columnconfigure(col, weight=1)

    def _mostrar_salida(self, titulo, salida_stdout, salida_stderr):
        """Ventana con scrolled text para mostrar stdout/stderr"""
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("900x500")
        txt = ScrolledText(win, wrap="word", font=("Consolas", 10))
        txt.pack(fill="both", expand=True)

        if salida_stdout:
            txt.insert("end", "=== STDOUT ===\n")
            txt.insert("end", salida_stdout + "\n")
        if salida_stderr:
            txt.insert("end", "\n=== STDERR ===\n")
            txt.insert("end", salida_stderr + "\n")

        txt.configure(state="disabled")

    def _preparar_comando(self, ruta_script):
        """
        Devuelve (cmd:list[str], cwd:str) según extensión.
        Corrige el caso donde la ruta incluye 'python ejecutar_proceso_completo.py'
        como parte del path por error.
        """
        ruta = ruta_script

        # Corrección automática del caso especial detectado
        # (si no existe el archivo y la cadena contiene 'python ')
        if not os.path.isfile(ruta) and "python " in os.path.basename(ruta):
            ruta_posible = ruta.replace("python ", "")
            if os.path.isfile(ruta_posible):
                ruta = ruta_posible

        if not os.path.isfile(ruta):
            # No existe; devolvemos None para que el caller lo maneje
            return None, None

        ext = os.path.splitext(ruta)[1].lower()
        cwd = os.path.dirname(ruta) if os.path.dirname(ruta) else None

        if ext == ".py":
            cmd = [sys.executable, ruta]  # usar el mismo intérprete de la GUI
        elif ext == ".ipynb":
            # Ejecutar notebook con jupyter nbconvert (requiere jupyter instalado)
            cmd = [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--inplace",
                ruta
            ]
        else:
            # Extensión no soportada
            return None, None

        return cmd, cwd

    def ejecutar_script_async(self, ruta_script, nombre):
        """Ejecutar script en un hilo separado, con captura de stdout/stderr"""
        if self.script_ejecutandose:
            messagebox.showwarning(
                "Script en Ejecución",
                "Ya hay un script ejecutándose. Por favor espera a que termine."
            )
            return

        def ejecutar():
            self.script_ejecutandose = True
            self.status_var.set(f"⏳ Ejecutando: {nombre}...")
            self.status_label.config(fg="#f39c12")

            cmd, cwd = self._preparar_comando(ruta_script)
            if cmd is None:
                self.status_var.set(f"⚠️ No se puede ejecutar: {nombre}")
                self.status_label.config(fg="#e67e22")
                messagebox.showerror(
                    "Ruta no válida",
                    f"No se encontró un ejecutable soportado para:\n\n{ruta_script}\n\n"
                    f"• Verifica que el archivo exista.\n"
                    f"• Si es un notebook (.ipynb), se ejecutará con Jupyter.\n"
                    f"• Si ves 'python ' dentro de la ruta, corrígelo al nombre real del .py."
                )
                return

            try:
                resultado = subprocess.run(
                    cmd,
                    check=False,               # evaluamos manualmente el código
                    capture_output=True,
                    text=True,
                    cwd=cwd
                )

                if resultado.returncode == 0:
                    self.status_var.set(f"✅ Completado: {nombre}")
                    self.status_label.config(fg="#27ae60")
                    messagebox.showinfo(
                        "Éxito",
                        f"✅ Script ejecutado exitosamente:\n\n{nombre}"
                    )
                    # Mostrar salida si hay algo interesante
                    if (resultado.stdout or resultado.stderr):
                        self._mostrar_salida(f"Salida de {nombre}", resultado.stdout, resultado.stderr)
                else:
                    self.status_var.set(f"❌ Error en: {nombre}")
                    self.status_label.config(fg="#e74c3c")
                    # Mostrar salida para diagnosticar
                    self._mostrar_salida(f"Error al ejecutar {nombre}", resultado.stdout, resultado.stderr)
                    messagebox.showerror(
                        "Error",
                        f"❌ El proceso terminó con código {resultado.returncode}.\n\n"
                        f"Se abrió una ventana con el detalle de STDOUT/STDERR."
                    )

            except Exception as e:
                self.status_var.set(f"❌ Error inesperado en: {nombre}")
                self.status_label.config(fg="#e74c3c")
                messagebox.showerror(
                    "Error",
                    f"❌ Error inesperado:\n\n{str(e)}"
                )
            finally:
                self.script_ejecutandose = False
                # Volver al estado listo después de 3 segundos
                self.root.after(3000, lambda: self.status_var.set("✅ Sistema Listo"))
                self.root.after(3000, lambda: self.status_label.config(fg="white"))

        # Ejecutar en hilo separado
        thread = threading.Thread(target=ejecutar, daemon=True)
        thread.start()

    def copiar_y_renombrar_archivo(self):
        """Copiar y renombrar el último archivo TorreControl"""
        carpeta = r"C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\10-octubre"  # [1](https://florida1-my.sharepoint.com/personal/elopez21334_fifco_com/Documents/Archivos%20de%20Microsoft%C2%A0Copilot%20Chat/menu_mas_utilizado.py)
        self.status_var.set("⏳ Procesando archivo Torre de Control...")
        self.status_label.config(fg="#f39c12")
        try:
            archivos = [
                os.path.join(carpeta, f)
                for f in os.listdir(carpeta)
                if os.path.isfile(os.path.join(carpeta, f))
            ]
            if not archivos:
                self.status_var.set("⚠️ No se encontraron archivos")
                self.status_label.config(fg="#e67e22")
                messagebox.showinfo(
                    "Información",
                    "ℹ️ No se encontraron archivos en la carpeta."
                )
                return

            archivo_mas_reciente = max(archivos, key=os.path.getmtime)
            fecha_nueva = (datetime.now() + timedelta(days=-1)).strftime("%d-%m-%Y")
            nuevo_nombre = f"torreControl_{fecha_nueva}.xlsx"
            nueva_ruta = os.path.join(carpeta, nuevo_nombre)

            # Si el archivo ya existe, preguntar si se sobreescribe
            if os.path.exists(nueva_ruta):
                if not messagebox.askyesno(
                    "Archivo existente",
                    f"El archivo {nuevo_nombre} ya existe.\n\n¿Deseas sobreescribirlo?"
                ):
                    return

            shutil.copy2(archivo_mas_reciente, nueva_ruta)

            self.status_var.set("✅ Archivo Torre de Control copiado exitosamente")
            self.status_label.config(fg="#27ae60")
            messagebox.showinfo(
                "Éxito",
                f"✅ Archivo copiado exitosamente:\n\n📄 {nuevo_nombre}\n\n📁 {carpeta}"
            )
        except Exception as e:
            self.status_var.set("❌ Error al copiar archivo")
            self.status_label.config(fg="#e74c3c")
            messagebox.showerror(
                "Error",
                f"❌ Ocurrió un error:\n\n{str(e)}"
            )
        finally:
            # Volver al estado listo después de 3 segundos
            self.root.after(3000, lambda: self.status_var.set("✅ Sistema Listo"))
            self.root.after(3000, lambda: self.status_label.config(fg="white"))


# Crear y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = MenuAplicacion(root)
    root.mainloop()