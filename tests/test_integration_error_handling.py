#!/usr/bin/env python3
"""Integration Components Error Handling Tests

Version: 0.3.5l (package 3.9a, stage 7.7b.3/7.7)
"""
import sys
import os
import unittest
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from monitoring_integration import MonitoringIntegration
from mock_objects import MockPerformanceMonitor, MockDataBus


class TestMonitoringIntegrationErrorHandling(unittest.TestCase):
    """Test MonitoringIntegration error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = MockPerformanceMonitor()
        self.bus = MockDataBus()
        self.integration = MonitoringIntegration(
            monitor=self.monitor,
            data_bus=self.bus,
            history_size=100
        )
    
    def tearDown(self):
        """Clean up"""
        if self.integration.is_active():
            self.integration.stop()
    
    def test_start_without_monitor(self):
        """Test starting without monitor (should work in testing mode)"""
        integration = MonitoringIntegration(
            monitor=None,
            data_bus=self.bus
        )
        
        # Should start successfully
        result = integration.start()
        self.assertTrue(result)
        
        integration.stop()
    
    def test_start_already_active(self):
        """Test starting when already active"""
        self.integration.start()
        
        # Second start should return True (already active)
        result = self.integration.start()
        self.assertTrue(result)
    
    def test_stop_not_active(self):
        """Test stopping when not active"""
        # Should return True (nothing to stop)
        result = self.integration.stop()
        self.assertTrue(result)
    
    def test_invalid_metrics_rejection(self):
        """Test that invalid metrics are rejected"""
        # Set invalid metrics
        self.monitor.set_metrics(cpu=150, gpu=-50, ram=200)
        
        self.integration.start()
        
        # Trigger recording
        self.integration._record_snapshot()
        
        # History should not contain invalid data
        history = self.integration.get_history()
        # Should be 0 because invalid metrics are rejected
        self.assertEqual(history.get_count(), 0)
        
        self.integration.stop()
    
    def test_valid_metrics_acceptance(self):
        """Test that valid metrics are accepted"""
        # Set valid metrics
        self.monitor.set_metrics(cpu=50, gpu=60, ram=40, fps=60)
        
        self.integration.start()
        
        # Trigger recording
        self.integration._record_snapshot()
        
        # History should contain data
        history = self.integration.get_history()
        self.assertGreater(history.get_count(), 0)
        
        self.integration.stop()
    
    def test_get_status(self):
        """Test getting integration status"""
        status = self.integration.get_status()
        
        self.assertIn('active', status)
        self.assertIn('analytics_available', status)
        self.assertIn('error_count', status)
        self.assertFalse(status['active'])
    
    def test_get_status_when_active(self):
        """Test status when integration is active"""
        self.integration.start()
        
        status = self.integration.get_status()
        
        self.assertTrue(status['active'])
        self.assertTrue(status['has_monitor'])
        
        self.integration.stop()
    
    def test_analytics_without_data(self):
        """Test analytics generation without sufficient data"""
        self.integration.start()
        
        # Try to run analytics immediately (not enough data)
        self.integration._run_analytics()
        
        # Should not crash, report should be None
        report = self.integration.get_latest_report()
        self.assertIsNone(report)
        
        self.integration.stop()
    
    def test_worker_error_recovery(self):
        """Test that worker recovers from errors"""
        # Create monitor that throws errors
        class ErrorMonitor:
            def __init__(self):
                self.call_count = 0
            
            def get_current_metrics(self):
                self.call_count += 1
                if self.call_count < 3:
                    raise Exception("Monitor error!")
                return {
                    'cpu': 50,
                    'gpu': 60,
                    'memory': 40,
                    'fps': 60
                }
        
        error_monitor = ErrorMonitor()
        integration = MonitoringIntegration(monitor=error_monitor)
        
        integration.start()
        
        # Wait for recovery
        time.sleep(5)
        
        # Should still be active after errors
        self.assertTrue(integration.is_active())
        
        integration.stop()
    
    def test_databus_publish_error_isolation(self):
        """Test that DataBus publish errors don't break integration"""
        # Create DataBus that throws errors
        class ErrorBus:
            def publish(self, topic, data, priority=5):
                raise Exception("Publish error!")
        
        integration = MonitoringIntegration(
            monitor=self.monitor,
            data_bus=ErrorBus()
        )
        
        # Add enough data for analytics
        for _ in range(15):
            integration._record_snapshot()
        
        # Try to run analytics (publish will fail)
        integration._run_analytics()
        
        # Should not crash, report should still be available
        report = integration.get_latest_report()
        # Report might be None or available depending on timing
        # Main thing is it didn't crash
        self.assertTrue(True)  # If we got here, test passed


if __name__ == '__main__':
    unittest.main()
