# PartMart Boost

**Version:** 0.3.5g (Package 3.9a, Stage 7.7b.9.1)  
**Gaming Performance Optimizer - USER READY**

## 🎮 Overview

PartMart Boost is a comprehensive gaming performance optimization tool with real-time monitoring, automatic error recovery, and advanced visualization capabilities.

## ✨ Features

### 📊 Core Monitoring
- **Real-time System Monitoring** - CPU, memory, disk, network tracking
- **Game Detection** - Automatic game process detection
- **Performance Analysis** - Detailed performance metrics
- **Health Status** - Component health tracking

### 🔄 Error Recovery
- **Automatic Error Detection** - Real-time error monitoring
- **Smart Recovery** - Automatic recovery strategies
- **Recovery History** - Track all recovery operations
- **Configurable Thresholds** - Customize recovery behavior

### 💾 Historical Data
- **Time-Series Storage** - SQLite-based data storage
- **Configurable Retention** - 7/30/90/365 days or unlimited
- **Automatic Collection** - Background data aggregation
- **Statistics** - Success rates, error counts, trends

### 📈 Visualization
- **Interactive Charts** - Line, bar, and pie charts
- **Health Timeline** - Visual health status over time
- **Error Rate Analysis** - Error distribution charts
- **Recovery Success** - Recovery operation statistics
- **Component Comparison** - Compare component performance

### ⚙️ Configuration
- **Centralized Settings** - JSON-based configuration
- **Customizable Intervals** - Adjust monitoring frequency
- **UI Preferences** - Theme, window size, notifications
- **Save/Load** - Persistent configuration

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Required packages
pip install PyQt6 pyqtgraph
```

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

**Main Window Features:**
- **Status Tab** - Real-time system status and monitoring
- **History Tab** - Historical data with interactive charts
- **Settings Tab** - Application configuration

### Console Mode

```bash
python src/main.py --no-gui
```

Runs monitoring systems without GUI. Useful for servers or headless environments.

### Command-Line Options

```bash
python src/main.py --help     # Show help
python src/main.py --version  # Show version
python src/main.py --check    # Check dependencies
python src/main.py --test     # Run tests
python src/main.py --no-gui   # Console mode
```

## 📖 Documentation

### User Guides
- [User Guide](docs/USER_GUIDE.md) - Complete user documentation
- [Quick Start](docs/QUICK_START.md) - Get started quickly
- [FAQ](docs/FAQ.md) - Frequently asked questions

### Technical Documentation
- [System Architecture](docs/ARCHITECTURE.md) - System design
- [API Documentation](docs/API.md) - Developer API
- [Configuration Guide](docs/CONFIGURATION.md) - Settings reference

### Component Documentation
- [Error Reporting](docs/ERROR_REPORTING.md) - Error reporter system
- [System Health](docs/SYSTEM_HEALTH.md) - Health monitoring
- [Recovery System](docs/RECOVERY_SYSTEM.md) - Auto-recovery
- [Historical Data](docs/HISTORICAL_DATA.md) - Data storage
- [Charts & Visualization](docs/CHARTS_VISUALIZATION.md) - Charting system

## 🛠️ Development

### Project Structure

```
partmart-boost/
├── src/
│   ├── core/                  # Core systems
│   │   ├── error_reporter.py
│   │   ├── system_health_monitor.py
│   │   ├── recovery_coordinator.py
│   │   ├── historical_data_store.py
│   │   ├── data_aggregator.py
│   │   ├── config_manager.py
│   │   └── system_integrator_final.py
│   ├── ui/                    # User interface
│   │   ├── widgets/
│   │   │   ├── monitoring_panel.py
│   │   │   ├── chart_widget.py
│   │   │   └── historical_data_viewer.py
│   │   └── main_window_complete.py
│   └── main.py               # Entry point
├── tests/                   # Test suite
├── docs/                    # Documentation
├── config/                  # Configuration
└── data/                    # Data storage
```

### Running Tests

```bash
# Run all tests
python src/main.py --test

# Run specific test file
python -m unittest tests/test_config_manager.py

# Run with coverage
pip install coverage
coverage run -m unittest discover tests
coverage report
```

### Building

```bash
# Create standalone executable
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

## 📈 Current Status

**Package 3.9a Progress:**

```
✅ Stage 7.7b.1-5: Core monitoring systems (100%)
✅ Stage 7.7b.6: Error recovery system (100%)
✅ Stage 7.7b.7: GUI monitoring integration (100%)
✅ Stage 7.7b.8: Advanced features (100%)
   ✅ 7.7b.8.1: Historical data system
   ✅ 7.7b.8.2: Charts & visualization
🔄 Stage 7.7b.9: Finalization (25%)
   ✅ 7.7b.9.1: Final integration
   ⏳ 7.7b.9.2: Complete documentation
   ⏳ 7.7b.9.3: Final testing
   ⏳ 7.7b.9.4: Package release
```

## ✅ System Requirements

### Minimum
- **OS:** Windows 10, Linux, macOS
- **Python:** 3.8+
- **RAM:** 512 MB
- **Disk:** 100 MB

### Recommended
- **OS:** Windows 11, Recent Linux/macOS
- **Python:** 3.10+
- **RAM:** 1 GB
- **Disk:** 500 MB

## 🐛 Known Issues

- PyQtGraph performance may degrade with >10,000 data points
- System tray icons not implemented yet
- Some chart export formats may not work on all platforms

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 👥 Contributors

- Developer: vitorpixel-6436
- AI Assistant: Claude (Anthropic)

## 🚀 Roadmap

### Stage 7.8 (Next)
- Advanced optimization features
- Game profiles
- Performance presets
- Network optimization

### Future
- Cloud sync
- Multi-language support
- Plugin system
- Mobile companion app

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vitorpixel-6436/partmart-boost/discussions)

---

**Made with ❤️ for gamers**
