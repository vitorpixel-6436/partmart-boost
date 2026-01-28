# 📦 Installation Guide

## Quick Install (Recommended)

### Windows

1. **Clone repository:**
```bash
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost
```

2. **Run launcher:**
```bash
launcher.bat
```

That's it! The launcher will:
- Check Python version (3.10+ required, 3.11-3.12 recommended)
- Create virtual environment
- Install dependencies
- Launch the application

---

## Manual Installation

### Requirements

- **Python 3.11 or 3.12** (recommended)
  - Python 3.10+ works
  - Python 3.14 may have PyQt6 DLL issues
- **Windows 10/11** (primary support)
- **NVIDIA GPU** (for GPU monitoring)
- **10MB disk space** + dependencies

### Step-by-Step

1. **Install Python:**
   - Download from https://www.python.org/downloads/
   - **Important:** Check "Add Python to PATH" during installation

2. **Clone repository:**
```bash
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost
```

3. **Create virtual environment:**
```bash
python -m venv venv
```

4. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

5. **Install dependencies:**
```bash
pip install -r requirements.txt
```

6. **Run application:**
```bash
python src/main.py
```

---

## Troubleshooting

### PyQt6 DLL Error (Python 3.14)

**Error:** `ImportError: DLL load failed while importing QtCore`

**Solution:** Use Python 3.11 or 3.12:
```bash
# Uninstall Python 3.14
# Install Python 3.12 from python.org
# Re-run launcher.bat
```

### GPU Not Detected

**Symptoms:** GPU metrics show "N/A"

**Solutions:**
1. **Update NVIDIA drivers:**
   - Visit https://nvidia.com/drivers
   - Install latest driver
   - Restart PC

2. **Check CUDA:**
```bash
nvidia-smi
```

If command fails, NVIDIA drivers are not installed.

### CPU Temperature Not Available

**Symptom:** CPU temp shows "--"

**Why:** Windows doesn't expose CPU temperature via standard APIs.

**Solutions:**
1. **Install OpenHardwareMonitor:**
   - Download from https://openhardwaremonitor.org/
   - Run as Administrator
   - Keep running in background

2. **Or just ignore:** CPU load is still tracked.

### RAM Speed Shows Wrong Value

**Symptom:** RAM speed shows 2133MHz instead of actual XMP speed.

**Solution:** Enable XMP in BIOS:
1. Restart PC
2. Enter BIOS (usually Del, F2, or F12)
3. Find "XMP" or "DOCP" setting
4. Enable XMP Profile 1
5. Save and exit

### Application Won't Start

**Check Python version:**
```bash
python --version
```
Should be 3.10+

**Check dependencies:**
```bash
pip list
```
Should include PyQt6, psutil, nvidia-ml-py

**View logs:**
```bash
type logs\partmart.log
```

---

## Advanced Options

### ML Optimizer (Beta)

Enable machine learning optimization:

1. Open **Settings** (menu bar)
2. Check **"Enable AI-powered optimization"**
3. Click **Save**

**Requirements:**
- `scikit-learn` package (auto-installed)
- 50MB free RAM
- Works 100% offline

**What it does:**
- Learns optimal GPU clock/voltage from your usage
- Predicts safe overclocking values
- Adapts to your specific hardware

### Config File

Manually edit `config/settings.json`:

```json
{
  "language": "ru",              // auto, en, ru
  "update_interval": 2000,       // milliseconds
  "ml_optimizer_enabled": true,  // true/false
  "log_level": "INFO"            // DEBUG, INFO, WARNING, ERROR
}
```

### Logs

Logs stored in `logs/partmart.log`

**View recent logs:**
```bash
# Windows
type logs\partmart.log | more

# Linux/Mac
tail -f logs/partmart.log
```

**Log rotation:**
- Automatic when file >10MB
- Keeps last 5 backups
- Old logs: `logs/partmart_YYYYMMDD_HHMMSS.log`

---

## Uninstall

1. Delete project folder:
```bash
rmdir /s /q partmart-boost
```

2. (Optional) Remove Python:
   - Windows Settings → Apps → Python → Uninstall

---

## System Requirements

### Minimum
- Windows 10 (64-bit)
- Python 3.10+
- 4GB RAM
- 100MB disk space
- Any GPU (NVIDIA recommended)

### Recommended
- Windows 11 (64-bit)
- Python 3.11 or 3.12
- 8GB+ RAM
- 500MB disk space
- NVIDIA RTX GPU

### Tested Configurations

✅ Windows 11 + Python 3.12 + RTX 3060  
✅ Windows 10 + Python 3.11 + GTX 1660  
✅ Windows 11 + Python 3.10 + RTX 2060 Super  
⚠️ Windows 11 + Python 3.14 + RTX 3060 (PyQt6 issues)  

---

## Building Executable (Coming Soon)

**v0.4.0 will include:**
- Standalone `.exe` file
- No Python installation needed
- NSIS installer
- Auto-updates

For now, use `launcher.bat` method.

---

## Getting Help

- **Issues:** https://github.com/vitorpixel-6436/partmart-boost/issues
- **Docs:** https://github.com/vitorpixel-6436/partmart-boost
- **Logs:** Check `logs/partmart.log` first

---

## License

MIT License - see [LICENSE](LICENSE)
