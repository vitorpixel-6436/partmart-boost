#!/usr/bin/env python3
"""Upscaler Backends

Version: 0.3.5d (package 3.7a)
"""

from .base import BaseBackend
from .fsr3 import FSR3Backend
from .xess import XeSSBackend
from .software import SoftwareBackend

__all__ = [
    'BaseBackend',
    'FSR3Backend',
    'XeSSBackend',
    'SoftwareBackend',
]
