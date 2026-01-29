# Logging System

**Version:** 0.3.5j (Package 3.9a, Stage 7.7b.1/7.7)

## Overview

Centralized logging system for PartMart Boost with file rotation, colored console output, and ConfigManager integration.

## Features

- ✅ **Singleton pattern** - One logger instance across application
- ✅ **Multiple log levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **File output** - Automatic log file creation with rotation
- ✅ **Console output** - Colored output for easy reading
- ✅ **Thread-safe** - Safe for multi-threaded applications
- ✅ **Configurable** - Integrates with ConfigManager
- ✅ **Log rotation** - 10MB per file, 5 backups

## Quick Start

### Basic Usage

```python
from core.logger import AppLogger

# Get logger instance
logger = AppLogger.get_instance()

# Log messages
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Connection failed")
```

### With Component Name

```python
logger.info("Monitoring started", component="Monitor")
logger.error("Failed to load config", component="ConfigManager")
```

### Exception Logging

```python
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed", component="MyComponent")
    # Automatically includes full traceback
```

### Convenience Functions

```python
from core import logger

# Quick logging without getting instance
logger.info("Quick info message")
logger.error("Quick error", component="DataBus")
logger.debug("Debug info", component="Test")
```

## Log Levels

### DEBUG

Detailed information for diagnosing problems.

```python
logger.debug("Processing item 42", component="Processor")
logger.debug(f"Cache size: {cache_size}")
```

**When to use:**
- Variable values
- Function entry/exit
- Loop iterations
- Detailed state information

### INFO

Confirmation that things are working as expected.

```python
logger.info("Application started successfully")
logger.info("Connected to server", component="Network")
```

**When to use:**
- Application lifecycle events
- Successful operations
- Configuration changes
- Normal state transitions

### WARNING

Indication that something unexpected happened, but application continues.

```python
logger.warning("Disk space below 10%")
logger.warning("Using fallback configuration", component="Config")
```

**When to use:**
- Deprecated features
- Recoverable errors
- Performance issues
- Resource constraints

### ERROR

Serious problem that prevented a function from completing.

```python
logger.error("Failed to save file", component="FileManager")
logger.error("Database connection lost", exc_info=True)
```

**When to use:**
- Failed operations
- Unrecoverable errors in components
- Invalid state
- Resource failures

### CRITICAL

Very serious error that may cause application shutdown.

```python
logger.critical("Out of memory", exc_info=True)
logger.critical("Fatal configuration error")
```

**When to use:**
- Fatal errors
- System-level failures
- Security breaches
- Unrecoverable state

## Configuration

### Via ConfigManager

```python
from core.config_manager import ConfigManager
from core.log_config import LogConfig

# Load config
config = ConfigManager('config.json')

# Set log level in config
config.set('advanced.log_level', 'debug')

# Create logger with config
log_config = LogConfig(config)
logger = log_config.get_logger()
```

### Log Level from Config

**config.json:**
```json
{
  "advanced": {
    "log_level": "info"
  }
}
```

**Valid values:** `debug`, `info`, `warning`, `error`, `critical`

### Dynamic Level Change

```python
# Change via LogConfig
log_config.set_level('debug')

# Change directly
logger.set_level(logging.DEBUG)

# Change via ConfigManager (auto-applied)
config.set('advanced.log_level', 'warning')
```

## Log Output

### Console Output

**Colored output for easy reading:**

```
[12:34:56] [PartMartBoost] [INFO] Application started
[12:34:57] [PartMartBoost] [WARNING] [Monitor] High CPU usage
[12:34:58] [PartMartBoost] [ERROR] [DataBus] Message delivery failed
```

**Colors:**
- 🔵 DEBUG - Cyan
- 🟢 INFO - Green
- 🟡 WARNING - Yellow
- 🔴 ERROR - Red
- 🟣 CRITICAL - Magenta

### File Output

**Location:** `logs/partmart_boost.log`

**Format:**
```
[2026-01-29 02:30:15] [PartMartBoost] [INFO] [main.py:45] Application started
[2026-01-29 02:30:16] [PartMartBoost] [ERROR] [data_bus.py:123] Connection failed
```

**Includes:**
- Full timestamp
- Log level
- Source file and line number
- Component name (if provided)
- Message
- Exception traceback (if applicable)

### Log Rotation

- **Max file size:** 10MB
- **Backup count:** 5 files
- **Naming:** `partmart_boost.log`, `partmart_boost.log.1`, etc.
- **Oldest file** is deleted when rotation occurs

## Advanced Usage

### Custom Log Directory

```python
logger = AppLogger.get_instance(
    log_dir='custom_logs',
    log_level=logging.DEBUG
)
```

### Get Log File Path

```python
log_path = logger.get_log_file_path()
print(f"Logs at: {log_path}")
```

### Get All Log Files

