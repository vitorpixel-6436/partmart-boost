#!/usr/bin/env python3
"""Error Handler

Version: 0.3.5j (package 3.9a, stage 7.7b/7.7)

Package 3.9a Stage 7.7b: Error handling and robustness.

Features:
- Centralized error handling
- Error recovery strategies
- Graceful degradation
- Error reporting
- Context preservation
"""
import sys
import traceback
import threading
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


@dataclass
class ErrorContext:
    """Error context information"""
    component: str
    operation: str
    severity: ErrorSeverity
    error_type: str
    error_message: str
    traceback: Optional[str]
    timestamp: datetime
    thread_id: int
    recoverable: bool = True
    recovery_attempted: bool = False
    recovery_successful: bool = False


class ErrorHandler:
    """Centralized Error Handler
    
    v0.3.5j (package 3.9a, stage 7.7b/7.7)
    
    Features:
    - Error capturing and logging
    - Recovery strategies
    - Error callbacks
    - Statistics tracking
    
    Usage:
        >>> handler = ErrorHandler()
        >>> 
        >>> try:
        ...     risky_operation()
        >>> except Exception as e:
        ...     handler.handle_error(
        ...         component='ComponentName',
        ...         operation='operation_name',
        ...         error=e,
        ...         severity=ErrorSeverity.ERROR,
        ...         recoverable=True
        ...     )
    """
    
    _instance: Optional['ErrorHandler'] = None
    _lock = threading.Lock()
    
    def __init__(self, max_errors: int = 1000):
        """Initialize error handler
        
        Args:
            max_errors: Maximum errors to keep in history
        """
        self._errors: list[ErrorContext] = []
        self._max_errors = max_errors
        self._callbacks: list[Callable[[ErrorContext], None]] = []
        self._recovery_strategies: Dict[str, Callable] = {}
        self._stats = {
            'total_errors': 0,
            'by_severity': {s: 0 for s in ErrorSeverity},
            'by_component': {},
            'recoveries_attempted': 0,
            'recoveries_successful': 0,
        }
        self._lock_errors = threading.RLock()
    
    @classmethod
    def get_instance(cls) -> 'ErrorHandler':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def handle_error(
        self,
        component: str,
        operation: str,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recoverable: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Handle an error
        
        Args:
            component: Component name
            operation: Operation name
            error: Exception object
            severity: Error severity
            recoverable: Whether error is recoverable
            context: Additional context
        
        Returns:
            True if error was handled successfully
        """
        # Create error context
        error_ctx = ErrorContext(
            component=component,
            operation=operation,
            severity=severity,
            error_type=type(error).__name__,
            error_message=str(error),
            traceback=traceback.format_exc() if severity >= ErrorSeverity.ERROR else None,
            timestamp=datetime.now(),
            thread_id=threading.get_ident(),
            recoverable=recoverable
        )
        
        # Store error
        with self._lock_errors:
            self._errors.append(error_ctx)
            if len(self._errors) > self._max_errors:
                self._errors.pop(0)
            
            # Update statistics
            self._stats['total_errors'] += 1
            self._stats['by_severity'][severity] += 1
            
            if component not in self._stats['by_component']:
                self._stats['by_component'][component] = 0
            self._stats['by_component'][component] += 1
        
        # Print error
        self._print_error(error_ctx)
        
        # Notify callbacks
        self._notify_callbacks(error_ctx)
        
        # Attempt recovery if possible
        if recoverable:
            return self._attempt_recovery(error_ctx, context)
        
        return False
    
    def _print_error(self, ctx: ErrorContext):
        """Print error to console"""
        severity_icons = {
            ErrorSeverity.DEBUG: '🔍',
            ErrorSeverity.INFO: 'ℹ️',
            ErrorSeverity.WARNING: '⚠️',
            ErrorSeverity.ERROR: '❌',
            ErrorSeverity.CRITICAL: '🔥',
        }
        
        icon = severity_icons.get(ctx.severity, '❓')
        timestamp = ctx.timestamp.strftime('%H:%M:%S.%f')[:-3]
        
        print(f"{icon} [{timestamp}] {ctx.severity.name}: {ctx.component}.{ctx.operation}")
        print(f"   {ctx.error_type}: {ctx.error_message}")
        
        if ctx.traceback and ctx.severity >= ErrorSeverity.ERROR:
            print(f"   Traceback:")
            for line in ctx.traceback.split('\n')[-5:]:
                if line.strip():
                    print(f"      {line}")
    
    def _notify_callbacks(self, ctx: ErrorContext):
        """Notify error callbacks"""
        for callback in self._callbacks:
            try:
                callback(ctx)
            except Exception as e:
                print(f"Error in error callback: {e}")
    
    def _attempt_recovery(self, ctx: ErrorContext, context: Optional[Dict[str, Any]]) -> bool:
        """Attempt error recovery
        
        Args:
            ctx: Error context
            context: Additional context
        
        Returns:
            True if recovery successful
        """
        ctx.recovery_attempted = True
        self._stats['recoveries_attempted'] += 1
        
        # Try component-specific recovery
        recovery_key = f"{ctx.component}.{ctx.operation}"
        if recovery_key in self._recovery_strategies:
            try:
                recovery_func = self._recovery_strategies[recovery_key]
                result = recovery_func(ctx, context)
                
                if result:
                    ctx.recovery_successful = True
                    self._stats['recoveries_successful'] += 1
                    print(f"   ✅ Recovery successful")
                    return True
            
            except Exception as e:
                print(f"   ❌ Recovery failed: {e}")
        
        return False
    
    def register_recovery_strategy(
        self,
        component: str,
        operation: str,
        strategy: Callable[[ErrorContext, Optional[Dict]], bool]
    ):
        """Register recovery strategy
        
        Args:
            component: Component name
            operation: Operation name
            strategy: Recovery function
        """
        key = f"{component}.{operation}"
        self._recovery_strategies[key] = strategy
    
    def add_callback(self, callback: Callable[[ErrorContext], None]):
        """Add error callback
        
        Args:
            callback: Callback function
        """
        self._callbacks.append(callback)
    
    def get_recent_errors(self, count: int = 10) -> list[ErrorContext]:
        """Get recent errors
        
        Args:
            count: Number of errors to return
        
        Returns:
            List of recent errors
        """
        with self._lock_errors:
            return self._errors[-count:]
    
    def get_errors_by_component(self, component: str) -> list[ErrorContext]:
        """Get errors for specific component
        
        Args:
            component: Component name
        
        Returns:
            List of errors
        """
        with self._lock_errors:
            return [e for e in self._errors if e.component == component]
    
    def get_errors_by_severity(self, severity: ErrorSeverity) -> list[ErrorContext]:
        """Get errors by severity
        
        Args:
            severity: Error severity
        
        Returns:
            List of errors
        """
        with self._lock_errors:
            return [e for e in self._errors if e.severity == severity]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics
        
        Returns:
            Statistics dictionary
        """
        with self._lock_errors:
            stats = self._stats.copy()
            
            # Calculate recovery rate
            if stats['recoveries_attempted'] > 0:
                stats['recovery_rate'] = (
                    stats['recoveries_successful'] / stats['recoveries_attempted'] * 100
                )
            else:
                stats['recovery_rate'] = 0.0
            
            return stats
    
    def clear(self):
        """Clear error history"""
        with self._lock_errors:
            self._errors.clear()
    
    def print_summary(self):
        """Print error summary"""
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print("ERROR SUMMARY")
        print("="*50)
        print(f"Total errors: {stats['total_errors']}")
        print()
        print("By severity:")
        for severity, count in stats['by_severity'].items():
            if count > 0:
                print(f"  {severity.name}: {count}")
        print()
        print("By component:")
        for component, count in sorted(stats['by_component'].items()):
            print(f"  {component}: {count}")
        print()
        print(f"Recoveries: {stats['recoveries_successful']}/{stats['recoveries_attempted']}")
        print(f"Recovery rate: {stats['recovery_rate']:.1f}%")
        print("="*50 + "\n")


def safe_execute(
    func: Callable,
    component: str,
    operation: str,
    default: Any = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    **kwargs
) -> Any:
    """Safely execute a function with error handling
    
    Args:
        func: Function to execute
        component: Component name
        operation: Operation name
        default: Default return value on error
        severity: Error severity
        **kwargs: Arguments for function
    
    Returns:
        Function result or default value
    """
    try:
        return func(**kwargs)
    except Exception as e:
        handler = ErrorHandler.get_instance()
        handler.handle_error(
            component=component,
            operation=operation,
            error=e,
            severity=severity
        )
        return default


# Testing
if __name__ == '__main__':
    print("="*60)
    print("ErrorHandler Test")
    print("="*60)
    print()
    
    handler = ErrorHandler()
    
    # Test 1: Simple error
    try:
        x = 1 / 0
    except Exception as e:
        handler.handle_error(
            component='Math',
            operation='divide',
            error=e,
            severity=ErrorSeverity.ERROR
        )
    
    # Test 2: Warning
    handler.handle_error(
        component='Config',
        operation='load',
        error=Exception('File not found'),
        severity=ErrorSeverity.WARNING
    )
    
    # Test 3: Recovery strategy
    def recovery_strategy(ctx, context):
        print("   Attempting recovery...")
        return True
    
    handler.register_recovery_strategy('Network', 'connect', recovery_strategy)
    
    try:
        raise ConnectionError('Connection failed')
    except Exception as e:
        handler.handle_error(
            component='Network',
            operation='connect',
            error=e,
            recoverable=True
        )
    
    # Print summary
    handler.print_summary()
    
    print("✅ Test completed!")
