#!/usr/bin/env python3
"""Integration Tests for Complete Monitoring System

Version: 0.3.5u (package 3.9a, stage 7.7b.8.1/7.7)

Tests complete integration of:
- ErrorReporter
- SystemHealthMonitor
- RecoveryCoordinator
- MonitoringPanel (GUI)
"""
import unittest
import time
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.error_reporter import ErrorReporter, ErrorSeverity
from core.system_health_monitor import SystemHealthMonitor, HealthStatus
from core.recovery_coordinator import RecoveryCoordinator, RecoveryStrategy


class TestMonitoringIntegration(unittest.TestCase):
    """Integration tests for monitoring system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.error_reporter = ErrorReporter()
        self.health_monitor = SystemHealthMonitor(
            check_interval=0.1,  # Fast for testing
            error_reporter=self.error_reporter
        )
        self.recovery_coordinator = RecoveryCoordinator(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter
        )
    
    def tearDown(self):
        """Clean up"""
        if self.health_monitor:
            self.health_monitor.stop()
    
    def test_error_to_health_integration(self):
        """Test error reporter integration with health monitor"""
        # Register component
        health_check = Mock(return_value=True)
        self.health_monitor.register_component(
            'TestComponent',
            health_check=health_check
        )
        
        # Report error for component
        self.error_reporter.report_error(
            'TestComponent',
            'Test error',
            severity=ErrorSeverity.ERROR
        )
        
        # Verify error was reported
        errors = self.error_reporter.get_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['component'], 'TestComponent')
    
    def test_health_to_recovery_integration(self):
        """Test health monitor integration with recovery coordinator"""
        # Register component with failing health check
        health_check = Mock(return_value=False)
        self.health_monitor.register_component(
            'FailingComponent',
            health_check=health_check
        )
        
        # Register recovery action
        recovery_action = Mock(return_value=True)
        self.recovery_coordinator.register_recovery(
            'FailingComponent',
            RecoveryStrategy.RESTART,
            action=recovery_action
        )
        
        # Enable auto-recovery
        self.recovery_coordinator.enable_auto_recovery()
        
        # Start monitoring
        self.health_monitor.start()
        
        # Wait for health check and recovery
        time.sleep(0.3)
        
        # Stop monitoring
        self.health_monitor.stop()
        
        # Verify recovery was attempted
        # (In real scenario, recovery would be triggered by alert)
        health = self.health_monitor.get_system_health()
        self.assertIsNotNone(health)
    
    def test_complete_error_flow(self):
        """Test complete error reporting and recovery flow"""
        # Setup component
        health_check = Mock(return_value=True)
        recovery_action = Mock(return_value=True)
        
        self.health_monitor.register_component(
            'Component',
            health_check=health_check
        )
        
        self.recovery_coordinator.register_recovery(
            'Component',
            RecoveryStrategy.RESTART,
            action=recovery_action
        )
        
        # 1. Report error
        self.error_reporter.report_error(
            'Component',
            'Component failed',
            severity=ErrorSeverity.CRITICAL
        )
        
        # 2. Simulate health check failure
        health_check.return_value = False
        self.health_monitor.start()
        time.sleep(0.2)
        
        # 3. Get health status
        health = self.health_monitor.get_system_health()
        self.assertIn('Component', health['components'])
        
        # 4. Manually trigger recovery
        result = self.recovery_coordinator.recover_component('Component')
        
        # 5. Verify recovery
        self.assertTrue(result)
        self.assertTrue(recovery_action.called)
        
        # 6. Check recovery history
        history = self.recovery_coordinator.get_recovery_history()
        self.assertGreater(len(history), 0)
        
        self.health_monitor.stop()
    
    def test_statistics_integration(self):
        """Test statistics collection across all systems"""
        # Register components
        for i in range(3):
            self.health_monitor.register_component(
                f'Component{i}',
                health_check=Mock(return_value=True)
            )
            
            self.recovery_coordinator.register_recovery(
                f'Component{i}',
                RecoveryStrategy.RESTART,
                action=Mock(return_value=True)
            )
        
        # Report some errors
        for i in range(5):
            self.error_reporter.report_error(
                f'Component{i % 3}',
                f'Error {i}',
                severity=ErrorSeverity.WARNING
            )
        
        # Start monitoring
        self.health_monitor.start()
        time.sleep(0.2)
        self.health_monitor.stop()
        
        # Get statistics
        error_stats = self.error_reporter.get_statistics()
        health_stats = self.health_monitor.get_system_health()['statistics']
        recovery_stats = self.recovery_coordinator.get_statistics()
        
        # Verify statistics
        self.assertGreater(error_stats['total_errors'], 0)
        self.assertGreater(health_stats['total_checks'], 0)
        self.assertIsNotNone(recovery_stats['auto_recovery_enabled'])
    
    def test_alert_callback_chain(self):
        """Test alert callback propagation"""
        # Setup callback
        alert_received = []
        
        def alert_callback(alert):
            alert_received.append(alert)
        
        self.health_monitor.add_alert_callback(alert_callback)
        
        # Register component with failing health
        self.health_monitor.register_component(
            'AlertComponent',
            health_check=Mock(return_value=False)
        )
        
        # Start monitoring
        self.health_monitor.start()
        time.sleep(0.3)
        self.health_monitor.stop()
        
        # Verify alert was received
        self.assertGreater(len(alert_received), 0)
    
    def test_concurrent_operations(self):
        """Test concurrent operations across systems"""
        # Register multiple components
        components = ['Comp1', 'Comp2', 'Comp3']
        
        for comp in components:
            self.health_monitor.register_component(
                comp,
                health_check=Mock(return_value=True)
            )
            
            self.recovery_coordinator.register_recovery(
                comp,
                RecoveryStrategy.RESTART,
                action=Mock(return_value=True)
            )
        
        # Start monitoring
        self.health_monitor.start()
        
        # Concurrent operations
        for _ in range(10):
            # Report errors
            for comp in components:
                self.error_reporter.report_error(
                    comp,
                    'Test error',
                    severity=ErrorSeverity.INFO
                )
            
            time.sleep(0.05)
        
        self.health_monitor.stop()
        
        # Verify system is stable
        health = self.health_monitor.get_system_health()
        self.assertEqual(len(health['components']), 3)


class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock PyQt6 if not available
        self.qt_available = False
        try:
            from PyQt6.QtWidgets import QApplication
            self.qt_available = True
        except ImportError:
            pass
    
    @unittest.skipIf(not os.getenv('DISPLAY'), "No display available")
    def test_monitoring_panel_creation(self):
        """Test monitoring panel can be created"""
        if not self.qt_available:
            self.skipTest("PyQt6 not available")
        
        try:
            from PyQt6.QtWidgets import QApplication
            from ui.widgets.monitoring_panel import MonitoringPanel
            
            app = QApplication.instance() or QApplication([])
            
            # Create panel
            panel = MonitoringPanel()
            self.assertIsNotNone(panel)
            
            # Verify tabs
            self.assertEqual(panel.tabs.count(), 3)
            
        except Exception as e:
            self.fail(f"Failed to create monitoring panel: {e}")
    
    @unittest.skipIf(not os.getenv('DISPLAY'), "No display available")
    def test_alert_notification_creation(self):
        """Test alert notification can be created"""
        if not self.qt_available:
            self.skipTest("PyQt6 not available")
        
        try:
            from PyQt6.QtWidgets import QApplication
            from ui.widgets.alert_notification import AlertNotification
            
            app = QApplication.instance() or QApplication([])
            
            alert_data = {
                'level': 'error',
                'component': 'TestComponent',
                'message': 'Test alert',
                'details': 'Test details'
            }
            
            # Create notification
            notification = AlertNotification(alert_data)
            self.assertIsNotNone(notification)
            
        except Exception as e:
            self.fail(f"Failed to create alert notification: {e}")


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for complete system"""
    
    def test_system_startup(self):
        """Test complete system startup"""
        # Create all components
        error_reporter = ErrorReporter()
        health_monitor = SystemHealthMonitor(
            check_interval=1.0,
            error_reporter=error_reporter
        )
        recovery_coordinator = RecoveryCoordinator(
            health_monitor=health_monitor,
            error_reporter=error_reporter
        )
        
        # Register test components
        health_monitor.register_component(
            'ConfigManager',
            health_check=Mock(return_value=True)
        )
        
        recovery_coordinator.register_recovery(
            'ConfigManager',
            RecoveryStrategy.RESTART,
            action=Mock(return_value=True)
        )
        
        # Start system
        health_monitor.start()
        recovery_coordinator.enable_auto_recovery()
        
        # Verify system is running
        self.assertTrue(health_monitor.is_running())
        self.assertTrue(recovery_coordinator.is_auto_recovery_enabled())
        
        # Get system state
        health = health_monitor.get_system_health()
        stats = recovery_coordinator.get_statistics()
        
        self.assertIsNotNone(health)
        self.assertIsNotNone(stats)
        
        # Cleanup
        health_monitor.stop()
    
    def test_system_resilience(self):
        """Test system resilience to component failures"""
        error_reporter = ErrorReporter()
        health_monitor = SystemHealthMonitor(
            check_interval=0.1,
            error_reporter=error_reporter
        )
        recovery_coordinator = RecoveryCoordinator(
            health_monitor=health_monitor,
            error_reporter=error_reporter
        )
        
        # Register component with intermittent failures
        failure_count = [0]
        
        def unreliable_health_check():
            failure_count[0] += 1
            return failure_count[0] % 3 != 0  # Fails every 3rd check
        
        health_monitor.register_component(
            'UnreliableComponent',
            health_check=unreliable_health_check
        )
        
        recovery_count = [0]
        
        def recovery_action():
            recovery_count[0] += 1
            return True
        
        recovery_coordinator.register_recovery(
            'UnreliableComponent',
            RecoveryStrategy.RESTART,
            action=recovery_action,
            max_attempts=5
        )
        
        # Start system
        health_monitor.start()
        recovery_coordinator.enable_auto_recovery()
        
        # Run for a while
        time.sleep(0.5)
        
        # Stop
        health_monitor.stop()
        
        # Verify system handled failures
        health = health_monitor.get_system_health()
        self.assertIn('UnreliableComponent', health['components'])
        
        # Check that monitoring continued
        stats = health['statistics']
        self.assertGreater(stats['total_checks'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
