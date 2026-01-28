#!/usr/bin/env python3
"""Dashboard Widget

Version: 0.4.0-alpha

Real-time dashboard with FPS graph and metrics.
"""
import sys
import time
from pathlib import Path
from collections import deque

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen

# Import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.fps_tracker import FPSTracker
from monitors.performance_monitor import PerformanceMonitor


class FPSGraphWidget(QWidget):
    """FPS Graph Widget
    
    Displays real-time FPS graph.
    """
    
    def __init__(self, max_samples=60):
        super().__init__()
        self.setMinimumHeight(200)
        
        self.max_samples = max_samples
        self.fps_history = deque(maxlen=max_samples)
        
        # Fill with zeros
        for _ in range(max_samples):
            self.fps_history.append(0.0)
    
    def add_fps(self, fps: float):
        """Add FPS value"""
        self.fps_history.append(fps)
        self.update()  # Trigger repaint
    
    def clear(self):
        """Clear history"""
        self.fps_history.clear()
        for _ in range(self.max_samples):
            self.fps_history.append(0.0)
        self.update()
    
    def paintEvent(self, event):
        """Paint graph"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(26, 26, 26))
        
        # Draw grid
        pen = QPen(QColor(58, 58, 58))
        pen.setWidth(1)
        painter.setPen(pen)
        
        width = self.width()
        height = self.height()
        
        # Horizontal lines (FPS marks)
        for fps in [30, 60, 120, 144]:
            y = height - int((fps / 200.0) * height)
            painter.drawLine(0, y, width, y)
            painter.drawText(5, y - 2, f"{fps}")
        
        # Draw FPS line
        if len(self.fps_history) > 1:
            pen = QPen(QColor(13, 115, 119))
            pen.setWidth(2)
            painter.setPen(pen)
            
            points = []
            for i, fps in enumerate(self.fps_history):
                x = int((i / self.max_samples) * width)
                y = height - int((min(fps, 200) / 200.0) * height)
                points.append((x, y))
            
            # Draw lines between points
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], 
                               points[i+1][0], points[i+1][1])
        
        # Draw current FPS
        if self.fps_history:
            current_fps = self.fps_history[-1]
            text = f"Current: {current_fps:.1f} FPS"
            painter.setPen(QColor(224, 224, 224))
            painter.drawText(width - 150, 20, text)


class DashboardWidget(QWidget):
    """Dashboard Widget
    
    Main dashboard with real-time monitoring.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize trackers
        self.fps_tracker = FPSTracker(window_size=30)
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.start()
        
        self.last_frame_time = time.perf_counter()
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)
        
        # FPS Graph
        fps_group = QGroupBox("FPS Monitor")
        fps_layout = QVBoxLayout(fps_group)
        
        self.fps_graph = FPSGraphWidget()
        fps_layout.addWidget(self.fps_graph)
        
        layout.addWidget(fps_group)
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        # FPS Metrics
        fps_metrics_group = QGroupBox("FPS Stats")
        fps_metrics_layout = QVBoxLayout(fps_metrics_group)
        
        self.current_fps_label = QLabel("Current: 0.0 FPS")
        self.avg_fps_label = QLabel("Average: 0.0 FPS")
        self.min_fps_label = QLabel("Minimum: 0.0 FPS")
        self.max_fps_label = QLabel("Maximum: 0.0 FPS")
        self.frame_time_label = QLabel("Frame Time: 0.0 ms")
        
        fps_metrics_layout.addWidget(self.current_fps_label)
        fps_metrics_layout.addWidget(self.avg_fps_label)
        fps_metrics_layout.addWidget(self.min_fps_label)
        fps_metrics_layout.addWidget(self.max_fps_label)
        fps_metrics_layout.addWidget(self.frame_time_label)
        
        metrics_layout.addWidget(fps_metrics_group)
        
        # Performance Metrics
        perf_metrics_group = QGroupBox("Performance")
        perf_metrics_layout = QVBoxLayout(perf_metrics_group)
        
        self.gpu_util_label = QLabel("GPU: 0%")
        self.cpu_util_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("Memory: 0 / 0 MB")
        self.temp_label = QLabel("Temperature: 0°C")
        self.power_label = QLabel("Power: 0 W")
        
        perf_metrics_layout.addWidget(self.gpu_util_label)
        perf_metrics_layout.addWidget(self.cpu_util_label)
        perf_metrics_layout.addWidget(self.memory_label)
        perf_metrics_layout.addWidget(self.temp_label)
        perf_metrics_layout.addWidget(self.power_label)
        
        metrics_layout.addWidget(perf_metrics_group)
        
        layout.addLayout(metrics_layout)
    
    def update_data(self):
        """Update dashboard data"""
        # Simulate frame
        current_time = time.perf_counter()
        if current_time - self.last_frame_time > 0.001:
            self.fps_tracker.frame()
            self.last_frame_time = current_time
        
        # Get FPS stats
        stats = self.fps_tracker.get_stats()
        
        # Update graph
        self.fps_graph.add_fps(stats.current)
        
        # Update FPS labels
        self.current_fps_label.setText(f"Current: {stats.current:.1f} FPS")
        self.avg_fps_label.setText(f"Average: {stats.average:.1f} FPS")
        self.min_fps_label.setText(f"Minimum: {stats.min:.1f} FPS")
        self.max_fps_label.setText(f"Maximum: {stats.max:.1f} FPS")
        self.frame_time_label.setText(f"Frame Time: {stats.frame_time:.2f} ms")
        
        # Get performance metrics
        metrics = self.performance_monitor.get_metrics()
        
        if metrics:
            self.gpu_util_label.setText(f"GPU: {metrics.gpu_util:.0f}%")
            self.cpu_util_label.setText(f"CPU: {metrics.cpu_util:.0f}%")
            self.memory_label.setText(f"Memory: {metrics.memory_used:.0f} / {metrics.memory_total:.0f} MB")
            self.temp_label.setText(f"Temperature: {metrics.temperature:.0f}°C")
            self.power_label.setText(f"Power: {metrics.power_draw:.0f} W")
    
    def get_current_fps(self) -> float:
        """Get current FPS"""
        return self.fps_tracker.get_fps()
    
    def clear_history(self):
        """Clear history"""
        self.fps_graph.clear()
        self.fps_tracker.reset()
