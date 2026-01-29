# PartMart Boost

**Version:** 0.3.5d (Package 3.9a, Stage 7.7c COMPLETE)  
**Gaming Performance Optimizer - REAL WORKING PROGRAM**

## 🎮 Overview

PartMart Boost is a gaming performance optimizer that uses **AMD FSR** (FidelityFX Super Resolution) and real-time system monitoring to boost game performance.

**NEW in 7.7c:** REAL monitoring, game detection, and FSR integration - NO STUBS!

## ✨ Features

### 📊 Real Performance Monitoring
- **CPU Monitoring** - Real-time usage and frequency (psutil)
- **GPU Monitoring** - NVIDIA GPU tracking (pynvml)
  - Usage percentage
  - Memory usage
  - Temperature
- **RAM Monitoring** - Memory usage tracking
- **Disk I/O** - Read/write speeds
- **Process Tracking** - System-wide process monitoring

### 🎮 Automatic Game Detection
- **40+ Known Games** - Automatic detection
  - GTA 5, Cyberpunk 2077, Witcher 3
  - Escape from Tarkov, Valorant, CS2
  - Elden Ring, Dark Souls, Sekiro
  - And many more...
- **Custom Games** - Add your own
- **Resource Tracking** - CPU/RAM per game
- **Event Callbacks** - React to game start/stop

### 🚀 FSR Integration
- **AMD FSR 2.x Support** - FidelityFX Super Resolution
- **5 Quality Presets**
  - Ultra Quality (77% render scale)
  - Quality (67% render scale)
  - Balanced (59% render scale)
  - Performance (50% render scale)
  - Ultra Performance (33% render scale)
- **Per-Game Configs** - Save settings per game
- **DLL Management** - Safe DLL handling

### 🔧 DLL Injection (Windows)
- **Safe Injection** - CreateRemoteThread technique
- **Admin Detection** - Automatic privilege check
- **Backup/Restore** - Original DLL backup

### 💾 Historical Data
- **SQLite Storage** - Time-series data
- **Configurable Retention** - 7/30/90/365 days
- **Auto Collection** - Background aggregation
- **Statistics** - Performance trends

### 📈 Visualization
- **Interactive Charts** - Real performance data
- **Health Timeline** - System health over time
- **Error Analysis** - Error tracking
- **Export** - Save charts as images

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- PyQt6 - GUI
- pyqtgraph - Charts
- psutil - System monitoring
- pynvml - NVIDIA GPU monitoring

### Installation

```bash
# Clone repository
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

### First Run

```bash
# Check dependencies
python src/main.py --check

# Run tests
python src/main.py --test

# Launch GUI
python src/main.py

# Console mode
python src/main.py --no-gui
```

## 💻 Usage

### GUI Mode (Default)

```bash
python src/main.py
```

**Main Window:**
- **Status Tab** - Real-time monitoring
  - CPU/GPU/RAM usage
  - Detected games
  - System health
- **History Tab** - Historical data charts
- **Settings Tab** - Configuration

### Monitoring Example

```python
from core.performance_monitor import get_performance_monitor

# Start monitoring
monitor = get_performance_monitor()
monitor.start()

# Get metrics
metrics = monitor.get_current_metrics()
print(f"CPU: {metrics.cpu_percent}%")
print(f"GPU: {metrics.gpu_percent}%")
print(f"RAM: {metrics.ram_percent}%")

monitor.stop()
```

### Game Detection Example

```python
from core.game_detector import get_game_detector

# Start detector
detector = get_game_detector()
detector.start()

# Get detected games
games = detector.get_detected_games()
for game in games:
    print(f"{game.display_name} - CPU: {game.cpu_percent}%")

detector.stop()
```

### FSR Configuration Example

```python
from core.fsr_manager import get_fsr_manager, FSRPreset

# Create FSR config
manager = get_fsr_manager()
config = manager.create_config(
    preset=FSRPreset.QUALITY,  # 67% render scale
    sharpness=0.7
)

# Save for game
manager.save_game_config('GTA5', config)
```

## 🛠️ Configuration

### Settings File

Location: `config/settings.json`

### Key Settings

```json
{
  "monitoring": {
    "check_interval": 5.0,
    "enable_performance_monitoring": true,
    "enable_auto_recovery": true
  },
  "historical_data": {
    "retention_days": 30,
    "collection_interval": 60.0
  }
}
```

## 📊 Current Status

**Package 3.9a Progress:**

```
✅ Stage 7.7b: Infrastructure        (100%) ~10,000 lines
✅ Stage 7.7c: Real Functionality    (100%)  ~1,800 lines
⏳ Stage 7.7d: Game Profiles          (0%)
⏳ Stage 7.7e: Final Polish           (0%)
```

**Total Code:** ~11,800 lines + 142 tests

## ✅ What Works NOW

- ✅ Real CPU monitoring (psutil)
- ✅ Real GPU monitoring (NVIDIA via pynvml)
- ✅ Real RAM monitoring
- ✅ Game detection (40+ games)
- ✅ FSR library management
- ✅ DLL injection (Windows)
- ✅ Historical data storage
- ✅ Interactive charts
- ✅ Configuration system
- ✅ Error recovery
- ✅ Health monitoring

## 🚧 In Progress

- ⏳ Auto FSR injection on game start
- ⏳ Game profile management UI
- ⏳ AMD GPU support
- ⏳ Performance optimization presets

## ⚠️ Important Notes

### DLL Injection Warning

**DLL injection may trigger anti-cheat systems!**

- ✅ Safe for single-player games
- ❌ DO NOT use with multiplayer games
- ❌ May result in bans if detected
- ✅ Always backup game files

### Administrator Required

DLL injection requires administrator privileges on Windows.

### GPU Support

- **NVIDIA:** Full support (pynvml)
- **AMD:** Not yet supported
- **Intel:** Not yet supported

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Stage 7.7c Complete](docs/STAGE_7.7c_COMPLETE.md)

## 🧪 Testing

```bash
# Run all tests
python src/main.py --test

# Run specific stage tests
python tests/test_stage_7.7c.py

# Expected: 142 tests passing
```

## ⚙️ System Requirements

### Minimum
- **OS:** Windows 10+ (DLL injection)
- **Python:** 3.8+
- **RAM:** 512 MB
- **Disk:** 100 MB

### Recommended
- **OS:** Windows 11
- **Python:** 3.10+
- **RAM:** 1 GB
- **GPU:** NVIDIA (for GPU monitoring)

## 🐛 Known Issues

- AMD GPU monitoring not implemented
- Linux/Mac have no DLL injection
- Some games may not be in detection database
- Anti-cheat may detect injection

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 👥 Contributors

- Developer: vitorpixel-6436
- AI Assistant: Claude (Anthropic)

## 🚀 Roadmap

### Stage 7.7d (Next)
- Game profile system
- Auto FSR injection
- Profile management UI

### Stage 7.7e (Final)
- End-to-end testing
- Performance optimization
- Bug fixes
- Documentation polish

### Future (Stage 7.8+)
- AMD GPU support
- Linux support
- Cloud profiles
- Multi-language support

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vitorpixel-6436/partmart-boost/discussions)

---

**Made with ❤️ for gamers**

**Version 0.3.5d - REAL WORKING PROGRAM!** 🎮🚀
