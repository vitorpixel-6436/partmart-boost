#!/usr/bin/env python3
"""Monitoring Panel Widget - GUI Integration

Version: 0.3.5t (package 3.9a, stage 7.7b.7.1/7.7)

Package 3.9a Stage 7.7b.7.1: GUI integration for monitoring systems.

Features:
- Real-time system health display
- Component status overview
- Error viewer
- Recovery control
- Statistics dashboard
- Alert notifications
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QProgressBar,
    QTabWidget, QTextEdit, QComboBox, QSpinBox, QCheckBox,
    QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from typing import Optional, Dict, Any, List
import time


class SystemHealthWidget(QWidget):
    """System health status widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._health_monitor = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Status indicator
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("System Status:")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        
        self.status_indicator = QLabel("UNKNOWN")
        self.status_indicator.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.status_indicator.setStyleSheet(
            "background-color: #808080; color: white; padding: 5px 15px; border-radius: 3px;"
        )
        status_layout.addWidget(self.status_indicator)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Components summary
        summary_layout = QHBoxLayout()
        
        self.total_label = self._create_stat_label("Total", "0", "#3498db")
        self.healthy_label = self._create_stat_label("Healthy", "0", "#2ecc71")
        self.degraded_label = self._create_stat_label("Degraded", "0", "#f39c12")
        self.unhealthy_label = self._create_stat_label("Unhealthy", "0", "#e74c3c")
        self.critical_label = self._create_stat_label("Critical", "0", "#c0392b")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.healthy_label)
        summary_layout.addWidget(self.degraded_label)
        summary_layout.addWidget(self.unhealthy_label)
        summary_layout.addWidget(self.critical_label)
        
        layout.addLayout(summary_layout)
        
        # Statistics
        stats_group = QGroupBox("Monitoring Statistics")
        stats_layout = QVBoxLayout()
        
        self.uptime_label = QLabel("Uptime: --")
        self.checks_label = QLabel("Total Checks: --")
        self.success_rate_label = QLabel("Success Rate: --%")
        
        stats_layout.addWidget(self.uptime_label)
        stats_layout.addWidget(self.checks_label)
        stats_layout.addWidget(self.success_rate_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
    
    def _create_stat_label(self, title: str, value: str, color: str) -> QFrame:
        """Create statistic label"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        frame.setStyleSheet(f"border: 2px solid {color}; border-radius: 5px; padding: 5px;")
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 9))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        frame.value_label = value_label  # Store for updates
        return frame
    
    def set_health_monitor(self, health_monitor: Any):
        """Set health monitor instance"""
        self._health_monitor = health_monitor
    
    def update_health(self, health_data: Dict[str, Any]):
        """Update health display"""
        if not health_data:
            return
        
        # Update status
        status = health_data.get('status', 'unknown').upper()
        self.status_indicator.setText(status)
        
        # Status colors
        colors = {
            'HEALTHY': '#2ecc71',
            'DEGRADED': '#f39c12',
            'UNHEALTHY': '#e74c3c',
            'CRITICAL': '#c0392b',
            'UNKNOWN': '#808080'
        }
        color = colors.get(status, '#808080')
        self.status_indicator.setStyleSheet(
            f"background-color: {color}; color: white; padding: 5px 15px; border-radius: 3px;"
        )
        
        # Update counts
        self.total_label.value_label.setText(str(health_data.get('total_components', 0)))
        self.healthy_label.value_label.setText(str(health_data.get('healthy_count', 0)))
        self.degraded_label.value_label.setText(str(health_data.get('degraded_count', 0)))
        self.unhealthy_label.value_label.setText(str(health_data.get('unhealthy_count', 0)))
        self.critical_label.value_label.setText(str(health_data.get('critical_count', 0)))
        
        # Update statistics
        stats = health_data.get('statistics', {})
        
        uptime = stats.get('uptime', 0)
        if uptime >= 3600:
            uptime_str = f"{uptime/3600:.1f}h"
        elif uptime >= 60:
            uptime_str = f"{uptime/60:.1f}m"
        else:
            uptime_str = f"{uptime:.0f}s"
        
        self.uptime_label.setText(f"Uptime: {uptime_str}")
        self.checks_label.setText(f"Total Checks: {stats.get('total_checks', 0)}")
        self.success_rate_label.setText(f"Success Rate: {stats.get('success_rate', 0):.1f}%")


class ComponentStatusWidget(QWidget):
    """Component status table widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Components table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Component", "Status", "Message", "Checks", "Last Check"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
    
    def update_components(self, components: Dict[str, Dict[str, Any]]):
        """Update components table"""
        self.table.setRowCount(0)
        
        for name, data in components.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Component name
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            # Status with color
            status = data.get('status', 'unknown')
            status_item = QTableWidgetItem(status.upper())
            
            colors = {
                'healthy': QColor('#2ecc71'),
                'degraded': QColor('#f39c12'),
                'unhealthy': QColor('#e74c3c'),
                'critical': QColor('#c0392b'),
                'unknown': QColor('#808080')
            }
            status_item.setBackground(colors.get(status, QColor('#808080')))
            status_item.setForeground(QColor('white'))
            self.table.setItem(row, 1, status_item)
            
            # Message
            self.table.setItem(row, 2, QTableWidgetItem(data.get('message', '')))
            
            # Consecutive failures
            failures = data.get('consecutive_failures', 0)
            self.table.setItem(row, 3, QTableWidgetItem(str(failures)))
            
            # Last check
            last_check = data.get('last_check', 0)
            if last_check > 0:
                ago = time.time() - last_check
                if ago < 60:
                    time_str = f"{ago:.0f}s ago"
                elif ago < 3600:
                    time_str = f"{ago/60:.0f}m ago"
                else:
                    time_str = f"{ago/3600:.1f}h ago"
            else:
                time_str = "Never"
            
            self.table.setItem(row, 4, QTableWidgetItem(time_str))
        
        self.table.resizeColumnsToContents()


class ErrorViewerWidget(QWidget):
    """Error viewer widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._error_reporter = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Filter by severity:"))
        
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.severity_combo.setCurrentText("WARNING")
        self.severity_combo.currentTextChanged.connect(self.refresh_errors)
        controls_layout.addWidget(self.severity_combo)
        
        controls_layout.addWidget(QLabel("Limit:"))
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(10, 1000)
        self.limit_spin.setValue(100)
        self.limit_spin.setSingleStep(10)
        controls_layout.addWidget(self.limit_spin)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_errors)
        controls_layout.addWidget(self.refresh_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_errors)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Errors table
        self.errors_table = QTableWidget()
        self.errors_table.setColumnCount(5)
        self.errors_table.setHorizontalHeaderLabels([
            "Time", "Severity", "Component", "Message", "Count"
        ])
        self.errors_table.horizontalHeader().setStretchLastSection(True)
        self.errors_table.setAlternatingRowColors(True)
        self.errors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.errors_table)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Total errors: 0")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
    
    def set_error_reporter(self, error_reporter: Any):
        """Set error reporter instance"""
        self._error_reporter = error_reporter
        self.refresh_errors()
    
    def refresh_errors(self):
        """Refresh error list"""
        if not self._error_reporter:
            return
        
        try:
            # Get severity filter
            severity_filter = self.severity_combo.currentText()
            min_severity = None
            
            if severity_filter != "ALL":
                from core.error_reporter import ErrorSeverity
                severity_map = {
                    'DEBUG': ErrorSeverity.DEBUG,
                    'INFO': ErrorSeverity.INFO,
                    'WARNING': ErrorSeverity.WARNING,
                    'ERROR': ErrorSeverity.ERROR,
                    'CRITICAL': ErrorSeverity.CRITICAL
                }
                min_severity = severity_map.get(severity_filter)
            
            # Get errors
            errors = self._error_reporter.get_errors(
                min_severity=min_severity,
                limit=self.limit_spin.value()
            )
            
            # Update table
            self.errors_table.setRowCount(0)
            
            for error in errors:
                row = self.errors_table.rowCount()
                self.errors_table.insertRow(row)
                
                # Timestamp
                timestamp = error.get('timestamp', 0)
                time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
                self.errors_table.setItem(row, 0, QTableWidgetItem(time_str))
                
                # Severity with color
                severity = error.get('severity', 'info').upper()
                severity_item = QTableWidgetItem(severity)
                
                colors = {
                    'DEBUG': QColor('#808080'),
                    'INFO': QColor('#3498db'),
                    'WARNING': QColor('#f39c12'),
                    'ERROR': QColor('#e74c3c'),
                    'CRITICAL': QColor('#c0392b')
                }
                severity_item.setBackground(colors.get(severity, QColor('#808080')))
                severity_item.setForeground(QColor('white'))
                self.errors_table.setItem(row, 1, severity_item)
                
                # Component
                self.errors_table.setItem(row, 2, QTableWidgetItem(error.get('component', '')))
                
                # Message
                self.errors_table.setItem(row, 3, QTableWidgetItem(error.get('message', '')))
                
                # Count
                self.errors_table.setItem(row, 4, QTableWidgetItem(str(error.get('count', 1))))
            
            self.errors_table.resizeColumnsToContents()
            
            # Update statistics
            stats = self._error_reporter.get_statistics()
            self.stats_label.setText(
                f"Total errors: {stats.get('total_errors', 0)} | "
                f"Current records: {stats.get('current_errors', 0)}"
            )
        
        except Exception as e:
            print(f"Error refreshing errors: {e}")
    
    def clear_errors(self):
        """Clear all errors"""
        if self._error_reporter:
            self._error_reporter.clear_all()
            self.refresh_errors()


class RecoveryControlWidget(QWidget):
    """Recovery control widget"""
    
    recovery_requested = pyqtSignal(str)  # component name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._recovery_coordinator = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Auto-recovery control
        auto_group = QGroupBox("Auto-Recovery")
        auto_layout = QHBoxLayout()
        
        self.auto_recovery_checkbox = QCheckBox("Enable Auto-Recovery")
        self.auto_recovery_checkbox.stateChanged.connect(self._on_auto_recovery_changed)
        auto_layout.addWidget(self.auto_recovery_checkbox)
        
        auto_layout.addStretch()
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Statistics
        stats_group = QGroupBox("Recovery Statistics")
        stats_layout = QVBoxLayout()
        
        self.total_label = QLabel("Total Recoveries: 0")
        self.success_label = QLabel("Successful: 0")
        self.failed_label = QLabel("Failed: 0")
        self.rate_label = QLabel("Success Rate: 0.0%")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.success_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.rate_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Recovery history
        history_group = QGroupBox("Recent Recoveries")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Component", "Strategy", "Status", "Duration"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setMaximumHeight(200)
        
        history_layout.addWidget(self.history_table)
        
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.clicked.connect(self.refresh_history)
        history_layout.addWidget(refresh_btn)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
    
    def set_recovery_coordinator(self, recovery_coordinator: Any):
        """Set recovery coordinator instance"""
        self._recovery_coordinator = recovery_coordinator
        
        # Update auto-recovery checkbox
        if self._recovery_coordinator:
            self.auto_recovery_checkbox.setChecked(
                self._recovery_coordinator.is_auto_recovery_enabled()
            )
    
    def _on_auto_recovery_changed(self, state: int):
        """Handle auto-recovery checkbox change"""
        if not self._recovery_coordinator:
            return
        
        if state == Qt.CheckState.Checked.value:
            self._recovery_coordinator.enable_auto_recovery()
        else:
            self._recovery_coordinator.disable_auto_recovery()
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics display"""
        self.total_label.setText(f"Total Recoveries: {stats.get('total_recoveries', 0)}")
        self.success_label.setText(f"Successful: {stats.get('successful_recoveries', 0)}")
        self.failed_label.setText(f"Failed: {stats.get('failed_recoveries', 0)}")
        self.rate_label.setText(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
    
    def refresh_history(self):
        """Refresh recovery history"""
        if not self._recovery_coordinator:
            return
        
        try:
            history = self._recovery_coordinator.get_recovery_history(limit=20)
            
            self.history_table.setRowCount(0)
            
            for record in history:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                
                # Time
                timestamp = record.get('timestamp', 0)
                time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
                self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
                
                # Component
                self.history_table.setItem(row, 1, QTableWidgetItem(record.get('component', '')))
                
                # Strategy
                self.history_table.setItem(row, 2, QTableWidgetItem(record.get('strategy', '')))
                
                # Status with color
                status = record.get('status', 'unknown').upper()
                status_item = QTableWidgetItem(status)
                
                colors = {
                    'SUCCESS': QColor('#2ecc71'),
                    'FAILED': QColor('#e74c3c'),
                    'SKIPPED': QColor('#95a5a6'),
                    'PENDING': QColor('#3498db')
                }
                status_item.setBackground(colors.get(status, QColor('#808080')))
                status_item.setForeground(QColor('white'))
                self.history_table.setItem(row, 3, status_item)
                
                # Duration
                duration = record.get('duration', 0)
                self.history_table.setItem(row, 4, QTableWidgetItem(f"{duration:.2f}s"))
            
            self.history_table.resizeColumnsToContents()
        
        except Exception as e:
            print(f"Error refreshing history: {e}")


class MonitoringPanel(QWidget):
    """Complete monitoring panel widget
    
    v0.3.5t (package 3.9a, stage 7.7b.7.1/7.7)
    
    Integrates:
    - SystemHealthMonitor
    - ErrorReporter
    - RecoveryCoordinator
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._health_monitor = None
        self._error_reporter = None
        self._recovery_coordinator = None
        self._update_timer = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # System Health tab
        health_widget = QWidget()
        health_layout = QVBoxLayout(health_widget)
        
        self.health_widget = SystemHealthWidget()
        health_layout.addWidget(self.health_widget)
        
        self.components_widget = ComponentStatusWidget()
        health_layout.addWidget(self.components_widget)
        
        self.tabs.addTab(health_widget, "System Health")
        
        # Error Viewer tab
        self.error_viewer = ErrorViewerWidget()
        self.tabs.addTab(self.error_viewer, "Error Viewer")
        
        # Recovery Control tab
        self.recovery_control = RecoveryControlWidget()
        self.tabs.addTab(self.recovery_control, "Recovery Control")
        
        layout.addWidget(self.tabs)
    
    def set_monitoring_systems(
        self,
        health_monitor: Optional[Any] = None,
        error_reporter: Optional[Any] = None,
        recovery_coordinator: Optional[Any] = None
    ):
        """Set monitoring system instances"""
        self._health_monitor = health_monitor
        self._error_reporter = error_reporter
        self._recovery_coordinator = recovery_coordinator
        
        # Set instances in widgets
        if self._health_monitor:
            self.health_widget.set_health_monitor(self._health_monitor)
        
        if self._error_reporter:
            self.error_viewer.set_error_reporter(self._error_reporter)
        
        if self._recovery_coordinator:
            self.recovery_control.set_recovery_coordinator(self._recovery_coordinator)
        
        # Start update timer
        self.start_updates()
    
    def start_updates(self, interval: int = 2000):
        """Start automatic updates
        
        Args:
            interval: Update interval in milliseconds
        """
        if self._update_timer:
            self._update_timer.stop()
        
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self.update_displays)
        self._update_timer.start(interval)
        
        # Initial update
        self.update_displays()
    
    def stop_updates(self):
        """Stop automatic updates"""
        if self._update_timer:
            self._update_timer.stop()
    
    def update_displays(self):
        """Update all displays"""
        try:
            # Update health display
            if self._health_monitor:
                health_data = self._health_monitor.get_system_health()
                self.health_widget.update_health(health_data)
                
                components = health_data.get('components', {})
                self.components_widget.update_components(components)
            
            # Update recovery statistics
            if self._recovery_coordinator:
                stats = self._recovery_coordinator.get_statistics()
                self.recovery_control.update_statistics(stats)
        
        except Exception as e:
            print(f"Error updating displays: {e}")


# Testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    panel = MonitoringPanel()
    panel.setWindowTitle("Monitoring Panel Test")
    panel.resize(900, 600)
    panel.show()
    
    sys.exit(app.exec())
