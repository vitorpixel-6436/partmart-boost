@echo off
chcp 65001 > nul
echo ╔═══════════════════════════════════════╗
echo ║   🐉 PartMart Boost Launcher v0.2    ║
echo ╚═══════════════════════════════════════╝
echo.
echo Проверка зависимостей...
echo.

python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Скачайте Python 3.11+ с https://python.org
    pause
    exit /b 1
)

echo ✅ Python обнаружен
echo.
echo Установка зависимостей...
python -m pip install --upgrade pip > nul 2>&1
python -m pip install -r requirements.txt > nul 2>&1

if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей
    echo Попробуйте: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Зависимости установлены
echo.
echo 🚀 Запуск PartMart Boost...
echo.
python src/main.py

if errorlevel 1 (
    echo.
    echo ❌ Ошибка запуска приложения
    echo Проверьте логи выше
    pause
)
