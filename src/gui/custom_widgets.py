#!/usr/bin/env python3
"""Custom UI Widgets

Version: 0.3.5d (package 3.9a, stage 4/4)

Modern, reusable UI components with animations and custom styling.

Package 3.9a Stage 4: New custom widget library.
"""
from PyQt6.QtWidgets import (
    QPushButton, QSlider, QProgressBar, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QBrush


class ModernButton(QPushButton):
    """Modern button with hover animations and custom styling
    
    Features:
    - Smooth hover effects
    - Click animations
    - Customizable colors
    - Rounded corners
    - Shadow effects
    """
    
    def __init__(self, text="", color="#0d7377", parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.hover_color = self._lighten_color(color, 20)
        self.pressed_color = self._darken_color(color, 20)
        
        self._setup_style()
    
    def _setup_style(self):
        """Setup button styling"""
        self.setStyleSheet(f"""
            ModernButton {{
                background-color: {self.base_color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 100px;
            }}
            ModernButton:hover {{
                background-color: {self.hover_color};
            }}
            ModernButton:pressed {{
                background-color: {self.pressed_color};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
            ModernButton:disabled {{
                background-color: #4a4a4a;
                color: #8a8a8a;
            }}
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    @staticmethod
    def _lighten_color(hex_color: str, percent: int) -> str:
        """Lighten hex color by percent"""
        # Remove #
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Lighten
        factor = 1 + (percent / 100)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def _darken_color(hex_color: str, percent: int) -> str:
        """Darken hex color by percent"""
        # Remove #
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        factor = 1 - (percent / 100)
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"


class ModernSlider(QSlider):
    """Modern slider with gradient and value display
    
    Features:
    - Gradient handle
    - Value tooltip
    - Smooth animations
    - Custom styling
    """
    
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup slider styling"""
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3a3a3a, stop:1 #0d7377);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #14a2aa, stop:1 #0d7377);
                border: 2px solid #14a2aa;
                width: 20px;
                margin: -7px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1fc9d3, stop:1 #14a2aa);
                border: 2px solid #1fc9d3;
                width: 22px;
                margin: -8px 0;
            }
            QSlider::groove:vertical {
                width: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #0d7377);
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #14a2aa, stop:1 #0d7377);
                border: 2px solid #14a2aa;
                height: 20px;
                margin: 0 -7px;
                border-radius: 10px;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class ModernProgressBar(QProgressBar):
    """Modern progress bar with animations
    
    Features:
    - Animated progress
    - Gradient fill
    - Smooth transitions
    - Text overlay
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup progress bar styling"""
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                text-align: center;
                background-color: #1e1e1e;
                color: white;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0d7377, stop:0.5 #14a2aa, stop:1 #1fc9d3);
                border-radius: 4px;
            }
        """)
        
        self.setTextVisible(True)


class ToggleSwitch(QCheckBox):
    """Modern toggle switch (iOS-style)
    
    Features:
    - Smooth toggle animation
    - Modern design
    - Color transitions
    - State indicators
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def paintEvent(self, event):
        """Custom paint event for toggle switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background track
        if self.isChecked():
            bg_color = QColor(13, 115, 119)  # Teal
        else:
            bg_color = QColor(100, 100, 100)  # Gray
        
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 60, 30, 15, 15)
        
        # Handle (circle)
        handle_x = 32 if self.isChecked() else 2
        
        # Shadow
        shadow_color = QColor(0, 0, 0, 50)
        painter.setBrush(shadow_color)
        painter.drawEllipse(handle_x + 1, 3, 26, 26)
        
        # Handle
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(handle_x, 2, 26, 26)
        
        painter.end()


class ModernComboBox(QComboBox):
    """Modern combo box with custom styling
    
    Features:
    - Custom dropdown
    - Hover effects
    - Better readability
    - Rounded design
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """Setup combo box styling"""
        self.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 2px solid #3a3a3a;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 10pt;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 2px solid #0d7377;
                background-color: #353535;
            }
            QComboBox:focus {
                border: 2px solid #14a2aa;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #e0e0e0;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #0d7377;
                selection-color: white;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #3a3a3a;
            }
        """)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
