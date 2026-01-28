# 🎨 PartMart Boost v0.3.5c - UI Foundation

**Release Date:** January 28, 2026  
**Type:** Major UI Framework Update  
**Focus:** Frontend Infrastructure

---

## 📋 OVERVIEW

**v0.3.5c** — Серьёзное обновление "под капот" frontend!

Это **фундамент** для постепенного перехода от сторонних решений к **собственной UI системе** без использования веб-приложений.

### Новые возможности:
- ✅ **Система тем** - централизованное управление стилями
- ✅ **Custom компоненты** - анимированные кнопки, карточки, индикаторы
- ✅ **Анимации** - плавные переходы и эффекты
- ✅ **UI утилиты** - formатирование, debounce, throttle
- ✅ **Custom layouts** - FlowLayout, ResponsiveGrid

---

## ✨ NEW FEATURES

### 1. 🎨 Theme System (`ui/theme.py`)

**Централизованное управление цветами и стилями**

```python
from ui.theme import get_theme, ThemeMode

# Get current theme
theme = get_theme()
colors = theme.colors

# Use colors
background = colors.bg_primary  # "#0D0D0D"
primary = colors.primary  # "#E63946"

# Get stylesheet for widget
style = theme.get_stylesheet('button_primary')

# Switch theme
theme.switch_mode(ThemeMode.AMOLED)
```

**Available themes:**
- `DARK` - Основная тёмная тема (по умолчанию)
- `AMOLED` - Чисто чёрная тема
- `LIGHT` - Светлая тема (для будущего)

**Color scheme includes:**
- Primary colors (4 variants)
- Background colors (4 levels)
- Text colors (4 levels)
- Border colors (3 types)
- Status colors (success, warning, error, info)
- Special (shadow, overlay)

---

### 2. 🔘 Custom Components (`ui/components/`)

#### AnimatedButton
```python
from ui.components import AnimatedButton

btn = AnimatedButton("Оптимизировать", "⚡")
btn.clicked.connect(lambda: print("Clicked!"))

# Loading state
btn.set_loading(True)
```

**Features:**
- Smooth hover animations
- Loading state support
- Icon support
- Automatic cursor change

#### MetricCard
```python
from ui.components import MetricCard

card = MetricCard("GPU Temperature", "🌡️")
card.set_value("65°C")
card.set_subtitle("RTX 4090")
```

**Features:**
- Animated shadow on hover
- Smooth elevation changes
- Consistent styling

#### ProgressRing
```python
from ui.components import ProgressRing

ring = ProgressRing(size=120)
ring.set_value(75, animate=True)  # Animated to 75%
```

**Features:**
- Circular progress indicator
- Gradient colors
- Smooth animations

#### StatusIndicator
```python
from ui.components import StatusIndicator, StatusType

indicator = StatusIndicator(StatusType.SUCCESS)
indicator.set_status(StatusType.ACTIVE, pulse=True)
```

**Features:**
- Color-coded statuses
- Pulsing animation
- 6 status types

---

### 3. 🎥 Animation System (`ui/animations.py`)

**Presets:**
```python
from ui.animations import AnimationPresets

# Fade in
anim = AnimationPresets.fade_in(widget, duration=300)
anim.start()

# Slide in
anim = AnimationPresets.slide_in(widget, direction="left")
anim.start()

# Bounce
anim = AnimationPresets.bounce(widget)
anim.start()
```

**Animation Chain:**
```python
from ui.animations import AnimationChain

chain = AnimationChain()
chain.add_sequential([anim1, anim2])
chain.add_pause(500)
chain.add_parallel([anim3, anim4])
chain.start()
```

**Easing curves:**
- `SMOOTH` - Natural easing
- `ELASTIC` - Elastic bounce
- `BOUNCE` - Bouncy effect
- `BACK` - Overshoot
- `SHARP` - Quick transition

---

### 4. 🛠️ UI Utilities (`ui/utils.py`)

**Formatters:**
```python
from ui.utils import *

format_bytes(1536000000)  # "1.4 GB"
format_temperature(65)     # "65°C"
format_percentage(67.8)    # "67.8%"
format_frequency(2400)     # "2.40 GHz"
```

**Effects:**
```python
fade_widget(widget, fade_in=True, duration=300)
set_opacity(widget, 0.5)
delay_call(callback, 1000)  # Call after 1 second
```

**Timing utilities:**
```python
# Debounce - wait for user to stop typing
debounce = DebounceTimer(300)
debounce.call(lambda: print("Search!"))

# Throttle - execute at most once per interval
throttle = ThrottleTimer(300)
throttle.call(lambda: update_ui())
```

---

### 5. 📏 Custom Layouts (`ui/layouts.py`)

#### FlowLayout
**Автоматический перенос виджетов на новую строку**

```python
from ui.layouts import FlowLayout

layout = FlowLayout(spacing=10)
for i in range(20):
    btn = QPushButton(f"Button {i}")
    layout.addWidget(btn)
```

