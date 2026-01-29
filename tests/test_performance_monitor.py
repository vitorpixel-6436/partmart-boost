#!/usr/bin/env python3
"""PerformanceMonitor Error Handling Tests

Version: 0.3.5n (package 3.9a, stage 7.7b.5.1/7.7)
"""
import sys
import os
import unittest
import time
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from performance_monitor import PerformanceMonitor, PerformanceMetrics, MonitorState


class TestPerformanceMetrics(unittest.TestCase):
    """Test PerformanceMetrics validation"""
    
    def test_valid_metrics(self):
        """Test valid metrics"""
        metrics = PerformanceMetrics(
            cpu=50.0,
            gpu=60.0,
            ram=40.0,
            fps=60.0,
            cpu_temp=50.0,
            gpu_temp=70.0,
            score=85.0,
            timestamp=time.time()
        )
        
        self.assertTrue(metrics.is_valid())
    
    def test_invalid_cpu(self):
        """Test invalid CPU value"""
        metrics = PerformanceMetrics(
            cpu=150.0,  # Invalid!
            gpu=60.0,
            ram=40.0,
            fps=60.0,
            cpu_temp=50.0,
            gpu_temp=70.0,
            score=85.0,
            timestamp=time.time()
        )
        
        self.assertFalse(metrics.is_valid())
    
    def test_invalid_gpu(self):
        """Test invalid GPU value"""
        metrics = PerformanceMetrics(
            cpu=50.0,
            gpu=-10.0,  # Invalid!
            ram=40.0,
            fps=60.0,
            cpu_temp=50.0,
            gpu_temp=70.0,
            score=85.0,
            timestamp=time.time()
        )
        
        self.assertFalse(metrics.is_valid())
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        metrics = PerformanceMetrics(
            cpu=50.0,
            gpu=60.0,
            ram=40.0,
            fps=60.0,
            cpu_temp=50.0,
            gpu_temp=70.0,
            score=85.0,
            timestamp=123.456
        )
        
        d = metrics.to_dict()
        
        self.assertEqual(d['cpu'], 50.0)
        self.assertEqual(d['gpu'], 60.0)
        self.assertEqual(d['timestamp'], 123.456)


class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor(interval=100)
    
    def tearDown(self):
        """Clean up"""
        if self.monitor.is_running():
            self.monitor.stop()
    
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertEqual(self.monitor.get_state(), MonitorState.STOPPED)
        self.assertFalse(self.monitor.is_running())
    
    def test_interval_clamping(self):
        """Test interval is clamped to valid range"""
        # Too low
        monitor1 = PerformanceMonitor(interval=5)
        status1 = monitor1.get_status()
        self.assertEqual(status1['interval'], 10)  # Clamped to min
        
        # Too high
        monitor2 = PerformanceMonitor(interval=10000)
        status2 = monitor2.get_status()
        self.assertEqual(status2['interval'], 5000)  # Clamped to max
    
    def test_start_stop(self):
        """Test basic start/stop"""
        # Start
        result = self.monitor.start()
        self.assertTrue(result)
        self.assertEqual(self.monitor.get_state(), MonitorState.RUNNING)
        
        # Wait for first update
        time.sleep(0.2)
        
        # Stop
        result = self.monitor.stop()
        self.assertTrue(result)
        self.assertEqual(self.monitor.get_state(), MonitorState.STOPPED)
    
    def test_start_already_running(self):
        """Test starting when already running"""
        self.monitor.start()
        
        # Second start should return True (already running)
        result = self.monitor.start()
        self.assertTrue(result)
    
    def test_stop_already_stopped(self):
        """Test stopping when already stopped"""
        # Should return True (already stopped)
        result = self.monitor.stop()
        self.assertTrue(result)
    
    def test_metrics_collection(self):
        """Test metrics are collected"""
        self.monitor.start()
        
        # Wait for collection
        time.sleep(0.3)
        
        # Get metrics
        metrics = self.monitor.get_current_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertIn('cpu', metrics)
        self.assertIn('ram', metrics)
        self.assertIn('score', metrics)
        
        self.monitor.stop()
    
    def test_callback_system(self):
        """Test callback system"""
        received = []
        
        def callback(metrics: PerformanceMetrics):
            received.append(metrics)
        
        # Add callback
        callback_id = self.monitor.add_callback(callback)
        self.assertGreaterEqual(callback_id, 0)
        
        # Start monitoring
        self.monitor.start()
        time.sleep(0.5)
        self.monitor.stop()
        
        # Should have received metrics
        self.assertGreater(len(received), 0)
    
    def test_callback_error_isolation(self):
        """Test that callback errors don't break monitoring"""
        received_good = []
        
        def bad_callback(metrics: PerformanceMetrics):
            raise Exception("Bad callback!")
        
        def good_callback(metrics: PerformanceMetrics):
            received_good.append(metrics)
        
        # Add both callbacks
        self.monitor.add_callback(bad_callback)
        self.monitor.add_callback(good_callback)
        
        # Start monitoring
        self.monitor.start()
        time.sleep(0.5)
        self.monitor.stop()
        
        # Good callback should still have received
        self.assertGreater(len(received_good), 0)
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.monitor.get_status()
        
        self.assertIn('state', status)
        self.assertIn('interval', status)
        self.assertIn('update_count', status)
        self.assertIn('error_count', status)
        
        self.assertEqual(status['state'], 'stopped')
    
    def test_status_when_running(self):
        """Test status when monitoring is running"""
        self.monitor.start()
        time.sleep(0.3)
        
        status = self.monitor.get_status()
        
        self.assertEqual(status['state'], 'running')
        self.assertGreater(status['update_count'], 0)
        self.assertTrue(status['has_metrics'])
        
        self.monitor.stop()
    
    @patch('psutil.cpu_percent')
    def test_cpu_error_recovery(self, mock_cpu):
        """Test recovery from CPU reading errors"""
        # First call succeeds, second fails, third succeeds
        mock_cpu.side_effect = [50.0, Exception("CPU error!"), 60.0]
        
        # Should not crash
        cpu1 = self.monitor._get_cpu_usage()
        self.assertEqual(cpu1, 50.0)
        
        cpu2 = self.monitor._get_cpu_usage()  # Error
        # Should return fallback (0 or last value)
        self.assertGreaterEqual(cpu2, 0.0)
        
        cpu3 = self.monitor._get_cpu_usage()
        self.assertEqual(cpu3, 60.0)
    
    def test_metrics_validation(self):
        """Test that invalid metrics are rejected"""
        # Create invalid metrics
        invalid_metrics = PerformanceMetrics(
            cpu=200.0,  # Invalid!
            gpu=50.0,
            ram=40.0,
            fps=60.0,
            cpu_temp=50.0,
            gpu_temp=70.0,
            score=85.0,
            timestamp=time.time()
        )
        
        # Should be rejected
        self.assertFalse(invalid_metrics.is_valid())


if __name__ == '__main__':
    unittest.main()
