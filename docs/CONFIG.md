# Configuration Management

**Version:** 0.3.5h (Package 3.9a, Stage 7.6/7.7)

## Overview

ConfigManager provides comprehensive configuration management for PartMart Boost.

### Features

- **Hierarchical structure**: Dot notation (e.g., `ui.theme`)
- **Schema validation**: Type checking and constraints
- **File persistence**: JSON format
- **Change notifications**: Subscribe to config changes
- **Default values**: Automatic fallbacks
- **Thread-safe**: Safe for multi-threaded use

## Basic Usage

### Creating ConfigManager

```python
from core.config_manager import ConfigManager

# With file persistence
config = ConfigManager('config.json')

# Without file (in-memory only)
config = ConfigManager()
```

### Getting Values

```python
# Get with default
theme = config.get('ui.theme', 'dark')

# Get without default (returns None if not found)
value = config.get('some.key')
```

### Setting Values

```python
# Set value (with validation)
config.set('ui.theme', 'light')

# Set without validation
config.set('custom.key', 'value', validate=False)
```

### Saving and Loading

```python
# Save to file
config.save()

# Save to different file
config.save('backup_config.json')

# Load from file
config.load('config.json')
```

## Configuration Schema

### Default Configuration

#### UI Settings

```python
ui.theme: str = 'dark'  # 'dark' or 'light'
ui.language: str = 'en'  # 'en' or 'ru'
ui.show_fps: bool = True
ui.window.width: int = 1200  # 800-3840
ui.window.height: int = 800  # 600-2160
```

#### Monitoring Settings

```python
monitor.enabled: bool = True
monitor.interval_ms: int = 100  # 10-5000
monitor.history_size: int = 1000  # 100-10000
```

#### Performance Settings

```python
performance.boost_enabled: bool = True
performance.priority: str = 'high'  # 'normal', 'high', 'realtime'
performance.affinity_enabled: bool = False
```

#### Game Detection

```python
games.auto_detect: bool = True
games.boost_on_start: bool = True
```

#### Advanced Settings

```python
advanced.analytics_interval: int = 10  # 5-60 seconds
advanced.log_level: str = 'info'  # 'debug', 'info', 'warning', 'error'
advanced.auto_save: bool = True
```

## Subscriptions

### Subscribe to Changes

```python
def on_theme_change(key, value):
    print(f"Theme changed to: {value}")

# Subscribe to specific key
sub_id = config.subscribe('ui.theme', on_theme_change)

# Subscribe to all UI changes
config.subscribe('ui.*', lambda k, v: print(f"{k} = {v}"))

# Subscribe to all changes
config.subscribe('**', lambda k, v: print(f"{k} = {v}"))
```

### Unsubscribe

```python
config.unsubscribe(sub_id)
```

## Sections

### Get Section

```python
# Get all UI settings
ui_config = config.get_section('ui')
# {'ui.theme': 'dark', 'ui.language': 'en', ...}

# Get all monitor settings
monitor_config = config.get_section('monitor')
```

## Schema Operations

### Get Schema

```python
schema = config.get_schema('ui.theme')
if schema:
    print(f"Type: {schema.type}")
    print(f"Default: {schema.default}")
    print(f"Choices: {schema.choices}")
```

### Get All Schemas

```python
all_schemas = config.get_all_schemas()
for key, schema in all_schemas.items():
    print(f"{key}: {schema.description}")
```

## Reset

### Reset Specific Key

```python
config.reset('ui.theme')  # Reset to default
```

### Reset All

```python
config.reset()  # Reset everything to defaults
```

## Export

### Export to Dictionary

```python
config_dict = config.to_dict()
# {'ui': {'theme': 'dark', ...}, 'monitor': {...}}
```

## Validation

### Automatic Validation

Values are automatically validated when set:

```python
# Valid
config.set('ui.theme', 'dark')  # OK

# Invalid type
config.set('ui.theme', 123)  # Error: must be str

# Invalid choice
config.set('ui.theme', 'red')  # Error: must be 'dark' or 'light'

# Out of range
config.set('monitor.interval_ms', 10000)  # Error: max is 5000
```

### Custom Validation

Add custom schema:

