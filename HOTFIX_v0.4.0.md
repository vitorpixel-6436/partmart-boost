# 🔧 HOTFIX v0.4.0 - System Monitor Исправления

## Проблемы

### 1. Ошибка импорта
```
CRITICAL: Fatal error: No module named 'system_monitor'
```

### 2. None values в метриках
```
ERROR: Failed to update system data: int() argument must be a string, 
a bytes-like object or a real number, not 'NoneType'
```

### 3. FallbackGPUMonitor без get_name()
```
ERROR: GPU Monitor init failed: 'FallbackGPUMonitor' 
object has no attribute 'get_name'
```

## Решения

### ✅ system_monitor.py (NEW)
Создан **обратно совместимый wrapper**:
- Предоставляет старый API
- Использует новый MonitorManager
- Полная обратная совместимость

### ✅ main_window.py - Безопасная обработка None
- Проверка на None перед int()
- Дефолтные значения (0, "--")
- Отображение "--" если данных нет
- Traceback в консоль для отладки

### ✅ fallback_gpu.py - Добавлен get_name()
- `get_name()` → возвращает имя GPU
- `get_data()` alias для `get_gpu_data()`
- Fallback: "No GPU detected (Fallback)"

### ✅ GAMES_AVAILABLE scope fix
- Глобальная переменная
- `self.games_available` в классе
- Избежание UnboundLocalError

## Как запустить

### 1. Скачать обновления
```bash
cd "U:\Users\admir\Downloads\pmb beta\pmb"
git pull origin main
```

### 2. Запустить
```bash
# Через лаунчер (рекомендуется)
start_app.bat

# ИЛИ напрямую
cd src
python main.py
```

## Что должно работать

### ✅ UI запускается
- Окно открывается 
- 4 вкладки: Home, GPU Control, RAM Tuner, Игры
- Красно-черная тема

### ✅ Метрики (Home)
**Если данные доступны:**
- GPU Temperature: XX°C
- RAM Usage: XX%
- CPU Load: XX%

**Если нет доступа:**
- Отображается "--" (не "None")
- Нет ошибок в консоли

### ⚠️ Ожидаемые предупреждения
```bash
[WARN] Game Profiles not available: No module named 'game_profiles'
# Это нормально - модуль еще не создан

[DEBUG] CPU temp sensor detection failed: module 'psutil' has no attribute 'sensors_temperatures'
# Нормально для Windows - температура CPU может быть недоступна
```

### ❌ НЕ должно быть
```bash
# Этих ошибок больше не будет:
ERROR: Failed to update system data: int() argument must be...
CRITICAL: Fatal error: No module named 'system_monitor'
ERROR: 'FallbackGPUMonitor' object has no attribute 'get_name'
```

## Отладка

### Если метрики показывают "--"

1. **Проверить MonitorManager:**
```python
python -c "from monitors.manager import MonitorManager; m = MonitorManager(); print(m.get_all_data())"
```

2. **Проверить SystemMonitor wrapper:**
```python
python -c "from system_monitor import SystemMonitor; m = SystemMonitor(); print(m.get_gpu_data())"
```

3. **Запустить тест:**
```bash
cd src
python system_monitor.py
```

### Если GPU не обнаружен
Попробуйте запустить от **администратора**:
- Некоторые данные требуют повышенных прав
- GPU температура может быть недоступна

### Sovereignty Score: 50/100
Это **нормально** для Windows без PyNVML:
- 100 = полная независимость (только native API)
- 50 = гибрид (psutil + native)
- 0 = полная зависимость от библиотек

## Известные ограничения

### GPU
- ⚠️ Температура может быть недоступна без PyNVML
- ⚠️ Fallback монитор использует WMIC (базовые данные)
- ✅ Имя GPU определяется всегда

### CPU
- ⚠️ Температура недоступна на Windows (только Linux)
- ✅ Загрузка, частота, ядра - работают

