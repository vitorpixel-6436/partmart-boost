#!/usr/bin/env python3
"""OptiScaler Types

Version: 0.3.5d (package 3.8a, stage 1/6)
"""
from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


class OptiScalerBackend(IntEnum):
    """OptiScaler upscaling backend"""
    FSR3 = 0        # AMD FidelityFX Super Resolution 3.1
    XESS = 1        # Intel Xe Super Sampling 2.1
    DLSS = 2        # NVIDIA Deep Learning Super Sampling
    AUTO = 3        # Auto-select based on GPU


class OptiScalerQuality(IntEnum):
    """Quality modes (matches OptiScaler presets)"""
    PERFORMANCE = 0      # 2.0x scale - max FPS
    BALANCED = 1         # 1.7x scale - balance
    QUALITY = 2          # 1.5x scale - recommended
    ULTRA_QUALITY = 3    # 1.3x scale - best quality
    NATIVE = 4           # 1.0x scale - no upscaling


class InstallStatus(IntEnum):
    """OptiScaler installation status"""
    NOT_INSTALLED = 0    # Not found
    INSTALLED = 1        # Installed and working
    OUTDATED = 2         # Old version detected
    CORRUPTED = 3        # Files corrupted
    DOWNLOADING = 4      # Download in progress
    INSTALLING = 5       # Installation in progress


@dataclass
class OptiScalerInfo:
    """OptiScaler installation information
    
    Attributes:
        version: OptiScaler version string
        install_path: Installation directory
        status: Installation status
        backends_available: Available backends (FSR3, XeSS, DLSS)
        config_path: Configuration file path
    """
    version: str
    install_path: Path
    status: InstallStatus
    backends_available: list
    config_path: Optional[Path] = None


@dataclass
class GameInfo:
    """Game information for injection
    
    Attributes:
        name: Game name
        exe_path: Path to game executable
        game_dir: Game installation directory
        process_id: Running process ID (if running)
        has_dlss: Game supports DLSS
        has_fsr: Game supports FSR
        has_xess: Game supports XeSS
    """
    name: str
    exe_path: Path
    game_dir: Path
    process_id: Optional[int] = None
    has_dlss: bool = False
    has_fsr: bool = False
    has_xess: bool = False


# Exceptions

class OptiScalerException(Exception):
    """Base OptiScaler exception"""
    pass


class InstallationError(OptiScalerException):
    """Installation failed"""
    pass


class InjectionError(OptiScalerException):
    """Game injection failed"""
    pass


class ConfigurationError(OptiScalerException):
    """Configuration error"""
    pass
