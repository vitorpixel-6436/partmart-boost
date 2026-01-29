#!/usr/bin/env python3
"""MSI Color Palette

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

MSI-inspired color system: aggressive reds, deep blacks, sharp grays
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class MSIColors:
    """MSI color palette"""
    
    # Primary MSI Red
    RED_PRIMARY: str = '#E30613'
    RED_HOVER: str = '#FF1825'
    RED_PRESSED: str = '#C00510'
    RED_DARK: str = '#8A0409'
    
    # Backgrounds - Deep blacks with subtle gradients
    BG_PRIMARY: str = '#0A0A0A'
    BG_SECONDARY: str = '#141414'
    BG_TERTIARY: str = '#1E1E1E'
    BG_ELEVATED: str = '#282828'
    
    # Glass effects - Transparent layers
    GLASS_DARK: str = 'rgba(10, 10, 10, 0.85)'
    GLASS_MEDIUM: str = 'rgba(20, 20, 20, 0.75)'
    GLASS_LIGHT: str = 'rgba(30, 30, 30, 0.65)'
    GLASS_SUBTLE: str = 'rgba(40, 40, 40, 0.45)'
    
    # Sharp grays - For borders and dividers
    GRAY_SHARP: str = '#3C3C3C'
    GRAY_BORDER: str = '#505050'
    GRAY_DIVIDER: str = '#646464'
    GRAY_SOFT: str = '#787878'
    
    # Text colors
    TEXT_PRIMARY: str = '#FFFFFF'
    TEXT_SECONDARY: str = '#B4B4B4'
    TEXT_TERTIARY: str = '#8C8C8C'
    TEXT_DISABLED: str = '#646464'
    
    # Accent colors
    ACCENT_GREEN: str = '#00D639'
    ACCENT_BLUE: str = '#00A8E8'
    ACCENT_YELLOW: str = '#FFB800'
    ACCENT_ORANGE: str = '#FF6B35'
    
    # Status colors
    STATUS_SUCCESS: str = '#00D639'
    STATUS_WARNING: str = '#FFB800'
    STATUS_ERROR: str = '#E30613'
    STATUS_INFO: str = '#00A8E8'
    
    # Gradients
    GRADIENT_RED: str = 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E30613, stop:1 #8A0409)'
    GRADIENT_DARK: str = 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141414, stop:1 #0A0A0A)'
    GRADIENT_GLASS: str = 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(30,30,30,0.9), stop:1 rgba(10,10,10,0.7))'
    
    @classmethod
    def to_dict(cls) -> Dict[str, str]:
        """Convert colors to dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and isinstance(value, str)
        }
    
    @classmethod
    def get_rgba(cls, color: str, alpha: float = 1.0) -> str:
        """Convert hex to rgba with custom alpha"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f'rgba({r}, {g}, {b}, {alpha})'
        return color
