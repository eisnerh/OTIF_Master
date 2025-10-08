import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import shutil
from datetime import datetime, timedelta
import threading

# Diccionario de nombres amigables para los scripts
NOMBRES_AMIGABLES = {
    "convertir_xls_a_xlsx.py": "📄 Convertir XLS a XLSX",
    "reorder_lists_of_excel_files.py": "🔄 Reordenar Archivos Excel",
    "consolidado_ultimo_archivo_materiales.py": "📊 Consolidar Materiales",
    "ejecutar_proceso_completo.py": "⚙️ Proceso Completo",
    "consolidar_zresguias_excel.ipynb": "📋 Consolidar Resguías",
    "carga_roadshow.py": "🚀 Carga Roadshow",
    "y_dev_45.py": "📦 Y_DEV_45 - Devoluciones",
    "y_dev_74.py": "📦 Y_DEV_74 - Devoluciones",
    "y_dev_82.py": "📦 Y_DEV_82 - Devoluciones",
    "y_rep_plr.py": "📈 Reporte PLR",
    "z_devo_alv.py": "📋 Devoluciones ALV",
    "zhbo.py": "📊 ZHBO - Entregas",
    "zred.py": "🔴 ZRED - Rechazos",
    "zresguias.py": "📄 Resguías",
    "zsd_incidencias.py": "⚠️ Incidencias SD"
}

