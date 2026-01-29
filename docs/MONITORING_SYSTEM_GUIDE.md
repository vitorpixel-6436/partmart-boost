# Monitoring System Complete Guide

**Version:** 0.3.6 (Package 3.9a COMPLETE)

## Overview

This guide provides complete documentation for the PartMart Boost monitoring system implemented in Package 3.9a.

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│              MonitoringSystemIntegrator                     │
│                 (Central Coordinator)                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┬──────────┐
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
  ┌──────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────────┐
  │  Error   │ │ Health │ │Recovery  │ │Historic│ │  Data    │
  │ Reporter │ │Monitor │ │Coordinator│ │  Store │ │Aggregator│
  └──────────┘ └────────┘ └──────────┘ └────────┘ └──────────┘
       │           │           │            │           │
       └───────────┴───────────┴────────────┴───────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │  GUI Layer    │
                  │               │
                  │ - Monitoring  │
                  │   Panel       │
                  │ - Charts      │
                  │ - Viewer      │
                  └───────────────┘
```

### Component Descriptions

#### 1. ErrorReporter (Stage 7.7b.6.1)
- **Purpose:** Centralized error logging and tracking
- **Features:** Error history, severity levels, component tracking
- **File:** `src/core/error_reporter.py`

#### 2. SystemHealthMonitor (Stage 7.7b.6.2)
- **Purpose:** Continuous health monitoring of system components
- **Features:** Automatic health checks, status tracking, component registration
- **File:** `src/core/system_health_monitor.py`

#### 3. RecoveryCoordinator (Stage 7.7b.6.3)
- **Purpose:** Automated recovery from failures
- **Features:** Multiple strategies, automatic retries, recovery history
- **File:** `src/core/recovery_coordinator.py`

#### 4. HistoricalDataStore (Stage 7.7b.8.1)
- **Purpose:** Time-series storage for monitoring data
- **Features:** SQLite backend, retention policies, indexed queries
- **File:** `src/core/historical_data_store.py`

#### 5. DataAggregator (Stage 7.7b.8.1)
- **Purpose:** Periodic data collection and aggregation
- **Features:** Background collection, statistics computation
- **File:** `src/core/data_aggregator.py`

#### 6. ChartWidget (Stage 7.7b.8.2)
- **Purpose:** Interactive data visualization
- **Features:** Line/Bar/Pie charts, export functionality
- **File:** `src/ui/widgets/chart_widget.py`

#### 7. HistoricalDataViewer (Stage 7.7b.8.2)
- **Purpose:** Complete visualization interface
- **Features:** Multiple chart views, time range selection, auto-refresh
- **File:** `src/ui/widgets/historical_data_viewer.py`

#### 8. MonitoringSystemIntegrator (Stage 7.7b.9)
- **Purpose:** Unified integration and lifecycle management
- **Features:** Complete system coordination, configuration, status reporting
- **File:** `src/core/monitoring_system_integrator.py`

## Quick Start

### Basic Usage

```python
from core.monitoring_system_integrator import (
    MonitoringSystemIntegrator,
    MonitoringConfig
)

# Create configuration
config = MonitoringConfig(
    health_check_interval=5.0,
    collection_interval=60.0,
    data_retention_days=30
)

# Create integrator
integrator = MonitoringSystemIntegrator(config)

# Initialize all components
if integrator.initialize():
    # Start monitoring
    if integrator.start():
        # System is running
        integrator.print_status()
        
        # ... your application code ...
        
        # Stop when done
        integrator.stop()
```

### GUI Integration

```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.widgets.monitoring_panel import MonitoringPanel
from ui.widgets.historical_data_viewer import HistoricalDataViewer

class MainWindow(QMainWindow):
    def __init__(self, integrator):
        super().__init__()
        
        # Create monitoring panel
        self.monitoring_panel = MonitoringPanel()
        self.monitoring_panel.set_health_monitor(
            integrator.get_health_monitor()
        )
        
        # Create history viewer
        self.history_viewer = HistoricalDataViewer()
        self.history_viewer.set_historical_store(
            integrator.get_historical_store()
        )
        
        # Add to UI...
