# Service Layer Error Handling

**Version:** 0.3.5n (Package 3.9a, Stage 7.7b.5/7.7)

## Overview

Error handling in service layer components that provide core functionality.

## Components

### PerformanceMonitor

Advanced performance analytics service with comprehensive error handling.

#### Error Scenarios

**1. Manager Interface Errors**
```python
try:
    cpu_load = manager.get_cpu_load()
except Exception as e:
    logger.error(f"Failed to get CPU load: {e}")
    cpu_load = 0.0  # Fallback
```

**2. Invalid Data Values**
```python
# Validate and clamp
cpu_load = self._validate_load_value(cpu_load, "CPU load")

# Values outside 0-100 are clamped
if value < 0 or value > 100:
    return max(0.0, min(100.0, value))
```

**3. Insufficient Data**
```python
def get_performance_score(self):
    if not self._snapshots:
        return 0.0  # No data available
    
    # Calculate score...
```

**4. Calculation Errors**
```python
try:
    correlation = np.corrcoef(cpu_loads, fps_values)[0, 1]
    if not np.isnan(correlation):
        self._cpu_fps_correlation = correlation
except (ValueError, FloatingPointError, np.linalg.LinAlgError) as e:
    logger.warning(f"Correlation calculation error: {e}")
```

**5. Error Threshold**
```python
# Track errors over time
if self._error_count >= self._max_errors:
    logger.error("Too many errors, monitor disabled")
    return False
```

#### Error Recovery

**Automatic Recovery:**
- Invalid data values are clamped to valid ranges
- Missing data uses fallback values (0.0)
- Calculation errors are logged and skipped
- Error counter resets after 60 seconds
- Returns last known good values on error

**Manual Recovery:**
```python
# Reset monitor
monitor.reset()

# Check status
status = monitor.get_status()
if status['error_count'] > 5:
    # Investigate issues
    pass
```

## Error Handling Patterns

### Pattern 1: Graceful Data Collection

```python
def update(self) -> bool:
    try:
        # Collect each metric separately
        try:
            cpu_load = manager.get_cpu_load()
            cpu_load = self._validate_load_value(cpu_load, "CPU load")
        except Exception as e:
            logger.error(f"CPU load error: {e}")
            cpu_load = 0.0  # Fallback
        
        try:
            gpu_load = manager.get_gpu_load()
            gpu_load = self._validate_load_value(gpu_load, "GPU load")
        except Exception as e:
            logger.error(f"GPU load error: {e}")
            gpu_load = 0.0  # Fallback
        
        # Create snapshot with potentially partial data
        snapshot = PerformanceSnapshot(...)
        self._snapshots.append(snapshot)
        
        return True
    
    except Exception as e:
        logger.error(f"Update failed: {e}", exc_info=True)
        return False
```

### Pattern 2: Data Validation

```python
def _validate_load_value(self, value: float, name: str) -> float:
    try:
        # Type check
        if not isinstance(value, (int, float)):
            logger.warning(f"Invalid {name} type: {type(value)}")
            return 0.0
        
        # Range check
        if value < 0 or value > 100:
            logger.warning(f"Invalid {name} range: {value}")
            return max(0.0, min(100.0, value))  # Clamp
        
        return float(value)
    
    except Exception as e:
        logger.error(f"Validation error for {name}: {e}")
        return 0.0
```

### Pattern 3: Safe Calculations

```python
def _update_correlations(self):
    try:
        # Calculation
        correlation = np.corrcoef(cpu_loads, fps_values)[0, 1]
        
        # Validate result
        if not np.isnan(correlation) and not np.isinf(correlation):
            self._cpu_fps_correlation = correlation
    
    except (ValueError, FloatingPointError, np.linalg.LinAlgError) as e:
        logger.warning(f"Correlation error: {e}")
        # Keep previous value
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
```

### Pattern 4: Fallback Values

```python
def get_performance_score(self) -> float:
    try:
        if not self._snapshots:
            return 0.0  # No data
        
        # Calculate score
        score = calculate_score()
        self._last_score = score  # Save for fallback
        return score
    
    except Exception as e:
        logger.error(f"Score calculation failed: {e}")
        return self._last_score  # Return last known score
```

### Pattern 5: Status Reporting

```python
def get_status(self) -> Dict[str, Any]:
    try:
        return {
            'active': True,
            'snapshot_count': len(self._snapshots),
            'baseline_established': self._baseline_established,
            'error_count': self._error_count,
            'last_score': self._last_score,
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        return {'error': str(e)}
```

