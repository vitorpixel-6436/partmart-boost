#!/usr/bin/env python3
"""Custom FPS Widget with Steam-inspired design

Version: 0.3.5e - Package 3.1

Features:
- Custom-painted UI (no standard widgets)
- Real-time FPS display (large digits)
- Frame time sparkline graph
- 1% low / 0.1% low indicators
- Stuttering warnings
- Color-coded performance
- Smooth animations
- Hardware-accelerated rendering
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QPainterPath, QFontMetrics
)
from typing import List, Optional
import time


class FPSWidget(QWidget):
    """Custom FPS display widget with Steam-inspired design
    
    v0.3.5e Package 3.1 - 100% custom UI
    
    This widget provides:
    - Large FPS number with color coding
    - Mini sparkline graph of frame times
    - 1% low and 0.1% low indicators
    - Stuttering warnings
    - Smooth animations
    
    Colors:
    - Green (>60 FPS): #4CAF50
    - Yellow (30-60 FPS): #FFC107
    - Red (<30 FPS): #F44336
    
    Example:
        >>> widget = FPSWidget()
        >>> widget.update_fps(fps=72.3, fps_1_low=65.1, fps_0_1_low=58.7)
        >>> widget.update_frame_times([16.2, 16.5, 16.1, 16.8, ...])
    """
    
    # Signals
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data
        self._fps = 0.0
        self._fps_1_low = 0.0
        self._fps_0_1_low = 0.0
        self._frame_times: List[float] = []
        self._stutter_count = 0
        self._last_update = time.time()
        
        # Animation
        self._fps_display = 0.0  # Smoothed FPS for display
        self._animation_speed = 0.15  # Lerp speed
        
        # Colors (Steam-inspired)
        self._color_excellent = QColor(76, 175, 80)  # Green
        self._color_good = QColor(139, 195, 74)  # Light green
        self._color_okay = QColor(255, 193, 7)  # Yellow
        self._color_poor = QColor(244, 67, 54)  # Red
        self._color_bg = QColor(23, 26, 33)  # Dark blue-gray
        self._color_text = QColor(255, 255, 255, 230)  # White
        self._color_text_dim = QColor(255, 255, 255, 150)  # Dimmed white
        self._color_graph = QColor(158, 158, 158, 100)  # Graph line
        
        # Fonts
        self._font_large = QFont("Segoe UI", 32, QFont.Weight.Bold)
        self._font_medium = QFont("Segoe UI", 10, QFont.Weight.Normal)
        self._font_small = QFont("Segoe UI", 8, QFont.Weight.Normal)
        
        # Layout
        self.setMinimumSize(200, 120)
        self.setMaximumSize(300, 150)
        
        # Animation timer
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(16)  # 60 FPS
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def update_fps(self, fps: float, fps_1_low: float = 0.0, fps_0_1_low: float = 0.0, stutter_count: int = 0):
        """Update FPS values
        
        Args:
            fps: Current average FPS
            fps_1_low: 1% low FPS
            fps_0_1_low: 0.1% low FPS
            stutter_count: Number of stutters detected
        """
        self._fps = fps
        self._fps_1_low = fps_1_low
        self._fps_0_1_low = fps_0_1_low
        self._stutter_count = stutter_count
        self._last_update = time.time()
    
    def update_frame_times(self, frame_times: List[float]):
        """Update frame time history for sparkline
        
        Args:
            frame_times: List of frame times (ms)
        """
        self._frame_times = frame_times[-60:]  # Keep last 60 frames
    
    def _animate(self):
        """Animation tick (smooth FPS interpolation)"""
        # Lerp FPS display toward target
        diff = self._fps - self._fps_display
        self._fps_display += diff * self._animation_speed
        
        # Update if changed
        if abs(diff) > 0.01:
            self.update()
    
    def _get_fps_color(self, fps: float) -> QColor:
        """Get color based on FPS value
        
        Args:
            fps: FPS value
        
        Returns:
            QColor for FPS display
        """
        if fps >= 60:
            return self._color_excellent
        elif fps >= 45:
            return self._color_good
        elif fps >= 30:
            return self._color_okay
        else:
            return self._color_poor
    
    def paintEvent(self, event):
        """Custom paint event
        
        Draws:
        - Background with gradient
        - Large FPS number
        - 1% low / 0.1% low indicators
        - Frame time sparkline
        - Stuttering warnings
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Background
        self._draw_background(painter)
        
        # FPS number (large)
        self._draw_fps_number(painter)
        
        # Low FPS indicators
        self._draw_low_fps_indicators(painter)
        
        # Sparkline graph
        if self._frame_times:
            self._draw_sparkline(painter)
        
        # Stuttering warning
        if self._stutter_count > 0:
            self._draw_stutter_warning(painter)
    
    def _draw_background(self, painter: QPainter):
        """Draw background with gradient"""
        rect = self.rect()
        
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(35, 39, 47))  # Lighter at top
        gradient.setColorAt(1, self._color_bg)  # Darker at bottom
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        
        # Subtle border
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 8, 8)
    
    def _draw_fps_number(self, painter: QPainter):
        """Draw large FPS number"""
        fps_text = f"{self._fps_display:.0f}"
        fps_color = self._get_fps_color(self._fps_display)
        
        # FPS number
        painter.setFont(self._font_large)
        painter.setPen(QPen(fps_color))
        
        # Center in upper portion
        fm = QFontMetrics(self._font_large)
        text_width = fm.horizontalAdvance(fps_text)
        text_height = fm.height()
        
        x = (self.width() - text_width) // 2
        y = 45  # From top
        
        painter.drawText(x, y, fps_text)
        
        # "FPS" label
        painter.setFont(self._font_small)
        painter.setPen(QPen(self._color_text_dim))
        
        label_fm = QFontMetrics(self._font_small)
        label_width = label_fm.horizontalAdvance("FPS")
        label_x = (self.width() - label_width) // 2
        
        painter.drawText(label_x, y + 15, "FPS")
    
    def _draw_low_fps_indicators(self, painter: QPainter):
        """Draw 1% low and 0.1% low FPS"""
        painter.setFont(self._font_small)
        painter.setPen(QPen(self._color_text_dim))
        
        # 1% low
        text_1_low = f"1%: {self._fps_1_low:.0f}"
        painter.drawText(10, self.height() - 30, text_1_low)
        
        # 0.1% low
        text_0_1_low = f"0.1%: {self._fps_0_1_low:.0f}"
        painter.drawText(10, self.height() - 15, text_0_1_low)
    
    def _draw_sparkline(self, painter: QPainter):
        """Draw frame time sparkline graph"""
        if not self._frame_times:
            return
        
        # Graph area (right side, middle)
        graph_x = self.width() - 90
        graph_y = 60
        graph_width = 80
        graph_height = 40
        
        # Find min/max for scaling
        min_ft = min(self._frame_times)
        max_ft = max(self._frame_times)
        range_ft = max_ft - min_ft if max_ft > min_ft else 1.0
        
        # Draw graph background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        painter.drawRoundedRect(graph_x - 2, graph_y - 2, graph_width + 4, graph_height + 4, 3, 3)
        
        # Draw sparkline
        if len(self._frame_times) > 1:
            path = QPainterPath()
            
            step = graph_width / (len(self._frame_times) - 1)
            
            # Start path
            first_ft = self._frame_times[0]
            first_y = graph_y + graph_height - ((first_ft - min_ft) / range_ft) * graph_height
            path.moveTo(graph_x, first_y)
            
            # Draw line through all points
            for i, ft in enumerate(self._frame_times):
                x = graph_x + i * step
                y = graph_y + graph_height - ((ft - min_ft) / range_ft) * graph_height
                path.lineTo(x, y)
            
            # Draw path
            painter.setPen(QPen(self._color_graph, 1.5))
            painter.drawPath(path)
        
        # Label
        painter.setFont(self._font_small)
        painter.setPen(QPen(self._color_text_dim))
        painter.drawText(graph_x, graph_y - 5, "Frame Time")
    
    def _draw_stutter_warning(self, painter: QPainter):
        """Draw stuttering warning indicator"""
        # Blink effect
        blink = int(time.time() * 2) % 2 == 0
        if not blink:
            return
        
        painter.setFont(self._font_small)
        painter.setPen(QPen(self._color_poor))
        
        text = f"⚠ {self._stutter_count} stutters"
        fm = QFontMetrics(self._font_small)
        text_width = fm.horizontalAdvance(text)
        
        x = self.width() - text_width - 10
        y = self.height() - 10
        
        painter.drawText(x, y, text)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


