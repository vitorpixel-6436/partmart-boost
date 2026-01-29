# Configuration Guide

**Version:** 0.3.5g (Package 3.9a)

## Configuration File

Location: `config/settings.json`

## Settings

### Monitoring

```json
{
  "monitoring": {
    "check_interval": 5.0,              // Seconds between checks
    "enable_performance_monitoring": true,
    "enable_game_detection": true,
    "enable_auto_recovery": true,
    "error_threshold": 10,              // Max errors before alert
    "recovery_retry_limit": 3           // Max recovery attempts
  }
}
```

### Historical Data

```json
{
  "historical_data": {
    "enabled": true,
    "retention_days": 30,               // Days to keep data
    "collection_interval": 60.0,        // Collection frequency (seconds)
    "aggregation_interval": 3600.0,     // Aggregation frequency (seconds)
    "enable_health_collection": true,
    "enable_error_collection": true,
    "enable_recovery_collection": true
  }
}
```

### Visualization

```json
{
  "visualization": {
    "enabled": true,
    "default_time_range": "Last 24 Hours",
    "auto_refresh": true,
    "refresh_interval": 30,             // Seconds
    "chart_colors": ["#3498db", "#2ecc71", ...]
  }
}
```

### User Interface

```json
{
  "ui": {
    "window_width": 1200,
    "window_height": 800,
    "theme": "light",                   // "light" or "dark"
    "show_notifications": true,
    "notification_duration": 5000,      // Milliseconds
    "show_system_tray": true
  }
}
```

## Presets

### Performance Mode
```json
{
  "monitoring": {
    "check_interval": 1.0,
    "enable_auto_recovery": true
  },
  "historical_data": {
    "collection_interval": 30.0
  }
}
```

### Battery Saver
```json
{
  "monitoring": {
    "check_interval": 30.0
  },
  "historical_data": {
    "collection_interval": 300.0
  }
}
```

### Minimal Storage
```json
{
  "historical_data": {
    "retention_days": 7,
    "collection_interval": 120.0
  }
}
```

## Editing Configuration

### Via GUI
1. Open Settings tab
2. Adjust values
3. Click Save

### Via File
1. Close application
2. Edit `config/settings.json`
3. Restart application

### Programmatically
```python
from core.config_manager import get_config_manager

config = get_config_manager()
config.set('monitoring.check_interval', 10.0)
config.save()
```

## Reset to Defaults

Delete `config/settings.json` and restart application.

## Environment Variables

```bash
# Override config path
export PARTMART_CONFIG="/path/to/config.json"

# Override data directory
export PARTMART_DATA="/path/to/data"
```

---

For more details, see [User Guide](USER_GUIDE.md)
