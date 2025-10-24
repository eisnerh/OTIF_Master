@echo off
title OTIF Master - Sistema Unificado
echo ========================================
echo    SISTEMA OTIF MASTER - INICIADOR
echo ========================================
echo.

:: Navegar al directorio del script
cd /d "%~dp0\.."

:: Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python y asegúrate de que esté en el PATH
    pause
    exit /b 1
)

:: Ejecutar el iniciador principal
echo Iniciando sistema OTIF Master...
echo.
python iniciar_otif.py

echo.
echo Sistema finalizado.
pause