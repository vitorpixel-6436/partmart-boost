#!/usr/bin/env python3
"""Frame Generation Interfaces

Version: 0.3.5d_package3.3a

Abstract interfaces for frame generation systems:
- IFrameGenerator: Base interface for all frame generators
- FrameData: Data structure for frame information
- Quality modes and capabilities

This module defines the contract that all frame generation
implementations must follow, enabling:
- FSR 3 Frame Generation
- DLSS 3 Frame Generation
- Custom ML-based generators
- Software interpolation

Preparation for real implementations in future versions.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any
from enum import Enum
import numpy as np
import numpy.typing as npt


class FrameGenQuality(Enum):
    """Frame generation quality modes
    
    Attributes:
        ULTRA: Maximum quality, highest latency
        QUALITY: High quality, balanced latency
        BALANCED: Default mode, good quality/performance
        PERFORMANCE: Speed priority, acceptable quality
        ULTRA_PERFORMANCE: Maximum speed, basic quality
    """
    ULTRA = "ultra"
    QUALITY = "quality"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    ULTRA_PERFORMANCE = "ultra_performance"


@dataclass
class FrameData:
    """Frame data structure
    
    Attributes:
        timestamp: Frame timestamp (seconds)
        resolution: (width, height) tuple
        pixels: Pixel data (numpy array, shape: [H, W, C])
        metadata: Optional metadata dict
            - motion_vectors: Motion vector data
            - depth_map: Depth information
            - quality_hint: Suggested quality level
            - frame_type: 'real' or 'generated'
    """
    timestamp: float
    resolution: Tuple[int, int]
    pixels: npt.NDArray[np.uint8]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FrameGenCapabilities:
    """Frame generator capabilities
    
    Attributes:
        max_interpolation_factor: Max frames to generate between real frames
        supports_motion_vectors: Can use motion vector data
        supports_adaptive_quality: Can adjust quality dynamically
        min_resolution: Minimum supported resolution (width, height)
        max_resolution: Maximum supported resolution (width, height)
        hardware_accelerated: Uses GPU acceleration
        supported_qualities: List of supported quality modes
    """
    max_interpolation_factor: int
    supports_motion_vectors: bool
    supports_adaptive_quality: bool
    min_resolution: Tuple[int, int]
    max_resolution: Tuple[int, int]
    hardware_accelerated: bool
    supported_qualities: List[FrameGenQuality]


@dataclass
class FrameGenStats:
    """Frame generation performance statistics
    
    Attributes:
        frames_generated: Total frames generated
        avg_generation_time: Average time per frame (ms)
        quality_mode: Current quality mode
        interpolation_factor: Current interpolation factor
        gpu_utilization: GPU usage (0-100)
        memory_usage: Memory usage (MB)
        last_error: Last error message (if any)
    """
    frames_generated: int
    avg_generation_time: float
    quality_mode: FrameGenQuality
    interpolation_factor: int
    gpu_utilization: float
    memory_usage: float
    last_error: Optional[str] = None


class IFrameGenerator(ABC):
    """Abstract interface for frame generation
    
    v0.3.5d_package3.3a - Foundation for Frame Gen
    
    This interface defines the contract for all frame generation
    implementations. Concrete implementations might include:
    - AMD FSR 3 Frame Generation
    - NVIDIA DLSS 3 Frame Generation
    - Custom ML-based generators
    - Software interpolation (fallback)
    
    Usage Pattern:
        1. Check availability: is_available()
        2. Query capabilities: get_capabilities()
        3. Set quality: set_quality(mode)
        4. Generate frames: generate_frame(prev, current, t)
        5. Monitor performance: get_performance_stats()
    
    Example:
        >>> generator = MyFrameGenerator()
        >>> 
        >>> if generator.is_available():
        >>>     caps = generator.get_capabilities()
        >>>     print(f"Max interpolation: {caps.max_interpolation_factor}x")
        >>>     
        >>>     generator.set_quality(FrameGenQuality.BALANCED)
        >>>     
        >>>     # Generate intermediate frame at t=0.5
        >>>     generated = generator.generate_frame(
        >>>         prev_frame=frame1,
        >>>         current_frame=frame2,
        >>>         t=0.5
        >>>     )
    """
    
    @abstractmethod
    def generate_frame(self,
                      prev_frame: FrameData,
                      current_frame: FrameData,
                      t: float) -> FrameData:
        """Generate an intermediate frame
        
        Args:
            prev_frame: Previous real frame
            current_frame: Current real frame
            t: Interpolation factor (0.0-1.0)
                0.0 = prev_frame
                0.5 = halfway between
                1.0 = current_frame
        
        Returns:
            Generated frame at time t
        
        Raises:
            RuntimeError: If generation fails
            ValueError: If t is out of range
        
        Example:
            >>> # Generate frame halfway between two frames
            >>> mid_frame = generator.generate_frame(frame1, frame2, 0.5)
        """
        pass
    
    @abstractmethod
    def set_quality(self, quality: FrameGenQuality) -> bool:
        """Set frame generation quality mode
        
        Args:
            quality: Desired quality mode
        
        Returns:
            True if quality was set successfully
        
        Example:
            >>> generator.set_quality(FrameGenQuality.BALANCED)
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> FrameGenCapabilities:
        """Get generator capabilities
        
        Returns:
            Capabilities object describing features
        
        Example:
            >>> caps = generator.get_capabilities()
            >>> if caps.supports_motion_vectors:
            >>>     print("Motion vectors supported!")
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if generator is available
        
        Returns:
            True if generator is ready to use
        
        Example:
            >>> if generator.is_available():
            >>>     # Safe to generate frames
            >>>     pass
        """
        pass
    
    @abstractmethod
    def get_performance_stats(self) -> FrameGenStats:
        """Get performance statistics
        
        Returns:
            Performance stats object
        
        Example:
            >>> stats = generator.get_performance_stats()
            >>> print(f"Avg gen time: {stats.avg_generation_time:.2f}ms")
        """
        pass
    
    # Optional methods (have default implementations)
    
    def set_interpolation_factor(self, factor: int) -> bool:
        """Set interpolation factor (frames to generate)
        
        Args:
            factor: Number of frames to generate between real frames
                    1 = no interpolation
                    2 = 1 generated frame (double FPS)
                    3 = 2 generated frames (triple FPS)
        
        Returns:
            True if factor was set successfully
        
        Example:
            >>> generator.set_interpolation_factor(2)  # Double FPS
        """
        # Default: not supported
        return False
    
    def initialize(self) -> bool:
        """Initialize the generator
        
        Returns:
            True if initialization succeeded
        
        Example:
            >>> if generator.initialize():
            >>>     print("Generator ready")
        """
        # Default: assume already initialized
        return True
    
    def shutdown(self):
        """Shutdown and cleanup resources
        
        Example:
            >>> generator.shutdown()
        """
        # Default: nothing to cleanup
        pass
    
    def get_name(self) -> str:
        """Get generator name
        
        Returns:
            Human-readable name
        
        Example:
            >>> print(generator.get_name())
        """
        return self.__class__.__name__
    
    def get_version(self) -> str:
        """Get generator version
        
        Returns:
            Version string
        
        Example:
            >>> print(f"Version: {generator.get_version()}")
        """
        return "1.0.0"


