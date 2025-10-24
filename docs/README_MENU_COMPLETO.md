# MENU COMPLETO OTIF - VERSION CMD

## Descripcion
Sistema de menu completo para CMD que incluye TODAS las funcionalidades del proyecto OTIF, organizadas por categorias y sin dependencias de tkinter.

## Formas de Iniciar el Menu Completo

### 1. **Metodo Recomendado - Archivo Batch**
```cmd
iniciar_menu_completo.bat
```
Solo haz doble clic en el archivo `iniciar_menu_completo.bat`

### 2. **Metodo Directo - Python**
```cmd
python menu_completo.py
```

### 3. **Metodo Alternativo - Menu Basico**
```cmd
python menu_cmd.py
```

### 4. **Metodo Existente - Sistema Unificado**
```cmd
python ejecutar_modulo.py
```

## Opciones del Menu Completo

### PROCESAMIENTO DE DATOS OTIF:
- **1.** Ejecutar TODO el procesamiento OTIF
- **2.** Procesar solo NO ENTREGAS
- **3.** Procesar solo REP PLR
- **4.** Procesar solo VOL PORTAFOLIO
- **5.** Unificar todos los datos

### SCRIPTS ESTRUCTURADOS:
- **6.** Consolidar datos
- **7.** Reporte PLR
- **8.** Volumen procesado familia
- **9.** Volumen no entregas
- **10.** Consolidar archivo PLR a Parquet

### AUTOMATIZACION SAP:
- **11.** Automatizacion reportes SAP
- **12.** Ejecutar proceso completo SAP
- **13.** Scripts individuales SAP
- **14.** Convertir XLS a XLSX
- **15.** Reordenar archivos Excel

### SCRIPTS ULTIMO ARCHIVO:
- **16.** Consolidado ultimo archivo materiales
- **17.** Consolidar zresguias
- **18.** Carga roadshow
- **19.** Consolidar mes PLR

### JUPYTER NOTEBOOKS:
- **20.** Ejecutar notebook consolidar zresguias
- **21.** Buscar notebooks disponibles

### VERIFICACION Y MONITOREO:
- **22.** Verificar estado de rutas
- **23.** Ver resumen de procesamiento
- **24.** Verificar estructura del sistema
- **25.** Ver archivos generados

### INTERFAZ WEB:
- **26.** Iniciar aplicacion web

### HERRAMIENTAS:
- **27.** Ver informacion del sistema
- **28.** Limpiar archivos temporales
- **29.** Ver estadisticas de rendimiento
- **30.** Menu mas utilizado

### SALIR:
- **0.** Salir del sistema

## Categorias de Scripts Incluidas

### 1. **PROCESAMIENTO OTIF** (Opciones 1-5)
Scripts principales del sistema OTIF:
- Agrupacion de datos
- Unificacion de datos
- Procesamiento completo

### 2. **SCRIPTS ESTRUCTURADOS** (Opciones 6-10)
Scripts de la carpeta `OTIF_Estructurado/`:
- Consolidacion de datos
- Reportes PLR
- Volumen procesado
- Conversion a Parquet

### 3. **AUTOMATIZACION SAP** (Opciones 11-15)
Scripts de automatizacion SAP:
- Extraccion de reportes
- Conversion de formatos
- Procesamiento diario
- Scripts individuales

### 4. **SCRIPTS ULTIMO ARCHIVO** (Opciones 16-19)
Scripts de la carpeta `ULTIMO_ARCHIVO/`:
- Consolidacion de materiales
- Carga de roadshow
- Consolidacion mensual

### 5. **JUPYTER NOTEBOOKS** (Opciones 20-21)
Notebooks de Jupyter disponibles:
- Ejecutar notebook consolidar zresguias
- Buscar notebooks disponibles

### 6. **VERIFICACION Y MONITOREO** (Opciones 22-25)
Herramientas de verificacion:
- Estado de rutas
- Resumen de procesamiento
- Estructura del sistema
- Archivos generados

### 6. **INTERFAZ WEB** (Opcion 24)
Aplicacion web del sistema

