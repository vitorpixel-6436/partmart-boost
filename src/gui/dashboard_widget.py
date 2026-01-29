#!/usr/bin/env python3
"""Dashboard Widget

Version: 0.3.5e (package 3.9a, stage 7/7)

Package 3.9a Stage 7: Integration with BackendBridge
- Use Bridge for all data access
- Subscribe to Qt signals
- Thread-safe updates
"""
try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QFrame, QGridLayout
    )
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QPainter, QPen, QColor, QFont
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("[DashboardWidget] PyQt6 not available")

from typing import Optional, List
from collections import deque

# STAGE 7: Import Bridge components
try:
    from core.backend_bridge import BackendBridge
    from core.query_system import QueryBuilder
    from core.qt_signal_bridge import QtSignalBridge
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    print("[DashboardWidget] BackendBridge not available")


class FPSGraphWidget(QWidget):
    """FPS Graph Widget
    
    Stage 7: Updated for Bridge integration
    """
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 150)
        self.fps_history: deque = deque(maxlen=100)
        
        # Add some initial data
        for _ in range(100):
            self.fps_history.append(0.0)
    
    def add_fps(self, fps: float):
        """Add FPS data point"""
        self.fps_history.append(fps)
        self.update()
    
    def paintEvent(self, event):
        """Paint FPS graph"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        try:
            # Background
            painter.fillRect(self.rect(), QColor(30, 30, 30))
            
            # Draw graph
            if len(self.fps_history) > 1:
                width = self.width()
                height = self.height()
                
                # Scale
                max_fps = max(max(self.fps_history), 60.0)
                points_per_pixel = len(self.fps_history) / width
                
                # Draw line
                painter.setPen(QPen(QColor(0, 200, 150), 2))
                
                prev_x = 0
                prev_y = height - (self.fps_history[0] / max_fps) * height
                
                for i, fps in enumerate(self.fps_history):
                    x = int(i / points_per_pixel)
                    y = height - (fps / max_fps) * height
                    
                    if i > 0:
                        painter.drawLine(int(prev_x), int(prev_y), x, int(y))
                    
                    prev_x = x
                    prev_y = y
                
                # Draw 60 FPS line
                sixty_fps_y = height - (60.0 / max_fps) * height
                painter.setPen(QPen(QColor(255, 255, 0, 100), 1, Qt.PenStyle.DashLine))
                painter.drawLine(0, int(sixty_fps_y), width, int(sixty_fps_y))
                
                # Labels
                painter.setPen(QColor(200, 200, 200))
                font = QFont()
                font.setPointSize(8)
                painter.setFont(font)
                painter.drawText(5, 15, f"Max: {max_fps:.0f}")
                painter.drawText(5, height - 5, "0")
        
        finally:
            painter.end()


class DashboardWidget(QWidget):
    """Dashboard Widget
    
    Version: 0.3.5e (package 3.9a, stage 7/7)
    
    Stage 7 Changes:
    - Integrated with BackendBridge
    - Uses Qt signals for updates
    - Thread-safe operations
    - No direct backend access
    """
    
    def __init__(self, bridge: Optional[BackendBridge] = None, 
                 qt_signals: Optional[QtSignalBridge] = None):
        """Initialize dashboard
        
        Args:
            bridge: BackendBridge instance (Stage 7)
            qt_signals: QtSignalBridge instance (Stage 7)
        """
        if not PYQT6_AVAILABLE:
            raise ImportError("PyQt6 is required")
        
        super().__init__()
        
        print("[DashboardWidget] Initializing (Stage 7)...")
        
        # STAGE 7: Store bridge
        self.bridge = bridge
        self.qt_signals = qt_signals
        
        # Current metrics
        self.current_fps = 0.0
        self.current_cpu = 0.0
        self.current_gpu = 0.0
        self.current_memory = 0.0
        self.current_temp = 0.0
        
        # Create UI
        self._create_ui()
        
        # STAGE 7: Connect to Qt signals
        if self.qt_signals:
            self._connect_signals()
        
        # Update timer (fallback)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._query_metrics)
        self.update_timer.start(100)  # 100ms
        
        print("[DashboardWidget] Initialized")
    
    def _create_ui(self):
        """Create user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Performance Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00C896;")
        layout.addWidget(title)
        
        # Metrics grid
        metrics_frame = QFrame()
        metrics_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        metrics_layout = QGridLayout(metrics_frame)
        
        # FPS
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00C896;")
        metrics_layout.addWidget(QLabel("Frame Rate:"), 0, 0)
        metrics_layout.addWidget(self.fps_label, 0, 1)
        
        # CPU
        self.cpu_label = QLabel("CPU: --")
        self.cpu_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        metrics_layout.addWidget(QLabel("CPU Usage:"), 1, 0)
        metrics_layout.addWidget(self.cpu_label, 1, 1)
        
        # GPU
        self.gpu_label = QLabel("GPU: --")
        self.gpu_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        metrics_layout.addWidget(QLabel("GPU Usage:"), 2, 0)
        metrics_layout.addWidget(self.gpu_label, 2, 1)
        
        # Memory
        self.memory_label = QLabel("Memory: --")
        self.memory_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        metrics_layout.addWidget(QLabel("Memory:"), 3, 0)
        metrics_layout.addWidget(self.memory_label, 3, 1)
        
        # Temperature
        self.temp_label = QLabel("Temp: --")
        self.temp_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        metrics_layout.addWidget(QLabel("Temperature:"), 4, 0)
        metrics_layout.addWidget(self.temp_label, 4, 1)
        
        layout.addWidget(metrics_frame)
        
        # FPS Graph
        graph_label = QLabel("FPS History")
        graph_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(graph_label)
        
        self.fps_graph = FPSGraphWidget()
        layout.addWidget(self.fps_graph)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect to Qt signals (Stage 7)"""
        if not self.qt_signals:
            return
        
        try:
            # Data updates
            self.qt_signals.data_updated.connect(self._on_data_updated)
            print("[DashboardWidget] Qt signals connected")
        except Exception as e:
            print(f"[DashboardWidget] Signal connection error: {e}")
    
    def _query_metrics(self):
        """Query metrics via Bridge (Stage 7)"""
        if not self.bridge:
            return
        
        try:
            # STAGE 7: Query via Bridge
            query = QueryBuilder() \
                .select(['fps', 'cpu', 'gpu', 'memory_used', 'temperature']) \
                .build()
            
            result = self.bridge.query_data('performance_metrics', query)
            
            if result.success and result.data:
                self._update_display(result.data)
        
        except Exception as e:
            # Silent fail - signals will handle updates
            pass
    
    def _on_data_updated(self, data_type: str, data: dict):
        """Handle data update signal (Stage 7)"""
        if data_type == 'performance_metrics':
            self._update_display(data)
    
    def _update_display(self, data: dict):
        """Update display with new data"""
        try:
            # Extract metrics
            fps = data.get('fps', 0.0)
            cpu = data.get('cpu', 0.0)
            gpu = data.get('gpu', 0.0)
            memory = data.get('memory_used', 0.0)
            temp = data.get('temperature', 0.0)
            
            # Update labels
            self.fps_label.setText(f"{fps:.1f}")
            self.cpu_label.setText(f"{cpu:.1f}%")
            self.gpu_label.setText(f"{gpu:.1f}%")
            self.memory_label.setText(f"{memory:.0f} MB")
            self.temp_label.setText(f"{temp:.1f}°C")
            
            # Update graph
            self.fps_graph.add_fps(fps)
            
            # Store current values
            self.current_fps = fps
            self.current_cpu = cpu
            self.current_gpu = gpu
            self.current_memory = memory
            self.current_temp = temp
        
        except Exception as e:
            print(f"[DashboardWidget] Display update error: {e}")
