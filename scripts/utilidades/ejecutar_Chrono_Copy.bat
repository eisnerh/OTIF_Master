@echo off
REM Script batch para ejecutar amalgama_reportes_ultima_hora.py
REM Descarga múltiples reportes de SAP con fecha de ayer
REM Este archivo puede ejecutarse manualmente o desde el Programador de Tareas de Windows

title Copiar Último Arhivo de Excel - Descarga Automática
echo ========================================
echo    Copia de archivo de Excel y renombrar con fecha de ayer
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
echo Ejecutando descarga y procesamiento de reportes...
echo Fecha/Hora: %date% %time%
echo Usando Python: %PYTHON_EXE%
echo.
echo [INFO] Esto puede tomar 1-2 minutos (depende del tamaño de los reportes)
echo.
"%PYTHON_EXE%" ChronoCopy.py

REM Capturar el código de salida
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% equ 0 (
    echo.
    echo ========================================
    echo Proceso completado exitosamente
    echo ========================================
    echo Los reportes se guardaron en:
    echo C:\Users\ELOPEZ21334\OneDrive - Distribuidora La Florida S.A\Retail\Proyectos de Reportes\2023\Torre de Control\YTD 2025
    echo.
    echo Cada carpeta contiene:
    echo   - archivo.txt  ^(original de SAP^)
    echo   - archivo.xlsx ^(procesado para analisis^)
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: El proceso fallo con codigo %EXIT_CODE%
    echo ========================================
    echo Revisa los mensajes de error anteriores
    echo.
)


REM Salir con el código de error del script Python
exit /b %EXIT_CODE%

