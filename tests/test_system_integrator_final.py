#!/usr/bin/env python3
"""Tests for SystemIntegratorFinal

Version: 0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)
"""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.system_integrator_final import SystemIntegratorFinal, SystemStatus


class TestSystemIntegratorFinal(unittest.TestCase):
    """Test SystemIntegratorFinal"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.integrator = SystemIntegratorFinal()
    
    def test_initialization(self):
        """Test integrator initialization"""
        self.assertIsNotNone(self.integrator)
        self.assertFalse(self.integrator._initialized)
        self.assertFalse(self.integrator._running)
    
    def test_initialize(self):
        """Test system initialization"""
        result = self.integrator.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.integrator._initialized)
    
    def test_double_initialize(self):
        """Test double initialization (should be safe)"""
        self.integrator.initialize()
        result = self.integrator.initialize()
        
        self.assertTrue(result)
        self.assertTrue(self.integrator._initialized)
    
    def test_start_without_initialize(self):
        """Test start automatically initializes"""
        result = self.integrator.start()
        
        self.assertTrue(result)
        self.assertTrue(self.integrator._initialized)
        self.assertTrue(self.integrator._running)
        
        # Cleanup
        self.integrator.stop()
    
    def test_start_and_stop(self):
        """Test start and stop sequence"""
        # Start
        self.assertTrue(self.integrator.start())
        self.assertTrue(self.integrator._running)
        
        # Stop
        self.assertTrue(self.integrator.stop())
        self.assertFalse(self.integrator._running)
    
    def test_double_start(self):
        """Test double start (should be safe)"""
        self.integrator.start()
        result = self.integrator.start()
        
        self.assertTrue(result)
        self.assertTrue(self.integrator._running)
        
        # Cleanup
        self.integrator.stop()
    
    def test_double_stop(self):
        """Test double stop (should be safe)"""
        self.integrator.start()
        self.integrator.stop()
        result = self.integrator.stop()
        
        self.assertTrue(result)
        self.assertFalse(self.integrator._running)
    
    def test_get_status_not_initialized(self):
        """Test getting status before initialization"""
        status = self.integrator.get_status()
        
        self.assertIsInstance(status, SystemStatus)
        self.assertFalse(status.initialized)
        self.assertFalse(status.running)
    
    def test_get_status_initialized(self):
        """Test getting status after initialization"""
        self.integrator.initialize()
        status = self.integrator.get_status()
        
        self.assertTrue(status.initialized)
        self.assertFalse(status.running)
    
    def test_get_status_running(self):
        """Test getting status while running"""
        self.integrator.start()
        status = self.integrator.get_status()
        
        self.assertTrue(status.initialized)
        self.assertTrue(status.running)
        self.assertGreaterEqual(status.uptime, 0.0)
        
        # Cleanup
        self.integrator.stop()
    
    def test_print_status(self):
        """Test printing status (should not crash)"""
        self.integrator.initialize()
        self.integrator.print_status()
        # Should not crash
    
    def test_config_manager_integration(self):
        """Test config manager integration"""
        self.integrator.initialize()
        
        # Should have config manager
        self.assertIsNotNone(self.integrator.config_manager)
    
    def test_components_created(self):
        """Test all components are created"""
        self.integrator.initialize()
        
        # Check components
        self.assertIsNotNone(self.integrator.error_reporter)
        self.assertIsNotNone(self.integrator.health_monitor)
        self.assertIsNotNone(self.integrator.recovery_coordinator)


class TestSystemStatus(unittest.TestCase):
    """Test SystemStatus dataclass"""
    
    def test_default_status(self):
        """Test default status values"""
        status = SystemStatus()
        
        self.assertFalse(status.initialized)
        self.assertFalse(status.running)
        self.assertEqual(status.error_count, 0)
        self.assertEqual(status.component_count, 0)
        self.assertEqual(status.uptime, 0.0)
    
    def test_custom_status(self):
        """Test custom status values"""
        status = SystemStatus(
            initialized=True,
            running=True,
            error_count=5,
            component_count=10,
            healthy_count=8,
            uptime=123.45
        )
        
        self.assertTrue(status.initialized)
        self.assertTrue(status.running)
        self.assertEqual(status.error_count, 5)
        self.assertEqual(status.component_count, 10)
        self.assertEqual(status.healthy_count, 8)
        self.assertEqual(status.uptime, 123.45)


if __name__ == '__main__':
    unittest.main(verbosity=2)
