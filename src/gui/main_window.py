#!/usr/bin/env python3
"""Main Window

Version: 0.3.5e (package 3.9a, stage 7/7)

Package 3.9a Stage 7: Integration with BackendBridge
- Use BackendBridge for all operations
- Subscribe to Qt signals
- Thread-safe updates
"""
try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QMessageBox, QStatusBar
    )
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtGui import QIcon
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("[MainWindow] PyQt6 not available")

import sys
import os
from typing import Optional

# STAGE 7: Import BackendBridge and Commands
try:
    from core.backend_bridge import BackendBridge
    from core.command_system import StartMonitoringCommand, StopMonitoringCommand
    from core.qt_signal_bridge import QtSignalBridge
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    print("[MainWindow] BackendBridge not available")


class MainWindow(QMainWindow):
    """Main Application Window
    
    Version: 0.3.5e (package 3.9a, stage 7/7)
    
    Stage 7 Changes:
    - Integrated with BackendBridge
    - Uses Commands instead of direct calls
    - Subscribes to Qt signals for updates
    - Thread-safe operations
    """
    
    def __init__(self, integrator=None):
        """Initialize main window
        
        Args:
            integrator: AppIntegrator instance (Stage 7)
        """
        if not PYQT6_AVAILABLE:
            raise ImportError("PyQt6 is required")
        
        super().__init__()
        
        print("[MainWindow] Initializing v0.3.5e (Stage 7)...")
        
        # STAGE 7: Store integrator
        self.integrator = integrator
        self.bridge: Optional[BackendBridge] = None
        self.qt_signals: Optional[QtSignalBridge] = None
        
        # STAGE 7: Get BackendBridge if available
        if integrator and integrator.is_ready():
            self.bridge = integrator.get_bridge()
            self.qt_signals = integrator.get_qt_signals()
            print("[MainWindow] ✅ BackendBridge connected")
        else:
            print("[MainWindow] ⚠️ Running without BackendBridge")
        
        # Widgets
        self.dashboard_widget = None
        self.performance_widget = None
        self.settings_widget = None
        self.optiscaler_widget = None
        self.logs_widget = None
        
        # Setup UI
        self._create_ui()
        
        # STAGE 7: Connect to Qt signals
        if self.qt_signals:
            self._connect_signals()
        
        # STAGE 7: Start monitoring via Bridge
        self._start_monitoring()
        
        # Update timer (fallback if signals don't work)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # 100ms = 10 FPS
        
        print("[MainWindow] ✅ Initialized successfully")
    
    def _create_ui(self):
        """Create user interface"""
        self.setWindowTitle("PartMart Boost v0.3.5e")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs (lazy load to avoid import errors)
        self._create_tabs()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        print("[MainWindow] UI created")
    
    def _create_tabs(self):
        """Create tab widgets"""
        try:
            # Dashboard tab
            try:
                from gui.dashboard_widget import DashboardWidget
                self.dashboard_widget = DashboardWidget(
                    bridge=self.bridge,
                    qt_signals=self.qt_signals
                )
                self.tabs.addTab(self.dashboard_widget, "Dashboard")
                print("[MainWindow] ✅ Dashboard tab created")
            except ImportError as e:
                print(f"[MainWindow] Dashboard import error: {e}")
                self.tabs.addTab(self._create_placeholder("Dashboard"), "Dashboard")
            
            # Performance tab
            try:
                from gui.performance_widget import PerformanceWidget
                self.performance_widget = PerformanceWidget(
                    bridge=self.bridge,
                    qt_signals=self.qt_signals
                )
                self.tabs.addTab(self.performance_widget, "Performance")
                print("[MainWindow] ✅ Performance tab created")
            except ImportError as e:
                print(f"[MainWindow] Performance import error: {e}")
                self.tabs.addTab(self._create_placeholder("Performance"), "Performance")
            
            # Settings tab
            try:
                from gui.settings_widget import SettingsWidget
                self.settings_widget = SettingsWidget(
                    bridge=self.bridge
                )
                self.tabs.addTab(self.settings_widget, "Settings")
                print("[MainWindow] ✅ Settings tab created")
            except ImportError as e:
                print(f"[MainWindow] Settings import error: {e}")
                self.tabs.addTab(self._create_placeholder("Settings"), "Settings")
            
            # OptiScaler tab
            try:
                from gui.optiscaler_tab import OptiScalerTab
                self.optiscaler_widget = OptiScalerTab()
                self.tabs.addTab(self.optiscaler_widget, "OptiScaler")
                print("[MainWindow] ✅ OptiScaler tab created")
            except ImportError as e:
                print(f"[MainWindow] OptiScaler import error: {e}")
                self.tabs.addTab(self._create_placeholder("OptiScaler"), "OptiScaler")
            
            # Logs tab
            try:
                from gui.logs_widget import LogsWidget
                self.logs_widget = LogsWidget()
                self.tabs.addTab(self.logs_widget, "Logs")
                print("[MainWindow] ✅ Logs tab created")
            except ImportError as e:
                print(f"[MainWindow] Logs import error: {e}")
                self.tabs.addTab(self._create_placeholder("Logs"), "Logs")
        
        except Exception as e:
            print(f"[MainWindow] Tab creation error: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_placeholder(self, name: str) -> QWidget:
        """Create placeholder widget for failed imports"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{name} tab not available")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget
    
    def _connect_signals(self):
        """Connect to Qt signals (Stage 7)"""
        if not self.qt_signals:
            return
        
        try:
            # Data updates
            self.qt_signals.data_updated.connect(self._on_data_updated)
            
            # Command completion
            self.qt_signals.command_completed.connect(self._on_command_completed)
            
            # Errors
            self.qt_signals.error_occurred.connect(self._on_error)
            
            # Status changes
            self.qt_signals.status_changed.connect(self._on_status_changed)
            
            print("[MainWindow] ✅ Qt signals connected")
        
        except Exception as e:
            print(f"[MainWindow] Signal connection error: {e}")
    
    def _start_monitoring(self):
        """Start monitoring (Stage 7: via Bridge)"""
        if not self.bridge:
            print("[MainWindow] No bridge, skipping monitoring start")
            return
        
        try:
            # STAGE 7: Use command instead of direct call
            command = StartMonitoringCommand(interval=100)
            result = self.bridge.execute_command(command)
            
            if result.success:
                print("[MainWindow] ✅ Monitoring started via Bridge")
                self.statusBar().showMessage("Monitoring active")
            else:
                print(f"[MainWindow] ⚠️ Monitoring failed: {result.error}")
                self.statusBar().showMessage(f"Monitoring error: {result.error}")
        
        except Exception as e:
            print(f"[MainWindow] Monitoring start error: {e}")
    
    def _update_ui(self):
        """Update UI (fallback timer)"""
        try:
            # Update widgets that need periodic refresh
            # Most updates now come via Qt signals (Stage 7)
            pass
        
        except Exception as e:
            print(f"[MainWindow] UI update error: {e}")
    
    # ========================================================================
    # STAGE 7: Qt Signal Handlers
    # ========================================================================
    
    def _on_data_updated(self, data_type: str, data: dict):
        """Handle data update signal (Stage 7)"""
        try:
            # Forward to widgets
            if data_type == 'performance_metrics':
                if self.dashboard_widget and hasattr(self.dashboard_widget, '_on_data_updated'):
                    self.dashboard_widget._on_data_updated(data_type, data)
                
                if self.performance_widget and hasattr(self.performance_widget, '_on_data_updated'):
                    self.performance_widget._on_data_updated(data_type, data)
        
        except Exception as e:
            print(f"[MainWindow] Data update handler error: {e}")
    
    def _on_command_completed(self, command_id: str, success: bool):
        """Handle command completion signal (Stage 7)"""
        if success:
            print(f"[MainWindow] Command {command_id} completed")
        else:
            print(f"[MainWindow] Command {command_id} failed")
    
    def _on_error(self, component: str, error: str):
        """Handle error signal (Stage 7)"""
        print(f"[MainWindow] Error in {component}: {error}")
        self.statusBar().showMessage(f"Error: {error}", 5000)
    
    def _on_status_changed(self, component: str, status: str):
        """Handle status change signal (Stage 7)"""
        print(f"[MainWindow] {component}: {status}")
        self.statusBar().showMessage(f"{component}: {status}", 2000)
    
    # ========================================================================
    # Window Events
    # ========================================================================
    
    def closeEvent(self, event):
        """Handle window close"""
        try:
            # Stop update timer
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            
            # STAGE 7: Stop monitoring via Bridge
            if self.bridge:
                command = StopMonitoringCommand()
                self.bridge.execute_command(command)
            
            print("[MainWindow] Closing...")
            event.accept()
        
        except Exception as e:
            print(f"[MainWindow] Close error: {e}")
            event.accept()
