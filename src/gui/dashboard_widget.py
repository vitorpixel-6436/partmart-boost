#!/usr/bin/env python3
"""Dashboard Widget

Version: 0.3.5d+patch7 - CRITICAL: Added error handling to prevent crashes

Real-time dashboard with crash protection.
"""
import sys
import time
import traceback
from pathlib import Path
from collections import deque

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.fps_tracker import FPSTracker
    from monitors.performance_monitor import PerformanceMonitor
except ImportError as e:
    print(f"[Dashboard] WARNING: Import error: {e}")
    FPSTracker = None
    PerformanceMonitor = None


class FPSGraphWidget(QWidget):
    """FPS Graph Widget"""
    
    def __init__(self, max_samples=60):
        super().__init__()
        self.setMinimumHeight(200)
        self.max_samples = max_samples
        self.fps_history = deque(maxlen=max_samples)
        
        for _ in range(max_samples):
            self.fps_history.append(0.0)
    
    def add_fps(self, fps: float):
        try:
            self.fps_history.append(fps)
            self.update()
        except Exception as e:
            print(f"[FPSGraph] Error: {e}")
    
    def clear(self):
        try:
            self.fps_history.clear()
            for _ in range(self.max_samples):
                self.fps_history.append(0.0)
            self.update()
        except Exception as e:
            print(f"[FPSGraph] Clear error: {e}")
    
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            painter.fillRect(self.rect(), QColor(26, 26, 26))
            
            pen = QPen(QColor(58, 58, 58))
            pen.setWidth(1)
            painter.setPen(pen)
            
            width = self.width()
            height = self.height()
            
            for fps in [30, 60, 120, 144]:
                y = height - int((fps / 200.0) * height)
                painter.drawLine(0, y, width, y)
                painter.drawText(5, y - 2, f"{fps}")
            
            if len(self.fps_history) > 1:
                pen = QPen(QColor(13, 115, 119))
                pen.setWidth(2)
                painter.setPen(pen)
                
                points = []
                for i, fps in enumerate(self.fps_history):
                    x = int((i / self.max_samples) * width)
                    y = height - int((min(fps, 200) / 200.0) * height)
                    points.append((x, y))
                
                for i in range(len(points) - 1):
                    painter.drawLine(points[i][0], points[i][1],
                                   points[i+1][0], points[i+1][1])
            
            if self.fps_history:
                current_fps = self.fps_history[-1]
                text = f"Current: {current_fps:.1f} FPS"
                painter.setPen(QColor(224, 224, 224))
                painter.drawText(width - 150, 20, text)
        
        except Exception as e:
            print(f"[FPSGraph] Paint error: {e}")


class DashboardWidget(QWidget):
    """Dashboard Widget v0.3.5d+patch7
    
    PATCH 7 Fixes:
    - Added try-catch in update_data()
    - Fixed crash on rapid tab switching
    - Added safety checks
    """
    
    def __init__(self):
        super().__init__()
        
        # PATCH 7: Safe initialization
        self._updating = False
        self._update_lock = False
        
        try:
            if FPSTracker is not None:
                self.fps_tracker = FPSTracker(window_size=30)
            else:
                self.fps_tracker = None
                print("[Dashboard] FPSTracker not available")
            
            if PerformanceMonitor is not None:
                self.performance_monitor = PerformanceMonitor()
                self.performance_monitor.start()
            else:
                self.performance_monitor = None
                print("[Dashboard] PerformanceMonitor not available")
            
            self.last_frame_time = time.perf_counter()
            self._create_ui()
        
        except Exception as e:
            print(f"[Dashboard] Init error: {e}")
            traceback.print_exc()
    
    def _create_ui(self):
        try:
            layout = QVBoxLayout(self)
            
            fps_group = QGroupBox("FPS Monitor")
            fps_layout = QVBoxLayout(fps_group)
            
            self.fps_graph = FPSGraphWidget()
            fps_layout.addWidget(self.fps_graph)
            
            layout.addWidget(fps_group)
            
            metrics_layout = QHBoxLayout()
            
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
        
        except Exception as e:
            print(f"[Dashboard] UI creation error: {e}")
    
    def update_data(self):
        """PATCH 7: Added error handling"""
        # PATCH 7: Prevent concurrent updates
        if self._update_lock:
            return
        
        self._update_lock = True
        
        try:
            if self.fps_tracker is None:
                return
            
            current_time = time.perf_counter()
            if current_time - self.last_frame_time > 0.001:
                self.fps_tracker.frame()
                self.last_frame_time = current_time
            
            stats = self.fps_tracker.get_stats()
            
            self.fps_graph.add_fps(stats.current)
            
            self.current_fps_label.setText(f"Current: {stats.current:.1f} FPS")
            self.avg_fps_label.setText(f"Average: {stats.average:.1f} FPS")
            self.min_fps_label.setText(f"Minimum: {stats.min:.1f} FPS")
            self.max_fps_label.setText(f"Maximum: {stats.max:.1f} FPS")
            self.frame_time_label.setText(f"Frame Time: {stats.frame_time:.2f} ms")
            
            if self.performance_monitor is not None:
                metrics = self.performance_monitor.get_metrics()
                
                if metrics:
                    self.gpu_util_label.setText(f"GPU: {metrics.gpu_util:.0f}%")
                    self.cpu_util_label.setText(f"CPU: {metrics.cpu_util:.0f}%")
                    self.memory_label.setText(
                        f"Memory: {metrics.memory_used:.0f} / {metrics.memory_total:.0f} MB"
                    )
                    self.temp_label.setText(f"Temperature: {metrics.temperature:.0f}°C")
                    self.power_label.setText(f"Power: {metrics.power_draw:.0f} W")
        
        except Exception as e:
            print(f"[Dashboard] Update error: {e}")
            # Don't crash - continue running
        
        finally:
            self._update_lock = False
    
    def get_current_fps(self) -> float:
        try:
            if self.fps_tracker is None:
                return 0.0
            return self.fps_tracker.get_fps()
        except:
            return 0.0
    
    def clear_history(self):
        try:
            if self.fps_graph is not None:
                self.fps_graph.clear()
            if self.fps_tracker is not None:
                self.fps_tracker.reset()
        except Exception as e:
            print(f"[Dashboard] Clear error: {e}")
