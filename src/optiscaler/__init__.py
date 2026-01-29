#!/usr/bin/env python3
"""OptiScaler Integration Module

Version: 0.3.5d (package 3.8a, stage 1/6)

Integrates OptiScaler middleware for real FSR 3.1, XeSS 2.1, and DLSS.

OptiScaler is an open-source middleware that bridges upscaling technologies,
allowing any game to use FSR 3.1, XeSS 2.1, or DLSS regardless of original support.

GitHub: https://github.com/optiscaler/OptiScaler
"""

from .core import OptiScalerManager
from .config import OptiScalerConfig
from .types import (
    OptiScalerBackend,
    OptiScalerQuality,
    InstallStatus,
    OptiScalerException,
    InstallationError
)

__version__ = "0.3.5d+stage1"
__all__ = [
    'OptiScalerManager',
    'OptiScalerConfig',
    'OptiScalerBackend',
    'OptiScalerQuality',
    'InstallStatus',
    'OptiScalerException',
    'InstallationError',
]

print("[OptiScaler] Stage 1/6 - Architecture loaded")