# ========== TESTING ==========

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    import sys
    import random
    
    print("="*60)
    print("FPSWidget v0.3.5e Package 3.1 Test")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    # Main window
    window = QMainWindow()
    window.setWindowTitle("FPS Widget Test")
    window.setStyleSheet("background-color: #1a1d24;")
    
    # Central widget
    central = QWidget()
    layout = QVBoxLayout(central)
    
    # FPS widget
    fps_widget = FPSWidget()
    layout.addWidget(fps_widget)
    
    window.setCentralWidget(central)
    window.resize(400, 300)
    window.show()
    
    # Simulate FPS updates
    def update_fps():
        # Simulate varying FPS
        base_fps = 60 + random.uniform(-10, 10)
        fps_1_low = base_fps * random.uniform(0.85, 0.95)
        fps_0_1_low = base_fps * random.uniform(0.75, 0.85)
        
        # Random stutters
        stutter_count = random.randint(0, 3) if random.random() < 0.1 else 0
        
        # Generate frame times
        frame_time = 1000.0 / base_fps
        frame_times = [frame_time + random.uniform(-2, 2) for _ in range(60)]
        
        # Update widget
        fps_widget.update_fps(base_fps, fps_1_low, fps_0_1_low, stutter_count)
        fps_widget.update_frame_times(frame_times)
    
    # Update timer
    timer = QTimer()
    timer.timeout.connect(update_fps)
    timer.start(100)  # Update every 100ms
    
    print("\n✅ FPSWidget displaying!")
    print("  - Custom-painted UI")
    print("  - Real-time FPS display")
    print("  - Sparkline graph")
    print("  - Low FPS indicators")
    print("  - Stuttering warnings")
    print("\nClose window to exit.")
    
    sys.exit(app.exec())