```

## Configuration

### MonitoringConfig Options

```python
config = MonitoringConfig(
    # Error reporting
    enable_error_reporting=True,
    max_error_history=1000,
    
    # Health monitoring
    enable_health_monitoring=True,
    health_check_interval=5.0,  # seconds
    
    # Recovery
    enable_auto_recovery=True,
    max_recovery_attempts=3,
    
    # Historical data
    enable_historical_data=True,
    historical_db_path="data/monitoring_history.db",
    data_retention_days=30,  # 7, 30, 90, 365, or unlimited
    
    # Data aggregation
    enable_data_aggregation=True,
    collection_interval=60.0,      # seconds
    aggregation_interval=3600.0,   # seconds
    
    # Performance monitoring
    enable_performance_monitoring=True,
    
    # GUI integration
    enable_gui_integration=True
)
```

### Preset Configurations

#### Development Configuration
```python
dev_config = MonitoringConfig(
    health_check_interval=2.0,     # Fast checks
    collection_interval=30.0,      # Frequent collection
    data_retention_days=7,         # Short retention
    enable_auto_recovery=False     # Manual recovery
)
```

#### Production Configuration
```python
prod_config = MonitoringConfig(
    health_check_interval=5.0,
    collection_interval=60.0,
    data_retention_days=90,
    enable_auto_recovery=True,
    max_recovery_attempts=5
)
```

#### Minimal Configuration
```python
minimal_config = MonitoringConfig(
    enable_historical_data=False,
    enable_data_aggregation=False,
    enable_gui_integration=False
)
```

## Component Usage

### Error Reporting

```python
error_reporter = integrator.get_error_reporter()

# Report error
error_reporter.report_error(
    severity='error',
    component='MyComponent',
    message='Something went wrong',
    details='Detailed error information'
)

# Get recent errors
errors = error_reporter.get_errors(limit=10)

# Get errors by severity
critical_errors = error_reporter.get_errors_by_severity('critical')
```

### Health Monitoring

```python
health_monitor = integrator.get_health_monitor()

# Register component
class MyComponent:
    def check_health(self):
        # Return health status
        return {
            'status': 'healthy',  # healthy, degraded, unhealthy, critical
            'message': 'Component OK',
            'metrics': {
                'value1': 100,
                'value2': 50
            }
        }

component = MyComponent()
health_monitor.register_component('MyComponent', component)

# Get system health
health = health_monitor.get_system_health()
print(f"System status: {health['status']}")
```

### Recovery Coordination

```python
recovery_coordinator = integrator.get_recovery_coordinator()

# Define recovery strategy
def restart_component(component_name):
    # Restart logic
    return True

recovery_coordinator.register_strategy(
    'MyComponent',
    'restart',
    restart_component
)

# Manual recovery
result = recovery_coordinator.attempt_recovery('MyComponent')
print(f"Recovery {'successful' if result else 'failed'}")
```

### Historical Data

```python
historical_store = integrator.get_historical_store()

# Query health history
import time
end_time = time.time()
start_time = end_time - 86400  # Last 24 hours

records = historical_store.query_health_history(
    start_time,
    end_time,
    component='MyComponent'
)

# Get statistics
stats = historical_store.get_statistics(start_time, end_time)
print(f"Success rate: {stats['success_rate']:.1f}%")
```

## Status Monitoring

### System Status

```python
# Get complete status
status = integrator.get_status()

print(f"Running: {status.is_running}")
print(f"Uptime: {status.uptime:.1f}s")
print(f"Total errors: {status.total_errors}")
print(f"Success rate: {status.success_rate:.1f}%")
print(f"Memory: {status.memory_usage_mb:.1f} MB")
print(f"CPU: {status.cpu_usage_percent:.1f}%")

# Component status
print(f"ErrorReporter: {'Active' if status.error_reporter_active else 'Inactive'}")
print(f"HealthMonitor: {'Active' if status.health_monitor_active else 'Inactive'}")
```

### Performance Statistics

```python
perf_stats = integrator.get_performance_stats()

print(f"Initialization time: {perf_stats['initialization_time']:.3f}s")
print(f"Startup time: {perf_stats['startup_time']:.3f}s")
```

## Best Practices

### 1. Proper Initialization

```python
# Always check initialization
if not integrator.initialize():
    print("Failed to initialize monitoring system")
    # Handle error
    exit(1)

# Always check startup
if not integrator.start():
    print("Failed to start monitoring system")
    # Handle error
    exit(1)
