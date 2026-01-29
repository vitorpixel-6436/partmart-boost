#!/usr/bin/env python3
"""GUI Widget Tests

Version: 0.3.5u (package 3.9a, stage 7.7b.8.1/7.7)

Tests for GUI monitoring widgets.
"""
import unittest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Check if PyQt6 is available
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
@unittest.skipIf(not os.getenv('DISPLAY'), "No display available")
class TestSystemHealthWidget(unittest.TestCase):
    """Tests for SystemHealthWidget"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication"""
        cls.app = QApplication.instance() or QApplication([])
    
    def setUp(self):
        """Set up test fixtures"""
        from ui.widgets.monitoring_panel import SystemHealthWidget
        self.widget = SystemHealthWidget()
    
    def test_widget_creation(self):
        """Test widget can be created"""
        self.assertIsNotNone(self.widget)
        self.assertIsNotNone(self.widget.status_indicator)
        self.assertIsNotNone(self.widget.total_label)
    
    def test_update_health(self):
        """Test health data update"""
        health_data = {
            'status': 'healthy',
            'total_components': 5,
            'healthy_count': 4,
            'degraded_count': 1,
            'unhealthy_count': 0,
            'critical_count': 0,
            'statistics': {
                'uptime': 3600,
                'total_checks': 100,
                'success_rate': 95.0
            }
        }
        
        self.widget.update_health(health_data)
        
        # Verify status updated
        self.assertEqual(self.widget.status_indicator.text(), 'HEALTHY')
    
    def test_status_colors(self):
        """Test status color changes"""
        statuses = ['healthy', 'degraded', 'unhealthy', 'critical']
        
        for status in statuses:
            health_data = {
                'status': status,
                'total_components': 1,
                'healthy_count': 0,
                'degraded_count': 0,
                'unhealthy_count': 0,
                'critical_count': 0,
                'statistics': {'uptime': 0, 'total_checks': 0, 'success_rate': 0}
            }
            
            self.widget.update_health(health_data)
            self.assertEqual(self.widget.status_indicator.text(), status.upper())


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
@unittest.skipIf(not os.getenv('DISPLAY'), "No display available")
class TestComponentStatusWidget(unittest.TestCase):
    """Tests for ComponentStatusWidget"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication"""
        cls.app = QApplication.instance() or QApplication([])
    
    def setUp(self):
        """Set up test fixtures"""
        from ui.widgets.monitoring_panel import ComponentStatusWidget
        self.widget = ComponentStatusWidget()
    
    def test_widget_creation(self):
        """Test widget can be created"""
        self.assertIsNotNone(self.widget)
        self.assertIsNotNone(self.widget.table)
        self.assertEqual(self.widget.table.columnCount(), 5)
    
    def test_update_components(self):
        """Test component update"""
        import time
        
        components = {
            'Component1': {
                'status': 'healthy',
                'message': 'OK',
                'consecutive_failures': 0,
                'last_check': time.time()
            },
            'Component2': {
                'status': 'degraded',
                'message': 'Warning',
                'consecutive_failures': 1,
                'last_check': time.time() - 60
            }
        }
        
        self.widget.update_components(components)
        
        # Verify rows added
        self.assertEqual(self.widget.table.rowCount(), 2)
    
    def test_empty_components(self):
        """Test with no components"""
        self.widget.update_components({})
        self.assertEqual(self.widget.table.rowCount(), 0)


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
@unittest.skipIf(not os.getenv('DISPLAY'), "No display available")
class TestMonitoringPanel(unittest.TestCase):
    """Tests for MonitoringPanel"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication"""
        cls.app = QApplication.instance() or QApplication([])
    
    def setUp(self):
        """Set up test fixtures"""
        from ui.widgets.monitoring_panel import MonitoringPanel
        self.panel = MonitoringPanel()
    
    def test_panel_creation(self):
        """Test panel can be created"""
        self.assertIsNotNone(self.panel)
        self.assertIsNotNone(self.panel.tabs)
        self.assertEqual(self.panel.tabs.count(), 3)
    
    def test_set_monitoring_systems(self):
        """Test setting monitoring systems"""
        # Create mock systems
        health_monitor = Mock()
        error_reporter = Mock()
        recovery_coordinator = Mock()
        recovery_coordinator.is_auto_recovery_enabled.return_value = False
        
        # Set systems
        self.panel.set_monitoring_systems(
            health_monitor=health_monitor,
            error_reporter=error_reporter,
            recovery_coordinator=recovery_coordinator
        )
        
        # Verify set
        self.assertEqual(self.panel._health_monitor, health_monitor)
        self.assertEqual(self.panel._error_reporter, error_reporter)
        self.assertEqual(self.panel._recovery_coordinator, recovery_coordinator)
    
    def test_start_stop_updates(self):
        """Test starting and stopping updates"""
        # Start updates
        self.panel.start_updates(interval=100)
        self.assertIsNotNone(self.panel._update_timer)
        self.assertTrue(self.panel._update_timer.isActive())
        
        # Stop updates
        self.panel.stop_updates()
        self.assertFalse(self.panel._update_timer.isActive())


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
@unittest.skipIf(not os.getenv('DISPLAY'), "No display available")
class TestAlertNotification(unittest.TestCase):
    """Tests for AlertNotification"""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication"""
        cls.app = QApplication.instance() or QApplication([])
    
    def test_notification_creation(self):
        """Test notification can be created"""
        from ui.widgets.alert_notification import AlertNotification
        
        alert_data = {
            'level': 'error',
            'component': 'TestComponent',
            'message': 'Test message',
            'details': 'Test details'
        }
        
        notification = AlertNotification(alert_data)
        self.assertIsNotNone(notification)
    
    def test_notification_levels(self):
        """Test different notification levels"""
        from ui.widgets.alert_notification import AlertNotification
        
        levels = ['info', 'warning', 'error', 'critical']
        
        for level in levels:
            alert_data = {
                'level': level,
                'component': 'TestComponent',
                'message': f'Test {level} message'
            }
            
            notification = AlertNotification(alert_data)
            self.assertIsNotNone(notification)


if __name__ == '__main__':
    unittest.main(verbosity=2)
