# Service Layer Error Handling

**Version:** 0.3.5n (Package 3.9a, Stage 7.7b.5.1/7.7)

## Overview

Error handling in backend services with automatic recovery and health monitoring.

## PerformanceMonitor Error Handling

### Overview

Real-time hardware monitoring service with comprehensive error handling.

**Features:**
- CPU, GPU, RAM, FPS monitoring
- Temperature monitoring
- Metrics validation
- Automatic recovery
- Error tracking
- Callback system

### Error Scenarios

#### 1. Hardware Access Errors

**CPU Reading Failure:**
```python
def _get_cpu_usage(self) -> float:
    try:
        cpu = psutil.cpu_percent(interval=None)
        return max(0.0, min(100.0, cpu))
    
    except Exception as e:
        self._log_warning(f"CPU usage failed: {e}")
        # Return last known value
        if self._last_valid_metrics:
            return self._last_valid_metrics.cpu
        return 0.0
```

**GPU Reading Failure:**
```python
def _get_gpu_usage(self) -> float:
    try:
        if not GPU_AVAILABLE:
            return 0.0
        
        gpus = GPUtil.getGPUs()
        if gpus:
            return max(0.0, min(100.0, gpus[0].load * 100))
        return 0.0
    
    except Exception as e:
        self._log_warning(f"GPU usage failed: {e}")
        # Return last known value or 0
        if self._last_valid_metrics:
            return self._last_valid_metrics.gpu
        return 0.0
```

#### 2. Invalid Metrics

**Validation:**
```python
class PerformanceMetrics:
    def is_valid(self) -> bool:
        return (
            0 <= self.cpu <= 100 and
            0 <= self.gpu <= 100 and
            0 <= self.ram <= 100 and
            0 <= self.fps <= 500 and
            0 <= self.cpu_temp <= 150 and
            0 <= self.gpu_temp <= 150 and
            0 <= self.score <= 100
        )
```

**Handling:**
```python
if metrics and metrics.is_valid():
    self._current_metrics = metrics
    self._last_valid_metrics = metrics
    self._consecutive_errors = 0
else:
    # Use last valid metrics
    self._handle_invalid_metrics(metrics)
```

#### 3. Worker Thread Errors

**Error Tracking:**
```python
def _handle_worker_error(self, error: Exception):
    now = time.time()
    
    # Reset error count after cooldown
    if now - self._last_error_time > 60.0:
        self._error_count = 0
    
    self._error_count += 1
    self._consecutive_errors += 1
    self._last_error_time = now
    
    self._log_error(f"Worker error ({self._error_count}/{self._max_errors}): {error}")
    
    # Sleep longer after error
    time.sleep(1.0)
```

**Automatic Shutdown:**
```python
if self._consecutive_errors >= self._max_consecutive_errors:
    self._log_error("Too many consecutive errors, stopping")
    break
```

#### 4. Callback Errors

**Error Isolation:**
```python
def _notify_callbacks(self, metrics: PerformanceMetrics):
    for callback in self._callbacks:
        try:
            callback(metrics)
        except Exception as e:
            # Don't let one bad callback break others
            self._log_error(f"Callback error: {e}", exc_info=True)
```

### Usage Examples

**Basic Usage:**
```python
# Create monitor
monitor = PerformanceMonitor(interval=100)

# Add callback
def on_metrics(metrics: PerformanceMetrics):
    print(f"CPU: {metrics.cpu}%, GPU: {metrics.gpu}%")

monitor.add_callback(on_metrics)

# Start monitoring
if monitor.start():
    print("Started successfully")
else:
    print("Failed to start")

# Get current metrics
metrics = monitor.get_current_metrics()
if metrics:
    print(f"Score: {metrics['score']}")

# Stop
monitor.stop()
```

**Error Recovery:**
```python
# Check status
status = monitor.get_status()

if status['consecutive_errors'] > 3:
    print("Monitor experiencing errors, restarting...")
    monitor.stop()
    time.sleep(1)
    monitor.start()
```

**Health Monitoring:**
```python
def check_health():
    if not monitor.is_running():
        print("Monitor not running!")
        return False
    
    status = monitor.get_status()
    
    if status['error_count'] > 10:
        print("Too many errors!")
        return False
    
    if not status['has_metrics']:
        print("No metrics available!")
        return False
    
    return True
```

### Error Recovery Strategies

#### 1. Automatic Recovery

