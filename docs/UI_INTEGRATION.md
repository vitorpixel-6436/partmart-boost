# 🎨 UI Integration Guide

**How to connect your UI widgets to the DataBus architecture**

---

## 🎯 Quick Start

### 1. Basic Widget Connection

```python
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from core.databus import get_databus

class CPUCard(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create UI elements
        self.layout = QVBoxLayout()
        self.label = QLabel("CPU: --")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
        # Connect to DataBus
        bus = get_databus()
        bus.cpu_updated.connect(self.on_cpu_update)
    
    def on_cpu_update(self, cpu_data: dict):
        """Called when CPU data changes"""
        load = cpu_data.get('load', 0)
        self.label.setText(f"CPU: {load:.1f}%")
```

**That's it!** ✅ Your widget now updates automatically every 2 seconds.

---

## 📄 Available Signals

### DataBus Signals:

```python
from core.databus import get_databus

bus = get_databus()

# Full data update (all components)
bus.data_updated.connect(callback)  # dict with 'gpu', 'cpu', 'ram'

# Component-specific updates
bus.gpu_updated.connect(callback)   # dict with GPU data
bus.cpu_updated.connect(callback)   # dict with CPU data
bus.ram_updated.connect(callback)   # dict with RAM data

# Error handling
bus.error_occurred.connect(callback) # str with error message
```

### Data Structure:

```python
{
    'gpu': {
        'name': 'NVIDIA GeForce RTX 3060 Ti',
        'temp_gpu': 65,          # °C
        'temp_hotspot': 75,      # °C (may be None)
        'clock_gpu': 1800,       # MHz
        'clock_mem': 7000,       # MHz
        'load_gpu': 80,          # %
        'load_mem': 60,          # %
        'power': 150,            # Watts
        'fan_speed': 70,         # %
    },
    'cpu': {
        'load': 45,              # %
        'temp': 55,              # °C (may be None)
        'freq': 3600,            # MHz
        'freq_min': 800,         # MHz
        'freq_max': 4400,        # MHz
        'count': 6,              # Physical cores
        'count_logical': 12,     # Threads
    },
    'ram': {
        'total': 16.0,           # GB
        'used': 8.5,             # GB
        'free': 7.5,             # GB
        'percent': 53.1,         # %
        'speed': 3200,           # MHz
        'xmp_enabled': True,     # bool
    }
}
```

---

## 📐 Integration Patterns

### Pattern 1: Single Component Widget

**Use case:** Widget only cares about one component (GPU, CPU, or RAM)

```python
class GPUTemperatureCard(QWidget):
    def __init__(self):
        super().__init__()
        self.temp_label = QLabel("--°C")
        
        # Subscribe to GPU updates only
        bus = get_databus()
        bus.gpu_updated.connect(self.on_gpu_update)
    
    def on_gpu_update(self, gpu_data: dict):
        temp = gpu_data.get('temp_gpu', 0)
        self.temp_label.setText(f"{temp}°C")
```

**Benefits:**
- ✅ Only receives relevant updates
- ✅ Lower overhead
- ✅ Cleaner code

---

### Pattern 2: Multi-Component Widget

**Use case:** Widget displays data from multiple components

```python
class SystemOverview(QWidget):
    def __init__(self):
        super().__init__()
        self.cpu_label = QLabel("CPU: --")
        self.gpu_label = QLabel("GPU: --")
        self.ram_label = QLabel("RAM: --")
        
        # Subscribe to full updates
        bus = get_databus()
        bus.data_updated.connect(self.on_update)
    
    def on_update(self, data: dict):
        # Update all components at once
        cpu = data.get('cpu', {})
        gpu = data.get('gpu', {})
        ram = data.get('ram', {})
        
        self.cpu_label.setText(f"CPU: {cpu.get('load', 0):.1f}%")
        self.gpu_label.setText(f"GPU: {gpu.get('temp_gpu', 0)}°C")
        self.ram_label.setText(f"RAM: {ram.get('percent', 0):.1f}%")
```

**Benefits:**
- ✅ Single callback for all data
- ✅ Atomic updates (all or nothing)
- ✅ Simpler logic

---

### Pattern 3: Conditional Updates

**Use case:** Only update UI when specific conditions are met

```python
class WarningWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        
        bus = get_databus()
        bus.gpu_updated.connect(self.check_temperature)
    
    def check_temperature(self, gpu_data: dict):
        temp = gpu_data.get('temp_gpu', 0)
        
        # Only update if temperature is critical
        if temp > 80:
            self.warning_label.setText(f"⚠️ WARNING: GPU at {temp}°C!")
            self.show()
        else:
            self.hide()
```

