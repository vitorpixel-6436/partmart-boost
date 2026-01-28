# 🏗️ PartMart Boost Architecture

## 📦 Project Structure (v0.3.4+)

```
partmart-boost/
├── src/
│   ├── core/
│   │   ├── config.py          # Configuration system (JSON persistence)
│   │   ├── logger.py          # Centralized logging
│   │   └── error_handler.py   # Error handling utilities (future)
│   │
│   ├── monitors/
│   │   ├── __init__.py        # Package exports
│   │   ├── gpu_monitor.py     # NVIDIA GPU monitoring (NVML)
│   │   ├── cpu_monitor.py     # CPU load, temp, frequency
│   │   └── ram_monitor.py     # RAM usage, speed, XMP detection
│   │
│   ├── optimizers/             # (future)
│   │   ├── gpu_optimizer.py   # GPU undervolt, OC
│   │   ├── ram_optimizer.py   # XMP enable, cleanup
│   │   └── ml_optimizer.py    # AI-powered tuning (optional)
│   │
│   ├── ui/
│   │   ├── main_window.py     # Main UI window
│   │   ├── settings_dialog.py # Settings UI (future)
│   │   └── theme.qss          # Styles
│   │
│   ├── localization.py        # i18n system (RU/EN)
│   ├── system_monitor.py      # Legacy (deprecated)
│   ├── ai_optimizer.py        # Legacy AI learning
│   └── main.py                # Entry point
│
├── config/
│   └── settings.json          # User configuration
│
├── logs/
│   └── partmart.log           # Application logs
│
├── launcher.bat               # Windows launcher with venv
├── requirements.txt           # Python dependencies
├── VERSION                    # Current version
├── CHANGELOG.md               # Version history
└── README.md                  # User guide
```

---

## 🧩 Core Components

### 1. Configuration System (`core/config.py`)

**Purpose:** Manage application settings with JSON persistence.

**Features:**
- Auto-detect system language
- User preferences (language, ML toggle, update interval)
- First-launch detection
- Thread-safe configuration updates

**Usage:**
```python
from core.config import get_config

config = get_config()
lang = config.get_language()  # 'ru' or 'en'
config.set_language('ru')
config.enable_ml(True)
```

**Config File** (`config/settings.json`):
```json
{
  "language": "ru",
  "update_interval": 2000,
  "ml_optimizer_enabled": false,
  "theme": "dark",
  "autostart": false
}
```

---

### 2. Logging System (`core/logger.py`)

**Purpose:** Centralized logging to file with rotation.

**Features:**
- Write to `logs/partmart.log`
- Auto-rotation when file > 10MB
- Keep last 5 backups
- Log levels: DEBUG, INFO, WARNING, ERROR
- Startup/shutdown tracking
- Optimization history

**Usage:**
```python
from core.logger import get_logger

logger = get_logger()
logger.log_startup("0.3.4")
logger.info("Application started")
logger.log_optimization("quick_boost", True, "Temp reduced by 4°C")
logger.error("GPU error", exc_info=True)
```

**Log Format:**
```
[2026-01-28 05:38:12] INFO: PartMart Boost 0.3.4 started
[2026-01-28 05:38:12] INFO: [GPU Monitor] GPU detected: NVIDIA GeForce RTX 3060
[2026-01-28 05:38:20] INFO: [RAM Monitor] RAM: DDR4 @ 3200 MHz (XMP: True)
```

---

## 📊 Monitors Package (`monitors/`)

### Design Principles

1. **Modularity:** Each monitor is independent
2. **Graceful Degradation:** Works even if hardware unavailable
3. **Error Handling:** No crashes, only warnings in logs
4. **Type Safety:** Full type hints for all public APIs
5. **Documentation:** Comprehensive docstrings
6. **Testing:** Can be tested standalone

---

### 3. GPU Monitor (`monitors/gpu_monitor.py`)

**Purpose:** Monitor NVIDIA GPU via pynvml.

