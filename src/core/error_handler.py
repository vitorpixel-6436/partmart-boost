"""Error handling and graceful degradation for PartMart Boost"""
import sys
import traceback
from typing import Optional, Callable, Any
from functools import wraps

try:
    from core.logger import get_logger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

class ErrorHandler:
    """Centralized error handling with graceful degradation"""
    
    def __init__(self):
        self.logger = get_logger() if LOGGER_AVAILABLE else None
        self.error_count = 0
        self.max_errors = 100  # Prevent error spam
    
    def handle_error(self, error: Exception, context: str = "", critical: bool = False) -> None:
        """Handle error with logging and optional user notification"""
        self.error_count += 1
        
        error_msg = f"{context}: {str(error)}" if context else str(error)
        
        # Log error
        if self.logger:
            if critical:
                self.logger.critical(error_msg, exc_info=True)
            else:
                self.logger.error(error_msg, exc_info=True)
        else:
            # Fallback to console
            print(f"ERROR: {error_msg}", file=sys.stderr)
            if critical:
                traceback.print_exc()
        
        # Check if we're getting too many errors
        if self.error_count > self.max_errors:
            if self.logger:
                self.logger.critical("Too many errors, application may be unstable")
    
    def safe_call(self, func: Callable, *args, fallback=None, context: str = "", **kwargs) -> Any:
        """Call function safely with fallback on error"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, context=context or func.__name__)
            return fallback
    
    def reset_error_count(self):
        """Reset error counter"""
        self.error_count = 0

def safe_call(fallback=None, context: str = "", critical: bool = False):
    """Decorator for safe function calls with graceful degradation"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or func.__name__
                
                # Log error
                if LOGGER_AVAILABLE:
                    logger = get_logger()
                    if critical:
                        logger.critical(f"{error_context}: {str(e)}", exc_info=True)
                    else:
                        logger.error(f"{error_context}: {str(e)}", exc_info=True)
                else:
                    print(f"ERROR in {error_context}: {str(e)}", file=sys.stderr)
                
                return fallback
        return wrapper
    return decorator

def safe_property(fallback=None):
    """Decorator for safe property access"""
    def decorator(func: Callable) -> property:
        @wraps(func)
        def wrapper(self):
            try:
                return func(self)
            except Exception as e:
                if LOGGER_AVAILABLE:
                    logger = get_logger()
                    logger.warning(f"Property {func.__name__} failed: {str(e)}")
                return fallback
        return property(wrapper)
    return decorator

class SafeDict(dict):
    """Dictionary with safe access (returns None instead of KeyError)"""
    
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return None
    
    def get_safe(self, key, default=None, type_cast=None):
        """Get value with optional type casting"""
        try:
            value = self.get(key, default)
            if type_cast and value is not None:
                return type_cast(value)
            return value
        except (ValueError, TypeError):
            return default

class HardwareNotFoundError(Exception):
    """Raised when hardware component is not found"""
    pass

class GPUNotFoundError(HardwareNotFoundError):
    """Raised when GPU is not found"""
    pass

class CPUTempUnavailableError(HardwareNotFoundError):
    """Raised when CPU temperature is unavailable"""
    pass

class RAMInfoUnavailableError(HardwareNotFoundError):
    """Raised when RAM info is unavailable"""
    pass

# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def init_error_handler() -> ErrorHandler:
    """Initialize global error handler"""
    global _error_handler
    _error_handler = ErrorHandler()
    return _error_handler

if __name__ == "__main__":
    # Test error handler
    print("Testing Error Handler...")
    
    handler = ErrorHandler()
    
    # Test safe_call
    def risky_function():
        raise ValueError("Something went wrong!")
    
    result = handler.safe_call(risky_function, fallback="Default value", context="Test")
    print(f"Result with fallback: {result}")
    
    # Test decorator
    @safe_call(fallback=0, context="Division")
    def divide(a, b):
        return a / b
    
    print(f"5 / 2 = {divide(5, 2)}")
    print(f"5 / 0 = {divide(5, 0)}  (should return 0)")
    
    # Test SafeDict
    data = SafeDict({
        'temperature': '75',
        'load': 50,
    })
    
    print(f"Temperature: {data.get_safe('temperature', type_cast=float)}")
    print(f"Load: {data.get_safe('load')}")
    print(f"Missing key: {data.get_safe('nonexistent', default='N/A')}")
    
    # Test custom exceptions
    try:
        raise GPUNotFoundError("No NVIDIA GPU detected")
    except GPUNotFoundError as e:
        print(f"Caught GPUNotFoundError: {e}")
    
    print("\n✅ Error Handler test complete!")
