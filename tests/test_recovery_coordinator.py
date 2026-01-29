#!/usr/bin/env python3
"""RecoveryCoordinator Tests

Version: 0.3.5s (package 3.9a, stage 7.7b.6.3/7.7)
"""
import sys
import os
import unittest
import time
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from recovery_coordinator import (
    RecoveryCoordinator,
    RecoveryStrategy,
    RecoveryStatus,
    RecoveryAction,
    RecoveryRecord
)


class MockComponent:
    """Mock component for testing"""
    
    def __init__(self, name="test"):
        self.name = name
        self.running = False
        self.restart_count = 0
        self.fail_until = 0
    
    def restart(self):
        self.restart_count += 1
        if self.restart_count <= self.fail_until:
            return False
        self.running = True
        return True
    
    def rollback(self):
        self.running = False
        return True
    
    def is_running(self):
        return self.running


class TestRecoveryCoordinator(unittest.TestCase):
    """Test RecoveryCoordinator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.coordinator = RecoveryCoordinator()
    
    def test_initialization(self):
        """Test coordinator initialization"""
        self.assertFalse(self.coordinator.is_auto_recovery_enabled())
        stats = self.coordinator.get_statistics()
        self.assertEqual(stats['total_recoveries'], 0)
    
    def test_register_recovery(self):
        """Test recovery registration"""
        comp = MockComponent("test1")
        
        result = self.coordinator.register_recovery(
            'test1',
            RecoveryStrategy.RESTART,
            action=comp.restart
        )
        
        self.assertTrue(result)
        
        stats = self.coordinator.get_statistics()
        self.assertEqual(stats['registered_components'], 1)
        self.assertIn('test1', stats['components'])
    
    def test_register_multiple_strategies(self):
        """Test registering multiple strategies for one component"""
        comp = MockComponent("test1")
        
        self.coordinator.register_recovery(
            'test1', RecoveryStrategy.RESTART, comp.restart
        )
        self.coordinator.register_recovery(
            'test1', RecoveryStrategy.ROLLBACK, comp.rollback
        )
        
        stats = self.coordinator.get_statistics()
        self.assertEqual(stats['registered_components'], 1)
    
    def test_unregister_recovery(self):
        """Test recovery unregistration"""
        comp = MockComponent("test1")
        self.coordinator.register_recovery('test1', RecoveryStrategy.RESTART, comp.restart)
        
        result = self.coordinator.unregister_recovery('test1')
        self.assertTrue(result)
        
        stats = self.coordinator.get_statistics()
        self.assertEqual(stats['registered_components'], 0)
    
    def test_successful_recovery(self):
        """Test successful recovery"""
        comp = MockComponent("test1")
        self.coordinator.register_recovery('test1', RecoveryStrategy.RESTART, comp.restart)
        
        result = self.coordinator.recover_component('test1')
        
        self.assertTrue(result)
        self.assertTrue(comp.running)
        self.assertEqual(comp.restart_count, 1)
        
        stats = self.coordinator.get_statistics()
        self.assertEqual(stats['successful_recoveries'], 1)
        self.assertEqual(stats['success_rate'], 100.0)
    
    def test_failed_recovery(self):
        """Test failed recovery"""
        comp = MockComponent("test1")
        comp.fail_until = 999  # Always fail
        
        self.coordinator.register_recovery(
            'test1',
            RecoveryStrategy.RESTART,
            comp.restart,
            max_attempts=2
        )
        
        result = self.coordinator.recover_component('test1')
        
        self.assertFalse(result)
        self.assertEqual(comp.restart_count, 1)
        
        stats = self.coordinator.get_statistics()
        self.assertEqual(stats['failed_recoveries'], 1)
    
    def test_max_attempts(self):
        """Test max attempts enforcement"""
        comp = MockComponent("test1")
        comp.fail_until = 999
        
        self.coordinator.register_recovery(
            'test1',
            RecoveryStrategy.RESTART,
            comp.restart,
            max_attempts=3,
            cooldown=0.0
        )
        
        # First attempt
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 1)
        
        # Second attempt
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 2)
        
        # Third attempt
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 3)
        
        # Fourth attempt should be blocked
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 3)  # No increase
    
    def test_cooldown_period(self):
        """Test cooldown period"""
        comp = MockComponent("test1")
        
        self.coordinator.register_recovery(
            'test1',
            RecoveryStrategy.RESTART,
            comp.restart,
            cooldown=1.0
        )
        
        # First recovery
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 1)
        
        # Second recovery immediately (should be blocked)
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 1)  # No increase
        
        # Wait for cooldown
        time.sleep(1.1)
        
        # Third recovery (should succeed)
        self.coordinator.recover_component('test1')
        self.assertEqual(comp.restart_count, 2)
    
    def test_rollback_on_failure(self):
        """Test rollback execution on failure"""
        comp = MockComponent("test1")
        comp.fail_until = 999  # Always fail recovery
        
        rollback_called = [False]
        
        def rollback_action():
            rollback_called[0] = True
            return True
        
        self.coordinator.register_recovery(
            'test1',
            RecoveryStrategy.RESTART,
            action=comp.restart,
            rollback_action=rollback_action
        )
        
        self.coordinator.recover_component('test1')
        
        # Rollback should have been called
        self.assertTrue(rollback_called[0])
    
    def test_recovery_history(self):
        """Test recovery history tracking"""
        comp = MockComponent("test1")
        self.coordinator.register_recovery('test1', RecoveryStrategy.RESTART, comp.restart)
        
        # Perform recovery
        self.coordinator.recover_component('test1')
        
        # Get history
        history = self.coordinator.get_recovery_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['component'], 'test1')
        self.assertEqual(history[0]['status'], 'success')
        self.assertEqual(history[0]['strategy'], 'restart')
    
    def test_recovery_history_filtering(self):
        """Test recovery history filtering"""
        comp1 = MockComponent("test1")
        comp2 = MockComponent("test2")
        
        self.coordinator.register_recovery('test1', RecoveryStrategy.RESTART, comp1.restart)
        self.coordinator.register_recovery('test2', RecoveryStrategy.RESTART, comp2.restart)
        
        self.coordinator.recover_component('test1')
        self.coordinator.recover_component('test2')
        
        # Get history for specific component
        history = self.coordinator.get_recovery_history(component='test1')
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['component'], 'test1')
    
    def test_enable_disable_auto_recovery(self):
        """Test auto-recovery enable/disable"""
        self.assertFalse(self.coordinator.is_auto_recovery_enabled())
        
        self.coordinator.enable_auto_recovery()
        self.assertTrue(self.coordinator.is_auto_recovery_enabled())
        
        self.coordinator.disable_auto_recovery()
        self.assertFalse(self.coordinator.is_auto_recovery_enabled())
    
    def test_clear_history(self):
        """Test clearing recovery history"""
        comp = MockComponent("test1")
        self.coordinator.register_recovery('test1', RecoveryStrategy.RESTART, comp.restart)
        
        self.coordinator.recover_component('test1')
        
        history = self.coordinator.get_recovery_history()
        self.assertGreater(len(history), 0)
        
        self.coordinator.clear_history()
        
        history = self.coordinator.get_recovery_history()
        self.assertEqual(len(history), 0)
    
    def test_reset_attempts(self):
        """Test resetting recovery attempts"""
        comp = MockComponent("test1")
        comp.fail_until = 999
        
        self.coordinator.register_recovery(
            'test1',
            RecoveryStrategy.RESTART,
            comp.restart,
            max_attempts=2,
            cooldown=0.0
        )
        
        # Exhaust attempts
        self.coordinator.recover_component('test1')
        self.coordinator.recover_component('test1')
        
        # Should be blocked now
        result = self.coordinator.recover_component('test1')
        self.assertFalse(result)
        
        # Reset attempts
        self.coordinator.reset_attempts('test1')
        
        # Should work again
        result = self.coordinator.recover_component('test1')
        # Will still fail, but attempt was made
        self.assertEqual(comp.restart_count, 3)
    
    def test_statistics(self):
        """Test recovery statistics"""
        comp1 = MockComponent("test1")
        comp2 = MockComponent("test2")
        comp2.fail_until = 999
        
        self.coordinator.register_recovery('test1', RecoveryStrategy.RESTART, comp1.restart)
        self.coordinator.register_recovery('test2', RecoveryStrategy.RESTART, comp2.restart)
        
        # One success, one failure
        self.coordinator.recover_component('test1')
        self.coordinator.recover_component('test2')
        
        stats = self.coordinator.get_statistics()
        
        self.assertEqual(stats['total_recoveries'], 2)
        self.assertEqual(stats['successful_recoveries'], 1)
        self.assertEqual(stats['failed_recoveries'], 1)
        self.assertEqual(stats['success_rate'], 50.0)
    
    def test_recovery_strategy_enum(self):
        """Test RecoveryStrategy enum"""
        self.assertEqual(RecoveryStrategy.RESTART.value, 'restart')
        self.assertEqual(RecoveryStrategy.ROLLBACK.value, 'rollback')
        self.assertEqual(RecoveryStrategy.RESET.value, 'reset')
    
    def test_recovery_status_enum(self):
        """Test RecoveryStatus enum"""
        self.assertEqual(RecoveryStatus.SUCCESS.value, 'success')
        self.assertEqual(RecoveryStatus.FAILED.value, 'failed')
        self.assertEqual(RecoveryStatus.SKIPPED.value, 'skipped')
    
    def test_recovery_record_to_dict(self):
        """Test RecoveryRecord to_dict conversion"""
        record = RecoveryRecord(
            timestamp=time.time(),
            component='test',
            strategy=RecoveryStrategy.RESTART,
            status=RecoveryStatus.SUCCESS,
            attempts=1,
            message='Test'
        )
        
        record_dict = record.to_dict()
        
        self.assertIn('timestamp', record_dict)
        self.assertEqual(record_dict['component'], 'test')
        self.assertEqual(record_dict['strategy'], 'restart')
        self.assertEqual(record_dict['status'], 'success')


if __name__ == '__main__':
    unittest.main()
