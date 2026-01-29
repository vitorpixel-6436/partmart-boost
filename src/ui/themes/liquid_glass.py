#!/usr/bin/env python3
"""Liquid Glass Theme

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

Modern glassmorphism theme inspired by:
- Apple macOS Big Sur/Sonoma (frosted glass)
- Steam Big Picture (smooth cards)
- Spotify (clean, modern)
- MSI (aggressive red/black aesthetic)

Features:
- Frosted glass panels with blur
- Soft rounded corners on cards
- Sharp angular base layout
- Smooth animations
- MSI color palette
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEasingCurve
from .msi_colors import MSIColors


class LiquidGlassTheme:
    """Liquid Glass theme configuration"""
    
    # Border radius values
    RADIUS_SHARP = 0
    RADIUS_SMALL = 4
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_SOFT = 16
    RADIUS_PILL = 999
    
    # Animation durations (ms)
    ANIM_FAST = 150
    ANIM_NORMAL = 250
    ANIM_SLOW = 350
    
    # Animation easings
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN = QEasingCurve.Type.InCubic
    
    # Shadows
    SHADOW_SMALL = '0 2px 8px rgba(0, 0, 0, 0.3)'
    SHADOW_MEDIUM = '0 4px 16px rgba(0, 0, 0, 0.4)'
    SHADOW_LARGE = '0 8px 32px rgba(0, 0, 0, 0.5)'
    SHADOW_GLOW_RED = '0 0 20px rgba(227, 6, 19, 0.5)'
    
    # Blur amounts (for glass effects)
    BLUR_SUBTLE = 10
    BLUR_MEDIUM = 20
    BLUR_STRONG = 30
    
    @staticmethod
    def get_stylesheet() -> str:
        """Generate complete QSS stylesheet"""
        c = MSIColors
        
        return f"""
        /* ===== GLOBAL STYLES ===== */
        QWidget {{
            background-color: {c.BG_PRIMARY};
            color: {c.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        
        /* ===== MAIN WINDOW ===== */
        QMainWindow {{
            background: {c.GRADIENT_DARK};
        }}
        
        /* ===== GLASS PANELS ===== */
        .glass-panel {{
            background: {c.GLASS_DARK};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 12px;
        }}
        
        .glass-panel-light {{
            background: {c.GLASS_LIGHT};
            border: 1px solid {c.GRAY_BORDER};
            border-radius: 12px;
        }}
        
        /* ===== GAME CARDS ===== */
        .game-card {{
            background: {c.BG_SECONDARY};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 16px;
            padding: 12px;
        }}
        
        .game-card:hover {{
            background: {c.BG_TERTIARY};
            border-color: {c.RED_PRIMARY};
        }}
        
        /* ===== BUTTONS ===== */
        QPushButton {{
            background: {c.BG_TERTIARY};
            color: {c.TEXT_PRIMARY};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }}
        
        QPushButton:hover {{
            background: {c.BG_ELEVATED};
            border-color: {c.RED_PRIMARY};
        }}
        
        QPushButton:pressed {{
            background: {c.BG_SECONDARY};
        }}
        
        /* Primary button (Red MSI style) */
        QPushButton.primary {{
            background: {c.GRADIENT_RED};
            border: none;
            color: white;
        }}
        
        QPushButton.primary:hover {{
            background: {c.RED_HOVER};
        }}
        
        QPushButton.primary:pressed {{
            background: {c.RED_PRESSED};
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            background: transparent;
            color: {c.TEXT_PRIMARY};
        }}
        
        QLabel.heading {{
            font-size: 24px;
            font-weight: 700;
            color: {c.TEXT_PRIMARY};
        }}
        
        QLabel.subheading {{
            font-size: 18px;
            font-weight: 600;
            color: {c.TEXT_SECONDARY};
        }}
        
        QLabel.caption {{
            font-size: 11px;
            color: {c.TEXT_TERTIARY};
        }}
        
        /* ===== SCROLLBARS ===== */
        QScrollBar:vertical {{
            background: {c.BG_SECONDARY};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {c.GRAY_SHARP};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {c.RED_PRIMARY};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background: {c.BG_SECONDARY};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {c.GRAY_SHARP};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {c.RED_PRIMARY};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            background: {c.BG_SECONDARY};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            padding: 8px;
        }}
        
        QTabBar::tab {{
            background: {c.BG_TERTIARY};
            color: {c.TEXT_SECONDARY};
            border: 1px solid {c.GRAY_SHARP};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 10px 20px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:hover {{
            background: {c.BG_ELEVATED};
            color: {c.TEXT_PRIMARY};
        }}
        
        QTabBar::tab:selected {{
            background: {c.BG_SECONDARY};
            color: {c.RED_PRIMARY};
            border-bottom: 2px solid {c.RED_PRIMARY};
        }}
        
        /* ===== INPUT FIELDS ===== */
        QLineEdit, QTextEdit {{
            background: {c.BG_TERTIARY};
            color: {c.TEXT_PRIMARY};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            padding: 8px 12px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {c.RED_PRIMARY};
        }}
        
        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            background: {c.BG_TERTIARY};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            height: 20px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background: {c.GRADIENT_RED};
            border-radius: 7px;
        }}
        
        /* ===== TOOLTIPS ===== */
        QToolTip {{
            background: {c.GLASS_DARK};
            color: {c.TEXT_PRIMARY};
            border: 1px solid {c.RED_PRIMARY};
            border-radius: 4px;
            padding: 6px 10px;
        }}
        
        /* ===== MENU ===== */
        QMenu {{
            background: {c.GLASS_DARK};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QMenu::item {{
            background: transparent;
            color: {c.TEXT_PRIMARY};
            padding: 8px 20px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background: {c.RED_PRIMARY};
        }}
        
        /* ===== STATUS BAR ===== */
        QStatusBar {{
            background: {c.BG_SECONDARY};
            color: {c.TEXT_SECONDARY};
            border-top: 1px solid {c.GRAY_SHARP};
        }}
        
        /* ===== COMBO BOX ===== */
        QComboBox {{
            background: {c.BG_TERTIARY};
            color: {c.TEXT_PRIMARY};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            padding: 6px 12px;
        }}
        
        QComboBox:hover {{
            border-color: {c.RED_PRIMARY};
        }}
        
        QComboBox::drop-down {{
            border: none;
        }}
        
        QComboBox QAbstractItemView {{
            background: {c.GLASS_DARK};
            border: 1px solid {c.GRAY_SHARP};
            border-radius: 8px;
            selection-background-color: {c.RED_PRIMARY};
        }}
        """


def apply_theme(app: QApplication) -> None:
    """Apply Liquid Glass theme to application"""
    theme = LiquidGlassTheme()
    app.setStyleSheet(theme.get_stylesheet())
    
    # Set application-wide font
    from PyQt6.QtGui import QFont
    font = QFont('Segoe UI', 13)
    app.setFont(font)
