# ❌ DEPRECATED & REMOVED CODE

**PartMart Boost v0.3.4-alpha**

This document lists deprecated and removed code from previous versions.

---

## 🗑️ REMOVED in v0.3.4

### 1. `src/system_monitor.py` ❌ **REMOVED**

**Reason:** Replaced by new 3-tier architecture

**Issues:**
- Tight coupling between UI and hardware
- Performance problems (150-300ms updates)
- No caching or optimization
- Hard to maintain and extend
- Security risks (direct WMI access)

**Migration:**
```python
# OLD (REMOVED)
from system_monitor import SystemMonitor
monitor = SystemMonitor()
data = monitor.get_all_data()  # Blocking!

# NEW (Use This)
from core.databus import get_databus
bus = get_databus()
bus.data_updated.connect(callback)  # Event-driven
bus.start()
```

**See:** [docs/MIGRATION.md](MIGRATION.md) for full migration guide

**Commit:** [f9d30f4](https://github.com/vitorpixel-6436/partmart-boost/commit/f9d30f40e3a6bb6479ef8d4d4f399b78035766d0)

---

### 2. `prototype_test.py` ❌ **REMOVED**

**Reason:** Obsolete prototype code

**Migration:** Use production code in `src/`

---

## ⚠️ UNSAFE PATTERNS (Avoid These)

### 1. Direct WMI Access ⚠️

**DON'T:**
```python
import wmi
c = wmi.WMI()
# Direct query - injection risk!
result = c.query(f"SELECT * FROM {user_input}")
```

**DO:**
```python
from core.safe_wmi import SafeWMI
safe_wmi = SafeWMI()
# Validated and safe
result = safe_wmi.get_ram_speed()
```

**See:** `src/core/safe_wmi.py`

---

### 2. Blocking CPU Measurement ⚠️

**DON'T:**
```python
import psutil
# Blocks UI for 100ms!
cpu = psutil.cpu_percent(interval=0.1)
```

**DO:**
```python
import psutil
# Non-blocking, instant
cpu = psutil.cpu_percent(interval=None)
```

**See:** `src/monitors/cpu_monitor.py`

---

### 3. No Caching ⚠️

**DON'T:**
```python
def get_temp():
    # Reads sensor every call (slow!)
    return read_sensor()
```

**DO:**
```python
from functools import lru_cache
from time import time

def get_temp():
    # Cache for 5 seconds
    if time() - self._last_temp_time < 5:
        return self._temp_cache
    
    self._temp_cache = read_sensor()
    self._last_temp_time = time()
    return self._temp_cache
```

**See:** `src/monitors/cpu_monitor.py`, `src/monitors/ram_monitor.py`

---

### 4. SQL String Concatenation ⚠️

**DON'T:**
```python
# SQL injection risk!
query = f"SELECT * FROM logs WHERE user = '{user_input}'"
cursor.execute(query)
```

**DO:**
```python
# Parameterized query (safe)
query = "SELECT * FROM logs WHERE user = ?"
cursor.execute(query, (user_input,))
```

**See:** `src/ai_optimizer.py`

---

### 5. Unchecked File Paths ⚠️

**DON'T:**
```python
# Path traversal risk!
path = f"data/{user_input}.db"
open(path, 'w')
```

**DO:**
```python
import os
from pathlib import Path

# Validate path
base = Path("data")
path = (base / user_input).resolve()

if not path.is_relative_to(base):
    raise ValueError("Invalid path")

open(path, 'w')
```

**See:** `src/ai_optimizer.py`, `src/core/config.py`

---

## 📝 DEPRECATED APIs (Still Work, But Update Soon)

### 1. Old Config Keys

**Deprecated:**
```python
config.get('update_ms')  # Old key name
```

**Use:**
```python
config.get_update_interval()  # New method
```

---

### 2. Old GPU Field Names

**Deprecated:**
```python
gpu_data['temperature']  # Old name
gpu_data['load']         # Old name
```

**Use:**
```python
gpu_data['temp_gpu']     # New name
gpu_data['load_gpu']     # New name
```

**See:** [docs/MIGRATION.md](MIGRATION.md) for full field mapping

---

## 🚀 MIGRATION TIMELINE

### v0.3.3 (Old)
- ❌ Tight coupling
- ❌ Blocking calls
- ❌ No caching
- ❌ Security issues

### v0.3.4-alpha (Current)
- ✅ Event-driven architecture
- ✅ Non-blocking updates
- ✅ Aggressive caching
- ✅ Security hardening
- ⚠️ **Breaking changes** (see MIGRATION.md)

### v0.4.0 (Stable) - Planned
- ✅ All deprecated code removed
- ✅ Full migration guide
- ✅ Comprehensive tests
- ✅ Production ready

---

## 🛠️ HOW TO UPDATE YOUR CODE

### Step 1: Check Current Code

Search your codebase for:
```bash
# Deprecated imports
grep -r "from system_monitor import" .
grep -r "import wmi" .

# Unsafe patterns
grep -r "cpu_percent(interval=" .
grep -r "f\"SELECT \* FROM" .
```

### Step 2: Read Migration Guide

See [docs/MIGRATION.md](MIGRATION.md) for:
- API changes
- Code examples
- Common issues
- Performance improvements

### Step 3: Update Code

Replace old patterns with new ones (see sections above)

### Step 4: Test

```bash
python src/monitors/manager.py  # Test monitors
python src/core/databus.py      # Test DataBus
```

---

## 📚 RESOURCES

- [MIGRATION.md](MIGRATION.md) - Full migration guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - New architecture
- [SECURITY.md](../SECURITY.md) - Security best practices
- [PERFORMANCE.md](../PERFORMANCE.md) - Performance details

---

## ❓ NEED HELP?

**Questions about deprecated code?**

Open an issue with:
- What you're trying to do
- Current code snippet
- Error message (if any)

**Want to contribute?**

Help us improve migration docs!

---

**Version:** 0.3.4-alpha

**Last Updated:** 2026-01-28
