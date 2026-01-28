# 🏴 Sovereignty & Autonomy Analysis

**Goal:** Achieve maximum independence from external dependencies

**Date:** 2026-01-28

---

## 🎯 Current Bottlenecks

### ❌ CRITICAL DEPENDENCIES (Sovereignty Risks)

| Dependency | Risk Level | Impact | Fallback Status |
|------------|-----------|---------|------------------|
| **nvidia-ml-py** | 🔴 HIGH | GPU monitoring | ✅ HAS FALLBACK (`fallback_gpu.py`) |
| **wmi** | 🟡 MEDIUM | RAM speed (Windows) | ✅ HAS WRAPPER (`safe_wmi.py`) |
| **psutil** | 🟡 MEDIUM | CPU/RAM monitoring | ❌ NO FALLBACK |
| **PyQt6** | 🔴 HIGH | Entire UI | ❌ NO ALTERNATIVE |
| **scikit-learn** | 🟢 LOW | ML predictions (optional) | ✅ ALREADY OPTIONAL |
| **requests** | 🟢 LOW | Updates check | ❌ Can use urllib |

---

## 🔴 PRIMARY BOTTLENECK: **psutil**

### Why It's Critical:

1. **CPU Monitoring:**
   - `psutil.cpu_percent()` - CPU load
   - `psutil.cpu_freq()` - CPU frequency
   - `psutil.cpu_count()` - Core count
   - `psutil.sensors_temperatures()` - CPU temp

2. **RAM Monitoring:**
   - `psutil.virtual_memory()` - RAM usage
   - Used in `CPUMonitor` and `RAMMonitor`

3. **Process Management:**
   - `psutil.Process()` - Process info
   - Used in Quick Boost

### Impact if psutil Unavailable:
- ❌ NO CPU monitoring
- ❌ NO RAM monitoring  
- ❌ NO Quick Boost
- ❌ Core functionality BREAKS

### Solution: Create Native System Monitors

---

## 🛠️ Solution: Sovereignty Mode

### Architecture:

```
┌─────────────────────────────────────────┐
│     TIER 1: PREFERRED (Full Features)   │
│  - pynvml (GPU)                         │
│  - psutil (CPU/RAM)                     │
│  - wmi (RAM speed)                      │
└────────────┬────────────────────────────┘
             │ if unavailable
             ↓
┌─────────────────────────────────────────┐
│     TIER 2: FALLBACK (Native OS APIs)   │
│  - fallback_gpu (WMIC/sysfs)            │
│  - native_cpu (WMI/proc)                │
│  - native_ram (/proc/meminfo)           │
└────────────┬────────────────────────────┘
             │ if unavailable
             ↓
┌─────────────────────────────────────────┐
│   TIER 3: MINIMAL (Read-Only Stubs)     │
│  - Return safe defaults                 │
│  - Show "Monitoring Unavailable"        │
│  - No crashes                           │
└─────────────────────────────────────────┘
```

---

## 📦 New Modules to Create

### 1. **Native CPU Monitor** (`monitors/native_cpu.py`)

**Purpose:** CPU monitoring WITHOUT psutil

**Windows Implementation:**
```python
import subprocess
import platform

def get_cpu_load_windows():
    # Use WMIC
    result = subprocess.check_output(
        ['wmic', 'cpu', 'get', 'loadpercentage'],
        text=True
    )
    return parse_wmic_output(result)

def get_cpu_temp_windows():
    # Use WMI via safe_wmi
    # Or parse from external sensor tools
    pass
```

**Linux Implementation:**
```python
def get_cpu_load_linux():
    # Parse /proc/stat
    with open('/proc/stat', 'r') as f:
        line = f.readline()
        # Calculate from jiffies
    return cpu_load

def get_cpu_temp_linux():
    # Parse /sys/class/thermal/
    thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
    temps = []
    for zone in thermal_zones:
        with open(zone) as f:
            temps.append(int(f.read()) / 1000.0)
    return max(temps) if temps else None
```

