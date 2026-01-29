#!/usr/bin/env python3
"""Status Indicator Widget

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

Animated status dot with:
- Pulsing effect
- Color coding
- Smooth animations
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient


class StatusIndicator(QWidget):
    """Animated status indicator dot"""
    
    def __init__(self, status: str = 'inactive', parent=None):
        super().__init__(parent)
        self.status = status
        self._pulse = 0.0
        
        self.setFixedSize(16, 16)
        
        # Pulsing animation
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(50)
    
    def _update_pulse(self):
        """Update pulse animation"""
        self._pulse = (self._pulse + 0.05) % 1.0
        self.update()
    
    def paintEvent(self, event):
        """Paint status dot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color based on status
        colors = {
            'active': QColor(0, 214, 57),
            'warning': QColor(255, 184, 0),
            'error': QColor(227, 6, 19),
            'inactive': QColor(100, 100, 100),
        }
        color = colors.get(self.status, colors['inactive'])
        
        # Pulsing effect
        pulse_size = 1.0 + (self._pulse * 0.3)
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = 5 * pulse_size
        
        # Gradient glow
        gradient = QRadialGradient(center_x, center_y, radius)
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), 
                           int(radius * 2), int(radius * 2))
    
    def set_status(self, status: str):
        """Update status"""
        self.status = status
        self.update()
