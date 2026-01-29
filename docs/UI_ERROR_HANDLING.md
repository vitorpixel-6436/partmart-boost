# UI Components Error Handling

**Version:** 0.3.5m (Package 3.9a, Stage 7.7b.4/7.7)

## Overview

Error handling in PyQt6-based UI components with graceful degradation and user-friendly messages.

## Principles

### 1. **Never Crash the UI**
UI errors should never crash the entire application.

### 2. **Graceful Degradation**
Show partial UI if some components fail to load.

### 3. **User-Friendly Messages**
Show simple messages to users, log technical details.

### 4. **Visual Feedback**
Use placeholders and error widgets when components fail.

### 5. **Logging Integration**
Log all UI errors for debugging.

## MainWindow Error Handling

### Initialization Errors

**Component Extraction:**
```python
def _extract_components(self):
    # Each component extracted separately
    try:
        self._bridge = self._integrator.get_bridge()
    except Exception as e:
        self._log_error(f"Failed to get bridge: {e}")
        self._bridge = None  # Continue without bridge
    
    try:
        self._qt_signals = self._integrator.get_qt_signals()
    except Exception as e:
        self._log_error(f"Failed to get Qt signals: {e}")
        self._qt_signals = None
```

**UI Initialization:**
```python
def _init_ui(self):
    try:
        # Create UI components
        self._create_header()
        self._create_tabs()
        self._create_status_bar()
    except Exception as e:
        self._log_error(f"UI init failed: {e}", exc_info=True)
        # Show minimal UI
        self._init_minimal_ui()
```

### Tab Creation Errors

**Individual Tab Protection:**
```python
def _create_tabs(self):
    # Dashboard tab
    try:
        if WIDGETS_AVAILABLE and self._bridge:
            dashboard = DashboardWidget(self._bridge, self._qt_signals)
            self._tabs.addTab(dashboard, "🏠 Dashboard")
        else:
            # Show placeholder
            dashboard = self._create_placeholder("Dashboard", "Not available")
            self._tabs.addTab(dashboard, "🏠 Dashboard")
    except Exception as e:
        # Show error widget
        error_widget = self._create_error_placeholder("Dashboard", str(e))
        self._tabs.addTab(error_widget, "🏠 Dashboard")
```

### Monitoring Startup Errors

**Safe Auto-Start:**
```python
def _auto_start_monitoring(self):
    try:
        if not self._bridge:
            self._log_warning("Bridge not available")
            self._status_label.setText("Monitoring unavailable")
            return
        
        command = StartMonitoringCommand(interval=100)
        result = self._bridge.execute_command(command)
        
        if result.success:
            self._status_label.setText("Monitoring active")
        else:
            self._status_label.setText(f"Failed: {result.error}")
    
    except Exception as e:
        self._log_error(f"Auto-start failed: {e}", exc_info=True)
        self._status_label.setText("Monitoring error")
```

### Close Event Handling

**Cleanup on Close:**
```python
def closeEvent(self, event: QCloseEvent):
    try:
        self._log_info("Window closing, cleaning up...")
        
        # Cleanup integrator
        if self._integrator:
            try:
                # Stop monitoring, save config, etc.
                self._integrator.cleanup()
            except Exception as e:
                self._log_error(f"Cleanup error: {e}")
        
        event.accept()
    
    except Exception as e:
        self._log_error(f"Close event error: {e}")
        event.accept()  # Close anyway
```

## Widget Error Handling

### PerformanceWidget

**Signal Connection Errors:**
```python
def __init__(self, qt_signals):
    super().__init__()
    self._qt_signals = qt_signals
    
    try:
        if qt_signals:
            qt_signals.performance_update.connect(self._on_performance_update)
        else:
            self._log_warning("No signals provided")
    except Exception as e:
        self._log_error(f"Signal connection failed: {e}")
```

