# Installation Guide

**Version:** 0.3.5d+patch6

## Quick Install

### Windows

```bash
# Download
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Install full dependencies
pip install -r requirements.txt

# Launch
launcher_simple.bat
```

### Linux/macOS

```bash
# Download
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Install full dependencies
pip install -r requirements.txt

# Launch GUI
python src/main.py

# Or CLI
python src/main_cli.py
```

## Detailed Installation

### Prerequisites

- **Python:** 3.8 or higher (tested up to 3.15)
- **pip:** Latest version recommended
- **Git:** For cloning repository

### Check Python Version

```bash
python --version
# Should show: Python 3.8.x or higher
```

### Install Options

#### Option 1: Full Install (Recommended)

Includes all features:
- System monitoring
- GPU detection
- Temperature sensors
- Frame processing
- Complete GUI

```bash
pip install -r requirements.txt
```

**Total size:** ~500 MB  
**Install time:** 2-5 minutes  
**Packages:** 57 (including dependencies)

#### Option 2: Minimal Install

Basic functionality only:
- GUI framework
- Core systems
- Limited monitoring

```bash
pip install -r requirements-minimal.txt
```

**Total size:** ~100 MB  
**Install time:** 30-60 seconds  
**Packages:** 10

**Note:** Many features won't work!

#### Option 3: Development Install

For developers:
- All production dependencies
- Testing frameworks
- Code quality tools
- Profiling tools

```bash
pip install -r requirements-dev.txt
```

**Total size:** ~800 MB  
**Packages:** 80+

### Virtual Environment (Recommended)

#### Windows

```bash
# Create venv
python -m venv venv

# Activate
venv\Scripts\activate

# Install
pip install -r requirements.txt
```

#### Linux/macOS

```bash
# Create venv
python -m venv venv

# Activate
source venv/bin/activate

# Install
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check all imports
python -c "import numpy, PyQt6, psutil, GPUtil, cv2, PIL; print('All OK!')"

# Run tests
python tests/test_all_modules.py

# Launch GUI
python src/main.py
```

## Troubleshooting

### Issue: pip install fails

**Solution 1:** Update pip
```bash
python -m pip install --upgrade pip
```

**Solution 2:** Install with --user
```bash
pip install --user -r requirements.txt
```

**Solution 3:** Use system Python
```bash
python3 -m pip install -r requirements.txt
```

### Issue: PyQt6 installation fails

**Windows:**
```bash
# Install Visual C++ Redistributable first
# Download from Microsoft

pip install PyQt6
```

**Linux:**
```bash
# Install system dependencies
sudo apt install python3-pyqt6  # Debian/Ubuntu
sudo dnf install python3-qt6    # Fedora

pip install PyQt6
```

**macOS:**
```bash
# Install via Homebrew
brew install pyqt6

pip install PyQt6
```

### Issue: opencv-python fails

```bash
# Install system libraries first

# Linux
sudo apt install libgl1-mesa-glx libglib2.0-0

# Then install opencv
pip install opencv-python
```

### Issue: wmi fails (Windows)

```bash
# Install with dependencies
pip install wmi pywin32
```

### Issue: numba fails (Python 3.12+)

```bash
# Skip numba - it's optional
pip install -r requirements.txt --no-deps
pip install numpy scipy PyQt6 psutil GPUtil opencv-python Pillow
```

### Issue: Permission denied

```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use venv (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Platform-Specific Notes

### Windows

- **wmi** package installed automatically for system monitoring
- **pywin32** may be required for some features
- Antivirus might slow down installation

### Linux

- System packages may be needed:
  ```bash
  sudo apt install python3-dev python3-pip
  sudo apt install libgl1-mesa-glx libglib2.0-0
  ```

- GPU monitoring requires proper drivers:
  ```bash
  # NVIDIA
  nvidia-smi  # Should work
  
  # AMD
  # Limited support currently
  ```

### macOS

- Xcode Command Line Tools required:
  ```bash
  xcode-select --install
  ```

- Some features may be limited:
  - GPU monitoring (limited)
  - Temperature sensors (limited)

## Dependency List

### Core (Required)

- **numpy** - Array operations
- **scipy** - Scientific computing
- **PyQt6** - GUI framework

### Monitoring (Required)

- **psutil** - System monitoring
- **GPUtil** - GPU detection
- **py-cpuinfo** - CPU information
- **screeninfo** - Monitor information
- **wmi** - Windows monitoring (Windows only)

### Processing (Required)

- **Pillow** - Image processing
- **opencv-python** - Computer vision

### Utilities (Required)

- **typing-extensions** - Type hints
- **colorama** - Colored output
- **pyyaml** - Config files
- **jsonschema** - Validation

### Optional

- **numba** - JIT compilation (Python < 3.12)
- **joblib** - Parallel processing
- **requests** - HTTP requests

## Updating

### Update PartMart Boost

```bash
git pull
pip install --upgrade -r requirements.txt
```

### Update Single Package

```bash
pip install --upgrade numpy
pip install --upgrade PyQt6
```

### Update All Packages

```bash
pip install --upgrade -r requirements.txt
```

## Uninstalling

### Remove PartMart Boost

```bash
# If using venv
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# If installed globally
pip uninstall -r requirements.txt -y
```

### Clean Install

```bash
# Remove all
pip uninstall -r requirements.txt -y

# Reinstall
pip install -r requirements.txt
```

## Getting Help

- **Installation issues:** [Open an issue](https://github.com/vitorpixel-6436/partmart-boost/issues)
- **General help:** Check README.md
- **Development:** See docs/DEVELOPMENT.md

---

**Ready to go?** Run:
```bash
python src/main.py
```
