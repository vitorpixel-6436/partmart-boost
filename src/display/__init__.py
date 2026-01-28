#!/usr/bin/env python3
"""Multi-Display Support System

Version: 0.3.5d_package3.4c

Multi-display management for PartMart Boost.

Components:
- manager: Display manager
- display_info: Display information structures
- hdr: HDR detection and management
- vrr: VRR/G-Sync/FreeSync detection

Example:
    >>> from display import DisplayManager
    >>> 
    >>> manager = DisplayManager()
    >>> manager.detect_displays()
    >>> 
    >>> for display in manager.get_displays():
    >>>     print(f"{display.name}: {display.resolution}")
"""

from .display_info import Display, DisplayInfo, HDRFormat, VRRType
from .manager import DisplayManager

__version__ = "0.3.5d_package3.4c"
__all__ = [
    'Display',
    'DisplayInfo',
    'HDRFormat',
    'VRRType',
    'DisplayManager',
]