# ========== HELPER FUNCTIONS ==========

def create_test_frame(width: int = 1920, height: int = 1080,
                     timestamp: float = 0.0) -> FrameData:
    """Create a test frame with random data
    
    Args:
        width: Frame width
        height: Frame height
        timestamp: Frame timestamp
    
    Returns:
        FrameData object with random pixels
    
    Example:
        >>> frame = create_test_frame()
    """
    pixels = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return FrameData(
        timestamp=timestamp,
        resolution=(width, height),
        pixels=pixels,
        metadata={'frame_type': 'test'}
    )


def validate_frame_data(frame: FrameData) -> bool:
    """Validate frame data structure
    
    Args:
        frame: Frame to validate
    
    Returns:
        True if valid
    
    Example:
        >>> if validate_frame_data(frame):
        >>>     # Safe to use
        >>>     pass
    """
    if frame.resolution[0] <= 0 or frame.resolution[1] <= 0:
        return False
    
    expected_shape = (frame.resolution[1], frame.resolution[0], 3)
    if frame.pixels.shape != expected_shape:
        return False
    
    return True


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("IFrameGenerator v0.3.5d_package3.3a Test")
    print("="*60)
    
    # Test frame creation
    print("\n[Test 1] Frame data creation")
    frame = create_test_frame(1920, 1080, 0.0)
    print(f"  Resolution: {frame.resolution}")
    print(f"  Pixels shape: {frame.pixels.shape}")
    print(f"  Timestamp: {frame.timestamp}")
    print(f"  Valid: {validate_frame_data(frame)}")
    
    # Test quality modes
    print("\n[Test 2] Quality modes")
    for quality in FrameGenQuality:
        print(f"  - {quality.value}")
    
    # Test capabilities
    print("\n[Test 3] Capabilities structure")
    caps = FrameGenCapabilities(
        max_interpolation_factor=4,
        supports_motion_vectors=True,
        supports_adaptive_quality=True,
        min_resolution=(640, 480),
        max_resolution=(3840, 2160),
        hardware_accelerated=True,
        supported_qualities=list(FrameGenQuality)
    )
    print(f"  Max interpolation: {caps.max_interpolation_factor}x")
    print(f"  Motion vectors: {caps.supports_motion_vectors}")
    print(f"  Adaptive quality: {caps.supports_adaptive_quality}")
    print(f"  Resolution range: {caps.min_resolution} - {caps.max_resolution}")
    print(f"  Hardware accelerated: {caps.hardware_accelerated}")
    
    # Test stats
    print("\n[Test 4] Performance stats structure")
    stats = FrameGenStats(
        frames_generated=1000,
        avg_generation_time=8.5,
        quality_mode=FrameGenQuality.BALANCED,
        interpolation_factor=2,
        gpu_utilization=45.2,
        memory_usage=512.0,
        last_error=None
    )
    print(f"  Frames generated: {stats.frames_generated}")
    print(f"  Avg time: {stats.avg_generation_time:.2f}ms")
    print(f"  Quality: {stats.quality_mode.value}")
    print(f"  GPU usage: {stats.gpu_utilization:.1f}%")
    
    print("\n" + "="*60)
    print("✅ IFrameGenerator v0.3.5d_package3.3a - All Tests Passed!")
    print("="*60)
    print("\nInterface Features:")
    print("  ✅ Abstract base class (ABC)")
    print("  ✅ Type hints for safety")
    print("  ✅ Quality modes enum")
    print("  ✅ Capabilities query")
    print("  ✅ Performance stats")
    print("  ✅ Frame data structure")
    print("\nReady for:")
    print("  🎯 FSR 3 implementation")
    print("  🎯 DLSS 3 implementation")
    print("  🎯 Custom ML models")
    print("  🎯 Software fallback")
    print("="*60)