## Testing

### Test Invalid Data

```python
def test_invalid_load_values(self):
    # Set invalid values
    manager.cpu_load = 150  # Over 100
    manager.gpu_load = -50  # Negative
    
    result = monitor.update()
    self.assertTrue(result)  # Should handle gracefully
```

### Test Interface Errors

```python
def test_manager_interface_error(self):
    class ErrorManager:
        def get_cpu_load(self):
            raise Exception("Interface error!")
    
    monitor = PerformanceMonitor(ErrorManager(), bus)
    result = monitor.update()
    
    # Should handle error
    self.assertTrue(result)
```

### Test Insufficient Data

```python
def test_score_without_data(self):
    monitor = PerformanceMonitor(manager, bus)
    score = monitor.get_performance_score()
    self.assertEqual(score, 0.0)
```

### Test Recovery

```python
def test_reset_recovery(self):
    # Cause errors
    for _ in range(5):
        monitor.update()  # With errors
    
    # Reset
    monitor.reset()
    
    # Check cleared
    status = monitor.get_status()
    self.assertEqual(status['error_count'], 0)
```

## Best Practices

### DO

✅ **Validate all input data**
```python
value = self._validate_load_value(value, "CPU load")
```

✅ **Collect data in isolation**
```python
try:
    cpu = manager.get_cpu_load()
except Exception:
    cpu = 0.0

try:
    gpu = manager.get_gpu_load()
except Exception:
    gpu = 0.0
```

✅ **Provide fallback values**
```python
if not snapshots:
    return 0.0

try:
    return calculate()
except Exception:
    return last_known_value
```

✅ **Track error frequency**
```python
if error_count >= max_errors:
    logger.error("Too many errors, disabling")
    return False
```

✅ **Status reporting**
```python
status = monitor.get_status()
if status['error_count'] > 5:
    investigate_issues()
```

### DON'T

❌ **Don't fail on single metric error**
```python
# BAD
cpu = manager.get_cpu_load()  # Crashes entire update!

# GOOD
try:
    cpu = manager.get_cpu_load()
except Exception as e:
    logger.error(f"CPU load error: {e}")
    cpu = 0.0  # Continue with fallback
```

❌ **Don't assume valid data**
```python
# BAD
score = cpu / 100  # What if cpu is 500?

# GOOD
cpu = max(0, min(100, cpu))  # Clamp first
score = cpu / 100
```

❌ **Don't ignore calculation errors**
```python
# BAD
corr = np.corrcoef(a, b)[0, 1]  # Can raise or return NaN!

# GOOD
try:
    corr = np.corrcoef(a, b)[0, 1]
    if not np.isnan(corr):
        self._correlation = corr
except Exception as e:
    logger.warning(f"Correlation error: {e}")
```

❌ **Don't return None on error**
```python
# BAD
def get_score():
    try:
        return calculate()
    except Exception:
        return None  # Caller must check for None!

# GOOD
def get_score() -> float:
    try:
        return calculate()
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0.0  # Always return float
```

## Service Lifecycle

### Initialization

```python
try:
    monitor = PerformanceMonitor(manager, bus)
    logger.info("Monitor initialized")
except Exception as e:
    logger.error(f"Initialization failed: {e}")
    # Use fallback or disable feature
```

### Operation

```python
while active:
    try:
        if not monitor.update():
            logger.warning("Update failed")
            # Could retry or pause
        
        time.sleep(interval)
    
    except Exception as e:
        logger.error(f"Operation error: {e}")
        # Decide: continue, retry, or stop
```

### Shutdown

```python
try:
    monitor.reset()
    logger.info("Monitor shutdown complete")
except Exception as e:
    logger.error(f"Shutdown error: {e}")
    # Still exit gracefully
```

## Error Messages

### For Logs (Technical)

```python
logger.error(
    f"Failed to get {metric} from manager: {error}",
    component="PerformanceMonitor",
    exc_info=True
)
```

**Include:**
- Which metric/operation failed
- Error details
- Stack trace
- Context (component name)

### For Users (Friendly)

```python
show_notification(
    "Performance monitoring unavailable",
    "Some performance metrics cannot be collected. "
    "Check logs for details."
)
```

**Include:**
- What's not working
- Impact on functionality
- Where to find details

## See Also

- [Core Error Handling](ERROR_HANDLING.md)
- [Integration Error Handling](INTEGRATION_ERROR_HANDLING.md)
- [UI Error Handling](UI_ERROR_HANDLING.md)
- [Logging System](LOGGING.md)
