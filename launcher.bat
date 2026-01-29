@echo off
REM PartMart Boost Launcher for Windows
REM Version: 0.3.5d_hotfix8 (Package 3.9a, Stage 7.8a)
REM Standalone Modern GUI with cache cleanup

title PartMart Boost - Stage 7.8a (hotfix8)

echo ========================================================
echo.
echo     PARTMART BOOST LAUNCHER
echo     Version: 0.3.5d_hotfix8 (Package 3.9a, Stage 7.8a)
echo     Liquid Glass UI Revolution
echo     Auto-Fix: PyQt6 + Cache cleanup
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

REM Install basic dependencies
echo [*] Checking dependencies...
pip install -q psutil nvidia-ml-py3 colorama >nul 2>&1
echo [+] Basic dependencies ready
echo.

echo [*] Launching PartMart Boost...
echo [*] Standalone GUI - no cache issues!
echo [*] PyQt6 will be auto-fixed if needed
echo.

REM Launch with cache cleanup
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
