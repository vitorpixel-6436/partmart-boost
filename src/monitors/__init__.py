"""Hardware monitoring modules for PartMart Boost
Optimized monitors with <10ms latency
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseMonitor(ABC):
    """Base class for all hardware monitors"""
    
    def __init__(self):
        self.available = False
        self.last_error: Optional[str] = None
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Get current hardware data
        
        Returns:
            Dict with hardware metrics or empty dict if unavailable
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get hardware name/identifier"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if monitor is available"""
        pass
    
    def get_last_error(self) -> Optional[str]:
        """Get last error message"""
        return self.last_error
    
    def _set_error(self, error: str):
        """Set error message and mark unavailable"""
        self.last_error = error
        self.available = False


# FIX: Don't import here to avoid circular imports
# Import monitors only when needed (lazy loading)
__all__ = [
    'BaseMonitor',
]
