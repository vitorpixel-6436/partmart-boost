# Recovery Coordinator - Automatic Error Recovery

**Version:** 0.3.5s (Package 3.9a, Stage 7.7b.6.3/7.7)

## Overview

The RecoveryCoordinator provides automatic error recovery, self-healing capabilities, and rollback mechanisms for system components.

## Features

- **Automatic Recovery**: Respond to component failures automatically
- **Multiple Strategies**: Restart, reload, rollback, reset, failover
- **Rollback Support**: Undo failed recovery attempts
- **Max Attempts**: Prevent infinite recovery loops
- **Cooldown Periods**: Rate-limit recovery attempts
- **History Tracking**: Complete recovery operation logs
- **Statistics**: Success rates and performance metrics
- **Full Integration**: Works with ErrorReporter and SystemHealthMonitor

## Recovery Strategies

```python
class RecoveryStrategy(Enum):
    RESTART = "restart"      # Restart component
    RELOAD = "reload"        # Reload configuration
    ROLLBACK = "rollback"    # Rollback to previous state
    RESET = "reset"          # Reset to default state
    FAILOVER = "failover"    # Switch to backup
    MANUAL = "manual"        # Requires manual intervention
```

## Recovery Status

```python
class RecoveryStatus(Enum):
    PENDING = "pending"          # Waiting to execute
    IN_PROGRESS = "in_progress"  # Currently executing
    SUCCESS = "success"          # Completed successfully
    FAILED = "failed"            # Failed to recover
    SKIPPED = "skipped"          # Skipped (cooldown/max attempts)
```

## Usage

### Basic Setup

```python
from core.recovery_coordinator import RecoveryCoordinator, RecoveryStrategy

# Create coordinator
coordinator = RecoveryCoordinator()

# Register recovery action
coordinator.register_recovery(
    'PerformanceMonitor',
    RecoveryStrategy.RESTART,
    action=lambda: performance_monitor.restart(),
    max_attempts=3,
    cooldown=30.0
)

# Manually trigger recovery
coordinator.recover_component('PerformanceMonitor')
```

### With Rollback

```python
# Register recovery with rollback
coordinator.register_recovery(
    'ConfigManager',
    RecoveryStrategy.RELOAD,
    action=lambda: config_manager.reload_config(),
    rollback_action=lambda: config_manager.restore_backup(),
    max_attempts=2,
    cooldown=60.0
)
```

**Rollback Execution:**
If the recovery action raises an exception, the rollback action is automatically executed to restore the previous state.

### Multiple Strategies

```python
# Register multiple recovery strategies
coordinator.register_recovery(
    'GameDetection',
    RecoveryStrategy.RESTART,
    action=lambda: game_detection.restart()
)

coordinator.register_recovery(
    'GameDetection',
    RecoveryStrategy.RESET,
    action=lambda: game_detection.reset_to_defaults()
)

# Trigger specific strategy
coordinator.recover_component('GameDetection', strategy=RecoveryStrategy.RESTART)

# Or try all strategies in order
coordinator.recover_component('GameDetection')
```

### Auto-Recovery

```python
from core.system_health_monitor import SystemHealthMonitor
from core.recovery_coordinator import RecoveryCoordinator

# Create health monitor
health_monitor = SystemHealthMonitor(check_interval=5.0)

# Create coordinator with health monitor
coordinator = RecoveryCoordinator(
    health_monitor=health_monitor
)

# Register recovery actions
coordinator.register_recovery(
    'PerformanceMonitor',
    RecoveryStrategy.RESTART,
    action=lambda: performance_monitor.restart()
)

# Enable auto-recovery
coordinator.enable_auto_recovery()

# Start monitoring
health_monitor.start()

# System will now automatically recover from failures!
```

**Auto-Recovery Flow:**
1. SystemHealthMonitor detects component failure (ERROR or CRITICAL alert)
2. Alert sent to RecoveryCoordinator
3. RecoveryCoordinator executes registered recovery actions
4. If successful, component returns to healthy state
5. If failed, error is logged and reported

### Recovery History

```python
# Get all recovery history
history = coordinator.get_recovery_history()

# Filter by component
history = coordinator.get_recovery_history(component='PerformanceMonitor')

# Limit results
history = coordinator.get_recovery_history(limit=10)

# Process history
for record in history:
    print(f"[{record['status']}] {record['component']}")
    print(f"  Strategy: {record['strategy']}")
    print(f"  Attempts: {record['attempts']}")
    print(f"  Duration: {record['duration']:.2f}s")
    print(f"  Message: {record['message']}")
    if record['error']:
        print(f"  Error: {record['error']}")
```

**Recovery Record:**
```python
{
    'timestamp': 1738119960.0,
    'component': 'PerformanceMonitor',
    'strategy': 'restart',
    'status': 'success',
    'attempts': 2,
    'duration': 1.23,
    'message': 'Recovery completed successfully',
    'error': None
}
```