---

### 2. **Native RAM Monitor** (`monitors/native_ram.py`)

**Purpose:** RAM monitoring WITHOUT psutil

**Windows Implementation:**
```python
import ctypes
from ctypes import wintypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', wintypes.DWORD),
        ('dwMemoryLoad', wintypes.DWORD),
        ('ullTotalPhys', ctypes.c_ulonglong),
        ('ullAvailPhys', ctypes.c_ulonglong),
        # ...
    ]

def get_ram_windows():
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    
    return {
        'total': stat.ullTotalPhys / (1024**3),  # GB
        'used': (stat.ullTotalPhys - stat.ullAvailPhys) / (1024**3),
        'percent': stat.dwMemoryLoad
    }
```

**Linux Implementation:**
```python
def get_ram_linux():
    with open('/proc/meminfo', 'r') as f:
        meminfo = {}
        for line in f:
            key, value = line.split(':')[0], line.split()[1]
            meminfo[key] = int(value) * 1024  # KB to bytes
    
    total = meminfo['MemTotal']
    available = meminfo['MemAvailable']
    used = total - available
    
    return {
        'total': total / (1024**3),
        'used': used / (1024**3),
        'percent': (used / total) * 100
    }
```

---

### 3. **Sovereignty Manager** (`core/sovereignty.py`)

**Purpose:** Detect available monitoring methods and prioritize

```python
class SovereigntyManager:
    """
    Manages fallback hierarchy for maximum autonomy.
    
    Priority:
    1. External libraries (psutil, pynvml) - BEST
    2. Native OS APIs (WMIC, sysfs, ctypes) - GOOD
    3. Stub monitors (safe defaults) - MINIMAL
    """
    
    def __init__(self):
        self.monitoring_level = self._detect_level()
    
    def _detect_level(self):
        # Try psutil
        try:
            import psutil
            return 'FULL'  # All features
        except ImportError:
            pass
        
        # Try native APIs
        if self._test_native_apis():
            return 'NATIVE'  # Native monitoring
        
        # Fallback to stubs
        return 'MINIMAL'  # Read-only mode
    
    def get_cpu_monitor(self):
        if self.monitoring_level == 'FULL':
            from monitors.cpu_monitor import CPUMonitor
            return CPUMonitor()
        elif self.monitoring_level == 'NATIVE':
            from monitors.native_cpu import NativeCPUMonitor
            return NativeCPUMonitor()
        else:
            from monitors.stub_monitor import StubCPUMonitor
            return StubCPUMonitor()
    
    def get_monitoring_status(self):
        return {
            'level': self.monitoring_level,
            'cpu': 'available',
            'gpu': 'fallback' if self.monitoring_level != 'FULL' else 'full',
            'ram': 'available',
            'sovereignty_score': self._calculate_score()
        }
    
    def _calculate_score(self):
        # 100 = complete autonomy (no external deps)
        # 0 = full external dependency
        if self.monitoring_level == 'MINIMAL':
            return 100  # stdlib only!
        elif self.monitoring_level == 'NATIVE':
            return 80   # native OS APIs
        else:
            return 50   # external libraries
```

---

## 🎯 Implementation Plan

### Phase 1: Native Monitors (Priority)

**Files to Create:**
1. ✅ `monitors/native_cpu.py` - CPU without psutil
2. ✅ `monitors/native_ram.py` - RAM without psutil
3. ✅ `core/sovereignty.py` - Fallback manager

**Features:**
- Windows: WMIC + ctypes (kernel32.dll)
- Linux: /proc/stat + /proc/meminfo
- macOS: sysctl + vm_stat

### Phase 2: Dependency Optimization

**Remove/Replace:**
1. ❌ `requests` → ✅ `urllib` (stdlib)
2. ❌ `scikit-learn` → ✅ Make fully optional
3. ❌ `numpy` → ✅ Only if sklearn enabled

