# System Health Monitor

**Version:** 0.3.5r (Package 3.9a, Stage 7.7b.6.2/7.7)

## Overview

The SystemHealthMonitor provides system-wide health monitoring, component status aggregation, and real-time alerting.

## Features

- **Component Health Monitoring**: Track health of individual components
- **Status Aggregation**: Aggregate status into system-wide health
- **Health Metrics**: Collect and report component metrics
- **Real-time Alerts**: Generate alerts on status changes
- **Alert Callbacks**: Real-time notifications
- **Statistics Tracking**: Monitor success rates and uptime
- **ErrorReporter Integration**: Automatic error reporting

## Component Status Levels

```python
class ComponentStatus(Enum):
    UNKNOWN = "unknown"        # Not checked yet
    HEALTHY = "healthy"        # Operating normally
    DEGRADED = "degraded"      # Intermittent issues (1-2 failures)
    UNHEALTHY = "unhealthy"    # Not responding (3+ failures)
    CRITICAL = "critical"      # Critical component failure
    OFFLINE = "offline"        # Component offline
```

## Alert Levels

```python
class AlertLevel(Enum):
    INFO = "info"              # Informational
    WARNING = "warning"        # Warning condition
    ERROR = "error"            # Error condition
    CRITICAL = "critical"      # Critical condition
```

## Usage

### Basic Usage

```python
from core.system_health_monitor import SystemHealthMonitor

# Create monitor
monitor = SystemHealthMonitor(check_interval=5.0)

# Register components
monitor.register_component(
    'PerformanceMonitor',
    health_check=lambda: performance_monitor.is_running(),
    get_metrics=lambda: performance_monitor.get_metrics(),
    critical=False
)

monitor.register_component(
    'ConfigManager',
    health_check=lambda: config_manager.is_healthy(),
    critical=True  # Critical component
)

# Start monitoring
monitor.start()

# Get system health
health = monitor.get_system_health()
print(f"System healthy: {health['healthy']}")
print(f"Status: {health['status']}")

# Stop monitoring
monitor.stop()
```

### Component Registration

```python
# Simple health check
def is_healthy():
    return service.is_running()

monitor.register_component('MyService', is_healthy)

# With metrics
def is_healthy():
    return service.is_running()

def get_metrics():
    return {
        'requests': service.request_count,
        'errors': service.error_count,
        'latency': service.avg_latency
    }

monitor.register_component(
    'MyService',
    health_check=is_healthy,
    get_metrics=get_metrics,
    critical=True  # Mark as critical
)
```

**Critical Components:**
When a critical component fails (3+ consecutive failures), its status becomes `CRITICAL` instead of just `UNHEALTHY`, and the system status reflects this severity.

### Health Checks

```python
# Get specific component health
health = monitor.get_component_health('PerformanceMonitor')
if health:
    print(f"Status: {health['status']}")
    print(f"Message: {health['message']}")
    print(f"Metrics: {health['metrics']}")
    print(f"Consecutive failures: {health['consecutive_failures']}")

# Get all components
all_health = monitor.get_all_components_health()
for name, health in all_health.items():
    print(f"{name}: {health['status']}")

# Get system-wide health
system_health = monitor.get_system_health()
print(f"Overall status: {system_health['status']}")
print(f"Healthy: {system_health['healthy']}")
print(f"Message: {system_health['message']}")
print(f"Healthy components: {system_health['healthy_count']}/{system_health['total_components']}")
```

**System Health Response:**
```python
{
    'healthy': False,
    'status': 'degraded',
    'message': '1 degraded component(s)',
    'total_components': 5,
    'healthy_count': 4,
    'degraded_count': 1,
    'unhealthy_count': 0,
    'critical_count': 0,
    'status_counts': {
        'healthy': 4,
        'degraded': 1
    },
    'components': {...},
    'statistics': {
        'running': True,
        'uptime': 123.45,
        'total_checks': 150,
        'failed_checks': 5,
        'success_rate': 96.67,
        'check_interval': 5.0
    }
}
```

### Alerts

#### Add Alert Callbacks

