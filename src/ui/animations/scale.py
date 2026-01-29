#!/usr/bin/env python3
"""Scale Animation

Version: 0.3.5e (Package 3.9a, Stage 7.8a)
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtWidgets import QWidget


class ScaleAnimation:
    """Scale animation"""
    
    @staticmethod
    def scale_up(widget: QWidget, duration: int = 250):
        """Scale widget up"""
        original_size = widget.size()
        small_size = QSize(int(original_size.width() * 0.8), 
                          int(original_size.height() * 0.8))
        
        widget.resize(small_size)
        
        anim = QPropertyAnimation(widget, b'size')
        anim.setDuration(duration)
        anim.setEndValue(original_size)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        anim.start()
        
        return anim
