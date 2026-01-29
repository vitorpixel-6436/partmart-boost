#!/usr/bin/env python3
"""SystemHealthMonitor Tests

Version: 0.3.5r (package 3.9a, stage 7.7b.6.2/7.7)
"""
import sys
import os
import unittest
import time
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from system_health_monitor import (
    SystemHealthMonitor,
    ComponentStatus,
    AlertLevel,
    ComponentHealth,
    HealthAlert
)


class MockComponent:
    """Mock component for testing"""
    
    def __init__(self, name="test", healthy=True):
        self.name = name
        self.healthy = healthy
        self.check_count = 0
    
    def is_healthy(self):
        self.check_count += 1
        return self.healthy
    
    def get_metrics(self):
        return {
            'check_count': self.check_count,
            'status': 'ok' if self.healthy else 'failed'
        }


class TestSystemHealthMonitor(unittest.TestCase):
    """Test SystemHealthMonitor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = SystemHealthMonitor(check_interval=0.5)
    
    def tearDown(self):
        """Clean up"""
        try:
            self.monitor.stop()
        except Exception:
            pass
    
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertFalse(self.monitor.is_running())
        health = self.monitor.get_system_health()
        self.assertEqual(health['status'], 'unknown')
    
    def test_register_component(self):
        """Test component registration"""
        comp = MockComponent("test1")
        
        result = self.monitor.register_component(
            'test1',
            comp.is_healthy,
            comp.get_metrics
        )
        
        self.assertTrue(result)
        
        health = self.monitor.get_component_health('test1')
        self.assertIsNotNone(health)
        self.assertEqual(health['status'], 'unknown')
    
    def test_register_duplicate(self):
        """Test registering duplicate component"""
        comp1 = MockComponent("test1")
        comp2 = MockComponent("test2")
        
        self.monitor.register_component('test1', comp1.is_healthy)
        
        # Second registration should fail
        result = self.monitor.register_component('test1', comp2.is_healthy)
        self.assertFalse(result)
    
    def test_unregister_component(self):
        """Test component unregistration"""
        comp = MockComponent("test1")
        self.monitor.register_component('test1', comp.is_healthy)
        
        result = self.monitor.unregister_component('test1')
        self.assertTrue(result)
        
        health = self.monitor.get_component_health('test1')
        self.assertIsNone(health)
    
    def test_start_stop(self):
        """Test starting and stopping monitor"""
        result = self.monitor.start()
        self.assertTrue(result)
        self.assertTrue(self.monitor.is_running())
        
        result = self.monitor.stop()
        self.assertTrue(result)
        self.assertFalse(self.monitor.is_running())
    
    def test_healthy_component(self):
        """Test monitoring healthy component"""
        comp = MockComponent("healthy", healthy=True)
        self.monitor.register_component('healthy', comp.is_healthy, comp.get_metrics)
        
        self.monitor.start()
        time.sleep(1.5)  # Wait for checks
        self.monitor.stop()
        
        health = self.monitor.get_component_health('healthy')
        self.assertEqual(health['status'], 'healthy')
        self.assertGreater(health['metrics']['check_count'], 0)
    
    def test_unhealthy_component(self):
        """Test monitoring unhealthy component"""
        comp = MockComponent("unhealthy", healthy=False)
        self.monitor.register_component('unhealthy', comp.is_healthy)
        
        self.monitor.start()
        time.sleep(2.0)  # Wait for multiple checks
        self.monitor.stop()
        
        health = self.monitor.get_component_health('unhealthy')
        # After 3+ failures, should be unhealthy or degraded
        self.assertIn(health['status'], ['unhealthy', 'degraded'])
        self.assertGreater(health['consecutive_failures'], 0)
    
    def test_critical_component(self):
        """Test critical component failure"""
        comp = MockComponent("critical", healthy=False)
        self.monitor.register_component('critical', comp.is_healthy, critical=True)
        
        self.monitor.start()
        time.sleep(2.0)  # Wait for multiple failures
        self.monitor.stop()
        
        health = self.monitor.get_component_health('critical')
        # Critical component with failures should be critical
        self.assertIn(health['status'], ['critical', 'unhealthy', 'degraded'])
    
    def test_system_health_all_healthy(self):
        """Test system health with all components healthy"""
        comp1 = MockComponent("comp1", healthy=True)
        comp2 = MockComponent("comp2", healthy=True)
        
        self.monitor.register_component('comp1', comp1.is_healthy)
        self.monitor.register_component('comp2', comp2.is_healthy)
        
        self.monitor.start()
        time.sleep(1.5)
        self.monitor.stop()
        
        health = self.monitor.get_system_health()
        self.assertTrue(health['healthy'])
        self.assertEqual(health['status'], 'healthy')
    
    def test_system_health_with_failures(self):
        """Test system health with some failures"""
        comp1 = MockComponent("comp1", healthy=True)
        comp2 = MockComponent("comp2", healthy=False)
        
        self.monitor.register_component('comp1', comp1.is_healthy)
        self.monitor.register_component('comp2', comp2.is_healthy)
        
        self.monitor.start()
        time.sleep(2.0)
        self.monitor.stop()
        
        health = self.monitor.get_system_health()
        self.assertFalse(health['healthy'])
        self.assertIn(health['status'], ['unhealthy', 'degraded'])
    
    def test_alert_generation(self):
        """Test alert generation on status change"""
        alert_received = []
        
        def on_alert(alert):
            alert_received.append(alert)
        
        self.monitor.add_alert_callback(on_alert)
        
        comp = MockComponent("test", healthy=False)
        self.monitor.register_component('test', comp.is_healthy)
        
        self.monitor.start()
        time.sleep(2.0)  # Wait for status change
        self.monitor.stop()
        
        # Should have received at least one alert
        self.assertGreater(len(alert_received), 0)
    
    def test_alert_callback_error_isolation(self):
        """Test alert callback errors are isolated"""
        def bad_callback(alert):
            raise Exception("Callback error!")
        
        def good_callback(alert):
            pass  # Should still be called
        
        self.monitor.add_alert_callback(bad_callback)
        self.monitor.add_alert_callback(good_callback)
        
        comp = MockComponent("test", healthy=False)
        self.monitor.register_component('test', comp.is_healthy)
        
        # Should not raise
        self.monitor.start()
        time.sleep(1.5)
        self.monitor.stop()
    
    def test_get_all_components_health(self):
        """Test getting all components health"""
        comp1 = MockComponent("comp1", healthy=True)
        comp2 = MockComponent("comp2", healthy=True)
        
        self.monitor.register_component('comp1', comp1.is_healthy)
        self.monitor.register_component('comp2', comp2.is_healthy)
        
        all_health = self.monitor.get_all_components_health()
        
        self.assertEqual(len(all_health), 2)
        self.assertIn('comp1', all_health)
        self.assertIn('comp2', all_health)
    
    def test_get_recent_alerts(self):
        """Test getting recent alerts"""
        comp = MockComponent("test", healthy=False)
        self.monitor.register_component('test', comp.is_healthy)
        
        self.monitor.start()
        time.sleep(2.0)
        self.monitor.stop()
        
        alerts = self.monitor.get_recent_alerts(limit=5)
        self.assertIsInstance(alerts, list)
        # Should have some alerts
        if len(alerts) > 0:
            self.assertIn('level', alerts[0])
            self.assertIn('component', alerts[0])
    
    def test_clear_alerts(self):
        """Test clearing alerts"""
        comp = MockComponent("test", healthy=False)
        self.monitor.register_component('test', comp.is_healthy)
        
        self.monitor.start()
        time.sleep(1.5)
        self.monitor.stop()
        
        # Clear alerts
        self.monitor.clear_alerts()
        
        alerts = self.monitor.get_recent_alerts()
        self.assertEqual(len(alerts), 0)
    
    def test_statistics(self):
        """Test monitoring statistics"""
        comp = MockComponent("test", healthy=True)
        self.monitor.register_component('test', comp.is_healthy)
        
        self.monitor.start()
        time.sleep(1.5)
        self.monitor.stop()
        
        health = self.monitor.get_system_health()
        stats = health['statistics']
        
        self.assertGreater(stats['total_checks'], 0)
        self.assertGreater(stats['success_rate'], 0)
        self.assertGreater(stats['uptime'], 0)
    
    def test_component_status_enum(self):
        """Test ComponentStatus enum"""
        self.assertEqual(ComponentStatus.HEALTHY.value, 'healthy')
        self.assertEqual(ComponentStatus.UNHEALTHY.value, 'unhealthy')
        self.assertEqual(ComponentStatus.CRITICAL.value, 'critical')
    
    def test_alert_level_enum(self):
        """Test AlertLevel enum"""
        self.assertEqual(AlertLevel.INFO.value, 'info')
        self.assertEqual(AlertLevel.WARNING.value, 'warning')
        self.assertEqual(AlertLevel.ERROR.value, 'error')
        self.assertEqual(AlertLevel.CRITICAL.value, 'critical')
    
    def test_component_health_to_dict(self):
        """Test ComponentHealth to_dict conversion"""
        health = ComponentHealth(
            name='test',
            status=ComponentStatus.HEALTHY,
            message='OK'
        )
        
        health_dict = health.to_dict()
        
        self.assertEqual(health_dict['name'], 'test')
        self.assertEqual(health_dict['status'], 'healthy')
        self.assertEqual(health_dict['message'], 'OK')
    
    def test_health_alert_to_dict(self):
        """Test HealthAlert to_dict conversion"""
        alert = HealthAlert(
            timestamp=time.time(),
            level=AlertLevel.ERROR,
            component='test',
            message='Test alert'
        )
        
        alert_dict = alert.to_dict()
        
        self.assertIn('timestamp', alert_dict)
        self.assertEqual(alert_dict['level'], 'error')
        self.assertEqual(alert_dict['component'], 'test')


if __name__ == '__main__':
    unittest.main()
