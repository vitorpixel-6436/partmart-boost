#!/usr/bin/env python3
"""Modern Button Widget

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

Beautiful animated button with:
- Smooth hover effects
- Click animations
- Icon support
- MSI red accent
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QColor


class ModernButton(QPushButton):
    """Modern animated button"""
    
    def __init__(self, text: str, primary: bool = False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._hover_progress = 0.0
        
        if primary:
            self.setProperty('class', 'primary')
        
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._setup_animations()
    
    def _setup_animations(self):
        """Setup hover animation"""
        self._hover_anim = QPropertyAnimation(self, b'hoverProgress')
        self._hover_anim.setDuration(250)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def enterEvent(self, event):
        """Start hover animation"""
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """End hover animation"""
        self._hover_anim.stop()
        self._hover_anim.setStartValue(self._hover_progress)
        self._hover_anim.setEndValue(0.0)
        self._hover_anim.start()
        super().leaveEvent(event)
    
    @pyqtProperty(float)
    def hoverProgress(self):
        return self._hover_progress
    
    @hoverProgress.setter
    def hoverProgress(self, value):
        self._hover_progress = value
        self.update()
