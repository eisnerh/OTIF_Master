@echo off
REM Script batch para ejecutar amalgama_reportes_ultima_hora.py
REM Descarga múltiples reportes de SAP con fecha de ayer
REM Este archivo puede ejecutarse manualmente o desde el Programador de Tareas de Windows

title Reportes Última Hora - Descarga Automática
echo ========================================
echo    REPORTES ULTIMA HORA - DESCARGA
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
    pause
    exit /b 1
)

REM Verificar que SAP está abierto
echo [INFO] Asegúrate de que SAP esté abierto y la sesión iniciada
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
echo.

REM Ejecutar el script Python
echo Ejecutando descarga de reportes...
echo Fecha/Hora: %date% %time%
echo Usando Python: %PYTHON_EXE%
echo.
echo [INFO] Esto puede tomar varios minutos dependiendo de la cantidad de reportes
echo [INFO] Los archivos se guardarán en: C:\data\SAP_Extraction\reportes_ultima_hora
echo.
"%PYTHON_EXE%" amalgama_reportes_ultima_hora.py

REM Capturar el código de salida
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% equ 0 (
    echo.
    echo ========================================
    echo Descarga completada exitosamente
    echo ========================================
    echo Los reportes se guardaron en:
    echo C:\data\SAP_Extraction\reportes_ultima_hora
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: La descarga falló con código %EXIT_CODE%
    echo ========================================
    echo Revisa los mensajes de error anteriores
    echo.
)

REM Pausar para ver los resultados (presiona cualquier tecla para cerrar)
pause

REM Salir con el código de error del script Python
exit /b %EXIT_CODE%

