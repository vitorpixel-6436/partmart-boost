# 🔧 HOTFIX v0.4.0 - System Monitor Import Fix

## Проблема

```
CRITICAL: Fatal error: No module named 'system_monitor'
```

## Решение

Создан **обратно совместимый wrapper** `system_monitor.py`, который:
- ✅ Предоставляет старый API (`get_gpu_data()`, `get_ram_data()`, `get_cpu_data()`)
- ✅ Использует новый `MonitorManager` под капотом
- ✅ Поддерживает все существующие функции

## Что исправлено

### 1. **system_monitor.py** (NEW)
Добавлен wrapper-класс для обратной совместимости:
```python
from system_monitor import SystemMonitor

monitor = SystemMonitor()
data = monitor.get_gpu_data()  # Работает как раньше!
```

### 2. **games_widget.py** 
Улучшен UI:
- 🎨 Tooltips на всех элементах
- 🎨 Hover-анимации и быстрые действия
- 🎨 Полноценный редактор профилей
- 🎨 Empty states с подсказками
- 🎨 Подтверждение удаления

### 3. **main_window.py**
Интеграция Game Profiles:
- 🎮 Новая вкладка "Игры" (4-я кнопка в навигации)
- 🎮 Автоматическое обнаружение игр
- 🎮 Применение профилей при запуске
- 🎮 Уведомления о статусе

## Как запустить

### Вариант 1: Через лаунчер (рекомендуется)
```bash
# Скачать последнюю версию с GitHub
git pull origin main

# Запустить лаунчер
start_app.bat
```

### Вариант 2: Напрямую
```bash
cd src
python main.py
```

## Структура проекта

```
src/
├── system_monitor.py          # NEW! Wrapper для обратной совместимости
├── monitors/                   # Новая система мониторинга
│   ├── manager.py             # MonitorManager (новый SystemMonitor)
│   ├── gpu_monitor.py
│   ├── cpu_monitor.py
│   └── ram_monitor.py
├── profiles/                   # Game Profiles система
│   ├── game_profiles.py
│   ├── game_detector.py
│   └── optimization_applier.py
└── ui/
    ├── games_widget.py         # NEW! UI для игровых профилей
    └── main_window.py          # Обновлен: интеграция Games
```

## Новые возможности в v0.4.0

### 🎮 Game Profiles
- **Автоматическая оптимизация** для игр
- **Создание профилей** с GPU/RAM настройками
- **Обнаружение запуска** игры в реальном времени
- **Применение профиля** автоматически при запуске
- **Откат изменений** при закрытии игры

### 🎨 Улучшенный UI
- **Tooltips** на всех элементах
- **Hover-эффекты** и анимации
- **Интуитивный редактор** профилей
- **Steam-стилизация** (синий #66c0f4)
- **Empty states** с подсказками

### ⚡ Производительность
- **MonitorManager** с <10ms латентностью
- **Sovereignty система** для независимости от внешних библиотек
- **Кэширование данных** для быстрого доступа

## Проверка установки

Запустите тест:
```python
python -c "from system_monitor import SystemMonitor; m = SystemMonitor(); print('✅ OK')"
```

Должно вывести: `✅ OK`

## Известные ограничения

1. **Game Profiles** требует запуска от администратора для некоторых оптимизаций
2. **GPU overclocking** доступен только для NVIDIA (через PyNVML)
3. **RAM priority** требует прав администратора

## Changelog

### [0.4.0] - 2026-01-28

#### Added
- ✅ `system_monitor.py` - обратная совместимость
- ✅ Game Profiles система
- ✅ Улучшенный UI для игровых профилей
- ✅ Tooltips и hover-эффекты
- ✅ Profile editor с валидацией

#### Fixed
- 🔧 Import error: `No module named 'system_monitor'`
- 🔧 Структура импортов (monitors/manager.py)

#### Changed
- 🔄 `SystemMonitor` → `MonitorManager` (внутри)
- 🔄 Версия: 0.3.4 → 0.4.0

## Поддержка

Если проблема не решена:
1. Создай issue: https://github.com/vitorpixel-6436/partmart-boost/issues
2. Приложи лог из лаунчера
3. Укажи версию Python: `python --version`

## Разработчик

**PartMart Team**  
Version: 0.4.0-alpha  
Date: 2026-01-28

---

💡 **Совет:** При первом запуске может потребоваться переустановка зависимостей:
```bash
pip install --upgrade -r requirements.txt
```
