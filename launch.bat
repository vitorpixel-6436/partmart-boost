@echo off
chcp 65001 > nul
title PartMart Boost Launcher
color 0C
echo.
echo  ██████╗ ██████╗ ███████╗███████╗██╗   ██╗ ██████╗ ███████╗
echo  ██╔════╝██╔═══██╗██╔════╝╚══██╔══╝██║██╔╝ ██╔═══██╗██╔════╝
echo  ██║     ███████║███████╗   ██║   █████╔╝ ███████║███████╗
echo  ██║     ██╔══██║██╔═══╝    ██║   ██╔═██╗ ██╔══██║╚════██║
echo  ╚██████╗██║  ██║██║        ██║   ██║ ╚██╗██║  ██║███████║
echo  ╚═════╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
echo.
echo         🐉 PartMart Boost v0.2-alpha Launcher
echo         Твой ПК. Твоя мощь.
echo.
echo  ========================================================
echo.

REM Check Python
echo  [✓] Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo  [✗] CRITICAL: Python не найден!
    echo.
    echo  Установите Python 3.11+ с:
    echo  https://www.python.org/downloads/
    echo.
    echo  Важно: при установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo  [✓] Python %PYTHON_VER% обнаружен
echo.

REM Check dependencies
echo  [✓] Проверка зависимостей...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo  [→] Установка зависимостей...
    echo.
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    
    if errorlevel 1 (
        color 0C
        echo.
        echo  [✗] ERROR: Ошибка установки зависимостей!
        echo.
        echo  Попробуйте вручную:
        echo  pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo  [✓] Зависимости установлены!
) else (
    echo  [✓] Зависимости уже установлены
)

echo.
echo  ========================================================
echo.
color 0A
echo  🚀 ЗАПУСК PartMart Boost...
echo.
echo  ========================================================
echo.

REM Launch app
python src/main.py
set ERROR_CODE=%ERRORLEVEL%

if %ERROR_CODE% neq 0 (
    color 0C
    echo.
    echo  ========================================================
    echo.
    echo  [✗] ОШИБКА ЗАПУСКА (Error code: %ERROR_CODE%)
    echo.
    echo  Проверьте логи выше и создайте issue на GitHub:
    echo  https://github.com/vitorpixel-6436/partmart-boost/issues
    echo.
    echo  ========================================================
    echo.
    pause
    exit /b %ERROR_CODE%
) else (
    color 0A
    echo.
    echo  [✓] Приложение закрыто корректно
    timeout /t 2 /nobreak >nul
    exit /b 0
)
