# 📂 Development Guide - PartMart Boost

## Quick Start for Developers

### Prerequisites
- Python 3.11+
- Windows 10 build 19043+ or Windows 11
- Administrator privileges (for GPU/RAM control)
- Git

### Setup Environment

```bash
# Clone repository
git clone https://github.com/vitorpixel-6436/partmart-boost.git
cd partmart-boost

# Create virtual environment
python -m venv venv

# Activate venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac (for WSL)

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (optional)
pip install pytest pytest-cov pylint black ipython

# Run application
python src/main.py
```

### Run Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_gpu_nvidia.py -v

# Run specific test
pytest tests/test_gpu_nvidia.py::test_nvidia_detection -v

# Check code quality
pylint src/
black --check src/
```

## Git Workflow

### Feature Development

```bash
# 1. Update dev branch
git checkout dev
git pull origin dev

# 2. Create feature branch
git checkout -b feature/my-feature-name

# 3. Write code + tests
# ... implement feature ...
# ... write unit tests ...

# 4. Run tests locally
pytest tests/ -v --cov=src

# 5. Format code
black src/ tests/

# 6. Commit (atomic, descriptive)
git add src/module/my_feature.py tests/test_my_feature.py
git commit -m "feat(module): add my feature

- Implemented X functionality
- Added comprehensive tests (95% coverage)
- Maintains backward compatibility

Closes #123"

# 7. Push branch
git push origin feature/my-feature-name

# 8. Create Pull Request on GitHub (to dev branch)
# ... fill PR template ...
# ... wait for CI/CD to pass ...

# 9. After merge, delete branch
git checkout dev
git pull origin dev
git branch -d feature/my-feature-name
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `test`: Test addition/modification
- `docs`: Documentation
- `chore`: Build, CI/CD, dependencies
- `perf`: Performance improvement

**Scope**: Module name (gpu, ram, ui, optimizer, partmart)

**Examples**:
```
feat(gpu): add NVIDIA undervolt control
feat(ram): implement XMP auto-enable
fix(optimizer): handle stability test timeout
refactor(ui): simplify main window layout
test(gpu): add nvidia detection tests
docs: update GPU optimization guide
```

## Code Structure

```
src/
├─ main.py              # Entry point
├─ ui/                  # PyQt6 UI components
├─ gpu/                 # GPU optimization
├─ ram/                 # RAM optimization
├─ optimizer/           # Optimization logic
├─ framegen/            # FrameGen integration
├─ partmart/            # PartMart integration
├─ monitor/             # Performance monitoring
├─ telemetry/           # Analytics
├─ updater/             # Auto-updater
├─ utils/               # Utilities
└─ inject/              # Game injection

tests/
├─ test_gpu_nvidia.py
├─ test_ram_xmp.py
└─ test_stability.py
```

## Testing Guidelines

### Test Coverage
- Minimum 80% code coverage required
- All public methods must have tests
- Critical paths (GPU control, RAM OC) need comprehensive testing

### Test Structure

```python
import pytest
from src.gpu.nvidia_control import NVIDIAControl

class TestNVIDIAControl:
    """Test NVIDIA GPU control"""
    
    @pytest.fixture
    def nvidia(self):
        """Setup NVIDIA control instance"""
        return NVIDIAControl()
    
    def test_gpu_detection(self, nvidia):
        """Test GPU detection"""
        assert nvidia.available == True
        assert nvidia.gpu_name is not None
    
    def test_undervolt_valid_range(self, nvidia):
        """Test undervolt with valid range"""
        result = nvidia.apply_undervolt(-100)
        assert result == True
    
    def test_undervolt_invalid_range(self, nvidia):
        """Test undervolt with invalid range"""
        with pytest.raises(ValueError):
            nvidia.apply_undervolt(-200)  # Out of range
    
    def test_revert_settings(self, nvidia):
        """Test reverting to stock settings"""
        nvidia.apply_undervolt(-100)
        nvidia.revert_all()
        assert nvidia.current_voltage == nvidia.original_voltage
```