**Last Known Value:**
- Hardware reading fails → return last valid value
- Prevents metric gaps
- Smooth degradation

**Error Cooldown:**
- Reset error count after 60 seconds
- Prevents permanent error state
- Allows recovery from transient issues

**Automatic Shutdown:**
- Stop after too many consecutive errors
- Prevents infinite error loops
- Protects system resources

#### 2. Manual Recovery

**Restart Monitor:**
```python
def restart_monitor():
    try:
        monitor.stop()
        time.sleep(1)
        
        if monitor.start():
            print("Monitor restarted")
            return True
        else:
            print("Restart failed")
            return False
    
    except Exception as e:
        print(f"Restart error: {e}")
        return False
```

**Clear Error State:**
```python
# Stop and create new instance
old_monitor.stop()
new_monitor = PerformanceMonitor(interval=100)
new_monitor.start()
```

### Testing

**Test Error Recovery:**
```python
def test_cpu_error_recovery(self):
    with patch('psutil.cpu_percent') as mock_cpu:
        # Simulate error
        mock_cpu.side_effect = Exception("CPU error!")
        
        # Should not crash
        cpu = monitor._get_cpu_usage()
        
        # Should return fallback
        self.assertGreaterEqual(cpu, 0.0)
```

**Test Invalid Metrics:**
```python
def test_invalid_metrics(self):
    metrics = PerformanceMetrics(
        cpu=200.0,  # Invalid!
        gpu=50.0,
        ram=40.0,
        fps=60.0,
        cpu_temp=50.0,
        gpu_temp=70.0,
        score=85.0,
        timestamp=time.time()
    )
    
    # Should be rejected
    self.assertFalse(metrics.is_valid())
```

**Test Callback Isolation:**
```python
def test_callback_isolation(self):
    received = []
    
    def bad_callback(m):
        raise Exception("Error!")
    
    def good_callback(m):
        received.append(m)
    
    monitor.add_callback(bad_callback)
    monitor.add_callback(good_callback)
    
    monitor.start()
    time.sleep(0.5)
    monitor.stop()
    
    # Good callback should still work
    self.assertGreater(len(received), 0)
```

### Best Practices

#### DO

✅ **Validate all metrics**
```python
if metrics and metrics.is_valid():
    self._process(metrics)
else:
    self._handle_invalid(metrics)
```

✅ **Track error frequency**
```python
self._error_count += 1
if self._error_count >= self._max_errors:
    self.stop()
```

✅ **Use last known values**
```python
except Exception as e:
    if self._last_valid_metrics:
        return self._last_valid_metrics.cpu
    return 0.0
```

✅ **Isolate callback errors**
```python
for callback in self._callbacks:
    try:
        callback(data)
    except Exception:
        # Log but continue
        pass
```

#### DON'T

❌ **Don't crash on hardware errors**
```python
# BAD
cpu = psutil.cpu_percent()  # May fail!

# GOOD
try:
    cpu = psutil.cpu_percent()
except Exception:
    cpu = last_known_value
```

❌ **Don't accept invalid values**
```python
# BAD
self._cpu = value  # No validation!

# GOOD
if 0 <= value <= 100:
    self._cpu = value
else:
    log_warning("Invalid value")
```

❌ **Don't run indefinitely with errors**
```python
# BAD
while True:
    try:
        collect()  # Fails every time!
    except:
        pass  # Infinite error loop!

# GOOD
while self._error_count < max_errors:
    try:
        collect()
    except:
        self._error_count += 1
```

### Monitoring State Machine

```
STOPPED → STARTING → RUNNING → STOPPING → STOPPED
            ↓
          ERROR
```

**State Transitions:**
- STOPPED: Initial state, can be started
- STARTING: Transitioning to running
- RUNNING: Actively monitoring
- STOPPING: Gracefully stopping
- ERROR: Error occurred, must be restarted

### Performance Metrics

**Update Rate:**
- Interval: 10-5000ms (configurable)
- Actual rate: ~90-95% of target
- Variance: ±10ms typical

**Error Rate:**
- Target: <1 error per 1000 updates
- Acceptable: <5 errors per 1000 updates
- Critical: >10 consecutive errors

**Recovery Time:**
- Single error: Immediate (next update)
- Multiple errors: 1 second delay
- Restart: 1-2 seconds

## See Also

- [Core Error Handling](ERROR_HANDLING.md)
- [Integration Error Handling](INTEGRATION_ERROR_HANDLING.md)
- [Logging System](LOGGING.md)
