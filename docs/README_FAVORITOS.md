# SISTEMA DE FAVORITOS OTIF

## Descripcion
Sistema de favoritos integrado que te permite guardar, organizar y ejecutar rapidamente tus scripts, notebooks y carpetas mas utilizados.

## Caracteristicas del Sistema de Favoritos

### ✅ **Funcionalidades Principales:**
- ✅ **Guardar scripts favoritos** - Agrega scripts Python a favoritos
- ✅ **Guardar notebooks favoritos** - Agrega notebooks Jupyter a favoritos
- ✅ **Guardar carpetas favoritas** - Agrega carpetas a favoritos
- ✅ **Ejecutar favoritos** - Ejecuta scripts y notebooks desde favoritos
- ✅ **Gestionar favoritos** - Ver, editar y eliminar favoritos
- ✅ **Buscar scripts** - Encuentra scripts disponibles en el sistema
- ✅ **Persistencia** - Los favoritos se guardan en `favoritos.json`

### 📁 **Tipos de Favoritos Soportados:**

#### 1. **SCRIPTS PYTHON**
- Scripts de procesamiento OTIF
- Scripts de automatizacion SAP
- Scripts estructurados
- Scripts de ultimo archivo
- Cualquier script Python del proyecto

#### 2. **NOTEBOOKS JUPYTER**
- Notebooks de analisis
- Notebooks de procesamiento
- Notebooks de consolidacion
- Cualquier archivo `.ipynb`

#### 3. **CARPETAS**
- Carpetas de datos
- Carpetas de salida
- Carpetas de scripts
- Cualquier carpeta del sistema

## Como Usar el Sistema de Favoritos

### 1. **Acceder a Favoritos**
```cmd
python menu_completo.py
# Selecciona opcion 24: Gestion de favoritos (Submenu)
```

### 2. **Agregar Script Favorito**
1. Selecciona "Agregar script favorito"
2. El sistema busca todos los scripts Python disponibles
3. Selecciona el script que quieres agregar
4. Ingresa un nombre personalizado
5. Agrega una descripcion (opcional)
6. ¡Listo! El script se guarda en favoritos

### 3. **Agregar Notebook Favorito**
1. Selecciona "Agregar notebook favorito"
2. El sistema busca todos los notebooks disponibles
3. Selecciona el notebook que quieres agregar
4. Ingresa un nombre personalizado
5. Agrega una descripcion (opcional)
6. ¡Listo! El notebook se guarda en favoritos

### 4. **Agregar Carpeta Favorita**
1. Selecciona "Agregar carpeta favorita"
2. Ingresa la ruta de la carpeta
3. Ingresa un nombre personalizado
4. Agrega una descripcion (opcional)
5. ¡Listo! La carpeta se guarda en favoritos

### 5. **Ejecutar Favoritos**
1. Selecciona "Ejecutar favorito"
2. El sistema muestra todos tus favoritos
3. Selecciona el favorito que quieres ejecutar
4. El sistema ejecuta el script/notebook o abre la carpeta

### 6. **Gestionar Favoritos**
- **Ver favoritos**: Muestra todos los favoritos guardados
- **Eliminar favorito**: Elimina favoritos que ya no necesitas
- **Buscar scripts**: Encuentra scripts disponibles en el sistema

## Estructura del Archivo de Favoritos

El sistema guarda los favoritos en `favoritos.json`:

```json
{
  "scripts": [
    {
      "nombre": "Mi Script Favorito",
      "ruta": "scripts/mi_script.py",
      "descripcion": "Script para procesar datos",
      "fecha_agregado": "2025-01-15T10:30:00"
    }
  ],
  "notebooks": [
    {
      "nombre": "Analisis de Datos",
      "ruta": "notebooks/analisis.ipynb",
      "descripcion": "Notebook para analizar datos",
      "fecha_agregado": "2025-01-15T10:35:00"
    }
  ],
  "carpetas": [
    {
      "nombre": "Carpeta de Datos",
      "ruta": "Data/Output",
      "descripcion": "Carpeta con archivos de salida",
      "fecha_agregado": "2025-01-15T10:40:00"
    }
  ]
}
```

