#!/usr/bin/env python3
"""Main Window Complete - Full application window

Version: 0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)

Package 3.9a Stage 7.7b.9.1: Complete main window with all features.

Features:
- Multiple tabs (Status, History, Settings)
- Monitoring panel
- Historical data viewer
- Settings panel
- System tray integration
"""
try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QPushButton, QGroupBox,
        QSystemTrayIcon, QMenu, QMessageBox
    )
    from PyQt6.QtCore import QTimer, Qt
    from PyQt6.QtGui import QIcon, QAction
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from typing import Optional
import time

try:
    from core.system_integrator_final import SystemIntegratorFinal, SystemStatus
except ImportError:
    SystemIntegratorFinal = None
    SystemStatus = None

try:
    from ui.widgets.monitoring_panel import MonitoringPanel
except ImportError:
    MonitoringPanel = None

try:
    from ui.widgets.historical_data_viewer import HistoricalDataViewer
except ImportError:
    HistoricalDataViewer = None


class StatusTab(QWidget):
    """Status tab widget"""
    
    def __init__(self, integrator: Optional[SystemIntegratorFinal] = None):
        super().__init__()
        self.integrator = integrator
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # System status group
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Initializing...")
        status_layout.addWidget(self.status_label)
        
        self.uptime_label = QLabel("Uptime: 0s")
        status_layout.addWidget(self.uptime_label)
        
        self.components_label = QLabel("Components: 0/0 healthy")
        status_layout.addWidget(self.components_label)
        
        self.errors_label = QLabel("Errors: 0")
        status_layout.addWidget(self.errors_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Monitoring panel
        if MonitoringPanel:
            self.monitoring_panel = MonitoringPanel()
            layout.addWidget(self.monitoring_panel)
        else:
            layout.addWidget(QLabel("Monitoring panel not available"))
        
        layout.addStretch()
    
    def update_status(self, status: SystemStatus):
        """Update status display"""
        self.status_label.setText(
            f"Status: {'Running' if status.running else 'Stopped'}"
        )
        self.uptime_label.setText(f"Uptime: {status.uptime:.0f}s")
        self.components_label.setText(
            f"Components: {status.healthy_count}/{status.component_count} healthy"
        )
        self.errors_label.setText(f"Errors: {status.error_count}")


class SettingsTab(QWidget):
    """Settings tab widget"""
    
    def __init__(self, integrator: Optional[SystemIntegratorFinal] = None):
        super().__init__()
        self.integrator = integrator
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Settings groups
        settings_label = QLabel("<h2>Application Settings</h2>")
        layout.addWidget(settings_label)
        
        # Monitoring settings
        monitoring_group = QGroupBox("Monitoring")
        monitoring_layout = QVBoxLayout()
        monitoring_layout.addWidget(QLabel("Check Interval: 5.0s"))
        monitoring_layout.addWidget(QLabel("Auto-recovery: Enabled"))
        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)
        
        # Historical data settings
        history_group = QGroupBox("Historical Data")
        history_layout = QVBoxLayout()
        history_layout.addWidget(QLabel("Retention: 30 days"))
        history_layout.addWidget(QLabel("Collection: Every 60s"))
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # UI settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QVBoxLayout()
        ui_layout.addWidget(QLabel("Theme: Light"))
        ui_layout.addWidget(QLabel("Notifications: Enabled"))
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
    
    def _save_settings(self):
        """Save settings"""
        if self.integrator and self.integrator.config_manager:
            if self.integrator.config_manager.save():
                QMessageBox.information(
                    self,
                    "Settings Saved",
                    "Settings saved successfully!"
                )


class MainWindowComplete(QMainWindow):
    """Complete main application window
    
    v0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)
    
    Features:
    - Status tab with monitoring panel
    - History tab with data viewer
    - Settings tab
    - System tray integration
    - Auto-update status
    """
    
    def __init__(self, integrator: Optional[SystemIntegratorFinal] = None):
        super().__init__()
        self.integrator = integrator or SystemIntegratorFinal()
        self._update_timer = None
        self._init_ui()
        self._setup_system_tray()
        self._start_status_updates()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("PartMart Boost - Gaming Performance Optimizer")
        
        # Get window size from config
        if self.integrator.config_manager:
            width = self.integrator.config_manager.get('ui.window_width', 1200)
            height = self.integrator.config_manager.get('ui.window_height', 800)
            self.resize(width, height)
        else:
            self.resize(1200, 800)
        
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("<h1>PartMart Boost v0.3.5g</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Status tab
        self.status_tab = StatusTab(self.integrator)
        self.tabs.addTab(self.status_tab, "Status")
        
        # History tab
        if HistoricalDataViewer:
            self.history_tab = HistoricalDataViewer()
            if self.integrator.historical_store:
                self.history_tab.set_historical_store(
                    self.integrator.historical_store
                )
            self.tabs.addTab(self.history_tab, "History")
        else:
            history_placeholder = QLabel("Historical data viewer not available")
            history_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabs.addTab(history_placeholder, "History")
        
        # Settings tab
        self.settings_tab = SettingsTab(self.integrator)
        self.tabs.addTab(self.settings_tab, "Settings")
        
        layout.addWidget(self.tabs)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self._start_monitoring)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.clicked.connect(self._stop_monitoring)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _setup_system_tray(self):
        """Setup system tray icon"""
        if not self.integrator.config_manager:
            return
        
        show_tray = self.integrator.config_manager.get(
            'ui.show_system_tray', True
        )
        
        if not show_tray:
            return
        
        # Create tray icon (would use actual icon in production)
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon('path/to/icon.png'))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _start_status_updates(self):
        """Start periodic status updates"""
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_status)
        self._update_timer.start(1000)  # Update every second
    
    def _update_status(self):
        """Update status display"""
        if self.integrator:
            status = self.integrator.get_status()
            self.status_tab.update_status(status)
            
            # Update monitoring panel
            if hasattr(self.status_tab, 'monitoring_panel'):
                if self.integrator.health_monitor:
                    health = self.integrator.health_monitor.get_system_health()
                    self.status_tab.monitoring_panel.update_health(health)
    
    def _start_monitoring(self):
        """Start monitoring systems"""
        if self.integrator.start():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            QMessageBox.information(
                self,
                "Monitoring Started",
                "System monitoring started successfully!"
            )
    
    def _stop_monitoring(self):
        """Stop monitoring systems"""
        if self.integrator.stop():
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            QMessageBox.information(
                self,
                "Monitoring Stopped",
                "System monitoring stopped."
            )
    
    def closeEvent(self, event):
        """Handle window close"""
        # Stop systems
        if self.integrator and self.integrator._running:
            self.integrator.stop()
        
        event.accept()


# Testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create integrator
    integrator = SystemIntegratorFinal()
    integrator.initialize()
    
    # Create window
    window = MainWindowComplete(integrator)
    window.show()
    
    sys.exit(app.exec())
