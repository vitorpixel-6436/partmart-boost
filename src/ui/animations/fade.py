#!/usr/bin/env python3
"""Fade Animation

Version: 0.3.5e (Package 3.9a, Stage 7.8a)
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget


class FadeAnimation:
    """Fade in/out animation"""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 250):
        """Fade widget in"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b'opacity')
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        
        return anim
    
    @staticmethod
    def fade_out(widget: QWidget, duration: int = 250):
        """Fade widget out"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b'opacity')
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.start()
        
        return anim
