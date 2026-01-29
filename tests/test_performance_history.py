#!/usr/bin/env python3
"""PerformanceHistory Unit Tests

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)
"""
import sys
import os
import unittest
import time
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from performance_history import PerformanceHistory, PerformanceSnapshot


class TestPerformanceHistory(unittest.TestCase):
    """Test PerformanceHistory functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.history = PerformanceHistory(max_samples=100)
    
    def test_add_snapshot(self):
        """Test adding snapshot"""
        self.history.add_snapshot(cpu=50, gpu=60, ram=40, fps=60)
        
        self.assertEqual(self.history.get_count(), 1)
    
    def test_get_latest(self):
        """Test getting latest snapshot"""
        self.history.add_snapshot(cpu=50, gpu=60, ram=40, fps=60)
        self.history.add_snapshot(cpu=55, gpu=65, ram=45, fps=55)
        
        latest = self.history.get_latest()
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest.cpu, 55)
        self.assertEqual(latest.gpu, 65)
    
    def test_get_stats(self):
        """Test getting statistics"""
        # Add some snapshots
        for i in range(10):
            self.history.add_snapshot(cpu=50 + i, gpu=60, ram=40, fps=60)
            time.sleep(0.01)
        
        stats = self.history.get_stats('cpu')
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.current, 59)  # Last value
        self.assertGreater(stats.mean, 50)
        self.assertEqual(stats.min, 50)
        self.assertEqual(stats.max, 59)
    
    def test_trend_detection(self):
        """Test trend detection"""
        # Rising trend
        for i in range(10):
            self.history.add_snapshot(cpu=50 + i*2, gpu=60, ram=40, fps=60)
            time.sleep(0.01)
        
        stats = self.history.get_stats('cpu')
        self.assertEqual(stats.trend, 'rising')
    
    def test_circular_buffer(self):
        """Test circular buffer behavior"""
        history = PerformanceHistory(max_samples=5)
        
        # Add more than max_samples
        for i in range(10):
            history.add_snapshot(cpu=i, gpu=60, ram=40, fps=60)
        
        # Should only keep last 5
        self.assertEqual(history.get_count(), 5)
        
        # Latest should be 9
        latest = history.get_latest()
        self.assertEqual(latest.cpu, 9)
    
    def test_get_recent(self):
        """Test getting recent snapshots"""
        # Add snapshots over time
        for i in range(5):
            self.history.add_snapshot(cpu=50, gpu=60, ram=40, fps=60)
            time.sleep(0.1)
        
        # Get last 0.3 seconds
        recent = self.history.get_recent(seconds=0.3)
        
        # Should get approximately 3 snapshots
        self.assertGreaterEqual(len(recent), 2)
        self.assertLessEqual(len(recent), 4)
    
    def test_get_all(self):
        """Test getting all snapshots"""
        for i in range(5):
            self.history.add_snapshot(cpu=50, gpu=60, ram=40, fps=60)
        
        all_snapshots = self.history.get_all()
        
        self.assertEqual(len(all_snapshots), 5)
    
    def test_clear(self):
        """Test clearing history"""
        self.history.add_snapshot(cpu=50, gpu=60, ram=40, fps=60)
        self.assertEqual(self.history.get_count(), 1)
        
        self.history.clear()
        self.assertEqual(self.history.get_count(), 0)
    
    def test_export_csv(self):
        """Test CSV export"""
        # Add some data
        for i in range(5):
            self.history.add_snapshot(cpu=50+i, gpu=60+i, ram=40+i, fps=60-i)
        
        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            self.history.export_csv(temp_file)
            
            # Check file exists and has content
            self.assertTrue(os.path.exists(temp_file))
            
            with open(temp_file, 'r') as f:
                content = f.read()
                self.assertIn('timestamp', content)
                self.assertIn('cpu', content)
                self.assertIn('gpu', content)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == '__main__':
    unittest.main()
