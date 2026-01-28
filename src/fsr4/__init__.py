#!/usr/bin/env python3
"""AMD FidelityFX Super Resolution 4 (FSR4)

Version: 0.3.5d+patch9 - FIXED: Added missing exception exports

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
from .exceptions import (
    FSR4Exception,
    FSR4InitializationError,
    FSR4ContextError,
    FSR4ProcessingError,
    FSR4InvalidParameterError,
    FSR4OutOfMemoryError,
    FSR4DeviceNotFoundError,
    FSR4UnsupportedFormatError
)

__version__ = "0.3.5d+patch9"
__all__ = [
    # Core classes
    'FSR4SDK',
    'FSR4Context',
    
    # Types and enums
    'FSR4QualityMode',
    'FSR4Feature',
    'FSR4Status',
    'FSR4Config',
    'FSR4FrameData',
    'FSR4PerformanceMetrics',
    
    # Exceptions
    'FSR4Exception',
    'FSR4InitializationError',
    'FSR4ContextError',
    'FSR4ProcessingError',
    'FSR4InvalidParameterError',
    'FSR4OutOfMemoryError',
    'FSR4DeviceNotFoundError',
    'FSR4UnsupportedFormatError',
]

print("[FSR4] Real implementation loaded (v0.3.5d+patch9)")
