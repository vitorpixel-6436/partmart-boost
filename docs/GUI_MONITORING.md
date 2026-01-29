# GUI Monitoring Integration

**Version:** 0.3.5t (Package 3.9a, Stage 7.7b.7/7.7)

## Overview

Stage 7.7b.7 provides comprehensive GUI integration for the monitoring and recovery systems, including real-time status displays, error viewing, recovery control, and alert notifications.

## Components

### 1. MonitoringPanel

**Purpose:** Complete monitoring dashboard with tabbed interface.

**Features:**
- System health overview
- Component status table
- Error viewer with filtering
- Recovery control and history
- Auto-updating displays

**Location:** `src/ui/widgets/monitoring_panel.py`

### 2. SystemHealthWidget

**Purpose:** Display overall system health status.

**Features:**
- Visual status indicator (color-coded)
- Component count summary
- Health statistics (uptime, checks, success rate)
- Real-time updates

### 3. ComponentStatusWidget

**Purpose:** Table view of individual component health.

**Features:**
- Component name and status
- Status message
- Consecutive failures count
- Last check timestamp
- Color-coded status

### 4. ErrorViewerWidget

**Purpose:** View and filter system errors.

**Features:**
- Severity filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Adjustable result limit
- Error count statistics
- Clear all errors
- Color-coded severity

### 5. RecoveryControlWidget

**Purpose:** Control and monitor recovery operations.

**Features:**
- Auto-recovery toggle
- Recovery statistics
- Recovery history table
- Manual refresh

### 6. AlertNotificationManager

**Purpose:** Display real-time alert notifications.

**Features:**
- Popup notifications
- Auto-close based on severity
- Manual dismiss
- Multiple notification support
- Positioned in top-right corner

## Usage

### Basic Integration

```python
from ui.widgets.monitoring_panel import MonitoringPanel
from core.error_reporter import ErrorReporter
from core.system_health_monitor import SystemHealthMonitor
from core.recovery_coordinator import RecoveryCoordinator

# Create monitoring systems
error_reporter = ErrorReporter()
health_monitor = SystemHealthMonitor(error_reporter=error_reporter)
recovery_coordinator = RecoveryCoordinator(
    health_monitor=health_monitor,
    error_reporter=error_reporter
)

# Create monitoring panel
panel = MonitoringPanel()
panel.set_monitoring_systems(
    health_monitor=health_monitor,
    error_reporter=error_reporter,
    recovery_coordinator=recovery_coordinator
)

# Start automatic updates
panel.start_updates(interval=2000)  # Update every 2 seconds
```

### Main Window Integration

```python
from PyQt6.QtWidgets import QMainWindow, QDockWidget
from PyQt6.QtCore import Qt
from ui.widgets.monitoring_panel import MonitoringPanel

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create monitoring dock
        monitoring_dock = QDockWidget("System Monitoring", self)
        
        # Create monitoring panel
        self.monitoring_panel = MonitoringPanel()
        monitoring_dock.setWidget(self.monitoring_panel)
        
        # Add to window (right side)
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            monitoring_dock
        )
        
        # Setup monitoring systems
        self.monitoring_panel.set_monitoring_systems(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter,
            recovery_coordinator=self.recovery_coordinator
        )
```

### Alert Notifications

```python
from ui.widgets.alert_notification import AlertNotificationManager

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create alert manager
        self.alert_manager = AlertNotificationManager(self)
        
        # Connect to health monitor
        self.health_monitor.add_alert_callback(self._on_health_alert)
    
    def _on_health_alert(self, alert):
        """Handle health alert"""
        alert_data = {
            'level': alert.level.value,
            'component': alert.component,
            'message': alert.message,
            'details': alert.details
        }
        self.alert_manager.show_alert(alert_data)
```

## MonitoringPanel Tabs

### Tab 1: System Health