**Features:**
- Temperature (core + hotspot)
- Clock speeds (GPU core, memory)
- Utilization (GPU, VRAM)
- Power consumption
- Fan speed
- Auto-reinit on NVML errors (max 3 attempts)

**API:**
```python
from monitors import GPUMonitor

gpu = GPUMonitor()

if gpu.is_available():
    print(f"GPU: {gpu.get_name()}")
    
    data = gpu.get_data()
    print(f"Temp: {data['temp_gpu']}°C")
    print(f"Load: {data['load_gpu']}%")
    print(f"Clock: {data['clock_gpu']} MHz")
    print(f"Power: {data['power']:.1f}W")

gpu.cleanup()  # Shutdown NVML
```

**Returns:**
```python
{
    "name": "NVIDIA GeForce RTX 3060",
    "temp_gpu": 52,          # Core temp (°C)
    "temp_hotspot": 65,      # Hotspot (°C) or None
    "clock_gpu": 1785,       # GPU clock (MHz)
    "clock_mem": 8001,       # Memory clock (MHz)
    "load_gpu": 38,          # GPU utilization (%)
    "load_mem": 42,          # VRAM utilization (%)
    "power": 120.5,          # Power draw (W)
    "fan_speed": 45,         # Fan speed (%)
}
```

---

### 4. CPU Monitor (`monitors/cpu_monitor.py`)

**Purpose:** Monitor CPU via psutil.

**Features:**
- CPU utilization
- Temperature (if sensors available)
- Current frequency
- Physical core count (not threads)
- Logical core count (with hyperthreading)
- Cross-platform (Windows/Linux/Mac)

**API:**
```python
from monitors import CPUMonitor

cpu = CPUMonitor()

if cpu.is_available():
    print(f"CPU: {cpu.get_name()}")
    
    data = cpu.get_data()
    print(f"Load: {data['load']}%")
    print(f"Temp: {data['temp']}°C" if data['temp'] else "Temp: N/A")
    print(f"Freq: {data['freq']:.0f} MHz")
    print(f"Cores: {data['count']} (Physical)")
```

**Returns:**
```python
{
    "name": "AMD Ryzen 5 5600X",
    "load": 38.5,            # CPU utilization (%)
    "temp": 52.0,            # Temperature (°C) or None
    "freq": 4200.0,          # Current frequency (MHz)
    "count": 6,              # Physical cores
    "count_logical": 12,     # Logical cores (threads)
}
```

**Temperature Notes:**
- **Windows:** Requires OpenHardwareMonitor, HWiNFO, or CoreTemp running
- **Linux:** Usually works via `sensors`
- **Mac:** Usually works via built-in sensors

---

### 5. RAM Monitor (`monitors/ram_monitor.py`)

**Purpose:** Monitor RAM via psutil + WMI (Windows).

**Features:**
- Memory usage (total, used, free, %)
- Memory speed (MHz) via WMI
- Memory type detection (DDR4, DDR5)
- XMP detection (heuristic-based)
- Detailed stick info (capacity, manufacturer)

**API:**
```python
from monitors import RAMMonitor

ram = RAMMonitor()

if ram.is_available():
    data = ram.get_data()
    print(f"RAM: {data['used']:.1f} / {data['total']:.1f} GB")
    print(f"Usage: {data['percent']:.1f}%")
    print(f"Speed: {data['speed']} MHz ({data['type']})")
    print(f"XMP: {'Enabled' if data['xmp_enabled'] else 'Disabled'}")
    
    # Detailed info (Windows only)
    detailed = ram.get_detailed_info()
    for i, stick in enumerate(detailed['sticks'], 1):
        print(f"Stick {i}: {stick['capacity_gb']}GB @ {stick['speed_mhz']}MHz")
```

**Returns:**
```python
{
    "total": 16.0,           # Total RAM (GB)
    "used": 8.5,             # Used RAM (GB)
    "free": 7.5,             # Available RAM (GB)
    "percent": 53.1,         # Usage (%)
    "speed": 3200,           # RAM speed (MHz)
    "type": "DDR4",          # Memory type
    "xmp_enabled": True,     # XMP status (heuristic)
}
```

