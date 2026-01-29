# Error Handling Guide

**Version:** 0.3.5k (Package 3.9a, Stage 7.7b.2/7.7)

## Overview

Comprehensive error handling system for PartMart Boost with logging integration and graceful degradation.

## Principles

### 1. **Fail Gracefully**
Never crash the application due to component failures.

### 2. **Log Everything**
All errors are logged with context and stack traces.

### 3. **Provide Fallbacks**
Components should have sensible fallback behavior.

### 4. **User-Friendly Messages**
Log technical details, but show user-friendly messages in UI.

### 5. **Recover When Possible**
Attempt to recover from transient errors.

## Error Handling Patterns

### Pattern 1: Try-Catch with Logging

```python
from core import logger

def risky_operation():
    try:
        # Risky code
        result = perform_operation()
        return result
    
    except SpecificError as e:
        logger.error(f"Operation failed: {e}", component="MyComponent")
        return default_value
    
    except Exception as e:
        logger.exception("Unexpected error", component="MyComponent")
        return default_value
```

### Pattern 2: Validation Before Execution

```python
def set_value(self, key: str, value: Any) -> bool:
    # Validate input
    if not key:
        logger.warning("Empty key provided", component="ConfigManager")
        return False
    
    if value is None:
        logger.warning(f"None value for {key}", component="ConfigManager")
        return False
    
    try:
        # Perform operation
        self._data[key] = value
        return True
    
    except Exception as e:
        logger.error(f"Failed to set {key}: {e}", component="ConfigManager")
        return False
```

### Pattern 3: Fallback Values

```python
def get_config(self, key: str, default: Any) -> Any:
    try:
        return self._config[key]
    
    except KeyError:
        logger.debug(f"Key not found: {key}, using default", component="Config")
        return default
    
    except Exception as e:
        logger.error(f"Error getting {key}: {e}", component="Config")
        return default
```

### Pattern 4: Resource Cleanup

```python
def save_file(self, filename: str) -> bool:
    temp_file = filename + '.tmp'
    
    try:
        # Write to temp file
        with open(temp_file, 'w') as f:
            f.write(data)
        
        # Atomic replace
        os.replace(temp_file, filename)
        return True
    
    except Exception as e:
        logger.error(f"Failed to save {filename}: {e}", component="FileManager")
        return False
    
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
```

### Pattern 5: Callback Error Isolation

```python
def _notify_subscribers(self, event: str, data: Any):
    for callback in self._callbacks:
        try:
            callback(event, data)
        
        except Exception as e:
            # Don't let one bad callback break all others
            logger.error(f"Callback error: {e}", component="EventBus", exc_info=True)
            # Continue with other callbacks
```

## Component Error Handling

### ConfigManager

**Error Scenarios:**
- File not found
- Invalid JSON
- Permission denied
- Invalid values
- Type mismatches

**Handling:**
```python
config = ConfigManager('config.json')

# Returns default if file missing
theme = config.get('ui.theme', 'dark')

# Returns False on error
if not config.set('ui.theme', 'invalid'):
    print("Failed to set theme")

# Returns False on error
if not config.save():
    print("Failed to save config")
```

### DataBus

**Error Scenarios:**
- Callback exceptions
- Invalid topics
- Memory limits
- Thread errors

**Handling:**
```python
bus = DataBus()

# Callback errors are logged but don't break other subscribers
def bad_callback(msg):
    raise Exception("Oops!")

bus.subscribe('test', bad_callback)  # Won't crash the bus
```

### PerformanceHistory

**Error Scenarios:**
- Invalid metrics
- Memory overflow
- File I/O errors
- Data corruption

**Handling:**
```python
history = PerformanceHistory(max_samples=1000)

# Invalid data is rejected
history.add_snapshot(cpu=-1, gpu=150)  # Logged and ignored

# Export failures return False
if not history.export_csv('invalid/path/file.csv'):
    print("Export failed")
```

### PerformanceAnalytics

**Error Scenarios:**
- Insufficient data
- Invalid metrics
- Calculation errors

**Handling:**
```python
analytics = PerformanceAnalytics(history)

# Returns None if not enough data
report = analytics.analyze()
if report is None:
    print("Not enough data for analysis")
```

## Error Recovery

### Automatic Recovery

**1. Configuration**
```python
# If config file corrupted, use defaults
config = ConfigManager('config.json')
# Automatically falls back to defaults if file invalid
```

