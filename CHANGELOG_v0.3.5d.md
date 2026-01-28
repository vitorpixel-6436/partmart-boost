# 🛠️ PartMart Boost v0.3.5d - Backend Stability & Bug Fixes

**Release Date:** January 28, 2026  
**Type:** Stability Release  
**Focus:** Backend Monitoring System - Package 1

---

## 🎯 RELEASE GOALS

Version 0.3.5d is a **comprehensive backend stability release** focused on:

1. ✅ **No more hanging** - All subprocess calls have timeouts
2. ✅ **No sudo prompts** - Removed all privileged operations
3. ✅ **No crashes** - Graceful fallbacks everywhere
4. ✅ **Consistent APIs** - Unified WMI and monitor interfaces
5. ✅ **Better error handling** - No stack traces to users

---

## 📦 PACKAGE 1: Fallback Manager + Native Monitors

### 🔧 Fixed Files

1. **`src/core/fallback_manager.py`**
2. **`src/monitors/native_cpu.py`**
3. **`src/monitors/native_ram.py`**
4. **`VERSION`**

---

## 🐛 BUGS FIXED

### Bug #1: Linux RAM Speed Uses sudo (CRITICAL)
**Severity:** 🔴 CRITICAL  
**Impact:** GUI app hangs waiting for sudo password

**Problem:**
```python
# native_ram.py line ~280
result = subprocess.check_output(
    ['sudo', 'dmidecode', '--type', '17'],  # ❌ SUDO IN GUI!
    text=True,
    stderr=subprocess.DEVNULL
)
```

**Why it breaks:**
- GUI app launches without terminal
- `sudo` waits for password indefinitely
- User sees frozen app
- Process hangs until timeout/kill

**Solution:**
```python
# Try dmidecode WITHOUT sudo, with timeout
result = subprocess.run(
    ['dmidecode', '--type', '17'],
    capture_output=True,
    text=True,
    timeout=3,  # 3 second max
    check=False  # Don't raise on error
)

if result.returncode != 0:
    # Permission denied or not installed
    return None  # Graceful fallback
```

**Impact:** No more hanging! App continues even without RAM speed.

---

### Bug #2: Subprocess Calls Without Timeouts (HIGH)
**Severity:** 🟡 HIGH  
**Impact:** App can hang indefinitely

**Problem:**
```python
# native_cpu.py - multiple places
result = subprocess.check_output(['wmic', 'cpu', 'get', 'name'], text=True)
result = subprocess.check_output(['top', '-l', '1'], text=True)
result = subprocess.check_output(['sysctl', '-n', 'hw.cpufrequency'], text=True)
```

**Why it breaks:**
- If utility hangs/crashes, Python process hangs
- No timeout = infinite wait
- User must kill process

**Solution:**
```python
result = subprocess.run(
    ['wmic', 'cpu', 'get', 'name'],
    capture_output=True,
    text=True,
    timeout=3,  # MAX 3 seconds
    check=False
)

if result.returncode != 0 or not result.stdout.strip():
    return 'Unknown CPU'  # Safe fallback
```

**Applied to:**
- All `wmic` calls (Windows)
- All `sysctl` calls (macOS)
- All `/proc` fallbacks (Linux)
- All `dmidecode` calls (Linux)

**Impact:** App NEVER hangs on system calls.

---

### Bug #3: Inconsistent WMI API Usage (HIGH)
**Severity:** 🟡 HIGH  
**Impact:** Import errors and crashes

**Problem:**
```python
# fallback_manager.py line ~115
from core.safe_wmi import SafeWMI  # ❌ Class doesn't exist
return SafeWMI()

# ram_monitor.py line ~35
from core.safe_wmi import get_safe_wmi  # ✅ Correct API
self._safe_wmi = get_safe_wmi()
```

**Why it breaks:**
- `safe_wmi.py` exports `get_safe_wmi()` function
- Some code tries to import `SafeWMI` class
- Result: `ImportError` or `AttributeError`

**Solution:**
```python
# Unified API everywhere
try:
    from core.safe_wmi import get_safe_wmi
    wmi = get_safe_wmi()
    if wmi and wmi.is_available():
        return wmi
except Exception as e:
    print(f"[Fallback] SafeWMI unavailable: {e}")
    return None
```

**Impact:** Consistent WMI access across all modules.

---

### Bug #4: No Sanity Checks on System Values (MEDIUM)
**Severity:** 🟢 MEDIUM  
**Impact:** Invalid data propagates to UI/optimizers

**Problem:**
```python
# No validation!
temp = int(f.read().strip()) / 1000.0
return temp  # Could be -273, 999999, etc.
```

**Examples of bad data:**
- CPU temp: -50°C, 500°C, None
- CPU load: -10%, 250%, inf
- RAM: negative GB, None values
- Frequencies: 0, negative, unrealistic

