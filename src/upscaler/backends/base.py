#!/usr/bin/env python3
"""Base Backend Interface

Version: 0.3.5d (package 3.7a)
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy.typing as npt

from ..types import (
    UpscaleConfig,
    FrameData,
    UpscaleMetrics,
    BackendInfo,
    UpscalerBackend
)


class BaseBackend(ABC):
    """Abstract base class for upscaler backends
    
    All backends (FSR3, XeSS, Software) must implement this interface.
    """
    
    def __init__(self):
        """Initialize backend"""
        self._initialized = False
        self._context = None
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize backend
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown backend and cleanup resources
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on this system
        
        Returns:
            True if backend can be used, False otherwise
        """
        pass
    
    @abstractmethod
    def get_info(self) -> BackendInfo:
        """Get backend information
        
        Returns:
            Backend info including version, features, etc.
        """
        pass
    
    @abstractmethod
    def create_context(self, config: UpscaleConfig) -> bool:
        """Create upscaling context
        
        Args:
            config: Upscale configuration
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def upscale(self, frame: FrameData) -> Tuple[npt.NDArray, UpscaleMetrics]:
        """Upscale frame
        
        Args:
            frame: Input frame data
        
        Returns:
            Tuple of (upscaled_frame, metrics)
        """
        pass
    
    @abstractmethod
    def generate_frame(
        self,
        prev_frame: FrameData,
        next_frame: FrameData,
        t: float = 0.5
    ) -> Tuple[npt.NDArray, UpscaleMetrics]:
        """Generate intermediate frame
        
        Args:
            prev_frame: Previous frame
            next_frame: Next frame
            t: Interpolation factor (0.0-1.0)
        
        Returns:
            Tuple of (generated_frame, metrics)
        """
        pass
    
    def is_initialized(self) -> bool:
        """Check if backend is initialized"""
        return self._initialized
    
    @abstractmethod
    def get_backend_type(self) -> UpscalerBackend:
        """Get backend type
        
        Returns:
            Backend enum value
        """
        pass