**Update Errors:**
```python
@pyqtSlot(dict)
def _on_performance_update(self, data: dict):
    try:
        # Validate data
        if not data:
            return
        
        cpu = data.get('cpu', 0)
        gpu = data.get('gpu', 0)
        
        # Update UI
        self._update_displays(cpu, gpu)
    
    except KeyError as e:
        self._log_warning(f"Missing key in data: {e}")
    
    except Exception as e:
        self._log_error(f"Update failed: {e}", exc_info=True)
```

### DashboardWidget

**Command Execution Errors:**
```python
def _on_boost_clicked(self):
    try:
        if not self._bridge:
            self._show_error("Backend not connected")
            return
        
        command = EnableBoostCommand()
        result = self._bridge.execute_command(command)
        
        if result.success:
            self._show_success("Boost enabled")
        else:
            self._show_error(f"Failed: {result.error}")
    
    except Exception as e:
        self._log_error(f"Boost command failed: {e}", exc_info=True)
        self._show_error("An error occurred. Check logs.")
```

### SettingsWidget

**Config Update Errors:**
```python
def _on_setting_changed(self, key: str, value: Any):
    try:
        if not self._bridge:
            self._show_error("Settings unavailable")
            return
        
        command = SetConfigCommand(key, value)
        result = self._bridge.execute_command(command)
        
        if not result.success:
            self._show_error(f"Failed to update {key}")
            self._revert_ui_change(key)  # Revert UI
    
    except Exception as e:
        self._log_error(f"Setting change failed: {e}", exc_info=True)
        self._show_error("Failed to save settings")
```

## Error Display Patterns

### Pattern 1: Placeholder Widgets

```python
def _create_placeholder(self, title: str, message: str) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    title_label = QLabel(title)
    title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
    title_label.setStyleSheet("color: #E63946;")
    layout.addWidget(title_label)
    
    msg_label = QLabel(message)
    msg_label.setStyleSheet("color: #666;")
    layout.addWidget(msg_label)
    
    return widget
```

**Usage:**
```python
if not component_available:
    widget = self._create_placeholder("Settings", "Settings not available")
    self._tabs.addTab(widget, "⚙️ Settings")
```

### Pattern 2: Error Placeholder

```python
def _create_error_placeholder(self, title: str, error: str) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    title_label = QLabel(f"⚠️ {title} Error")
    title_label.setStyleSheet("color: #F44336;")
    layout.addWidget(title_label)
    
    error_label = QLabel(f"Failed to load {title.lower()}.")
    error_label.setStyleSheet("color: #888;")
    layout.addWidget(error_label)
    
    return widget
```

**Usage:**
```python
try:
    widget = ComplexWidget()
except Exception as e:
    widget = self._create_error_placeholder("Dashboard", str(e))

self._tabs.addTab(widget, "🏠 Dashboard")
```

### Pattern 3: Status Bar Messages

```python
def _show_status_error(self, message: str):
    if self._status_label:
        self._status_label.setText(f"❌ {message}")
        self._status_label.setStyleSheet("color: #F44336;")

def _show_status_success(self, message: str):
    if self._status_label:
        self._status_label.setText(f"✅ {message}")
        self._status_label.setStyleSheet("color: #4CAF50;")

def _show_status_warning(self, message: str):
    if self._status_label:
        self._status_label.setText(f"⚠️ {message}")
        self._status_label.setStyleSheet("color: #FFC107;")
```

### Pattern 4: Error Dialogs

```python
def show_error_dialog(self, title: str, message: str, details: str = None):
    try:
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if details:
            msg_box.setDetailedText(details)
        
        msg_box.exec()
    
    except Exception as e:
        self._log_error(f"Error dialog failed: {e}")
```

**Usage:**
```python
try:
    risky_operation()
except Exception as e:
    self.show_error_dialog(
        "Operation Failed",
        "Could not complete the operation.",
        str(e)
    )
```

## Testing UI Error Handling

