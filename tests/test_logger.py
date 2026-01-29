#!/usr/bin/env python3
"""Logger Unit Tests

Version: 0.3.5j (package 3.9a, stage 7.7b.1/7.7)
"""
import sys
import os
import unittest
import tempfile
import logging
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from logger import AppLogger


class TestAppLogger(unittest.TestCase):
    """Test AppLogger functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary log directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Reset singleton
        AppLogger._instance = None
        
        # Create logger
        self.logger = AppLogger.get_instance(
            log_dir=self.temp_dir,
            log_level=logging.DEBUG
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Reset singleton
        AppLogger._instance = None
    
    def test_singleton(self):
        """Test singleton pattern"""
        logger1 = AppLogger.get_instance()
        logger2 = AppLogger.get_instance()
        
        self.assertIs(logger1, logger2)
    
    def test_log_directory_created(self):
        """Test that log directory is created"""
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_log_file_created(self):
        """Test that log file is created"""
        self.logger.info("Test message")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        self.assertTrue(os.path.exists(log_file))
    
    def test_debug_logging(self):
        """Test debug level logging"""
        self.logger.debug("Debug message")
        
        # Check log file contains message
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('Debug message', content)
        self.assertIn('DEBUG', content)
    
    def test_info_logging(self):
        """Test info level logging"""
        self.logger.info("Info message")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('Info message', content)
        self.assertIn('INFO', content)
    
    def test_warning_logging(self):
        """Test warning level logging"""
        self.logger.warning("Warning message")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('Warning message', content)
        self.assertIn('WARNING', content)
    
    def test_error_logging(self):
        """Test error level logging"""
        self.logger.error("Error message")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('Error message', content)
        self.assertIn('ERROR', content)
    
    def test_critical_logging(self):
        """Test critical level logging"""
        self.logger.critical("Critical message")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('Critical message', content)
        self.assertIn('CRITICAL', content)
    
    def test_exception_logging(self):
        """Test exception logging"""
        try:
            raise ValueError("Test exception")
        except ValueError:
            self.logger.exception("Exception caught")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('Exception caught', content)
        self.assertIn('ValueError', content)
        self.assertIn('Test exception', content)
    
    def test_component_logging(self):
        """Test logging with component name"""
        self.logger.info("Test message", component="TestComponent")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertIn('[TestComponent]', content)
    
    def test_set_level(self):
        """Test changing log level"""
        # Set to WARNING
        self.logger.set_level(logging.WARNING)
        
        # Debug and info should not appear
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        
        log_file = os.path.join(self.temp_dir, 'partmart_boost.log')
        with open(log_file, 'r') as f:
            content = f.read()
        
        self.assertNotIn('Debug message', content)
        self.assertNotIn('Info message', content)
        self.assertIn('Warning message', content)
    
    def test_get_log_file_path(self):
        """Test getting log file path"""
        path = self.logger.get_log_file_path()
        
        self.assertTrue(os.path.isabs(path))
        self.assertTrue(path.endswith('partmart_boost.log'))
    
    def test_get_log_files(self):
        """Test getting list of log files"""
        # Create some logs
        self.logger.info("Test message")
        
        log_files = self.logger.get_log_files()
        
        self.assertGreater(len(log_files), 0)
        self.assertTrue(any('partmart_boost.log' in f for f in log_files))


if __name__ == '__main__':
    unittest.main()
