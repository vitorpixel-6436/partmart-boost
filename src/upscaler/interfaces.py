#!/usr/bin/env python3
"""Upscaler Interfaces

Version: 0.3.5d_package3.3c

Abstract interfaces for upscaling systems:
- IUpscaler: Base interface for all upscalers
- UpscaleQuality: Quality modes enum
- Capabilities and statistics

This module defines the contract that all upscaler
implementations must follow, enabling:
- FSR 4 Super Resolution
- DLSS Super Resolution
- XeSS
- Custom ML-based upscalers
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List
from enum import Enum
import numpy as np
import numpy.typing as npt


class UpscaleQuality(Enum):
    """Upscale quality modes
    
    Attributes:
        NATIVE: No upscaling (1.0x)
        QUALITY: High quality (1.5x)
        BALANCED: Balanced quality/performance (1.7x)
        PERFORMANCE: Speed priority (2.0x)
        ULTRA_PERFORMANCE: Maximum speed (3.0x)
    """
    NATIVE = "native"
    QUALITY = "quality"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    ULTRA_PERFORMANCE = "ultra_performance"


@dataclass
class UpscaleCapabilities:
    """Upscaler capabilities
    
    Attributes:
        min_input_resolution: Minimum input resolution (width, height)
        max_input_resolution: Maximum input resolution
        min_output_resolution: Minimum output resolution
        max_output_resolution: Maximum output resolution
        min_scaling_ratio: Minimum scaling ratio
        max_scaling_ratio: Maximum scaling ratio
        supports_temporal: Temporal anti-aliasing support
        supports_motion_vectors: Motion vector support
        supports_depth: Depth buffer support
        supports_hdr: HDR support
        hardware_accelerated: GPU acceleration
        supported_qualities: List of supported quality modes
    """
    min_input_resolution: Tuple[int, int]
    max_input_resolution: Tuple[int, int]
    min_output_resolution: Tuple[int, int]
    max_output_resolution: Tuple[int, int]
    min_scaling_ratio: float
    max_scaling_ratio: float
    supports_temporal: bool
    supports_motion_vectors: bool
    supports_depth: bool
    supports_hdr: bool
    hardware_accelerated: bool
    supported_qualities: List[UpscaleQuality]


@dataclass
class UpscaleStats:
    """Upscaler performance statistics
    
    Attributes:
        frames_upscaled: Total frames upscaled
        avg_upscale_time: Average time per frame (ms)
        quality_mode: Current quality mode
        input_resolution: Current input resolution
        output_resolution: Current output resolution
        scaling_ratio: Current scaling ratio
        sharpness: Current sharpness level
        gpu_utilization: GPU usage (0-100)
        memory_usage: Memory usage (MB)
        last_error: Last error message (if any)
    """
    frames_upscaled: int
    avg_upscale_time: float
    quality_mode: UpscaleQuality
    input_resolution: Tuple[int, int]
    output_resolution: Tuple[int, int]
    scaling_ratio: float
    sharpness: float
    gpu_utilization: float
    memory_usage: float
    last_error: Optional[str] = None


# ========== EXCEPTIONS ==========

class UpscaleException(Exception):
    """Base exception for upscaler errors"""
    pass


class UpscaleNotAvailableException(UpscaleException):
    """Upscaler not available"""
    pass


class UpscaleInitializationException(UpscaleException):
    """Upscaler initialization failed"""
    pass


# ========== INTERFACE ==========

class IUpscaler(ABC):
    """Abstract interface for upscaling
    
    v0.3.5d_package3.3c - Foundation for Upscaling
    
    This interface defines the contract for all upscaler
    implementations. Concrete implementations might include:
    - AMD FSR 4 Super Resolution
    - NVIDIA DLSS Super Resolution
    - Intel XeSS
    - Custom ML-based upscalers
    
    Usage Pattern:
        1. Check availability: is_available()
        2. Initialize: initialize(display_width, display_height)
        3. Set quality: set_quality(mode)
        4. Upscale frames: upscale(frame)
        5. Monitor performance: get_performance_stats()
    
    Example:
        >>> upscaler = MyUpscaler()
        >>> 
        >>> if upscaler.is_available():
        >>>     upscaler.initialize(1920, 1080)
        >>>     upscaler.set_quality(UpscaleQuality.BALANCED)
        >>>     
        >>>     # Upscale low-res frame to display resolution
        >>>     upscaled = upscaler.upscale(low_res_frame)
    """
    
    @abstractmethod
    def upscale(self,
               frame: npt.NDArray[np.uint8],
               metadata: Optional[Dict] = None) -> npt.NDArray[np.uint8]:
        """Upscale frame to display resolution
        
        Args:
            frame: Input frame (render resolution)
            metadata: Optional metadata (motion vectors, depth, etc.)
        
        Returns:
            Upscaled frame (display resolution)
        
        Raises:
            RuntimeError: If upscaling fails
            ValueError: If frame is invalid
        
        Example:
            >>> upscaled = upscaler.upscale(low_res_frame)
        """
        pass
    
    @abstractmethod
    def set_quality(self, quality: UpscaleQuality) -> bool:
        """Set upscale quality mode
        
        Args:
            quality: Desired quality mode
        
        Returns:
            True if quality was set successfully
        
        Example:
            >>> upscaler.set_quality(UpscaleQuality.QUALITY)
        """
        pass
    
    @abstractmethod
    def set_sharpness(self, sharpness: float) -> bool:
        """Set sharpening strength
        
        Args:
            sharpness: Sharpness level (0.0-1.0)
        
        Returns:
            True if sharpness was set
        
        Example:
            >>> upscaler.set_sharpness(0.7)
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> UpscaleCapabilities:
        """Get upscaler capabilities
        
        Returns:
            Capabilities object
        
        Example:
            >>> caps = upscaler.get_capabilities()
            >>> print(f"Max ratio: {caps.max_scaling_ratio}x")
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if upscaler is available
        
        Returns:
            True if upscaler is ready
        
        Example:
            >>> if upscaler.is_available():
            >>>     # Safe to upscale
            >>>     pass
        """
        pass
    
    @abstractmethod
    def get_performance_stats(self) -> UpscaleStats:
        """Get performance statistics
        
        Returns:
            Performance stats
        
        Example:
            >>> stats = upscaler.get_performance_stats()
            >>> print(f"Avg time: {stats.avg_upscale_time:.2f}ms")
        """
        pass
    
    # Optional methods
    
    def initialize(self,
                  display_width: int,
                  display_height: int,
                  quality: UpscaleQuality = UpscaleQuality.BALANCED) -> bool:
        """Initialize upscaler
        
        Args:
            display_width: Target display width
            display_height: Target display height
            quality: Initial quality mode
        
        Returns:
            True if initialization succeeded
        
        Example:
            >>> upscaler.initialize(1920, 1080, UpscaleQuality.QUALITY)
        """
        # Default: assume ready
        return True
    
    def shutdown(self):
        """Shutdown and cleanup
        
        Example:
            >>> upscaler.shutdown()
        """
        # Default: nothing to cleanup
        pass
    
    def get_name(self) -> str:
        """Get upscaler name
        
        Returns:
            Human-readable name
        """
        return self.__class__.__name__
    
    def get_version(self) -> str:
        """Get upscaler version
        
        Returns:
            Version string
        """
        return "1.0.0"
    
    def calculate_render_resolution(self,
                                   display_width: int,
                                   display_height: int,
                                   quality: UpscaleQuality) -> Tuple[int, int]:
        """Calculate render resolution for given quality
        
        Args:
            display_width: Display width
            display_height: Display height
            quality: Quality mode
        
        Returns:
            (render_width, render_height)
        
        Example:
            >>> render_res = upscaler.calculate_render_resolution(1920, 1080, UpscaleQuality.QUALITY)
        """
        # Default ratios
        ratios = {
            UpscaleQuality.NATIVE: 1.0,
            UpscaleQuality.QUALITY: 1.5,
            UpscaleQuality.BALANCED: 1.7,
            UpscaleQuality.PERFORMANCE: 2.0,
            UpscaleQuality.ULTRA_PERFORMANCE: 3.0,
        }
        
        ratio = ratios.get(quality, 1.7)
        render_width = int(display_width / ratio)
        render_height = int(display_height / ratio)
        
        # Ensure even dimensions
        render_width = (render_width // 2) * 2
        render_height = (render_height // 2) * 2
        
        return (render_width, render_height)


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("IUpscaler v0.3.5d_package3.3c Test")
    print("="*60)
    
    print("\n[Test 1] Quality modes")
    for quality in UpscaleQuality:
        print(f"  - {quality.value}")
    
    print("\n[Test 2] Capabilities structure")
    caps = UpscaleCapabilities(
        min_input_resolution=(640, 480),
        max_input_resolution=(7680, 4320),
        min_output_resolution=(1280, 720),
        max_output_resolution=(7680, 4320),
        min_scaling_ratio=1.0,
        max_scaling_ratio=3.0,
        supports_temporal=True,
        supports_motion_vectors=True,
        supports_depth=True,
        supports_hdr=True,
        hardware_accelerated=True,
        supported_qualities=list(UpscaleQuality)
    )
    print(f"  Input resolution: {caps.min_input_resolution} - {caps.max_input_resolution}")
    print(f"  Scaling ratio: {caps.min_scaling_ratio}x - {caps.max_scaling_ratio}x")
    print(f"  Temporal: {caps.supports_temporal}")
    print(f"  Hardware accelerated: {caps.hardware_accelerated}")
    
    print("\n[Test 3] Stats structure")
    stats = UpscaleStats(
        frames_upscaled=1000,
        avg_upscale_time=5.2,
        quality_mode=UpscaleQuality.BALANCED,
        input_resolution=(1280, 720),
        output_resolution=(1920, 1080),
        scaling_ratio=1.7,
        sharpness=0.5,
        gpu_utilization=38.5,
        memory_usage=256.0,
    )
    print(f"  Frames: {stats.frames_upscaled}")
    print(f"  Avg time: {stats.avg_upscale_time:.2f}ms")
    print(f"  {stats.input_resolution} → {stats.output_resolution} ({stats.scaling_ratio:.1f}x)")
    
    print("\n" + "="*60)
    print("✅ IUpscaler - All Tests Passed!")
    print("="*60)