### RAM
- ✅ Все метрики доступны
- ⚠️ XMP статус может быть недоступен

### Game Profiles
- ❌ Модуль еще не создан (profiles/game_profiles.py)
- ❌ Вкладка "Игры" пустая
- 🕒 **В разработке**

## Changelog

### [0.4.0-hotfix2] - 2026-01-28 07:45 GMT

#### Fixed
- 🔧 **None handling**: Безопасная обработка int(None)
- 🔧 **FallbackGPUMonitor**: Добавлен get_name() и get_data()
- 🔧 **GAMES_AVAILABLE**: Исправлен scope UnboundLocalError
- 🔧 **UI metrics**: Отображение "--" вместо "None°C"

#### Added
- ✅ Traceback в консоль для отладки
- ✅ Дефолтные значения для всех метрик
- ✅ Проверка на 0 перед отображением

### [0.4.0-hotfix1] - 2026-01-28 07:28 GMT

#### Added
- ✅ `system_monitor.py` - обратная совместимость
- ✅ Game Profiles система (UI)
- ✅ Улучшенный UI с tooltips
- ✅ Profile editor с валидацией

#### Fixed
- 🔧 Import error: `No module named 'system_monitor'`
- 🔧 Структура импортов (monitors/manager.py)

## Следующие шаги

### 🎮 Game Profiles (Приоритет)
1. Создать `profiles/game_profiles.py`
2. Создать `profiles/game_detector.py`
3. Создать `profiles/optimization_applier.py`
4. Заполнить вкладку "Игры"

### 🎮 GPU Control
1. Создать `ui/gpu_widget.py`
2. GPU overclocking controls
3. Fan curve editor
4. Power limit slider

### 🧠 RAM Tuner
1. Создать `ui/ram_widget.py`
2. XMP profile selector
3. Memory cleaner
4. Process priority manager

### 🎨 Custom UI Components
ПОСТЕПЕННО заменять PyQt6 на свои:
1. **Начать с простых компонентов:**
   - Custom buttons (с анимацией)
   - Progress bars (с gradients)
   - Cards (с hover эффектами)

2. **Затем сложные:**
   - Sliders (для GPU/fan control)
   - Charts (для графиков)
   - Custom windows

3. **В конце:**
   - Полная замена PyQt6
   - Свой rendering engine

**Варианты реализации:**
- **Web-based** (Flask/FastAPI + HTML/CSS/JS) - САМЫЙ ПРОСТОЙ
- **PyGame** - хорошо для 2D UI
- **DearPyGui** - быстрый, но GPU-требовательный
- **Custom OpenGL/DirectX** - максимальный контроль

## Поддержка

### Если проблема не решена:
1. 🐛 **GitHub Issue**: https://github.com/vitorpixel-6436/partmart-boost/issues
2. 📝 **Приложи лог:**
   - Весь вывод терминала
   - Скриншот UI
3. 📊 **Система:**
   - `python --version`
   - ОС: Windows/Linux
   - GPU модель

## Разработчики

**PartMart Team**  
Version: 0.4.0-hotfix2  
Date: 2026-01-28 07:45 GMT

Commits:
- [3ec22ae](https://github.com/vitorpixel-6436/partmart-boost/commit/3ec22ae8496225e5422fba41d7e02b087d204db6) - Handle None values
- [a8f050f](https://github.com/vitorpixel-6436/partmart-boost/commit/a8f050ff77735dcf0e81cf2073f463b830692466) - FallbackGPU get_name()
- [3eac5d6](https://github.com/vitorpixel-6436/partmart-boost/commit/3eac5d6b8df0a3496f6b8d3f310d1d961dac44ca) - GAMES_AVAILABLE fix
- [1dc076f](https://github.com/vitorpixel-6436/partmart-boost/commit/1dc076f57726fe96826fba59992d090bbe73b923) - system_monitor wrapper

---

💡 **Совет:** Если метрики показывают "--", попробуйте запустить от администратора!
