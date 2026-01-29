#!/usr/bin/env python3
"""Settings Widget - Monitoring Controls

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Package 3.9a Stage 7.3: Frontend integration with BackendBridge.

Features:
- Monitoring controls
- Update interval configuration
- Start/stop monitoring via commands
- Real-time status display
- Command execution via bridge
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QCheckBox, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, Optional

try:
    from core.command_system import StartMonitoringCommand, StopMonitoringCommand
    COMMANDS_AVAILABLE = True
except ImportError:
    COMMANDS_AVAILABLE = False
    print("[SettingsWidget] Command system not available")


class SettingsWidget(QWidget):
    """Settings widget with monitoring controls
    
    v0.3.5e (package 3.9a, stage 7.3/7.7)
    
    Controls:
    - Start/Stop monitoring
    - Update interval (50-1000ms)
    - Auto-start option
    - Status display
    
    Integration:
        >>> from core.app_integrator import AppIntegrator
        >>> 
        >>> integrator = AppIntegrator.get_instance()
        >>> bridge = integrator.get_bridge()
        >>> qt_signals = integrator.get_qt_signals()
        >>> 
        >>> widget = SettingsWidget(bridge, qt_signals)
    """
    
    # Signals
    monitoring_started = pyqtSignal()
    monitoring_stopped = pyqtSignal()
    
    def __init__(self, bridge=None, qt_signals=None, parent=None):
        """Initialize settings widget
        
        Args:
            bridge: BackendBridge instance (optional)
            qt_signals: QtSignalBridge instance (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Bridge connections
        self._bridge = bridge
        self._qt_signals = qt_signals
        
        # State
        self._monitoring_active = False
        self._interval = 100  # Default 100ms
        
        # UI setup
        self._init_ui()
        
        # Connect to signals
        if self._qt_signals:
            self._qt_signals.event_received.connect(self._on_event_received)
            print("[SettingsWidget] Connected to Qt signals")
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Monitoring Settings")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Controls group
        self._controls_group = self._create_controls_group()
        layout.addWidget(self._controls_group)
        
        # Configuration group
        self._config_group = self._create_config_group()
        layout.addWidget(self._config_group)
        
        # Status group
        self._status_group = self._create_status_group()
        layout.addWidget(self._status_group)
        
        layout.addStretch()
    
    def _create_controls_group(self) -> QGroupBox:
        """Create controls group"""
        group = QGroupBox("Controls")
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
        layout.setSpacing(10)
        
        # Start button
        self._start_btn = QPushButton("▶ Start Monitoring")
        self._start_btn.setFont(QFont("Segoe UI", 10))
        self._start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self._start_btn.clicked.connect(self._on_start_clicked)
        layout.addWidget(self._start_btn)
        
        # Stop button
        self._stop_btn = QPushButton("⏹ Stop Monitoring")
        self._stop_btn.setFont(QFont("Segoe UI", 10))
        self._stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        self._stop_btn.setEnabled(False)
        layout.addWidget(self._stop_btn)
        
        return group
    
    def _create_config_group(self) -> QGroupBox:
        """Create configuration group"""
        group = QGroupBox("Configuration")
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
        layout.setSpacing(10)
        
        # Interval slider
        interval_label = QLabel("Update Interval:")
        interval_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        interval_label.setStyleSheet("color: white;")
        layout.addWidget(interval_label)
        
        self._interval_value_label = QLabel(f"{self._interval} ms")
        self._interval_value_label.setFont(QFont("Segoe UI", 10))
        self._interval_value_label.setStyleSheet("color: #aaa;")
        layout.addWidget(self._interval_value_label)
        
        self._interval_slider = QSlider(Qt.Orientation.Horizontal)
        self._interval_slider.setMinimum(50)
        self._interval_slider.setMaximum(1000)
        self._interval_slider.setValue(self._interval)
        self._interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._interval_slider.setTickInterval(100)
        self._interval_slider.valueChanged.connect(self._on_interval_changed)
        layout.addWidget(self._interval_slider)
        
        # Auto-start checkbox
        self._auto_start_check = QCheckBox("Auto-start monitoring")
        self._auto_start_check.setFont(QFont("Segoe UI", 10))
        self._auto_start_check.setStyleSheet("color: white;")
        self._auto_start_check.setChecked(True)
        layout.addWidget(self._auto_start_check)
        
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
        
        # Status label
        self._status_label = QLabel("⏳ Monitoring pending...")
        self._status_label.setFont(QFont("Segoe UI", 10))
        self._status_label.setStyleSheet("color: #FFC107;")
        layout.addWidget(self._status_label)
        
        return group
    
    def _on_interval_changed(self, value: int):
        """Handle interval change
        
        Args:
            value: New interval value (ms)
        """
        self._interval = value
        self._interval_value_label.setText(f"{value} ms")
    
    def _on_start_clicked(self):
        """Handle start button click"""
        if not self._bridge or not COMMANDS_AVAILABLE:
            print("[SettingsWidget] Bridge or commands not available")
            self._update_status("❌ Command system unavailable", "#F44336")
            return
        
        try:
            # Create command
            command = StartMonitoringCommand(interval=self._interval)
            
            # Execute
            result = self._bridge.execute_command(command)
            
            if result.success:
                self._monitoring_active = True
                self._start_btn.setEnabled(False)
                self._stop_btn.setEnabled(True)
                self._update_status("✅ Monitoring started", "#4CAF50")
                self.monitoring_started.emit()
            else:
                error = result.error or "Unknown error"
                self._update_status(f"❌ Failed: {error}", "#F44336")
        
        except Exception as e:
            self._update_status(f"❌ Error: {e}", "#F44336")
            print(f"[SettingsWidget] Start failed: {e}")
    
    def _on_stop_clicked(self):
        """Handle stop button click"""
        if not self._bridge or not COMMANDS_AVAILABLE:
            print("[SettingsWidget] Bridge or commands not available")
            return
        
        try:
            # Create command
            command = StopMonitoringCommand()
            
            # Execute
            result = self._bridge.execute_command(command)
            
            if result.success:
                self._monitoring_active = False
                self._start_btn.setEnabled(True)
                self._stop_btn.setEnabled(False)
                self._update_status("⏹ Monitoring stopped", "#FFC107")
                self.monitoring_stopped.emit()
            else:
                error = result.error or "Unknown error"
                self._update_status(f"❌ Failed: {error}", "#F44336")
        
        except Exception as e:
            self._update_status(f"❌ Error: {e}", "#F44336")
            print(f"[SettingsWidget] Stop failed: {e}")
    
    def _on_event_received(self, event_type: str, data: Dict[str, Any]):
        """Handle event from backend
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if event_type == 'monitoring_started':
            self._monitoring_active = True
            self._start_btn.setEnabled(False)
            self._stop_btn.setEnabled(True)
            
            interval = data.get('interval', 100)
            self._update_status(f"✅ Monitoring active ({interval}ms)", "#4CAF50")
        
        elif event_type == 'monitoring_stopped':
            self._monitoring_active = False
            self._start_btn.setEnabled(True)
            self._stop_btn.setEnabled(False)
            self._update_status("⏹ Monitoring stopped", "#FFC107")
    
    def _update_status(self, text: str, color: str):
        """Update status label
        
        Args:
            text: Status text
            color: Text color (hex)
        """
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"color: {color};")
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active
        
        Returns:
            True if monitoring
        """
        return self._monitoring_active
    
    def get_interval(self) -> int:
        """Get current interval
        
        Returns:
            Interval in milliseconds
        """
        return self._interval
    
    def is_auto_start_enabled(self) -> bool:
        """Check if auto-start is enabled
        
        Returns:
            True if enabled
        """
        return self._auto_start_check.isChecked()
