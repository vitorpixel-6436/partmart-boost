# 🐉 PartMart Boost v0.3-alpha

**Игровой оптимизатор ПК с РЕАЛЬНЫМ мониторингом и автоматическими профилями для игр**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078d4)](https://www.microsoft.com/windows)
![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange)

---

## 🆕 Что нового в v0.3-alpha (28 января 2026)

### ✅ 🎮 GAME PROFILES (НОВИНКА!)
- **Автоматическое обнаружение игр**: детектирует запуск 8+ популярных игр (GTA 5, Cyberpunk, CS2, Tarkov, Minecraft, Valorant, League, RDR2)
- **Авто-оптимизация**: применяет профиль автоматически при запуске игры
- **Умные настройки**: индивидуальные GPU/RAM настройки для каждой игры
- **RAM Cleanup**: очистка памяти перед запуском игры (EmptyWorkingSet)
- **Process Priority**: повышение приоритета игрового процесса (high/realtime)
- **Power Plans**: автоматическое переключение на High Performance

### Пример работы:
```
🎮 [AUTO-OPTIMIZE] Grand Theft Auto V started!
⚙️ Applying optimizations:
   🧹 RAM Freed: 847 MB
   ✅ Process Priority: HIGH
   📡 GPU Core: +100 MHz
   📡 GPU Memory: +400 MHz
   🔋 Power Plan: HIGH_PERFORMANCE
✅ Profile applied successfully!
```

### ✅ Улучшенный мониторинг
- **GPU**: температура (core + hotspot), частоты, загрузка, питание через `pynvml`
- **CPU**: загрузка, температура, частота через `psutil`
- **RAM**: использование, скорость, автоопределение XMP статуса через WMI
- **Автообновление**: данные обновляются каждые 2 секунды

### ⚠️ Что еще в разработке
- ✅ ~~Game Profiles~~ — **ГОТОВО!** ✅
- ⏳ GPU Optimizer (undervolt, OC) — частично реализовано (нужен MSI Afterburner)
- ⏳ RAM XMP Enable — Coming Soon
- ⏳ FrameGen (FSR 3, DLSS 3) — Coming Soon

---

## 📥 Установка (ПРОСТАЯ)

### Способ 1: Один клик (рекомендуется) 🚀

```bash
# 1. Скачай проект
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# 2. Запусти launcher (автоматически установит зависимости)
launch.bat
```

**Готово!** Приложение автоматически установит все зависимости и запустится.

### Способ 2: Тестирование Game Profiles

```bash
# Запустить автоматическую оптимизацию игр
python src/profiles/game_detector.py

# Посмотреть все доступные профили
python src/profiles/game_profiles.py

# Тест системы оптимизации
python src/profiles/optimization_applier.py
```

### Требования:
- **Python**: 3.11+ (3.14 поддерживается)
- **ОС**: Windows 10 (build 19043+) или Windows 11
- **RAM**: 2GB+
- **GPU**: NVIDIA (рекомендуется), AMD, Intel Arc
- **MSI Afterburner** (опционально): для GPU overclocking

---

## 🎮 Что это?

**PartMart Boost** — desktop приложение для покупателей ПК от [PartMart](https://avito.ru/user/partmart) (Samara). 

### Текущие возможности (v0.3-alpha):
- ✅ Реальное отображение температур GPU/CPU
- ✅ Мониторинг загрузки GPU и RAM в реальном времени
- ✅ Автоопределение XMP статуса памяти
- ✅ **Автоматические игровые профили (8 игр)**
- ✅ **RAM cleanup перед запуском игр**
- ✅ **Автоматическое управление приоритетом процессов**
- ✅ **Переключение Power Plans**
- ✅ Steam-inspired интерфейс
- ✅ Автообновление данных каждые 2 секунды

### Поддерживаемые игры:
1. **GTA 5** (Grand Theft Auto V)
2. **Cyberpunk 2077**
3. **Counter-Strike 2** (CS2)
4. **Escape from Tarkov**
5. **Minecraft** (Java Edition)
6. **Valorant**
7. **League of Legends**
8. **Red Dead Redemption 2** (RDR2)

### Планируется (v0.5-beta):
- ⏳ GPU Optimizer (полная интеграция с MSI Afterburner)
- ⏳ RAM XMP Enable
- ⏳ Интеграция профилей в основной UI
- ⏳ FrameGen (FSR 3, DLSS 3)
- ⏳ Пользовательские профили
- ⏳ RTSS Overlay

---

## 🖼️ Интерфейс

### Главная страница
```
┌─────────────────────────────────────────────────────┐
│ 🐉 PartMart Boost v0.3                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🚀 БЫСТРЫЙ СТАРТ                                   │
│  Оптимизируй свой ПК в один клик                    │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │ 💻 СТАТУС СИСТЕМЫ (РЕАЛЬНЫЕ ДАННЫЕ)            │ │
│  │                                                │ │
│  │ 🎮 GPU: NVIDIA RTX 3060 (45% load)             │ │
│  │ 🧠 RAM: 14.2GB / 16GB (3200 MHz)               │ │
│  │ 🌡️ GPU: 68°C (hotspot) | CPU: 55°C            │ │
│  │                                                │ │
│  │ █████████████████░░░░░ RAM 89%                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │ 🎮 АКТИВНЫЕ ИГРЫ                                │ │
│  │                                                │ │
│  │ ▶️ GTA 5 - Профиль активен (+100 MHz GPU)     │ │
│  │ 📊 RAM Cleanup: 847 MB freed                   │ │
│  │ ⚡ Priority: HIGH | Power: High Performance    │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Sidebar (Steam-inspired)
```
┌──────────────────┐
│      🐉          │
│  PartMart Boost  │
│  Твой ПК. Твоя   │
│      мощь.       │
├──────────────────┤
│ 🏠  ГЛАВНАЯ      │ ← Active
│ ⚡  GPU CONTROL  │
│ 🧠  RAM TUNER    │
│ 🎮  ИГРЫ         │ ← NEW!
│ ⚙️  НАСТРОЙКИ    │
├──────────────────┤
│   v0.3.0-alpha   │
└──────────────────┘
```

---

## ⚙️ Технический стек

### Мониторинг
- **pynvml** (13.0.1+) — NVIDIA GPU мониторинг
- **psutil** (7.2.1+) — CPU/RAM/Process мониторинг
- **wmi** (1.5.1+) — XMP detection

### Оптимизация (NEW!)
- **ctypes** — EmptyWorkingSet для RAM cleanup
- **subprocess** — Power Plan management (powercfg)
- **psutil** — Process priority control
- **MSI Afterburner** (опционально) — GPU overclocking

### UI
- **PyQt6** (6.10+) — современный интерфейс
- **QTimer** — автообновление данных
- **QSS** — Steam-inspired стили

### Язык и платформа
- **Python** 3.11+ (3.14 поддерживается)
- **Windows** 10/11 только
- **Размер**: ~150MB

---

## 📊 Структура проекта

```
partmart-boost/
├─ launch.bat                      # 🚀 Launcher (1-click)
├─ VERSION                         # Версия (0.3.0-alpha)
├─ src/
│  ├─ main.py                      # Entry point
│  ├─ system_monitor.py            # Реальный мониторинг
│  ├─ ai_optimizer.py              # AI рекомендации
│  ├─ profiles/                    # 🆕 Game Profiles System
│  │  ├─ game_profiles.py          # Менеджер профилей
│  │  ├─ game_detector.py          # Детектор игр
│  │  └─ optimization_applier.py   # Применение оптимизаций
│  ├─ ui/
│  │  ├─ main_window.py            # Главное окно
│  │  ├─ ai_widget.py              # AI insights widget
│  │  └─ theme.qss                 # Steam-inspired theme
│  └─ gpu/
│     ├─ nvidia_control.py         # NVIDIA (pynvml)
│     └─ amd_control.py            # AMD (симуляция)
├─ config/
│  └─ profiles/                    # JSON профили игр
├─ requirements.txt                # Зависимости
└─ README.md                       # Это файл
```

---

## 🎮 Как использовать Game Profiles

### Автоматический режим (рекомендуется)
```bash
# Запустить фоновый сервис
python src/profiles/game_detector.py

# Теперь просто запусти любимую игру!
# Приложение автоматически:
# 1. Обнаружит игру
# 2. Применит оптимальный профиль
# 3. Очистит RAM
# 4. Повысит приоритет процесса
# 5. Включит High Performance режим
```

### Ручной режим
```python
from src.profiles.game_profiles import GameProfileManager
from src.profiles.optimization_applier import ProfileApplier

# Создать менеджер профилей
manager = GameProfileManager()

# Получить профиль для игры
profile = manager.get_profile("gta5")

# Применить оптимизации
applier = ProfileApplier()
applier.apply_profile(profile, game_pid)
```

### Создать свой профиль
```python
from src.profiles.game_profiles import GameProfileManager

manager = GameProfileManager()

# Создать профиль для новой игры
manager.create_profile(
    game_id="my_game",
    game_name="My Awesome Game",
    executable="game.exe",
    gpu_clock_offset=120,
    gpu_mem_offset=450,
    gpu_power_limit=110,
    ram_cleanup=True,
    ram_priority="high"
)
```

---

## 🔧 Устранение проблем

### Game Profiles не применяются
1. Убедись, что запущен `game_detector.py`
2. Проверь, что игра в списке поддерживаемых
3. Запусти от имени администратора (для повышения приоритета)

### GPU Overclocking не работает
- Установи [MSI Afterburner](https://www.msi.com/Landing/afterburner)
- Убедись, что он запущен в фоне
- Проверь путь в `optimization_applier.py`

### Ошибка "Could not parse stylesheet"
✅ **Исправлено в v0.2** — убраны некорректные CSS свойства из QSS

### Статичные данные (температура не меняется)
✅ **Исправлено в v0.2** — реальное чтение через pynvml/psutil + QTimer

---

## 🛡️ Безопасность

### Текущая версия (v0.3-alpha)
- ✅ **RAM Cleanup** — безопасный EmptyWorkingSet (Windows API)
- ✅ **Process Priority** — безопасное повышение через psutil
- ✅ **Power Plans** — стандартный powercfg
- ⚠️ **GPU OC** — только с MSI Afterburner (безопасно)
- ✅ **Auto-revert** — восстановление настроек после закрытия игры

### Будущие версии (v0.5+)
- ⏳ **Права админа** — для полного доступа к оптимизациям
- ⏳ **Stability test** — перед применением агрессивных твиков
- ⏳ **Backup system** — автоматическое сохранение дефолтных настроек

---

## 🗓️ Дорожная карта

| Версия | Статус | Фичи |
|--------|--------|------|
| **v0.3-alpha** | ✅ **ТЕКУЩАЯ** | Game Profiles, RAM cleanup, Process priority |
| **v0.4-alpha** | 🔄 В разработке | Интеграция профилей в UI, AMD GPU поддержка |
| **v0.5-beta** | 📅 Февраль 2026 | FrameGen (FSR 3), RAM XMP Enable, RTSS Overlay |
| **v1.0-release** | 📅 Март 2026 | Premium tier, NSIS installer, Code signing |

---

## 🐛 Известные проблемы

- ⚠️ **CPU температура**: не работает без OpenHardwareMonitor/HWiNFO
- ⚠️ **AMD GPU OC**: пока только симуляция (реальный контроль в v0.4)
- ⚠️ **MSI Afterburner CLI**: нужна документация по флагам командной строки
- ⚠️ **Game detection**: может пропустить игры с нестандартными процессами

**Отчеты о багах**: [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)

---

## 📝 Changelog

### v0.3.0-alpha (28 января 2026) — **GAME PROFILES**
- ✅ **Новинка**: Система игровых профилей
- ✅ Автоматическое обнаружение 8 популярных игр
- ✅ RAM cleanup перед запуском (EmptyWorkingSet)
- ✅ Управление приоритетом процессов
- ✅ Автоматическое переключение Power Plans
- ✅ Частичная интеграция GPU overclocking (MSI Afterburner)
- ✅ JSON-based профили (легко редактировать)
- ✅ Callbacks при запуске/закрытии игр
- 📄 Обновлена документация

### v0.2.0-alpha (28 января 2026)
- ✅ Добавлен реальный мониторинг GPU/CPU/RAM
- ✅ Автообновление данных каждые 2 секунды
- ✅ Hotspot temperature для GPU
- ✅ XMP detection через WMI
- ✅ Прогресс-бары для GPU/RAM
- ✅ Улучшенный Steam-inspired UI
- ✅ Launcher `launch.bat` для упрощенной установки
- ✅ Поддержка Python 3.14
- 🐛 Исправлены ошибки парсинга QSS

### v0.1.0-alpha (27 января 2026)
- ✅ Базовый UI с заглушками
- ✅ AI Optimizer (симуляция)
- ✅ Структура проекта

---

## 📞 Контакты

**PartMart** (Samara, Russia)
- 🌐 Avito: [PartMart](https://avito.ru/user/partmart)
- 💬 Issues: [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)
- 📧 Support: создай issue с тегом `help`

---

## ⭐ Поддержи проект

Если PartMart Boost помог тебе — оставь ⭐ на GitHub!

**Благодарности:**
- NVIDIA NVML SDK
- PyQt6 community
- Steam (design inspiration)
- MSI Afterburner team

---

**🚀 Твой ПК. Твоя мощь.**

*PartMart Boost — real-time PC optimization with intelligent game profiles*
