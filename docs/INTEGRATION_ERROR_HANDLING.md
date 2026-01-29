# Integration Components Error Handling

**Version:** 0.3.5l (Package 3.9a, Stage 7.7b.3/7.7)

## Overview

Error handling in integration layer components that connect core systems together.

## Components

### MonitoringIntegration

Connects PerformanceMonitor → History → Analytics → DataBus

#### Error Scenarios

**1. Monitor Unavailable**
```python
# Gracefully handles missing monitor
integration = MonitoringIntegration(monitor=None)
integration.start()  # ✅ Works (testing mode)
```

**2. Invalid Metrics**
```python
# Validates and rejects invalid data
monitor.set_metrics(cpu=150, gpu=-50)  # Invalid!
integration._record_snapshot()  # ❌ Rejected, logged
```

**3. Analytics Module Missing**
```python
# Falls back gracefully
integration = MonitoringIntegration(monitor)
integration.start()  # ✅ Works without analytics
```

**4. DataBus Errors**
```python
# Isolates publish errors
bus.publish()  # Raises exception
# Analytics continues, error logged
```

**5. Worker Thread Errors**
```python
# Tracks errors and stops if threshold exceeded
error_count = 0
max_errors = 10

if error_count >= max_errors:
    integration.stop()  # Auto-stop on too many errors
```

#### Error Recovery

**Automatic Recovery:**
- Worker thread continues after transient errors
- Error counter resets after 60 seconds
- Invalid metrics are logged and skipped
- Missing data returns None instead of crashing

**Manual Recovery:**
```python
# Stop and restart
integration.stop()
time.sleep(1)
integration.start()
```

#### Status Checking

```python
status = integration.get_status()
print(status)
# {
#     'active': True,
#     'analytics_available': True,
#     'has_monitor': True,
#     'has_databus': True,
#     'error_count': 2,
#     'history_samples': 150,
#     'has_report': True
# }
```

### ConfigIntegration

Connects ConfigManager → DataBus

#### Error Scenarios

**1. Config File Missing**
```python
# Uses defaults
config = ConfigManager('missing.json')
integration = ConfigIntegration(config, bus)
integration.start()  # ✅ Works with defaults
```

**2. Invalid Config Changes**
```python
# Validation prevents invalid values
config.set('ui.theme', 'invalid')  # ❌ Rejected
# No event published to DataBus
```

**3. DataBus Unavailable**
```python
# Works without DataBus
integration = ConfigIntegration(config, data_bus=None)
integration.start()  # ✅ Works, no events published
```

## Error Handling Patterns

### Pattern 1: Graceful Start/Stop

```python
def start(self) -> bool:
    try:
        if self._active:
            self._log_info("Already active")
            return True
        
        # Check prerequisites
        if not self._can_start():
            self._log_error("Cannot start: prerequisites not met")
            return False
        
        # Start
        self._active = True
        self._start_worker()
        
        return True
    
    except Exception as e:
        self._log_error(f"Failed to start: {e}", exc_info=True)
        self._active = False
        return False
```

### Pattern 2: Error Tracking

```python
class ComponentIntegration:
    def __init__(self):
        self._error_count = 0
        self._max_errors = 10
        self._last_error_time = 0.0
    
    def _handle_error(self, error: Exception):
        now = time.time()
        
        # Reset count after cooldown
        if now - self._last_error_time > 60.0:
            self._error_count = 0
        
        self._error_count += 1
        self._last_error_time = now
        
        self._log_error(f"Error ({self._error_count}/{self._max_errors}): {error}")
        
        # Stop if too many errors
        if self._error_count >= self._max_errors:
            self._log_error("Too many errors, stopping")
            self.stop()
```

### Pattern 3: Metrics Validation

```python
def _record_snapshot(self):
    try:
        metrics = self._monitor.get_current_metrics()
        
        # Validate
        if not self._validate_metrics(metrics):
            self._log_warning(f"Invalid metrics: {metrics}")
            return
        
        # Record
        self._history.add_snapshot(**metrics)
    
    except Exception as e:
        self._log_error(f"Failed to record: {e}", exc_info=True)

def _validate_metrics(self, metrics: Dict) -> bool:
    if not metrics:
        return False
    
    cpu = metrics.get('cpu', 0)
    gpu = metrics.get('gpu', 0)
    ram = metrics.get('memory', 0)
    
    # Range check
    if not (0 <= cpu <= 100 and 0 <= gpu <= 100 and 0 <= ram <= 100):
        return False
    
    return True
```

### Pattern 4: Status Reporting

```python
def get_status(self) -> Dict[str, Any]:
    try:
        return {
            'active': self._active,
            'component_a_available': self._component_a is not None,
            'component_b_available': self._component_b is not None,
            'error_count': self._error_count,
            'data_points': self._get_data_count(),
            'last_update': self._last_update_time,
        }
    
    except Exception as e:
        self._log_error(f"Failed to get status: {e}")
        return {'error': str(e)}
```

## Testing

### Test Error Recovery

```python
def test_worker_error_recovery(self):
    # Create monitor that throws errors first, then works
    class RecoveringMonitor:
        def __init__(self):
            self.call_count = 0
        
        def get_current_metrics(self):
            self.call_count += 1
            if self.call_count < 3:
                raise Exception("Temporary error!")
            return {'cpu': 50, 'gpu': 60, 'memory': 40}
    
    integration = MonitoringIntegration(monitor=RecoveringMonitor())
    integration.start()
    
    # Wait for recovery
    time.sleep(5)
    
    # Should still be active
    self.assertTrue(integration.is_active())
```

### Test Graceful Degradation

```python
def test_missing_components(self):
    # Should work without optional components
    integration = MonitoringIntegration(
        monitor=None,  # Missing
        data_bus=None  # Missing
    )
    
    result = integration.start()
    self.assertTrue(result)
```

### Test Status Reporting

```python
def test_status_reporting(self):
    integration = MonitoringIntegration(monitor=mock_monitor)
    integration.start()
    
    status = integration.get_status()
    
    self.assertIn('active', status)
    self.assertIn('error_count', status)
    self.assertTrue(status['active'])
```

## Best Practices

### DO

✅ **Return bool for start/stop**
```python
def start(self) -> bool:
    # Returns False on error
    pass
```

✅ **Validate data before processing**
```python
if self._validate(data):
    self._process(data)
else:
    self._log_warning("Invalid data")
```

✅ **Track error frequency**
```python
if self._error_count >= self._max_errors:
    self.stop()
```

✅ **Provide status reporting**
```python
status = component.get_status()
if status['error_count'] > 5:
    alert_user()
```

### DON'T

❌ **Don't let worker threads crash silently**
```python
# BAD
def _worker(self):
    while True:
        self._process()  # Unhandled exceptions!

# GOOD
def _worker(self):
    while self._active:
        try:
            self._process()
        except Exception as e:
            self._handle_error(e)
```

❌ **Don't ignore component failures**
```python
# BAD
integration.start()  # Ignoring return value

# GOOD
if not integration.start():
    logger.error("Integration failed to start")
    use_fallback_mode()
```

❌ **Don't crash on missing dependencies**
```python
# BAD
def __init__(self, monitor, bus):
    self._monitor = monitor
    metrics = monitor.get_metrics()  # Crashes if None!

# GOOD
def __init__(self, monitor, bus):
    self._monitor = monitor
    if monitor:
        metrics = monitor.get_metrics()
```

## See Also

- [Core Components Error Handling](ERROR_HANDLING.md)
- [Logging System](LOGGING.md)
- [Testing Guide](../tests/README.md)
