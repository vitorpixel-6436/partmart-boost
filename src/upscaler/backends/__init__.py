#!/usr/bin/env python3
"""Upscaler Backends

Version: 0.4.0-alpha
"""

from .fsr3_backend import FSR3Backend
from .xess_backend import XeSSBackend
from .software_backend import SoftwareBackend

__all__ = ['FSR3Backend', 'XeSSBackend', 'SoftwareBackend']
