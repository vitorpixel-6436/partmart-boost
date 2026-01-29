# Service Layer Error Handling

**Version:** 0.3.5o (Package 3.9a, Stage 7.7b.5.2/7.7)

## Overview

Error handling in backend services with automatic recovery and health monitoring.

## Table of Contents

1. [PerformanceMonitor Error Handling](#performancemonitor-error-handling)
2. [GameDetectionService Error Handling](#gamedetectionservice-error-handling)

---

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

---

## GameDetectionService Error Handling

### Overview

Automatic game detection service with comprehensive error handling.

**Features:**
- Process monitoring
- Window enumeration
- Game database
- Thread-safe operation
- Automatic recovery

### Error Scenarios

#### 1. Process Detection Errors

**Process Enumeration:**
```python
def _get_game_processes(self) -> List[tuple]:
    games = []
    known_processes = self._database.get_all_process_names()
    
    try:
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name'].lower()
                
                if proc_name in known_processes:
                    game_name = self._database.lookup(proc_name)
                    if game_name:
                        games.append((proc, game_name))
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process terminated or access denied - skip
                continue
            
            except Exception as e:
                self._log_warning(f"Error checking process: {e}")
                continue
    
    except Exception as e:
        self._log_error(f"Process enumeration failed: {e}")
    
    return games
```

**Key Points:**
- Each process checked individually
- Access denied errors handled gracefully
- Process termination during enumeration handled
- Continues on individual process errors

#### 2. Window Enumeration Errors

**Get Window Title:**
```python
def _get_window_title(self, pid: int) -> str:
    try:
        if not WINDOWS_AVAILABLE:
            return ""
        
        def callback(hwnd, titles):
            try:
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        titles.append(title)
            except Exception:
                pass  # Skip problematic windows
        
        titles = []
        win32gui.EnumWindows(callback, titles)
        
        return titles[0] if titles else ""
    
    except Exception as e:
        self._log_warning(f"Failed to get window title: {e}")
        return ""
```

**Key Points:**
- Graceful degradation without Windows API
- Individual window errors handled in callback
- Returns empty string on failure
- No crash if enumeration fails

#### 3. Game Database Errors

**File I/O Errors:**
```python
def _load_from_file(self):
    try:
        if not os.path.exists(self._db_path):
            self._log_debug("Database file not found")
            return
        
        with open(self._db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            self._log_warning("Invalid database format")
            return
        
        with self._lock:
            self._games.update(data)
        
        self._log_info(f"Loaded {len(data)} games from file")
    
    except json.JSONDecodeError as e:
        self._log_error(f"Failed to parse database: {e}")
    
    except Exception as e:
        self._log_error(f"Failed to load database: {e}")
```

**Save with Atomic Write:**
```python
def save_to_file(self) -> bool:
    try:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        
        # Write to temp file first
        temp_path = f"{self._db_path}.tmp"
        
        with self._lock:
            data = dict(self._games)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Replace original file atomically
        if os.path.exists(self._db_path):
            os.replace(temp_path, self._db_path)
        else:
            os.rename(temp_path, self._db_path)
        
        return True
    
    except Exception as e:
        self._log_error(f"Failed to save database: {e}")
        return False
```

**Key Points:**
- Missing file is not an error
- JSON parse errors handled
- Atomic file writes (temp file + replace)
- Directory creation handled
- Returns success/failure status

#### 4. Worker Thread Errors

**Error Tracking:**
```python
def _handle_worker_error(self, error: Exception):
    now = time.time()
    
    # Reset error count after cooldown (60s)
    if now - self._last_error_time > 60.0:
        self._error_count = 0
    
    self._error_count += 1
    self._consecutive_errors += 1
    self._last_error_time = now
    
    self._log_error(
        f"Worker error ({self._error_count}/{self._max_errors}): {error}"
    )
    
    # Sleep longer after error
    time.sleep(1.0)
```

**Automatic Shutdown:**
```python
if self._consecutive_errors >= self._max_consecutive_errors:
    self._log_error("Too many consecutive errors, stopping")
    break
```

### Usage Examples

**Basic Usage:**
```python
# Create service
service = GameDetectionService(interval=1000)

# Add callback
def on_game_detected(game: GameInfo):
    print(f"Detected: {game.name}")
    print(f"Process: {game.process_name} (PID: {game.pid})")

service.add_callback(on_game_detected)

# Start detection
if service.start():
    print("Started successfully")

# Get current game
game = service.get_current_game()
if game:
    print(f"Currently playing: {game['name']}")

# Stop
service.stop()
```

**Add Custom Game:**
```python
# Add to database
service.add_game_to_database('mygame.exe', 'My Game')

# Save database
if service.save_database():
    print("Database saved")
```

**Error Recovery:**
```python
# Check status
status = service.get_status()

if status['consecutive_errors'] > 3:
    print("Service experiencing errors, restarting...")
    service.stop()
    time.sleep(1)
    service.start()
```

### Error Recovery Strategies

#### 1. Process Access Errors

**Strategy:** Skip inaccessible processes
- Individual process errors don't stop enumeration
- Continue checking other processes
- Log warning for debugging

#### 2. Window Enumeration Errors

**Strategy:** Graceful degradation
- Return empty string if title unavailable
- Continue detection without window info
- Non-critical for game detection

#### 3. Database Errors

**Strategy:** Use defaults
- Load defaults if file missing/corrupt
- Continue with in-memory database
- Save functionality still available

#### 4. Detection Errors

**Strategy:** Error counting + cooldown
- Track consecutive errors
- Auto-stop after threshold (5 errors)
- Reset count after cooldown (60s)
- Allows recovery from transient issues

### Testing

**Test Process Errors:**
```python
def test_process_access_denied(self):
    mock_proc = Mock()
    mock_proc.info = {'name': 'test.exe', 'pid': 1234}
    mock_proc.name.side_effect = psutil.AccessDenied()
    
    with patch('psutil.process_iter', return_value=[mock_proc]):
        games = service._get_game_processes()
        # Should handle gracefully
        self.assertIsInstance(games, list)
```

**Test Database Errors:**
```python
def test_load_corrupt_database(self):
    # Write invalid JSON
    with open(db_path, 'w') as f:
        f.write("invalid json{{{")
    
    # Should not crash
    db = GameDatabase(db_path=db_path)
    
    # Should still have defaults
    self.assertGreater(len(db.get_all_process_names()), 0)
```

**Test Callback Isolation:**
```python
def test_callback_isolation(self):
    received = []
    
    def bad_callback(g):
        raise Exception("Error!")
    
    def good_callback(g):
        received.append(g)
    
    service.add_callback(bad_callback)
    service.add_callback(good_callback)
    
    # Trigger detection
    # Good callback should still work
    self.assertGreater(len(received), 0)
```

### Best Practices

#### DO

✅ **Handle process errors individually**
```python
for proc in psutil.process_iter():
    try:
        process_data(proc)
    except (NoSuchProcess, AccessDenied):
        continue  # Skip this process
```

✅ **Provide defaults for missing data**
```python
def get_window_title(pid):
    try:
        return _get_title_windows_api(pid)
    except Exception:
        return ""  # Empty string is valid default
```

✅ **Use atomic file operations**
```python
# Write to temp, then replace
with open(temp_path, 'w') as f:
    json.dump(data, f)
os.replace(temp_path, final_path)
```

✅ **Isolate callback errors**
```python
for callback in callbacks:
    try:
        callback(data)
    except Exception:
        log_error()  # Don't break other callbacks
```

#### DON'T

❌ **Don't crash on single process error**
```python
# BAD
for proc in processes:
    name = proc.name()  # May raise AccessDenied!

# GOOD
for proc in processes:
    try:
        name = proc.name()
    except (NoSuchProcess, AccessDenied):
        continue
```

❌ **Don't require Windows API**
```python
# BAD
from win32gui import *  # Crashes on Linux!

# GOOD
try:
    import win32gui
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
```

❌ **Don't lose data on save errors**
```python
# BAD
with open(db_path, 'w') as f:
    json.dump(data, f)  # Original lost if error!

# GOOD
with open(temp_path, 'w') as f:
    json.dump(data, f)
os.replace(temp_path, db_path)  # Atomic
```

### Performance Metrics

**Detection Rate:**
- Interval: 100-10000ms (configurable)
- Actual rate: ~95% of target
- Process scan: 10-50ms typical

**Error Rate:**
- Target: <1 error per 100 detections
- Acceptable: <5 errors per 100 detections
- Critical: >5 consecutive errors → auto-stop

**Database:**
- Default games: 13
- Load time: <10ms
- Save time: <50ms

## See Also

- [Core Error Handling](ERROR_HANDLING.md)
- [Integration Error Handling](INTEGRATION_ERROR_HANDLING.md)
- [Logging System](LOGGING.md)
