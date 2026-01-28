@echo off
REM PartMart Boost Launcher for Windows
REM Version: 0.3.5d+patch4
REM Note: Use launcher_simple.bat for simpler launch

title PartMart Boost Launcher

echo ========================================================
echo.
echo     PARTMART BOOST LAUNCHER
echo     Version: 0.3.5d+patch4
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

REM Install dependencies if needed
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
    echo.
)

echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [*] Installing/updating dependencies...
pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Some dependencies failed, but continuing...
)
echo [+] Dependencies ready
echo.

echo ========================================================
echo.
echo Select mode:
echo.
echo   1. CLI Mode (Recommended for testing)
echo   2. GUI Mode (Requires PyQt6)
echo   3. Run Full Test Suite
echo   4. Exit
echo.
echo ========================================================
echo.

set /p mode="Enter choice (1-4): "

if "%mode%"=="1" (
    echo.
    echo [*] Launching CLI mode...
    echo.
    python src\main_cli.py
) else if "%mode%"=="2" (
    echo.
    echo [*] Launching GUI mode...
    echo.
    python src\main.py
) else if "%mode%"=="3" (
    echo.
    echo [*] Running full test suite...
    echo.
    python tests\test_all_modules.py
) else if "%mode%"=="4" (
    echo.
    echo Goodbye!
    goto :end
) else (
    echo.
    echo [X] Invalid choice
)

echo.
echo ========================================================
echo.

:end
pause
