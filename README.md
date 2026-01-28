# 🐉 PartMart Boost v0.2-alpha

**Игровой оптимизатор ПК с РЕАЛЬНЫМ мониторингом системы**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078d4)](https://www.microsoft.com/windows)
![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange)

---

## 🆕 Что нового в v0.2-alpha (28 января 2026)

### ✅ РЕАЛЬНЫЙ мониторинг системы
- **GPU**: температура (core + hotspot), частоты, загрузка, питание через `pynvml`
- **CPU**: загрузка, температура, частота через `psutil`
- **RAM**: использование, скорость, автоопределение XMP статуса через WMI
- **Автообновление**: данные обновляются каждые 2 секунды

### ✅ Улучшенный UI
- Дизайн в стиле Steam Big Picture
- Sidebar 280px с голубыми акцентами (#66c0f4)
- Прогресс-бары для GPU/RAM загрузки
- Плавные градиенты и улучшенная типографика

### ✅ Упрощенная установка
- **`launch.bat`** — запуск в 1 клик (автоустановка зависимостей)
- Больше не нужно вручную устанавливать pip/requirements

### ⚠️ Что еще в разработке
- GPU Optimizer (undervolt, OC) — Coming Soon
- RAM XMP Enable — Coming Soon
- FrameGen (FSR 3, DLSS 3) — Coming Soon
- Game Profiles — Coming Soon

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

### Способ 2: Ручная установка

```bash
# 1. Установить Python 3.11+ с https://python.org

# 2. Скачать проект
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить
python src/main.py
```

### Требования:
- **Python**: 3.11+ (3.14 поддерживается)
- **ОС**: Windows 10 (build 19043+) или Windows 11
- **RAM**: 2GB+
- **GPU**: NVIDIA (рекомендуется), AMD, Intel Arc

---

## 🎮 Что это?

**PartMart Boost** — desktop приложение для покупателей ПК от [PartMart](https://avito.ru/user/partmart) (Samara). 

### Текущие возможности (v0.2-alpha):
- ✅ Реальное отображение температур GPU/CPU
- ✅ Мониторинг загрузки GPU и RAM в реальном времени
- ✅ Автоопределение XMP статуса памяти
- ✅ Steam-inspired интерфейс
- ✅ Автообновление данных каждые 2 секунды

### Планируется (v0.5-beta):
- ⏳ GPU Optimizer (undervolt, memory OC)
- ⏳ RAM XMP Enable
- ⏳ Quick Boost (1-click оптимизация)
- ⏳ FrameGen (FSR 3, DLSS 3)
- ⏳ Game Profiles
- ⏳ RTSS Overlay

---

## 🖼️ Интерфейс

### Главная страница
```
┌─────────────────────────────────────────────────────┐
│ 🐉 PartMart Boost v0.2                               │
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
│  │ ⚡ БЫСТРЫЙ БУСТ                                 │ │
│  │ GPU Optimize + RAM Cleanup + System Tweaks     │ │
│  │                                                │ │
│  │ 📈 Ожидаемый прирост: +30-50 FPS               │ │
│  │                                                │ │
│  │  🚀 ЗАПУСТИТЬ ОПТИМИЗАЦИЮ                      │ │
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
│ 🎮  FRAMEGEN     │
│ 🎯  ИГРЫ         │
│ ⚙️  НАСТРОЙКИ    │
├──────────────────┤
│   v0.2.0-alpha   │
└──────────────────┘
```

---

## ⚙️ Технический стек

### Мониторинг
- **pynvml** (13.0.1+) — NVIDIA GPU мониторинг
- **psutil** (7.2.1+) — CPU/RAM мониторинг
- **wmi** (1.5.1+) — XMP detection

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
├─ VERSION                         # Версия (0.2.0-alpha)
├─ src/
│  ├─ main.py                      # Entry point
│  ├─ system_monitor.py            # 🆕 Реальный мониторинг
│  ├─ ai_optimizer.py              # AI рекомендации
│  ├─ ui/
│  │  ├─ main_window.py            # 🆕 Главное окно с автообновлением
│  │  ├─ ai_widget.py              # AI insights widget
│  │  └─ theme.qss                 # Steam-inspired theme
│  └─ gpu/
│     ├─ nvidia_control.py         # NVIDIA (pynvml)
│     └─ amd_control.py            # AMD (симуляция)
├─ requirements.txt                # Зависимости
└─ README.md                       # Это файл
```

---

## 🔧 Устранение проблем

### Ошибка "Could not parse stylesheet"
✅ **Исправлено в v0.2** — убраны некорректные CSS свойства из QSS

### Статичные данные (температура не меняется)
✅ **Исправлено в v0.2** — реальное чтение через pynvml/psutil + QTimer

### Неверная температура GPU (+18°C разница)
✅ **Исправлено в v0.2** — теперь используется hotspot temperature (если доступна)

### XMP статус неверный
✅ **Исправлено в v0.2** — реальное чтение через WMI (ConfiguredClockSpeed)

### Python 3.14 не поддерживается
✅ **Исправлено** — обновлены зависимости (PyQt6 6.10+, PyInstaller 6.15+)

---

## 🛡️ Безопасность

### Текущая версия (v0.2-alpha)
- ✅ **Только чтение** — никаких изменений системы
- ✅ **Безопасный мониторинг** — стандартные API (pynvml, psutil)
- ✅ **Без прав администратора** — для базового мониторинга

### Будущие версии (v0.5+)
- ⏳ **Права админа** — для GPU/RAM оптимизации
- ⏳ **Auto-revert** — откат при крашах
- ⏳ **Stability test** — перед применением твиков

---

## 🗓️ Дорожная карта

| Версия | Статус | Фичи |
|--------|--------|------|
| **v0.2-alpha** | ✅ **ТЕКУЩАЯ** | Реальный мониторинг, Steam UI, launch.bat |
| **v0.3-alpha** | 🔄 В разработке | GPU Optimizer (NVIDIA), RAM XMP Enable |
| **v0.5-beta** | 📅 Февраль 2026 | AMD GPU, FrameGen (FSR 3), Game profiles |
| **v1.0-release** | 📅 Март 2026 | Premium tier, NSIS installer, Code signing |

---

## 🐛 Известные проблемы

- ⚠️ **CPU температура**: не работает без OpenHardwareMonitor/HWiNFO
- ⚠️ **AMD GPU**: пока только симуляция (реальный контроль в v0.3)
- ⚠️ **Quick Boost**: UI есть, функционал в разработке

**Отчеты о багах**: [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)

---

## 📝 Changelog

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

---

**🚀 Твой ПК. Твоя мощь.**

*PartMart Boost — real-time PC optimization*
