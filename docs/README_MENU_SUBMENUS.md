# MENU COMPLETO OTIF CON SUBMENUS - VERSION CMD

## Descripcion
Sistema de menu completo con submenus organizados para CMD que incluye TODAS las funcionalidades del proyecto OTIF, organizadas por categorias y sin dependencias de tkinter.

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

## Opciones del Menu Completo con Submenus

### PROCESAMIENTO DE DATOS OTIF:
- **1.** Ejecutar TODO el procesamiento OTIF
- **2.** Procesar solo NO ENTREGAS
- **3.** Procesar solo REP PLR
- **4.** Procesar solo VOL PORTAFOLIO
- **5.** Unificar todos los datos

### SCRIPTS ESTRUCTURADOS:
- **6.** Scripts estructurados (Submenu)

### AUTOMATIZACION SAP:
- **7.** Automatizacion reportes SAP
- **8.** Ejecutar proceso completo SAP
- **9.** Scripts individuales SAP (Submenu)
- **10.** Convertir XLS a XLSX
- **11.** Reordenar archivos Excel

### SCRIPTS ULTIMO ARCHIVO:
- **12.** Scripts ultimo archivo (Submenu)

### JUPYTER NOTEBOOKS:
- **13.** Ejecutar notebook consolidar zresguias
- **14.** Buscar notebooks disponibles

### VERIFICACION Y MONITOREO:
- **15.** Verificar estado de rutas
- **16.** Ver resumen de procesamiento
- **17.** Verificar estructura del sistema
- **18.** Ver archivos generados

### INTERFAZ WEB:
- **19.** Iniciar aplicacion web

### HERRAMIENTAS:
- **20.** Ver informacion del sistema
- **21.** Limpiar archivos temporales
- **22.** Ver estadisticas de rendimiento
- **23.** Menu mas utilizado

### SALIR:
- **0.** Salir del sistema

## Submenus Disponibles

### 1. **SCRIPTS ESTRUCTURADOS (Opcion 6)**
- **1.** Consolidar datos
- **2.** Reporte PLR
- **3.** Volumen procesado familia
- **4.** Volumen no entregas
- **5.** Consolidar archivo PLR a Parquet
- **6.** Ejecutar TODOS los scripts estructurados
- **0.** Volver al menu principal

### 2. **SCRIPTS INDIVIDUALES SAP (Opcion 9)**
- **1.** Y_DEV_45 - Devoluciones 45
- **2.** Y_DEV_74 - Devoluciones 74
- **3.** Y_DEV_82 - Devoluciones 82
- **4.** Y_REP_PLR - Reporte PLR
- **5.** Z_DEVO_ALV - Devoluciones ALV
- **6.** ZHBO - Reporte HBO
- **7.** ZRED - Reporte de Red
- **8.** ZRESGUIAS - Resguías
- **9.** ZSD_INCIDENCIAS - Incidencias
- **10.** Ejecutar TODOS los scripts individuales
- **0.** Volver al menu principal

### 3. **SCRIPTS ULTIMO ARCHIVO (Opcion 12)**
- **1.** Consolidado ultimo archivo materiales
- **2.** Consolidar zresguias
- **3.** Carga roadshow
- **4.** Consolidar mes PLR
- **5.** Ejecutar TODOS los scripts ultimo archivo
- **0.** Volver al menu principal

## Caracteristicas del Menu con Submenus

### Ventajas:
- ✅ **Sin tkinter** - Evita todos los errores de tkinter
- ✅ **Menu organizado** - Submenus para mejor navegacion
- ✅ **23 opciones principales** - Menu principal simplificado
- ✅ **Submenus especializados** - Acceso rapido a scripts relacionados
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
- **Submenus especializados** (NUEVO)

## Archivos Creados

1. **`menu_completo.py`** - Menu principal completo con submenus
2. **`iniciar_menu_completo.bat`** - Archivo batch para Windows
3. **`README_MENU_SUBMENUS.md`** - Este archivo de documentacion
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
2. Usa la opcion 17 del menu para verificar la estructura
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
3. **Para scripts estructurados:** Usa la opcion 6 (submenu)
4. **Para automatizacion SAP:** Usa las opciones 7-11
5. **Para scripts individuales SAP:** Usa la opcion 9 (submenu)
6. **Para scripts de ultimo archivo:** Usa la opcion 12 (submenu)
7. **Para notebooks de Jupyter:** Usa las opciones 13-14
8. **Para verificar el sistema:** Usa las opciones 15-18
9. **Para interfaz web:** Usa la opcion 19
10. **Para herramientas:** Usa las opciones 20-23

## Comparacion de Menus

| Caracteristica | Menu Basico | Menu Completo | Menu con Submenus |
|----------------|-------------|---------------|-------------------|
| Opciones principales | 13 | 30 | 23 |
| Submenus | ❌ | ❌ | ✅ |
| Scripts OTIF | ✅ | ✅ | ✅ |
| Scripts Estructurados | ❌ | ✅ | ✅ (Submenu) |
| Automatizacion SAP | ❌ | ✅ | ✅ |
| Scripts Individuales SAP | ❌ | ✅ | ✅ (Submenu) |
| Scripts Ultimo Archivo | ❌ | ✅ | ✅ (Submenu) |
| Jupyter Notebooks | ❌ | ✅ | ✅ |
| Verificacion | ✅ | ✅ | ✅ |
| Interfaz Web | ✅ | ✅ | ✅ |
| Herramientas | ✅ | ✅ | ✅ |
| Organizacion | Basica | Por Categorias | Por Categorias + Submenus |

## ¡Listo para Usar!

El menu completo con submenus esta diseñado para ser:
- **Completo** - Incluye todas las funcionalidades
- **Organizado** - Submenus para mejor navegacion
- **Eficiente** - Sin dependencias problemáticas
- **Facil de usar** - Interfaz intuitiva con submenus
- **Escalable** - Facil agregar nuevos submenus

¡Disfruta de tu nuevo sistema de menu completo con submenus!
