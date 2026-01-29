#!/usr/bin/env python3
"""Monitoring GUI Example

Version: 0.3.5u (package 3.9a, stage 7.7b.8/7.7)

Demonstrates GUI integration with monitoring system.
"""
import sys
import os
import time
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
    from PyQt6.QtCore import QTimer, Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Error: PyQt6 not available")
    print("Install with: pip install PyQt6")
    sys.exit(1)

from core.error_reporter import ErrorReporter, ErrorSeverity
from core.system_health_monitor import SystemHealthMonitor
from core.recovery_coordinator import RecoveryCoordinator, RecoveryStrategy
from ui.widgets.monitoring_panel import MonitoringPanel
from ui.widgets.alert_notification import AlertNotificationManager


class DemoWindow(QMainWindow):
    """Demo window with monitoring"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitoring System Demo - v0.3.5u")
        self.resize(1200, 800)
        
        # Create monitoring systems
        self.error_reporter = ErrorReporter()
        self.health_monitor = SystemHealthMonitor(
            check_interval=2.0,
            error_reporter=self.error_reporter
        )
        self.recovery_coordinator = RecoveryCoordinator(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter
        )
        
        # Component states
        self.components = {
            'ConfigManager': {'running': True},
            'PerformanceMonitor': {'running': True},
            'GameDetector': {'running': True}
        }
        
        # Setup
        self._setup_components()
        self._init_ui()
        self._start_monitoring()
    
    def _setup_components(self):
        """Setup monitoring for components"""
        for component in self.components:
            # Health check
            self.health_monitor.register_component(
                component,
                health_check=lambda c=component: self.components[c]['running'],
                get_metrics=lambda c=component: {'running': self.components[c]['running']}
            )
            
            # Recovery
            self.recovery_coordinator.register_recovery(
                component,
                RecoveryStrategy.RESTART,
                action=lambda c=component: self._restart_component(c),
                max_attempts=3
            )
    
    def _restart_component(self, component: str) -> bool:
        """Restart component"""
        self.components[component]['running'] = True
        return True
    
    def _init_ui(self):
        """Initialize UI"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Monitoring System Demo")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Info
        info = QLabel("Version 0.3.5u (Package 3.9a, Stage 7.7 COMPLETE)")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # Demo controls
        controls_layout = QVBoxLayout()
        
        btn_warning = QPushButton("Simulate Warning Error")
        btn_warning.clicked.connect(lambda: self._simulate_error(ErrorSeverity.WARNING))
        controls_layout.addWidget(btn_warning)
        
        btn_error = QPushButton("Simulate Error")
        btn_error.clicked.connect(lambda: self._simulate_error(ErrorSeverity.ERROR))
        controls_layout.addWidget(btn_error)
        
        btn_critical = QPushButton("Simulate Critical Error")
        btn_critical.clicked.connect(lambda: self._simulate_error(ErrorSeverity.CRITICAL))
        controls_layout.addWidget(btn_critical)
        
        layout.addLayout(controls_layout)
        
        # Monitoring panel
        self.monitoring_panel = MonitoringPanel()
        self.monitoring_panel.set_monitoring_systems(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter,
            recovery_coordinator=self.recovery_coordinator
        )
        layout.addWidget(self.monitoring_panel)
        
        # Alert manager
        self.alert_manager = AlertNotificationManager(self)
        self.health_monitor.add_alert_callback(self._on_alert)
    
    def _start_monitoring(self):
        """Start monitoring"""
        self.health_monitor.start()
        self.recovery_coordinator.enable_auto_recovery()
        self.monitoring_panel.start_updates(interval=2000)
    
    def _simulate_error(self, severity: ErrorSeverity):
        """Simulate error"""
        import random
        component = random.choice(list(self.components.keys()))
        
        self.error_reporter.report_error(
            component,
            f"Simulated {severity.value} error",
            severity=severity
        )
        
        if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.components[component]['running'] = False
    
    def _on_alert(self, alert):
        """Handle alert"""
        alert_data = {
            'level': alert.level.value,
            'component': alert.component,
            'message': alert.message,
            'details': alert.details
        }
        self.alert_manager.show_alert(alert_data)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.monitoring_panel.stop_updates()
        self.health_monitor.stop()
        event.accept()


def main():
    """Main function"""
    print("\nStarting Monitoring GUI Demo...\n")
    print("Version: 0.3.5u (Package 3.9a, Stage 7.7 COMPLETE)")
    print("\nFeatures:")
    print("  - Real-time monitoring")
    print("  - Error reporting")
    print("  - Auto-recovery")
    print("  - Alert notifications")
    print("\nClick buttons to simulate errors and watch the system recover!\n")
    
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    if not PYQT_AVAILABLE:
        sys.exit(1)
    main()
