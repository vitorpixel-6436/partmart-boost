#!/usr/bin/env python3
"""Main Window with Monitoring Integration

Version: 0.3.5t (package 3.9a, stage 7.7b.7/7.7)

Extends main window with monitoring panel integration.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QDockWidget
)
from PyQt6.QtCore import Qt
from typing import Optional

try:
    from ui.widgets.monitoring_panel import MonitoringPanel
    from ui.widgets.alert_notification import AlertNotificationManager
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


class MainWindowMonitoring(QMainWindow):
    """Main window with monitoring integration
    
    v0.3.5t (package 3.9a, stage 7.7b.7/7.7)
    
    Extends main application window with:
    - Monitoring panel (dock widget)
    - Alert notifications
    - Health status bar
    """
    
    def __init__(self, integrator=None, parent=None):
        super().__init__(parent)
        self._integrator = integrator
        self._monitoring_panel = None
        self._alert_manager = None
        
        self._init_ui()
        self._setup_monitoring()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("PartMart Boost - Monitoring")
        self.resize(1200, 800)
        
        # Central widget
        central = QWidget()
        layout = QVBoxLayout(central)
        
        # Main content tabs
        self.main_tabs = QTabWidget()
        
        # Add your main application tabs here
        # Example: self.main_tabs.addTab(dashboard, "Dashboard")
        
        layout.addWidget(self.main_tabs)
        self.setCentralWidget(central)
        
        # Menu bar
        self._create_menu_bar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create monitoring dock
        if MONITORING_AVAILABLE:
            self._create_monitoring_dock()
        
        # Alert manager
        if MONITORING_AVAILABLE:
            self._alert_manager = AlertNotificationManager(self)
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        if MONITORING_AVAILABLE and self._monitoring_dock:
            view_menu.addAction(self._monitoring_dock.toggleViewAction())
        
        # Monitoring menu
        if MONITORING_AVAILABLE:
            monitoring_menu = menubar.addMenu("Monitoring")
            
            monitoring_menu.addAction("Refresh Status", self._refresh_monitoring)
            monitoring_menu.addAction("Clear Errors", self._clear_errors)
            monitoring_menu.addSeparator()
            monitoring_menu.addAction("Export Error Report", self._export_error_report)
    
    def _create_monitoring_dock(self):
        """Create monitoring dock widget"""
        self._monitoring_dock = QDockWidget("System Monitoring", self)
        self._monitoring_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea |
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        
        # Create monitoring panel
        self._monitoring_panel = MonitoringPanel()
        self._monitoring_dock.setWidget(self._monitoring_panel)
        
        # Add to window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._monitoring_dock)
    
    def _setup_monitoring(self):
        """Setup monitoring systems"""
        if not self._integrator or not MONITORING_AVAILABLE:
            return
        
        try:
            # Get monitoring systems from integrator
            health_monitor = getattr(self._integrator, 'health_monitor', None)
            error_reporter = getattr(self._integrator, 'error_reporter', None)
            recovery_coordinator = getattr(self._integrator, 'recovery_coordinator', None)
            
            # Set in monitoring panel
            if self._monitoring_panel:
                self._monitoring_panel.set_monitoring_systems(
                    health_monitor=health_monitor,
                    error_reporter=error_reporter,
                    recovery_coordinator=recovery_coordinator
                )
            
            # Setup alert callbacks
            if health_monitor and self._alert_manager:
                health_monitor.add_alert_callback(self._on_health_alert)
        
        except Exception as e:
            print(f"Error setting up monitoring: {e}")
    
    def _on_health_alert(self, alert):
        """Handle health alert
        
        Args:
            alert: Health alert object
        """
        if not self._alert_manager:
            return
        
        try:
            alert_data = {
                'level': alert.level.value,
                'component': alert.component,
                'message': alert.message,
                'details': alert.details
            }
            self._alert_manager.show_alert(alert_data)
            
            # Update status bar
            self.status_bar.showMessage(
                f"Alert: {alert.component} - {alert.message}",
                5000
            )
        
        except Exception as e:
            print(f"Error handling alert: {e}")
    
    def _refresh_monitoring(self):
        """Refresh monitoring displays"""
        if self._monitoring_panel:
            self._monitoring_panel.update_displays()
    
    def _clear_errors(self):
        """Clear all errors"""
        if self._integrator:
            error_reporter = getattr(self._integrator, 'error_reporter', None)
            if error_reporter:
                error_reporter.clear_all()
                self._refresh_monitoring()
    
    def _export_error_report(self):
        """Export error report"""
        if not self._integrator:
            return
        
        try:
            error_reporter = getattr(self._integrator, 'error_reporter', None)
            if error_reporter:
                from PyQt6.QtWidgets import QFileDialog
                import time
                
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export Error Report",
                    f"error_report_{int(time.time())}.html",
                    "HTML Files (*.html);;Text Files (*.txt);;JSON Files (*.json)"
                )
                
                if filename:
                    # Determine format from extension
                    if filename.endswith('.html'):
                        format_type = 'html'
                    elif filename.endswith('.txt'):
                        format_type = 'text'
                    else:
                        format_type = 'json'
                    
                    error_reporter.export_report(filename, format=format_type)
                    self.status_bar.showMessage(f"Report exported to {filename}", 3000)
        
        except Exception as e:
            print(f"Error exporting report: {e}")
            self.status_bar.showMessage(f"Export failed: {e}", 5000)


# Testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    window = MainWindowMonitoring()
    window.show()
    
    sys.exit(app.exec())
