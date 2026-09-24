@echo off
title Sistema Estadístico Interactivo
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================================================
echo    INICIANDO SISTEMA ESTADÍSTICO INTERACTIVO (WEB)
echo ======================================================================
echo.

:: 1. Verificar si existe el entorno virtual local (.venv)
if not exist ".venv\Scripts\python.exe" (
    echo [AVISO] No se encontró el entorno virtual local. Configurando por primera vez...
    
    :: Verificar si python está en PATH
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python no está instalado o no se encuentra en el PATH de Windows.
        echo Por favor instala Python 3.10 o superior desde https://www.python.org/
        pause
        exit /b 1
    )
    
    echo Creando entorno virtual en .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    
    echo Instalando dependencias necesarias (Flask, ReportLab, Matplotlib, SciPy)...
    .venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual configurado exitosamente.
    echo.
)

:: 2. Iniciar la aplicación web con el entorno virtual
echo Iniciando servidor local...
echo Tu navegador predeterminado se abrirá automáticamente en breve.
echo Presiona Ctrl+C en esta ventana para detener el servidor cuando termines.
echo.

.venv\Scripts\python.exe app.py

if errorlevel 1 (
    echo.
    echo [AVISO] El servidor se ha detenido con código de salida %errorlevel%.
    pause
)
