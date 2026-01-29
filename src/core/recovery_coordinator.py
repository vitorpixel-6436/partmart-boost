#!/usr/bin/env python3
"""Recovery Coordinator for Automatic Error Recovery

Version: 0.3.5s (package 3.9a, stage 7.7b.6.3/7.7)

Package 3.9a Stage 7.7b.6.3: Automatic recovery and self-healing.

Features:
- Automatic recovery strategies
- Recovery workflows
- Rollback mechanisms
- Emergency procedures
- Self-healing capabilities
- Integration with ErrorReporter and SystemHealthMonitor
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

try:
    from system_health_monitor import SystemHealthMonitor, ComponentStatus, AlertLevel
    HEALTH_MONITOR_AVAILABLE = True
except ImportError:
    HEALTH_MONITOR_AVAILABLE = False


class RecoveryStrategy(Enum):
    """Recovery strategy types"""
    RESTART = "restart"              # Restart component
    RELOAD = "reload"                # Reload configuration
    ROLLBACK = "rollback"            # Rollback to previous state
    RESET = "reset"                  # Reset to default state
    FAILOVER = "failover"            # Switch to backup
    MANUAL = "manual"                # Requires manual intervention


class RecoveryStatus(Enum):
    """Recovery operation status"""
    PENDING = "pending"              # Waiting to execute
    IN_PROGRESS = "in_progress"      # Currently executing
    SUCCESS = "success"              # Completed successfully
    FAILED = "failed"                # Failed to recover
    SKIPPED = "skipped"              # Skipped (conditions not met)


@dataclass
class RecoveryAction:
    """Recovery action definition
    
    Attributes:
        component: Component name
        strategy: Recovery strategy
        action: Action callable
        rollback_action: Optional rollback callable
        max_attempts: Maximum recovery attempts
        cooldown: Cooldown period between attempts (seconds)
    """
    component: str
    strategy: RecoveryStrategy
    action: Callable[[], bool]
    rollback_action: Optional[Callable[[], bool]] = None
    max_attempts: int = 3
    cooldown: float = 30.0


@dataclass
class RecoveryRecord:
    """Recovery operation record
    
    Attributes:
        timestamp: Operation timestamp
        component: Component name
        strategy: Strategy used
        status: Operation status
        attempts: Number of attempts
        duration: Operation duration
        message: Status message
        error: Error message (if failed)
    """
    timestamp: float
    component: str
    strategy: RecoveryStrategy
    status: RecoveryStatus
    attempts: int = 1
    duration: float = 0.0
    message: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'component': self.component,
            'strategy': self.strategy.value,
            'status': self.status.value,
            'attempts': self.attempts,
            'duration': self.duration,
            'message': self.message,
            'error': self.error,
        }


class RecoveryCoordinator:
    """Automatic recovery coordinator
    
    v0.3.5s (package 3.9a, stage 7.7b.6.3/7.7)
    
    Features:
    - Automatic recovery strategies
    - Recovery workflows
    - Rollback mechanisms
    - Emergency procedures
    - Self-healing
    - Full integration
    
    Usage:
        >>> coordinator = RecoveryCoordinator(
        ...     health_monitor=health_monitor,
        ...     error_reporter=error_reporter
        ... )
        >>> 
        >>> # Register recovery action
        >>> coordinator.register_recovery(
        ...     'PerformanceMonitor',
        ...     RecoveryStrategy.RESTART,
        ...     action=lambda: performance_monitor.restart()
        ... )
        >>> 
        >>> # Enable auto-recovery
        >>> coordinator.enable_auto_recovery()
        >>> 
        >>> # Manually trigger recovery
        >>> coordinator.recover_component('PerformanceMonitor')
    """
    
    def __init__(
        self,
        health_monitor: Optional[Any] = None,
        error_reporter: Optional[Any] = None
    ):
        """Initialize recovery coordinator
        
        Args:
            health_monitor: Optional SystemHealthMonitor instance
            error_reporter: Optional ErrorReporter instance
        """
        self._health_monitor = health_monitor
        self._error_reporter = error_reporter
        self._lock = threading.RLock()
        self._logger = None
        
        # Recovery actions
        self._recovery_actions: Dict[str, List[RecoveryAction]] = defaultdict(list)
        
        # Recovery tracking
        self._recovery_history: List[RecoveryRecord] = []
        self._max_history = 100
        self._last_recovery: Dict[str, float] = {}
        self._recovery_attempts: Dict[str, int] = defaultdict(int)
        
        # Auto-recovery
        self._auto_recovery_enabled = False
        self._auto_recovery_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Statistics
        self._total_recoveries = 0
        self._successful_recoveries = 0
        self._failed_recoveries = 0
        
        # Get logger
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug("RecoveryCoordinator initializing")
            except Exception:
                pass
        
        # Setup health monitor integration
        if self._health_monitor and HEALTH_MONITOR_AVAILABLE:
            try:
                self._health_monitor.add_alert_callback(self._on_health_alert)
                self._log_info("Connected to SystemHealthMonitor")
            except Exception as e:
                self._log_warning(f"Failed to connect to health monitor: {e}")
        
        self._log_info("Initialized")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="RecoveryCoordinator")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="RecoveryCoordinator")
        else:
            print(f"[RecoveryCoordinator] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="RecoveryCoordinator")
        else:
            print(f"[RecoveryCoordinator] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="RecoveryCoordinator", exc_info=exc_info)
        else:
            print(f"[RecoveryCoordinator] ERROR: {message}")
    
    def register_recovery(
        self,
        component: str,
        strategy: RecoveryStrategy,
        action: Callable[[], bool],
        rollback_action: Optional[Callable[[], bool]] = None,
        max_attempts: int = 3,
        cooldown: float = 30.0
    ) -> bool:
        """Register a recovery action
        
        Args:
            component: Component name
            strategy: Recovery strategy
            action: Recovery action callable returning bool
            rollback_action: Optional rollback action
            max_attempts: Maximum recovery attempts
            cooldown: Cooldown period between attempts
        
        Returns:
            True if registered successfully
        """
        try:
            if not component or not action:
                self._log_error("Invalid component or action")
                return False
            
            with self._lock:
                recovery = RecoveryAction(
                    component=component,
                    strategy=strategy,
                    action=action,
                    rollback_action=rollback_action,
                    max_attempts=max_attempts,
                    cooldown=cooldown
                )
                
                self._recovery_actions[component].append(recovery)
            
            self._log_info(
                f"Registered recovery: {component} - {strategy.value} "
                f"(attempts: {max_attempts}, cooldown: {cooldown}s)"
            )
            return True
        
        except Exception as e:
            self._log_error(f"Failed to register recovery: {e}", exc_info=True)
            return False
    
    def unregister_recovery(self, component: str, strategy: Optional[RecoveryStrategy] = None) -> bool:
        """Unregister recovery actions
        
        Args:
            component: Component name
            strategy: Optional specific strategy to remove
        
        Returns:
            True if unregistered successfully
        """
        try:
            with self._lock:
                if component not in self._recovery_actions:
                    self._log_warning(f"No recovery actions for {component}")
                    return False
                
                if strategy:
                    # Remove specific strategy
                    self._recovery_actions[component] = [
                        a for a in self._recovery_actions[component]
                        if a.strategy != strategy
                    ]
                else:
                    # Remove all
                    del self._recovery_actions[component]
            
            self._log_info(f"Unregistered recovery: {component}")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to unregister recovery: {e}")
            return False
    
    def recover_component(
        self,
        component: str,
        strategy: Optional[RecoveryStrategy] = None
    ) -> bool:
        """Manually trigger component recovery
        
        Args:
            component: Component name
            strategy: Optional specific strategy to use
        
        Returns:
            True if recovery succeeded
        """
        try:
            with self._lock:
                if component not in self._recovery_actions:
                    self._log_error(f"No recovery actions for {component}")
                    return False
                
                actions = self._recovery_actions[component]
                
                # Filter by strategy if specified
                if strategy:
                    actions = [a for a in actions if a.strategy == strategy]
                    if not actions:
                        self._log_error(f"No {strategy.value} recovery for {component}")
                        return False
            
            # Try recovery actions in order
            for action in actions:
                if self._execute_recovery(action):
                    return True
            
            return False
        
        except Exception as e:
            self._log_error(f"Failed to recover {component}: {e}", exc_info=True)
            return False
    
    def _execute_recovery(self, action: RecoveryAction) -> bool:
        """Execute a recovery action
        
        Args:
            action: Recovery action
        
        Returns:
            True if recovery succeeded
        """
        component = action.component
        strategy = action.strategy
        
        try:
            # Check cooldown
            now = time.time()
            last_recovery = self._last_recovery.get(component, 0)
            
            if now - last_recovery < action.cooldown:
                remaining = action.cooldown - (now - last_recovery)
                self._log_info(
                    f"Recovery for {component} on cooldown "
                    f"({remaining:.1f}s remaining)"
                )
                
                # Record skipped
                self._record_recovery(
                    component, strategy, RecoveryStatus.SKIPPED,
                    message=f"Cooldown period ({remaining:.1f}s remaining)"
                )
                return False
            
            # Check max attempts
            attempts = self._recovery_attempts.get(component, 0)
            if attempts >= action.max_attempts:
                self._log_error(
                    f"Max recovery attempts ({action.max_attempts}) "
                    f"reached for {component}"
                )
                
                # Record failed
                self._record_recovery(
                    component, strategy, RecoveryStatus.FAILED,
                    attempts=attempts,
                    message=f"Max attempts ({action.max_attempts}) reached"
                )
                return False
            
            # Execute recovery
            self._log_info(
                f"Executing recovery: {component} - {strategy.value} "
                f"(attempt {attempts + 1}/{action.max_attempts})"
            )
            
            start_time = time.time()
            
            try:
                result = action.action()
                duration = time.time() - start_time
                
                if result:
                    # Success
                    self._log_info(
                        f"Recovery succeeded: {component} "
                        f"({duration:.2f}s)"
                    )
                    
                    # Update tracking
                    with self._lock:
                        self._last_recovery[component] = now
                        self._recovery_attempts[component] = 0  # Reset
                        self._total_recoveries += 1
                        self._successful_recoveries += 1
                    
                    # Record success
                    self._record_recovery(
                        component, strategy, RecoveryStatus.SUCCESS,
                        attempts=attempts + 1,
                        duration=duration,
                        message="Recovery completed successfully"
                    )
                    
                    # Report success
                    if self._error_reporter and ERROR_REPORTER_AVAILABLE:
                        try:
                            self._error_reporter.report_error(
                                component=component,
                                severity=ErrorSeverity.INFO,
                                message=f"Recovery succeeded using {strategy.value}",
                                details=f"Duration: {duration:.2f}s, Attempt: {attempts + 1}"
                            )
                        except Exception:
                            pass
                    
                    return True
                
                else:
                    # Failed
                    self._log_error(f"Recovery failed: {component}")
                    
                    # Update tracking
                    with self._lock:
                        self._recovery_attempts[component] = attempts + 1
                        self._total_recoveries += 1
                        self._failed_recoveries += 1
                    
                    # Record failure
                    self._record_recovery(
                        component, strategy, RecoveryStatus.FAILED,
                        attempts=attempts + 1,
                        duration=duration,
                        message="Recovery action returned False"
                    )
                    
                    return False
            
            except Exception as e:
                duration = time.time() - start_time
                
                self._log_error(f"Recovery error for {component}: {e}", exc_info=True)
                
                # Update tracking
                with self._lock:
                    self._recovery_attempts[component] = attempts + 1
                    self._total_recoveries += 1
                    self._failed_recoveries += 1
                
                # Record failure
                self._record_recovery(
                    component, strategy, RecoveryStatus.FAILED,
                    attempts=attempts + 1,
                    duration=duration,
                    message="Recovery action raised exception",
                    error=str(e)
                )
                
                # Try rollback
                if action.rollback_action:
                    self._execute_rollback(action)
                
                return False
        
        except Exception as e:
            self._log_error(f"Error executing recovery: {e}", exc_info=True)
            return False
    
    def _execute_rollback(self, action: RecoveryAction):
        """Execute rollback action
        
        Args:
            action: Recovery action with rollback
        """
        try:
            if not action.rollback_action:
                return
            
            self._log_info(f"Executing rollback for {action.component}")
            
            result = action.rollback_action()
            
            if result:
                self._log_info(f"Rollback succeeded: {action.component}")
            else:
                self._log_error(f"Rollback failed: {action.component}")
        
        except Exception as e:
            self._log_error(f"Rollback error: {e}", exc_info=True)
    
    def _record_recovery(
        self,
        component: str,
        strategy: RecoveryStrategy,
        status: RecoveryStatus,
        attempts: int = 1,
        duration: float = 0.0,
        message: str = "",
        error: Optional[str] = None
    ):
        """Record recovery operation
        
        Args:
            component: Component name
            strategy: Strategy used
            status: Operation status
            attempts: Number of attempts
            duration: Operation duration
            message: Status message
            error: Error message
        """
        try:
            record = RecoveryRecord(
                timestamp=time.time(),
                component=component,
                strategy=strategy,
                status=status,
                attempts=attempts,
                duration=duration,
                message=message,
                error=error
            )
            
            with self._lock:
                self._recovery_history.append(record)
                
                # Trim history
                if len(self._recovery_history) > self._max_history:
                    self._recovery_history = self._recovery_history[-self._max_history:]
        
        except Exception as e:
            self._log_error(f"Failed to record recovery: {e}")
    
    def _on_health_alert(self, alert: Any):
        """Handle health monitor alert
        
        Args:
            alert: Health alert
        """
        try:
            if not self._auto_recovery_enabled:
                return
            
            # Only respond to ERROR and CRITICAL alerts
            if not HEALTH_MONITOR_AVAILABLE:
                return
            
            if alert.level not in (AlertLevel.ERROR, AlertLevel.CRITICAL):
                return
            
            component = alert.component
            
            self._log_info(
                f"Health alert received: {component} - {alert.level.value}"
            )
            
            # Trigger recovery
            self.recover_component(component)
        
        except Exception as e:
            self._log_error(f"Error handling health alert: {e}", exc_info=True)
    
    def enable_auto_recovery(self) -> bool:
        """Enable automatic recovery
        
        Returns:
            True if enabled successfully
        """
        try:
            with self._lock:
                self._auto_recovery_enabled = True
            
            self._log_info("Auto-recovery enabled")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to enable auto-recovery: {e}")
            return False
    
    def disable_auto_recovery(self) -> bool:
        """Disable automatic recovery
        
        Returns:
            True if disabled successfully
        """
        try:
            with self._lock:
                self._auto_recovery_enabled = False
            
            self._log_info("Auto-recovery disabled")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to disable auto-recovery: {e}")
            return False
    
    def is_auto_recovery_enabled(self) -> bool:
        """Check if auto-recovery is enabled
        
        Returns:
            True if enabled
        """
        return self._auto_recovery_enabled
    
    def get_recovery_history(
        self,
        component: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get recovery history
        
        Args:
            component: Filter by component
            limit: Maximum number of records
        
        Returns:
            List of recovery records
        """
        try:
            with self._lock:
                history = list(self._recovery_history)
            
            # Filter by component
            if component:
                history = [r for r in history if r.component == component]
            
            # Sort by timestamp (newest first)
            history.sort(key=lambda r: r.timestamp, reverse=True)
            
            # Apply limit
            if limit:
                history = history[:limit]
            
            return [r.to_dict() for r in history]
        
        except Exception as e:
            self._log_error(f"Failed to get recovery history: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            with self._lock:
                success_rate = 0.0
                if self._total_recoveries > 0:
                    success_rate = (self._successful_recoveries / self._total_recoveries) * 100
                
                return {
                    'auto_recovery_enabled': self._auto_recovery_enabled,
                    'total_recoveries': self._total_recoveries,
                    'successful_recoveries': self._successful_recoveries,
                    'failed_recoveries': self._failed_recoveries,
                    'success_rate': round(success_rate, 2),
                    'registered_components': len(self._recovery_actions),
                    'components': list(self._recovery_actions.keys()),
                }
        
        except Exception as e:
            self._log_error(f"Failed to get statistics: {e}")
            return {'error': str(e)}
    
    def clear_history(self):
        """Clear recovery history"""
        try:
            with self._lock:
                self._recovery_history.clear()
            self._log_debug("Cleared recovery history")
        
        except Exception as e:
            self._log_error(f"Failed to clear history: {e}")
    
    def reset_attempts(self, component: Optional[str] = None):
        """Reset recovery attempts counter
        
        Args:
            component: Specific component or None for all
        """
        try:
            with self._lock:
                if component:
                    self._recovery_attempts[component] = 0
                    self._log_info(f"Reset attempts for {component}")
                else:
                    self._recovery_attempts.clear()
                    self._log_info("Reset all attempts")
        
        except Exception as e:
            self._log_error(f"Failed to reset attempts: {e}")


# Testing
if __name__ == '__main__':
    print("="*80)
    print("RecoveryCoordinator Test")
    print("="*80)
    print()
    
    # Mock component
    class MockComponent:
        def __init__(self, name):
            self.name = name
            self.running = False
            self.restart_count = 0
        
        def start(self):
            self.running = True
            return True
        
        def stop(self):
            self.running = False
            return True
        
        def restart(self):
            self.restart_count += 1
            print(f"  [{self.name}] Restarting... (count: {self.restart_count})")
            time.sleep(0.1)
            self.running = True
            return True
        
        def is_running(self):
            return self.running
    
    # Create coordinator
    coordinator = RecoveryCoordinator()
    
    # Create component
    component = MockComponent("TestService")
    
    # Register recovery
    print("Registering recovery action...")
    coordinator.register_recovery(
        'TestService',
        RecoveryStrategy.RESTART,
        action=component.restart,
        max_attempts=3,
        cooldown=2.0
    )
    print()
    
    # Trigger recovery
    print("Triggering recovery...")
    result = coordinator.recover_component('TestService')
    print(f"✅ Recovery {'succeeded' if result else 'failed'}\n")
    
    # Get statistics
    stats = coordinator.get_statistics()
    print("Statistics:")
    print(f"  Total recoveries: {stats['total_recoveries']}")
    print(f"  Successful: {stats['successful_recoveries']}")
    print(f"  Failed: {stats['failed_recoveries']}")
    print(f"  Success rate: {stats['success_rate']}%")
    print()
    
    # Get history
    history = coordinator.get_recovery_history(limit=5)
    print(f"Recovery History ({len(history)}):")
    for record in history:
        print(f"  [{record['status']}] {record['component']} - {record['strategy']}")
        print(f"    Message: {record['message']}")
        print(f"    Duration: {record['duration']:.2f}s")
    print()
    
    print("✅ Test completed!")