**XMP Detection Logic:**
- **DDR5:** JEDEC = 4800 MHz, XMP if > 4800
- **DDR4:** JEDEC = 2133 MHz, XMP if > 2133
- **DDR3:** JEDEC = 1600 MHz, XMP if > 1600

---

## 🔄 Migration Guide

### Old Code (v0.3.3)
```python
from system_monitor import SystemMonitor

monitor = SystemMonitor()
data = monitor.get_all_data()

gpu_temp = data['gpu']['temp_gpu']
cpu_load = data['cpu']['load']
ram_used = data['ram']['used']
```

### New Code (v0.3.4+)
```python
from monitors import GPUMonitor, CPUMonitor, RAMMonitor

gpu = GPUMonitor()
cpu = CPUMonitor()
ram = RAMMonitor()

if gpu.is_available():
    gpu_data = gpu.get_data()
    gpu_temp = gpu_data['temp_gpu']

cpu_data = cpu.get_data()
cpu_load = cpu_data['load']

ram_data = ram.get_data()
ram_used = ram_data['used']
```

**Benefits:**
- ✅ Independent modules (test separately)
- ✅ Graceful degradation (GPU optional)
- ✅ Better error handling
- ✅ Type hints for IDE support
- ✅ Logging integration

---

## 🧪 Testing

### Test Individual Monitors

```bash
# GPU Monitor
python src/monitors/gpu_monitor.py

# CPU Monitor
python src/monitors/cpu_monitor.py

# RAM Monitor
python src/monitors/ram_monitor.py
```

### Test Config
```bash
python src/core/config.py
```

### Test Logger
```bash
python src/core/logger.py
```

---

## 📈 Future Architecture

### v0.4.0 Roadmap

```
src/
├── optimizers/
│   ├── gpu_optimizer.py    # Undervolt, OC, fan curves
│   ├── ram_optimizer.py    # XMP enable, cleanup
│   └── ml_optimizer.py     # AI predictions (sklearn)
│
├── profiles/
│   ├── game_profiles.py    # Per-game optimization
│   └── presets.py          # Pre-defined profiles
│
└── utils/
    ├── stress_test.py      # FurMark integration
    └── benchmark.py        # Performance tracking
```

---

## 🛡️ Error Handling Philosophy

1. **Never crash:** Always return safe defaults
2. **Log everything:** Errors, warnings, info to file
3. **Inform user:** Show friendly messages in UI
4. **Graceful degradation:** Work with partial data
5. **Retry smartly:** Auto-reinit with limits (max 3)

**Example:**
```python
try:
    gpu_temp = gpu.get_temperature()
except GPUError as e:
    logger.error(f"GPU error: {e}")
    gpu_temp = 0  # Safe default
    show_notification("GPU monitoring unavailable")
```

---

## 🔗 Dependencies

- **pynvml** (12.560.30+): NVIDIA GPU control
- **psutil** (7.0.0+): System monitoring
- **PyQt6** (6.8.0+): UI framework
- **wmi** (1.5.1+): Windows hardware info
- **scikit-learn** (1.6.0+): ML models (optional)

---

## 📝 Code Style

- **Type hints:** All public APIs
- **Docstrings:** Google style
- **Line length:** 100 chars
- **Imports:** Absolute from `src/`
- **Logging:** Via `core.logger`
- **Config:** Via `core.config`

---

## 🎯 Design Goals

✅ **Modularity:** Independent components
✅ **Reliability:** Error handling everywhere
✅ **Performance:** Minimal overhead (<1% CPU)
✅ **Maintainability:** Clear code structure
✅ **Testability:** Unit tests for all modules
✅ **Documentation:** Comprehensive guides

---

**Last Updated:** 2026-01-28  
**Version:** 0.3.4-alpha