# Configuración de argumentos para scripts SAP
SCRIPTS_SAP_CONFIG = {
    "y_dev_45.py": ["--conn", "-1", "--sess", "-1"],
    "y_dev_74.py": ["--conn", "-1", "--sess", "-1"],
    "y_dev_82.py": ["--conn", "-1", "--sess", "-1"],
    "y_rep_plr.py": ["--conn", "-1", "--sess", "-1"],
    "z_devo_alv.py": ["--conn", "-1", "--sess", "-1"],
    "zhbo.py": ["--conn", "-1", "--sess", "-1"],
    "zred.py": ["--conn", "-1", "--sess", "-1"],
    "zresguias.py": ["--conn", "-1", "--sess", "-1"],
    "zsd_incidencias.py": ["--conn", "-1", "--sess", "-1"]
}

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
        style.map("Action.TButton",
                 background=[("active", "#45a049")])
        
        style.configure("SAP.TButton",
                       font=("Segoe UI", 10),
                       padding=10,
                       background="#2196F3",
                       foreground="white")
        style.map("SAP.TButton",
                 background=[("active", "#1976D2")])
        
        style.configure("Special.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=10,
                       background="#FF9800",
                       foreground="white")
        style.map("Special.TButton",
                 background=[("active", "#F57C00")])
        
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
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def crear_header(self, parent):
        """Crear encabezado de la aplicación"""
        header_frame = tk.Frame(parent, bg="#2c3e50", height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Título principal
        titulo = tk.Label(
            header_frame,
            text="🎯 Sistema OTIF - Centro de Control",
            font=("Segoe UI", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        titulo.pack(pady=10)
        
        # Subtítulo
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
        # Frame contenedor
        container = ttk.Frame(parent, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título de la sección
        titulo = tk.Label(
            container,
            text="📁 Scripts Generales",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        titulo.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Descripción
        desc = tk.Label(
            container,
            text="Herramientas de procesamiento y consolidación de datos",
            font=("Segoe UI", 9),
            bg="white",
            fg="#7f8c8d"
        )
        desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Frame para botones en grid
        botones_frame = tk.Frame(container, bg="white")
        botones_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

scripts_generales = [
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\convertir_xls_a_xlsx.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\reorder_lists_of_excel_files.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\consolidado_ultimo_archivo_materiales.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\python ejecutar_proceso_completo.py",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\consolidar_zresguias_excel.ipynb",
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\ULTIMO_ARCHIVO\carga_roadshow.py"
]

        self.crear_grid_botones(botones_frame, scripts_generales, "Action.TButton", 2)
        
    def crear_seccion_sap(self, parent):
        """Crear sección de SAP Scripting"""
        # Frame contenedor
        container = ttk.Frame(parent, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título de la sección
        titulo = tk.Label(
            container,
            text="🔷 SAP Scripting",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        titulo.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Descripción
        desc = tk.Label(
            container,
            text="Automatización de reportes y extracción de datos SAP",
            font=("Segoe UI", 9),
            bg="white",
            fg="#7f8c8d"
        )
        desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Frame para botones en grid
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
    r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\zsd_incidencias.py"
]

        self.crear_grid_botones(botones_frame, scripts_sap, "SAP.TButton", 3)
        
        # Botón para ejecutar todos los scripts SAP
        btn_ejecutar_todos = tk.Button(
            container,
            text="🚀 Ejecutar TODOS los Scripts SAP en Secuencia",
            command=self.ejecutar_todos_sap,
            font=("Segoe UI", 11, "bold"),
            bg="#9C27B0",
            fg="white",
            activebackground="#7B1FA2",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=15,
            cursor="hand2"
        )
        btn_ejecutar_todos.pack(fill="x", padx=15, pady=(10, 15))
        
    def crear_seccion_torre_control(self, parent):
        """Crear sección especial para Torre de Control"""
        # Frame contenedor
        container = ttk.Frame(parent, style="Card.TFrame")
        container.pack(fill="both", padx=10, pady=10)
        
        # Título de la sección
        titulo = tk.Label(
            container,
            text="🏢 Torre de Control",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        titulo.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Frame para botón
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
    
    def ejecutar_script_async(self, ruta_script, nombre):
        """Ejecutar script en un hilo separado"""
        if self.script_ejecutandose:
            messagebox.showwarning(
                "Script en Ejecución",
                "Ya hay un script ejecutándose. Por favor espera a que termine."
            )
            return
        
        # Verificar si es un script SAP y mostrar advertencia
        nombre_archivo = os.path.basename(ruta_script)
        if nombre_archivo in SCRIPTS_SAP_CONFIG:
            respuesta = messagebox.askyesno(
                "Script SAP",
                f"⚠️ Vas a ejecutar un script SAP:\n\n{nombre}\n\n"
                "❗ Asegúrate de que SAP Logon esté abierto y con una sesión activa.\n\n"
                "¿Deseas continuar?",
                icon='warning'
            )
            if not respuesta:
                return
        
        def ejecutar():
            self.script_ejecutandose = True
            self.status_var.set(f"⏳ Ejecutando: {nombre}...")
            self.status_label.config(fg="#f39c12")
            
            try:
                # Obtener nombre del archivo
                nombre_archivo = os.path.basename(ruta_script)
                
                # Construir comando con argumentos específicos para scripts SAP
                cmd = ["python", ruta_script]
                if nombre_archivo in SCRIPTS_SAP_CONFIG:
                    cmd.extend(SCRIPTS_SAP_CONFIG[nombre_archivo])
                
                resultado = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                self.status_var.set(f"✅ Completado: {nombre}")
                self.status_label.config(fg="#27ae60")
                
                messagebox.showinfo(
                    "Éxito",
                    f"✅ Script ejecutado exitosamente:\n\n{nombre}"
                )
                
            except subprocess.CalledProcessError as e:
                self.status_var.set(f"❌ Error en: {nombre}")
                self.status_label.config(fg="#e74c3c")
                
                error_msg = f"❌ Error al ejecutar el script:\n\n{nombre}\n\n"
                error_msg += f"Código de salida: {e.returncode}\n\n"
                if e.stdout:
                    error_msg += f"Salida estándar:\n{e.stdout}\n\n"
                if e.stderr:
                    error_msg += f"Errores:\n{e.stderr}"
                
                messagebox.showerror("Error", error_msg)
            
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
    
    def ejecutar_todos_sap(self):
        """Ejecutar todos los scripts SAP en secuencia usando ejecutar_todos.py"""
        if self.script_ejecutandose:
            messagebox.showwarning(
                "Script en Ejecución",
                "Ya hay un script ejecutándose. Por favor espera a que termine."
            )
            return
        
        respuesta = messagebox.askyesno(
            "Ejecutar Todos los Scripts SAP",
            "⚠️ Vas a ejecutar TODOS los scripts SAP en secuencia:\n\n"
            "📦 Y_DEV_45, Y_DEV_74, Y_DEV_82\n"
            "📈 Y_REP_PLR\n"
            "📋 Z_DEVO_ALV\n"
            "📊 ZHBO\n"
            "🔴 ZRED\n"
            "📄 ZRESGUIAS\n"
            "⚠️ ZSD_INCIDENCIAS\n\n"
            "❗ Asegúrate de que SAP Logon esté abierto y con una sesión activa.\n\n"
            "⏱️ Este proceso puede tomar varios minutos.\n\n"
            "¿Deseas continuar?",
            icon='warning'
        )
        
        if not respuesta:
            return
        
        def ejecutar():
            self.script_ejecutandose = True
            self.status_var.set("⏳ Ejecutando todos los scripts SAP...")
            self.status_label.config(fg="#f39c12")
            
            try:
                ruta_ejecutar_todos = r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\ejecutar_todos.py"
                
                resultado = subprocess.run(
                    ["python", ruta_ejecutar_todos],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                self.status_var.set("✅ Todos los scripts SAP completados")
                self.status_label.config(fg="#27ae60")
                
                messagebox.showinfo(
                    "Éxito",
                    "✅ Todos los scripts SAP se ejecutaron exitosamente!\n\n"
                    "Los archivos se guardaron en C:\\data\\SAP_Extraction\\"
                )
                
            except subprocess.CalledProcessError as e:
                self.status_var.set("❌ Error en ejecución de scripts SAP")
                self.status_label.config(fg="#e74c3c")
                
                error_msg = "❌ Error al ejecutar los scripts SAP:\n\n"
                error_msg += f"Código de salida: {e.returncode}\n\n"
                if e.stdout:
                    error_msg += f"Salida estándar:\n{e.stdout[:500]}\n\n"
                if e.stderr:
                    error_msg += f"Errores:\n{e.stderr[:500]}"
                
                messagebox.showerror("Error", error_msg)
            
            except Exception as e:
                self.status_var.set("❌ Error inesperado en scripts SAP")
                self.status_label.config(fg="#e74c3c")
                
                messagebox.showerror(
                    "Error",
                    f"❌ Error inesperado:\n\n{str(e)}"
                )
            
            finally:
                self.script_ejecutandose = False
                self.root.after(3000, lambda: self.status_var.set("✅ Sistema Listo"))
                self.root.after(3000, lambda: self.status_label.config(fg="white"))
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=ejecutar, daemon=True)
        thread.start()
    
    def copiar_y_renombrar_archivo(self):
        """Copiar y renombrar el último archivo TorreControl"""
        carpeta = r"C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025\10-octubre"
        
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
