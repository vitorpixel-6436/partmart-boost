#!/usr/bin/env python3
"""Service Layer Error Handling Tests

Version: 0.3.5n (package 3.9a, stage 7.7b.5/7.7)
"""
import sys
import os
import unittest
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from performance_monitor import PerformanceMonitor


class MockManager:
    """Mock MonitorManager for testing"""
    
    def __init__(self):
        self.cpu_load = 50.0
        self.gpu_load = 60.0
        self.ram_percent = 70.0
        self.cpu_temp = 65.0
        self.gpu_temp = 70.0
        self.fps = 60.0
        self.frame_time = 16.67
        self.should_fail = False
    
    def get_cpu_load(self):
        if self.should_fail:
            raise Exception("CPU load error!")
        return self.cpu_load
    
    def get_gpu_load(self):
        if self.should_fail:
            raise Exception("GPU load error!")
        return self.gpu_load
    
    def get_ram_percent(self):
        return self.ram_percent
    
    def get_cpu_temp(self):
        return self.cpu_temp
    
    def get_gpu_temp(self):
        return self.gpu_temp
    
    def get_fps(self):
        return self.fps
    
    def get_frame_time(self):
        return self.frame_time


class MockBus:
    """Mock DataBus for testing"""
    pass


class TestPerformanceMonitorErrorHandling(unittest.TestCase):
    """Test PerformanceMonitor error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = MockManager()
        self.bus = MockBus()
        self.monitor = PerformanceMonitor(self.manager, self.bus, history_size=100)
    
    def test_update_success(self):
        """Test successful update"""
        result = self.monitor.update()
        self.assertTrue(result)
    
    def test_update_without_manager(self):
        """Test update without manager"""
        monitor = PerformanceMonitor(None, self.bus)
        result = monitor.update()
        self.assertFalse(result)
    
    def test_invalid_load_values(self):
        """Test handling of invalid load values"""
        # Set invalid values
        self.manager.cpu_load = 150  # Over 100
        self.manager.gpu_load = -50  # Negative
        
        result = self.monitor.update()
        self.assertTrue(result)  # Should handle gracefully
        
        # Values should be clamped
        status = self.monitor.get_status()
        self.assertEqual(status['snapshot_count'], 1)
    
    def test_manager_interface_error(self):
        """Test handling of manager interface errors"""
        self.manager.should_fail = True
        
        # Should handle error and continue
        result = self.monitor.update()
        self.assertTrue(result)  # Returns True but with default values
    
    def test_performance_score_without_data(self):
        """Test performance score without data"""
        monitor = PerformanceMonitor(self.manager, self.bus)
        score = monitor.get_performance_score()
        self.assertEqual(score, 0.0)
    
    def test_performance_score_with_data(self):
        """Test performance score with data"""
        # Collect some data
        for _ in range(30):
            self.monitor.update()
        
        score = self.monitor.get_performance_score()
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 100.0)
    
    def test_bottleneck_detection(self):
        """Test bottleneck detection"""
        # Set high CPU load
        self.manager.cpu_load = 95.0
        self.manager.gpu_load = 30.0
        
        self.monitor.update()
        
        bottleneck = self.monitor.get_current_bottleneck()
        self.assertIsNotNone(bottleneck)
        self.assertEqual(bottleneck.component, 'cpu')
        self.assertEqual(bottleneck.severity, 'high')
    
    def test_baseline_establishment(self):
        """Test baseline establishment"""
        # Collect enough data for baseline
        for _ in range(60):
            self.monitor.update()
            time.sleep(0.001)
        
        baseline = self.monitor.get_baseline_fps()
        self.assertGreater(baseline, 0.0)
    
    def test_performance_degradation_detection(self):
        """Test performance degradation detection"""
        # Establish baseline
        for _ in range(60):
            self.monitor.update()
        
        # Drop FPS significantly
        self.manager.fps = 30.0
        
        # Collect more data
        for _ in range(30):
            self.monitor.update()
        
        # Should detect degradation
        self.assertTrue(self.monitor.is_performance_degrading())
    
    def test_status_reporting(self):
        """Test status reporting"""
        status = self.monitor.get_status()
        
        self.assertIn('active', status)
        self.assertIn('snapshot_count', status)
        self.assertIn('baseline_established', status)
        self.assertIn('error_count', status)
    
    def test_reset(self):
        """Test reset functionality"""
        # Collect some data
        for _ in range(30):
            self.monitor.update()
        
        # Reset
        result = self.monitor.reset()
        self.assertTrue(result)
        
        # Check if cleared
        status = self.monitor.get_status()
        self.assertEqual(status['snapshot_count'], 0)
        self.assertFalse(status['baseline_established'])


if __name__ == '__main__':
    unittest.main()