#### ResponsiveGrid
**Автоматический расчёт колонок**

```python
from ui.layouts import ResponsiveGrid

cols = ResponsiveGrid.calculate_columns(
    container_width=1200,
    item_width=250,
    spacing=20
)
# Returns: 4 (optimal columns)
```

---

## 📊 ARCHITECTURE

### 🏛️ Structure

```
src/ui/
├── theme.py              # Theme system
├── animations.py         # Animation utilities
├── utils.py              # UI utilities
├── layouts.py            # Custom layouts
└── components/
    ├── __init__.py
    ├── animated_button.py
    ├── card.py
    ├── progress_ring.py
    └── status_indicator.py
```

### 📦 Separation of Concerns

```
┌─────────────────────────────┐
│   Application Logic        │
│  (main_window.py, etc)     │
└───────────┬────────────────┘
           │
    ┌──────┴──────┐
    │  Components  │
    │   (reusable) │
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │    Theme     │
    │  (styling)  │
    └─────────────┘
```

---

## 🔧 TECHNICAL DETAILS

### Theme System
- **Type-safe** color scheme with dataclasses
- **Hot-swappable** themes (no restart required)
- **Centralized** stylesheet generation
- **Consistent** colors across entire app

### Components
- **PyQt6-native** - no web dependencies
- **Animated** - smooth transitions
- **Themeable** - automatically adapt to theme
- **Reusable** - drop-in replacements

### Animations
- **Property-based** - any Qt property can be animated
- **Chainable** - sequential and parallel support
- **Performance-optimized** - hardware accelerated

---

## 🚀 MIGRATION GUIDE

### Before (v0.3.5b_hotfix):
```python
button = QPushButton("Оптимизировать")
button.setStyleSheet("""
    QPushButton {
        background: #E63946;
        color: white;
        ...
    }
""")
```

### After (v0.3.5c):
```python
from ui.components import AnimatedButton

button = AnimatedButton("Оптимизировать", "⚡")
# Styling automatic from theme!
```

---

## 🎯 BENEFITS

### 🚀 Performance
- **Native Qt** - нет overhead от веб-движков
- **Hardware accelerated** - GPU ускорение анимаций
- **Optimized** - минимальное потребление RAM

### 🛠️ Maintainability
- **DRY** - не повторяем стили
- **Centralized** - одно место для темы
- **Reusable** - компоненты можно переиспользовать

### 🎨 Flexibility
- **Easy theming** - смена темы за 1 строку
- **Custom components** - легко создавать новые
- **Extensible** - просто добавлять функции

---

## 📝 EXAMPLES

### Creating a themed card
```python
from ui.components import Card
from PyQt6.QtWidgets import QVBoxLayout, QLabel

card = Card()
layout = QVBoxLayout()

title = QLabel("🔥 Status")
value = QLabel("Active")

layout.addWidget(title)
layout.addWidget(value)
card.setLayout(layout)
```

### Animated transition
```python
from ui.animations import AnimationPresets

# Fade out old widget
fade_out = AnimationPresets.fade_out(old_widget)
fade_out.finished.connect(old_widget.hide)
fade_out.start()

# Fade in new widget
fade_in = AnimationPresets.fade_in(new_widget)
new_widget.show()
fade_in.start()
```

---

## 🔮 ROADMAP (v0.3.6+)

### Planned Components
- [ ] `Toast` - Уведомления
- [ ] `Modal` - Модальные окна
- [ ] `Slider` - Ползунок с анимацией
- [ ] `TabBar` - Анимированные вкладки
- [ ] `Tooltip` - Кастомные подсказки

### Planned Features
- [ ] Theme editor UI
- [ ] Animation timing debugger
- [ ] Component showcase/demo
- [ ] Accessibility improvements

---

## 📊 STATISTICS

| Metric | Value |
|--------|-------|
| **New Files** | 9 |
| **New Components** | 4 |
| **Total LOC** | ~1200 |
| **Themes** | 3 |
| **Animation Presets** | 5 |
| **Easing Curves** | 7 |

---

## ❗ BREAKING CHANGES

**None!** 🎉

v0.3.5c полностью **обратно совместима** с v0.3.5b_hotfix.

Старый код продолжит работать, новые компоненты - это **дополнение**.

---

## 👥 CREDITS

**Architecture:** PartMart Team  
**Design System:** Modern PyQt6 patterns  
**Inspiration:** Material Design, Fluent UI

---

## 📞 USAGE

### Quick Start
```python
# 1. Import theme
from ui.theme import get_theme

# 2. Import components
from ui.components import AnimatedButton, MetricCard

# 3. Use!
button = AnimatedButton("🚀 Launch", "🚀")
card = MetricCard("GPU Temp", "🌡️")
```

---

**Version:** 0.3.5c  
**Build Date:** 2026-01-28  
**Status:** ✅ Stable  
**Type:** Foundation Release