### Statistics

```python
stats = coordinator.get_statistics()

print(f"Auto-recovery: {stats['auto_recovery_enabled']}")
print(f"Total recoveries: {stats['total_recoveries']}")
print(f"Successful: {stats['successful_recoveries']}")
print(f"Failed: {stats['failed_recoveries']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Registered components: {stats['registered_components']}")
print(f"Components: {', '.join(stats['components'])}")
```

### Managing Recovery

```python
# Reset recovery attempts for a component
coordinator.reset_attempts('PerformanceMonitor')

# Reset all attempts
coordinator.reset_attempts()

# Clear recovery history
coordinator.clear_history()

# Unregister specific strategy
coordinator.unregister_recovery(
    'GameDetection',
    strategy=RecoveryStrategy.RESTART
)

# Unregister all strategies for component
coordinator.unregister_recovery('GameDetection')
```

## Integration Examples

### Complete Monitoring & Recovery System

```python
from core.error_reporter import ErrorReporter
from core.system_health_monitor import SystemHealthMonitor
from core.recovery_coordinator import RecoveryCoordinator, RecoveryStrategy

class Application:
    def __init__(self):
        # Create error reporter
        self.error_reporter = ErrorReporter()
        
        # Create health monitor with error reporter
        self.health_monitor = SystemHealthMonitor(
            check_interval=5.0,
            error_reporter=self.error_reporter
        )
        
        # Create recovery coordinator
        self.recovery_coordinator = RecoveryCoordinator(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter
        )
        
        # Components
        self.performance_monitor = None
        self.game_detection = None
        self.config_manager = None
    
    def setup_monitoring(self):
        """Setup monitoring for all components"""
        # Register health checks
        self.health_monitor.register_component(
            'PerformanceMonitor',
            health_check=lambda: self.performance_monitor.is_running(),
            get_metrics=lambda: self.performance_monitor.get_status(),
            critical=False
        )
        
        self.health_monitor.register_component(
            'GameDetection',
            health_check=lambda: self.game_detection.is_running(),
            critical=False
        )
        
        self.health_monitor.register_component(
            'ConfigManager',
            health_check=lambda: self.config_manager.is_healthy(),
            critical=True
        )
        
        # Register recovery actions
        self.recovery_coordinator.register_recovery(
            'PerformanceMonitor',
            RecoveryStrategy.RESTART,
            action=lambda: self.performance_monitor.restart(),
            max_attempts=3,
            cooldown=30.0
        )
        
        self.recovery_coordinator.register_recovery(
            'GameDetection',
            RecoveryStrategy.RESTART,
            action=lambda: self.game_detection.restart(),
            max_attempts=3,
            cooldown=30.0
        )
        
        self.recovery_coordinator.register_recovery(
            'ConfigManager',
            RecoveryStrategy.RELOAD,
            action=lambda: self.config_manager.reload(),
            rollback_action=lambda: self.config_manager.restore_backup(),
            max_attempts=2,
            cooldown=60.0
        )
        
        # Enable auto-recovery
        self.recovery_coordinator.enable_auto_recovery()
    
    def start(self):
        """Start application with monitoring"""
        # Initialize components
        self.performance_monitor.start()
        self.game_detection.start()
        
        # Setup monitoring
        self.setup_monitoring()
        
        # Start health monitoring
        self.health_monitor.start()
        
        print("Application started with auto-recovery enabled")
    
    def get_system_status(self):
        """Get complete system status"""
        return {
            'health': self.health_monitor.get_system_health(),
            'recovery': self.recovery_coordinator.get_statistics(),
            'errors': self.error_reporter.get_statistics()
        }
```

### Custom Recovery Strategies

```python
class CustomRecovery:
    def __init__(self, coordinator):
        self.coordinator = coordinator
    
    def register_database_recovery(self, db_manager):
        """Register database recovery strategies"""
        # Try reconnect first
        self.coordinator.register_recovery(
            'Database',
            RecoveryStrategy.RESTART,
            action=lambda: db_manager.reconnect(),
            max_attempts=3,
            cooldown=10.0
        )
        
        # Try pool reset if reconnect fails
        self.coordinator.register_recovery(
            'Database',
            RecoveryStrategy.RESET,
            action=lambda: db_manager.reset_connection_pool(),
            max_attempts=2,
            cooldown=30.0
        )
        
        # Failover to backup if all else fails
        self.coordinator.register_recovery(
            'Database',
            RecoveryStrategy.FAILOVER,
            action=lambda: db_manager.failover_to_backup(),
            max_attempts=1,
            cooldown=300.0
        )
    
    def register_api_recovery(self, api_client):
        """Register API client recovery"""
        # Save state before recovery
        saved_state = {}
        
        def save_state():
            saved_state['config'] = api_client.get_config()
            saved_state['auth'] = api_client.get_auth_token()
            return True
        
        def restore_state():
            api_client.set_config(saved_state.get('config'))
            api_client.set_auth_token(saved_state.get('auth'))
            return True
        
        def recreate_client():
            save_state()
            api_client.close()
            api_client.initialize()
            return api_client.is_connected()
        
        self.coordinator.register_recovery(
            'APIClient',
            RecoveryStrategy.RESET,
            action=recreate_client,
            rollback_action=restore_state,
            max_attempts=2,
            cooldown=15.0
        )
```

