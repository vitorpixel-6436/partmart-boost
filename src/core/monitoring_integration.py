#!/usr/bin/env python3
"""Monitoring Integration with Error Handling

Version: 0.3.5l (package 3.9a, stage 7.7b.3/7.7)

Package 3.9a Stage 7.7b.3: Error handling in integration components.

Features:
- Automatic history recording
- Real-time analytics
- Event generation
- DataBus integration
- Comprehensive error handling
- Graceful degradation
"""
import threading
import time
from typing import Optional, Dict, Any

try:
    from performance_history import PerformanceHistory
    from performance_analytics import PerformanceAnalytics, AnalyticsReport
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


class MonitoringIntegration:
    """Monitoring integration layer with error handling
    
    v0.3.5l (package 3.9a, stage 7.7b.3/7.7)
    
    Connects:
    - PerformanceMonitor → raw metrics
    - PerformanceHistory → time-series storage
    - PerformanceAnalytics → insights
    - DataBus → event distribution
    
    Features:
    - Automatic error recovery
    - Graceful degradation
    - Logging integration
    - Thread safety
    
    Usage:
        >>> integration = MonitoringIntegration(
        ...     monitor=monitor,
        ...     data_bus=bus
        ... )
        >>> integration.start()
        >>> 
        >>> # Get report (returns None on error)
        >>> report = integration.get_latest_report()
        >>> if report:
        >>>     print(f"Score: {report.score}")
    """
    
    def __init__(self, monitor=None, data_bus=None,
                 history_size: int = 1000):
        """Initialize integration
        
        Args:
            monitor: PerformanceMonitor instance
            data_bus: DataBus instance
            history_size: Max history samples
        """
        self._monitor = monitor
        self._data_bus = data_bus
        self._logger = None
        
        # Get logger if available
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._logger.debug("MonitoringIntegration initializing", component="MonitoringIntegration")
            except Exception:
                pass
        
        try:
            # Create history and analytics
            if ANALYTICS_AVAILABLE:
                self._history = PerformanceHistory(max_samples=history_size)
                self._analytics = PerformanceAnalytics(self._history)
                self._log_debug(f"Created history (size: {history_size})")
            else:
                self._history = None
                self._analytics = None
                self._log_warning("Analytics modules not available")
            
            self._active = False
            self._thread: Optional[threading.Thread] = None
            self._lock = threading.RLock()
            
            self._latest_report: Optional['AnalyticsReport'] = None
            self._analytics_interval = 10.0  # Run analytics every 10s
            self._last_analytics = 0.0
            
            # Error tracking
            self._error_count = 0
            self._max_errors = 10
            self._last_error_time = 0.0
            
            self._log_info("Initialized successfully")
        
        except Exception as e:
            self._log_error(f"Initialization error: {e}", exc_info=True)
            # Set safe defaults
            self._history = None
            self._analytics = None
            self._active = False
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="MonitoringIntegration")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="MonitoringIntegration")
        else:
            print(f"[MonitoringIntegration] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="MonitoringIntegration")
        else:
            print(f"[MonitoringIntegration] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="MonitoringIntegration", exc_info=exc_info)
        else:
            print(f"[MonitoringIntegration] ERROR: {message}")
    
    def start(self) -> bool:
        """Start integration
        
        Returns:
            True if started successfully
        """
        try:
            if self._active:
                self._log_info("Already active")
                return True
            
            if not ANALYTICS_AVAILABLE:
                self._log_error("Cannot start: analytics not available")
                return False
            
            if not self._monitor:
                self._log_warning("Starting without monitor (testing mode)")
            
            with self._lock:
                self._active = True
                self._error_count = 0
            
            # Start worker thread
            self._thread = threading.Thread(
                target=self._worker,
                name='MonitoringIntegration',
                daemon=True
            )
            self._thread.start()
            
            self._log_info("Started successfully")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to start: {e}", exc_info=True)
            self._active = False
            return False
    
    def stop(self) -> bool:
        """Stop integration
        
        Returns:
            True if stopped successfully
        """
        try:
            with self._lock:
                if not self._active:
                    self._log_debug("Not active, nothing to stop")
                    return True
                
                self._active = False
            
            if self._thread:
                self._thread.join(timeout=2.0)
                
                if self._thread.is_alive():
                    self._log_warning("Thread did not stop gracefully")
                    return False
            
            self._log_info("Stopped successfully")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to stop: {e}", exc_info=True)
            return False
    
    def _worker(self):
        """Worker thread with error handling"""
        self._log_debug("Worker thread started")
        
        while self._active:
            try:
                # Check error threshold
                if self._error_count >= self._max_errors:
                    self._log_error(f"Too many errors ({self._error_count}), stopping")
                    self._active = False
                    break
                
                # Record snapshot
                self._record_snapshot()
                
                # Run analytics periodically
                now = time.time()
                if now - self._last_analytics >= self._analytics_interval:
                    self._run_analytics()
                    self._last_analytics = now
                
                # Sleep
                time.sleep(1.0)
            
            except Exception as e:
                self._handle_worker_error(e)
        
        self._log_debug("Worker thread stopped")
    
    def _handle_worker_error(self, error: Exception):
        """Handle worker thread error
        
        Args:
            error: Exception that occurred
        """
        now = time.time()
        
        # Reset error count if enough time has passed
        if now - self._last_error_time > 60.0:
            self._error_count = 0
        
        self._error_count += 1
        self._last_error_time = now
        
        self._log_error(
            f"Worker error ({self._error_count}/{self._max_errors}): {error}",
            exc_info=True
        )
        
        # Sleep longer after error
        time.sleep(5.0)
    
    def _record_snapshot(self):
        """Record performance snapshot with error handling"""
        if not self._history:
            return
        
        try:
            # Get current metrics
            if not self._monitor:
                return
            
            metrics = self._monitor.get_current_metrics()
            
            if not metrics:
                self._log_debug("No metrics available")
                return
            
            # Validate metrics
            cpu = metrics.get('cpu', 0)
            gpu = metrics.get('gpu', 0)
            ram = metrics.get('memory', 0)
            fps = metrics.get('fps', 0)
            
            # Basic validation
            if not (0 <= cpu <= 100 and 0 <= gpu <= 100 and 0 <= ram <= 100):
                self._log_warning(f"Invalid metrics: CPU={cpu}, GPU={gpu}, RAM={ram}")
                return
            
            # Add to history
            self._history.add_snapshot(
                cpu=cpu,
                gpu=gpu,
                ram=ram,
                fps=fps,
                gpu_temp=0,  # TODO: Get from GPU monitor
                score=metrics.get('score', 0)
            )
            
            self._log_debug(f"Recorded snapshot: CPU={cpu:.1f}, GPU={gpu:.1f}, RAM={ram:.1f}, FPS={fps:.1f}")
        
        except AttributeError as e:
            self._log_error(f"Monitor interface error: {e}")
        
        except Exception as e:
            self._log_error(f"Failed to record snapshot: {e}", exc_info=True)
    
    def _run_analytics(self):
        """Run analytics and publish results with error handling"""
        if not self._analytics:
            return
        
        try:
            # Check if we have enough data
            if self._history and self._history.get_count() < 10:
                self._log_debug("Not enough data for analytics yet")
                return
            
            # Analyze
            report = self._analytics.analyze()
            
            if report is None:
                self._log_debug("No analytics report generated")
                return
            
            with self._lock:
                self._latest_report = report
            
            self._log_debug(f"Analytics: Score={report.score:.1f}, Bottleneck={report.bottleneck.type.value}")
            
            # Publish to DataBus
            self._publish_report(report)
        
        except Exception as e:
            self._log_error(f"Analytics error: {e}", exc_info=True)
    
    def _publish_report(self, report: 'AnalyticsReport'):
        """Publish report to DataBus with error handling
        
        Args:
            report: Analytics report to publish
        """
        if not self._data_bus:
            return
        
        try:
            # Publish full report
            self._data_bus.publish(
                'analytics.report',
                report.to_dict(),
                priority=7
            )
            
            # Publish bottleneck separately
            if report.bottleneck:
                self._data_bus.publish(
                    'analytics.bottleneck',
                    report.bottleneck.to_dict(),
                    priority=8
                )
            
            # Publish top recommendation
            if report.recommendations:
                top_rec = report.recommendations[0]
                self._data_bus.publish(
                    'analytics.recommendation',
                    top_rec.to_dict(),
                    priority=6
                )
            
            self._log_debug("Published analytics to DataBus")
        
        except AttributeError as e:
            self._log_error(f"DataBus interface error: {e}")
        
        except Exception as e:
            self._log_error(f"Failed to publish report: {e}", exc_info=True)
    
    def get_latest_report(self) -> Optional['AnalyticsReport']:
        """Get latest analytics report
        
        Returns:
            AnalyticsReport or None if not available or error
        """
        try:
            with self._lock:
                return self._latest_report
        
        except Exception as e:
            self._log_error(f"Failed to get latest report: {e}")
            return None
    
    def get_history(self) -> Optional['PerformanceHistory']:
        """Get history instance
        
        Returns:
            PerformanceHistory or None
        """
        return self._history
    
    def get_analytics(self) -> Optional['PerformanceAnalytics']:
        """Get analytics instance
        
        Returns:
            PerformanceAnalytics or None
        """
        return self._analytics
    
    def is_active(self) -> bool:
        """Check if active
        
        Returns:
            True if active
        """
        try:
            return self._active
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status
        
        Returns:
            Status dictionary
        """
        try:
            status = {
                'active': self._active,
                'analytics_available': ANALYTICS_AVAILABLE,
                'has_monitor': self._monitor is not None,
                'has_databus': self._data_bus is not None,
                'error_count': self._error_count,
                'history_samples': self._history.get_count() if self._history else 0,
                'has_report': self._latest_report is not None,
            }
            return status
        
        except Exception as e:
            self._log_error(f"Failed to get status: {e}")
            return {'error': str(e)}


# Testing
if __name__ == '__main__' and ANALYTICS_AVAILABLE:
    print("="*60)
    print("MonitoringIntegration Test (with Error Handling)")
    print("="*60)
    print()
    
    # Mock monitor
    class MockMonitor:
        def get_current_metrics(self):
            return {
                'cpu': 65,
                'gpu': 78,
                'memory': 50,
                'fps': 60,
                'score': 85,
            }
    
    monitor = MockMonitor()
    integration = MonitoringIntegration(monitor=monitor)
    
    print("Starting integration...")
    if integration.start():
        print("✅ Started successfully")
    else:
        print("❌ Failed to start")
    
    # Wait for some data
    print("Collecting data (15 seconds)...")
    time.sleep(15)
    
    # Get status
    status = integration.get_status()
    print("\nStatus:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Get report
    report = integration.get_latest_report()
    if report:
        print("\nAnalytics Report:")
        print(f"  Score: {report.score:.1f}")
        print(f"  Bottleneck: {report.bottleneck.type.value}")
        print(f"  Recommendations: {len(report.recommendations)}")
    else:
        print("\nNo report available yet")
    
    # Stop
    if integration.stop():
        print("\n✅ Stopped successfully")
    else:
        print("\n❌ Failed to stop")
    
    # Check history
    history = integration.get_history()
    if history:
        print(f"\nHistory: {history.get_count()} samples")
    
    print()
    print("✅ Test completed!")
