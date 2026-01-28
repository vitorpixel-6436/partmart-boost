# 🚀 Migration Guide: UI → DataBus

## 🎯 Overview

This guide helps you migrate existing UI code from direct monitor access to the new DataBus architecture.

**Before (OLD):**
```python
# UI directly calls monitors
self.gpu_monitor = GPUMonitor()
self.timer = QTimer()
self.timer.timeout.connect(self.update_ui)

def update_ui(self):
    data = self.gpu_monitor.get_data()  # Direct call
    self.update_widgets(data)
```

**After (NEW):**
```python
# UI subscribes to DataBus
from core.databus import get_databus

self.databus = get_databus()
self.databus.gpu_updated.connect(self.on_gpu_update)

def on_gpu_update(self, data):
    self.update_widgets(data)  # Event-driven
```

---

## 🛠️ Step-by-Step Migration

### Step 1: Remove Direct Monitor Imports

**OLD CODE:**
```python
# ❌ Remove these
from monitors.gpu_monitor import GPUMonitor
from monitors.cpu_monitor import CPUMonitor
from monitors.ram_monitor import RAMMonitor
import psutil
import pynvml
```

**NEW CODE:**
```python
# ✅ Add this
from core.databus import get_databus
```

---

### Step 2: Replace Monitor Initialization

**OLD CODE:**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ❌ Remove these
        self.gpu_monitor = GPUMonitor()
        self.cpu_monitor = CPUMonitor()
        self.ram_monitor = RAMMonitor()
        
        # ❌ Remove timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_data)
        self.timer.start(2000)
```

**NEW CODE:**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ✅ Get global DataBus (already started in main.py)
        self.databus = get_databus()
        
        # ✅ Subscribe to updates
        self.databus.data_updated.connect(self.on_data_update)
        # OR subscribe to specific monitors:
        # self.databus.gpu_updated.connect(self.on_gpu_update)
        # self.databus.cpu_updated.connect(self.on_cpu_update)
        # self.databus.ram_updated.connect(self.on_ram_update)
```

---

### Step 3: Replace Update Methods

**OLD CODE:**
```python
def update_all_data(self):
    """Timer callback - polls all monitors"""
    try:
        # ❌ Multiple blocking calls
        gpu_data = self.gpu_monitor.get_data()
        cpu_data = self.cpu_monitor.get_data()
        ram_data = self.ram_monitor.get_data()
        
        # Update UI
        self.update_gpu_ui(gpu_data)
        self.update_cpu_ui(cpu_data)
        self.update_ram_ui(ram_data)
    except Exception as e:
        print(f"Update failed: {e}")
```

**NEW CODE (Option A - All Data):**
```python
def on_data_update(self, data: dict):
    """DataBus signal callback - receives all data"""
    # ✅ Data already collected and cached
    gpu_data = data['gpu']
    cpu_data = data['cpu']
    ram_data = data['ram']
    
    # Update UI
    self.update_gpu_ui(gpu_data)
    self.update_cpu_ui(cpu_data)
    self.update_ram_ui(ram_data)
```

**NEW CODE (Option B - Specific Monitors):**
```python
def on_gpu_update(self, gpu_data: dict):
    """GPU-specific callback"""
    self.update_gpu_ui(gpu_data)

def on_cpu_update(self, cpu_data: dict):
    """CPU-specific callback"""
    self.update_cpu_ui(cpu_data)

def on_ram_update(self, ram_data: dict):
    """RAM-specific callback"""
    self.update_ram_ui(ram_data)
```

---

### Step 4: Handle Synchronous Access (Optional)

If you need immediate data access (e.g., on button click):

**OLD CODE:**
```python
def on_button_click(self):
    # ❌ Direct monitor call
    data = self.gpu_monitor.get_data()
    self.show_popup(data)
```

**NEW CODE:**
```python
def on_button_click(self):
    # ✅ Get cached data from DataBus
    data = self.databus.get_gpu_data()  # Instant, from cache
    self.show_popup(data)
    
    # OR force fresh update:
    # self.databus.force_update()  # Triggers immediate poll
    # data = self.databus.get_gpu_data()
```

---

### Step 5: Update Error Handling

**OLD CODE:**
```python
try:
    data = self.gpu_monitor.get_data()
except Exception as e:
    self.show_error(f"GPU error: {e}")
```

**NEW CODE:**
```python
# ✅ Subscribe to error signal
self.databus.error_occurred.connect(self.on_error)

def on_error(self, error_message: str):
    self.show_error(error_message)
```

---

## 📄 Complete Example: Before & After

### Before (OLD)

```python
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import QTimer
from monitors.gpu_monitor import GPUMonitor
import psutil

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Direct monitor access
        self.gpu_monitor = GPUMonitor()
        
        # UI elements
        self.gpu_temp_label = QLabel()
        self.cpu_label = QLabel()
        
        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(2000)
    
    def update_all(self):
        """Update all metrics"""
        try:
            # Blocking calls
            gpu_data = self.gpu_monitor.get_data()
            cpu_load = psutil.cpu_percent(interval=0.1)
            
            # Update UI
            self.gpu_temp_label.setText(f"{gpu_data.get('temp_gpu', 0)}°C")
            self.cpu_label.setText(f"{cpu_load:.1f}%")
        except Exception as e:
            print(f"Error: {e}")
    
    def on_quick_boost_click(self):
        """Quick boost button"""
        # Direct access for immediate data
        gpu_temp = self.gpu_monitor.get_data()['temp_gpu']
        if gpu_temp > 80:
            self.show_warning("GPU too hot!")
```

### After (NEW)