```python
log_files = logger.get_log_files()
for log_file in log_files:
    print(log_file)
```

### Thread-Safe Logging

```python
import threading

def worker(n):
    logger = AppLogger.get_instance()
    logger.info(f"Worker {n} started", component="Worker")
    # ... do work ...
    logger.info(f"Worker {n} finished", component="Worker")

threads = []
for i in range(10):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Integration Examples

### With DataBus

```python
from core.data_bus import DataBus
from core.logger import get_logger

logger = get_logger()
bus = DataBus()

def on_message(msg):
    logger.debug(f"Received: {msg.topic}", component="DataBus")
    try:
        # Process message
        process(msg.data)
    except Exception as e:
        logger.error(f"Failed to process: {msg.topic}", 
                    component="DataBus", exc_info=True)

bus.subscribe('**', on_message)
```

### With ConfigManager

```python
from core.config_manager import ConfigManager
from core.logger import get_logger

logger = get_logger()
config = ConfigManager('config.json')

def on_config_change(key, value):
    logger.info(f"Config changed: {key} = {value}", component="Config")

config.subscribe('**', on_config_change)
```

### With PerformanceMonitor

```python
from core.performance_monitor import PerformanceMonitor
from core.logger import get_logger

logger = get_logger()
monitor = PerformanceMonitor()

try:
    monitor.start_monitoring()
    logger.info("Monitoring started", component="Monitor")
except Exception as e:
    logger.error("Failed to start monitoring", 
                component="Monitor", exc_info=True)
```

## Best Practices

### DO

✅ **Use appropriate log levels**
```python
logger.debug("Detailed trace info")
logger.info("Normal operation")
logger.error("Something went wrong")
```

✅ **Include component names**
```python
logger.info("Started", component="DataBus")
```

✅ **Log exceptions with traceback**
```python
try:
    risky()
except Exception:
    logger.exception("Failed", component="MyComponent")
```

✅ **Use f-strings for readability**
```python
logger.info(f"Processed {count} items in {elapsed:.2f}s")
```

### DON'T

❌ **Don't log sensitive data**
```python
# BAD
logger.info(f"Password: {password}")

# GOOD
logger.info("User authenticated")
```

❌ **Don't log in tight loops**
```python
# BAD
for item in million_items:
    logger.debug(f"Processing {item}")  # Too many logs!

# GOOD
logger.info(f"Processing {len(million_items)} items")
# ... process ...
logger.info("Processing complete")
```

❌ **Don't use string concatenation**
```python
# BAD
logger.info("User " + username + " logged in")  # Slow!

# GOOD
logger.info(f"User {username} logged in")  # Fast!
```

❌ **Don't ignore exceptions silently**
```python
# BAD
try:
    risky()
except Exception:
    pass  # Silent failure!

# GOOD
try:
    risky()
except Exception:
    logger.exception("Operation failed", component="MyComponent")
```

## Troubleshooting

### Logs not appearing

**Check log level:**
```python
logger.set_level(logging.DEBUG)  # Show all logs
```

### Log file not created

**Check directory permissions:**
```python
import os
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)
```

### Too many log files

**Adjust rotation settings:**

Edit `logger.py`:
```python
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=5*1024*1024,  # 5MB instead of 10MB
    backupCount=3,         # 3 backups instead of 5
    encoding='utf-8'
)
```

### Colors not showing in console

**Check terminal support:**
- Windows: Use Windows Terminal or ConEmu
- Linux/Mac: Most terminals support ANSI colors

## Testing

### Run Logger Tests

```bash
python -m unittest tests.test_logger
```

### Test Output

```
test_debug_logging ✓ (0.012s)
test_error_logging ✓ (0.008s)
test_exception_logging ✓ (0.015s)
test_set_level ✓ (0.010s)
...

======================================================================
Tests run: 13
Passed: 13
Failed: 0
======================================================================
```

## API Reference

### AppLogger

#### Methods

- `get_instance(log_dir='logs', log_level=logging.INFO)` - Get singleton instance
- `set_level(level)` - Set log level
- `debug(message, component=None, **kwargs)` - Log debug message
- `info(message, component=None, **kwargs)` - Log info message
- `warning(message, component=None, **kwargs)` - Log warning message
- `error(message, component=None, exc_info=False, **kwargs)` - Log error message
- `critical(message, component=None, exc_info=False, **kwargs)` - Log critical message
- `exception(message, component=None, **kwargs)` - Log exception with traceback
- `get_log_file_path()` - Get current log file path
- `get_log_files()` - Get list of all log files

### LogConfig

#### Methods

- `__init__(config_manager=None, log_dir='logs')` - Initialize with config
- `get_logger()` - Get logger instance
- `set_level(level_name)` - Set log level by name

## See Also

- [Configuration System](CONFIG.md)
- [Data Bus](DATABUS.md)
- [Testing Guide](../tests/README.md)
