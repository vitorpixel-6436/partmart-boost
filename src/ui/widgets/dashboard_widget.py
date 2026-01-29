#!/usr/bin/env python3
"""Dashboard Widget - Main System Overview

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Package 3.9a Stage 7.3: Frontend integration with BackendBridge.

Features:
- System overview panel
- Performance score display
- Resource utilization
- Bottleneck indicators
- Efficiency metrics
- Real-time updates via bridge
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import Dict, Any, Optional


class DashboardWidget(QWidget):
    """Dashboard widget with system overview
    
    v0.3.5e (package 3.9a, stage 7.3/7.7)
    
    Displays:
    - Performance score
    - CPU/GPU/RAM utilization
    - Bottleneck information
    - Efficiency metrics
    - System status
    
    Integration:
        >>> from core.app_integrator import AppIntegrator
        >>> 
        >>> integrator = AppIntegrator.get_instance()
        >>> bridge = integrator.get_bridge()
        >>> qt_signals = integrator.get_qt_signals()
        >>> 
        >>> widget = DashboardWidget(bridge, qt_signals)
    """
    
    # Signals
    clicked = pyqtSignal()
    
    def __init__(self, bridge=None, qt_signals=None, parent=None):
        """Initialize dashboard widget
        
        Args:
            bridge: BackendBridge instance (optional)
            qt_signals: QtSignalBridge instance (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Bridge connections
        self._bridge = bridge
        self._qt_signals = qt_signals
        
        # Data
        self._score = 0.0
        self._cpu = 0.0
        self._gpu = 0.0
        self._ram = 0.0
        self._fps = 0.0
        self._bottleneck = 'none'
        self._bottleneck_severity = 'none'
        
        # UI setup
        self._init_ui()
        
        # Connect to signals
        if self._qt_signals:
            self._qt_signals.data_updated.connect(self._on_data_updated)
            print("[DashboardWidget] Connected to Qt signals")
        
        # Query initial data
        if self._bridge:
            self._query_initial_data()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("System Overview")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Performance score
        self._score_group = self._create_score_group()
        layout.addWidget(self._score_group)
        
        # Resource utilization
        self._resource_group = self._create_resource_group()
        layout.addWidget(self._resource_group)
        
        # Status info
        self._status_group = self._create_status_group()
        layout.addWidget(self._status_group)
        
        layout.addStretch()
    
    def _create_score_group(self) -> QGroupBox:
        """Create performance score group"""
        group = QGroupBox("Performance")
        group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Score label
        self._score_label = QLabel("0")
        self._score_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self._score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_label.setStyleSheet("color: #4CAF50;")
        layout.addWidget(self._score_label)
        
        # Score text
        score_text = QLabel("Performance Score")
        score_text.setFont(QFont("Segoe UI", 10))
        score_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_text.setStyleSheet("color: #aaa;")
        layout.addWidget(score_text)
        
        return group
    
    def _create_resource_group(self) -> QGroupBox:
        """Create resource utilization group"""
        group = QGroupBox("Resource Utilization")
        group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        
        layout = QGridLayout(group)
        layout.setSpacing(10)
        
        # CPU
        layout.addWidget(self._create_label("CPU:", bold=True), 0, 0)
        self._cpu_label = self._create_label("0%")
        layout.addWidget(self._cpu_label, 0, 1)
        
        # GPU
        layout.addWidget(self._create_label("GPU:", bold=True), 1, 0)
        self._gpu_label = self._create_label("0%")
        layout.addWidget(self._gpu_label, 1, 1)
        
        # RAM
        layout.addWidget(self._create_label("RAM:", bold=True), 2, 0)
        self._ram_label = self._create_label("0%")
        layout.addWidget(self._ram_label, 2, 1)
        
        # FPS
        layout.addWidget(self._create_label("FPS:", bold=True), 3, 0)
        self._fps_label = self._create_label("0")
        layout.addWidget(self._fps_label, 3, 1)
        
        return group
    
    def _create_status_group(self) -> QGroupBox:
        """Create status group"""
        group = QGroupBox("Status")
        group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Bottleneck
        bottleneck_layout = QHBoxLayout()
        bottleneck_layout.addWidget(self._create_label("Bottleneck:", bold=True))
        self._bottleneck_label = self._create_label("None")
        bottleneck_layout.addWidget(self._bottleneck_label)
        bottleneck_layout.addStretch()
        layout.addLayout(bottleneck_layout)
        
        # Monitoring status
        status_layout = QHBoxLayout()
        status_layout.addWidget(self._create_label("Monitoring:", bold=True))
        self._monitoring_label = self._create_label("⏳ Pending")
        status_layout.addWidget(self._monitoring_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        return group
    
    def _create_label(self, text: str, bold: bool = False) -> QLabel:
        """Create styled label"""
        label = QLabel(text)
        font = QFont("Segoe UI", 10)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        label.setFont(font)
        label.setStyleSheet("color: white;")
        return label
    
    def _query_initial_data(self):
        """Query initial data from backend"""
        if not self._bridge:
            return
        
        try:
            # Query performance metrics
            result = self._bridge.query_data('performance_metrics', {})
            
            if result.success and result.data:
                self._update_from_data(result.data)
        
        except Exception as e:
            print(f"[DashboardWidget] Query failed: {e}")
    
    def _on_data_updated(self, data_type: str, data: Dict[str, Any]):
        """Handle data update from backend
        
        Args:
            data_type: Type of data
            data: Data dictionary
        """
        if data_type == 'performance_metrics':
            self._update_from_data(data)
        elif data_type == 'monitoring_started':
            self._monitoring_label.setText("✅ Active")
            self._monitoring_label.setStyleSheet("color: #4CAF50;")
        elif data_type == 'monitoring_stopped':
            self._monitoring_label.setText("❌ Stopped")
            self._monitoring_label.setStyleSheet("color: #F44336;")
    
    def _update_from_data(self, data: Dict[str, Any]):
        """Update UI from data
        
        Args:
            data: Performance metrics
        """
        # Extract data
        self._score = data.get('score', 0.0)
        self._cpu = data.get('cpu', 0.0)
        self._gpu = data.get('gpu', 0.0)
        self._ram = data.get('memory', 0.0)
        self._fps = data.get('fps', 0.0)
        
        # Update labels
        self._score_label.setText(f"{self._score:.0f}")
        self._cpu_label.setText(f"{self._cpu:.1f}%")
        self._gpu_label.setText(f"{self._gpu:.1f}%")
        self._ram_label.setText(f"{self._ram:.1f}%")
        self._fps_label.setText(f"{self._fps:.0f}")
        
        # Update score color
        if self._score >= 80:
            color = "#4CAF50"  # Green
        elif self._score >= 60:
            color = "#8BC34A"  # Light green
        elif self._score >= 40:
            color = "#FF9800"  # Orange
        else:
            color = "#F44336"  # Red
        
        self._score_label.setStyleSheet(f"color: {color};")
