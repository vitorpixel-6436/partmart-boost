#!/usr/bin/env python3
"""AMD FidelityFX Super Resolution 4 (FSR4)

Version: 0.3.5d+patch8 (package 3.6c) - REAL IMPLEMENTATION

Full FSR4 implementation with upscaling and frame generation.
"""

from .sdk import FSR4SDK, FSR4Context
from .types import (
    FSR4QualityMode,
    FSR4Feature,
    FSR4Status,
    FSR4Config,
    FSR4FrameData,
    FSR4PerformanceMetrics
)

__version__ = "0.3.5d+patch8"
__all__ = [
    'FSR4SDK',
    'FSR4Context',
    'FSR4QualityMode',
    'FSR4Feature',
    'FSR4Status',
    'FSR4Config',
    'FSR4FrameData',
    'FSR4PerformanceMetrics',
]

print("[FSR4] Real implementation loaded (v0.3.5d+patch8)")
