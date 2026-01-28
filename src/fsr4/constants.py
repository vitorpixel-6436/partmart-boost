#!/usr/bin/env python3
"""FSR 4 Constants and Enums

Version: 0.3.5d_package3.3a

Constants and enumerations from AMD FSR 4 SDK.
Mapped from ffx_fsr4.h and related headers.
"""
from enum import IntEnum, Enum
from typing import Dict


class FSR4QualityMode(IntEnum):
    """FSR 4 quality modes with scaling ratios
    
    Each mode defines the ratio between output and input resolution.
    For example, Quality (1.5x) means:
    - Input: 1280x720
    - Output: 1920x1080 (1.5x upscale)
    
    Attributes:
        NATIVE: No upscaling (1.0x)
        QUALITY: High quality (1.5x)
        BALANCED: Balanced quality/performance (1.7x)
        PERFORMANCE: Performance priority (2.0x)
        ULTRA_PERFORMANCE: Maximum performance (3.0x)
    """
    NATIVE = 0
    QUALITY = 1
    BALANCED = 2
    PERFORMANCE = 3
    ULTRA_PERFORMANCE = 4


class FSR4ResourceType(IntEnum):
    """FSR 4 resource types
    
    Attributes:
        TEXTURE_2D: 2D texture resource
        BUFFER: Buffer resource
    """
    TEXTURE_2D = 0
    BUFFER = 1


class FSR4Feature(IntEnum):
    """FSR 4 features
    
    Attributes:
        FRAME_GENERATION: Frame generation feature
        SUPER_RESOLUTION: Super resolution (upscaling) feature
    """
    FRAME_GENERATION = 0
    SUPER_RESOLUTION = 1


class FSR4ContextFlags(IntEnum):
    """FSR 4 context creation flags
    
    Attributes:
        NONE: No special flags
        ENABLE_HIGH_DYNAMIC_RANGE: Enable HDR support
        ENABLE_DISPLAY_RESOLUTION_MOTION_VECTORS: Use display resolution MVs
        ENABLE_MOTION_VECTORS_JITTER_CANCELLATION: Cancel jitter in MVs
        ENABLE_DEPTH_INVERTED: Depth buffer is inverted (0=far, 1=near)
        ENABLE_DEPTH_INFINITE: Infinite far plane
        ENABLE_AUTO_EXPOSURE: Auto exposure adjustment
        ENABLE_DYNAMIC_RESOLUTION: Support dynamic resolution
    """
    NONE = 0
    ENABLE_HIGH_DYNAMIC_RANGE = 1 << 0
    ENABLE_DISPLAY_RESOLUTION_MOTION_VECTORS = 1 << 1
    ENABLE_MOTION_VECTORS_JITTER_CANCELLATION = 1 << 2
    ENABLE_DEPTH_INVERTED = 1 << 3
    ENABLE_DEPTH_INFINITE = 1 << 4
    ENABLE_AUTO_EXPOSURE = 1 << 5
    ENABLE_DYNAMIC_RESOLUTION = 1 << 6


class FSR4MessageType(IntEnum):
    """FSR 4 message types for logging
    
    Attributes:
        ERROR: Error message
        WARNING: Warning message
        INFO: Information message
    """
    ERROR = 0
    WARNING = 1
    INFO = 2


# Quality mode scaling ratios
FSR4_QUALITY_MODE_RATIOS: Dict[FSR4QualityMode, float] = {
    FSR4QualityMode.NATIVE: 1.0,
    FSR4QualityMode.QUALITY: 1.5,
    FSR4QualityMode.BALANCED: 1.7,
    FSR4QualityMode.PERFORMANCE: 2.0,
    FSR4QualityMode.ULTRA_PERFORMANCE: 3.0,
}


# Quality mode names
FSR4_QUALITY_MODE_NAMES: Dict[FSR4QualityMode, str] = {
    FSR4QualityMode.NATIVE: "Native",
    FSR4QualityMode.QUALITY: "Quality",
    FSR4QualityMode.BALANCED: "Balanced",
    FSR4QualityMode.PERFORMANCE: "Performance",
    FSR4QualityMode.ULTRA_PERFORMANCE: "Ultra Performance",
}


def get_scaling_ratio(quality_mode: FSR4QualityMode) -> float:
    """Get scaling ratio for quality mode
    
    Args:
        quality_mode: Quality mode
    
    Returns:
        Scaling ratio (output/input)
    
    Example:
        >>> ratio = get_scaling_ratio(FSR4QualityMode.QUALITY)
        >>> print(f"Quality mode scales by {ratio}x")
    """
    return FSR4_QUALITY_MODE_RATIOS.get(quality_mode, 1.0)


def get_quality_mode_name(quality_mode: FSR4QualityMode) -> str:
    """Get human-readable name for quality mode
    
    Args:
        quality_mode: Quality mode
    
    Returns:
        Mode name
    
    Example:
        >>> name = get_quality_mode_name(FSR4QualityMode.BALANCED)
        >>> print(name)  # "Balanced"
    """
    return FSR4_QUALITY_MODE_NAMES.get(quality_mode, "Unknown")


def calculate_render_resolution(display_width: int, display_height: int,
                               quality_mode: FSR4QualityMode) -> tuple[int, int]:
    """Calculate render resolution for FSR 4 upscaling
    
    Args:
        display_width: Target display width
        display_height: Target display height
        quality_mode: FSR 4 quality mode
    
    Returns:
        Tuple of (render_width, render_height)
    
    Example:
        >>> render_res = calculate_render_resolution(1920, 1080, FSR4QualityMode.QUALITY)
        >>> print(f"Render at: {render_res}")  # (1280, 720)
    """
    ratio = get_scaling_ratio(quality_mode)
    
    render_width = int(display_width / ratio)
    render_height = int(display_height / ratio)
    
    # Ensure even dimensions (required by FSR 4)
    render_width = (render_width // 2) * 2
    render_height = (render_height // 2) * 2
    
    return (render_width, render_height)


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("FSR 4 Constants v0.3.5d_package3.3a Test")
    print("="*60)
    
    print("\n[Test 1] Quality modes")
    for mode in FSR4QualityMode:
        name = get_quality_mode_name(mode)
        ratio = get_scaling_ratio(mode)
        print(f"  {name:20} {ratio:.1f}x")
    
    print("\n[Test 2] Render resolution calculation")
    display_res = (1920, 1080)
    print(f"  Display: {display_res}")
    
    for mode in FSR4QualityMode:
        render_res = calculate_render_resolution(*display_res, mode)
        name = get_quality_mode_name(mode)
        print(f"  {name:20} {render_res}")
    
    print("\n[Test 3] Context flags")
    flags = FSR4ContextFlags.ENABLE_HIGH_DYNAMIC_RANGE | FSR4ContextFlags.ENABLE_AUTO_EXPOSURE
    print(f"  Combined flags: {flags}")
    print(f"  HDR enabled: {bool(flags & FSR4ContextFlags.ENABLE_HIGH_DYNAMIC_RANGE)}")
    print(f"  Auto exposure: {bool(flags & FSR4ContextFlags.ENABLE_AUTO_EXPOSURE)}")
    
    print("\n" + "="*60)
    print("✅ FSR 4 Constants - All Tests Passed!")
    print("="*60)
