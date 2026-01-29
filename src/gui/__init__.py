#!/usr/bin/env python3
"""GUI Module

Version: 0.3.5d (package 3.8a, stage 5/6)
"""

try:
    from .optiscaler_tab import OptiScalerTab
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("[GUI] Warning: PyQt6 not available")

__all__ = ['OptiScalerTab'] if GUI_AVAILABLE else []

if GUI_AVAILABLE:
    print("[GUI] Stage 5/6 - OptiScaler Controls loaded")