## Recovery Flow

### Manual Recovery

```
User/System → recover_component()
    ↓
Check registered actions
    ↓
Check cooldown period
    ↓
Check max attempts
    ↓
Execute recovery action
    ↓
  Success? → YES → Reset attempts, Record success
    ↓ NO
  Execute rollback (if registered)
    ↓
  Increment attempts, Record failure
```

### Auto-Recovery

```
SystemHealthMonitor → Component failure detected
    ↓
Generate ERROR/CRITICAL alert
    ↓
RecoveryCoordinator receives alert
    ↓
Auto-recovery enabled? → YES → recover_component()
    ↓
Component recovered
    ↓
SystemHealthMonitor sees healthy status
```

## Best Practices

### 1. Choose Appropriate Strategies

```python
# RESTART: For stateless services
coordinator.register_recovery(
    'StatelessService',
    RecoveryStrategy.RESTART,
    action=lambda: service.restart()
)

# RELOAD: For configuration changes
coordinator.register_recovery(
    'ConfigService',
    RecoveryStrategy.RELOAD,
    action=lambda: service.reload_config()
)

# ROLLBACK: For state changes
coordinator.register_recovery(
    'StatefulService',
    RecoveryStrategy.ROLLBACK,
    action=lambda: service.rollback_transaction(),
    rollback_action=lambda: service.restore_checkpoint()
)

# FAILOVER: For critical services with backups
coordinator.register_recovery(
    'CriticalService',
    RecoveryStrategy.FAILOVER,
    action=lambda: service.failover_to_backup()
)
```

### 2. Set Appropriate Limits

```python
# Fast-recovering components
coordinator.register_recovery(
    'LightweightService',
    RecoveryStrategy.RESTART,
    action=restart_action,
    max_attempts=5,      # More attempts
    cooldown=10.0        # Short cooldown
)

# Slow-recovering components
coordinator.register_recovery(
    'HeavyService',
    RecoveryStrategy.RESTART,
    action=restart_action,
    max_attempts=2,      # Fewer attempts
    cooldown=300.0       # Long cooldown (5 min)
)
```

### 3. Implement Proper Rollback

```python
def safe_recovery():
    # Save current state
    checkpoint = service.create_checkpoint()
    
    def rollback():
        service.restore_checkpoint(checkpoint)
        return True
    
    def recover():
        try:
            service.update_to_new_version()
            service.restart()
            return service.is_healthy()
        except Exception:
            return False
    
    coordinator.register_recovery(
        'Service',
        RecoveryStrategy.ROLLBACK,
        action=recover,
        rollback_action=rollback
    )
```

### 4. Monitor Recovery Operations

```python
# Regular monitoring
def check_recovery_health():
    stats = coordinator.get_statistics()
    
    # Alert if success rate drops
    if stats['total_recoveries'] > 10:
        if stats['success_rate'] < 50.0:
            alert_admin("Low recovery success rate")
    
    # Check recent failures
    history = coordinator.get_recovery_history(limit=10)
    recent_failures = [r for r in history if r['status'] == 'failed']
    
    if len(recent_failures) > 5:
        alert_admin("High failure rate in recent recoveries")

# Schedule regular checks
scheduler.every(5).minutes.do(check_recovery_health)
```

## Configuration

```python
class RecoveryConfig:
    # Default max attempts
    DEFAULT_MAX_ATTEMPTS = 3
    
    # Default cooldown period
    DEFAULT_COOLDOWN = 30.0
    
    # Maximum recovery history
    MAX_HISTORY_RECORDS = 100
    
    # Auto-recovery settings
    AUTO_RECOVERY_ENABLED = True
    AUTO_RECOVERY_MIN_ALERT_LEVEL = AlertLevel.ERROR
    
    # Component-specific settings
    COMPONENT_SETTINGS = {
        'ConfigManager': {
            'max_attempts': 2,
            'cooldown': 60.0,
            'strategies': [RecoveryStrategy.RELOAD, RecoveryStrategy.ROLLBACK]
        },
        'PerformanceMonitor': {
            'max_attempts': 5,
            'cooldown': 15.0,
            'strategies': [RecoveryStrategy.RESTART]
        }
    }
```

## See Also

- [ErrorReporter](ERROR_REPORTING.md) - Error collection and reporting
- [SystemHealthMonitor](SYSTEM_HEALTH.md) - Health monitoring
- [Stage 7.7b.6 Summary](STAGE_7.7b.6_SUMMARY.md) - Complete error recovery system
