#!/usr/bin/env python3
"""Error Handling Unit Tests

Version: 0.3.5k (package 3.9a, stage 7.7b.2/7.7)
"""
import sys
import os
import unittest
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from config_manager import ConfigManager


class TestConfigManagerErrorHandling(unittest.TestCase):
    """Test ConfigManager error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, 'test_config.json')
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_nonexistent_file(self):
        """Test loading nonexistent file uses defaults"""
        config = ConfigManager('nonexistent_file.json')
        
        # Should have default values
        theme = config.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_invalid_json(self):
        """Test handling invalid JSON"""
        # Create invalid JSON file
        with open(self.temp_file, 'w') as f:
            f.write('{invalid json}')
        
        config = ConfigManager(self.temp_file)
        
        # Should fall back to defaults
        theme = config.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_invalid_type(self):
        """Test rejecting invalid types"""
        config = ConfigManager()
        
        # Try to set string to int field
        result = config.set('monitor.interval_ms', 'invalid')
        
        self.assertFalse(result)
        
        # Value should not change
        interval = config.get('monitor.interval_ms')
        self.assertEqual(interval, 100)
    
    def test_invalid_choice(self):
        """Test rejecting invalid choices"""
        config = ConfigManager()
        
        # Try to set invalid theme
        result = config.set('ui.theme', 'invalid_theme')
        
        self.assertFalse(result)
        
        # Value should not change
        theme = config.get('ui.theme')
        self.assertEqual(theme, 'dark')
    
    def test_invalid_range(self):
        """Test rejecting out-of-range values"""
        config = ConfigManager()
        
        # Try to set too high interval
        result = config.set('monitor.interval_ms', 10000)
        
        self.assertFalse(result)
        
        # Try to set too low interval
        result = config.set('monitor.interval_ms', 5)
        
        self.assertFalse(result)
        
        # Value should not change
        interval = config.get('monitor.interval_ms')
        self.assertEqual(interval, 100)
    
    def test_save_permission_denied(self):
        """Test handling permission errors on save"""
        # Create read-only directory
        readonly_dir = os.path.join(self.temp_dir, 'readonly')
        os.makedirs(readonly_dir)
        os.chmod(readonly_dir, 0o444)
        
        config = ConfigManager()
        readonly_file = os.path.join(readonly_dir, 'config.json')
        
        # Should return False and not crash
        result = config.save(readonly_file)
        
        self.assertFalse(result)
        
        # Cleanup
        os.chmod(readonly_dir, 0o755)
    
    def test_callback_exception_isolation(self):
        """Test that callback exceptions don't break other callbacks"""
        config = ConfigManager()
        
        received = []
        
        def bad_callback(key, value):
            raise Exception("Bad callback!")
        
        def good_callback(key, value):
            received.append((key, value))
        
        # Subscribe both
        config.subscribe('ui.*', bad_callback)
        config.subscribe('ui.*', good_callback)
        
        # Change value
        config.set('ui.theme', 'light')
        
        # Good callback should still have received
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0][0], 'ui.theme')
        self.assertEqual(received[0][1], 'light')
    
    def test_get_with_missing_key(self):
        """Test getting missing key returns default"""
        config = ConfigManager()
        
        value = config.get('nonexistent.key', 'fallback')
        
        self.assertEqual(value, 'fallback')
    
    def test_empty_key(self):
        """Test handling empty key"""
        config = ConfigManager()
        
        value = config.get('', 'default')
        
        self.assertEqual(value, 'default')
    
    def test_corrupted_config_recovery(self):
        """Test recovery from corrupted config"""
        config = ConfigManager(self.temp_file)
        
        # Save valid config
        config.set('ui.theme', 'light')
        config.save()
        
        # Corrupt the file
        with open(self.temp_file, 'w') as f:
            f.write('corrupted')
        
        # Load should fail but not crash
        result = config.load()
        
        self.assertFalse(result)
        
        # Should still have old values
        theme = config.get('ui.theme')
        self.assertEqual(theme, 'light')


if __name__ == '__main__':
    unittest.main()