```python
from PyQt6.QtWidgets import QMainWindow, QLabel
from core.databus import get_databus

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Get DataBus (singleton)
        self.databus = get_databus()
        
        # UI elements
        self.gpu_temp_label = QLabel()
        self.cpu_label = QLabel()
        
        # Subscribe to updates (event-driven)
        self.databus.data_updated.connect(self.on_data_update)
        self.databus.error_occurred.connect(self.on_error)
    
    def on_data_update(self, data: dict):
        """Event-driven update"""
        # Data already collected by DataBus
        gpu_data = data['gpu']
        cpu_data = data['cpu']
        
        # Update UI (fast, no blocking)
        self.gpu_temp_label.setText(f"{gpu_data.get('temp_gpu', 0)}°C")
        self.cpu_label.setText(f"{cpu_data.get('load', 0):.1f}%")
    
    def on_error(self, error: str):
        """Error handling"""
        print(f"DataBus error: {error}")
    
    def on_quick_boost_click(self):
        """Quick boost button"""
        # Get cached data (instant)
        gpu_data = self.databus.get_gpu_data()
        gpu_temp = gpu_data.get('temp_gpu', 0)
        
        if gpu_temp > 80:
            self.show_warning("GPU too hot!")
```

---

## 💡 Best Practices

### ✅ DO:

1. **Subscribe to signals for reactive UI:**
   ```python
   self.databus.gpu_updated.connect(self.on_gpu_update)
   ```

2. **Use cached data for button clicks:**
   ```python
   data = self.databus.get_gpu_data()  # Fast!
   ```

3. **Let DataBus handle polling:**
   ```python
   # No need for QTimer in UI
   # DataBus polls automatically
   ```

4. **Handle errors via signals:**
   ```python
   self.databus.error_occurred.connect(self.on_error)
   ```

### ❌ DON'T:

1. **Don't import monitors directly in UI:**
   ```python
   # ❌ NEVER do this in UI code
   from monitors.gpu_monitor import GPUMonitor
   monitor = GPUMonitor()
   ```

2. **Don't create your own polling timer:**
   ```python
   # ❌ DataBus already does this
   timer = QTimer()
   timer.timeout.connect(self.update)
   ```

3. **Don't call psutil/pynvml directly:**
   ```python
   # ❌ Backend responsibility
   import psutil
   cpu = psutil.cpu_percent()
   ```

4. **Don't start/stop DataBus from UI:**
   ```python
   # ❌ main.py handles this
   self.databus.start()  # Don't do this
   ```

---

## 🚀 Migration Checklist

- [ ] Remove direct monitor imports
- [ ] Remove `import psutil`, `import pynvml`, etc.
- [ ] Replace monitor initialization with `get_databus()`
- [ ] Remove QTimer for polling
- [ ] Replace `update_all()` methods with signal callbacks
- [ ] Subscribe to `data_updated` or specific signals
- [ ] Replace direct `get_data()` calls with `databus.get_*_data()`
- [ ] Add error signal handler
- [ ] Test UI reactivity
- [ ] Verify performance improvement

---

## 📊 DataBus API Reference

### Signals

```python
data_updated = pyqtSignal(dict)   # All system data
gpu_updated = pyqtSignal(dict)    # GPU metrics only
cpu_updated = pyqtSignal(dict)    # CPU metrics only
ram_updated = pyqtSignal(dict)    # RAM metrics only
error_occurred = pyqtSignal(str)  # Error messages
```

### Methods

```python
# Get cached data (synchronous, fast)
get_data() -> dict               # All data
get_gpu_data() -> dict           # GPU only
get_cpu_data() -> dict           # CPU only
get_ram_data() -> dict           # RAM only

# Control
start()                          # Start polling (main.py only)
stop()                           # Stop polling
set_update_interval(ms: int)     # Change interval
force_update()                   # Force immediate poll

# Performance
get_performance_stats() -> dict  # Get DataBus stats
```

### Data Structure

```python
{
    'gpu': {
        'temp_gpu': float,       # °C
        'temp_hotspot': float,   # °C
        'clock_gpu': int,        # MHz
        'load_gpu': int,         # %
        'power': float,          # W
        'fan_speed': int,        # %
    },
    'cpu': {
        'load': float,           # %
        'temp': float,           # °C (or None)
        'freq': float,           # MHz
        'count': int,            # Physical cores
        'count_logical': int,    # Threads
    },
    'ram': {
        'total': float,          # GB
        'used': float,           # GB
        'free': float,           # GB
        'percent': float,        # %
        'speed': int,            # MHz (or None)
        'xmp_enabled': bool,     # True/False
        'type': str,             # DDR3/DDR4/DDR5
    },
    'timestamp': float           # Unix timestamp
}
```

---

## 🔍 Troubleshooting

### Issue: UI not updating

**Check:**
1. DataBus started in `main.py`
2. Signals connected properly
3. No exceptions in callback

```python
# Debug
self.databus.data_updated.connect(lambda d: print("Update!", d))
```

### Issue: Slow performance

**Check:**
1. Not calling monitors directly
2. Using cached `get_*_data()` methods
3. DataBus interval not too low

```python
# Check performance
stats = self.databus.get_performance_stats()
print(stats)  # Should show <30ms poll time
```

### Issue: Missing data

**Check:**
1. Hardware available (`monitor.is_available()`)
2. No errors in logs
3. DataBus initialized monitors

```python
# Check data
data = self.databus.get_data()
print(data)  # Should have all keys
```

---

## 🚀 Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
2. Check [CHANGELOG.md](../CHANGELOG.md) for Part 2 details
3. See example implementation in `src/ui/main_window.py`
4. Run tests to verify migration

---

**Questions?** Check documentation or create an issue on GitHub.