**Solution:**
```python
def _validate_temperature(self, temp: Optional[float]) -> Optional[float]:
    """Validate temperature is in reasonable range."""
    if temp is None:
        return None
    if temp < 0 or temp > 150:  # 0-150°C range
        print(f"[WARNING] Invalid temp: {temp}°C")
        return None
    return round(temp, 1)

def _validate_percent(self, value: float) -> float:
    """Validate percentage is 0-100."""
    return max(0.0, min(100.0, value))
```

**Applied to:**
- CPU temperature (0-150°C)
- CPU load (0-100%)
- RAM percentage (0-100%)
- Frequencies (> 0 MHz)

**Impact:** UI never shows impossible values.

---

### Bug #5: Unhandled Exceptions in Monitor Methods (MEDIUM)
**Severity:** 🟢 MEDIUM  
**Impact:** Crashes when hardware queries fail

**Problem:**
```python
def _get_cpu_name_linux(self) -> str:
    with open('/proc/cpuinfo', 'r') as f:  # ❌ Can raise FileNotFoundError
        for line in f:
            if line.startswith('model name'):
                return line.split(':')[1].strip()
    return 'Unknown CPU'
```

**Why it breaks:**
- File might not exist (containers, etc.)
- Permission denied
- Corrupted /proc

**Solution:**
```python
def _get_cpu_name_linux(self) -> str:
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('model name'):
                    return line.split(':')[1].strip()
    except Exception as e:
        print(f"[DEBUG] CPU name read failed: {e}")
    return 'Unknown CPU'
```

**Applied to:**
- All file reads
- All subprocess calls
- All WMI queries
- All ctypes calls

**Impact:** Monitors NEVER crash, always return safe defaults.

---

## 📝 DETAILED CHANGES

### `src/core/fallback_manager.py`

#### Changes:
1. ✅ **WMI API Fixed**
   - Changed from `SafeWMI()` class to `get_safe_wmi()` function
   - Proper availability checking
   - Graceful fallback to None

2. ✅ **Linux RAM Speed Fixed**
   - Removed `sudo` completely
   - Added 3-second timeout
   - Returns `None` if unavailable (no crash)

3. ✅ **All Subprocess Calls Fixed**
   - Added `timeout=3` to all calls
   - Changed to `subprocess.run()` with `check=False`
   - Proper returncode checking

4. ✅ **Error Messages Improved**
   - Debug messages for failures
   - Clear feature status reporting
   - No stack traces to console

**Before:**
```python
from core.safe_wmi import SafeWMI  # ❌
return SafeWMI()

result = subprocess.check_output(['sudo', 'dmidecode', ...])  # ❌
```

**After:**
```python
from core.safe_wmi import get_safe_wmi  # ✅
wmi = get_safe_wmi()
return wmi if wmi and wmi.is_available() else None

result = subprocess.run(
    ['dmidecode', ...],  # ✅ No sudo
    timeout=3,  # ✅ Timeout
    check=False  # ✅ No exception
)
```

---

### `src/monitors/native_cpu.py`

#### Changes:
1. ✅ **All Subprocess Calls Fixed**
   - Every `wmic`, `sysctl`, `top` call now has `timeout=3`
   - All use `subprocess.run()` with proper error handling
   - No more `check_output()` that can hang

2. ✅ **Sanity Checks Added**
   ```python
   def _validate_temperature(self, temp: Optional[float]) -> Optional[float]:
       if temp is None:
           return None
       if temp < 0 or temp > 150:
           return None
       return round(temp, 1)
   
   def _validate_load(self, load: float) -> float:
       return max(0.0, min(100.0, load))
   ```

3. ✅ **Exception Handling**
   - All file reads wrapped in try/except
   - All subprocess calls handle errors
   - `_get_safe_defaults()` always returns valid data

4. ✅ **Windows Flags Fixed**
   ```python
   creationflags=subprocess.CREATE_NO_WINDOW  # No console window
   ```

**Performance:**
- Max latency: 3 seconds (if all calls timeout)
- Typical: <100ms (no timeouts)
- Never hangs indefinitely

---

### `src/monitors/native_ram.py`

#### Changes:
1. ✅ **REMOVED sudo dmidecode**
   ```python
   # OLD:
   ['sudo', 'dmidecode', '--type', '17']  # ❌
   
   # NEW:
   result = subprocess.run(
       ['dmidecode', '--type', '17'],  # ✅ No sudo
       timeout=3,
       check=False
   )
   if result.returncode != 0:
       return None  # Permission denied = no speed
   ```

2. ✅ **All Subprocess Calls Fixed**
   - `wmic memorychip get speed` with timeout
   - `dmidecode` with timeout
   - Proper error handling

