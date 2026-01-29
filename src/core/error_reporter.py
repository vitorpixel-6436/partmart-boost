#!/usr/bin/env python3
"""Error Reporter for System-Wide Error Collection

Version: 0.3.5q (package 3.9a, stage 7.7b.6.1/7.7)

Package 3.9a Stage 7.7b.6.1: Error reporting and analysis.

Features:
- Error collection from all components
- Error report generation
- Multiple export formats (JSON, text, HTML)
- Error severity classification
- Error aggregation and deduplication
- Error statistics and analytics
"""
import json
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict
import os

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __lt__(self, other):
        order = [self.DEBUG, self.INFO, self.WARNING, self.ERROR, self.CRITICAL]
        return order.index(self) < order.index(other)


@dataclass
class ErrorRecord:
    """Error record
    
    Attributes:
        timestamp: Error timestamp
        component: Component name
        severity: Error severity
        message: Error message
        details: Additional details
        exception_type: Exception type (if applicable)
        traceback: Stack traceback (if applicable)
        count: Number of occurrences (for aggregation)
    """
    timestamp: float
    component: str
    severity: ErrorSeverity
    message: str
    details: Optional[str] = None
    exception_type: Optional[str] = None
    traceback: Optional[str] = None
    count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'component': self.component,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'exception_type': self.exception_type,
            'traceback': self.traceback,
            'count': self.count,
        }
    
    def get_key(self) -> str:
        """Get unique key for aggregation"""
        return f"{self.component}:{self.severity.value}:{self.message}"


