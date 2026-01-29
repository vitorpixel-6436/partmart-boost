#!/usr/bin/env python3
"""Universal Upscaler Module

Version: 0.3.5d (package 3.8a, stage 4/6)

Multi-backend upscaling system supporting:
- OptiScaler (FSR 3.1 / XeSS 2.1 / DLSS via middleware) ⭐
- FSR 3.1 (direct DLL)
- XeSS 2.1 (direct DLL)
- Software fallback
"""

from .core import UniversalUpscaler, UpscaleContext
from .types import (
    UpscalerBackend,
    UpscalerQuality,
    UpscalerFeature,
    UpscaleConfig,
    FrameData,
    UpscaleMetrics,
    BackendInfo
)

__version__ = "0.3.5d+stage4"
__all__ = [
    'UniversalUpscaler',
    'UpscaleContext',
    'UpscalerBackend',
    'UpscalerQuality',
    'UpscalerFeature',
    'UpscaleConfig',
    'FrameData',
    'UpscaleMetrics',
    'BackendInfo',
]

print("[UniversalUpscaler] Package 3.8a Stage 4/6 - OptiScaler Integration loaded")
print("  Backends: OptiScaler ⭐ | FSR3 | XeSS | Software")
