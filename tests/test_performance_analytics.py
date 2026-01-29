#!/usr/bin/env python3
"""PerformanceAnalytics Unit Tests

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)
"""
import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from performance_history import PerformanceHistory
from performance_analytics import PerformanceAnalytics, BottleneckType, Severity


class TestPerformanceAnalytics(unittest.TestCase):
    """Test PerformanceAnalytics functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.history = PerformanceHistory(max_samples=100)
        self.analytics = PerformanceAnalytics(self.history)
    
    def test_analyze_no_data(self):
        """Test analysis with no data"""
        report = self.analytics.analyze()
        
        self.assertIsNone(report)
    
    def test_analyze_normal_load(self):
        """Test analysis with normal load"""
        # Add normal load data
        for _ in range(10):
            self.history.add_snapshot(cpu=50, gpu=60, ram=40, fps=60)
        
        report = self.analytics.analyze()
        
        self.assertIsNotNone(report)
        self.assertEqual(report.bottleneck.type, BottleneckType.NONE)
        self.assertGreater(report.score, 50)
    
    def test_detect_cpu_bottleneck(self):
        """Test CPU bottleneck detection"""
        # Add high CPU load
        for _ in range(10):
            self.history.add_snapshot(cpu=95, gpu=60, ram=40, fps=45)
        
        report = self.analytics.analyze()
        
        self.assertEqual(report.bottleneck.type, BottleneckType.CPU)
        self.assertIn(report.bottleneck.severity, [Severity.HIGH, Severity.CRITICAL])
    
    def test_detect_gpu_bottleneck(self):
        """Test GPU bottleneck detection"""
        # Add high GPU load
        for _ in range(10):
            self.history.add_snapshot(cpu=50, gpu=95, ram=40, fps=45)
        
        report = self.analytics.analyze()
        
        self.assertEqual(report.bottleneck.type, BottleneckType.GPU)
    
    def test_detect_ram_bottleneck(self):
        """Test RAM bottleneck detection"""
        # Add high RAM usage
        for _ in range(10):
            self.history.add_snapshot(cpu=50, gpu=60, ram=95, fps=50)
        
        report = self.analytics.analyze()
        
        self.assertEqual(report.bottleneck.type, BottleneckType.RAM)
    
    def test_detect_thermal_bottleneck(self):
        """Test thermal throttling detection"""
        # Add high temperature
        for _ in range(10):
            self.history.add_snapshot(cpu=70, gpu=80, ram=40, fps=45, gpu_temp=90)
        
        report = self.analytics.analyze()
        
        self.assertEqual(report.bottleneck.type, BottleneckType.THERMAL)
    
    def test_performance_score(self):
        """Test performance scoring"""
        # Good performance
        for _ in range(10):
            self.history.add_snapshot(cpu=40, gpu=50, ram=30, fps=60)
        
        report = self.analytics.analyze()
        
        self.assertGreater(report.score, 70)
        self.assertLessEqual(report.score, 100)
    
    def test_efficiency_calculation(self):
        """Test efficiency calculation"""
        # High usage, good FPS = efficient
        for _ in range(10):
            self.history.add_snapshot(cpu=70, gpu=80, ram=50, fps=60)
        
        report = self.analytics.analyze()
        
        self.assertGreater(report.efficiency, 60)
    
    def test_recommendations(self):
        """Test recommendation generation"""
        # Add bottleneck scenario
        for _ in range(10):
            self.history.add_snapshot(cpu=95, gpu=60, ram=40, fps=45)
        
        report = self.analytics.analyze()
        
        self.assertGreater(len(report.recommendations), 0)
        
        # Should have CPU-related recommendations
        cpu_recs = [r for r in report.recommendations if 'CPU' in r.title or 'cpu' in r.title.lower()]
        self.assertGreater(len(cpu_recs), 0)
    
    def test_trend_analysis(self):
        """Test trend analysis"""
        # Add rising CPU trend
        for i in range(10):
            self.history.add_snapshot(cpu=50 + i*2, gpu=60, ram=40, fps=60)
        
        report = self.analytics.analyze()
        
        self.assertIn('cpu', report.trends)
        self.assertEqual(report.trends['cpu'], 'rising')
    
    def test_severity_levels(self):
        """Test severity classification"""
        # Critical severity
        for _ in range(10):
            self.history.add_snapshot(cpu=98, gpu=60, ram=40, fps=30)
        
        report = self.analytics.analyze()
        self.assertEqual(report.bottleneck.severity, Severity.CRITICAL)
        
        # Low severity
        self.history.clear()
        for _ in range(10):
            self.history.add_snapshot(cpu=88, gpu=60, ram=40, fps=55)
        
        report = self.analytics.analyze()
        self.assertEqual(report.bottleneck.severity, Severity.LOW)


if __name__ == '__main__':
    unittest.main()
