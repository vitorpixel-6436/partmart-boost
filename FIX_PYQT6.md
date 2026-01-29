# Fix PyQt6 DLL Load Error (Windows)

## Problem

When launching Modern GUI, you see:

```
[-] Failed to import PyQt6: DLL load failed while importing QtCore: The specified procedure could not be found.
```

This happens when PyQt6 installation is corrupted or incomplete on Windows.

## Solution

### Quick Fix (Recommended)

Run these commands in order:

```bash
# 1. Uninstall all PyQt6 components
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y

# 2. Clear pip cache
pip cache purge

# 3. Upgrade pip and setuptools
pip install --upgrade pip setuptools

# 4. Reinstall PyQt6
pip install PyQt6
```

### Alternative Fix (If Quick Fix Fails)

Install specific stable version:

```bash
# Uninstall first
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y

# Install specific version
pip install PyQt6==6.6.1
```

### Nuclear Option (Last Resort)

If nothing works, recreate Python environment:

```bash
# 1. Delete venv if exists
rmdir /s /q venv

# 2. Create fresh venv
python -m venv venv

# 3. Activate
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

## Verify Fix

After fixing, test:

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK!')"
```

If no errors, PyQt6 is fixed!

## Launch Modern GUI

```bash
python launcher.py
# Select option 1 (Modern GUI)
```

## Still Not Working?

### Use Legacy GUI

If Modern GUI still fails, use Legacy GUI:

```bash
python launcher.py
# Select option 2 (Legacy GUI)
```

Legacy GUI works without fancy UI but has all features.

### Use CLI Mode

Or use CLI mode (no GUI):

```bash
python launcher.py
# Select option 3 (CLI Mode)
```

## Common Causes

1. **Conflicting Python versions** - Check: `python --version`
2. **Corrupted pip cache** - Fixed by `pip cache purge`
3. **Missing Visual C++ redistributables** - Download from Microsoft
4. **Antivirus blocking DLLs** - Temporarily disable and retry

## More Help

If issue persists:
1. Check Python version: `python --version` (need 3.8+)
2. Check pip version: `pip --version`
3. Try running as Administrator
4. Create GitHub issue with error details

---

**After fixing, enjoy the beautiful Liquid Glass UI!** ✨