```

### 2. Graceful Shutdown

```python
import signal

def signal_handler(sig, frame):
    print("\nShutting down...")
    integrator.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

### 3. Error Handling

```python
try:
    # Your code
    result = dangerous_operation()
except Exception as e:
    # Report to monitoring system
    error_reporter.report_error(
        severity='error',
        component='MyModule',
        message=str(e),
        details=traceback.format_exc()
    )
    # Handle error
```

### 4. Health Check Implementation

```python
class MyComponent:
    def check_health(self):
        try:
            # Perform checks
            if self.is_connected():
                if self.has_errors():
                    return {
                        'status': 'degraded',
                        'message': 'Component has errors',
                        'metrics': self.get_metrics()
                    }
                else:
                    return {
                        'status': 'healthy',
                        'message': 'Component OK',
                        'metrics': self.get_metrics()
                    }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Connection lost'
                }
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Health check failed: {e}'
            }
```

## Troubleshooting

### System Won't Start

```python
# Check initialization
if not integrator.initialize():
    # Check component availability
    print(f"ErrorReporter: {integrator.get_error_reporter() is not None}")
    print(f"HealthMonitor: {integrator.get_health_monitor() is not None}")
    # Check file permissions
    # Check disk space
```

### High Memory Usage

```python
# Check database size
historical_store = integrator.get_historical_store()
size_bytes = historical_store.get_database_size()
size_mb = size_bytes / 1024 / 1024
print(f"Database size: {size_mb:.2f} MB")

# Cleanup old data
if size_mb > 100:
    deleted = historical_store.cleanup_old_data()
    historical_store.vacuum()
    print(f"Cleaned up {deleted} records")
```

### Charts Not Updating

```python
# Check data aggregator is running
data_aggregator = integrator.get_data_aggregator()
if not data_aggregator.is_running():
    print("Data aggregator not running!")
    # Restart if needed

# Check historical store has data
records = historical_store.query_health_history(
    time.time() - 3600,
    time.time()
)
print(f"Found {len(records)} records in last hour")
```

## Testing

### Running Tests

```bash
# Run all monitoring tests
python -m pytest tests/test_monitoring_*.py -v

# Run specific component tests
python tests/test_error_reporter.py
python tests/test_system_health_monitor.py
python tests/test_recovery_coordinator.py

# Run integration tests
python tests/test_monitoring_system_integrator.py
```

### Test Coverage

- ErrorReporter: 15 tests
- SystemHealthMonitor: 16 tests
- RecoveryCoordinator: 14 tests
- HistoricalDataStore: 16 tests
- DataAggregator: 11 tests
- ChartWidget: 13 tests
- HistoricalDataViewer: 15 tests
- MonitoringSystemIntegrator: 12 tests

**Total: 112+ comprehensive tests**

## Performance Guidelines

### Recommended Settings

**Small Application (<10 components):**
```python
config = MonitoringConfig(
    health_check_interval=5.0,
    collection_interval=60.0,
    data_retention_days=30
)
```

**Medium Application (10-50 components):**
```python
config = MonitoringConfig(
    health_check_interval=10.0,
    collection_interval=120.0,
    data_retention_days=30
)
```

**Large Application (50+ components):**
```python
config = MonitoringConfig(
    health_check_interval=30.0,
    collection_interval=300.0,
    data_retention_days=30
)
```

### Memory Usage

- Base system: ~20-30 MB
- Per component: ~1-2 MB
- Historical data: ~40 MB per 30 days
- Charts: ~30-40 MB (4 charts)

**Total typical usage: 100-150 MB**

### CPU Usage

- Health checks: <1% CPU
- Data collection: <2% CPU
- Chart rendering: <5% CPU
- Recovery operations: <3% CPU

**Total typical usage: <10% CPU**

## See Also

- [Error Reporting Documentation](ERROR_REPORTING.md)
- [System Health Documentation](SYSTEM_HEALTH.md)
- [Recovery System Documentation](RECOVERY_SYSTEM.md)
- [Historical Data Documentation](HISTORICAL_DATA.md)
- [Charts & Visualization Documentation](CHARTS_VISUALIZATION.md)
- [Package 3.9a Summary](PACKAGE_3.9a_SUMMARY.md)