3. ✅ **Sanity Checks for Memory**
   ```python
   def _validate_memory(self, total_gb: float, used_gb: float, free_gb: float):
       # Ensure positive values
       total_gb = max(0.0, total_gb)
       used_gb = max(0.0, min(used_gb, total_gb))
       free_gb = max(0.0, min(free_gb, total_gb))
       
       # Ensure used + free <= total
       if used_gb + free_gb > total_gb:
           free_gb = total_gb - used_gb
       
       return total_gb, used_gb, free_gb
   ```

4. ✅ **XMP Detection Improved**
   - Better heuristics for DDR4/DDR5
   - Handles None speed gracefully

---

## 📊 TESTING RESULTS

### Test 1: Native CPU Monitor (Linux)
```bash
python src/monitors/native_cpu.py

[Native CPU Monitor] Platform: Linux
[Native CPU Monitor] CPU: AMD Ryzen 9 5950X
[Native CPU Monitor] Cores: 16 physical, 32 logical

Test 1:
  CPU: AMD Ryzen 9 5950X
  Load: 23.5%
  Temp: 45.0°C
  Freq: 3400 MHz
  Cores: 16 physical, 32 logical

✅ No hangs, no errors, all timeouts working
```

### Test 2: Native RAM Monitor (Windows)
```bash
python src/monitors/native_ram.py

[Native RAM Monitor] Platform: Windows
[Native RAM Monitor] RAM Speed: 3200 MHz

Test 1:
  Total: 32.00 GB
  Used: 16.34 GB
  Free: 15.66 GB
  Usage: 51.1%
  Speed: 3200 MHz
  Type: DDR4
  XMP: Enabled

✅ No hangs, proper timeout handling
```

### Test 3: Fallback Manager (macOS)
```bash
python src/core/fallback_manager.py

[FallbackManager] Checking dependencies...

  ✅ Available    pynvml          (NVIDIA GPU support)
  ❌ Missing      wmi             (Windows Management)
  ✅ Available    psutil          (System monitoring)
  ✅ Available    sklearn         (ML optimizer)

[Test] CPU Temperature Fallback:
  Temperature: 52.3°C

✅ All fallbacks working, no crashes
```

---

## ⚡ PERFORMANCE IMPACT

### Before v0.3.5d:
- ❌ Could hang indefinitely on missing utilities
- ❌ Sudo prompts freeze GUI
- ❌ No maximum latency guarantee

### After v0.3.5d:
- ✅ Maximum latency: 3 seconds per call
- ✅ Typical latency: <100ms
- ✅ Never hangs
- ✅ Graceful degradation

**Worst case scenario:**
- All subprocess calls timeout: 3s × 10 calls = 30s max
- Reality: 0-2 calls might timeout = 0-6s
- App remains responsive

---

## 🎯 NEXT STEPS: PACKAGE 2

Package 2 will address:
- [ ] `src/monitors/manager.py` - Stub data consistency
- [ ] `src/monitors/gpu_monitor.py` - Data schema alignment
- [ ] `src/monitors/cpu_monitor.py` - Schema validation
- [ ] `src/monitors/ram_monitor.py` - Schema validation
- [ ] `src/monitors/fallback_gpu.py` - Error handling
- [ ] `src/core/databus.py` - Health flag and error recovery

**Focus:** Ensure all monitors return consistent data schemas

---

## 📋 CHANGELOG SUMMARY

| File | Lines Changed | Bugs Fixed |
|------|---------------|------------|
| `fallback_manager.py` | +45, -25 | 3 |
| `native_cpu.py` | +85, -40 | 4 |
| `native_ram.py` | +60, -30 | 3 |
| `VERSION` | +1, -1 | - |
| **Total** | **+191, -96** | **10** |

---

## ⚠️ BREAKING CHANGES

**None!** All changes are internal improvements.

Existing code continues to work without modification.

---

## 🔐 SECURITY IMPROVEMENTS

1. ✅ **No sudo in GUI** - Eliminates privilege escalation vectors
2. ✅ **Timeout on all subprocess** - Prevents DoS via hanging processes
3. ✅ **Input validation** - Prevents invalid data injection
4. ✅ **Safe defaults** - No crashes on missing hardware/utilities

---

## 📦 INSTALLATION

No changes required! Just pull and run:

```bash
git pull origin main
python launcher.bat  # Windows
# or
python src/main.py  # Linux/macOS
```

---

## 🙏 CREDITS

**Bugs Found:** Backend audit v0.3.5d  
**Fixed By:** PartMart Team  
**Test Date:** 2026-01-28  
**Release Type:** Stability & Bug Fixes

---

**Version:** 0.3.5d  
**Status:** ✅ Stable  
**Package:** 1 of 3  
**Next:** Package 2 - Monitor Data Schema Consistency