```python
def on_alert(alert):
    print(f"[{alert.level.value.upper()}] {alert.component}")
    print(f"  {alert.message}")
    
    if alert.level == AlertLevel.CRITICAL:
        send_sms_alert(alert)
    elif alert.level == AlertLevel.ERROR:
        send_email_alert(alert)

callback_id = monitor.add_alert_callback(on_alert)
```

#### Get Recent Alerts

```python
# Get all recent alerts
alerts = monitor.get_recent_alerts(limit=10)

# Filter by level
alerts = monitor.get_recent_alerts(
    limit=20,
    min_level=AlertLevel.ERROR  # Only ERROR and CRITICAL
)

# Process alerts
for alert in alerts:
    print(f"[{alert['level']}] {alert['component']}: {alert['message']}")
    print(f"  Time: {alert['timestamp']}")
    if alert['details']:
        print(f"  Details: {alert['details']}")
```

#### Clear Alerts

```python
# Clear all alerts
monitor.clear_alerts()
```

### Statistics

```python
health = monitor.get_system_health()
stats = health['statistics']

print(f"Uptime: {stats['uptime']:.1f} seconds")
print(f"Total checks: {stats['total_checks']}")
print(f"Failed checks: {stats['failed_checks']}")
print(f"Success rate: {stats['success_rate']:.2f}%")
print(f"Check interval: {stats['check_interval']} seconds")
```

## Integration Examples

### With BackendServiceManager

```python
from backend.service_manager import BackendServiceManager
from core.system_health_monitor import SystemHealthMonitor

class Application:
    def __init__(self):
        self.service_manager = BackendServiceManager()
        self.health_monitor = SystemHealthMonitor(check_interval=5.0)
    
    def initialize(self):
        # Register services
        self.service_manager.register_service('monitor', performance_monitor)
        self.service_manager.register_service('detection', game_detection)
        
        # Register health checks
        self.health_monitor.register_component(
            'ServiceManager',
            health_check=lambda: self.service_manager.get_health()['healthy'],
            get_metrics=lambda: self.service_manager.get_all_status()['services'],
            critical=True
        )
        
        self.health_monitor.register_component(
            'PerformanceMonitor',
            health_check=lambda: performance_monitor.is_running(),
            get_metrics=lambda: performance_monitor.get_status()
        )
        
        # Start everything
        self.service_manager.start_all()
        self.health_monitor.start()
```

### With ErrorReporter

```python
from core.error_reporter import ErrorReporter
from core.system_health_monitor import SystemHealthMonitor

# Create error reporter
error_reporter = ErrorReporter()

# Create health monitor with error reporter
monitor = SystemHealthMonitor(
    check_interval=5.0,
    error_reporter=error_reporter
)

# Register components
monitor.register_component('MyService', health_check)

# Start monitoring
monitor.start()

# Health status changes are automatically reported to ErrorReporter
# CRITICAL status → ErrorSeverity.CRITICAL
# UNHEALTHY status → ErrorSeverity.ERROR
# DEGRADED status → ErrorSeverity.WARNING
```

### Complete Monitoring System

```python
class MonitoringSystem:
    def __init__(self):
        self.error_reporter = ErrorReporter()
        self.health_monitor = SystemHealthMonitor(
            check_interval=5.0,
            error_reporter=self.error_reporter
        )
        
        # Setup alert handling
        self.health_monitor.add_alert_callback(self._on_alert)
    
    def _on_alert(self, alert):
        """Handle health alerts"""
        if alert.level == AlertLevel.CRITICAL:
            # Send immediate notification
            self._send_critical_alert(alert)
            
            # Generate emergency report
            self.error_reporter.export_report(
                f'reports/critical_{int(time.time())}.html',
                format='html',
                min_severity=ErrorSeverity.CRITICAL
            )
        
        elif alert.level == AlertLevel.ERROR:
            # Log to monitoring system
            self._log_to_monitoring(alert)
    
    def register_all_components(self):
        """Register all system components"""
        components = [
            ('ConfigManager', config_manager, True),
            ('PerformanceMonitor', perf_monitor, False),
            ('GameDetection', game_detection, False),
            ('ServiceManager', service_manager, True),
        ]
        
        for name, component, critical in components:
            self.health_monitor.register_component(
                name,
                health_check=lambda c=component: c.is_running(),
                get_metrics=lambda c=component: c.get_status(),
                critical=critical
            )
    
    def start(self):
        """Start monitoring"""
        self.health_monitor.start()
    
    def get_dashboard(self):
        """Get dashboard data"""
        health = self.health_monitor.get_system_health()
        alerts = self.health_monitor.get_recent_alerts(limit=10)
        errors = self.error_reporter.get_statistics()
        
        return {
            'health': health,
            'alerts': alerts,
            'errors': errors
        }
```

