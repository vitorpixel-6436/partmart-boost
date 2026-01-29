#!/usr/bin/env python3
"""Slide Animation

Version: 0.3.5e (Package 3.9a, Stage 7.8a)
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtWidgets import QWidget


class SlideAnimation:
    """Slide animation"""
    
    @staticmethod
    def slide_in(widget: QWidget, direction: str = 'left', duration: int = 350):
        """Slide widget in
        
        Args:
            direction: 'left', 'right', 'up', 'down'
        """
        start_pos = widget.pos()
        
        if direction == 'left':
            widget.move(start_pos.x() - 300, start_pos.y())
        elif direction == 'right':
            widget.move(start_pos.x() + 300, start_pos.y())
        elif direction == 'up':
            widget.move(start_pos.x(), start_pos.y() - 300)
        elif direction == 'down':
            widget.move(start_pos.x(), start_pos.y() + 300)
        
        anim = QPropertyAnimation(widget, b'pos')
        anim.setDuration(duration)
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        
        return anim
