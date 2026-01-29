# Backend-Frontend Communication Guide

**Version:** 0.3.5d (Package 3.9a)  
**Target Audience:** Developers  
**Updated:** 2026-01-29

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Frontend Examples](#frontend-examples)
3. [Backend Examples](#backend-examples)
4. [Command Guide](#command-guide)
5. [Query Guide](#query-guide)
6. [Event Guide](#event-guide)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Quick Start

### Step 1: Get Backend Bridge

```python
from backend_bridge import BackendBridge

# Get singleton instance
bridge = BackendBridge.get_instance()
```

### Step 2: Execute Command

```python
from command_system import StartMonitoringCommand

# Create command
command = StartMonitoringCommand(interval=100)

# Execute
result = bridge.execute_command(command)

if result.success:
    print("Monitoring started!")
else:
    print(f"Error: {result.error}")
```

### Step 3: Subscribe to Events

```python
def on_metrics_updated(event_type, data):
    print(f"New metrics: {data}")

# Subscribe
bridge.subscribe('metrics_updated', on_metrics_updated)
```

---

## Frontend Examples

### Example 1: Dashboard Widget

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from backend_bridge import BackendBridge
from command_system import StartMonitoringCommand, StopMonitoringCommand
from query_system import QueryBuilder

class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Get bridge
        self.bridge = BackendBridge.get_instance()
        
        # Subscribe to events
        self.bridge.subscribe('metrics_updated', self._on_metrics)
        
        # Connect Qt signals
        if self.bridge.qt_signals:
            self.bridge.qt_signals.data_updated.connect(self._on_data_updated)
            self.bridge.qt_signals.error_occurred.connect(self._on_error)
        
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        
        # Labels
        self.fps_label = QLabel("FPS: --")
        self.cpu_label = QLabel("CPU: --")
        self.gpu_label = QLabel("GPU: --")
        
        layout.addWidget(self.fps_label)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.gpu_label)
        
        # Buttons
        start_btn = QPushButton("Start Monitoring")
        start_btn.clicked.connect(self._start_monitoring)
        layout.addWidget(start_btn)
        
        stop_btn = QPushButton("Stop Monitoring")
        stop_btn.clicked.connect(self._stop_monitoring)
        layout.addWidget(stop_btn)
    
    def _start_monitoring(self):
        """Start monitoring via bridge"""
        command = StartMonitoringCommand(interval=100)
        result = self.bridge.execute_command(command)
        
        if not result.success:
            # Show error to user
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", result.error)
    
    def _stop_monitoring(self):
        """Stop monitoring via bridge"""
        command = StopMonitoringCommand()
        result = self.bridge.execute_command(command)
    
    def _on_metrics(self, event_type, data):
        """Handle metrics event"""
        print(f"Metrics: {data}")
    
    def _on_data_updated(self, data_type, data):
        """Handle Qt signal (thread-safe)"""
        if data_type == 'performance_metrics':
            self.fps_label.setText(f"FPS: {data.get('fps', '--')}")
            self.cpu_label.setText(f"CPU: {data.get('cpu', '--')}%")
            self.gpu_label.setText(f"GPU: {data.get('gpu', '--')}%")
    
    def _on_error(self, component, error):
        """Handle error signal"""
        print(f"Error in {component}: {error}")
```

### Example 2: Performance Widget with Queries

```python
from PyQt6.QtWidgets import QWidget
from backend_bridge import BackendBridge
from query_system import QueryBuilder

class PerformanceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.bridge = BackendBridge.get_instance()
    
    def get_recent_metrics(self):
        """Get recent performance metrics"""
        # Build query
        query = QueryBuilder() \
            .select(['fps', 'cpu', 'gpu', 'memory']) \
            .filter({'timestamp': '>1h'}) \
            .order_by('timestamp', desc=True) \
            .limit(100) \
            .build()
        
        # Execute query
        result = self.bridge.query_data('performance_metrics', query)
        
        if result.success:
            # Display data
            self._display_metrics(result.data)
            print(f"Retrieved {result.row_count} rows")
        else:
            print(f"Query error: {result.error}")
    
    def get_average_fps(self):
        """Get average FPS"""
        query = QueryBuilder() \
            .select(['fps']) \
            .filter({'timestamp': '>10m'}) \
            .build()
        
        result = self.bridge.query_data('performance_metrics', query)
        
        if result.success and result.data:
            fps_values = [m['fps'] for m in result.data]
            avg_fps = sum(fps_values) / len(fps_values)
            print(f"Average FPS: {avg_fps:.1f}")
        
        return avg_fps
```

### Example 3: Settings Widget

```python
from PyQt6.QtWidgets import QWidget, QCheckBox, QComboBox
from backend_bridge import BackendBridge
from command_system import UpdateSettingsCommand

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.bridge = BackendBridge.get_instance()
        
        # Subscribe to settings updates
        self.bridge.subscribe('settings_updated', self._on_settings_updated)
    
    def apply_settings(self):
        """Apply settings via bridge"""
        # Collect settings from UI
        settings = {
            'quality': self.quality_combo.currentText(),
            'frame_gen_enabled': self.framegen_check.isChecked(),
            'upscaling_enabled': self.upscaling_check.isChecked(),
        }
        
        # Create command
        command = UpdateSettingsCommand(settings)
        
        # Execute
        result = self.bridge.execute_command(command)
        
        if result.success:
            print("Settings applied successfully")
        else:
            print(f"Failed to apply settings: {result.error}")
    
    def _on_settings_updated(self, event_type, data):
        """Handle settings update event"""
        print(f"Settings updated: {data}")
        # Refresh UI if needed
```

---

## Backend Examples

### Example 1: Register Command Handler

```python
from backend_bridge import BackendBridge, Command, CommandResult

class PerformanceMonitor:
    def __init__(self):
        # Get bridge
        bridge = BackendBridge.get_instance()
        
        # Register handlers
        bridge.register_command_handler('start_monitoring', self._handle_start)
        bridge.register_command_handler('stop_monitoring', self._handle_stop)
    
    def _handle_start(self, command: Command) -> CommandResult:
        """Handle start monitoring command"""
        try:
            # Get parameters
            interval = command.params.get('interval', 100)
            metrics = command.params.get('metrics', [])
            
            # Start monitoring
            self.start(interval, metrics)
            
            # Publish event
            bridge = BackendBridge.get_instance()
            bridge.publish_event('monitoring_started', {
                'interval': interval,
                'metrics': metrics,
            })
            
            return CommandResult(
                request_id=command.request_id,
                success=True,
                data={'status': 'started'}
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    def _handle_stop(self, command: Command) -> CommandResult:
        """Handle stop monitoring command"""
        try:
            self.stop()
            
            return CommandResult(
                request_id=command.request_id,
                success=True
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
```

### Example 2: Publish Data Updates

```python
from backend_bridge import BackendBridge
import time

class PerformanceMonitor:
    def __init__(self):
        self.bridge = BackendBridge.get_instance()
        self.running = False
    
    def collect_metrics(self):
        """Collect and publish metrics"""
        while self.running:
            # Collect metrics
            metrics = {
                'fps': self._get_fps(),
                'cpu': self._get_cpu_usage(),
                'gpu': self._get_gpu_usage(),
                'memory': self._get_memory_usage(),
                'timestamp': time.time(),
            }
            
            # Publish via bridge
            self.bridge.publish_data('performance_metrics', metrics)
            
            # Also publish event
            self.bridge.publish_event('metrics_updated', metrics)
            
            time.sleep(0.1)  # 100ms
```

### Example 3: Register Query Handler

```python
from backend_bridge import BackendBridge, QueryResult

class MetricsDatabase:
    def __init__(self):
        bridge = BackendBridge.get_instance()
        bridge.register_query_handler('performance_metrics', self._handle_query)
        
        self.metrics_history = []
    
    def _handle_query(self, params: dict) -> QueryResult:
        """Handle metrics query"""
        try:
            # Parse query parameters
            select_fields = params.get('select', [])
            filters = params.get('filter', {})
            limit = params.get('limit')
            
            # Filter data
            filtered_data = self._filter_metrics(filters)
            
            # Limit results
            if limit:
                filtered_data = filtered_data[:limit]
            
            return QueryResult(
                success=True,
                data=filtered_data,
                row_count=len(filtered_data)
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def _filter_metrics(self, filters):
        """Filter metrics based on conditions"""
        # Implementation...
        return self.metrics_history
```

---

## Command Guide

### Available Commands

| Command | Purpose | Parameters |
|---------|---------|------------|
| `StartMonitoringCommand` | Start monitoring | `interval`, `metrics` |
| `StopMonitoringCommand` | Stop monitoring | None |
| `UpdateSettingsCommand` | Update settings | `settings` |
| `InstallOptiScalerCommand` | Install OptiScaler | `version`, `force` |
| `GetMetricsCommand` | Get metrics | `time_range`, `limit` |
| `ClearHistoryCommand` | Clear history | None |
| `ExportDataCommand` | Export data | `file_path`, `format` |
| `ApplyProfileCommand` | Apply profile | `profile_name` |

### Creating Custom Commands

```python
from backend_bridge import Command
from dataclasses import dataclass

@dataclass
class MyCustomCommand(Command):
    """My custom command"""
    
    def __init__(self, param1: str, param2: int):
        super().__init__(
            command_type='my_custom_command',
            params={
                'param1': param1,
                'param2': param2,
            }
        )
```

---

## Query Guide

### Query Builder Methods

```python
query = QueryBuilder() \
    .select(['field1', 'field2'])  # Select fields
    .filter({'field': 'value'})     # Filter conditions
    .order_by('field', desc=True)   # Sort order
    .limit(100)                     # Limit results
    .offset(50)                     # Offset (pagination)
    .build()                        # Build query dict
```

### Filter Operators

```python
# Equals
.filter({'status': 'active'})

# Greater than
.filter({'fps': '>60'})

# Less than
.filter({'cpu': '<80'})

# Range
.filter({'timestamp': '> 1h'})

# Multiple conditions
.filter({'status': 'active', 'fps': '>60'})
```

---

## Event Guide

### Available Events

| Event | Triggered When | Data |
|-------|----------------|------|
| `metrics_updated` | New metrics available | `{fps, cpu, gpu, ...}` |
| `command_completed` | Command finishes | `{request_id, success}` |
| `settings_updated` | Settings changed | `{settings}` |
| `monitoring_started` | Monitoring starts | `{interval, metrics}` |
| `monitoring_stopped` | Monitoring stops | `{}` |
| `error_occurred` | Error happens | `{component, error}` |

### Subscribing to Events

```python
def my_callback(event_type, data):
    print(f"Event: {event_type}, Data: {data}")

# Subscribe
bridge.subscribe('metrics_updated', my_callback)

# Unsubscribe
bridge.unsubscribe('metrics_updated', my_callback)
```

---

## Error Handling

### Command Errors

```python
result = bridge.execute_command(command)

if not result.success:
    print(f"Error: {result.error}")
    print(f"Execution time: {result.execution_time}ms")
    
    # Show error to user
    QMessageBox.critical(self, "Error", result.error)
```

### Query Errors

```python
result = bridge.query_data('metrics', query)

if not result.success:
    print(f"Query failed: {result.error}")
    # Use fallback data
    data = self._get_cached_data()
```

### Event Errors

```python
def on_event(event_type, data):
    try:
        # Process event
        pass
    except Exception as e:
        print(f"Event processing error: {e}")
        # Don't crash, just log

bridge.subscribe('metrics_updated', on_event)
```

---

## Best Practices

### 1. Always Check Results

```python
# ✅ Good
result = bridge.execute_command(command)
if result.success:
    use_data(result.data)
else:
    handle_error(result.error)

# ❌ Bad
result = bridge.execute_command(command)
use_data(result.data)  # Might be None!
```

### 2. Use Type-Safe Commands

```python
# ✅ Good
command = StartMonitoringCommand(interval=100)

# ❌ Bad
command = Command('start_monitoring', {'interval': 100})
```

### 3. Subscribe Early, Unsubscribe on Cleanup

```python
class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.bridge = BackendBridge.get_instance()
        self.bridge.subscribe('metrics', self._on_metrics)
    
    def closeEvent(self, event):
        # Clean up
        self.bridge.unsubscribe('metrics', self._on_metrics)
        event.accept()
```

### 4. Use Query Builder

```python
# ✅ Good - Type-safe, readable
query = QueryBuilder() \
    .select(['fps']) \
    .filter({'timestamp': '>1h'}) \
    .limit(100)

# ❌ Bad - Error-prone
query = {'select': ['fps'], 'filter': {'timestamp': '>1h'}}
```

### 5. Handle Qt Signals Properly

```python
# ✅ Good - Connect in __init__
def __init__(self):
    if self.bridge.qt_signals:
        self.bridge.qt_signals.data_updated.connect(self._update_ui)

# ❌ Bad - Connect multiple times
def update(self):
    self.bridge.qt_signals.data_updated.connect(self._update_ui)
```

---

## Summary

**Key Points:**

✅ Use BackendBridge for all backend access  
✅ Use Commands for operations  
✅ Use Queries for data retrieval  
✅ Subscribe to events for notifications  
✅ Always check result.success  
✅ Use Qt signals for thread-safe UI updates  
✅ Clean up subscriptions  

**Version:** 0.3.5d (Package 3.9a) - COMPLETE!
