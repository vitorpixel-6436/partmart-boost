#!/usr/bin/env python3
"""MonitoringIntegration Unit Tests

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)
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


class TestMonitoringIntegration(unittest.TestCase):
    """Test MonitoringIntegration functionality"""
    
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
    
    def test_initialization(self):
        """Test initialization"""
        self.assertIsNotNone(self.integration.get_history())
        self.assertFalse(self.integration.is_active())
    
    def test_start_stop(self):
        """Test starting and stopping"""
        self.integration.start()
        self.assertTrue(self.integration.is_active())
        
        self.integration.stop()
        self.assertFalse(self.integration.is_active())
    
    def test_history_recording(self):
        """Test that metrics are recorded to history"""
        self.monitor.set_metrics(cpu=60, gpu=70, ram=50, fps=60)
        self.integration.start()
        
        # Trigger recording manually
        self.integration._record_metrics()
        
        history = self.integration.get_history()
        self.assertGreater(history.get_count(), 0)
        
        latest = history.get_latest()
        self.assertEqual(latest.cpu, 60)
        self.assertEqual(latest.gpu, 70)
    
    def test_analytics_generation(self):
        """Test analytics report generation"""
        # Add some data
        for i in range(15):
            self.monitor.set_metrics(cpu=50 + i, gpu=60, ram=40, fps=60)
            self.integration._record_metrics()
        
        # Trigger analytics
        self.integration._run_analytics()
        
        report = self.integration.get_latest_report()
        self.assertIsNotNone(report)
    
    def test_databus_publishing(self):
        """Test that analytics are published to DataBus"""
        self.integration.start()
        
        # Add data and run analytics
        for _ in range(15):
            self.monitor.set_metrics(cpu=50, gpu=60, ram=40, fps=60)
            self.integration._record_metrics()
        
        self.integration._run_analytics()
        
        # Check that messages were published
        self.assertGreater(len(self.bus.published_messages), 0)
        
        # Check for analytics topics
        topics = [msg['topic'] for msg in self.bus.published_messages]
        self.assertTrue(any('analytics' in topic for topic in topics))
    
    def test_clear_history(self):
        """Test clearing history"""
        self.integration._record_metrics()
        self.integration._record_metrics()
        
        history = self.integration.get_history()
        self.assertGreater(history.get_count(), 0)
        
        history.clear()
        self.assertEqual(history.get_count(), 0)


if __name__ == '__main__':
    unittest.main()
