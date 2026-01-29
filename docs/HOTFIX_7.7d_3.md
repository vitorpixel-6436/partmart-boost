# Hotfix 7.7d_3 - Config Manager Call Fix + Dependency Update

**Version:** 0.3.5d_hotfix3 (Package 3.9a, Stage 7.7d_hotfix3)  
**Date:** January 29, 2026  
**Status:** ✅ FIXED

## Issues

**Issue 1: Config Manager Error**
```
❌ TypeError: get_config_manager() takes 0 positional arguments but 1 was given
```

**Issue 2: Deprecated Package Warning**
```
⚠️ FutureWarning: The pynvml package is deprecated. 
   Please install nvidia-ml-py instead.
```

## Root Causes

### Issue 1: Config Manager
- `get_config_manager()` is a singleton function
- Takes NO arguments
- `SystemIntegratorFinal.__init__()` was passing `config_path`

### Issue 2: Deprecated Package
- `pynvml` is deprecated by NVIDIA
- Official package is now `nvidia-ml-py`
- Need to update `requirements.txt`

## Fixes

### Fix 1: Remove Config Path Argument

**Before:**
```python
def __init__(self, config_path: str = 'config/settings.json'):
    # ...
    self.config_manager = get_config_manager(config_path)  # ❌ ERROR
```

**After:**
```python
def __init__(self):
    """Initialize system integrator
    
    Note: Managers are singletons - no config path needed
    """
    # ...
    self.config_manager = get_config_manager()  # ✅ FIXED
```

### Fix 2: Update Dependencies

**Before (requirements.txt):**
```txt
pynvml>=11.5.0             # Deprecated!
```

**After (requirements.txt):**
```txt
# GPU monitoring (NVIDIA)
# UPDATED: nvidia-ml-py is the official package (pynvml is deprecated)
nvidia-ml-py>=12.535.133   # NVIDIA GPU monitoring (official)
```

## Files Changed

1. `src/core/system_integrator_final.py`
   - Removed `config_path` parameter from `__init__`
   - Fixed `get_config_manager()` call (no arguments)
   - Updated version to 0.3.5d_hotfix3

2. `requirements.txt`
   - Replaced `pynvml>=11.5.0` with `nvidia-ml-py>=12.535.133`
   - Added comments explaining the change

3. `VERSION.txt`
   - Updated to 0.3.5d_hotfix3

4. `docs/HOTFIX_7.7d_3.md`
   - This document

## How to Apply

### Step 1: Update Files

**Option A: Git Pull**
```bash
cd partmart-boost
git pull origin main
```

**Option B: Download Files**
- system_integrator_final.py
- requirements.txt

### Step 2: Update Dependencies

**Uninstall old package:**
```bash
pip uninstall pynvml -y
```

**Install new package:**
```bash
pip install nvidia-ml-py
```

**Or install all:**
```bash
pip install -r requirements.txt
```

## Testing

**Before Fix:**
```
❌ TypeError: get_config_manager() takes 0 positional arguments but 1 was given
⚠️ FutureWarning: pynvml is deprecated
❌ Program crashes
```

**After Fix:**
```
✅ No TypeError
✅ No deprecation warning
✅ Program launches successfully
```

## Verification Steps

1. Apply hotfix
2. Update dependencies: `pip install -r requirements.txt`
3. Launch: `python launcher.py`
4. Select GUI mode (2)
5. Verify initialization completes

**Expected Output:**
```
Initializing PartMart Boost v0.3.5d_hotfix3...
[+] Configuration loaded
[+] Error reporter ready
[+] Health monitor ready
[+] Recovery coordinator ready
[+] Historical data store ready
[+] Data aggregator ready
[+] Performance monitor ready (CPU/GPU/RAM)
[+] Game detector ready (40+ games)
[+] FSR 3.x manager ready (frame generation)
[+] DLL injector ready
[+] Game profile manager ready
[+] Auto-injection manager ready

[+] PartMart Boost initialized successfully!
    Stage 7.7d: FSR 3.x + Game Profiles + Auto-Injection
```

## Impact

**Severity:** HIGH  
**Priority:** URGENT  
**Status:** FIXED ✅

**Affected:**
- System initialization
- GPU monitoring

**Fixed:**
- Config manager call
- Dependency deprecation warning

## About nvidia-ml-py

**What is it?**
- Official NVIDIA Management Library Python bindings
- Maintained by NVIDIA
- Replaces deprecated `pynvml`

**Features:**
- GPU monitoring
- Temperature readings
- Memory usage
- Clock speeds
- Power usage

**Compatibility:**
- Same API as pynvml
- Drop-in replacement
- No code changes needed in performance_monitor.py

## Checklist

- [x] Fixed get_config_manager() call
- [x] Updated requirements.txt
- [x] Replaced pynvml with nvidia-ml-py
- [x] Updated version number
- [x] Tested initialization
- [x] Verified no errors
- [x] Documented changes

## Additional Notes

**Why Singleton Pattern?**
- `get_config_manager()` returns singleton instance
- Config is loaded once, shared globally
- No need to pass config path
- Pattern used throughout codebase

**Migration Path:**
- Old code: `pynvml` → imports work but deprecated
- New code: `nvidia-ml-py` → official, no warnings
- API identical: no code changes needed

## Future Prevention

**For Developers:**
1. Check singleton pattern before passing arguments
2. Use latest official packages
3. Watch for deprecation warnings
4. Update dependencies regularly

---

**Hotfix Complete!** ✅

**Program ready to launch!**
