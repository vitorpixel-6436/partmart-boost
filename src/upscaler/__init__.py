#!/usr/bin/env python3
"""Upscaler Package

Version: 0.3.5d_hotfix4 (package 3.9a, stage 7.7d_hotfix4)

UPDATED: Import from upscaler_types instead of types
"""
from .upscaler_types import UpscaleMode, Backend, APIType
from .upscaler import Upscaler

__all__ = ['Upscaler', 'UpscaleMode', 'Backend', 'APIType']
