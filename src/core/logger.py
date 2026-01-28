"""Logging system for PartMart Boost"""
import logging
import os
from datetime import datetime
from pathlib import Path

class PartMartLogger:
    """Centralized logging for application"""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, "partmart.log")
        self._ensure_log_dir()
        self._setup_logger(log_level)
    
    def _ensure_log_dir(self):
        """Create logs directory if it doesn't exist"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _setup_logger(self, log_level: str):
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger("PartMartBoost")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler (optional - for development)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info=False):
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info)
    
    def log_startup(self, version: str):
        """Log application startup"""
        self.info("="*60)
        self.info(f"PartMart Boost {version} started")
        self.info(f"Python: {self._get_python_version()}")
        self.info(f"OS: {self._get_os_info()}")
        self.info("="*60)
    
    def log_shutdown(self):
        """Log application shutdown"""
        self.info("PartMart Boost shutting down")
        self.info("="*60)
    
    def log_optimization(self, opt_type: str, success: bool, details: str = ""):
        """Log optimization attempt"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Optimization [{opt_type}]: {status}"
        if details:
            message += f" - {details}"
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_gpu_info(self, gpu_name: str, temp: float, load: float):
        """Log GPU information"""
        self.info(f"GPU detected: {gpu_name} | Temp: {temp}°C | Load: {load}%")
    
    def log_error_with_trace(self, message: str, exception: Exception):
        """Log error with full traceback"""
        self.error(f"{message}: {str(exception)}", exc_info=True)
    
    def _get_python_version(self) -> str:
        """Get Python version string"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_os_info(self) -> str:
        """Get OS information"""
        import platform
        return f"{platform.system()} {platform.release()} ({platform.machine()})"
    
    def rotate_logs(self, max_size_mb: int = 10):
        """Rotate log file if it exceeds max size"""
        if not os.path.exists(self.log_file):
            return
        
        file_size_mb = os.path.getsize(self.log_file) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            # Rename current log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.log_dir, f"partmart_{timestamp}.log")
            os.rename(self.log_file, backup_file)
            self.info(f"Log rotated: {backup_file}")
            
            # Keep only last 5 backups
            self._cleanup_old_logs(5)
    
    def _cleanup_old_logs(self, keep_count: int):
        """Remove old log backups"""
        log_files = sorted(
            [f for f in os.listdir(self.log_dir) if f.startswith("partmart_") and f.endswith(".log")],
            reverse=True
        )
        for old_log in log_files[keep_count:]:
            try:
                os.remove(os.path.join(self.log_dir, old_log))
            except:
                pass

# Global logger instance
_logger = None

def get_logger() -> PartMartLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = PartMartLogger()
    return _logger

def init_logger(log_dir: str = "logs", log_level: str = "INFO") -> PartMartLogger:
    """Initialize global logger"""
    global _logger
    _logger = PartMartLogger(log_dir, log_level)
    return _logger

if __name__ == "__main__":
    # Test
    logger = PartMartLogger("test_logs")
    logger.log_startup("0.3.4-alpha")
    logger.info("Test info message")
    logger.warning("Test warning")
    logger.error("Test error")
    logger.log_gpu_info("NVIDIA GeForce RTX 3060", 52.0, 38.5)
    logger.log_optimization("quick_boost", True, "Temp reduced by 4°C")
    logger.log_shutdown()
    
    # Cleanup
    import shutil
    if os.path.exists("test_logs"):
        shutil.rmtree("test_logs")
