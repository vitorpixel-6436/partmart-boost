#!/usr/bin/env python3
"""Performance Widget

Version: 0.3.5e (package 3.9a, stage 7/7)

Package 3.9a Stage 7: Integration with BackendBridge
- Use Bridge for data queries
- Subscribe to Qt signals
- Real-time chart updates
"""
try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QFrame, QGridLayout, QPushButton
    )
    from PyQt6.QtCore import Qt, QTimer
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("[PerformanceWidget] PyQt6 not available")

from typing import Optional, List, Dict, Any
from collections import deque
import time

# STAGE 7: Import Bridge components
try:
    from core.backend_bridge import BackendBridge
    from core.query_system import QueryBuilder
    from core.qt_signal_bridge import QtSignalBridge
    from core.command_system import ClearHistoryCommand
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    print("[PerformanceWidget] BackendBridge not available")


class PerformanceWidget(QWidget):
    """Performance Widget
    
    Version: 0.3.5e (package 3.9a, stage 7/7)
    
    Stage 7 Changes:
    - Integrated with BackendBridge
    - Uses Qt signals for updates
    - QueryBuilder for data access
    - No direct backend access
    """
    
    def __init__(self, bridge: Optional[BackendBridge] = None,
                 qt_signals: Optional[QtSignalBridge] = None):
        """Initialize performance widget
        
        Args:
            bridge: BackendBridge instance (Stage 7)
            qt_signals: QtSignalBridge instance (Stage 7)
        """
        if not PYQT6_AVAILABLE:
            raise ImportError("PyQt6 is required")
        
        super().__init__()
        
        print("[PerformanceWidget] Initializing (Stage 7)...")
        
        # STAGE 7: Store bridge
        self.bridge = bridge
        self.qt_signals = qt_signals
        
        # Metrics history
        self.metrics_history: deque = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            'avg_fps': 0.0,
            'min_fps': 0.0,
            'max_fps': 0.0,
            'avg_cpu': 0.0,
            'avg_gpu': 0.0,
            'samples': 0,
        }
        
        # Create UI
        self._create_ui()
        
        # STAGE 7: Connect to Qt signals
        if self.qt_signals:
            self._connect_signals()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_stats)
        self.update_timer.start(1000)  # 1 second
        
        print("[PerformanceWidget] Initialized")
    
    def _create_ui(self):
        """Create user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Performance Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00C896;")
        layout.addWidget(title)
        
        # Statistics grid
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QGridLayout(stats_frame)
        
        # FPS stats
        stats_layout.addWidget(QLabel("Average FPS:"), 0, 0)
        self.avg_fps_label = QLabel("--")
        self.avg_fps_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        stats_layout.addWidget(self.avg_fps_label, 0, 1)
        
        stats_layout.addWidget(QLabel("Min FPS:"), 1, 0)
        self.min_fps_label = QLabel("--")
        stats_layout.addWidget(self.min_fps_label, 1, 1)
        
        stats_layout.addWidget(QLabel("Max FPS:"), 2, 0)
        self.max_fps_label = QLabel("--")
        stats_layout.addWidget(self.max_fps_label, 2, 1)
        
        # Resource stats
        stats_layout.addWidget(QLabel("Average CPU:"), 3, 0)
        self.avg_cpu_label = QLabel("--")
        stats_layout.addWidget(self.avg_cpu_label, 3, 1)
        
        stats_layout.addWidget(QLabel("Average GPU:"), 4, 0)
        self.avg_gpu_label = QLabel("--")
        stats_layout.addWidget(self.avg_gpu_label, 4, 1)
        
        stats_layout.addWidget(QLabel("Samples:"), 5, 0)
        self.samples_label = QLabel("--")
        stats_layout.addWidget(self.samples_label, 5, 1)
        
        layout.addWidget(stats_frame)
        
        # Clear button
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect to Qt signals (Stage 7)"""
        if not self.qt_signals:
            return
        
        try:
            # Data updates
            self.qt_signals.data_updated.connect(self._on_data_updated)
            print("[PerformanceWidget] Qt signals connected")
        except Exception as e:
            print(f"[PerformanceWidget] Signal connection error: {e}")
    
    def _on_data_updated(self, data_type: str, data: dict):
        """Handle data update signal (Stage 7)"""
        if data_type == 'performance_metrics':
            self._add_metrics(data)
    
    def _add_metrics(self, data: dict):
        """Add metrics to history"""
        try:
            # Add to history
            self.metrics_history.append({
                'timestamp': time.time(),
                'fps': data.get('fps', 0.0),
                'cpu': data.get('cpu', 0.0),
                'gpu': data.get('gpu', 0.0),
                'memory': data.get('memory_used', 0.0),
                'temperature': data.get('temperature', 0.0),
            })
        
        except Exception as e:
            print(f"[PerformanceWidget] Add metrics error: {e}")
    
    def _update_stats(self):
        """Update statistics"""
        if not self.metrics_history:
            return
        
        try:
            # Calculate stats
            fps_values = [m['fps'] for m in self.metrics_history if m['fps'] > 0]
            cpu_values = [m['cpu'] for m in self.metrics_history]
            gpu_values = [m['gpu'] for m in self.metrics_history]
            
            if fps_values:
                self.stats['avg_fps'] = sum(fps_values) / len(fps_values)
                self.stats['min_fps'] = min(fps_values)
                self.stats['max_fps'] = max(fps_values)
            
            if cpu_values:
                self.stats['avg_cpu'] = sum(cpu_values) / len(cpu_values)
            
            if gpu_values:
                self.stats['avg_gpu'] = sum(gpu_values) / len(gpu_values)
            
            self.stats['samples'] = len(self.metrics_history)
            
            # Update labels
            self.avg_fps_label.setText(f"{self.stats['avg_fps']:.1f}")
            self.min_fps_label.setText(f"{self.stats['min_fps']:.1f}")
            self.max_fps_label.setText(f"{self.stats['max_fps']:.1f}")
            self.avg_cpu_label.setText(f"{self.stats['avg_cpu']:.1f}%")
            self.avg_gpu_label.setText(f"{self.stats['avg_gpu']:.1f}%")
            self.samples_label.setText(f"{self.stats['samples']}")
        
        except Exception as e:
            print(f"[PerformanceWidget] Stats update error: {e}")
    
    def _clear_history(self):
        """Clear history (Stage 7: via Bridge)"""
        try:
            # Clear local history
            self.metrics_history.clear()
            
            # Reset stats
            self.stats = {
                'avg_fps': 0.0,
                'min_fps': 0.0,
                'max_fps': 0.0,
                'avg_cpu': 0.0,
                'avg_gpu': 0.0,
                'samples': 0,
            }
            
            # Update labels
            self.avg_fps_label.setText("--")
            self.min_fps_label.setText("--")
            self.max_fps_label.setText("--")
            self.avg_cpu_label.setText("--")
            self.avg_gpu_label.setText("--")
            self.samples_label.setText("--")
            
            # STAGE 7: Clear Bridge history
            if self.bridge:
                command = ClearHistoryCommand()
                self.bridge.execute_command(command)
            
            print("[PerformanceWidget] History cleared")
        
        except Exception as e:
            print(f"[PerformanceWidget] Clear history error: {e}")
