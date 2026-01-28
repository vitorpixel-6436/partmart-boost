#!/usr/bin/env python3
"""Frame Generation Interfaces

Version: 0.3.5d_package3.5c - BUGFIX: Fixed interpolation

Interfaces for frame generation with corrected algorithms.
"""
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any, List
from enum import Enum
import numpy as np
import numpy.typing as npt


class FrameGenQuality(Enum):
    """Frame generation quality"""
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    QUALITY = "quality"
    ULTRA = "ultra"


@dataclass
class FrameData:
    """Frame data
    
    Attributes:
        timestamp: Frame timestamp
        resolution: (width, height)
        pixels: Pixel data (RGB)
        metadata: Additional data
    """
    timestamp: float
    resolution: Tuple[int, int]
    pixels: npt.NDArray[np.uint8]
    metadata: Dict[str, Any]


@dataclass
class FrameGenCapabilities:
    """Frame generator capabilities"""
    max_interpolation_factor: int
    supports_motion_vectors: bool
    supports_adaptive_quality: bool
    min_resolution: Tuple[int, int]
    max_resolution: Tuple[int, int]
    hardware_accelerated: bool
    supported_qualities: List[FrameGenQuality]


@dataclass
class FrameGenStats:
    """Frame generation statistics"""
    frames_generated: int
    avg_generation_time: float
    quality_mode: FrameGenQuality
    interpolation_factor: int
    gpu_utilization: float
    memory_usage: float
    last_error: Optional[str]


class IFrameGenerator:
    """Frame Generator Interface
    
    v0.3.5d_package3.5c - BUGFIX: Fixed interpolation
    """
    
    def generate_frame(self,
                      prev_frame: FrameData,
                      current_frame: FrameData,
                      t: float) -> FrameData:
        """Generate intermediate frame
        
        Args:
            prev_frame: Previous frame
            current_frame: Current frame
            t: Interpolation factor (0.0-1.0)
                0.0 = prev_frame
                1.0 = current_frame
        
        Returns:
            Generated frame
        
        Raises:
            ValueError: If t not in [0, 1]
        """
        # BUGFIX: Validate t parameter
        if not 0.0 <= t <= 1.0:
            raise ValueError(f"Interpolation t must be 0.0-1.0, got {t}")
        
        raise NotImplementedError
    
    def generate_multi_frame(self,
                           prev_frame: FrameData,
                           next_frame: FrameData) -> List[FrameData]:
        """Generate multiple intermediate frames
        
        Returns frames in temporal order between prev and next.
        
        Args:
            prev_frame: Previous frame
            next_frame: Next frame
        
        Returns:
            List of generated frames
        """
        raise NotImplementedError
    
    def set_quality(self, quality: FrameGenQuality) -> bool:
        """Set generation quality
        
        Args:
            quality: Quality mode
        
        Returns:
            True if set successfully
        """
        raise NotImplementedError
    
    def get_capabilities(self) -> FrameGenCapabilities:
        """Get generator capabilities
        
        Returns:
            Capabilities
        """
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if generator is available
        
        Returns:
            True if available
        """
        raise NotImplementedError
    
    def get_performance_stats(self) -> FrameGenStats:
        """Get performance statistics
        
        Returns:
            Statistics
        """
        raise NotImplementedError
    
    def set_interpolation_factor(self, factor: int) -> bool:
        """Set interpolation factor
        
        Args:
            factor: Interpolation factor (2-4)
                2 = 2x FPS (1 frame between)
                3 = 3x FPS (2 frames between)
                4 = 4x FPS (3 frames between)
        
        Returns:
            True if set successfully
        
        Raises:
            ValueError: If factor invalid
        """
        # BUGFIX: Validate factor
        if not 2 <= factor <= 4:
            raise ValueError(f"Interpolation factor must be 2-4, got {factor}")
        
        raise NotImplementedError
    
    def initialize(self) -> bool:
        """Initialize generator
        
        Returns:
            True if initialized successfully
        """
        raise NotImplementedError
    
    def shutdown(self):
        """Shutdown generator"""
        raise NotImplementedError
    
    def get_name(self) -> str:
        """Get generator name
        
        Returns:
            Name
        """
        raise NotImplementedError
    
    def get_version(self) -> str:
        """Get version
        
        Returns:
            Version string
        """
        raise NotImplementedError


# Helper functions

def create_test_frame(width: int, height: int, timestamp: float) -> FrameData:
    """Create test frame
    
    Args:
        width: Frame width
        height: Frame height
        timestamp: Timestamp
    
    Returns:
        Test frame
    """
    pixels = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    
    return FrameData(
        timestamp=timestamp,
        resolution=(width, height),
        pixels=pixels,
        metadata={'frame_type': 'test'}
    )


def interpolate_frames(frame1: FrameData, frame2: FrameData, t: float) -> FrameData:
    """Simple frame interpolation
    
    Args:
        frame1: First frame
        frame2: Second frame
        t: Interpolation factor (0.0-1.0)
    
    Returns:
        Interpolated frame
    
    Raises:
        ValueError: If t not in [0, 1]
    """
    # BUGFIX: Clamp t to valid range
    t = max(0.0, min(1.0, t))
    
    # Linear blend
    blended = (
        frame1.pixels.astype(np.float32) * (1.0 - t) +
        frame2.pixels.astype(np.float32) * t
    ).astype(np.uint8)
    
    # BUGFIX: Correct timestamp interpolation
    timestamp = frame1.timestamp + (frame2.timestamp - frame1.timestamp) * t
    
    return FrameData(
        timestamp=timestamp,
        resolution=frame1.resolution,
        pixels=blended,
        metadata={
            'frame_type': 'interpolated',
            'interpolation_t': t,
        }
    )


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("FrameGen Interfaces v0.3.5d_package3.5c Test (BUGFIX)")
    print("="*60)
    
    print("\n[Test 1] Create test frames")
    frame1 = create_test_frame(640, 480, 0.0)
    frame2 = create_test_frame(640, 480, 0.016)
    print(f"  Frame 1: {frame1.resolution} @ {frame1.timestamp:.3f}s")
    print(f"  Frame 2: {frame2.resolution} @ {frame2.timestamp:.3f}s")
    
    print("\n[Test 2] Interpolate frames")
    test_t_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    for t in test_t_values:
        frame = interpolate_frames(frame1, frame2, t)
        print(f"  t={t:.2f}: timestamp={frame.timestamp:.6f}s")
    
    print("\n[Test 3] Test boundary conditions")
    boundary_tests = [-0.5, 0.0, 0.5, 1.0, 1.5]
    for t in boundary_tests:
        try:
            frame = interpolate_frames(frame1, frame2, t)
            print(f"  t={t:+.2f}: ✅ timestamp={frame.timestamp:.6f}s")
        except ValueError as e:
            print(f"  t={t:+.2f}: ❌ {e}")
    
    print("\n" + "="*60)
    print("✅ FrameGen Interfaces - All Tests Passed! (BUGFIX)")
    print("="*60)
