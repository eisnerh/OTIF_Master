@echo off
title Sistema OTIF Master - Menu Interactivo
color 0A

echo.
echo ========================================
echo    SISTEMA OTIF MASTER - INICIANDO
echo ========================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python y vuelve a intentar
    pause
    exit /b 1
)

REM Verificar que estamos en el directorio correcto
if not exist "menu_cmd.py" (
    echo ERROR: No se encontró menu_cmd.py
    echo Asegúrate de estar en el directorio correcto del proyecto
    pause
    exit /b 1
)

REM Iniciar el menú
echo Iniciando menú interactivo...
python iniciar_menu.py

REM Si hay error, mostrar alternativas
if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar el menú
    echo.
    echo Alternativas:
    echo   python menu_cmd.py
    echo   python ejecutar_modulo.py
    echo.
    pause
)
