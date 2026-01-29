#!/usr/bin/env python3
"""Glass Panel Widget

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

Frosted glass panel container with:
- Translucent background
- Blur effect simulation
- Smooth borders
- Apple-inspired glassmorphism
"""
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPen


class GlassPanel(QFrame):
    """Glassmorphism panel widget"""
    
    def __init__(self, opacity: float = 0.85, radius: int = 12, parent=None):
        super().__init__(parent)
        self.opacity = opacity
        self.radius = radius
        
        # Make background transparent for custom paint
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
    
    def paintEvent(self, event):
        """Custom paint for glass effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 
                           self.radius, self.radius)
        
        # Glass background
        alpha = int(255 * self.opacity)
        bg_color = QColor(10, 10, 10, alpha)
        painter.fillPath(path, bg_color)
        
        # Border
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawPath(path)
        
        super().paintEvent(event)
