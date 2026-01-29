#!/usr/bin/env python3
"""Centralized Logger

Version: 0.3.5j (package 3.9a, stage 7.7b.1/7.7)

Package 3.9a Stage 7.7b.1: Logging infrastructure.

Features:
- Singleton logger
- Multiple log levels
- File and console output
- Colored console output
- Log file rotation
- Thread-safe
- Configurable via ConfigManager
"""
import os
import sys
import logging
import threading
from typing import Optional
from datetime import datetime
from logging.handlers import RotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[95m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Add color
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format message
        record.levelname = f"{color}{record.levelname}{reset}"
        record.name = f"\033[94m{record.name}{reset}"  # Blue
        
        return super().format(record)


class AppLogger:
    """Application Logger (Singleton)
    
    v0.3.5j (package 3.9a, stage 7.7b.1/7.7)
    
    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File and console output
    - Colored console output
    - Log file rotation (10MB, 5 backups)
    - Thread-safe
    
    Usage:
        >>> logger = AppLogger.get_instance()
        >>> logger.info('Application started')
        >>> logger.error('An error occurred', exc_info=True)
        >>> logger.debug('Debug info', component='DataBus')
    """
    
    _instance: Optional['AppLogger'] = None
    _lock = threading.Lock()
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, log_dir: str = 'logs', log_level: int = logging.INFO):
        """Initialize logger
        
        Args:
            log_dir: Directory for log files
            log_level: Minimum log level
        """
        self.log_dir = log_dir
        self.log_level = log_level
        
        # Create logs directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger('PartMartBoost')
        self.logger.setLevel(log_level)
        self.logger.handlers = []  # Clear existing handlers
        
        # Console handler with colors
        self._setup_console_handler()
        
        # File handler with rotation
        self._setup_file_handler()
        
        self.logger.info("="*60)
        self.logger.info("Logger initialized")
        self.logger.info(f"Log level: {logging.getLevelName(log_level)}")
        self.logger.info(f"Log directory: {os.path.abspath(log_dir)}")
        self.logger.info("="*60)
    
    def _setup_console_handler(self):
        """Set up console handler with colored output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Use colored formatter for console
        console_format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
        console_formatter = ColoredFormatter(
            console_format,
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Set up rotating file handler"""
        log_file = os.path.join(self.log_dir, 'partmart_boost.log')
        
        # Rotating file handler (10MB per file, 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # Plain formatter for file (no colors)
        file_format = '[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
        file_formatter = logging.Formatter(
            file_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
    
    @classmethod
    def get_instance(cls, log_dir: str = 'logs', log_level: int = logging.INFO) -> 'AppLogger':
        """Get singleton instance
        
        Args:
            log_dir: Directory for log files
            log_level: Minimum log level
        
        Returns:
            AppLogger instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(log_dir, log_level)
        return cls._instance
    
    def set_level(self, level: int):
        """Set log level
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_level = level
        self.logger.setLevel(level)
        
        # Update all handlers
        for handler in self.logger.handlers:
            handler.setLevel(level)
        
        self.logger.info(f"Log level changed to: {logging.getLevelName(level)}")
    
    def debug(self, message: str, component: Optional[str] = None, **kwargs):
        """Log debug message
        
        Args:
            message: Log message
            component: Component name
            **kwargs: Additional logging arguments
        """
        if component:
            message = f"[{component}] {message}"
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, component: Optional[str] = None, **kwargs):
        """Log info message
        
        Args:
            message: Log message
            component: Component name
            **kwargs: Additional logging arguments
        """
        if component:
            message = f"[{component}] {message}"
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, component: Optional[str] = None, **kwargs):
        """Log warning message
        
        Args:
            message: Log message
            component: Component name
            **kwargs: Additional logging arguments
        """
        if component:
            message = f"[{component}] {message}"
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, component: Optional[str] = None, exc_info: bool = False, **kwargs):
        """Log error message
        
        Args:
            message: Log message
            component: Component name
            exc_info: Include exception info
            **kwargs: Additional logging arguments
        """
        if component:
            message = f"[{component}] {message}"
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, component: Optional[str] = None, exc_info: bool = False, **kwargs):
        """Log critical message
        
        Args:
            message: Log message
            component: Component name
            exc_info: Include exception info
            **kwargs: Additional logging arguments
        """
        if component:
            message = f"[{component}] {message}"
        self.logger.critical(message, exc_info=exc_info, **kwargs)
    
    def exception(self, message: str, component: Optional[str] = None, **kwargs):
        """Log exception (automatically includes traceback)
        
        Args:
            message: Log message
            component: Component name
            **kwargs: Additional logging arguments
        """
        if component:
            message = f"[{component}] {message}"
        self.logger.exception(message, **kwargs)
    
    def get_log_file_path(self) -> str:
        """Get path to current log file
        
        Returns:
            Absolute path to log file
        """
        return os.path.abspath(os.path.join(self.log_dir, 'partmart_boost.log'))
    
    def get_log_files(self) -> list:
        """Get list of all log files
        
        Returns:
            List of log file paths
        """
        if not os.path.exists(self.log_dir):
            return []
        
        log_files = []
        for filename in os.listdir(self.log_dir):
            if filename.startswith('partmart_boost') and filename.endswith('.log'):
                log_files.append(os.path.join(self.log_dir, filename))
        
        return sorted(log_files)


# Convenience functions for quick logging
_logger_instance = None

def get_logger() -> AppLogger:
    """Get logger instance
    
    Returns:
        AppLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AppLogger.get_instance()
    return _logger_instance


def debug(message: str, component: Optional[str] = None, **kwargs):
    """Quick debug log"""
    get_logger().debug(message, component, **kwargs)


def info(message: str, component: Optional[str] = None, **kwargs):
    """Quick info log"""
    get_logger().info(message, component, **kwargs)


def warning(message: str, component: Optional[str] = None, **kwargs):
    """Quick warning log"""
    get_logger().warning(message, component, **kwargs)


def error(message: str, component: Optional[str] = None, exc_info: bool = False, **kwargs):
    """Quick error log"""
    get_logger().error(message, component, exc_info, **kwargs)


def critical(message: str, component: Optional[str] = None, exc_info: bool = False, **kwargs):
    """Quick critical log"""
    get_logger().critical(message, component, exc_info, **kwargs)


def exception(message: str, component: Optional[str] = None, **kwargs):
    """Quick exception log"""
    get_logger().exception(message, component, **kwargs)


# Testing
if __name__ == '__main__':
    print("="*60)
    print("Logger Test")
    print("="*60)
    print()
    
    # Create logger
    logger = AppLogger.get_instance(log_level=logging.DEBUG)
    
    # Test all levels
    logger.debug("This is a debug message", component="Test")
    logger.info("This is an info message", component="Test")
    logger.warning("This is a warning message", component="Test")
    logger.error("This is an error message", component="Test")
    logger.critical("This is a critical message", component="Test")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("Exception caught", component="Test")
    
    print()
    print(f"Log file: {logger.get_log_file_path()}")
    print()
    print("✅ Logger test completed!")
