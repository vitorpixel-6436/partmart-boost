#!/usr/bin/env python3
"""Universal Upscaler System

Version: 0.3.5d (package 3.7a) - Stage 1/9

Hybrid upscaling system supporting:
- FSR 3.1 (AMD, real implementation)
- XeSS 2.1 (Intel, real implementation)  
- Software Fallback (cross-platform)

Auto-detects best backend and swaps on the fly.
"""

from .core import UniversalUpscaler
from .types import (
    UpscalerBackend,
    UpscalerQuality,
    UpscaleConfig,
    FrameData,
    UpscaleMetrics,
    UpscalerException,
    BackendNotAvailableError,
    UpscaleError
)

__version__ = "0.3.5d+stage1"
__all__ = [
    'UniversalUpscaler',
    'UpscalerBackend',
    'UpscalerQuality',
    'UpscaleConfig',
    'FrameData',
    'UpscaleMetrics',
    'UpscalerException',
    'BackendNotAvailableError',
    'UpscaleError',
]

print("[UniversalUpscaler] Stage 1/9 - Architecture loaded")
