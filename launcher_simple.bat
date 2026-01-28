@echo off
REM PartMart Boost Simple Launcher
REM Version: 0.3.5d+patch4
REM Direct launch without virtual environment

title PartMart Boost
cls

echo ========================================================
echo.
echo     PARTMART BOOST
echo     Version: 0.3.5d+patch4
echo.
echo ========================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo.
    echo Install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Checking Python...
python --version
echo.

REM Check dependencies
echo Checking dependencies...
python -c "import numpy" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Installing numpy...
    pip install numpy
    echo.
)

python -c "import PyQt6" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Installing PyQt6...
    pip install PyQt6
    echo.
)

echo Dependencies OK!
echo.
echo ========================================================
echo.
echo Select mode:
echo.
echo   1. GUI Mode (Full Interface)
echo   2. CLI Mode (Command Line)
echo   3. Run Tests
echo   0. Exit
echo.
echo ========================================================
echo.

set /p choice="Your choice: "

if "%choice%"=="1" (
    echo.
    echo Starting GUI...
    echo.
    python src\main.py
) else if "%choice%"=="2" (
    echo.
    echo Starting CLI...
    echo.
    python src\main_cli.py
) else if "%choice%"=="3" (
    echo.
    echo Running tests...
    echo.
    python tests\test_all_modules.py
) else if "%choice%"=="0" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo Invalid choice!
)

echo.
echo ========================================================
echo.
pause
