# Troubleshooting Guide

Package 3.8a - Common issues and solutions

## Installation Issues

### Issue: "OptiScaler not found"

**Symptom:**
```python
ImportError: No module named 'optiscaler'
```

**Solution:**
```bash
# Ensure you're in the project root
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/partmart-boost/src"
```

---

### Issue: "Installation failed - Network error"

**Symptom:**
```
Download failed: URLError
```

**Solutions:**

1. Check internet connection
2. Try again (auto-retry 3 times)
3. Manual download:
   ```bash
   # Download OptiScaler manually
   wget https://github.com/optiscaler/OptiScaler/releases/latest/download/OptiScaler.zip
   
   # Extract to ./optiscaler/
   unzip OptiScaler.zip -d ./optiscaler/
   ```

---

### Issue: "Installation failed - GitHub rate limit"

**Symptom:**
```
HTTP 403: Rate limit exceeded
```

**Solution:**
Wait 1 hour or use GitHub token:

```python
import os
os.environ['GITHUB_TOKEN'] = 'your_token_here'
```

---

## Configuration Issues

### Issue: "Configuration not applied"

**Symptom:**
Game doesn't use FSR 3.1 after configuration

**Solutions:**

1. Check installation:
   ```python
   manager = OptiScalerManager()
   manager.initialize()
   print(manager.is_installed())  # Should be True
   ```

2. Verify configuration file:
   ```python
   config_path = manager.get_install_dir() / "nvngx.ini"
   print(config_path.exists())  # Should be True
   print(config_path.read_text())  # Check content
   ```

3. Re-apply configuration:
   ```python
   manager.configure(config)
   ```

---

## Injection Issues

### Issue: "Game not detected"

**Symptom:**
```python
game = manager.detect_game(game_dir)
print(game)  # None
```

**Solutions:**

1. Check game directory path:
   ```python
   game_dir = Path("C:/Games/YourGame/bin/x64")  # Typical location
   print(game_dir.exists())  # Should be True
   ```

2. Look for game executable manually:
   ```python
   for exe in game_dir.glob("*.exe"):
       print(exe.name)
   ```

3. Check for upscaler DLLs:
   ```python
   dlss = game_dir / "nvngx_dlss.dll"
   fsr2 = game_dir / "amd_fidelityfx_fsr2.dll"
   print(f"DLSS: {dlss.exists()}")
   print(f"FSR2: {fsr2.exists()}")
   ```

---

### Issue: "Injection failed - Permission denied"

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
Run as administrator (Windows):

```bash
# Right-click Python script → "Run as administrator"
```

Or check admin privileges:
```python
from optiscaler.injector import OptiScalerInjector
print(OptiScalerInjector.is_admin())  # Should be True
```

---

### Issue: "Game crashes after injection"

**Symptom:**
Game crashes on startup after OptiScaler injection

**Solutions:**

1. Remove OptiScaler:
   ```python
   manager.remove_from_game(game)
   ```

2. Check game compatibility:
   - Verify game is in [supported list](https://github.com/optiscaler/OptiScaler#supported-games)

3. Try different backend:
   ```python
   config.backend = OptiScalerBackend.XESS  # Instead of FSR3
   manager.configure(config)
   manager.inject_into_game(game)
   ```

4. Restore original DLLs:
   ```bash
   # Manual restore from backup
   cd "C:/Games/YourGame/bin/x64"
   cp optiscaler_backup/*.dll .
   ```

---

## Performance Issues

### Issue: "Low FPS with OptiScaler"

**Symptom:**
FPS lower than expected

**Solutions:**

1. Try Performance mode:
   ```python
   config.quality = OptiScalerQuality.PERFORMANCE
   manager.configure(config)
   ```

2. Disable frame generation:
   ```python
   config.enable_frame_gen = False
   manager.configure(config)
   ```

3. Check GPU usage:
   - OptiScaler should use GPU, not CPU
   - Use GPU monitoring tool (MSI Afterburner, etc.)

4. Verify backend:
   ```python
   upscaler = UniversalUpscaler()
   upscaler.initialize()
   info = upscaler.get_backend_info()
   print(f"Backend: {info.backend.name}")  # Should be OPTISCALER
   ```

---

### Issue: "Software fallback instead of GPU"

**Symptom:**
```
Backend: SOFTWARE
FPS: ~30 (should be 300+)
```

**Solutions:**

1. Install OptiScaler:
   ```python
   if not manager.is_installed():
       manager.install()
   ```

2. Check OptiScaler files:
   ```python
   install_dir = manager.get_install_dir()
   print((install_dir / "nvngx.dll").exists())
   print((install_dir / "ffx_fsr3_x64.dll").exists())
   ```

3. Force OptiScaler backend:
   ```python
   from upscaler import UniversalUpscaler, UpscalerBackend
   
   upscaler = UniversalUpscaler(backend=UpscalerBackend.OPTISCALER)
   upscaler.initialize()
   ```

---

## GUI Issues

### Issue: "GUI not starting"

**Symptom:**
```
ImportError: No module named 'PyQt6'
```

**Solution:**
```bash
pip install PyQt6
```

---

### Issue: "Install button disabled"

**Symptom:**
"Install OptiScaler" button is grayed out

**Reasons:**
1. OptiScaler already installed → Check status label
2. Installation in progress → Wait for completion
3. Error occurred → Check status log

---

## FAQ

### Q: Does OptiScaler work on Linux?

**A:** Partially. OptiScaler primarily targets Windows. Linux support is experimental.

### Q: Can I use OptiScaler with DLSS games?

**A:** Yes! OptiScaler can replace DLSS with FSR 3.1 or XeSS.

### Q: Will this break my game?

**A:** No. OptiScaler creates backups of original DLLs. You can always restore them.

### Q: What if my game isn't supported?

**A:** Try anyway! OptiScaler works with many unlisted games. Report results to OptiScaler project.

### Q: How do I uninstall everything?

**A:**
```python
# Remove from game
manager.remove_from_game(game)

# Uninstall OptiScaler
manager.uninstall()
```

---

## Still Need Help?

1. Check [Quick Start Guide](QUICK_START.md)
2. Read [API Reference](OPTISCALER_API.md)
3. Open issue: [GitHub Issues](https://github.com/vitorpixel-6436/partmart-boost/issues)
4. OptiScaler issues: [OptiScaler GitHub](https://github.com/optiscaler/OptiScaler/issues)

---

**Remember:** Always backup your game files before injection!
