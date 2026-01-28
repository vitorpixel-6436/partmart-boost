#!/usr/bin/env python3
"""Custom Temperature Widget with thermometer-style design

Version: 0.3.5d_package3.2c

Features:
- Vertical thermometer bars
- Gradient temperature zones
- Multi-sensor display (CPU/GPU/Hotspot)
- Temperature history sparklines
- Warning indicators
- Status badges
- Smooth animations
- Glass-effect rendering
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush,
    QLinearGradient, QPainterPath, QFontMetrics
)
from typing import List, Optional, Dict, Deque
from collections import deque
import math
import time


class TemperatureWidget(QWidget):
    """Custom temperature display widget with thermometer design
    
    v0.3.5d_package3.2c - 100% custom UI
    
    This widget provides:
    - Vertical thermometer bars
    - Gradient temperature zones
    - Multi-sensor support
    - Warning indicators
    - Thermal status
    - Smooth animations
    
    Temperature Zones:
    - Cool (<40°C): #2196F3 (Blue)
    - Normal (40-60°C): #4CAF50 (Green)
    - Warm (60-75°C): #FFC107 (Yellow)
    - Hot (75-85°C): #FF9800 (Orange)
    - Critical (>85°C): #F44336 (Red)
    
    Example:
        >>> widget = TemperatureWidget()
        >>> widget.update_temperatures(
        >>>     cpu=65.5,
        >>>     gpu=70.2,
        >>>     gpu_hotspot=78.5
        >>> )
    """
    
    # Signals
    clicked = pyqtSignal()
    temperature_warning = pyqtSignal(str, float)  # sensor, temp
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Data
        self._cpu_temp: Optional[float] = None
        self._gpu_temp: Optional[float] = None
        self._gpu_hotspot: Optional[float] = None
        
        # Display values (smoothed)
        self._cpu_display = 0.0
        self._gpu_display = 0.0
        self._hotspot_display = 0.0
        
        # Max tracking
        self._cpu_max = 0.0
        self._gpu_max = 0.0
        self._hotspot_max = 0.0
        
        # History (30 samples)
        self._cpu_history: Deque[float] = deque(maxlen=30)
        self._gpu_history: Deque[float] = deque(maxlen=30)
        self._hotspot_history: Deque[float] = deque(maxlen=30)
        
        # Animation
        self._animation_speed = 0.15
        self._pulse_phase = 0.0
        
        # Warning state
        self._warning_active = False
        self._last_warning_time = 0
        
        # Colors (Temperature zones)
        self._color_cool = QColor(33, 150, 243)  # Blue
        self._color_normal = QColor(76, 175, 80)  # Green
        self._color_warm = QColor(255, 193, 7)  # Yellow
        self._color_hot = QColor(255, 152, 0)  # Orange
        self._color_critical = QColor(244, 67, 54)  # Red
        self._color_bg = QColor(23, 26, 33)  # Dark
        self._color_bg_light = QColor(35, 39, 47)
        self._color_text = QColor(255, 255, 255, 230)
        self._color_text_dim = QColor(255, 255, 255, 150)
        self._color_border = QColor(255, 255, 255, 30)
        
        # Fonts
        self._font_large = QFont("Segoe UI", 20, QFont.Weight.Bold)
        self._font_medium = QFont("Segoe UI", 11, QFont.Weight.Normal)
        self._font_small = QFont("Segoe UI", 9, QFont.Weight.Normal)
        self._font_tiny = QFont("Segoe UI", 8, QFont.Weight.Normal)
        
        # Layout
        self.setMinimumSize(280, 240)
        self.setMaximumSize(350, 300)
        
        # Animation timer
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start(16)  # 60 FPS
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def update_temperatures(self, cpu: Optional[float] = None,
                          gpu: Optional[float] = None,
                          gpu_hotspot: Optional[float] = None):
        """Update temperature values
        
        Args:
            cpu: CPU temperature (°C)
            gpu: GPU temperature (°C)
            gpu_hotspot: GPU hotspot temperature (°C)
        """
        # Update values
        if cpu is not None:
            self._cpu_temp = cpu
            self._cpu_max = max(self._cpu_max, cpu)
            self._cpu_history.append(cpu)
            
            # Warning check
            if cpu >= 85:
                self._emit_warning('CPU', cpu)
        
        if gpu is not None:
            self._gpu_temp = gpu
            self._gpu_max = max(self._gpu_max, gpu)
            self._gpu_history.append(gpu)
            
            if gpu >= 85:
                self._emit_warning('GPU', gpu)
        
        if gpu_hotspot is not None:
            self._gpu_hotspot = gpu_hotspot
            self._hotspot_max = max(self._hotspot_max, gpu_hotspot)
            self._hotspot_history.append(gpu_hotspot)
            
            if gpu_hotspot >= 90:
                self._emit_warning('GPU Hotspot', gpu_hotspot)
    
    def _emit_warning(self, sensor: str, temp: float):
        """Emit temperature warning
        
        Args:
            sensor: Sensor name
            temp: Temperature value
        """
        current_time = time.time()
        if current_time - self._last_warning_time > 5.0:  # Throttle warnings
            self._warning_active = True
            self.temperature_warning.emit(sensor, temp)
            self._last_warning_time = current_time
    
    def _animate(self):
        """Animation tick"""
        # Lerp temperatures
        if self._cpu_temp is not None:
            self._cpu_display += (self._cpu_temp - self._cpu_display) * self._animation_speed
        
        if self._gpu_temp is not None:
            self._gpu_display += (self._gpu_temp - self._gpu_display) * self._animation_speed
        
        if self._gpu_hotspot is not None:
            self._hotspot_display += (self._gpu_hotspot - self._hotspot_display) * self._animation_speed
        
        # Pulse phase
        self._pulse_phase += 0.05
        if self._pulse_phase > 2 * math.pi:
            self._pulse_phase = 0.0
        
        # Update display
        self.update()
    
    def _get_temp_color(self, temp: float) -> QColor:
        """Get color based on temperature
        
        Args:
            temp: Temperature value
        
        Returns:
            QColor
        """
        if temp >= 85:
            return self._color_critical
        elif temp >= 75:
            return self._color_hot
        elif temp >= 60:
            return self._color_warm
        elif temp >= 40:
            return self._color_normal
        else:
            return self._color_cool
    
    def _get_thermal_status(self) -> tuple[str, QColor]:
        """Get overall thermal status
        
        Returns:
            Tuple of (status_text, color)
        """
        temps = []
        if self._cpu_temp is not None:
            temps.append(self._cpu_temp)
        if self._gpu_temp is not None:
            temps.append(self._gpu_temp)
        if self._gpu_hotspot is not None:
            temps.append(self._gpu_hotspot)
        
        if not temps:
            return ("No Data", self._color_text_dim)
        
        max_temp = max(temps)
        
        if max_temp >= 85:
            return ("CRITICAL", self._color_critical)
        elif max_temp >= 75:
            return ("HOT", self._color_hot)
        elif max_temp >= 60:
            return ("WARM", self._color_warm)
        else:
            return ("NORMAL", self._color_normal)
    
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # Background
        self._draw_background(painter)
        
        # Title
        self._draw_title(painter)
        
        # Thermometers
        self._draw_thermometers(painter)
        
        # Thermal status
        self._draw_status(painter)
    
    def _draw_background(self, painter: QPainter):
        """Draw background with gradient"""
        rect = self.rect()
        
        # Gradient
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
    
    def _draw_title(self, painter: QPainter):
        """Draw title"""
        painter.setFont(self._font_medium)
        painter.setPen(QPen(self._color_text))
        
        painter.drawText(15, 25, "🌡️ TEMPERATURES")
    
    def _draw_thermometers(self, painter: QPainter):
        """Draw thermometer bars"""
        # Thermometer layout
        thermo_y = 45
        thermo_height = 120
        thermo_width = 30
        thermo_spacing = 20
        
        # Calculate positions
        sensors = []
        
        if self._cpu_temp is not None:
            sensors.append(('CPU', self._cpu_display, self._cpu_max, list(self._cpu_history)))
        
        if self._gpu_temp is not None:
            sensors.append(('GPU', self._gpu_display, self._gpu_max, list(self._gpu_history)))
        
        if self._gpu_hotspot is not None:
            sensors.append(('HotSpot', self._hotspot_display, self._hotspot_max, list(self._hotspot_history)))
        
        if not sensors:
            # No data
            painter.setFont(self._font_small)
            painter.setPen(QPen(self._color_text_dim))
            painter.drawText(15, 100, "No temperature data available")
            return
        
        total_width = len(sensors) * thermo_width + (len(sensors) - 1) * thermo_spacing
        start_x = (self.width() - total_width) // 2
        
        # Draw each thermometer
        for i, (label, temp, max_temp, history) in enumerate(sensors):
            x = start_x + i * (thermo_width + thermo_spacing)
            
            self._draw_thermometer(
                painter,
                x=x,
                y=thermo_y,
                width=thermo_width,
                height=thermo_height,
                temperature=temp,
                max_temp=max_temp,
                label=label,
                history=history
            )
    
    def _draw_thermometer(self, painter: QPainter, x: int, y: int,
                         width: int, height: int, temperature: float,
                         max_temp: float, label: str, history: List[float]):
        """Draw a single thermometer
        
        Args:
            painter: QPainter instance
            x, y: Top-left position
            width, height: Dimensions
            temperature: Current temperature
            max_temp: Maximum recorded temperature
            label: Sensor label
            history: Temperature history
        """
        # Temperature scale (0-100°C)
        scale_min = 0
        scale_max = 100
        
        # Calculate fill height
        fill_ratio = (temperature - scale_min) / (scale_max - scale_min)
        fill_ratio = max(0, min(1, fill_ratio))
        fill_height = int(height * fill_ratio)
        
        # Background bar
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 80)))
        painter.drawRoundedRect(x, y, width, height, 5, 5)
        
        # Gradient fill
        gradient = QLinearGradient(x, y + height, x, y)
        
        # Add color stops based on temperature zones
        if temperature < 40:
            gradient.setColorAt(0, self._color_cool)
            gradient.setColorAt(1, self._color_cool.lighter(120))
        elif temperature < 60:
            gradient.setColorAt(0, self._color_cool)
            gradient.setColorAt(0.5, self._color_normal)
            gradient.setColorAt(1, self._color_normal.lighter(120))
        elif temperature < 75:
            gradient.setColorAt(0, self._color_normal)
            gradient.setColorAt(0.5, self._color_warm)
            gradient.setColorAt(1, self._color_warm.lighter(120))
        elif temperature < 85:
            gradient.setColorAt(0, self._color_warm)
            gradient.setColorAt(0.5, self._color_hot)
            gradient.setColorAt(1, self._color_hot.lighter(120))
        else:
            # Critical - pulsing effect
            pulse = math.sin(self._pulse_phase) * 0.3 + 0.7
            critical_color = QColor(
                int(self._color_critical.red() * pulse),
                int(self._color_critical.green() * pulse),
                int(self._color_critical.blue() * pulse)
            )
            gradient.setColorAt(0, self._color_hot)
            gradient.setColorAt(0.5, critical_color)
            gradient.setColorAt(1, critical_color.lighter(120))
        
        # Draw fill
        painter.setBrush(QBrush(gradient))
        fill_rect = QRectF(x, y + height - fill_height, width, fill_height)
        
        # Clip to rounded rect
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, width, height), 5, 5)
        painter.setClipPath(path)
        painter.drawRect(fill_rect)
        painter.setClipping(False)
        
        # Glass effect (highlight)
        highlight = QLinearGradient(x, y, x + width, y)
        highlight.setColorAt(0, QColor(255, 255, 255, 50))
        highlight.setColorAt(0.5, QColor(255, 255, 255, 20))
        highlight.setColorAt(1, QColor(255, 255, 255, 5))
        
        painter.setBrush(QBrush(highlight))
        painter.drawRoundedRect(x, y, width // 2, height, 5, 5)
        
        # Temperature text
        painter.setFont(self._font_medium)
        temp_color = self._get_temp_color(temperature)
        painter.setPen(QPen(temp_color))
        
        temp_text = f"{temperature:.0f}°"
        fm = QFontMetrics(self._font_medium)
        text_width = fm.horizontalAdvance(temp_text)
        text_x = x + (width - text_width) // 2
        text_y = y - 5
        
        painter.drawText(text_x, text_y, temp_text)
        
        # Label
        painter.setFont(self._font_tiny)
        painter.setPen(QPen(self._color_text_dim))
        
        label_fm = QFontMetrics(self._font_tiny)
        label_width = label_fm.horizontalAdvance(label)
        label_x = x + (width - label_width) // 2
        label_y = y + height + 12
        
        painter.drawText(label_x, label_y, label)
        
        # Max temp indicator
        painter.setFont(self._font_tiny)
        max_text = f"max: {max_temp:.0f}°"
        max_width = label_fm.horizontalAdvance(max_text)
        max_x = x + (width - max_width) // 2
        max_y = label_y + 12
        
        painter.drawText(max_x, max_y, max_text)
    
    def _draw_status(self, painter: QPainter):
        """Draw thermal status"""
        status_text, status_color = self._get_thermal_status()
        
        y = self.height() - 25
        
        # Icon
        icon = "✅" if status_text == "NORMAL" else "⚠️"
        painter.setFont(self._font_medium)
        painter.setPen(QPen(status_color))
        painter.drawText(15, y, icon)
        
        # Status text
        painter.setFont(self._font_small)
        
        # Pulsing for critical
        if status_text == "CRITICAL":
            pulse = math.sin(self._pulse_phase) * 0.5 + 0.5
            alpha = int(150 + pulse * 105)
            status_color = QColor(status_color.red(), status_color.green(), status_color.blue(), alpha)
        
        painter.setPen(QPen(status_color))
        painter.drawText(40, y, f"Status: {status_text}")
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def reset_max_temps(self):
        """Reset maximum temperature tracking
        
        Example:
            >>> widget.reset_max_temps()
        """
        self._cpu_max = 0.0
        self._gpu_max = 0.0
        self._hotspot_max = 0.0


# ========== TESTING ==========

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    import sys
    import random
    
    print("="*60)
    print("TemperatureWidget v0.3.5d_package3.2c Test")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    # Main window
    window = QMainWindow()
    window.setWindowTitle("Temperature Widget Test")
    window.setStyleSheet("background-color: #1a1d24;")
    
    # Central widget
    central = QWidget()
    layout = QVBoxLayout(central)
    
    # Temperature widget
    temp_widget = TemperatureWidget()
    layout.addWidget(temp_widget)
    
    # Connect warning signal
    def on_temp_warning(sensor: str, temp: float):
        print(f"⚠️ WARNING: {sensor} temperature: {temp:.1f}°C")
    
    temp_widget.temperature_warning.connect(on_temp_warning)
    
    window.setCentralWidget(central)
    window.resize(400, 350)
    window.show()
    
    # Simulate temperature updates
    base_cpu = 60.0
    base_gpu = 65.0
    base_hotspot = 72.0
    counter = 0
    
    def update_temps():
        global base_cpu, base_gpu, base_hotspot, counter
        
        # Vary temperatures
        cpu = base_cpu + random.uniform(-3, 3)
        gpu = base_gpu + random.uniform(-3, 3)
        hotspot = base_hotspot + random.uniform(-3, 3)
        
        # Occasionally spike to high temps
        counter += 1
        if counter > 100:
            base_cpu = random.uniform(55, 85)
            base_gpu = random.uniform(60, 90)
            base_hotspot = random.uniform(70, 95)
            counter = 0
        
        # Update widget
        temp_widget.update_temperatures(
            cpu=cpu,
            gpu=gpu,
            gpu_hotspot=hotspot
        )
    
    # Update timer
    timer = QTimer()
    timer.timeout.connect(update_temps)
    timer.start(100)  # Update every 100ms
    
    print("\n✅ TemperatureWidget displaying!")
    print("  - Vertical thermometers")
    print("  - Gradient temperature zones")
    print("  - Multi-sensor support")
    print("  - Warning indicators")
    print("  - Status display")
    print("  - Smooth animations")
    print("\nClose window to exit.")
    print("\n" + "="*60)
    print("🎉 PACKAGE 3.2 COMPLETE!")
    print("="*60)
    print("\nCompleted:")
    print("  ✅ 3.2a - PerformanceMonitor")
    print("  ✅ 3.2b - PerformanceWidget")
    print("  ✅ 3.2c - TemperatureWidget")
    print("\nNext: Package 3.3 - Frame Gen/Upscaler Interfaces")
    print("="*60)
    
    sys.exit(app.exec())