## Status Determination Logic

### Component Status

```
Health Check → Result → Consecutive Failures → Status

✓ True      →   0    →  0  → HEALTHY
✗ False     →   0    →  1  → DEGRADED (first failure)
✗ False     →   1    →  2  → DEGRADED (second failure)
✗ False     →   2    →  3  → UNHEALTHY (3+ failures, non-critical)
✗ False     →   2    →  3  → CRITICAL (3+ failures, critical component)
```

### System Status

```
Component States → System Status

Any CRITICAL      → CRITICAL
Any UNHEALTHY     → UNHEALTHY
Any DEGRADED      → DEGRADED
All HEALTHY       → HEALTHY
No components     → UNKNOWN
```

## Best Practices

### 1. Choose Appropriate Check Intervals

```python
# Fast checks for critical components
monitor = SystemHealthMonitor(check_interval=2.0)

# Slower checks for less critical
monitor = SystemHealthMonitor(check_interval=10.0)
```

### 2. Implement Efficient Health Checks

```python
# Good: Fast check
def is_healthy():
    return service.is_running()  # O(1) check

# Bad: Slow check
def is_healthy():
    try:
        service.test_full_functionality()  # May be slow
        return True
    except:
        return False
```

### 3. Mark Critical Components

```python
# Critical: Core functionality
monitor.register_component('ConfigManager', check, critical=True)
monitor.register_component('ServiceManager', check, critical=True)

# Non-critical: Optional features
monitor.register_component('Analytics', check, critical=False)
monitor.register_component('Telemetry', check, critical=False)
```

### 4. Provide Useful Metrics

```python
def get_metrics():
    return {
        'requests_per_sec': service.get_rps(),
        'error_rate': service.get_error_rate(),
        'avg_latency_ms': service.get_avg_latency(),
        'active_connections': service.get_connection_count(),
        'queue_size': service.get_queue_size()
    }

monitor.register_component('API', is_healthy, get_metrics)
```

### 5. Handle Alerts Appropriately

```python
def on_alert(alert):
    if alert.level == AlertLevel.CRITICAL:
        # Immediate action required
        send_pager_alert(alert)
        trigger_incident_response(alert)
    
    elif alert.level == AlertLevel.ERROR:
        # Investigate soon
        send_email_alert(alert)
        log_to_monitoring(alert)
    
    elif alert.level == AlertLevel.WARNING:
        # Monitor situation
        log_to_monitoring(alert)
    
    else:  # INFO
        # Just log
        log_to_file(alert)
```

## Configuration

```python
class HealthMonitorConfig:
    # Check interval in seconds
    CHECK_INTERVAL = 5.0
    
    # Consecutive failures before UNHEALTHY
    UNHEALTHY_THRESHOLD = 3
    
    # Maximum alerts to keep
    MAX_ALERTS = 100
    
    # Alert retention time
    ALERT_RETENTION = 3600  # 1 hour
    
    # Critical components
    CRITICAL_COMPONENTS = [
        'ConfigManager',
        'ServiceManager',
        'DatabaseConnection'
    ]
```

## See Also

- [ErrorReporter](ERROR_REPORTING.md) - Error reporting system
- [BackendServiceManager](../src/backend/service_manager.py) - Service management
- [RecoveryCoordinator](RECOVERY_SYSTEM.md) - Recovery system (Stage 7.7b.6.3)
- [Stage 7.7b.6 Summary](STAGE_7.7b.6_SUMMARY.md)
