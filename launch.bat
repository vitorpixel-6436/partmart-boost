@echo off
chcp 65001 >nul 2>&1
title PartMart Boost Launcher
color 0C
echo.
echo ========================================================
echo.
echo           PartMart Boost v0.3-alpha Launcher
echo           Your PC. Your Power.
echo.
echo ========================================================
echo.

REM Check Python
echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [X] CRITICAL: Python not found!
    echo.
    echo Install Python 3.11+ from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [+] Python %PYTHON_VER% detected
echo.

REM Check dependencies
echo [*] Checking dependencies...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    echo.
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    if errorlevel 1 (
        color 0C
        echo.
        echo [X] ERROR: Failed to install dependencies!
        echo.
        echo Try manually:
        echo pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [+] Dependencies installed!
) else (
    echo [+] Dependencies already installed
)

echo.
echo ========================================================
echo.
color 0A
echo [*] Launching PartMart Boost...
echo.
echo ========================================================
echo.

REM Launch app
python src/main.py
set ERROR_CODE=%ERRORLEVEL%

if %ERROR_CODE% neq 0 (
    color 0C
    echo.
    echo ========================================================
    echo.
    echo [X] LAUNCH ERROR (Error code: %ERROR_CODE%)
    echo.
    echo Check logs above and create issue on GitHub:
    echo https://github.com/vitorpixel-6436/partmart-boost/issues
    echo.
    echo ========================================================
    echo.
    pause
    exit /b %ERROR_CODE%
) else (
    color 0A
    echo.
    echo [+] Application closed correctly
    timeout /t 2 /nobreak >nul
    exit /b 0
)