```python
from core.config_manager import ConfigSchema

schema = ConfigSchema(
    key='custom.port',
    type=int,
    default=8080,
    description='Server port',
    min_value=1024,
    max_value=65535
)

config._schema['custom.port'] = schema
```

## Integration with DataBus

### ConfigIntegration

Automatically publishes config changes to DataBus:

```python
from core.config_manager import ConfigManager
from core.data_bus import DataBus
from core.config_integration import ConfigIntegration

config = ConfigManager('config.json')
bus = DataBus()
integration = ConfigIntegration(config=config, data_bus=bus)

integration.start()

# Subscribe to config changes on bus
bus.subscribe('config.changed.*', lambda msg: print(msg.data))

# Change config (automatically published to bus)
config.set('ui.theme', 'light')
# Bus receives: topic='config.changed.ui.theme', data={'key': 'ui.theme', 'value': 'light'}
```

## File Format

### JSON Structure

```json
{
  "ui": {
    "theme": "dark",
    "language": "en",
    "show_fps": true,
    "window": {
      "width": 1200,
      "height": 800
    }
  },
  "monitor": {
    "enabled": true,
    "interval_ms": 100,
    "history_size": 1000
  },
  "performance": {
    "boost_enabled": true,
    "priority": "high",
    "affinity_enabled": false
  },
  "games": {
    "auto_detect": true,
    "boost_on_start": true
  },
  "advanced": {
    "analytics_interval": 10,
    "log_level": "info",
    "auto_save": true
  }
}
```

## Best Practices

### Key Naming

1. Use lowercase
2. Use dots for hierarchy
3. Be descriptive but concise
4. Group related settings

```python
# Good
'ui.theme'
'monitor.interval_ms'
'performance.boost_enabled'

# Avoid
'UI_THEME'  # Use lowercase
'interval'  # Too vague
'performance_boost_enabled'  # Use dots, not underscores
```

### Subscriptions

```python
# Subscribe to specific keys when possible
config.subscribe('ui.theme', handler)  # Good

# Use wildcards sparingly
config.subscribe('ui.*', handler)  # OK for sections
config.subscribe('**', handler)  # Use only for logging/debugging
```

### Auto-Save

```python
# Enable auto-save for user settings
config.set('advanced.auto_save', True)

# Disable for temporary/test configurations
config.set('advanced.auto_save', False)
```

## Examples

### Example 1: Theme Switcher

```python
config = ConfigManager('config.json')

def switch_theme():
    current = config.get('ui.theme')
    new_theme = 'light' if current == 'dark' else 'dark'
    config.set('ui.theme', new_theme)
    print(f"Switched to {new_theme} theme")

switch_theme()
```

### Example 2: Monitor Settings

```python
# Get monitor settings
interval = config.get('monitor.interval_ms')
history = config.get('monitor.history_size')
enabled = config.get('monitor.enabled')

# Apply to monitor
if enabled:
    monitor.set_interval(interval)
    monitor.set_history_size(history)
```

### Example 3: Settings Panel

```python
# Get all settings for display
ui_settings = config.get_section('ui')
monitor_settings = config.get_section('monitor')

for key, value in ui_settings.items():
    schema = config.get_schema(key)
    if schema:
        print(f"{schema.description}: {value}")
```

### Example 4: Validation

```python
# Try to set value
if config.set('monitor.interval_ms', 50):
    print("Interval updated")
else:
    print("Invalid interval (must be 10-5000)")
```

## Architecture

```
Application
├─ ConfigManager
│  ├─ Load from file
│  ├─ Schema validation
│  ├─ Change tracking
│  └─ Save to file
│
├─ ConfigIntegration
│  ├─ Subscribe to changes
│  ├─ Publish to DataBus
│  └─ Auto-save
│
└─ Components
   ├─ Subscribe to config changes
   ├─ Apply settings
   └─ Update when changed
```

## Thread Safety

ConfigManager is fully thread-safe:

- All operations use `threading.RLock()`
- Safe to get/set from any thread
- Callbacks execute in setting thread

## Performance

- **Get latency:** <0.01ms
- **Set latency:** <0.1ms (with validation)
- **Save latency:** <10ms (typical)
- **Memory:** ~1KB base + ~100 bytes per setting
