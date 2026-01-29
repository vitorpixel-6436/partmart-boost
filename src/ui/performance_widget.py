#!/usr/bin/env python3
"""Custom Performance Widget with Steam-inspired design

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Package 3.9a Stage 7.3: Integrated with BackendBridge.

Features:
- 100% custom-painted UI (no standard widgets)
- Circular progress indicators
- Performance score display
- Mini sparklines
- Efficiency badges
- Bottleneck warnings
- Gradient color zones
- Smooth animations
- Hardware-accelerated rendering
- Real-time updates via Qt signals
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QConicalGradient, QPainterPath,
    QFontMetrics, QRadialGradient
)
from typing import List, Optional, Deque, Dict, Any
from collections import deque
import math
import time


class PerformanceWidget(QWidget):
    """Custom performance display widget with Steam-inspired design
    
    v0.3.5e (package 3.9a, stage 7.3/7.7) - Integrated with BackendBridge
    
    This widget provides:
    - Circular gauges for CPU/GPU/RAM
    - Performance score (0-100)
    - Efficiency indicators
    - Bottleneck warnings
    - Trend sparklines
    - Smooth animations
    - Real-time updates via Qt signals
    
    Colors:
    - Excellent (>80): #4CAF50 (Green)
    - Good (60-80): #8BC34A (Light Green)
    - Fair (40-60): #FF9800 (Orange)
    - Poor (<40): #F44336 (Red)
    
    Integration:
        >>> from core.app_integrator import AppIntegrator
        >>> 
        >>> integrator = AppIntegrator.get_instance()
        >>> qt_signals = integrator.get_qt_signals()
        >>> 
        >>> widget = PerformanceWidget(qt_signals)
        >>> # Widget automatically receives updates via signals
    """
    
    # Signals
    clicked = pyqtSignal()
    
    def __init__(self, qt_signals=None, parent=None):
        """Initialize performance widget
        
        Args:
            qt_signals: QtSignalBridge instance (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Bridge connection
        self._qt_signals = qt_signals
        
        # Data
        self._score = 0.0
        self._cpu_load = 0.0
        self._gpu_load = 0.0
        self._ram_load = 0.0
        self._cpu_efficiency = 0.0
        self._gpu_efficiency = 0.0
        self._bottleneck = 'none'
        self._bottleneck_severity = 'none'
        
        # History for sparklines (30 samples)
        self._cpu_history: Deque[float] = deque(maxlen=30)
        self._gpu_history: Deque[float] = deque(maxlen=30)
        self._ram_history: Deque[float] = deque(maxlen=30)
        
        # Animation
        self._score_display = 0.0
        self._cpu_display = 0.0
        self._gpu_display = 0.0
        self._ram_display = 0.0
        self._animation_speed = 0.15
        
        # Pulsing effect for bottleneck
        self._pulse_phase = 0.0
        
        # Colors (Steam-inspired)
        self._color_excellent = QColor(76, 175, 80)  # Green
        self._color_good = QColor(139, 195, 74)  # Light green
        self._color_fair = QColor(255, 152, 0)  # Orange
        self._color_poor = QColor(244, 67, 54)  # Red
        self._color_bg = QColor(23, 26, 33)  # Dark blue-gray
        self._color_bg_light = QColor(35, 39, 47)  # Lighter
        self._color_text = QColor(255, 255, 255, 230)  # White
        self._color_text_dim = QColor(255, 255, 255, 150)  # Dimmed
        self._color_border = QColor(255, 255, 255, 30)  # Subtle border
        
        # Fonts
        self._font_large = QFont("Segoe UI", 28, QFont.Weight.Bold)
        self._font_medium = QFont("Segoe UI", 11, QFont.Weight.Normal)
        self._font_small = QFont("Segoe UI", 9, QFont.Weight.Normal)
        self._font_tiny = QFont("Segoe UI", 8, QFont.Weight.Normal)
        
        # Layout
        self.setMinimumSize(320, 280)
        self.setMaximumSize(400, 350)
        
        # Animation timer
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(16)  # 60 FPS
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Connect to signals
        if self._qt_signals:
            self._qt_signals.data_updated.connect(self._on_data_updated)
            print("[PerformanceWidget] Connected to Qt signals")
    
    def _on_data_updated(self, data_type: str, data: Dict[str, Any]):
        """Handle data update from backend (Stage 7.3)
        
        Args:
            data_type: Type of data ('performance_metrics', etc.)
            data: Data dictionary
        """
        if data_type == 'performance_metrics':
            # Extract metrics
            score = data.get('score', 0.0)
            cpu = data.get('cpu', 0.0)
            gpu = data.get('gpu', 0.0)
            ram = data.get('memory', 0.0)  # 'memory' in backend
            
            # Update performance
            self.update_performance(
                score=score,
                cpu=cpu,
                gpu=gpu,
                ram=ram
            )
    
    def update_performance(self, score: float, cpu: float, gpu: float, ram: float,
                          cpu_eff: float = 0.0, gpu_eff: float = 0.0,
                          bottleneck: str = 'none', bottleneck_severity: str = 'none'):
        """Update performance data
        
        Args:
            score: Performance score (0-100)
            cpu: CPU load (0-100)
            gpu: GPU load (0-100)
            ram: RAM usage (0-100)
            cpu_eff: CPU efficiency (FPS per %)
            gpu_eff: GPU efficiency (FPS per %)
            bottleneck: 'cpu', 'gpu', 'ram', or 'none'
            bottleneck_severity: 'low', 'medium', 'high', or 'none'
        """
        self._score = score
        self._cpu_load = cpu
        self._gpu_load = gpu
        self._ram_load = ram
        self._cpu_efficiency = cpu_eff
        self._gpu_efficiency = gpu_eff
        self._bottleneck = bottleneck
        self._bottleneck_severity = bottleneck_severity
        
        # Add to history
        self._cpu_history.append(cpu)
        self._gpu_history.append(gpu)
        self._ram_history.append(ram)
    
    def _animate(self):
        """Animation tick"""
        # Lerp values
        self._score_display += (self._score - self._score_display) * self._animation_speed
        self._cpu_display += (self._cpu_load - self._cpu_display) * self._animation_speed
        self._gpu_display += (self._gpu_load - self._gpu_display) * self._animation_speed
        self._ram_display += (self._ram_load - self._ram_display) * self._animation_speed
        
        # Pulse phase
        self._pulse_phase += 0.05
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase = 0.0
        
        # Update display
        self.update()
    
    def _get_performance_color(self, value: float) -> QColor:
        """Get color based on performance value
        
        Args:
            value: Value (0-100)
        
        Returns:
            QColor
        """
        if value >= 80:
            return self._color_excellent
        elif value >= 60:
            return self._color_good
        elif value >= 40:
            return self._color_fair
        else:
            return self._color_poor
    
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Background
        self._draw_background(painter)
        
        # Performance score (top)
        self._draw_score(painter)
        
        # Circular gauges (CPU/GPU/RAM)
        self._draw_gauges(painter)
        
        # Efficiency badges
        self._draw_efficiency(painter)
        
        # Bottleneck warning
        if self._bottleneck != 'none' and self._bottleneck_severity != 'none':
            self._draw_bottleneck_warning(painter)
    
    def _draw_background(self, painter: QPainter):
        """Draw background with gradient"""
        rect = self.rect()
        
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, self._color_bg_light)
        gradient.setColorAt(1, self._color_bg)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        
        # Border
        painter.setPen(QPen(self._color_border, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 8, 8)
    
    def _draw_score(self, painter: QPainter):
        """Draw performance score"""
        score_text = f"{self._score_display:.0f}"
        score_color = self._get_performance_color(self._score_display)
        
        # Score number
        painter.setFont(self._font_large)
        painter.setPen(QPen(score_color))
        
        fm = QFontMetrics(self._font_large)
        text_width = fm.horizontalAdvance(score_text)
        
        x = (self.width() - text_width) // 2
        y = 40
        
        painter.drawText(x, y, score_text)
        
        # "PERFORMANCE" label
        painter.setFont(self._font_small)
        painter.setPen(QPen(self._color_text_dim))
        
        label = "PERFORMANCE SCORE"
        label_fm = QFontMetrics(self._font_small)
        label_width = label_fm.horizontalAdvance(label)
        label_x = (self.width() - label_width) // 2
        
        painter.drawText(label_x, y + 15, label)
    
    def _draw_gauges(self, painter: QPainter):
        """Draw circular gauges for CPU/GPU/RAM"""
        # Gauge positions
        gauge_y = 90
        gauge_size = 70
        gauge_spacing = 10
        
        total_width = 3 * gauge_size + 2 * gauge_spacing
        start_x = (self.width() - total_width) // 2
        
        # CPU gauge
        self._draw_circular_gauge(
            painter,
            x=start_x,
            y=gauge_y,
            size=gauge_size,
            value=self._cpu_display,
            label="CPU",
            history=list(self._cpu_history),
            highlight=(self._bottleneck == 'cpu')
        )
        
        # GPU gauge
        self._draw_circular_gauge(
            painter,
            x=start_x + gauge_size + gauge_spacing,
            y=gauge_y,
            size=gauge_size,
            value=self._gpu_display,
            label="GPU",
            history=list(self._gpu_history),
            highlight=(self._bottleneck == 'gpu')
        )
        
        # RAM gauge
        self._draw_circular_gauge(
            painter,
            x=start_x + 2 * (gauge_size + gauge_spacing),
            y=gauge_y,
            size=gauge_size,
            value=self._ram_display,
            label="RAM",
            history=list(self._ram_history),
            highlight=(self._bottleneck == 'ram')
        )
    
    def _draw_circular_gauge(self, painter: QPainter, x: int, y: int, size: int,
                            value: float, label: str, history: List[float],
                            highlight: bool = False):
        """Draw a single circular gauge"""
        center_x = x + size // 2
        center_y = y + size // 2
        radius = size // 2 - 5
        
        # Background circle
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Progress arc with gradient
        color = self._get_performance_color(value)
        
        if highlight:
            # Pulsing effect
            pulse = math.sin(self._pulse_phase) * 0.3 + 0.7
            color = QColor(
                int(color.red() * pulse),
                int(color.green() * pulse),
                int(color.blue() * pulse)
            )
        
        # Create conical gradient
        gradient = QConicalGradient(center_x, center_y, 90)
        gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 100))
        gradient.setColorAt(value / 100.0, color)
        gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 50))
        
        # Draw arc
        pen = QPen(QBrush(gradient), 6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        span_angle = int(value * 360 / 100)
        painter.drawArc(
            center_x - radius, center_y - radius,
            radius * 2, radius * 2,
            90 * 16,  # Start angle (top)
            -span_angle * 16  # Span angle (clockwise)
        )
        
        # Value text
        painter.setFont(self._font_medium)
        painter.setPen(QPen(self._color_text))
        
        value_text = f"{value:.0f}"
        fm = QFontMetrics(self._font_medium)
        text_width = fm.horizontalAdvance(value_text)
        text_x = center_x - text_width // 2
        text_y = center_y + 5
        
        painter.drawText(text_x, text_y, value_text)
        
        # Label
        painter.setFont(self._font_tiny)
        painter.setPen(QPen(self._color_text_dim))
        
        label_fm = QFontMetrics(self._font_tiny)
        label_width = label_fm.horizontalAdvance(label)
        label_x = center_x - label_width // 2
        label_y = y + size + 12
        
        painter.drawText(label_x, label_y, label)
        
        # Mini sparkline below label
        if len(history) > 1:
            self._draw_mini_sparkline(
                painter,
                x=x,
                y=label_y + 5,
                width=size,
                height=15,
                data=history
            )
    
    def _draw_mini_sparkline(self, painter: QPainter, x: int, y: int,
                            width: int, height: int, data: List[float]):
        """Draw mini sparkline graph"""
        if len(data) < 2:
            return
        
        # Scale data
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val > min_val else 1.0
        
        # Create path
        path = QPainterPath()
        step = width / (len(data) - 1)
        
        for i, val in enumerate(data):
            px = x + i * step
            py = y + height - ((val - min_val) / range_val) * height
            
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)
        
        # Draw
        painter.setPen(QPen(self._color_text_dim, 1))
        painter.drawPath(path)
    
    def _draw_efficiency(self, painter: QPainter):
        """Draw efficiency badges"""
        y = 200
        
        painter.setFont(self._font_tiny)
        painter.setPen(QPen(self._color_text_dim))
        
        # CPU efficiency
        cpu_eff_text = f"CPU: {self._cpu_efficiency:.1f} FPS/%"
        painter.drawText(20, y, cpu_eff_text)
        
        # GPU efficiency
        gpu_eff_text = f"GPU: {self._gpu_efficiency:.1f} FPS/%"
        painter.drawText(self.width() // 2 + 10, y, gpu_eff_text)
    
    def _draw_bottleneck_warning(self, painter: QPainter):
        """Draw bottleneck warning"""
        # Pulsing effect
        pulse = math.sin(self._pulse_phase) * 0.5 + 0.5
        alpha = int(150 + pulse * 105)  # 150-255
        
        y = self.height() - 35
        
        # Icon
        painter.setFont(self._font_medium)
        painter.setPen(QPen(QColor(255, 152, 0, alpha)))  # Orange
        painter.drawText(15, y, "⚠")
        
        # Text
        painter.setFont(self._font_small)
        
        severity_colors = {
            'low': QColor(255, 193, 7, alpha),  # Yellow
            'medium': QColor(255, 152, 0, alpha),  # Orange
            'high': QColor(244, 67, 54, alpha),  # Red
        }
        
        color = severity_colors.get(self._bottleneck_severity, self._color_text_dim)
        painter.setPen(QPen(color))
        
        text = f"Bottleneck: {self._bottleneck.upper()} ({self._bottleneck_severity})"
        painter.drawText(40, y, text)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