**Benefits:**
- ✅ Reduces unnecessary UI updates
- ✅ Better performance
- ✅ User-focused alerts

---

### Pattern 4: Lazy Initialization

**Use case:** Widget may not be visible initially

```python
class DetailedStatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._connected = False
    
    def showEvent(self, event):
        """Connect to DataBus when widget becomes visible"""
        super().showEvent(event)
        
        if not self._connected:
            bus = get_databus()
            bus.data_updated.connect(self.on_update)
            self._connected = True
            
            # Force immediate update
            self.on_update(bus.get_data())
    
    def on_update(self, data: dict):
        # Update UI
        pass
```

**Benefits:**
- ✅ No overhead when hidden
- ✅ Instant update when shown
- ✅ Better resource usage

---

## 🚀 Advanced Features

### Get Current Data (Synchronous)

```python
from core.databus import get_databus

bus = get_databus()

# Get latest cached data (instant, no hardware access)
data = bus.get_data()

print(f"CPU Load: {data['cpu']['load']}%")
```

**Use cases:**
- Initial widget setup
- On-demand data access
- Testing

---

### Force Update

```python
bus = get_databus()

# Force immediate update (bypasses throttling)
bus.force_update()
```

**Use cases:**
- User clicked "Refresh" button
- Critical alert check
- Manual data refresh

---

### Change Update Interval

```python
bus = get_databus()

# Change to 1 second updates
bus.set_update_interval(1000)  # milliseconds

# Change to 5 second updates
bus.set_update_interval(5000)
```

**Use cases:**
- Power saving mode (slower updates)
- Performance mode (faster updates)
- User preference

---

### Throttling Control

```python
bus = get_databus()

# Disable throttling (emit all updates)
bus.set_throttling(enabled=False)

# Enable with custom threshold (2% change)
bus.set_throttling(enabled=True, threshold=0.02)
```

**Use cases:**
- Debug mode (see all updates)
- High-precision monitoring
- Custom sensitivity

---

### Performance Monitoring

```python
bus = get_databus()

stats = bus.get_performance_stats()

print(f"Average update time: {stats['avg_time_ms']:.2f}ms")
print(f"Last update time: {stats['last_time_ms']:.2f}ms")
print(f"Total updates: {stats['total_updates']}")
print(f"Update interval: {stats['update_interval_ms']}ms")
```

**Use cases:**
- Performance debugging
- System monitoring
- Optimization validation

---

## 💡 Best Practices

### DO ✅

#### 1. Connect in `__init__`
```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Good: Connect early
        bus = get_databus()
        bus.cpu_updated.connect(self.on_update)
```

#### 2. Use Specific Signals
```python
# Good: Only subscribe to what you need
bus.gpu_updated.connect(self.on_gpu_update)

# Less efficient: Receive all updates
bus.data_updated.connect(self.on_all_updates)
```

#### 3. Check for None Values
```python
def on_cpu_update(self, cpu_data: dict):
    temp = cpu_data.get('temp')
    if temp is not None:
        self.temp_label.setText(f"{temp}°C")
    else:
        self.temp_label.setText("--")
```

#### 4. Use Type Hints
```python
def on_update(self, data: Dict[str, Any]) -> None:
    pass
```

---

### DON'T ❌

#### 1. Don't Access Hardware Directly
```python
# ❌ BAD
import psutil
cpu = psutil.cpu_percent()

# ✅ GOOD
bus = get_databus()
bus.cpu_updated.connect(self.on_cpu_update)
```

#### 2. Don't Poll Manually
```python
# ❌ BAD
while True:
    data = bus.get_data()
    self.update(data)
    time.sleep(2)

# ✅ GOOD
bus.cpu_updated.connect(self.on_update)
```

#### 3. Don't Block in Callbacks
```python
# ❌ BAD
def on_update(self, data):
    time.sleep(1)  # Blocks UI!
    self.update(data)

# ✅ GOOD
def on_update(self, data):
    self.update(data)  # Fast update only
```

#### 4. Don't Forget Error Handling
```python
# ❌ BAD
def on_update(self, data):
    value = data['cpu']['temp']  # May be None!

# ✅ GOOD
def on_update(self, data):
    try:
        value = data.get('cpu', {}).get('temp')
        if value is not None:
            self.display(value)
    except Exception as e:
        print(f"Update error: {e}")
```

