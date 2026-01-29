#!/usr/bin/env python3
"""System Health Monitor

Version: 0.3.5r (package 3.9a, stage 7.7b.6.2/7.7)

Package 3.9a Stage 7.7b.6.2: System-wide health monitoring.

Features:
- Component health monitoring
- Status aggregation
- Health metrics dashboard
- Real-time health updates
- Alert system
- Integration with ErrorReporter
"""
import threading
import time
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

try:
    from error_reporter import ErrorReporter, ErrorSeverity
    ERROR_REPORTER_AVAILABLE = True
except ImportError:
    ERROR_REPORTER_AVAILABLE = False


class ComponentStatus(Enum):
    """Component health status"""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    OFFLINE = "offline"


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ComponentHealth:
    """Component health information
    
    Attributes:
        name: Component name
        status: Current status
        message: Status message
        metrics: Health metrics dict
        last_check: Last check timestamp
        consecutive_failures: Number of consecutive check failures
    """
    name: str
    status: ComponentStatus
    message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_check: float = 0.0
    consecutive_failures: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'status': self.status.value,
            'message': self.message,
            'metrics': self.metrics,
            'last_check': self.last_check,
            'consecutive_failures': self.consecutive_failures,
        }


@dataclass
class HealthAlert:
    """Health alert
    
    Attributes:
        timestamp: Alert timestamp
        level: Alert level
        component: Component name
        message: Alert message
        details: Additional details
    """
    timestamp: float
    level: AlertLevel
    component: str
    message: str
    details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'level': self.level.value,
            'component': self.component,
            'message': self.message,
            'details': self.details,
        }


