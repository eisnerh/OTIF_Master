@echo off
REM Script batch para ejecutar amalgama_y_dev_74.py
REM Este archivo puede ejecutarse manualmente o desde el Programador de Tareas de Windows

title Monitor Guías - Ejecución Automática
echo ========================================
echo    MONITOR GUIAS - EJECUCION AUTOMATICA
echo ========================================
echo.

REM Obtener la ruta del directorio donde está este script
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python y asegúrate de que esté en el PATH
    exit /b 1
)

REM Verificar que existe el archivo credentials.ini
if not exist "credentials.ini" (
    echo ERROR: No se encontró el archivo credentials.ini
    echo Por favor crea el archivo a partir de credentials.ini.example
    exit /b 1
)

REM Ejecutar el script Python
echo Ejecutando script de Monitor Guías...
echo Fecha/Hora: %date% %time%
echo.
python amalgama_y_dev_74.py

REM Capturar el código de salida
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% equ 0 (
    echo.
    echo ========================================
    echo Ejecución completada exitosamente
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR: La ejecución falló con código %EXIT_CODE%
    echo ========================================
)

REM Salir con el código de error del script Python
exit /b %EXIT_CODE%

