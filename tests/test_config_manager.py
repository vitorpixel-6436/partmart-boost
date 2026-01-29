#!/usr/bin/env python3
"""ConfigManager Unit Tests

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)
"""
import sys
import os
import unittest
import tempfile
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from config_manager import ConfigManager, ConfigSchema


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.config = ConfigManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_get_default_value(self):
        """Test getting default values"""
        theme = self.config.get('ui.theme')
        self.assertEqual(theme, 'dark')
        
        interval = self.config.get('monitor.interval_ms')
        self.assertEqual(interval, 100)
    
    def test_get_with_fallback(self):
        """Test getting non-existent key with fallback"""
        value = self.config.get('nonexistent.key', 'fallback')
        self.assertEqual(value, 'fallback')
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        self.config.set('ui.theme', 'light')
        theme = self.config.get('ui.theme')
        self.assertEqual(theme, 'light')
    
    def test_validation_type_error(self):
        """Test type validation"""
        result = self.config.set('ui.theme', 123)  # Should be str
        self.assertFalse(result)
        
        # Value should not change
        theme = self.config.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_validation_choice_error(self):
        """Test choice validation"""
        result = self.config.set('ui.theme', 'red')  # Not in choices
        self.assertFalse(result)
    
    def test_validation_range_error(self):
        """Test range validation"""
        result = self.config.set('monitor.interval_ms', 10000)  # Exceeds max
        self.assertFalse(result)
        
        result = self.config.set('monitor.interval_ms', 5)  # Below min
        self.assertFalse(result)
    
    def test_validation_success(self):
        """Test successful validation"""
        result = self.config.set('monitor.interval_ms', 200)
        self.assertTrue(result)
        
        interval = self.config.get('monitor.interval_ms')
        self.assertEqual(interval, 200)
    
    def test_get_section(self):
        """Test getting config section"""
        ui_config = self.config.get_section('ui')
        
        self.assertIn('ui.theme', ui_config)
        self.assertIn('ui.language', ui_config)
        self.assertIn('ui.show_fps', ui_config)
    
    def test_get_all_keys(self):
        """Test getting all keys"""
        keys = self.config.get_all_keys()
        
        self.assertIsInstance(keys, list)
        self.assertIn('ui.theme', keys)
        self.assertIn('monitor.interval_ms', keys)
    
    def test_subscribe(self):
        """Test subscription to changes"""
        callback_called = []
        
        def on_change(key, value):
            callback_called.append((key, value))
        
        self.config.subscribe('ui.theme', on_change)
        self.config.set('ui.theme', 'light')
        
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], ('ui.theme', 'light'))
    
    def test_subscribe_wildcard(self):
        """Test wildcard subscription"""
        callback_called = []
        
        def on_change(key, value):
            callback_called.append(key)
        
        self.config.subscribe('ui.*', on_change)
        
        self.config.set('ui.theme', 'light')
        self.config.set('ui.language', 'ru')
        self.config.set('monitor.interval_ms', 200)  # Should not trigger
        
        self.assertEqual(len(callback_called), 2)
        self.assertIn('ui.theme', callback_called)
        self.assertIn('ui.language', callback_called)
        self.assertNotIn('monitor.interval_ms', callback_called)
    
    def test_save_and_load(self):
        """Test saving and loading config"""
        # Set some values
        self.config.set('ui.theme', 'light')
        self.config.set('monitor.interval_ms', 200)
        
        # Save
        self.config.save()
        
        # Create new config and load
        config2 = ConfigManager(self.temp_file.name)
        
        # Check values
        self.assertEqual(config2.get('ui.theme'), 'light')
        self.assertEqual(config2.get('monitor.interval_ms'), 200)
    
    def test_reset_single_key(self):
        """Test resetting single key"""
        self.config.set('ui.theme', 'light')
        self.assertEqual(self.config.get('ui.theme'), 'light')
        
        self.config.reset('ui.theme')
        self.assertEqual(self.config.get('ui.theme'), 'dark')
    
    def test_reset_all(self):
        """Test resetting all config"""
        self.config.set('ui.theme', 'light')
        self.config.set('monitor.interval_ms', 200)
        
        self.config.reset()
        
        self.assertEqual(self.config.get('ui.theme'), 'dark')
        self.assertEqual(self.config.get('monitor.interval_ms'), 100)
    
    def test_to_dict(self):
        """Test exporting to dictionary"""
        config_dict = self.config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('ui', config_dict)
        self.assertIn('monitor', config_dict)
    
    def test_get_schema(self):
        """Test getting schema"""
        schema = self.config.get_schema('ui.theme')
        
        self.assertIsInstance(schema, ConfigSchema)
        self.assertEqual(schema.type, str)
        self.assertEqual(schema.default, 'dark')


if __name__ == '__main__':
    unittest.main()
