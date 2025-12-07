@echo off
REM =====================================
REM Stalker - Script de Instalacion
REM Instala dependencias y prepara el proyecto
REM =====================================

echo.
echo ==========================================
echo   Stalker - Instalacion de Dependencias
echo ==========================================
echo.

REM Verificar que Python este instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo.
    echo Por favor instale Python 3.9 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegurese de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

echo [1/4] Python detectado correctamente
python --version
echo.

REM Verificar que pip este disponible
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no esta disponible
    echo.
    echo Intentando instalar pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo ERROR: No se pudo instalar pip
        pause
        exit /b 1
    )
)

echo [2/4] pip detectado correctamente
python -m pip --version
echo.

REM Actualizar pip a la ultima version
echo [3/4] Actualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias del proyecto
echo [4/4] Instalando dependencias del proyecto...
echo.
echo Instalando paquetes desde requirements.txt...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Hubo un problema al instalar las dependencias
    echo.
    echo Intente ejecutar manualmente:
    echo   python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Instalacion Completada Exitosamente!
echo ==========================================
echo.
echo Las dependencias han sido instaladas correctamente.
echo.
echo Para ejecutar el proyecto:
echo   python main.py
echo.
echo Para crear el ejecutable:
echo   python build_exe.py
echo.
pause
