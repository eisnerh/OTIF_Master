# 🎯 SISTEMA OTIF MASTER - VERSION UNIFICADA

## 📋 **DESCRIPCION**

Sistema unificado de procesamiento OTIF que reemplaza todos los menus anteriores con una estructura organizada y eficiente.

## 🏗️ **ESTRUCTURA DEL PROYECTO**

```
OTIF_Master/
├── 📁 core/                    # Scripts principales del sistema
│   └── menu_principal.py       # Menu unificado principal
├── 📁 scripts/                 # Scripts organizados por categoría
│   ├── 📁 procesamiento/       # Scripts de procesamiento de datos
│   ├── 📁 sap/                 # Scripts de SAP (futuro)
│   ├── 📁 notebooks/           # Jupyter notebooks
│   └── 📁 utilidades/          # Scripts de utilidades
├── 📁 data/                    # Datos y archivos de entrada
├── 📁 output/                  # Archivos generados
├── 📁 web/                     # Interfaz web (futuro)
├── 📁 docs/                    # Documentación
├── 📁 config/                  # Archivos de configuración
├── 📁 batch/                   # Archivos .bat para ejecución
├── iniciar_otif.py             # Iniciador principal
└── app.py                      # Aplicación web Flask
```

## 🚀 **INICIO RAPIDO**

### **Opción 1: Iniciador Principal (Recomendado)**
```bash
python iniciar_otif.py
```

### **Opción 2: Archivo Batch**
```bash
batch/iniciar_otif.bat
```

### **Opción 3: Menu Principal Directo**
```bash
python core/menu_principal.py
```

## 📊 **FUNCIONALIDADES PRINCIPALES**

### **PROCESAMIENTO DE DATOS OTIF:**
- ✅ Ejecutar TODO el procesamiento OTIF
- ✅ Procesar solo NO ENTREGAS
- ✅ Procesar solo REP PLR
- ✅ Procesar solo VOL PORTAFOLIO
- ✅ Unificar todos los datos

### **SCRIPTS ESTRUCTURADOS:**
- ✅ Consolidar datos
- ✅ Reporte PLR
- ✅ Volumen procesado familia
- ✅ Volumen no entregas
- ✅ Consolidar archivo PLR a Parquet

### **AUTOMATIZACION SAP:**
- ✅ Automatizacion reportes SAP
- ✅ Ejecutar proceso completo SAP
- ✅ Scripts individuales SAP (Submenu)
- ✅ Convertir XLS a XLSX
- ✅ Reordenar archivos Excel

### **SCRIPTS ULTIMO ARCHIVO:**
- ✅ Consolidado ultimo archivo materiales
- ✅ Consolidar zresguias
- ✅ Carga roadshow
- ✅ Consolidar mes PLR

### **JUPYTER NOTEBOOKS:**
- ✅ Ejecutar notebook consolidar zresguias
- ✅ Buscar notebooks disponibles

### **VERIFICACION Y MONITOREO:**
- ✅ Verificar estado de rutas
- ✅ Ver resumen de procesamiento
- ✅ Verificar estructura del sistema
- ✅ Ver archivos generados

### **INTERFAZ WEB:**
- ✅ Iniciar aplicacion web

### **HERRAMIENTAS:**
- ✅ Ver informacion del sistema
- ✅ Limpiar archivos temporales
- ✅ Ver estadisticas de rendimiento
- ✅ Gestion de favoritos (En desarrollo)

## 🔧 **CONFIGURACION**

### **Archivo de Configuración:**
- `config/configuracion_unificada.json` - Configuración principal del sistema

### **Rutas Importantes:**
- Scripts de procesamiento: `scripts/procesamiento/`
- Scripts de utilidades: `scripts/utilidades/`
- Notebooks: `scripts/notebooks/`
- Datos: `data/`
- Salida: `output/`

## 📁 **ORGANIZACION DE ARCHIVOS**

### **Scripts de Procesamiento:**
- `agrupar_datos_no_entregas_mejorado.py`
- `agrupar_datos_rep_plr.py`
- `agrupar_datos_vol_portafolio.py`
- `unificar_datos_completos.py`

### **Scripts de Utilidades:**
- `configuracion_sistema.py`
- `verificar_estructura.py`
- `unificador_principal.py`
- `menu_mas_utilizado.py`
- `ejecutar_notebook.py`
- `ejemplo_favoritos.py`

### **Notebooks:**
- `consolidar_zresguias_excel.ipynb`

## 🛠️ **REQUISITOS DEL SISTEMA**

### **Python:**
- Python 3.8 o superior
- Módulos: os, sys, subprocess, json, pathlib

### **Dependencias Opcionales:**
- `jupyter` - Para ejecutar notebooks
- `pandas` - Para procesamiento de datos
- `openpyxl` - Para archivos Excel
- `flask` - Para la aplicación web

## 🚨 **SOLUCION DE PROBLEMAS**

### **Error: "No se encuentra el script"**
- Verifica que la estructura del proyecto sea correcta
- Ejecuta `python iniciar_otif.py` y selecciona "Verificar sistema"

### **Error: "Jupyter no está instalado"**
- Instala Jupyter: `pip install jupyter`
- O usa la opción de scripts Python en lugar de notebooks

### **Error: "Estructura del proyecto incorrecta"**
- Ejecuta el script de reestructuración
- Verifica que todos los directorios existan

## 📈 **MEJORAS IMPLEMENTADAS**

### **Organización:**
- ✅ Estructura de directorios clara y lógica
- ✅ Separación de responsabilidades
- ✅ Archivos organizados por categoría

### **Funcionalidad:**
- ✅ Menu unificado que reemplaza todos los anteriores
- ✅ Sistema de configuración centralizado
- ✅ Verificación automática del sistema
- ✅ Iniciador principal con opciones

### **Mantenimiento:**
- ✅ Documentación unificada
- ✅ Scripts de utilidades organizados
- ✅ Configuración en archivos JSON
- ✅ Sistema de verificación integrado

## 🔄 **MIGRACION DESDE VERSIONES ANTERIORES**

### **Menus Anteriores:**
- `menu_cmd.py` - Movido a utilidades
- `menu_completo.py` - Movido a utilidades
- `ejecutar_modulo.py` - Funcionalidad integrada

### **Scripts Reorganizados:**
- Scripts de procesamiento → `scripts/procesamiento/`
- Scripts de utilidades → `scripts/utilidades/`
- Notebooks → `scripts/notebooks/`
- Documentación → `docs/`
- Configuración → `config/`

## 🎯 **PRÓXIMOS PASOS**

1. **Completar sistema de favoritos**
2. **Integrar interfaz web**
3. **Añadir más scripts SAP**
4. **Implementar logging avanzado**
5. **Crear sistema de respaldos**

## 📞 **SOPORTE**

Para problemas o preguntas:
1. Ejecuta "Verificar sistema" en el iniciador
2. Revisa la documentación en `docs/`
3. Verifica la configuración en `config/`

---

**Versión:** 2.0.0  
**Fecha:** 2025-10-24  
**Estado:** Estable y funcional
