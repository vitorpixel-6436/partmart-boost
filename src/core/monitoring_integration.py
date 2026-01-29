#!/usr/bin/env python3
"""Monitoring Integration - Connects Monitor + History + Analytics

Version: 0.3.5g (package 3.9a, stage 7.5/7.7)

Package 3.9a Stage 7.5: Complete monitoring pipeline integration.

Features:
- Automatic history recording
- Real-time analytics
- Event generation
- DataBus integration
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
    print("[MonitoringIntegration] Analytics modules not available")


class MonitoringIntegration:
    """Monitoring integration layer
    
    v0.3.5g (package 3.9a, stage 7.5/7.7)
    
    Connects:
    - PerformanceMonitor → raw metrics
    - PerformanceHistory → time-series storage
    - PerformanceAnalytics → insights
    - DataBus → event distribution
    
    Usage:
        >>> integration = MonitoringIntegration(
        ...     monitor=monitor,
        ...     data_bus=bus
        ... )
        >>> integration.start()
        >>> 
        >>> # Get report
        >>> report = integration.get_latest_report()
        >>> print(f"Score: {report.score}")
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
        
        # Create history and analytics
        if ANALYTICS_AVAILABLE:
            self._history = PerformanceHistory(max_samples=history_size)
            self._analytics = PerformanceAnalytics(self._history)
        else:
            self._history = None
            self._analytics = None
        
        self._active = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        self._latest_report: Optional['AnalyticsReport'] = None
        self._analytics_interval = 10.0  # Run analytics every 10s
        self._last_analytics = 0.0
        
        print("[MonitoringIntegration] Initialized")
    
    def start(self):
        """Start integration"""
        if self._active:
            print("[MonitoringIntegration] Already active")
            return
        
        if not ANALYTICS_AVAILABLE:
            print("[MonitoringIntegration] Analytics not available")
            return
        
        with self._lock:
            self._active = True
        
        # Start worker thread
        self._thread = threading.Thread(
            target=self._worker,
            name='MonitoringIntegration',
            daemon=True
        )
        self._thread.start()
        
        print("[MonitoringIntegration] ✅ Started")
    
    def stop(self):
        """Stop integration"""
        with self._lock:
            self._active = False
        
        if self._thread:
            self._thread.join(timeout=2.0)
        
        print("[MonitoringIntegration] Stopped")
    
    def _worker(self):
        """Worker thread"""
        print("[MonitoringIntegration] Worker started")
        
        while self._active:
            try:
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
                print(f"[MonitoringIntegration] Worker error: {e}")
        
        print("[MonitoringIntegration] Worker stopped")
    
    def _record_snapshot(self):
        """Record performance snapshot"""
        if not self._monitor or not self._history:
            return
        
        try:
            # Get current metrics
            metrics = self._monitor.get_current_metrics()
            
            if metrics:
                # Add to history
                self._history.add_snapshot(
                    cpu=metrics.get('cpu', 0),
                    gpu=metrics.get('gpu', 0),
                    ram=metrics.get('memory', 0),  # Note: 'memory' in monitor
                    fps=metrics.get('fps', 0),
                    gpu_temp=0,  # TODO: Get from GPU monitor
                    score=metrics.get('score', 0)
                )
        
        except Exception as e:
            print(f"[MonitoringIntegration] Snapshot error: {e}")
    
    def _run_analytics(self):
        """Run analytics and publish results"""
        if not self._analytics:
            return
        
        try:
            # Analyze
            report = self._analytics.analyze()
            
            with self._lock:
                self._latest_report = report
            
            # Publish to DataBus
            if self._data_bus:
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
        
        except Exception as e:
            print(f"[MonitoringIntegration] Analytics error: {e}")
    
    def get_latest_report(self) -> Optional['AnalyticsReport']:
        """Get latest analytics report
        
        Returns:
            AnalyticsReport or None
        """
        with self._lock:
            return self._latest_report
    
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
        return self._active


# Testing
if __name__ == '__main__' and ANALYTICS_AVAILABLE:
    print("="*60)
    print("MonitoringIntegration Test")
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
    integration.start()
    
    # Wait for some data
    print("Collecting data (15 seconds)...")
    time.sleep(15)
    
    # Get report
    report = integration.get_latest_report()
    if report:
        print("\nAnalytics Report:")
        print(f"  Score: {report.score:.1f}")
        print(f"  Bottleneck: {report.bottleneck.type.value}")
        print(f"  Recommendations: {len(report.recommendations)}")
    
    # Stop
    integration.stop()
    
    # Check history
    history = integration.get_history()
    if history:
        print(f"\nHistory: {history.get_count()} samples")
    
    print()
    print("✅ Test completed!")
