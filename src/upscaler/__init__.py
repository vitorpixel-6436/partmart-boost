#!/usr/bin/env python3
"""Upscaler Package

Version: 0.3.5d_package3.3c

Upscaling implementations for PartMart Boost.

Components:
- interfaces: Abstract upscaler interface
- fsr4_upscaler: AMD FSR 4 Super Resolution implementation

Example:
    >>> from upscaler import FSR4Upscaler, UpscaleQuality
    >>> 
    >>> upscaler = FSR4Upscaler()
    >>> upscaler.initialize(display_width=1920, display_height=1080)
    >>> upscaler.set_quality(UpscaleQuality.QUALITY)
    >>> 
    >>> upscaled = upscaler.upscale(low_res_frame)
"""

from .interfaces import (
    IUpscaler,
    UpscaleQuality,
    UpscaleCapabilities,
    UpscaleStats,
    UpscaleException,
    UpscaleNotAvailableException,
)

from .fsr4_upscaler import FSR4Upscaler

__version__ = "0.3.5d_package3.3c"
__all__ = [
    # Interfaces
    'IUpscaler',
    'UpscaleQuality',
    'UpscaleCapabilities',
    'UpscaleStats',
    # Implementations
    'FSR4Upscaler',
    # Exceptions
    'UpscaleException',
    'UpscaleNotAvailableException',
]