## Ejemplos de Uso

### Ejemplo 1: Agregar Script de Procesamiento OTIF
```
1. Ejecuta: python menu_completo.py
2. Selecciona: 24 (Gestion de favoritos)
3. Selecciona: 2 (Agregar script favorito)
4. Selecciona el script: scripts/agrupar_datos_rep_plr.py
5. Nombre: "Procesar REP PLR"
6. Descripcion: "Script para agrupar datos REP PLR"
7. ¡Favorito agregado!
```

### Ejemplo 2: Agregar Notebook de Analisis
```
1. Ejecuta: python menu_completo.py
2. Selecciona: 24 (Gestion de favoritos)
3. Selecciona: 3 (Agregar notebook favorito)
4. Selecciona el notebook: OTIF_Estructurado/ULTIMO_ARCHIVO/consolidar_zresguias_excel.ipynb
5. Nombre: "Consolidar Zresguias"
6. Descripcion: "Notebook para consolidar datos de zresguias"
7. ¡Favorito agregado!
```

### Ejemplo 3: Ejecutar Favorito
```
1. Ejecuta: python menu_completo.py
2. Selecciona: 24 (Gestion de favoritos)
3. Selecciona: 5 (Ejecutar favorito)
4. Selecciona el favorito que quieres ejecutar
5. ¡El script/notebook se ejecuta automaticamente!
```

## Ventajas del Sistema de Favoritos

### ✅ **Rapidez**
- Acceso directo a scripts mas utilizados
- No necesitas navegar por submenus
- Ejecucion con un solo clic

### ✅ **Personalizacion**
- Nombres personalizados para favoritos
- Descripciones para recordar que hace cada script
- Organizacion por tipo (scripts, notebooks, carpetas)

### ✅ **Persistencia**
- Los favoritos se guardan entre sesiones
- No necesitas volver a agregar favoritos
- Backup automatico en archivo JSON

### ✅ **Flexibilidad**
- Agregar cualquier script del proyecto
- Agregar notebooks de Jupyter
- Agregar carpetas para acceso rapido
- Eliminar favoritos que ya no necesitas

## Solucion de Problemas

### Si no puedes agregar favoritos:
1. Verifica que tengas permisos de escritura en el directorio
2. Asegurate de que el archivo `favoritos.json` no este bloqueado
3. Revisa que el script/notebook exista en la ruta especificada

### Si los favoritos no se guardan:
1. Verifica que tengas espacio en disco
2. Revisa que no haya caracteres especiales en los nombres
3. Asegurate de que el archivo JSON no este corrupto

### Si no puedes ejecutar favoritos:
1. Verifica que el script/notebook aun exista
2. Revisa que tengas permisos de ejecucion
3. Asegurate de que las dependencias esten instaladas

## Consejos de Uso

1. **Organiza tus favoritos**: Usa nombres descriptivos y descripciones claras
2. **Mantén favoritos actualizados**: Elimina favoritos que ya no uses
3. **Usa descripciones**: Te ayudan a recordar que hace cada favorito
4. **Agrupa por tipo**: Separa scripts, notebooks y carpetas
5. **Revisa regularmente**: Mantén tu lista de favoritos limpia y organizada

## ¡Listo para Usar!

El sistema de favoritos esta integrado en el menu completo y listo para usar. Solo necesitas:

1. **Ejecutar el menu**: `python menu_completo.py`
2. **Acceder a favoritos**: Opcion 24
3. **Agregar tus scripts favoritos**
4. **¡Disfrutar del acceso rapido!**

¡Tu sistema OTIF ahora es mas personal y eficiente que nunca!