### 7. **HERRAMIENTAS** (Opciones 25-28)
Utilidades del sistema:
- Informacion del sistema
- Limpieza de archivos
- Estadisticas de rendimiento
- Menu mas utilizado

## Caracteristicas del Menu Completo

### Ventajas:
- ✅ **Sin tkinter** - Evita todos los errores de tkinter
- ✅ **Menu completo** - Incluye TODAS las funcionalidades
- ✅ **Organizado por categorias** - Facil navegacion
- ✅ **Interfaz limpia** - Sin emojis, compatible con CMD
- ✅ **Progreso en tiempo real** - Muestra el avance de cada proceso
- ✅ **Manejo de errores robusto** - Captura y muestra errores claramente
- ✅ **Compatible con Windows CMD** - Funciona perfectamente en CMD
- ✅ **Múltiples formas de iniciar** - Flexibilidad total

### Funcionalidades:
- Limpieza automática de pantalla
- Pausas para lectura
- Manejo de errores
- Verificación de archivos
- Progreso visual
- Resúmenes detallados
- Organización por categorías

## Archivos Creados

1. **`menu_completo.py`** - Menu principal completo
2. **`iniciar_menu_completo.bat`** - Archivo batch para Windows
3. **`README_MENU_COMPLETO.md`** - Este archivo de documentacion
4. **`menu_cmd.py`** - Menu basico (version anterior)
5. **`iniciar_menu.py`** - Iniciador del menu basico
6. **`iniciar_otif.bat`** - Archivo batch para menu basico

## Solucion de Problemas

### Si el menu no inicia:
1. Verifica que estes en el directorio correcto del proyecto
2. Asegurate de que Python este instalado
3. Usa el metodo alternativo: `python ejecutar_modulo.py`

### Si hay errores de rutas:
1. Verifica que los scripts esten en las carpetas correctas
2. Usa la opcion 22 del menu para verificar la estructura
3. Revisa que los archivos de datos esten en las ubicaciones correctas

### Si hay errores de SAP:
1. Verifica que tengas conexion a SAP
2. Revisa las credenciales en los scripts SAP
3. Asegurate de que los scripts SAP esten configurados correctamente

### Si hay errores con notebooks:
1. Verifica que Jupyter este instalado: `pip install jupyter`
2. Verifica que nbconvert este instalado: `pip install nbconvert`
3. Asegurate de que el notebook tenga el kernel correcto
4. Revisa que las dependencias del notebook esten instaladas

## Consejos de Uso

1. **Para procesamiento completo:** Usa la opcion 1
2. **Para procesamiento especifico:** Usa las opciones 2-5
3. **Para scripts estructurados:** Usa las opciones 6-10
4. **Para automatizacion SAP:** Usa las opciones 11-15
5. **Para scripts de ultimo archivo:** Usa las opciones 16-19
6. **Para notebooks de Jupyter:** Usa las opciones 20-21
7. **Para verificar el sistema:** Usa las opciones 22-25
8. **Para interfaz web:** Usa la opcion 26
9. **Para herramientas:** Usa las opciones 27-30

## Comparacion de Menus

| Caracteristica | Menu Basico | Menu Completo |
|----------------|-------------|---------------|
| Opciones | 13 | 30 |
| Scripts OTIF | ✅ | ✅ |
| Scripts Estructurados | ❌ | ✅ |
| Automatizacion SAP | ❌ | ✅ |
| Scripts Ultimo Archivo | ❌ | ✅ |
| Jupyter Notebooks | ❌ | ✅ |
| Verificacion | ✅ | ✅ |
| Interfaz Web | ✅ | ✅ |
| Herramientas | ✅ | ✅ |
| Organizacion | Basica | Por Categorias |

## ¡Listo para Usar!

El menu completo esta diseñado para ser:
- **Completo** - Incluye todas las funcionalidades
- **Organizado** - Categorias claras y logicas
- **Eficiente** - Sin dependencias problemáticas
- **Facil de usar** - Interfaz intuitiva

¡Disfruta de tu nuevo sistema de menu completo!
