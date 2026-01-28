# 🎨 PartMart Boost UI System

**Version:** 0.3.5c  
**Framework:** PyQt6  
**Philosophy:** Native, Performant, Beautiful

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Theme System](#theme-system)
4. [Components](#components)
5. [Animations](#animations)
6. [Utilities](#utilities)
7. [Layouts](#layouts)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

---

## 🌟 Overview

PartMart UI System - это **собственная UI библиотека** для PartMart Boost, созданная на базе PyQt6.

### Преимущества:
- ✅ **Native** - нет зависимости от веб-технологий
- ✅ **Fast** - hardware-accelerated animations
- ✅ **Beautiful** - современный дизайн
- ✅ **Themeable** - легко менять темы
- ✅ **Reusable** - компоненты можно переиспользовать

### Architecture:
```
ui/
├── theme.py           # Theme system
├── animations.py      # Animation utilities
├── utils.py           # Helper functions
├── layouts.py         # Custom layouts
└── components/        # Reusable components
    ├── animated_button.py
    ├── card.py
    ├── progress_ring.py
    └── status_indicator.py
```

---

## 🚀 Quick Start

### 1. Basic Usage

```python
from ui.theme import get_theme
from ui.components import AnimatedButton, MetricCard

# Get theme
theme = get_theme()

# Create button
button = AnimatedButton("Optimize", "⚡")
button.clicked.connect(lambda: print("Clicked!"))

# Create metric card
card = MetricCard("GPU Temperature", "🌡️")
card.set_value("65°C")
card.set_subtitle("RTX 4090")
```

### 2. Apply Theme to Window

```python
from PyQt6.QtWidgets import QMainWindow
from ui.theme import get_theme

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        theme = get_theme()
        self.setStyleSheet(theme.get_stylesheet('main_window'))
```

---

## 🎨 Theme System

### Using Themes

```python
from ui.theme import get_theme, set_theme_mode, ThemeMode

# Get global theme instance
theme = get_theme()

# Access colors
colors = theme.colors
print(colors.primary)        # "#E63946"
print(colors.bg_primary)     # "#0D0D0D"
print(colors.text_primary)   # "#FFFFFF"

# Get stylesheet for widget type
style = theme.get_stylesheet('button_primary')
widget.setStyleSheet(style)

# Switch theme
set_theme_mode(ThemeMode.AMOLED)
```

### Available Themes

| Theme | Background | Use Case |
|-------|------------|----------|
| **DARK** | `#0D0D0D` | Default, balanced |
| **AMOLED** | `#000000` | Pure black, OLED screens |
| **LIGHT** | `#FFFFFF` | Coming soon |

### Color Scheme

```python
from ui.theme import get_theme

colors = get_theme().colors

# Primary
colors.primary          # Main brand color
colors.primary_hover    # Hover state
colors.primary_light    # Lighter variant
colors.primary_dark     # Darker variant

# Backgrounds
colors.bg_primary       # Main background
colors.bg_secondary     # Secondary surfaces
colors.bg_tertiary      # Tertiary surfaces
colors.bg_card          # Card backgrounds

# Text
colors.text_primary     # Main text
colors.text_secondary   # Secondary text
colors.text_tertiary    # Tertiary text
colors.text_disabled    # Disabled text

# Borders
colors.border_primary   # Default borders
colors.border_secondary # Secondary borders
colors.border_focus     # Focus/active state

# Status
colors.success          # Success state
colors.warning          # Warning state
colors.error            # Error state
colors.info             # Info state
```

### Creating Custom Stylesheets

```python
from ui.theme import get_theme

theme = get_theme()
c = theme.colors

custom_style = f"""
    QWidget {{
        background: {c.bg_primary};
        color: {c.text_primary};
    }}
    QPushButton {{
        background: {c.primary};
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background: {c.primary_hover};
    }}
"""

widget.setStyleSheet(custom_style)
```

---

## 🔸 Components

### AnimatedButton

**Кнопка с плавными анимациями**

```python
from ui.components import AnimatedButton

# Basic
button = AnimatedButton("Click Me", "🚀")

# With loading state
button.set_loading(True)  # Shows "⏳ Loading..."

# Change icon
button.set_icon("✅")

# Connect signal
button.clicked.connect(on_click)
```

**Features:**
- ✅ Smooth hover animations
- ✅ Loading state
- ✅ Icon support
- ✅ Auto cursor change

---

### IconButton

**Круглая кнопка с иконкой**

```python
from ui.components import IconButton

button = IconButton("⚙️", tooltip="Settings")
button.clicked.connect(open_settings)
```

---

### Card

**Базовая карточка с тенью**

```python
from ui.components import Card
from PyQt6.QtWidgets import QVBoxLayout, QLabel

card = Card()
layout = QVBoxLayout()

title = QLabel("Title")
content = QLabel("Content")

layout.addWidget(title)
layout.addWidget(content)
card.setLayout(layout)
```

**Features:**
- ✅ Animated shadow on hover
- ✅ Smooth elevation changes
- ✅ Themed automatically

---

### MetricCard

**Карточка для метрик**

```python
from ui.components import MetricCard

card = MetricCard("GPU Temperature", "🌡️")
card.set_value("65°C")
card.set_subtitle("RTX 4090")

# Update dynamically
card.set_value("70°C")
```

**Structure:**
```
┌──────────────────────┐
│ 🌡️ GPU Temperature  │ <- Title
│                      │
│       65°C           │ <- Value (large)
│                      │
│    RTX 4090          │ <- Subtitle
└──────────────────────┘
```

---

### ProgressRing

**Круговой прогресс-индикатор**

```python
from ui.components import ProgressRing

ring = ProgressRing(size=120)
ring.set_value(75, animate=True)

# Without animation
ring.set_value(50, animate=False)
```

**Features:**
- ✅ Smooth animations
- ✅ Gradient colors
- ✅ Customizable size

---

### StatusIndicator

**Цветной индикатор статуса**

```python
from ui.components import StatusIndicator, StatusType

# Create indicator
indicator = StatusIndicator(StatusType.SUCCESS)

# Change status
indicator.set_status(StatusType.ACTIVE, pulse=True)

# Available statuses
StatusType.SUCCESS   # Green
StatusType.WARNING   # Yellow
StatusType.ERROR     # Red
StatusType.INFO      # Blue
StatusType.IDLE      # Gray
StatusType.ACTIVE    # Primary color
```

**Features:**
- ✅ 6 status types
- ✅ Pulsing animation
- ✅ Color-coded

---

## 🎥 Animations

### Animation Presets

```python
from ui.animations import AnimationPresets

# Fade in
anim = AnimationPresets.fade_in(widget, duration=300)
anim.start()

# Fade out
anim = AnimationPresets.fade_out(widget)
anim.finished.connect(widget.hide)
anim.start()

# Slide in
anim = AnimationPresets.slide_in(widget, direction="left")
anim.start()

# Bounce
anim = AnimationPresets.bounce(widget)
anim.start()
```

### Animation Chains

**Sequential (one after another):**
```python
from ui.animations import AnimationChain

chain = AnimationChain()
chain.add_sequential([anim1, anim2, anim3])
chain.start()
```

**Parallel (all at once):**
```python
chain = AnimationChain()
chain.add_parallel([anim1, anim2, anim3])
chain.start()
```

**Mixed:**
```python
chain = AnimationChain()
chain.add_parallel([fade_in, slide_in])  # Fade + slide together
chain.add_pause(500)                     # Wait 500ms
chain.add_sequential([anim1, anim2])     # Then one by one
chain.start()
```

### Easing Curves

```python
from ui.animations import EasingCurves
from PyQt6.QtCore import QPropertyAnimation

anim = QPropertyAnimation(widget, b"pos")
anim.setEasingCurve(EasingCurves.SMOOTH)    # Natural
anim.setEasingCurve(EasingCurves.ELASTIC)   # Bouncy
anim.setEasingCurve(EasingCurves.BACK)      # Overshoot
anim.setEasingCurve(EasingCurves.SHARP)     # Quick
```

---

## 🛠️ Utilities

### Formatters

```python
from ui.utils import *

# Bytes
format_bytes(1536000000)    # "1.4 GB"
format_bytes(1024)          # "1.0 KB"

# Temperature
format_temperature(65)      # "65°C"
format_temperature(65, 'F') # "149°F"

# Percentage
format_percentage(67.8)     # "67.8%"
format_percentage(67.8, 0)  # "68%"

# Frequency
format_frequency(2400)      # "2.40 GHz"
format_frequency(800)       # "800 MHz"
```

### Effects

```python
from ui.utils import fade_widget, set_opacity, delay_call

# Fade widget
fade_widget(widget, fade_in=True, duration=300)

# Set opacity
set_opacity(widget, 0.5)  # 50% opacity

# Delayed call
delay_call(lambda: print("Hello!"), 1000)  # After 1 second
```

### Timing

```python
from ui.utils import DebounceTimer, ThrottleTimer

# Debounce - wait for user to stop
search_debounce = DebounceTimer(300)

def on_search_input(text):
    search_debounce.call(lambda: perform_search(text))

# Throttle - execute at most once per interval
update_throttle = ThrottleTimer(100)

def on_mouse_move(pos):
    update_throttle.call(lambda: update_ui(pos))
```

### Math

```python
from ui.utils import clamp, lerp

# Clamp value
clamp(150, 0, 100)  # Returns 100
clamp(-10, 0, 100)  # Returns 0

# Linear interpolation
lerp(0, 100, 0.5)   # Returns 50.0
lerp(0, 100, 0.75)  # Returns 75.0
```

---

## 📐 Layouts

### FlowLayout

**Автоматический перенос виджетов на новую строку**

```python
from ui.layouts import FlowLayout
from PyQt6.QtWidgets import QWidget, QPushButton

widget = QWidget()
layout = FlowLayout(spacing=10)

for i in range(20):
    btn = QPushButton(f"Button {i}")
    layout.addWidget(btn)

widget.setLayout(layout)
```

**Result:**
```
[Button 1] [Button 2] [Button 3] [Button 4]
[Button 5] [Button 6] [Button 7]
[Button 8] [Button 9]
```

---

### ResponsiveGrid

**Автоматический расчёт колонок**

```python
from ui.layouts import ResponsiveGrid

# Calculate optimal columns
container_width = 1200
item_width = 250
spacing = 20

cols = ResponsiveGrid.calculate_columns(
    container_width=container_width,
    item_width=item_width,
    spacing=spacing,
    min_cols=1,
    max_cols=4
)
# Returns: 4

# Calculate item size
item_size = ResponsiveGrid.calculate_item_size(
    container_width=1200,
    columns=3,
    spacing=20
)
# Returns: 380
```

---

## ✅ Best Practices

### 1. Always Use Theme

❌ **Bad:**
```python
button.setStyleSheet("background: #E63946;")
```

✅ **Good:**
```python
from ui.theme import get_theme

theme = get_theme()
button.setStyleSheet(f"background: {theme.colors.primary};")
```

---

### 2. Use Components

❌ **Bad:**
```python
button = QPushButton("Click Me")
button.setStyleSheet("""
    QPushButton {
        background: #E63946;
        color: white;
        border-radius: 8px;
        ...
    }
""")
```

✅ **Good:**
```python
from ui.components import AnimatedButton

button = AnimatedButton("Click Me", "🚀")
```

---

### 3. Animate Transitions

❌ **Bad:**
```python
old_widget.hide()
new_widget.show()
```

✅ **Good:**
```python
from ui.animations import AnimationPresets

fade_out = AnimationPresets.fade_out(old_widget)
fade_out.finished.connect(lambda: [
    old_widget.hide(),
    new_widget.show(),
    AnimationPresets.fade_in(new_widget).start()
])
fade_out.start()
```

---

### 4. Use Formatters

❌ **Bad:**
```python
label.setText(f"{bytes_value / 1024 / 1024 / 1024:.1f} GB")
```

✅ **Good:**
```python
from ui.utils import format_bytes

label.setText(format_bytes(bytes_value))
```

---

## 💡 Examples

### Example 1: Metric Dashboard

```python
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from ui.components import MetricCard

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        
        # GPU
        self.gpu_card = MetricCard("GPU Temp", "🌡️")
        self.gpu_card.set_value("65°C")
        self.gpu_card.set_subtitle("RTX 4090")
        layout.addWidget(self.gpu_card)
        
        # RAM
        self.ram_card = MetricCard("RAM Usage", "🧠")
        self.ram_card.set_value("67%")
        self.ram_card.set_subtitle("16.2 / 32.0 GB")
        layout.addWidget(self.ram_card)
        
        # CPU
        self.cpu_card = MetricCard("CPU Load", "💻")
        self.cpu_card.set_value("42%")
        self.cpu_card.set_subtitle("AMD Ryzen 9")
        layout.addWidget(self.cpu_card)
        
        self.setLayout(layout)
```

---

### Example 2: Animated Button Panel

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from ui.components import AnimatedButton
from ui.animations import AnimationPresets

class ButtonPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        
        buttons = [
            ("Optimize", "⚡", self.optimize),
            ("Clean RAM", "🧹", self.clean_ram),
            ("Boost GPU", "🚀", self.boost_gpu),
        ]
        
        for text, icon, callback in buttons:
            btn = AnimatedButton(text, icon)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        self.setLayout(layout)
        
        # Animate in
        for i, btn in enumerate(self.findChildren(AnimatedButton)):
            anim = AnimationPresets.fade_in(btn, duration=300)
            anim.start()
    
    def optimize(self):
        print("Optimizing...")
    
    def clean_ram(self):
        print("Cleaning RAM...")
    
    def boost_gpu(self):
        print("Boosting GPU...")
```

---

### Example 3: Status Panel with Indicators

```python
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from ui.components import StatusIndicator, StatusType

class StatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QHBoxLayout()
        
        statuses = [
            ("System", StatusType.SUCCESS),
            ("GPU", StatusType.ACTIVE),
            ("RAM", StatusType.WARNING),
        ]
        
        for name, status in statuses:
            col = QVBoxLayout()
            
            indicator = StatusIndicator(status)
            if status == StatusType.ACTIVE:
                indicator.set_status(status, pulse=True)
            
            label = QLabel(name)
            label.setStyleSheet("color: white;")
            
            col.addWidget(indicator)
            col.addWidget(label)
            
            layout.addLayout(col)
        
        self.setLayout(layout)
```

---

## 📞 Support

Если нужна помощь:
1. Проверь примеры в этом README
2. Посмотри код компонентов
3. Запусти тесты: `python -m ui.components.card`
4. Создай issue на GitHub

---

**Version:** 0.3.5c  
**Last Updated:** 2026-01-28  
**Maintained by:** PartMart Team
