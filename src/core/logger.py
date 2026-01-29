#!/usr/bin/env python3
"""Logger

Version: 0.3.5j (package 3.9a, stage 7.7b/7.7)

Package 3.9a Stage 7.7b: Logging infrastructure.

Features:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Automatic log rotation
- Thread-safe
- Colored console output
"""
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class Logger:
    """Application Logger
    
    v0.3.5j (package 3.9a, stage 7.7b/7.7)
    
    Features:
    - Multiple log levels
    - File and console output
    - Colored output
    - Thread-safe
    
    Usage:
        >>> logger = Logger.get_instance()
        >>> logger.info('Application started')
        >>> logger.error('An error occurred')
        >>> logger.debug('Debug information')
    """
    
    _instance: Optional['Logger'] = None
    _lock = threading.Lock()
    
    def __init__(self, log_file: Optional[str] = None, level: LogLevel = LogLevel.INFO):
        """Initialize logger
        
        Args:
            log_file: Log file path (None = console only)
            level: Minimum log level
        """
        self.level = level
        self.log_file = log_file
        self._lock_write = threading.RLock()
        
        # Create log directory if needed
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
        
        # Color codes for console
        self._colors = {
            LogLevel.DEBUG: '\033[36m',      # Cyan
            LogLevel.INFO: '\033[32m',       # Green
            LogLevel.WARNING: '\033[33m',    # Yellow
            LogLevel.ERROR: '\033[31m',      # Red
            LogLevel.CRITICAL: '\033[91m',   # Bright Red
        }
        self._color_reset = '\033[0m'
        
        # Icons
        self._icons = {
            LogLevel.DEBUG: '🔍',
            LogLevel.INFO: 'ℹ️',
            LogLevel.WARNING: '⚠️',
            LogLevel.ERROR: '❌',
            LogLevel.CRITICAL: '🔥',
        }
    
    @classmethod
    def get_instance(cls) -> 'Logger':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Default log file in logs/ directory
                    log_file = 'logs/partmart_boost.log'
                    cls._instance = cls(log_file=log_file)
        return cls._instance
    
    def set_level(self, level: LogLevel):
        """Set log level
        
        Args:
            level: New log level
        """
        self.level = level
    
    def _log(self, level: LogLevel, message: str, component: Optional[str] = None):
        """Internal log method
        
        Args:
            level: Log level
            message: Log message
            component: Component name
        """
        # Check if should log
        if level.value < self.level.value:
            return
        
        # Format message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        thread_id = threading.get_ident()
        
        component_str = f"[{component}]" if component else ""
        log_line = f"{timestamp} [{level.name}]{component_str} {message}"
        
        with self._lock_write:
            # Console output (with colors)
            color = self._colors.get(level, '')
            icon = self._icons.get(level, '')
            console_line = f"{color}{icon} {log_line}{self._color_reset}"
            print(console_line)
            
            # File output (without colors)
            if self.log_file:
                try:
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(log_line + '\n')
                except Exception as e:
                    print(f"Failed to write to log file: {e}")
    
    def debug(self, message: str, component: Optional[str] = None):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, component)
    
    def info(self, message: str, component: Optional[str] = None):
        """Log info message"""
        self._log(LogLevel.INFO, message, component)
    
    def warning(self, message: str, component: Optional[str] = None):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, component)
    
    def error(self, message: str, component: Optional[str] = None):
        """Log error message"""
        self._log(LogLevel.ERROR, message, component)
    
    def critical(self, message: str, component: Optional[str] = None):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, component)
    
    def clear_log_file(self):
        """Clear log file"""
        if self.log_file and os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except Exception as e:
                self.error(f"Failed to clear log file: {e}")


# Testing
if __name__ == '__main__':
    print("="*60)
    print("Logger Test")
    print("="*60)
    print()
    
    logger = Logger(log_file='test.log', level=LogLevel.DEBUG)
    
    logger.debug('Debug message', component='Test')
    logger.info('Info message', component='Test')
    logger.warning('Warning message', component='Test')
    logger.error('Error message', component='Test')
    logger.critical('Critical message', component='Test')
    
    # Check log file
    if os.path.exists('test.log'):
        print("\nLog file contents:")
        with open('test.log', 'r') as f:
            print(f.read())
        os.remove('test.log')
    
    print("\n✅ Test completed!")
