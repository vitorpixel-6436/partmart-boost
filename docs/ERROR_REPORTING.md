# Error Reporting System

**Version:** 0.3.5q (Package 3.9a, Stage 7.7b.6.1/7.7)

## Overview

The ErrorReporter provides system-wide error collection, analysis, and reporting capabilities.

## Features

- **Error Collection**: Collect errors from all components
- **Error Aggregation**: Deduplicate similar errors
- **Severity Classification**: 5 severity levels
- **Statistics Tracking**: Track errors by component and severity
- **Multiple Report Formats**: JSON, text, HTML
- **Export Capabilities**: Save reports to files
- **Callback System**: Real-time error notifications

## Usage

### Basic Usage

```python
from core.error_reporter import ErrorReporter, ErrorSeverity

# Create reporter
reporter = ErrorReporter(max_records=1000, aggregate=True)

# Report an error
reporter.report_error(
    component='ConfigManager',
    severity=ErrorSeverity.ERROR,
    message='Failed to load config file',
    details='File not found: config.json'
)

# Report an exception
try:
    risky_operation()
except Exception as e:
    reporter.report_exception(
        component='DataProcessor',
        exception=e,
        severity=ErrorSeverity.ERROR,
        context='Processing user data'
    )
```

### Error Severity Levels

```python
class ErrorSeverity(Enum):
    DEBUG = "debug"          # Debug information
    INFO = "info"            # Informational messages
    WARNING = "warning"      # Warning conditions
    ERROR = "error"          # Error conditions
    CRITICAL = "critical"    # Critical conditions
```

**Severity Comparison:**
```python
ErrorSeverity.DEBUG < ErrorSeverity.INFO < ErrorSeverity.WARNING < ErrorSeverity.ERROR < ErrorSeverity.CRITICAL
```

### Statistics

```python
# Get error statistics
stats = reporter.get_statistics()

print(f"Total errors: {stats['total_errors']}")
print(f"Current records: {stats['current_errors']}")
print(f"By component: {stats['errors_by_component']}")
print(f"By severity: {stats['errors_by_severity']}")
```

**Example Output:**
```python
{
    'total_errors': 42,
    'current_errors': 15,
    'errors_by_component': {
        'ConfigManager': 5,
        'PerformanceMonitor': 3,
        'GameDetection': 7
    },
    'errors_by_severity': {
        'warning': 8,
        'error': 6,
        'critical': 1
    },
    'aggregation_enabled': True,
    'max_records': 1000
}
```

### Filtering Errors

```python
# Get all errors
errors = reporter.get_errors()

# Filter by component
errors = reporter.get_errors(component='ConfigManager')

# Filter by exact severity
errors = reporter.get_errors(severity=ErrorSeverity.ERROR)

# Filter by minimum severity (ERROR and above)
errors = reporter.get_errors(min_severity=ErrorSeverity.ERROR)

# Apply limit
errors = reporter.get_errors(limit=10)

# Combine filters
errors = reporter.get_errors(
    component='PerformanceMonitor',
    min_severity=ErrorSeverity.WARNING,
    limit=5
)
```

### Callbacks

```python
# Add callback for real-time notifications
def on_error(error: ErrorRecord):
    if error.severity == ErrorSeverity.CRITICAL:
        send_alert(f"CRITICAL: {error.message}")
    
    log_to_monitoring(error)

callback_id = reporter.add_callback(on_error)
```

**Callback Error Isolation:**
Callbacks are isolated - if one callback raises an exception, others continue to execute.

### Report Generation

#### JSON Report

```python
# Generate JSON report
report = reporter.generate_report(
    format='json',
    component='ConfigManager',  # Optional filter
    min_severity=ErrorSeverity.ERROR,  # Optional filter
    limit=50  # Optional limit
)

# Parse JSON
import json
data = json.loads(report)
print(data['statistics'])
print(data['errors'])
```

**JSON Structure:**
```json
{
  "generated_at": "2026-01-29T03:26:00",
  "statistics": {
    "total_errors": 42,
    "current_errors": 15,
    "errors_by_component": {...},
    "errors_by_severity": {...}
  },
  "errors": [
    {
      "timestamp": 1738119960.0,
      "datetime": "2026-01-29T03:26:00",
      "component": "ConfigManager",
      "severity": "error",
      "message": "Failed to load config",
      "details": "File not found",
      "exception_type": "FileNotFoundError",
      "traceback": "...",
      "count": 1
    }
  ]
}
```

#### Text Report

```python
# Generate text report
report = reporter.generate_report(format='text')
print(report)
```

**Text Format:**
```
================================================================================
ERROR REPORT
================================================================================
Generated: 2026-01-29T03:26:00

STATISTICS
--------------------------------------------------------------------------------
Total Errors: 42
Current Records: 15

Errors by Component:
  ConfigManager: 5
  PerformanceMonitor: 3
  GameDetection: 7

Errors by Severity:
  WARNING: 8
  ERROR: 6
  CRITICAL: 1

ERROR RECORDS (15)
--------------------------------------------------------------------------------

[1] ERROR - ConfigManager
    Time: 2026-01-29T03:26:00
    Message: Failed to load config
    Details: File not found
    Exception: FileNotFoundError
    Traceback:
      File "config.py", line 45, in load
        with open(path) as f:
      ...
```

#### HTML Report

```python
# Generate HTML report
report = reporter.generate_report(format='html')

# Save to file
with open('error_report.html', 'w') as f:
    f.write(report)
```

**HTML Features:**
- Color-coded severity levels
- Expandable tracebacks
- Responsive design
- Styled statistics

### Export Reports

