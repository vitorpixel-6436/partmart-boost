# OptiScaler API Reference

Package 3.8a - Complete API documentation

## Table of Contents

- [OptiScalerManager](#optiscalermanager)
- [OptiScalerConfig](#optiscalerconfig)
- [Types and Enums](#types-and-enums)
- [Examples](#examples)

---

## OptiScalerManager

Main API for managing OptiScaler installation and configuration.

### Constructor

```python
OptiScalerManager(install_dir: Optional[Path] = None)
```

**Parameters:**
- `install_dir`: Installation directory (default: `./optiscaler`)

### Methods

#### `initialize() -> bool`

Initialize OptiScaler manager and detect installation.

**Returns:** `True` if OptiScaler is installed and ready

**Example:**
```python
manager = OptiScalerManager()
if manager.initialize():
    print("OptiScaler ready!")
```

---

#### `is_installed() -> bool`

Check if OptiScaler is installed.

**Returns:** `True` if installed

---

#### `install(force: bool = False, progress_callback: Optional[Callable] = None) -> bool`

Install or update OptiScaler.

**Parameters:**
- `force`: Force reinstall even if already installed
- `progress_callback`: Progress callback `(status: str, percent: int)`

**Returns:** `True` if successful

**Example:**
```python
def progress(status, percent):
    print(f"[{percent}%] {status}")

manager.install(progress_callback=progress)
```

---

#### `configure(config: OptiScalerConfig) -> bool`

Configure OptiScaler settings.

**Parameters:**
- `config`: OptiScalerConfig instance

**Returns:** `True` if successful

**Example:**
```python
config = OptiScalerConfig(
    backend=OptiScalerBackend.FSR3,
    quality=OptiScalerQuality.QUALITY
)
manager.configure(config)
```

---

#### `inject_into_game(game: GameInfo) -> bool`

Inject OptiScaler into game.

**Parameters:**
- `game`: GameInfo instance from `detect_game()`

**Returns:** `True` if successful

**Example:**
```python
game = manager.detect_game(Path("C:/Games/Cyberpunk2077"))
if game:
    manager.inject_into_game(game)
```

---

#### `detect_game(game_dir: Path) -> Optional[GameInfo]`

Detect game and its upscaler support.

**Parameters:**
- `game_dir`: Game installation directory

**Returns:** `GameInfo` or `None`

**Example:**
```python
game = manager.detect_game(Path("C:/Games/Cyberpunk2077"))
if game:
    print(f"Game: {game.name}")
    print(f"DLSS: {game.has_dlss}")
```

---

#### `get_info() -> Optional[OptiScalerInfo]`

Get OptiScaler installation information.

**Returns:** `OptiScalerInfo` or `None`

**Example:**
```python
info = manager.get_info()
if info:
    print(f"Version: {info.version}")
    print(f"Backends: {info.backends_available}")
```

---

## OptiScalerConfig

Configuration for OptiScaler.

### Constructor

```python
OptiScalerConfig(
    backend: OptiScalerBackend = OptiScalerBackend.AUTO,
    quality: OptiScalerQuality = OptiScalerQuality.QUALITY,
    sharpness: float = 0.5,
    enable_frame_gen: bool = False,
    enable_hud_fix: bool = True,
    enable_overlay: bool = False,
    output_scaling: float = 1.0,
    mip_bias: float = 0.0
)
```

**Parameters:**
- `backend`: Upscaling backend (FSR3/XeSS/DLSS/AUTO)
- `quality`: Quality mode (PERFORMANCE/BALANCED/QUALITY/ULTRA_QUALITY)
- `sharpness`: Sharpness level (0.0-1.0)
- `enable_frame_gen`: Enable frame generation
- `enable_hud_fix`: Enable HUD position fix
- `enable_overlay`: Enable performance overlay
- `output_scaling`: Output scaling factor
- `mip_bias`: Mipmap bias adjustment

### Methods

#### `save(path: Path) -> bool`

Save configuration to file.

#### `load(path: Path) -> Optional[OptiScalerConfig]`

Load configuration from file.

---

## Types and Enums

### OptiScalerBackend

```python
class OptiScalerBackend(IntEnum):
    FSR3 = 0   # AMD FSR 3.1
    XESS = 1   # Intel XeSS 2.1
    DLSS = 2   # NVIDIA DLSS
    AUTO = 3   # Auto-select
```

### OptiScalerQuality

```python
class OptiScalerQuality(IntEnum):
    PERFORMANCE = 0      # 2.0x scale
    BALANCED = 1         # 1.7x scale
    QUALITY = 2          # 1.5x scale (recommended)
    ULTRA_QUALITY = 3    # 1.3x scale
    NATIVE = 4           # 1.0x scale
```

### GameInfo

```python
@dataclass
class GameInfo:
    name: str
    exe_path: Path
    game_dir: Path
    process_id: Optional[int]
    has_dlss: bool
    has_fsr: bool
    has_xess: bool
```

---

## Examples

### Complete Workflow

```python
from optiscaler import (
    OptiScalerManager,
    OptiScalerConfig,
    OptiScalerBackend,
    OptiScalerQuality
)
from pathlib import Path

# 1. Initialize manager
manager = OptiScalerManager()
manager.initialize()

# 2. Install if needed
if not manager.is_installed():
    def progress(status, percent):
        print(f"[{percent}%] {status}")
    
    manager.install(progress_callback=progress)

# 3. Configure
config = OptiScalerConfig(
    backend=OptiScalerBackend.FSR3,
    quality=OptiScalerQuality.ULTRA_QUALITY,
    sharpness=0.8,
    enable_frame_gen=True,
    enable_hud_fix=True
)

manager.configure(config)

# 4. Detect game
game_dir = Path("C:/Games/Cyberpunk 2077/bin/x64")
game = manager.detect_game(game_dir)

if game:
    print(f"Detected: {game.name}")
    print(f"Supports DLSS: {game.has_dlss}")
    
    # 5. Inject OptiScaler
    if manager.inject_into_game(game):
        print("✅ OptiScaler injected!")
        print("Game now uses FSR 3.1!")
```

### Error Handling

```python
from optiscaler import (
    OptiScalerManager,
    InstallationError,
    InjectionError
)

try:
    manager = OptiScalerManager()
    manager.initialize()
    
    if not manager.is_installed():
        manager.install()
    
    game = manager.detect_game(game_dir)
    if game:
        manager.inject_into_game(game)

except InstallationError as e:
    print(f"Installation failed: {e}")
except InjectionError as e:
    print(f"Injection failed: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Performance Benchmarks](PERFORMANCE.md)
