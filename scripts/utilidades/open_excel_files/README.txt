================================================================================
SCRIPT PARA ABRIR ARCHIVOS EXCEL
================================================================================

DESCRIPCION:
Este script abre multiples archivos Excel de forma automatica.
Si los archivos estan en OneDrive en modo "online-only", los descarga
automaticamente antes de abrirlos.

--------------------------------------------------------------------------------
ARCHIVOS:
--------------------------------------------------------------------------------

1. config.json        - Configuracion con la lista de archivos a abrir
2. open_excel.py      - Script principal simplificado
3. validator.py       - Script de diagnostico avanzado (opcional)
4. ejecutar.bat       - Archivo batch para ejecutar facilmente

--------------------------------------------------------------------------------
USO RAPIDO:
--------------------------------------------------------------------------------

Opcion 1: Doble clic en "ejecutar.bat"

Opcion 2: Desde linea de comandos:
   python open_excel.py

--------------------------------------------------------------------------------
CONFIGURACION (config.json):
--------------------------------------------------------------------------------

Edita el archivo "config.json" para:
- Agregar o quitar archivos de la lista "archivos"
- Cambiar la ubicacion del archivo de log "log_file"
- Ajustar reintentos y delays para errores OLE/COM

Ejemplo:
{
  "archivos": [
    "D:\\ruta\\al\\archivo1.xlsx",
    "D:\\ruta\\al\\archivo2.xlsx"
  ],
  "log_file": "D:\\ruta\\al\\log.txt",
  "csv_resumen": "D:\\ruta\\al\\resumen.csv",
  "retry_open_attempts": 4,
  "retry_base_delay": 1.5
}

IMPORTANTE: Usa doble backslash (\\) en las rutas.

Parametros opcionales:
- retry_open_attempts: Numero de intentos al abrir archivo (default: 4)
- retry_base_delay: Delay base en segundos entre reintentos (default: 1.5)
  El delay real es exponencial: 1.5s, 3s, 6s, 12s...

--------------------------------------------------------------------------------
CARACTERISTICAS:
--------------------------------------------------------------------------------

- Detecta archivos de OneDrive no descargados
- Descarga automaticamente archivos online-only
- Verifica integridad de cada archivo antes de abrirlo
- Manejo de timeouts OLE/COM con reintentos automaticos
- Manejo de archivos bloqueados o en uso
- Reintentos exponenciales (hasta 4 intentos por defecto)
- Genera log detallado de la operacion
- Abre archivos con Excel (programa predeterminado)
- Sin emojis, salida simple y clara

--------------------------------------------------------------------------------
DIAGNOSTICO:
--------------------------------------------------------------------------------

Si tienes problemas, ejecuta el validator.py para diagnosticar:
   python validator.py

Esto generara un archivo CSV con el estado detallado de cada archivo.

--------------------------------------------------------------------------------
REQUISITOS:
--------------------------------------------------------------------------------

- Python 3.x
- Libreria openpyxl: pip install openpyxl
- Windows (para deteccion de OneDrive)
- Excel instalado

================================================================================