**Display:**
- Overall system status (HEALTHY, DEGRADED, UNHEALTHY, CRITICAL)
- Component count summary
- Monitoring statistics
- Component status table

**Status Colors:**
- **Healthy:** Green (#2ecc71)
- **Degraded:** Orange (#f39c12)
- **Unhealthy:** Red (#e74c3c)
- **Critical:** Dark Red (#c0392b)
- **Unknown:** Gray (#808080)

**Component Table Columns:**
1. Component name
2. Status (color-coded)
3. Status message
4. Consecutive failures
5. Last check time

### Tab 2: Error Viewer

**Display:**
- Error filtering controls
- Error table with timestamps
- Error statistics

**Features:**
- Filter by severity (ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Adjustable limit (10-1000 errors)
- Manual refresh
- Clear all errors

**Error Table Columns:**
1. Timestamp
2. Severity (color-coded)
3. Component
4. Message
5. Count (aggregated)

### Tab 3: Recovery Control

**Display:**
- Auto-recovery toggle
- Recovery statistics
- Recovery history table

**Statistics:**
- Total recoveries
- Successful recoveries
- Failed recoveries
- Success rate percentage

**History Table Columns:**
1. Timestamp
2. Component
3. Strategy used
4. Status (color-coded)
5. Duration

## Alert Notifications

### Alert Levels

| Level | Color | Auto-Close Time |
|-------|-------|----------------|
| INFO | Blue | 3 seconds |
| WARNING | Orange | 5 seconds |
| ERROR | Red | 7 seconds |
| CRITICAL | Dark Red | 10 seconds |

### Alert Display

**Position:** Top-right corner of main window

**Features:**
- Level indicator with icon
- Component name
- Alert message
- Optional details
- Manual close button
- Fade-out animation

**Behavior:**
- Maximum 5 notifications visible
- Oldest auto-removed when limit reached
- Different auto-close durations by severity
- Can be manually dismissed anytime

## Update Intervals

### Default Settings

```python
# Monitoring panel update
DEFAULT_UPDATE_INTERVAL = 2000  # 2 seconds

# Component-specific intervals
HEALTH_MONITOR_CHECK_INTERVAL = 5.0  # 5 seconds
ERROR_REPORTER_UPDATE = 2000  # 2 seconds
RECOVERY_HISTORY_UPDATE = 2000  # 2 seconds
```

### Customizing Update Interval

```python
# Faster updates (1 second)
panel.start_updates(interval=1000)

# Slower updates (5 seconds)
panel.start_updates(interval=5000)

# Stop updates
panel.stop_updates()
```

## Styling

### Status Colors

```python
STATUS_COLORS = {
    'healthy': '#2ecc71',    # Green
    'degraded': '#f39c12',   # Orange
    'unhealthy': '#e74c3c',  # Red
    'critical': '#c0392b',   # Dark Red
    'unknown': '#808080'     # Gray
}

SEVERITY_COLORS = {
    'DEBUG': '#808080',      # Gray
    'INFO': '#3498db',       # Blue
    'WARNING': '#f39c12',    # Orange
    'ERROR': '#e74c3c',      # Red
    'CRITICAL': '#c0392b'    # Dark Red
}
```

### Custom Styling

```python
# Customize panel appearance
panel.setStyleSheet("""
    QGroupBox {
        font-weight: bold;
        border: 2px solid #3498db;
        border-radius: 5px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
""")
```

## Integration Examples

### Complete Application

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.main_window_monitoring import MainWindowMonitoring

class Application:
    def __init__(self):
        # Create monitoring systems
        self.error_reporter = ErrorReporter()
        self.health_monitor = SystemHealthMonitor(
            check_interval=5.0,
            error_reporter=self.error_reporter
        )
        self.recovery_coordinator = RecoveryCoordinator(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter
        )
        
        # Create integrator
        self.integrator = type('Integrator', (), {
            'error_reporter': self.error_reporter,
            'health_monitor': self.health_monitor,
            'recovery_coordinator': self.recovery_coordinator
        })()
    
    def run(self):
        """Run application"""
        import sys
        
        app = QApplication(sys.argv)
        
        # Create main window with monitoring
        window = MainWindowMonitoring(self.integrator)
        window.show()
        
        # Start monitoring
        self.health_monitor.start()
        self.recovery_coordinator.enable_auto_recovery()
        
        sys.exit(app.exec())

if __name__ == '__main__':
    app = Application()
    app.run()
```

### Custom Monitoring Panel

```python
from ui.widgets.monitoring_panel import (
    SystemHealthWidget,
    ComponentStatusWidget,
    ErrorViewerWidget
)

class CustomMonitoringWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # Add only health widget
        self.health_widget = SystemHealthWidget()
        layout.addWidget(self.health_widget)
        
        # Add custom controls
        self.my_controls = MyCustomControls()
        layout.addWidget(self.my_controls)
    
    def set_health_monitor(self, health_monitor):
        self.health_widget.set_health_monitor(health_monitor)
```

## Best Practices

### 1. Update Interval Selection

```python
# Real-time monitoring (frequent updates)
panel.start_updates(interval=1000)  # 1 second

# Normal monitoring (balanced)
panel.start_updates(interval=2000)  # 2 seconds (default)

# Low-frequency monitoring (resource-conscious)
panel.start_updates(interval=5000)  # 5 seconds
```

### 2. Error Filtering

```python
# Show only important errors
error_viewer.severity_combo.setCurrentText("ERROR")

# Limit result count for performance
error_viewer.limit_spin.setValue(50)
```

### 3. Alert Management

```python
# Adjust max visible notifications
alert_manager._max_notifications = 3  # Show max 3 at once

# Clear all notifications
alert_manager.clear_all()
```

### 4. Dock Widget Management

```python
# Allow floating
monitoring_dock.setFeatures(
    QDockWidget.DockWidgetFeature.DockWidgetFloatable |
    QDockWidget.DockWidgetFeature.DockWidgetMovable
)

# Start hidden
monitoring_dock.hide()

# Add menu action to toggle
view_menu.addAction(monitoring_dock.toggleViewAction())
```

## Performance Considerations

### Update Optimization

```python
# Only update visible tab
def update_displays(self):
    current_tab = self.tabs.currentIndex()
    
    if current_tab == 0:  # Health tab
        self.update_health_display()
    elif current_tab == 1:  # Error tab
        self.update_error_display()
    elif current_tab == 2:  # Recovery tab
        self.update_recovery_display()
```

### Resource Management

```python
# Stop updates when window is hidden
def hideEvent(self, event):
    self.monitoring_panel.stop_updates()
    super().hideEvent(event)

# Resume updates when shown
def showEvent(self, event):
    self.monitoring_panel.start_updates()
    super().showEvent(event)
```

## Troubleshooting

### Panel Not Updating

```python
# Check if monitoring systems are set
if panel._health_monitor is None:
    panel.set_monitoring_systems(health_monitor=monitor)

# Check if updates are started
if not panel._update_timer or not panel._update_timer.isActive():
    panel.start_updates()
```

### Alerts Not Showing

```python
# Verify alert manager is created
if not hasattr(window, '_alert_manager'):
    window._alert_manager = AlertNotificationManager(window)

# Verify callback is connected
health_monitor.add_alert_callback(window._on_health_alert)
```

## See Also

- [ErrorReporter Documentation](ERROR_REPORTING.md)
- [SystemHealthMonitor Documentation](SYSTEM_HEALTH.md)
- [RecoveryCoordinator Documentation](RECOVERY_SYSTEM.md)
- [Stage 7.7b.6 Summary](STAGE_7.7b.6_SUMMARY.md)
- [Stage 7.7b.7 Summary](STAGE_7.7b.7_SUMMARY.md)