---

## 🔧 Real-World Example

### Complete Widget Implementation:

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from core.databus import get_databus
from typing import Dict, Optional

class SystemCard(QWidget):
    """Complete system monitoring card with best practices"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_databus()
    
    def _setup_ui(self):
        """Initialize UI elements"""
        self.layout = QVBoxLayout()
        
        # Title
        self.title = QLabel("System Monitor")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Metrics
        self.cpu_label = QLabel("CPU: --")
        self.gpu_label = QLabel("GPU: --")
        self.ram_label = QLabel("RAM: --")
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        
        # Layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.gpu_label)
        self.layout.addWidget(self.ram_label)
        self.layout.addWidget(self.refresh_btn)
        
        self.setLayout(self.layout)
    
    def _connect_databus(self):
        """Connect to DataBus signals"""
        self.bus = get_databus()
        self.bus.data_updated.connect(self._on_data_update)
        self.bus.error_occurred.connect(self._on_error)
        
        # Get initial data
        initial_data = self.bus.get_data()
        if initial_data:
            self._on_data_update(initial_data)
    
    def _on_data_update(self, data: Dict):
        """Handle data update"""
        try:
            # CPU
            cpu = data.get('cpu', {})
            cpu_load = cpu.get('load', 0)
            cpu_temp = cpu.get('temp')
            
            cpu_text = f"CPU: {cpu_load:.1f}%"
            if cpu_temp is not None:
                cpu_text += f" @ {cpu_temp}°C"
            
            self.cpu_label.setText(cpu_text)
            
            # GPU
            gpu = data.get('gpu', {})
            gpu_temp = gpu.get('temp_gpu', 0)
            gpu_load = gpu.get('load_gpu', 0)
            
            self.gpu_label.setText(f"GPU: {gpu_load}% @ {gpu_temp}°C")
            
            # RAM
            ram = data.get('ram', {})
            ram_percent = ram.get('percent', 0)
            ram_used = ram.get('used', 0)
            ram_total = ram.get('total', 0)
            
            self.ram_label.setText(
                f"RAM: {ram_percent:.1f}% ({ram_used:.1f}/{ram_total:.1f} GB)"
            )
        
        except Exception as e:
            print(f"[SystemCard] Update error: {e}")
    
    def _on_error(self, error_msg: str):
        """Handle error"""
        print(f"[SystemCard] DataBus error: {error_msg}")
        # Could show error in UI
    
    def _on_refresh_clicked(self):
        """Handle refresh button click"""
        self.bus.force_update()
    
    def showEvent(self, event):
        """Widget shown - ensure we have latest data"""
        super().showEvent(event)
        if self.bus:
            data = self.bus.get_data()
            if data:
                self._on_data_update(data)
```

---

## 📊 Performance Tips

### 1. Use Specific Signals
```python
# Efficient: Only GPU updates
bus.gpu_updated.connect(self.on_gpu)  # ✅ Fast

# Less efficient: All updates
bus.data_updated.connect(self.on_all)  # ❌ Slower
```

### 2. Minimize UI Updates
```python
def on_update(self, data):
    # Group updates
    self.setUpdatesEnabled(False)
    
    self.label1.setText("...")
    self.label2.setText("...")
    self.label3.setText("...")
    
    self.setUpdatesEnabled(True)
```

### 3. Use Throttling
```python
# Only emit if >5% change
bus.set_throttling(enabled=True, threshold=0.05)
```

### 4. Lazy Connect
```python
def showEvent(self, event):
    if not self._connected:
        bus.cpu_updated.connect(self.on_update)
        self._connected = True
```

---

## 🎓 Summary

### Integration Steps:

1. **Import DataBus:**
   ```python
   from core.databus import get_databus
   ```

2. **Get instance:**
   ```python
   bus = get_databus()
   ```

3. **Connect signals:**
   ```python
   bus.cpu_updated.connect(self.on_cpu_update)
   ```

4. **Handle updates:**
   ```python
   def on_cpu_update(self, cpu_data: dict):
       self.label.setText(f"{cpu_data['load']:.1f}%")
   ```

5. **Start DataBus (in main window):**
   ```python
   bus.start()
   ```

**Done!** ✅ Your widget now updates automatically.

---

**See Also:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Full architecture overview
- [PERFORMANCE.md](../PERFORMANCE.md) - Performance details
- [../src/core/databus.py](../src/core/databus.py) - DataBus source code

---

**Version:** 0.3.4-alpha

**Last Updated:** 2026-01-28