**2. Monitoring**
```python
# If monitoring fails, log and continue
monitor.start_monitoring()
# Internal errors logged, app continues
```

**3. Analytics**
```python
# If analytics fail, return None
report = analytics.analyze()
if report is None:
    # App continues without analytics
    pass
```

### Manual Recovery

**1. Reset Configuration**
```python
# Reset to defaults
config.reset()
config.save()
```

**2. Clear History**
```python
# Clear corrupted history
history.clear()
```

**3. Restart Component**
```python
# Stop and restart monitoring
monitor.stop_monitoring()
time.sleep(0.1)
monitor.start_monitoring()
```

## Testing Error Handling

### Unit Tests

```python
class TestErrorHandling(unittest.TestCase):
    def test_invalid_config_value(self):
        config = ConfigManager()
        
        # Should return False
        result = config.set('ui.theme', 123)
        self.assertFalse(result)
        
        # Value should not change
        theme = config.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_file_not_found(self):
        config = ConfigManager('nonexistent.json')
        
        # Should use defaults
        theme = config.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_callback_exception(self):
        bus = DataBus()
        received = []
        
        def bad_callback(msg):
            raise Exception("Error!")
        
        def good_callback(msg):
            received.append(msg.data)
        
        bus.subscribe('test', bad_callback)
        bus.subscribe('test', good_callback)
        
        bus.publish('test', {'value': 42})
        
        # Good callback should still receive
        time.sleep(0.01)
        self.assertEqual(len(received), 1)
```

## Best Practices

### DO

✅ **Always handle exceptions**
```python
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed", component="MyComponent")
```

✅ **Provide fallback values**
```python
value = config.get('key', default_value)
```

✅ **Return success status**
```python
def save() -> bool:
    try:
        # ...
        return True
    except Exception:
        return False
```

✅ **Log with context**
```python
logger.error(f"Failed to process {filename}", component="FileProcessor", exc_info=True)
```

✅ **Validate inputs**
```python
if not filename or not os.path.exists(filename):
    logger.warning(f"Invalid file: {filename}")
    return False
```

### DON'T

❌ **Don't swallow exceptions silently**
```python
# BAD
try:
    risky()
except Exception:
    pass  # Silent failure!

# GOOD
try:
    risky()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

❌ **Don't crash on invalid input**
```python
# BAD
def process(data):
    return data['key']  # KeyError crashes app!

# GOOD
def process(data):
    try:
        return data.get('key', default)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return default
```

❌ **Don't ignore return values**
```python
# BAD
config.save()  # Ignoring return value

# GOOD
if not config.save():
    logger.warning("Failed to save config")
    show_error_message("Could not save settings")
```

❌ **Don't use bare except**
```python
# BAD
try:
    operation()
except:  # Catches everything, including KeyboardInterrupt!
    pass

# GOOD
try:
    operation()
except Exception as e:  # Specific exception handling
    logger.error(f"Error: {e}")
```

## Error Messages

### For Logs (Technical)

```python
logger.error(
    f"Failed to load config from {filename}: {error}",
    component="ConfigManager",
    exc_info=True
)
```

**Include:**
- What operation failed
- Which file/resource
- Error details
- Stack trace

### For Users (Friendly)

```python
show_error_dialog(
    title="Configuration Error",
    message="Could not load settings. Using defaults.",
    details="Check logs for details."
)
```

**Include:**
- What went wrong (simple terms)
- What happens now (fallback)
- How to fix it (if possible)

## Debugging

### Enable Debug Logging

```python
from core.logger import AppLogger
import logging

logger = AppLogger.get_instance()
logger.set_level(logging.DEBUG)
```

### Check Log Files

```
logs/partmart_boost.log
```

### Common Error Patterns

**1. Permission Denied**
```
[ERROR] [ConfigManager] Permission denied: config.json
```

**Solution:** Run with appropriate permissions or change file location.

**2. Invalid JSON**
```
[ERROR] [ConfigManager] Invalid JSON: Expecting ',' delimiter: line 5 column 10
```

**Solution:** Fix JSON syntax or delete file to use defaults.

**3. Import Error**
```
[ERROR] [SystemInit] Failed to import module: No module named 'PyQt6'
```

**Solution:** Install missing dependencies.

## See Also

- [Logging System](LOGGING.md)
- [Configuration System](CONFIG.md)
- [Testing Guide](../tests/README.md)