**Keep (Critical):**
- ✅ `PyQt6` - No alternative for UI
- ✅ `pynvml` - Best GPU API (has fallback)
- ✅ `wmi` - Windows-only, has safe wrapper

### Phase 3: Sovereignty Mode UI

**Add Settings:**
```python
[ ] Prefer Native Monitoring (No psutil)
[ ] Offline Mode (No internet checks)
[ ] Minimal Dependencies (No ML)
```

**Show Status:**
```
Sovereignty Level: NATIVE (80/100)
✅ CPU Monitoring: Native APIs
✅ GPU Monitoring: Fallback (WMIC)
✅ RAM Monitoring: Native APIs
⚠️  ML Optimizer: Disabled (sklearn unavailable)
```

---

## 📊 Sovereignty Metrics

### Current State (v0.3.4):

| Metric | Score |
|--------|-------|
| **External Dependencies** | 12 packages |
| **Critical Dependencies** | 3 (psutil, PyQt6, pynvml) |
| **Native Fallbacks** | 1 (GPU only) |
| **Offline Capability** | ⚠️  Partial (needs pip install) |
| **Sovereignty Score** | **50/100** |

### Target State (v0.3.5):

| Metric | Score |
|--------|-------|
| **External Dependencies** | 10 packages (-2) |
| **Critical Dependencies** | 1 (PyQt6 only) |
| **Native Fallbacks** | 3 (GPU, CPU, RAM) |
| **Offline Capability** | ✅ Full (after first install) |
| **Sovereignty Score** | **80/100** |

---

## 🏁 Success Criteria

### Must Have:
1. ✅ App runs WITHOUT psutil
2. ✅ App runs WITHOUT pynvml
3. ✅ App runs WITHOUT wmi
4. ✅ CPU/RAM/GPU monitoring works with native APIs
5. ✅ No internet required after install

### Nice to Have:
1. ⭐ Vendored dependencies (embed critical libs)
2. ⭐ Single .exe with everything bundled
3. ⭐ Zero external API calls
4. ⭐ Fully airgapped operation

---

## 🚀 Quick Start (After Implementation)

**MINIMAL MODE (stdlib only):**
```bash
# Uninstall external deps
pip uninstall psutil pynvml wmi scikit-learn -y

# Run with native monitoring
python src/main.py --sovereignty-mode
```

**Result:**
```
[INFO] Sovereignty Mode: NATIVE
[INFO] CPU Monitor: Native (WMIC)
[INFO] GPU Monitor: Fallback (WMIC)
[INFO] RAM Monitor: Native (kernel32)
[OK] Application running with FULL AUTONOMY
```

---

## 📈 Benefits

### 1. **True Independence**
- No reliance on external pip packages
- Works in airgapped environments
- No supply chain attacks

### 2. **Better Reliability**
- Fallbacks for every component
- Graceful degradation
- Never breaks from missing deps

### 3. **Faster Startup**
- No import overhead from large libs
- Direct OS API calls
- Minimal memory footprint

### 4. **Political Freedom**
- No dependence on NVIDIA's pynvml
- No dependence on Microsoft's WMI
- Maximum sovereignty

---

## 🎯 Priority Actions

### IMMEDIATE (Today):
1. Create `monitors/native_cpu.py`
2. Create `monitors/native_ram.py`
3. Create `core/sovereignty.py`
4. Update `MonitorManager` to use sovereignty

### SHORT-TERM (This Week):
5. Replace `requests` with `urllib`
6. Make sklearn fully optional
7. Add sovereignty UI settings
8. Test with zero external deps

### LONG-TERM (v0.4.0):
9. Vendor critical dependencies
10. Create standalone .exe
11. Implement full airgap mode
12. Achieve 100/100 sovereignty score

---

**Recommendation:** 🚀 **START WITH NATIVE MONITORS**

Eliminating psutil dependency = 80% sovereignty gain!

---

**Status:** 📝 PLANNED

**Risk:** 🟢 LOW

**Impact:** 🔴 HIGH (Maximum autonomy)

**Version:** v0.3.5-alpha
