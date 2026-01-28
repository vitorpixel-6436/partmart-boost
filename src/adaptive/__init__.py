#!/usr/bin/env python3
"""Adaptive Performance System

Version: 0.3.5d_package3.4a

Intelligent performance adaptation system for PartMart Boost.

Components:
- controller: Adaptive performance controller
- strategies: Quality adjustment strategies
- thermal: Thermal management
- power_modes: Power mode definitions

Example:
    >>> from adaptive import AdaptiveController, PowerMode
    >>> 
    >>> controller = AdaptiveController(databus)
    >>> controller.set_power_mode(PowerMode.BALANCED)
    >>> controller.set_target_fps(60)
    >>> controller.start()
"""

from .controller import AdaptiveController
from .power_modes import PowerMode, PowerProfile
from .strategies import QualityStrategy

__version__ = "0.3.5d_package3.4a"
__all__ = [
    'AdaptiveController',
    'PowerMode',
    'PowerProfile',
    'QualityStrategy',
]