class SystemHealthMonitor:
    """System-wide health monitor
    
    v0.3.5r (package 3.9a, stage 7.7b.6.2/7.7)
    
    Features:
    - Component health monitoring
    - Status aggregation
    - Health metrics dashboard
    - Real-time updates
    - Alert system
    - Error reporter integration
    
    Usage:
        >>> monitor = SystemHealthMonitor(check_interval=5.0)
        >>> 
        >>> # Register components
        >>> monitor.register_component(
        ...     'PerformanceMonitor',
        ...     health_check=lambda: performance_monitor.is_healthy()
        ... )
        >>> 
        >>> # Start monitoring
        >>> monitor.start()
        >>> 
        >>> # Get health status
        >>> health = monitor.get_system_health()
        >>> print(f"System healthy: {health['healthy']}")
        >>> 
        >>> # Stop monitoring
        >>> monitor.stop()
    """
    
    def __init__(
        self,
        check_interval: float = 5.0,
        error_reporter: Optional[Any] = None
    ):
        """Initialize health monitor
        
        Args:
            check_interval: Health check interval in seconds
            error_reporter: Optional ErrorReporter instance
        """
        self._check_interval = max(1.0, check_interval)
        self._error_reporter = error_reporter
        self._lock = threading.RLock()
        self._logger = None
        
        # Component tracking
        self._components: Dict[str, Dict[str, Any]] = {}
        self._component_health: Dict[str, ComponentHealth] = {}
        
        # Monitoring thread
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Alerts
        self._alerts: List[HealthAlert] = []
        self._max_alerts = 100
        self._alert_callbacks: List[Callable[[HealthAlert], None]] = []
        
        # Statistics
        self._total_checks = 0
        self._failed_checks = 0
        self._start_time = 0.0
        
        # Get logger
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug("SystemHealthMonitor initializing")
            except Exception:
                pass
        
        self._log_info("Initialized")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="HealthMonitor")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="HealthMonitor")
        else:
            print(f"[HealthMonitor] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="HealthMonitor")
        else:
            print(f"[HealthMonitor] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="HealthMonitor", exc_info=exc_info)
        else:
            print(f"[HealthMonitor] ERROR: {message}")
    
    def register_component(
        self,
        name: str,
        health_check: Callable[[], bool],
        get_metrics: Optional[Callable[[], Dict[str, Any]]] = None,
        critical: bool = False
    ) -> bool:
        """Register a component for monitoring
        
        Args:
            name: Component name
            health_check: Health check function returning bool
            get_metrics: Optional metrics getter function
            critical: Whether component is critical for system health
        
        Returns:
            True if registered successfully
        """
        try:
            if not name or not health_check:
                self._log_error("Invalid component name or health check")
                return False
            
            with self._lock:
                if name in self._components:
                    self._log_warning(f"Component {name} already registered")
                    return False
                
                # Register component
                self._components[name] = {
                    'health_check': health_check,
                    'get_metrics': get_metrics,
                    'critical': critical,
                }
                
                # Initialize health
                self._component_health[name] = ComponentHealth(
                    name=name,
                    status=ComponentStatus.UNKNOWN,
                    message="Not checked yet"
                )
            
            self._log_info(f"Registered component: {name} (critical: {critical})")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to register component {name}: {e}", exc_info=True)
            return False
    
    def unregister_component(self, name: str) -> bool:
        """Unregister a component
        
        Args:
            name: Component name
        
        Returns:
            True if unregistered successfully
        """
        try:
            with self._lock:
                if name not in self._components:
                    self._log_warning(f"Component {name} not registered")
                    return False
                
                del self._components[name]
                del self._component_health[name]
            
            self._log_info(f"Unregistered component: {name}")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to unregister component {name}: {e}")
            return False
    
    def start(self) -> bool:
        """Start health monitoring
        
        Returns:
            True if started successfully
        """
        try:
            with self._lock:
                if self._running:
                    self._log_debug("Already running")
                    return True
                
                self._running = True
                self._start_time = time.time()
            
            # Start monitor thread
            self._monitor_thread = threading.Thread(
                target=self._monitor_worker,
                name='HealthMonitor',
                daemon=True
            )
            self._monitor_thread.start()
            
            self._log_info("Started")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to start: {e}", exc_info=True)
            with self._lock:
                self._running = False
            return False
    
    def stop(self) -> bool:
        """Stop health monitoring
        
        Returns:
            True if stopped successfully
        """
        try:
            with self._lock:
                if not self._running:
                    self._log_debug("Already stopped")
                    return True
                
                self._running = False
            
            # Wait for thread
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2.0)
            
            self._log_info("Stopped")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to stop: {e}")
            return False
    
    def _monitor_worker(self):
        """Health monitoring worker thread"""
        self._log_debug("Monitor worker started")
        
        while self._running:
            try:
                # Check all components
                self._check_all_components()
                
                # Sleep
                time.sleep(self._check_interval)
            
            except Exception as e:
                self._log_error(f"Monitor worker error: {e}", exc_info=True)
                time.sleep(1.0)
        
        self._log_debug("Monitor worker stopped")
    
    def _check_all_components(self):
        """Check health of all components"""
        with self._lock:
            components = list(self._components.items())
        
        for name, config in components:
            self._check_component(name, config)
    
    def _check_component(self, name: str, config: Dict[str, Any]):
        """Check health of a single component
        
        Args:
            name: Component name
            config: Component configuration
        """
        try:
            # Get health check function
            health_check = config['health_check']
            get_metrics = config.get('get_metrics')
            is_critical = config.get('critical', False)
            
            # Run health check
            is_healthy = False
            try:
                result = health_check()
                is_healthy = bool(result)
            except Exception as e:
                self._log_warning(f"Health check failed for {name}: {e}")
                is_healthy = False
            
            # Get metrics
            metrics = {}
            if get_metrics:
                try:
                    metrics = get_metrics()
                except Exception as e:
                    self._log_warning(f"Failed to get metrics for {name}: {e}")
            
            # Update health
            with self._lock:
                health = self._component_health.get(name)
                if not health:
                    return
                
                old_status = health.status
                
                # Determine new status
                if is_healthy:
                    health.status = ComponentStatus.HEALTHY
                    health.message = "Operating normally"
                    health.consecutive_failures = 0
                else:
                    health.consecutive_failures += 1
                    
                    if health.consecutive_failures >= 3:
                        if is_critical:
                            health.status = ComponentStatus.CRITICAL
                            health.message = "Critical component failure"
                        else:
                            health.status = ComponentStatus.UNHEALTHY
                            health.message = "Component not responding"
                    else:
                        health.status = ComponentStatus.DEGRADED
                        health.message = "Intermittent issues detected"
                
                health.metrics = metrics
                health.last_check = time.time()
                
                # Update statistics
                self._total_checks += 1
                if not is_healthy:
                    self._failed_checks += 1
                
                # Check for status change
                if old_status != health.status:
                    self._handle_status_change(health, old_status)
        
        except Exception as e:
            self._log_error(f"Error checking component {name}: {e}", exc_info=True)
    
    def _handle_status_change(
        self,
        health: ComponentHealth,
        old_status: ComponentStatus
    ):
        """Handle component status change
        
        Args:
            health: Component health
            old_status: Previous status
        """
        try:
            self._log_info(
                f"Component {health.name} status changed: "
                f"{old_status.value} → {health.status.value}"
            )
            
            # Determine alert level
            alert_level = AlertLevel.INFO
            
            if health.status == ComponentStatus.CRITICAL:
                alert_level = AlertLevel.CRITICAL
            elif health.status == ComponentStatus.UNHEALTHY:
                alert_level = AlertLevel.ERROR
            elif health.status == ComponentStatus.DEGRADED:
                alert_level = AlertLevel.WARNING
            elif health.status == ComponentStatus.HEALTHY:
                alert_level = AlertLevel.INFO
            
            # Create alert
            alert = HealthAlert(
                timestamp=time.time(),
                level=alert_level,
                component=health.name,
                message=f"Status changed to {health.status.value}",
                details=health.message
            )
            
            # Store alert
            self._alerts.append(alert)
            if len(self._alerts) > self._max_alerts:
                self._alerts = self._alerts[-self._max_alerts:]
            
            # Report to error reporter
            if self._error_reporter and ERROR_REPORTER_AVAILABLE:
                severity = self._alert_level_to_error_severity(alert_level)
                try:
                    self._error_reporter.report_error(
                        component=health.name,
                        severity=severity,
                        message=alert.message,
                        details=alert.details
                    )
                except Exception as e:
                    self._log_warning(f"Failed to report to ErrorReporter: {e}")
            
            # Notify callbacks
            self._notify_alert_callbacks(alert)
        
        except Exception as e:
            self._log_error(f"Error handling status change: {e}", exc_info=True)
    
    def _alert_level_to_error_severity(self, level: AlertLevel) -> Any:
        """Convert alert level to error severity
        
        Args:
            level: Alert level
        
        Returns:
            ErrorSeverity
        """
        if not ERROR_REPORTER_AVAILABLE:
            return None
        
        mapping = {
            AlertLevel.INFO: ErrorSeverity.INFO,
            AlertLevel.WARNING: ErrorSeverity.WARNING,
            AlertLevel.ERROR: ErrorSeverity.ERROR,
            AlertLevel.CRITICAL: ErrorSeverity.CRITICAL,
        }
        return mapping.get(level, ErrorSeverity.INFO)
    
    def _notify_alert_callbacks(self, alert: HealthAlert):
        """Notify alert callbacks with error isolation
        
        Args:
            alert: Health alert
        """
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self._log_error(f"Alert callback error: {e}", exc_info=True)
    
    def add_alert_callback(self, callback: Callable[[HealthAlert], None]) -> int:
        """Add alert callback
        
        Args:
            callback: Callback function(alert)
        
        Returns:
            Callback ID
        """
        try:
            with self._lock:
                callback_id = len(self._alert_callbacks)
                self._alert_callbacks.append(callback)
                self._log_debug(f"Added alert callback (ID: {callback_id})")
                return callback_id
        
        except Exception as e:
            self._log_error(f"Failed to add callback: {e}")
            return -1
    
    def get_component_health(self, name: str) -> Optional[Dict[str, Any]]:
        """Get health of a specific component
        
        Args:
            name: Component name
        
        Returns:
            Health dictionary or None
        """
        try:
            with self._lock:
                health = self._component_health.get(name)
                if not health:
                    return None
                return health.to_dict()
        
        except Exception as e:
            self._log_error(f"Failed to get component health: {e}")
            return None
    
    def get_all_components_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health of all components
        
        Returns:
            Dictionary of component health
        """
        try:
            with self._lock:
                return {
                    name: health.to_dict()
                    for name, health in self._component_health.items()
                }
        
        except Exception as e:
            self._log_error(f"Failed to get all components health: {e}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health
        
        Returns:
            System health dictionary
        """
        try:
            with self._lock:
                total = len(self._component_health)
                if total == 0:
                    return {
                        'healthy': True,
                        'status': 'unknown',
                        'message': 'No components registered',
                        'components': {},
                        'statistics': self._get_statistics(),
                    }
                
                # Count by status
                status_counts = defaultdict(int)
                critical_count = 0
                unhealthy_count = 0
                degraded_count = 0
                healthy_count = 0
                
                for health in self._component_health.values():
                    status_counts[health.status.value] += 1
                    
                    if health.status == ComponentStatus.CRITICAL:
                        critical_count += 1
                    elif health.status == ComponentStatus.UNHEALTHY:
                        unhealthy_count += 1
                    elif health.status == ComponentStatus.DEGRADED:
                        degraded_count += 1
                    elif health.status == ComponentStatus.HEALTHY:
                        healthy_count += 1
                
                # Determine overall status
                if critical_count > 0:
                    overall_status = 'critical'
                    overall_healthy = False
                    message = f"{critical_count} critical component(s)"
                elif unhealthy_count > 0:
                    overall_status = 'unhealthy'
                    overall_healthy = False
                    message = f"{unhealthy_count} unhealthy component(s)"
                elif degraded_count > 0:
                    overall_status = 'degraded'
                    overall_healthy = False
                    message = f"{degraded_count} degraded component(s)"
                else:
                    overall_status = 'healthy'
                    overall_healthy = True
                    message = "All components healthy"
                
                return {
                    'healthy': overall_healthy,
                    'status': overall_status,
                    'message': message,
                    'total_components': total,
                    'healthy_count': healthy_count,
                    'degraded_count': degraded_count,
                    'unhealthy_count': unhealthy_count,
                    'critical_count': critical_count,
                    'status_counts': dict(status_counts),
                    'components': self.get_all_components_health(),
                    'statistics': self._get_statistics(),
                }
        
        except Exception as e:
            self._log_error(f"Failed to get system health: {e}", exc_info=True)
            return {'error': str(e)}
    
    def _get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics
        
        Returns:
            Statistics dictionary
        """
        uptime = time.time() - self._start_time if self._start_time > 0 else 0
        
        success_rate = 0.0
        if self._total_checks > 0:
            success_rate = ((self._total_checks - self._failed_checks) / self._total_checks) * 100
        
        return {
            'running': self._running,
            'uptime': uptime,
            'total_checks': self._total_checks,
            'failed_checks': self._failed_checks,
            'success_rate': round(success_rate, 2),
            'check_interval': self._check_interval,
        }
    
    def get_recent_alerts(
        self,
        limit: Optional[int] = None,
        min_level: Optional[AlertLevel] = None
    ) -> List[Dict[str, Any]]:
        """Get recent alerts
        
        Args:
            limit: Maximum number of alerts
            min_level: Minimum alert level
        
        Returns:
            List of alert dictionaries
        """
        try:
            with self._lock:
                alerts = list(self._alerts)
            
            # Filter by level
            if min_level:
                level_order = {
                    AlertLevel.INFO: 0,
                    AlertLevel.WARNING: 1,
                    AlertLevel.ERROR: 2,
                    AlertLevel.CRITICAL: 3,
                }
                min_order = level_order.get(min_level, 0)
                alerts = [
                    a for a in alerts
                    if level_order.get(a.level, 0) >= min_order
                ]
            
            # Sort by timestamp (newest first)
            alerts.sort(key=lambda a: a.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                alerts = alerts[:limit]
            
            return [a.to_dict() for a in alerts]
        
        except Exception as e:
            self._log_error(f"Failed to get alerts: {e}")
            return []
    
    def clear_alerts(self):
        """Clear all alerts"""
        try:
            with self._lock:
                self._alerts.clear()
            self._log_debug("Cleared all alerts")
        
        except Exception as e:
            self._log_error(f"Failed to clear alerts: {e}")
    
    def is_running(self) -> bool:
        """Check if monitoring is running
        
        Returns:
            True if running
        """
        return self._running


# Testing
if __name__ == '__main__':
    print("="*80)
    print("SystemHealthMonitor Test")
    print("="*80)
    print()
    
    # Mock component
    class MockComponent:
        def __init__(self, name, healthy=True):
            self.name = name
            self.healthy = healthy
            self.check_count = 0
        
        def is_healthy(self):
            self.check_count += 1
            return self.healthy
        
        def get_metrics(self):
            return {
                'check_count': self.check_count,
                'status': 'ok' if self.healthy else 'failed'
            }
    
    # Create monitor
    monitor = SystemHealthMonitor(check_interval=1.0)
    
    # Create components
    comp1 = MockComponent("Component1", healthy=True)
    comp2 = MockComponent("Component2", healthy=True)
    comp3 = MockComponent("Component3", healthy=False)
    
    # Register components
    print("Registering components...")
    monitor.register_component('comp1', comp1.is_healthy, comp1.get_metrics, critical=False)
    monitor.register_component('comp2', comp2.is_healthy, comp2.get_metrics, critical=False)
    monitor.register_component('comp3', comp3.is_healthy, comp3.get_metrics, critical=True)
    print()
    
    # Add alert callback
    def on_alert(alert: HealthAlert):
        print(f"\n🔔 ALERT: [{alert.level.value.upper()}] {alert.component}")
        print(f"   Message: {alert.message}")
        if alert.details:
            print(f"   Details: {alert.details}")
    
    monitor.add_alert_callback(on_alert)
    
    # Start monitoring
    print("Starting monitoring...")
    monitor.start()
    print("✅ Started\n")
    
    # Wait for checks
    print("Running for 5 seconds...")
    time.sleep(5)
    
    # Get system health
    print("\nSystem Health:")
    health = monitor.get_system_health()
    print(f"  Status: {health['status']}")
    print(f"  Healthy: {health['healthy']}")
    print(f"  Message: {health['message']}")
    print(f"  Components: {health['total_components']}")
    print(f"    Healthy: {health['healthy_count']}")
    print(f"    Degraded: {health['degraded_count']}")
    print(f"    Unhealthy: {health['unhealthy_count']}")
    print(f"    Critical: {health['critical_count']}")
    print()
    
    # Get statistics
    stats = health['statistics']
    print("Statistics:")
    print(f"  Total checks: {stats['total_checks']}")
    print(f"  Failed checks: {stats['failed_checks']}")
    print(f"  Success rate: {stats['success_rate']}%")
    print()
    
    # Get recent alerts
    alerts = monitor.get_recent_alerts(limit=5)
    print(f"Recent Alerts ({len(alerts)}):")
    for alert in alerts:
        print(f"  [{alert['level'].upper()}] {alert['component']}: {alert['message']}")
    print()
    
    # Stop monitoring
    print("Stopping monitoring...")
    monitor.stop()
    print("✅ Stopped")
    
    print()
    print("✅ Test completed!")