### Test Component Failures

```python
def test_window_without_integrator(self):
    # Should create window with placeholders
    window = MainWindowStage7(integrator=None)
    self.assertIsNotNone(window)
    self.assertTrue(window.isVisible())

def test_window_with_broken_integrator(self):
    class BrokenIntegrator:
        def get_bridge(self):
            raise Exception("Bridge error!")
    
    # Should handle error gracefully
    window = MainWindowStage7(integrator=BrokenIntegrator())
    self.assertIsNotNone(window)
```

### Test Widget Errors

```python
def test_widget_without_signals(self):
    # Should create widget without signals
    widget = PerformanceWidget(qt_signals=None)
    self.assertIsNotNone(widget)

def test_widget_with_invalid_data(self):
    widget = PerformanceWidget(qt_signals)
    
    # Should handle invalid data
    widget._on_performance_update({'invalid': 'data'})
    # Should not crash
```

## Best Practices

### DO

✅ **Wrap each component creation in try-catch**
```python
try:
    widget = ComplexWidget()
except Exception as e:
    widget = error_placeholder
```

✅ **Check for None before using**
```python
if self._bridge:
    result = self._bridge.execute_command(cmd)
else:
    self._show_error("Backend unavailable")
```

✅ **Provide visual feedback**
```python
if error:
    self._status_label.setText("❌ Error")
    self._status_label.setStyleSheet("color: red;")
```

✅ **Use placeholders for missing components**
```python
if not available:
    return self._create_placeholder("Feature", "Not available")
```

✅ **Log all errors**
```python
except Exception as e:
    self._log_error(f"Operation failed: {e}", exc_info=True)
```

### DON'T

❌ **Don't crash on component failure**
```python
# BAD
widget = RequiredWidget()  # Crashes if fails

# GOOD
try:
    widget = RequiredWidget()
except Exception:
    widget = placeholder_widget
```

❌ **Don't show technical errors to users**
```python
# BAD
QMessageBox.critical(self, "Error", str(exception))

# GOOD
QMessageBox.critical(self, "Error", "Operation failed. Check logs.")
self._log_error(f"Details: {exception}", exc_info=True)
```

❌ **Don't ignore closeEvent errors**
```python
# BAD
def closeEvent(self, event):
    self._cleanup()  # May fail!
    event.accept()

# GOOD
def closeEvent(self, event):
    try:
        self._cleanup()
    except Exception as e:
        self._log_error(f"Cleanup failed: {e}")
    event.accept()
```

❌ **Don't assume integrator is available**
```python
# BAD
bridge = integrator.get_bridge()

# GOOD
if integrator:
    bridge = integrator.get_bridge()
else:
    bridge = None
```

## Error Recovery

### Reload Components

```python
def reload_component(self, component_name: str):
    try:
        if component_name == 'dashboard':
            # Remove old tab
            self._tabs.removeTab(0)
            
            # Create new dashboard
            dashboard = DashboardWidget(self._bridge, self._qt_signals)
            self._tabs.insertTab(0, dashboard, "🏠 Dashboard")
            
            self._show_status_success("Dashboard reloaded")
    
    except Exception as e:
        self._log_error(f"Reload failed: {e}", exc_info=True)
        self._show_status_error("Reload failed")
```

### Reconnect Backend

```python
def reconnect_backend(self):
    try:
        if self._integrator:
            # Attempt reconnection
            self._integrator.reconnect()
            
            # Extract components again
            self._extract_components()
            
            # Update UI
            self._update_connection_status()
            self._show_status_success("Reconnected")
    
    except Exception as e:
        self._log_error(f"Reconnection failed: {e}")
        self._show_status_error("Reconnection failed")
```

## See Also

- [Core Error Handling](ERROR_HANDLING.md)
- [Integration Error Handling](INTEGRATION_ERROR_HANDLING.md)
- [Logging System](LOGGING.md)