class ErrorReporter:
    """Error reporter for system-wide error collection
    
    v0.3.5q (package 3.9a, stage 7.7b.6.1/7.7)
    
    Features:
    - Error collection from all components
    - Error report generation
    - Multiple export formats
    - Error severity classification
    - Error aggregation
    - Error statistics
    
    Usage:
        >>> reporter = ErrorReporter(max_records=1000)
        >>> 
        >>> # Report an error
        >>> reporter.report_error(
        ...     component='ConfigManager',
        ...     severity=ErrorSeverity.ERROR,
        ...     message='Failed to load config'
        ... )
        >>> 
        >>> # Get statistics
        >>> stats = reporter.get_statistics()
        >>> print(f"Total errors: {stats['total_errors']}")
        >>> 
        >>> # Generate report
        >>> report = reporter.generate_report(format='json')
        >>> with open('error_report.json', 'w') as f:
        ...     f.write(report)
    """
    
    def __init__(self, max_records: int = 1000, aggregate: bool = True):
        """Initialize error reporter
        
        Args:
            max_records: Maximum number of error records to keep
            aggregate: Enable error aggregation (deduplication)
        """
        self._max_records = max(100, max_records)
        self._aggregate = aggregate
        self._lock = threading.RLock()
        self._logger = None
        
        # Error storage
        self._errors: List[ErrorRecord] = []
        self._aggregated_errors: Dict[str, ErrorRecord] = {}
        
        # Statistics
        self._total_errors = 0
        self._errors_by_component: Dict[str, int] = defaultdict(int)
        self._errors_by_severity: Dict[ErrorSeverity, int] = defaultdict(int)
        
        # Callbacks
        self._callbacks: List[Callable[[ErrorRecord], None]] = []
        
        # Get logger
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug("ErrorReporter initializing")
            except Exception:
                pass
        
        self._log_info(f"Initialized (max_records: {self._max_records}, aggregate: {aggregate})")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="ErrorReporter")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="ErrorReporter")
        else:
            print(f"[ErrorReporter] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="ErrorReporter")
        else:
            print(f"[ErrorReporter] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="ErrorReporter", exc_info=exc_info)
        else:
            print(f"[ErrorReporter] ERROR: {message}")
    
    def report_error(
        self,
        component: str,
        severity: ErrorSeverity,
        message: str,
        details: Optional[str] = None,
        exception_type: Optional[str] = None,
        traceback: Optional[str] = None
    ) -> bool:
        """Report an error
        
        Args:
            component: Component name
            severity: Error severity
            message: Error message
            details: Additional details
            exception_type: Exception type
            traceback: Stack traceback
        
        Returns:
            True if reported successfully
        """
        try:
            # Create error record
            error = ErrorRecord(
                timestamp=time.time(),
                component=component,
                severity=severity,
                message=message,
                details=details,
                exception_type=exception_type,
                traceback=traceback
            )
            
            with self._lock:
                # Update statistics
                self._total_errors += 1
                self._errors_by_component[component] += 1
                self._errors_by_severity[severity] += 1
                
                # Store error
                if self._aggregate:
                    # Aggregate similar errors
                    key = error.get_key()
                    if key in self._aggregated_errors:
                        # Increment count
                        self._aggregated_errors[key].count += 1
                        self._aggregated_errors[key].timestamp = error.timestamp
                    else:
                        self._aggregated_errors[key] = error
                else:
                    # Store all errors
                    self._errors.append(error)
                    
                    # Trim if needed
                    if len(self._errors) > self._max_records:
                        self._errors = self._errors[-self._max_records:]
            
            # Notify callbacks
            self._notify_callbacks(error)
            
            return True
        
        except Exception as e:
            self._log_error(f"Failed to report error: {e}", exc_info=True)
            return False
    
    def report_exception(
        self,
        component: str,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[str] = None
    ) -> bool:
        """Report an exception
        
        Args:
            component: Component name
            exception: Exception object
            severity: Error severity
            context: Additional context
        
        Returns:
            True if reported successfully
        """
        try:
            import traceback as tb
            
            return self.report_error(
                component=component,
                severity=severity,
                message=str(exception),
                details=context,
                exception_type=type(exception).__name__,
                traceback=''.join(tb.format_exception(type(exception), exception, exception.__traceback__))
            )
        
        except Exception as e:
            self._log_error(f"Failed to report exception: {e}")
            return False
    
    def _notify_callbacks(self, error: ErrorRecord):
        """Notify callbacks with error isolation
        
        Args:
            error: Error record
        """
        for callback in self._callbacks:
            try:
                callback(error)
            except Exception as e:
                self._log_error(f"Callback error: {e}", exc_info=True)
    
    def add_callback(self, callback: Callable[[ErrorRecord], None]) -> int:
        """Add error callback
        
        Args:
            callback: Callback function(error_record)
        
        Returns:
            Callback ID
        """
        try:
            with self._lock:
                callback_id = len(self._callbacks)
                self._callbacks.append(callback)
                self._log_debug(f"Added callback (ID: {callback_id})")
                return callback_id
        
        except Exception as e:
            self._log_error(f"Failed to add callback: {e}")
            return -1
    
    def get_errors(
        self,
        component: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None,
        min_severity: Optional[ErrorSeverity] = None,
        limit: Optional[int] = None
    ) -> List[ErrorRecord]:
        """Get error records with filtering
        
        Args:
            component: Filter by component
            severity: Filter by exact severity
            min_severity: Filter by minimum severity
            limit: Maximum number of records
        
        Returns:
            List of error records
        """
        try:
            with self._lock:
                # Get all errors
                if self._aggregate:
                    errors = list(self._aggregated_errors.values())
                else:
                    errors = list(self._errors)
                
                # Apply filters
                if component:
                    errors = [e for e in errors if e.component == component]
                
                if severity:
                    errors = [e for e in errors if e.severity == severity]
                
                if min_severity:
                    errors = [e for e in errors if e.severity.value in 
                             [s.value for s in ErrorSeverity if s >= min_severity]]
                
                # Sort by timestamp (newest first)
                errors.sort(key=lambda e: e.timestamp, reverse=True)
                
                # Apply limit
                if limit:
                    errors = errors[:limit]
                
                return errors
        
        except Exception as e:
            self._log_error(f"Failed to get errors: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get error statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            with self._lock:
                # Calculate stats
                current_errors = len(self._aggregated_errors) if self._aggregate else len(self._errors)
                
                return {
                    'total_errors': self._total_errors,
                    'current_errors': current_errors,
                    'errors_by_component': dict(self._errors_by_component),
                    'errors_by_severity': {
                        k.value: v for k, v in self._errors_by_severity.items()
                    },
                    'aggregation_enabled': self._aggregate,
                    'max_records': self._max_records,
                }
        
        except Exception as e:
            self._log_error(f"Failed to get statistics: {e}")
            return {'error': str(e)}
    
    def generate_report(
        self,
        format: str = 'json',
        component: Optional[str] = None,
        min_severity: Optional[ErrorSeverity] = None,
        limit: Optional[int] = None
    ) -> str:
        """Generate error report
        
        Args:
            format: Report format ('json', 'text', 'html')
            component: Filter by component
            min_severity: Minimum severity level
            limit: Maximum number of errors
        
        Returns:
            Report string
        """
        try:
            # Get errors
            errors = self.get_errors(
                component=component,
                min_severity=min_severity,
                limit=limit
            )
            
            # Get statistics
            stats = self.get_statistics()
            
            # Generate report based on format
            if format == 'json':
                return self._generate_json_report(errors, stats)
            elif format == 'text':
                return self._generate_text_report(errors, stats)
            elif format == 'html':
                return self._generate_html_report(errors, stats)
            else:
                self._log_warning(f"Unknown report format: {format}")
                return self._generate_json_report(errors, stats)
        
        except Exception as e:
            self._log_error(f"Failed to generate report: {e}", exc_info=True)
            return f"Error generating report: {e}"
    
    def _generate_json_report(self, errors: List[ErrorRecord], stats: Dict[str, Any]) -> str:
        """Generate JSON report
        
        Args:
            errors: Error records
            stats: Statistics
        
        Returns:
            JSON string
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'errors': [e.to_dict() for e in errors]
        }
        
        return json.dumps(report, indent=2)
    
    def _generate_text_report(self, errors: List[ErrorRecord], stats: Dict[str, Any]) -> str:
        """Generate text report
        
        Args:
            errors: Error records
            stats: Statistics
        
        Returns:
            Text string
        """
        lines = []
        lines.append("="*80)
        lines.append("ERROR REPORT")
        lines.append("="*80)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("")
        
        # Statistics
        lines.append("STATISTICS")
        lines.append("-"*80)
        lines.append(f"Total Errors: {stats['total_errors']}")
        lines.append(f"Current Records: {stats['current_errors']}")
        lines.append("")
        
        # By component
        lines.append("Errors by Component:")
        for comp, count in stats['errors_by_component'].items():
            lines.append(f"  {comp}: {count}")
        lines.append("")
        
        # By severity
        lines.append("Errors by Severity:")
        for sev, count in stats['errors_by_severity'].items():
            lines.append(f"  {sev.upper()}: {count}")
        lines.append("")
        
        # Error records
        lines.append(f"ERROR RECORDS ({len(errors)})")
        lines.append("-"*80)
        
        for i, error in enumerate(errors, 1):
            lines.append(f"\n[{i}] {error.severity.value.upper()} - {error.component}")
            lines.append(f"    Time: {datetime.fromtimestamp(error.timestamp).isoformat()}")
            lines.append(f"    Message: {error.message}")
            
            if error.count > 1:
                lines.append(f"    Count: {error.count}")
            
            if error.details:
                lines.append(f"    Details: {error.details}")
            
            if error.exception_type:
                lines.append(f"    Exception: {error.exception_type}")
            
            if error.traceback:
                lines.append(f"    Traceback:")
                for line in error.traceback.split('\n')[:5]:  # First 5 lines
                    lines.append(f"      {line}")
        
        lines.append("")
        lines.append("="*80)
        
        return '\n'.join(lines)
    
    def _generate_html_report(self, errors: List[ErrorRecord], stats: Dict[str, Any]) -> str:
        """Generate HTML report
        
        Args:
            errors: Error records
            stats: Statistics
        
        Returns:
            HTML string
        """
        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html>')
        html.append('<head>')
        html.append('<meta charset="UTF-8">')
        html.append('<title>Error Report</title>')
        html.append('<style>')
        html.append('body { font-family: Arial, sans-serif; margin: 20px; }')
        html.append('h1 { color: #333; }')
        html.append('h2 { color: #666; margin-top: 30px; }')
        html.append('.stats { background: #f5f5f5; padding: 15px; border-radius: 5px; }')
        html.append('.error { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }')
        html.append('.critical { border-left: 5px solid #d32f2f; }')
        html.append('.error-level { border-left: 5px solid #f57c00; }')
        html.append('.warning { border-left: 5px solid #fbc02d; }')
        html.append('.info { border-left: 5px solid #1976d2; }')
        html.append('.error-header { font-weight: bold; color: #333; }')
        html.append('.error-time { color: #666; font-size: 0.9em; }')
        html.append('.error-message { margin: 10px 0; }')
        html.append('.traceback { background: #f9f9f9; padding: 10px; font-family: monospace; font-size: 0.9em; overflow-x: auto; }')
        html.append('</style>')
        html.append('</head>')
        html.append('<body>')
        
        # Header
        html.append('<h1>Error Report</h1>')
        html.append(f'<p>Generated: {datetime.now().isoformat()}</p>')
        
        # Statistics
        html.append('<div class="stats">')
        html.append('<h2>Statistics</h2>')
        html.append(f'<p><strong>Total Errors:</strong> {stats["total_errors"]}</p>')
        html.append(f'<p><strong>Current Records:</strong> {stats["current_errors"]}</p>')
        
        html.append('<h3>By Component</h3>')
        html.append('<ul>')
        for comp, count in stats['errors_by_component'].items():
            html.append(f'<li>{comp}: {count}</li>')
        html.append('</ul>')
        
        html.append('<h3>By Severity</h3>')
        html.append('<ul>')
        for sev, count in stats['errors_by_severity'].items():
            html.append(f'<li>{sev.upper()}: {count}</li>')
        html.append('</ul>')
        html.append('</div>')
        
        # Errors
        html.append(f'<h2>Error Records ({len(errors)})</h2>')
        
        for error in errors:
            severity_class = error.severity.value
            if severity_class == 'error':
                severity_class = 'error-level'
            
            html.append(f'<div class="error {severity_class}">')
            html.append(f'<div class="error-header">{error.severity.value.upper()} - {error.component}</div>')
            html.append(f'<div class="error-time">{datetime.fromtimestamp(error.timestamp).isoformat()}</div>')
            html.append(f'<div class="error-message">{error.message}</div>')
            
            if error.count > 1:
                html.append(f'<p><strong>Occurrences:</strong> {error.count}</p>')
            
            if error.details:
                html.append(f'<p><strong>Details:</strong> {error.details}</p>')
            
            if error.exception_type:
                html.append(f'<p><strong>Exception:</strong> {error.exception_type}</p>')
            
            if error.traceback:
                html.append('<details>')
                html.append('<summary>Traceback</summary>')
                html.append(f'<pre class="traceback">{error.traceback}</pre>')
                html.append('</details>')
            
            html.append('</div>')
        
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)
    
    def export_report(
        self,
        filepath: str,
        format: str = 'json',
        **kwargs
    ) -> bool:
        """Export report to file
        
        Args:
            filepath: Output file path
            format: Report format
            **kwargs: Additional arguments for generate_report
        
        Returns:
            True if exported successfully
        """
        try:
            # Generate report
            report = self.generate_report(format=format, **kwargs)
            
            # Create directory if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self._log_info(f"Report exported to: {filepath}")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to export report: {e}", exc_info=True)
            return False
    
    def clear(
        self,
        component: Optional[str] = None,
        severity: Optional[ErrorSeverity] = None
    ):
        """Clear error records
        
        Args:
            component: Clear specific component only
            severity: Clear specific severity only
        """
        try:
            with self._lock:
                if not component and not severity:
                    # Clear all
                    self._errors.clear()
                    self._aggregated_errors.clear()
                    self._log_info("Cleared all error records")
                else:
                    # Clear filtered
                    if self._aggregate:
                        keys_to_remove = [
                            k for k, e in self._aggregated_errors.items()
                            if (not component or e.component == component) and
                               (not severity or e.severity == severity)
                        ]
                        for key in keys_to_remove:
                            del self._aggregated_errors[key]
                    else:
                        self._errors = [
                            e for e in self._errors
                            if not ((not component or e.component == component) and
                                   (not severity or e.severity == severity))
                        ]
                    
                    self._log_info(f"Cleared errors (component: {component}, severity: {severity})")
        
        except Exception as e:
            self._log_error(f"Failed to clear errors: {e}")


# Testing
if __name__ == '__main__':
    print("="*80)
    print("ErrorReporter Test")
    print("="*80)
    print()
    
    # Create reporter
    reporter = ErrorReporter(max_records=100, aggregate=True)
    
    # Report some errors
    print("Reporting errors...")
    reporter.report_error('ConfigManager', ErrorSeverity.ERROR, 'Failed to load config file')
    reporter.report_error('PerformanceMonitor', ErrorSeverity.WARNING, 'CPU usage spike detected')
    reporter.report_error('GameDetection', ErrorSeverity.ERROR, 'Failed to detect game process')
    reporter.report_error('ConfigManager', ErrorSeverity.ERROR, 'Failed to load config file')  # Duplicate
    reporter.report_error('UI', ErrorSeverity.CRITICAL, 'Window crashed', details='Stack overflow')
    print()
    
    # Get statistics
    stats = reporter.get_statistics()
    print("Statistics:")
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Current records: {stats['current_errors']}")
    print(f"  By component: {stats['errors_by_component']}")
    print(f"  By severity: {stats['errors_by_severity']}")
    print()
    
    # Generate text report
    print("Text Report:")
    print("-"*80)
    report = reporter.generate_report(format='text', limit=10)
    print(report)
    print()
    
    # Export reports
    print("Exporting reports...")
    reporter.export_report('reports/error_report.json', format='json')
    reporter.export_report('reports/error_report.txt', format='text')
    reporter.export_report('reports/error_report.html', format='html')
    print("✅ Reports exported!")
    print()
    
    print("✅ Test completed!")
