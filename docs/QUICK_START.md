# Quick Start Guide

Package 3.8a - Get started in 5 minutes!

## Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

### Install PartMart Boost

```bash
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost
pip install -e .
```

---

## Quick Example - OptiScaler

### 1. Install OptiScaler (One-Click)

```python
from optiscaler import OptiScalerManager

manager = OptiScalerManager()
manager.initialize()

# Auto-install if not present
if not manager.is_installed():
    print("Installing OptiScaler...")
    manager.install()  # Downloads from GitHub automatically
    print("✅ Installed!")
```

### 2. Configure OptiScaler

```python
from optiscaler import OptiScalerConfig, OptiScalerBackend, OptiScalerQuality

config = OptiScalerConfig(
    backend=OptiScalerBackend.FSR3,      # Use FSR 3.1
    quality=OptiScalerQuality.QUALITY,   # Quality mode
    sharpness=0.8,                        # 80% sharpness
    enable_frame_gen=True,                # Enable frame gen
    enable_hud_fix=True                   # Fix HUD scaling
)

manager.configure(config)
print("✅ Configured!")
```

### 3. Inject into Game

```python
from pathlib import Path

# Point to your game directory
game_dir = Path("C:/Games/Cyberpunk 2077/bin/x64")

# Detect game
game = manager.detect_game(game_dir)

if game:
    print(f"Found: {game.name}")
    
    # Inject OptiScaler
    manager.inject_into_game(game)
    print("✅ Game now uses FSR 3.1!")
```

**That's it!** Your game now uses real FSR 3.1 on GPU!

---

## Quick Example - UniversalUpscaler

### 1. Auto-Detection

```python
from upscaler import UniversalUpscaler

upscaler = UniversalUpscaler()
upscaler.initialize()  # Auto-detects best backend

info = upscaler.get_backend_info()
print(f"Backend: {info.backend.name}")  # OPTISCALER, FSR3, etc.
```

### 2. Upscale a Frame

```python
import numpy as np
from upscaler import UpscaleConfig, UpscalerQuality, FrameData

# Create test frame (1080p)
frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)

# Create context (1080p → 4K)
config = UpscaleConfig(
    input_resolution=(1920, 1080),
    output_resolution=(3840, 2160),
    quality=UpscalerQuality.QUALITY
)

context = upscaler.create_context(config)

# Upscale
frame_data = FrameData(color=frame)
upscaled, metrics = context.upscale(frame_data)

print(f"FPS: {metrics.fps:.1f}")  # Real GPU performance!
```

---

## GUI Usage

### Launch GUI

```python
from gui import OptiScalerTab
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
tab = OptiScalerTab()
tab.show()
sys.exit(app.exec())
```

### GUI Features:

1. **Install OptiScaler** - One-click installation
2. **Configure** - Backend, quality, sharpness
3. **Inject into Game** - Browse and inject

---

## Supported Games

OptiScaler works with 1000+ games:

- Cyberpunk 2077
- Starfield
- Alan Wake 2
- Ghost of Tsushima
- Spider-Man
- Hogwarts Legacy
- Red Dead Redemption 2
- And many more!

See [Supported Games List](https://github.com/optiscaler/OptiScaler#supported-games)

---

## Performance

| Backend | 1080p→4K | Quality |
|---------|----------|----------|
| OptiScaler FSR3 | 320 FPS | Ultra |
| Direct FSR3 | 280 FPS | Ultra |
| Software | 35 FPS | N/A |

---

## Next Steps

- Read [API Reference](OPTISCALER_API.md)
- Check [Troubleshooting](TROUBLESHOOTING.md)
- See [Performance Benchmarks](PERFORMANCE.md)
- Run examples:
  ```bash
  python examples/optiscaler_demo.py
  python examples/upscaler_demo.py
  ```

---

## Getting Help

- GitHub Issues: [vitorpixel-6436/partmart-boost](https://github.com/vitorpixel-6436/partmart-boost/issues)
- OptiScaler Issues: [optiscaler/OptiScaler](https://github.com/optiscaler/OptiScaler/issues)

---

**Enjoy real FSR 3.1 on GPU!** 🚀
