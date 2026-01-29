#!/usr/bin/env python3
"""Logging Configuration

Version: 0.3.5j (package 3.9a, stage 7.7b.1/7.7)

Package 3.9a Stage 7.7b.1: Logging configuration integration.

Features:
- Default logging configuration
- ConfigManager integration
- Dynamic log level changes
"""
import logging
from typing import Optional

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


class LogConfig:
    """Logging configuration manager
    
    v0.3.5j (package 3.9a, stage 7.7b.1/7.7)
    
    Integrates logger with ConfigManager.
    
    Usage:
        >>> config = ConfigManager('config.json')
        >>> log_config = LogConfig(config)
        >>> logger = log_config.get_logger()
    """
    
    # Log level mapping
    LEVEL_MAP = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    def __init__(self, config_manager=None, log_dir: str = 'logs'):
        """Initialize log config
        
        Args:
            config_manager: ConfigManager instance
            log_dir: Directory for log files
        """
        self.config = config_manager
        self.log_dir = log_dir
        self.logger = None
        
        # Initialize logger
        self._init_logger()
        
        # Subscribe to config changes
        if self.config:
            self.config.subscribe('advanced.log_level', self._on_log_level_change)
    
    def _init_logger(self):
        """Initialize logger with config"""
        if not LOGGER_AVAILABLE:
            print("[LogConfig] Logger not available")
            return
        
        # Get log level from config
        log_level = logging.INFO
        if self.config:
            level_name = self.config.get('advanced.log_level', 'info')
            log_level = self.LEVEL_MAP.get(level_name.lower(), logging.INFO)
        
        # Create logger
        self.logger = AppLogger.get_instance(
            log_dir=self.log_dir,
            log_level=log_level
        )
    
    def _on_log_level_change(self, key: str, value: str):
        """Handle log level change from config
        
        Args:
            key: Config key
            value: New log level name
        """
        if not self.logger:
            return
        
        level = self.LEVEL_MAP.get(value.lower(), logging.INFO)
        self.logger.set_level(level)
    
    def get_logger(self) -> Optional[AppLogger]:
        """Get logger instance
        
        Returns:
            AppLogger instance or None
        """
        return self.logger
    
    def set_level(self, level_name: str):
        """Set log level by name
        
        Args:
            level_name: Level name (debug, info, warning, error, critical)
        """
        if not self.logger:
            return
        
        level = self.LEVEL_MAP.get(level_name.lower(), logging.INFO)
        self.logger.set_level(level)
        
        # Update config if available
        if self.config:
            self.config.set('advanced.log_level', level_name.lower())


# Testing
if __name__ == '__main__' and LOGGER_AVAILABLE:
    print("="*60)
    print("LogConfig Test")
    print("="*60)
    print()
    
    # Create mock config
    class MockConfig:
        def __init__(self):
            self.data = {'advanced.log_level': 'info'}
            self.subscribers = []
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def set(self, key, value):
            self.data[key] = value
        
        def subscribe(self, pattern, callback):
            self.subscribers.append((pattern, callback))
    
    # Create log config
    config = MockConfig()
    log_config = LogConfig(config)
    
    logger = log_config.get_logger()
    
    # Test logging
    logger.info("LogConfig initialized", component="Test")
    
    # Change log level
    log_config.set_level('debug')
    logger.debug("This should now be visible", component="Test")
    
    print()
    print("✅ LogConfig test completed!")
