@echo off
REM ============================================================
REM Script batch para ejecutar Reporte PLR
REM ============================================================

echo.
echo ============================================================
echo  REPORTE PLR - Extraccion Automatica
echo ============================================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que existe el archivo de credenciales
if not exist "credentials.ini" (
    echo ERROR: No se encontro el archivo credentials.ini
    echo Por favor, copia credentials.ini.example a credentials.ini
    echo y configura tus credenciales SAP.
    echo.
    pause
    exit /b 1
)

REM Verificar que Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python desde https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Ejecutar el script Python
echo Ejecutando reporte PLR...
echo.
python amalgama_y_rep_plr.py

REM Verificar si hubo error
if errorlevel 1 (
    echo.
    echo ERROR: El script termino con errores
    echo Revisa los mensajes anteriores para mas detalles
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Proceso completado exitosamente
echo ============================================================
echo.
pause


