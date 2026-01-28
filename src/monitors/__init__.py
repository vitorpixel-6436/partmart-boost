"""Hardware monitoring modules for PartMart Boost"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseMonitor(ABC):
    """Base class for all hardware monitors"""
    
    def __init__(self):
        self.available = False
        self.last_error: Optional[str] = None
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> bool:
        """Initialize monitor (detect hardware, load libraries)
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
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
    
    def is_available(self) -> bool:
        """Check if monitor is available"""
        return self.available
    
    def get_last_error(self) -> Optional[str]:
        """Get last error message"""
        return self.last_error
    
    def _set_error(self, error: str):
        """Set error message and mark unavailable"""
        self.last_error = error
        self.available = False

# Export monitors
__all__ = ['BaseMonitor']
