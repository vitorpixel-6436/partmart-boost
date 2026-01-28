# 📄 Changelog

All notable changes to PartMart Boost will be documented in this file.

---

## [0.3.3-alpha] - 2026-01-28

### ✅ FIXED
- **launcher.bat**: Proper venv-based installation with Python version check
- **CPU cores**: Now shows physical cores instead of threads (4 cores vs 12 threads)
- **Quick Boost error**: Removed PowerShell Clear-RecycleBin (timeout issues)
- **Text visibility**: All labels guaranteed visible with background: transparent
- **Error handling**: Added try-catch blocks throughout codebase

### ✨ ADDED
- **i18n Localization System**:
  - Auto-detects system language (RU/EN)
  - Embedded translations (no external files)
  - Format string support: `t('cpu_cores', count=6)`
  - Easy language switching
- **Launcher improvements**:
  - Automatic venv creation and activation
  - Python 3.14 warning (recommends 3.11/3.12)
  - Better error messages
- **Documentation**:
  - INSTALL.md - Simple installation guide
  - CHANGELOG.md - This file

### 🔧 IMPROVED
- **Reliability**: Graceful error handling in all modules
- **Autonomy**: Works offline after installation
- **Maintainability**: Separated concerns (localization, monitoring, AI)

### 📝 KNOWN ISSUES
- **PyQt6 on Python 3.14**: DLL load errors - use Python 3.12 instead
- **Quick Boost**: Currently only optimizes process priority (RAM cleanup disabled)
- **CPU Temperature**: May not work on all systems (requires LibreHardwareMonitor)

---

## [0.3.2-alpha] - 2026-01-28

### ✨ ADDED
- **Quick Boost Button**: RAM cleanup + process priority optimization
- **Learning AI optimizer**: SQLite-based learning system
  - Records optimization history
  - Learns from your system
  - Provides personalized recommendations
  - Auto-cleanup (max 1000 records, <10MB)
- **Text visibility fixes**: Added repaint() calls for dynamic labels

### 🔧 IMPROVED
- **UI rendering**: Better label visibility with explicit background colors
- **AI recommendations**: Context-aware suggestions based on historical data

---

## [0.3.1-alpha] - 2026-01-28

### ✅ FIXED
- **launcher.bat**: Removed UTF-8 characters causing batch file errors
- **Main page text**: Fixed missing text in metric cards
- **PyQt6 compatibility**: Updated to 6.8.0+ for Python 3.14

### ✨ ADDED
- **Issue #6**: Roadmap for v0.4 stability improvements

---

## [0.3-alpha] - 2026-01-27

### ✨ ADDED
- **Modern card-based UI**: Red PartMart branding
- **Real-time monitoring**:
  - GPU: Temperature (hotspot), clock, load, power, fan
  - CPU: Load, temperature (if available), frequency
  - RAM: Usage, speed, XMP detection
- **Three pages**: Home, GPU Control, RAM Tuner
- **Auto-update**: System metrics every 2 seconds
- **Responsive design**: Minimum 1000x700 window

### 🔧 TECH STACK
- PyQt6 6.8.0+ (UI framework)
- psutil 7.0.0+ (System monitoring)
- nvidia-ml-py 12.560.30+ (NVIDIA GPU)
- wmi 1.5.1+ (Windows Management - RAM speed)

---

## Future Roadmap

### v0.3.4 (Planned: Jan 31)
- AMD GPU support (temperature, load)
- Unit tests (pytest, coverage >40%)
- Integration with localization system in UI

### v0.4.0 (Planned: Feb 2-3)
- **First Stable Release**
- Full code refactoring
- Comprehensive documentation
- PyInstaller .exe build
- GitHub Release with installer

### v0.5.0 (Future)
- CPU overclocking profiles
- RAM XMP auto-enable
- GPU fan curve control
- Game optimization profiles
- Background service mode

---

## Notes

### Python Version Compatibility
- **Recommended**: Python 3.11.x or 3.12.x
- **Works**: Python 3.10+
- **Issues**: Python 3.14 (PyQt6 DLL errors)

### Why Python?
> "Shouldn't you use a faster language?"

Python is ideal for this project because:
1. **Rapid development**: Faster iteration on features
2. **Library ecosystem**: psutil, PyQt6, nvidia-ml-py
3. **Performance is sufficient**: UI updates every 2s, not real-time gaming
4. **Easy maintenance**: Clear, readable code for future contributors
5. **Cross-platform**: Works on Windows/Linux with same codebase

For performance-critical parts (GPU control, overclocking), we can use:
- **C extensions** (Cython)
- **External binaries** (MSI Afterburner integration)
- **Native libraries** (NVAPI, ADL)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)