```python
# Export to JSON
reporter.export_report(
    'reports/error_report.json',
    format='json',
    min_severity=ErrorSeverity.WARNING
)

# Export to text
reporter.export_report(
    'reports/error_report.txt',
    format='text',
    component='PerformanceMonitor'
)

# Export to HTML
reporter.export_report(
    'reports/error_report.html',
    format='html',
    limit=100
)
```

### Clear Errors

```python
# Clear all errors
reporter.clear()

# Clear specific component
reporter.clear(component='ConfigManager')

# Clear specific severity
reporter.clear(severity=ErrorSeverity.WARNING)

# Clear with multiple filters
reporter.clear(component='ConfigManager', severity=ErrorSeverity.ERROR)
```

## Error Aggregation

**With Aggregation (default):**
```python
reporter = ErrorReporter(aggregate=True)

# Report same error 5 times
for i in range(5):
    reporter.report_error('Test', ErrorSeverity.ERROR, 'Same error')

# Only 1 record stored, count = 5
errors = reporter.get_errors()
print(len(errors))  # 1
print(errors[0].count)  # 5
```

**Without Aggregation:**
```python
reporter = ErrorReporter(aggregate=False)

# Report same error 5 times
for i in range(5):
    reporter.report_error('Test', ErrorSeverity.ERROR, 'Same error')

# All 5 records stored separately
errors = reporter.get_errors()
print(len(errors))  # 5
```

**Aggregation Key:**
Errors are aggregated based on:
- Component name
- Severity level
- Error message

## Integration Example

### With Logging System

```python
from logger import AppLogger
from core.error_reporter import ErrorReporter, ErrorSeverity

class Application:
    def __init__(self):
        self.logger = AppLogger.get_instance()
        self.error_reporter = ErrorReporter()
        
        # Add callback to report errors to logger
        self.error_reporter.add_callback(self._on_error)
    
    def _on_error(self, error):
        # Log critical errors
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(
                error.message,
                component=error.component
            )
```

### With Service Manager

```python
from backend.service_manager import BackendServiceManager
from core.error_reporter import ErrorReporter, ErrorSeverity

class ServiceMonitor:
    def __init__(self):
        self.manager = BackendServiceManager()
        self.reporter = ErrorReporter()
    
    def monitor_services(self):
        health = self.manager.get_health()
        
        if not health['healthy']:
            self.reporter.report_error(
                component='ServiceManager',
                severity=ErrorSeverity.ERROR,
                message=f"{health['crashed']} services crashed",
                details=f"Running: {health['running']}/{health['total_services']}"
            )
```

## Best Practices

### 1. Choose Appropriate Severity

```python
# DEBUG: Development information
reporter.report_error('Debug', ErrorSeverity.DEBUG, 'Variable x = 42')

# INFO: Normal operations
reporter.report_error('System', ErrorSeverity.INFO, 'Service started')

# WARNING: Recoverable issues
reporter.report_error('Monitor', ErrorSeverity.WARNING, 'High CPU usage')

# ERROR: Operation failures
reporter.report_error('Config', ErrorSeverity.ERROR, 'Failed to load')

# CRITICAL: System failures
reporter.report_error('Core', ErrorSeverity.CRITICAL, 'System crash')
```

### 2. Provide Context

```python
# Good: Include details
reporter.report_error(
    component='DatabaseManager',
    severity=ErrorSeverity.ERROR,
    message='Query failed',
    details=f'Table: users, Query: {query}, Timeout: 30s'
)

# Bad: No context
reporter.report_error(
    component='DatabaseManager',
    severity=ErrorSeverity.ERROR,
    message='Error'
)
```

### 3. Use Exception Reporting

```python
# Good: Report exceptions properly
try:
    process_data()
except Exception as e:
    reporter.report_exception(
        component='DataProcessor',
        exception=e,
        context='Processing batch 42'
    )

# Bad: Lose traceback
try:
    process_data()
except Exception as e:
    reporter.report_error(
        component='DataProcessor',
        severity=ErrorSeverity.ERROR,
        message=str(e)
    )
```

### 4. Regular Report Export

```python
import schedule

def export_daily_report():
    reporter.export_report(
        f'reports/daily_{datetime.now().strftime("%Y%m%d")}.html',
        format='html',
        min_severity=ErrorSeverity.WARNING
    )

# Schedule daily at 23:59
schedule.every().day.at("23:59").do(export_daily_report)
```

### 5. Monitor Critical Errors

```python
def on_critical_error(error):
    if error.severity == ErrorSeverity.CRITICAL:
        # Send alert
        send_email_alert(error)
        send_slack_notification(error)
        
        # Generate immediate report
        reporter.export_report(
            f'reports/critical_{int(time.time())}.html',
            format='html',
            severity=ErrorSeverity.CRITICAL
        )

reporter.add_callback(on_critical_error)
```

## Configuration

```python
class ErrorReporterConfig:
    # Maximum records to keep in memory
    MAX_RECORDS = 1000
    
    # Enable error aggregation
    AGGREGATE = True
    
    # Report export directory
    REPORT_DIR = 'reports'
    
    # Alert thresholds
    ALERT_THRESHOLD_ERROR = 10  # Alert after 10 errors
    ALERT_THRESHOLD_CRITICAL = 1  # Alert immediately
    
    # Cleanup settings
    AUTO_CLEANUP = True
    CLEANUP_INTERVAL = 3600  # 1 hour
    CLEANUP_AGE = 86400  # 24 hours
```

## See Also

- [AppLogger](../src/logger.py) - Logging system
- [SystemHealthMonitor](SYSTEM_HEALTH.md) - Health monitoring (Stage 7.7b.6.2)
- [RecoveryCoordinator](RECOVERY_SYSTEM.md) - Recovery system (Stage 7.7b.6.3)
- [Stage 7.7b.6 Summary](STAGE_7.7b.6_SUMMARY.md)
