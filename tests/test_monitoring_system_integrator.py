#!/usr/bin/env python3
"""Tests for MonitoringSystemIntegrator

Version: 0.3.6 (package 3.9a, stage 7.7b.9)
"""
import unittest
import tempfile
import os
import time
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from core.monitoring_system_integrator import (
        MonitoringSystemIntegrator,
        MonitoringConfig,
        SystemStatus
    )
    INTEGRATOR_AVAILABLE = True
except ImportError:
    INTEGRATOR_AVAILABLE = False


@unittest.skipIf(not INTEGRATOR_AVAILABLE, "Integrator not available")
class TestMonitoringSystemIntegrator(unittest.TestCase):
    """Test MonitoringSystemIntegrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create config with temp paths
        self.config = MonitoringConfig(
            historical_db_path=os.path.join(self.temp_dir, 'test.db'),
            health_check_interval=0.5,  # Fast for testing
            collection_interval=1.0
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test integrator initialization"""
        integrator = MonitoringSystemIntegrator(self.config)
        
        result = integrator.initialize()
        self.assertTrue(result)
    
    def test_default_config(self):
        """Test with default configuration"""
        integrator = MonitoringSystemIntegrator()
        self.assertIsNotNone(integrator.config)
    
    def test_start_stop(self):
        """Test starting and stopping system"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        
        # Start
        result = integrator.start()
        self.assertTrue(result)
        self.assertTrue(integrator.is_running())
        
        # Stop
        integrator.stop()
        self.assertFalse(integrator.is_running())
    
    def test_double_start(self):
        """Test starting already running system"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        
        # First start
        result1 = integrator.start()
        self.assertTrue(result1)
        
        # Second start should return False
        result2 = integrator.start()
        self.assertFalse(result2)
        
        integrator.stop()
    
    def test_get_status(self):
        """Test getting system status"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        integrator.start()
        
        status = integrator.get_status()
        
        self.assertIsInstance(status, SystemStatus)
        self.assertTrue(status.is_running)
        self.assertGreaterEqual(status.uptime, 0)
        
        integrator.stop()
    
    def test_component_access(self):
        """Test accessing components"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        
        # Components should be accessible
        error_reporter = integrator.get_error_reporter()
        health_monitor = integrator.get_health_monitor()
        recovery_coordinator = integrator.get_recovery_coordinator()
        historical_store = integrator.get_historical_store()
        data_aggregator = integrator.get_data_aggregator()
        
        # At least some should be initialized
        self.assertIsNotNone(error_reporter)
    
    def test_performance_stats(self):
        """Test performance statistics"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        
        stats = integrator.get_performance_stats()
        
        self.assertIn('initialization_time', stats)
        self.assertGreaterEqual(stats['initialization_time'], 0)
    
    def test_status_reporting(self):
        """Test status reporting"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        integrator.start()
        
        # Wait a bit
        time.sleep(0.5)
        
        status = integrator.get_status()
        
        # Check components are active
        self.assertTrue(status.error_reporter_active)
        self.assertTrue(status.health_monitor_active)
        self.assertTrue(status.recovery_coordinator_active)
        self.assertTrue(status.historical_store_active)
        self.assertTrue(status.data_aggregator_active)
        
        integrator.stop()
    
    def test_print_status_no_crash(self):
        """Test print_status doesn't crash"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        integrator.start()
        
        # Should not crash
        integrator.print_status()
        
        integrator.stop()
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown"""
        integrator = MonitoringSystemIntegrator(self.config)
        integrator.initialize()
        integrator.start()
        
        time.sleep(0.5)
        
        # Should shutdown without errors
        integrator.stop()
        
        # Should be stopped
        self.assertFalse(integrator.is_running())
    
    def test_custom_config(self):
        """Test custom configuration"""
        custom_config = MonitoringConfig(
            enable_error_reporting=False,
            enable_health_monitoring=True,
            data_retention_days=7
        )
        
        integrator = MonitoringSystemIntegrator(custom_config)
        self.assertEqual(integrator.config.data_retention_days, 7)
    
    def test_data_directory_creation(self):
        """Test automatic data directory creation"""
        config = MonitoringConfig(
            historical_db_path=os.path.join(self.temp_dir, 'subdir', 'test.db')
        )
        
        integrator = MonitoringSystemIntegrator(config)
        integrator.initialize()
        
        # Directory should be created
        # (Historical store creates it)


class TestMonitoringConfig(unittest.TestCase):
    """Test MonitoringConfig"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = MonitoringConfig()
        
        self.assertTrue(config.enable_error_reporting)
        self.assertTrue(config.enable_health_monitoring)
        self.assertTrue(config.enable_auto_recovery)
        self.assertTrue(config.enable_historical_data)
        self.assertTrue(config.enable_data_aggregation)
        self.assertEqual(config.data_retention_days, 30)
    
    def test_custom_values(self):
        """Test custom configuration"""
        config = MonitoringConfig(
            enable_error_reporting=False,
            max_error_history=500,
            health_check_interval=10.0,
            data_retention_days=90
        )
        
        self.assertFalse(config.enable_error_reporting)
        self.assertEqual(config.max_error_history, 500)
        self.assertEqual(config.health_check_interval, 10.0)
        self.assertEqual(config.data_retention_days, 90)


if __name__ == '__main__':
    unittest.main(verbosity=2)
