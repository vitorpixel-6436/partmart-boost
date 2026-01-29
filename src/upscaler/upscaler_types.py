#!/usr/bin/env python3
"""Upscaler Types and Enums

Version: 0.3.5d_hotfix4 (package 3.9a, stage 7.7d_hotfix4)

RENAMED from types.py to avoid conflict with Python stdlib 'types' module.
"""
from enum import IntEnum, IntFlag


class UpscaleMode(IntEnum):
    """Upscaling mode"""
    QUALITY = 0
    BALANCED = 1
    PERFORMANCE = 2
    ULTRA_PERFORMANCE = 3


class Backend(IntEnum):
    """Upscaling backend"""
    FSR = 0
    DLSS = 1
    XESS = 2
    NATIVE = 3


class APIType(IntFlag):
    """Graphics API type"""
    DX11 = 1
    DX12 = 2
    VULKAN = 4
    OPENGL = 8
