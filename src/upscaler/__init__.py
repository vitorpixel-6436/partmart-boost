#!/usr/bin/env python3
"""Universal Hybrid Upscaler System

Version: 0.4.0-alpha

Multi-backend upscaling with FSR 3.1, XeSS 2.1, and software fallback.
"""

from .core import UniversalUpscaler, UpscalerContext
from .types import QualityMode, UpscalerBackend, UpscalerStatus
from .exceptions import UpscalerException

__version__ = "0.4.0-alpha"
__all__ = [
    'UniversalUpscaler',
    'UpscalerContext',
    'QualityMode',
    'UpscalerBackend',
    'UpscalerStatus',
    'UpscalerException',
]

print("[Upscaler] Universal Hybrid Upscaler System loaded (v0.4.0-alpha)")
print("[Upscaler] Backends: FSR 3.1 | XeSS 2.1 | Software Fallback")
