@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================================
echo.
echo           PartMart Boost Launcher
echo           Your PC. Your Power.
echo.
echo ========================================================
echo.

REM Check Python installation
echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found!
    echo.
    echo Please install Python 3.11 or 3.12 from python.org
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [+] Python !PYTHON_VERSION! detected

REM Check if version is 3.14 (not recommended)
echo !PYTHON_VERSION! | findstr "3.14" >nul
if not errorlevel 1 (
    echo.
    echo [!] WARNING: Python 3.14 has compatibility issues with PyQt6
    echo [!] Recommended: Python 3.11 or 3.12
    echo.
    echo Continue anyway? Press Ctrl+C to cancel, or
    pause
)

echo.
echo [*] Setting up virtual environment...

REM Check if venv exists
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [X] Failed to create venv
        pause
        exit /b 1
    )
    echo [+] Virtual environment created
) else (
    echo [+] Virtual environment found
)

echo.
echo [*] Activating venv...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [X] Failed to activate venv
    pause
    exit /b 1
)

echo [+] Venv activated
echo.
echo [*] Checking dependencies...

REM Check if requirements are installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [X] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [+] Dependencies installed
) else (
    echo [+] Dependencies already installed
)

echo.
echo ========================================================
echo.
echo [*] Launching PartMart Boost...
echo.
echo ========================================================
echo.

python src/main.py

if errorlevel 1 (
    echo.
    echo ========================================================
    echo.
    echo [X] LAUNCH ERROR
    echo.
    echo Check logs above and create issue on GitHub:
    echo https://github.com/vitorpixel-6436/partmart-boost/issues
    echo.
    echo ========================================================
    echo.
)

pause