## Code Quality

### Pylint
```bash
pylint src/
# Target: score > 8.0
```

### Black Formatting
```bash
black src/ tests/
```

### Type Hints
Use type hints for better code clarity:

```python
from typing import Dict, Optional, List

def apply_undervolt(self, offset_mv: int) -> bool:
    """Apply GPU undervolt
    
    Args:
        offset_mv: Voltage offset in millivolts (-50 to -150)
    
    Returns:
        True if successful, False otherwise
    """
    pass
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Interactive Python

```bash
ipython

from src.gpu.nvidia_control import NVIDIAControl
nvidia = NVIDIAControl()
print(nvidia.get_info())
```

## Build & Release

### Build .exe (PyInstaller)

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico src/main.py
# Output: dist/main.exe
```

### Create Release

```bash
# Tag commit
git tag v0.1-mvp
git push origin v0.1-mvp

# GitHub Actions automatically:
# 1. Runs tests
# 2. Builds .exe
# 3. Creates GitHub Release
# 4. Uploads .exe to Release
```

## Performance Guidelines

### GPU Control
- Undervolt: Conservative default (-50mV), max safe (-150mV)
- Memory OC: Conservative default (+200MHz), max safe (+500MHz)
- **Always include stability test (FurMark 30s) before applying**

### RAM Optimization
- XMP: Safe (no stability risk from manufacturer profile)
- Timing tweaks: Requires stability test
- **Auto-revert on system crash**

### UI Responsiveness
- GPU/RAM control in background threads
- Never block UI for >500ms
- Use QThread for long operations

## Documentation

### Code Comments
- Focus on "why", not "what"
- Document complex logic
- Example:

```python
# GOOD: Explains why
if offset_mv < -50:
    # Conservative default prevents damage on first run
    offset_mv = -50

# BAD: Just repeats code
if offset_mv < -50:  # if offset is less than -50
    offset_mv = -50  # set it to -50
```

### Docstrings

```python
def apply_undervolt(self, offset_mv: int) -> bool:
    """Apply GPU undervolt with safety checks.
    
    Applies voltage offset to GPU core with conservative limits.
    Always performs stability test before applying to production.
    
    Args:
        offset_mv: Voltage offset in millivolts.
            Range: -50 to -150 (safe)
            Default: -100 (recommended)
    
    Returns:
        True if undervolt applied and stable, False otherwise.
    
    Raises:
        ValueError: If offset outside safe range
        RuntimeError: If GPU not accessible
    
    Example:
        >>> nvidia = NVIDIAControl()
        >>> nvidia.apply_undervolt(-100)
        True
        >>> nvidia.get_info()['voltage']
        -100
    """
```

## Security & Safety

### Critical Rules
1. ✅ **All tweaks reversible** - Revert button available
2. ✅ **Stability test mandatory** - 30sec FurMark before apply
3. ✅ **Temperature protection** - Auto-revert if >85°C
4. ✅ **Conservative defaults** - Start safe, users can increase
5. ✅ **Crash detection** - Auto-revert on 2x game crashes
6. ✅ **No malware** - No hidden mining, spyware, or crypto
7. ✅ **Privacy** - Optional opt-in telemetry only

## Support

- 💫 Issues: https://github.com/vitorpixel-6436/partmart-boost/issues
- 💭 Discussions: https://github.com/vitorpixel-6436/partmart-boost/discussions
- 📇 Wiki: https://github.com/vitorpixel-6436/partmart-boost/wiki (coming soon)

## Resources

- [NVIDIA NVML Documentation](https://docs.nvidia.com/deploy/nvml-api/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [pynvml Python Package](https://github.com/gpuci/pynvml)
- [PartMart - PC Builder (Avito)](https://avito.ru/user/partmart)

---

**Questions?** Open a GitHub issue or discussion! 📚
