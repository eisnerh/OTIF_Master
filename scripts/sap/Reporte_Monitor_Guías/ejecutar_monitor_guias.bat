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

REM Configurar la ruta de Python (ajustar según tu instalación)
REM Opción 1: Usar la ruta completa de Anaconda (recomendado)
set PYTHON_EXE=C:\ProgramData\anaconda3\python.exe

REM Opción 2: Si Python está en el PATH, usar simplemente "python"
REM set PYTHON_EXE=python

REM Verificar que Python esté disponible
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está disponible en la ruta especificada: %PYTHON_EXE%
    echo Por favor verifica la ruta de Python en este archivo .bat
    pause
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
echo Usando Python: %PYTHON_EXE%
echo.
"%PYTHON_EXE%" amalgama_y_dev_74.py

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

REM Pausar para ver los resultados (presiona cualquier tecla para cerrar)
pause

REM Salir con el código de error del script Python
exit /b %EXIT_CODE%

