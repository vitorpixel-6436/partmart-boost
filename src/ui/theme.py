"""Theme System - Centralized styling and colors

Version: 0.3.5c
Author: PartMart Team
"""
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum


class ThemeMode(Enum):
    """Theme modes"""
    DARK = "dark"
    LIGHT = "light"
    AMOLED = "amoled"


@dataclass
class ColorScheme:
    """Color scheme for theme"""
    # Primary colors
    primary: str
    primary_hover: str
    primary_light: str
    primary_dark: str
    
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_card: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_disabled: str
    
    # Border colors
    border_primary: str
    border_secondary: str
    border_focus: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Special
    shadow: str
    overlay: str


class Theme:
    """Theme management system"""
    
    # PartMart Dark Theme (Default)
    DARK = ColorScheme(
        # Primary (PartMart Red)
        primary="#E63946",
        primary_hover="#FF4757",
        primary_light="#FF6B7A",
        primary_dark="#D62839",
        
        # Backgrounds
        bg_primary="#0D0D0D",
        bg_secondary="#1A1A1A",
        bg_tertiary="#252525",
        bg_card="#1A1A1A",
        
        # Text
        text_primary="#FFFFFF",
        text_secondary="#A0A0A0",
        text_tertiary="#666666",
        text_disabled="#404040",
        
        # Borders
        border_primary="#252525",
        border_secondary="#1A1A1A",
        border_focus="#E63946",
        
        # Status
        success="#4CAF50",
        warning="#FFC107",
        error="#F44336",
        info="#2196F3",
        
        # Special
        shadow="rgba(0, 0, 0, 0.5)",
        overlay="rgba(0, 0, 0, 0.7)",
    )
    
    # AMOLED Theme (Pure black)
    AMOLED = ColorScheme(
        primary="#E63946",
        primary_hover="#FF4757",
        primary_light="#FF6B7A",
        primary_dark="#D62839",
        
        bg_primary="#000000",
        bg_secondary="#0A0A0A",
        bg_tertiary="#141414",
        bg_card="#0A0A0A",
        
        text_primary="#FFFFFF",
        text_secondary="#B0B0B0",
        text_tertiary="#707070",
        text_disabled="#404040",
        
        border_primary="#1A1A1A",
        border_secondary="#0A0A0A",
        border_focus="#E63946",
        
        success="#4CAF50",
        warning="#FFC107",
        error="#F44336",
        info="#2196F3",
        
        shadow="rgba(0, 0, 0, 0.8)",
        overlay="rgba(0, 0, 0, 0.9)",
    )
    
    # Light Theme (For future)
    LIGHT = ColorScheme(
        primary="#E63946",
        primary_hover="#D62839",
        primary_light="#FF6B7A",
        primary_dark="#C52836",
        
        bg_primary="#FFFFFF",
        bg_secondary="#F5F5F5",
        bg_tertiary="#E0E0E0",
        bg_card="#FFFFFF",
        
        text_primary="#000000",
        text_secondary="#5A5A5A",
        text_tertiary="#9E9E9E",
        text_disabled="#BDBDBD",
        
        border_primary="#E0E0E0",
        border_secondary="#F5F5F5",
        border_focus="#E63946",
        
        success="#4CAF50",
        warning="#FFC107",
        error="#F44336",
        info="#2196F3",
        
        shadow="rgba(0, 0, 0, 0.1)",
        overlay="rgba(0, 0, 0, 0.3)",
    )
    
    def __init__(self, mode: ThemeMode = ThemeMode.DARK):
        self.mode = mode
        self._current_scheme = self._get_scheme(mode)
    
    def _get_scheme(self, mode: ThemeMode) -> ColorScheme:
        """Get color scheme by mode"""
        if mode == ThemeMode.DARK:
            return self.DARK
        elif mode == ThemeMode.AMOLED:
            return self.AMOLED
        elif mode == ThemeMode.LIGHT:
            return self.LIGHT
        return self.DARK
    
    @property
    def colors(self) -> ColorScheme:
        """Get current color scheme"""
        return self._current_scheme
    
    def switch_mode(self, mode: ThemeMode):
        """Switch theme mode"""
        self.mode = mode
        self._current_scheme = self._get_scheme(mode)
    
    def get_stylesheet(self, widget_type: str) -> str:
        """Get stylesheet for widget type"""
        c = self.colors
        
        stylesheets = {
            'main_window': f"""
                QMainWindow {{
                    background-color: {c.bg_primary};
                }}
                * {{
                    font-family: "Segoe UI", "Arial", sans-serif;
                }}
                QLabel {{
                    color: {c.text_primary};
                }}
            """,
            
            'card': f"""
                QFrame {{
                    background-color: {c.bg_card};
                    border-left: 4px solid {c.primary};
                    border-radius: 16px;
                }}
                QFrame:hover {{
                    background-color: {c.bg_tertiary};
                }}
            """,
            
            'button_primary': f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {c.primary}, stop:1 {c.primary_hover});
                    color: {c.text_primary};
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    padding: 12px 24px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {c.primary_hover}, stop:1 {c.primary});
                }}
                QPushButton:pressed {{
                    background: {c.primary_dark};
                }}
                QPushButton:disabled {{
                    background: {c.bg_tertiary};
                    color: {c.text_disabled};
                }}
            """,
            
            'button_secondary': f"""
                QPushButton {{
                    background: {c.bg_secondary};
                    color: {c.text_primary};
                    border: 2px solid {c.border_primary};
                    border-radius: 8px;
                    font-weight: 500;
                    padding: 12px 24px;
                }}
                QPushButton:hover {{
                    background: {c.bg_tertiary};
                    border-color: {c.border_focus};
                }}
                QPushButton:pressed {{
                    background: {c.bg_primary};
                }}
            """,
            
            'input': f"""
                QLineEdit, QTextEdit {{
                    background: {c.bg_secondary};
                    border: 2px solid {c.border_primary};
                    border-radius: 8px;
                    color: {c.text_primary};
                    padding: 12px;
                    font-size: 14px;
                }}
                QLineEdit:focus, QTextEdit:focus {{
                    border-color: {c.border_focus};
                }}
            """,
            
            'menu': f"""
                QMenuBar {{
                    background-color: {c.bg_secondary};
                    color: {c.text_primary};
                    border-bottom: 1px solid {c.primary};
                }}
                QMenuBar::item:selected {{
                    background-color: {c.primary};
                }}
                QMenu {{
                    background-color: {c.bg_secondary};
                    color: {c.text_primary};
                    border: 1px solid {c.primary};
                }}
                QMenu::item:selected {{
                    background-color: {c.primary};
                }}
            """,
        }
        
        return stylesheets.get(widget_type, "")


# Global theme instance
_theme_instance: Optional[Theme] = None


def get_theme() -> Theme:
    """Get global theme instance"""
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = Theme(ThemeMode.DARK)
    return _theme_instance


def set_theme_mode(mode: ThemeMode):
    """Set global theme mode"""
    theme = get_theme()
    theme.switch_mode(mode)


if __name__ == "__main__":
    # Test
    print("[TEST] Theme System")
    print("=" * 60)
    
    theme = Theme(ThemeMode.DARK)
    print(f"\nCurrent mode: {theme.mode.value}")
    print(f"Primary color: {theme.colors.primary}")
    print(f"Background: {theme.colors.bg_primary}")
    
    print("\n[TEST] Switch to AMOLED")
    theme.switch_mode(ThemeMode.AMOLED)
    print(f"Background: {theme.colors.bg_primary}")
    
    print("\n[TEST] Get button stylesheet")
    style = theme.get_stylesheet('button_primary')
    print(f"Length: {len(style)} chars")
    
    print("\n" + "=" * 60)
    print("✅ Theme system works!")
