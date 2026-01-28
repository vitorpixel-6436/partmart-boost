#!/usr/bin/env python3
"""AMD FidelityFX Super Resolution 4 (FSR 4) Integration

Version: 0.3.5d_package3.3a

This package provides Python bindings and integration for AMD FSR 4,
including:
- Frame Generation (FG)
- Super Resolution (SR/Upscaling)
- Motion vector support
- Temporal stability

Components:
- constants: FSR 4 enums and constants
- bindings: ctypes FFI bindings to C++ library
- sdk: High-level SDK wrapper

Example:
    >>> from fsr4 import FSR4SDK, FSR4QualityMode
    >>> 
    >>> sdk = FSR4SDK()
    >>> if sdk.is_available():
    >>>     print(f"FSR 4 version: {sdk.get_version()}")
"""

from .constants import (
    FSR4QualityMode,
    FSR4ResourceType,
    FSR4Feature,
)

from .sdk import (
    FSR4SDK,
    FSR4Exception,
    FSR4NotAvailableException,
    FSR4InitializationException,
)

__version__ = "0.3.5d_package3.3a"
__all__ = [
    # Constants
    'FSR4QualityMode',
    'FSR4ResourceType',
    'FSR4Feature',
    # SDK
    'FSR4SDK',
    # Exceptions
    'FSR4Exception',
    'FSR4NotAvailableException',
    'FSR4InitializationException',
]
