@echo off
REM PartMart Boost Launcher for Windows
REM Version: 0.3.5d (Package 3.9a, Stage 7.8a)
REM Launches new launcher.py with Modern GUI support

title PartMart Boost - Stage 7.8a

echo ========================================================
echo.
echo     PARTMART BOOST LAUNCHER
echo     Version: 0.3.5d (Package 3.9a, Stage 7.8a)
echo     Liquid Glass UI Revolution
echo.
echo ========================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [+] Python found
echo.

REM Install PyQt6 if needed
echo [*] Checking dependencies...
pip install -q PyQt6 psutil nvidia-ml-py3 colorama
if %errorlevel% neq 0 (
    echo [!] Some dependencies failed, but continuing...
)
echo [+] Dependencies ready
echo.

echo [*] Launching PartMart Boost...
echo.

REM Launch new launcher.py with Modern GUI support
python launcher.py

if %errorlevel% neq 0 (
    echo.
    echo [X] Launch failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo.

pause
