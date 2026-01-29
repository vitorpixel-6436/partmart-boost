#!/usr/bin/env python3
"""Tests for ConfigManager

Version: 0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)
"""
import unittest
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.config_manager import (
    ConfigManager,
    ApplicationConfig,
    MonitoringConfig,
    HistoricalDataConfig,
    VisualizationConfig,
    UIConfig
)


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary config file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='.json'
        )
        self.config_path = self.temp_file.name
        self.temp_file.close()
        
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
    
    def test_initialization(self):
        """Test config manager initialization"""
        self.assertIsNotNone(self.config_manager)
        self.assertIsInstance(self.config_manager.config, ApplicationConfig)
    
    def test_default_config(self):
        """Test default configuration values"""
        config = self.config_manager.load()
        
        self.assertEqual(config.version, "0.3.5g")
        self.assertEqual(config.package, "3.9a")
        self.assertIsInstance(config.monitoring, MonitoringConfig)
        self.assertIsInstance(config.historical_data, HistoricalDataConfig)
        self.assertIsInstance(config.visualization, VisualizationConfig)
        self.assertIsInstance(config.ui, UIConfig)
    
    def test_monitoring_config_defaults(self):
        """Test monitoring config defaults"""
        config = self.config_manager.load()
        
        self.assertEqual(config.monitoring.check_interval, 5.0)
        self.assertTrue(config.monitoring.enable_performance_monitoring)
        self.assertTrue(config.monitoring.enable_auto_recovery)
    
    def test_historical_data_config_defaults(self):
        """Test historical data config defaults"""
        config = self.config_manager.load()
        
        self.assertTrue(config.historical_data.enabled)
        self.assertEqual(config.historical_data.retention_days, 30)
        self.assertEqual(config.historical_data.collection_interval, 60.0)
    
    def test_ui_config_defaults(self):
        """Test UI config defaults"""
        config = self.config_manager.load()
        
        self.assertEqual(config.ui.window_width, 1200)
        self.assertEqual(config.ui.window_height, 800)
        self.assertEqual(config.ui.theme, "light")
    
    def test_save_and_load(self):
        """Test saving and loading configuration"""
        # Modify config
        self.config_manager.set('monitoring.check_interval', 10.0)
        self.config_manager.set('ui.window_width', 1600)
        
        # Save
        self.assertTrue(self.config_manager.save())
        
        # Load in new manager
        new_manager = ConfigManager(self.config_path)
        config = new_manager.load()
        
        self.assertEqual(config.monitoring.check_interval, 10.0)
        self.assertEqual(config.ui.window_width, 1600)
    
    def test_get_value(self):
        """Test getting configuration values"""
        config = self.config_manager.load()
        
        # Get nested values
        check_interval = self.config_manager.get('monitoring.check_interval')
        self.assertEqual(check_interval, 5.0)
        
        window_width = self.config_manager.get('ui.window_width')
        self.assertEqual(window_width, 1200)
        
        # Get with default
        unknown = self.config_manager.get('unknown.key', 'default')
        self.assertEqual(unknown, 'default')
    
    def test_set_value(self):
        """Test setting configuration values"""
        # Set values
        self.assertTrue(self.config_manager.set('monitoring.check_interval', 15.0))
        self.assertTrue(self.config_manager.set('ui.theme', 'dark'))
        
        # Verify
        self.assertEqual(
            self.config_manager.get('monitoring.check_interval'),
            15.0
        )
        self.assertEqual(self.config_manager.get('ui.theme'), 'dark')
        
        # Try to set invalid key
        self.assertFalse(self.config_manager.set('invalid.key', 'value'))
    
    def test_reset_to_defaults(self):
        """Test resetting to default configuration"""
        # Modify config
        self.config_manager.set('monitoring.check_interval', 20.0)
        
        # Reset
        self.config_manager.reset_to_defaults()
        
        # Verify defaults restored
        self.assertEqual(
            self.config_manager.config.monitoring.check_interval,
            5.0
        )
    
    def test_get_config_dict(self):
        """Test getting configuration as dictionary"""
        config_dict = self.config_manager.get_config_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('version', config_dict)
        self.assertIn('monitoring', config_dict)
        self.assertIn('historical_data', config_dict)
        self.assertIn('ui', config_dict)
    
    def test_visualization_config_defaults(self):
        """Test visualization config defaults"""
        config = self.config_manager.load()
        
        self.assertTrue(config.visualization.enabled)
        self.assertEqual(config.visualization.default_time_range, "Last 24 Hours")
        self.assertTrue(config.visualization.auto_refresh)
        self.assertIsInstance(config.visualization.chart_colors, list)


class TestDataClasses(unittest.TestCase):
    """Test configuration data classes"""
    
    def test_monitoring_config(self):
        """Test MonitoringConfig dataclass"""
        config = MonitoringConfig(
            check_interval=10.0,
            enable_auto_recovery=False
        )
        
        self.assertEqual(config.check_interval, 10.0)
        self.assertFalse(config.enable_auto_recovery)
        self.assertEqual(config.error_threshold, 10)  # Default
    
    def test_historical_data_config(self):
        """Test HistoricalDataConfig dataclass"""
        config = HistoricalDataConfig(
            retention_days=60,
            collection_interval=30.0
        )
        
        self.assertEqual(config.retention_days, 60)
        self.assertEqual(config.collection_interval, 30.0)
        self.assertTrue(config.enabled)  # Default
    
    def test_ui_config(self):
        """Test UIConfig dataclass"""
        config = UIConfig(
            window_width=1920,
            window_height=1080,
            theme="dark"
        )
        
        self.assertEqual(config.window_width, 1920)
        self.assertEqual(config.window_height, 1080)
        self.assertEqual(config.theme, "dark")
    
    def test_application_config(self):
        """Test ApplicationConfig dataclass"""
        config = ApplicationConfig()
        
        self.assertEqual(config.version, "0.3.5g")
        self.assertEqual(config.package, "3.9a")
        self.assertIsInstance(config.monitoring, MonitoringConfig)
        self.assertIsInstance(config.historical_data, HistoricalDataConfig)
        self.assertIsInstance(config.visualization, VisualizationConfig)
        self.assertIsInstance(config.ui, UIConfig)


if __name__ == '__main__':
    unittest.main(verbosity=2)
