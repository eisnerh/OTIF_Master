@echo off
REM Script batch para procesar archivos .txt a Excel
REM Convierte todos los archivos .txt de reportes SAP a Excel con transformaciones

title Procesar TXT a Excel - Reportes SAP
echo ========================================
echo    PROCESAR TXT A EXCEL - REPORTES SAP
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

REM Ejecutar el script Python
echo Procesando archivos .txt a Excel...
echo Fecha/Hora: %date% %time%
echo Usando Python: %PYTHON_EXE%
echo.
echo [INFO] Esto procesará todos los archivos .txt en:
echo C:\data\SAP_Extraction\reportes_ultima_hora\
echo.
"%PYTHON_EXE%" procesar_txt_a_excel.py

REM Capturar el código de salida
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% equ 0 (
    echo.
    echo ========================================
    echo Procesamiento completado exitosamente
    echo ========================================
    echo Los archivos Excel se generaron en las carpetas correspondientes
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: El procesamiento falló con código %EXIT_CODE%
    echo ========================================
    echo Revisa los mensajes de error anteriores
    echo.
)

REM Pausar para ver los resultados (presiona cualquier tecla para cerrar)
pause

REM Salir con el código de error del script Python
exit /b %EXIT_CODE%

