#!/usr/bin/env python3
"""Historical Data Viewer - View historical monitoring data with charts

Version: 0.3.5f (package 3.9a, stage 7.7b.8.2/7.7b.8)

Package 3.9a Stage 7.7b.8.2: Historical data visualization.

Features:
- Multiple chart types
- Time range selection
- Component filtering
- Metric selection
- Real-time updates
- Data export
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTabWidget, QGroupBox,
    QDateTimeEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from typing import Optional, Dict, Any, List
import time

try:
    from ui.widgets.chart_widget import (
        LineChartWidget, BarChartWidget, PieChartWidget,
        PYQTGRAPH_AVAILABLE
    )
except ImportError:
    PYQTGRAPH_AVAILABLE = False


class HistoricalDataViewer(QWidget):
    """Historical data visualization widget
    
    v0.3.5f (package 3.9a, stage 7.7b.8.2/7.7b.8)
    
    Features:
    - Health status timeline
    - Error rate charts
    - Recovery success charts
    - Component comparison
    - Time range selection
    - Auto-refresh
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._historical_store = None
        self._update_timer = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Check availability
        if not PYQTGRAPH_AVAILABLE:
            error_label = QLabel(
                "PyQtGraph not available. Charts disabled.\n"
                "Install with: pip install pyqtgraph"
            )
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            return
        
        # Controls
        controls_group = QGroupBox("View Options")
        controls_layout = QVBoxLayout()
        
        # Time range selection
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Time Range:"))
        
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems([
            "Last Hour",
            "Last 6 Hours",
            "Last 24 Hours",
            "Last 7 Days",
            "Last 30 Days",
            "Custom"
        ])
        self.time_range_combo.setCurrentText("Last 24 Hours")
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)
        time_layout.addWidget(self.time_range_combo)
        
        # Custom time range
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.start_time_edit.setEnabled(False)
        time_layout.addWidget(QLabel("From:"))
        time_layout.addWidget(self.start_time_edit)
        
        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setDateTime(QDateTime.currentDateTime())
        self.end_time_edit.setEnabled(False)
        time_layout.addWidget(QLabel("To:"))
        time_layout.addWidget(self.end_time_edit)
        
        time_layout.addStretch()
        controls_layout.addLayout(time_layout)
        
        # Component selection
        component_layout = QHBoxLayout()
        component_layout.addWidget(QLabel("Component:"))
        
        self.component_combo = QComboBox()
        self.component_combo.addItems(["All Components", "System"])
        component_layout.addWidget(self.component_combo)
        
        # Auto-refresh
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.stateChanged.connect(self._on_auto_refresh_changed)
        component_layout.addWidget(self.auto_refresh_checkbox)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Now")
        self.refresh_btn.clicked.connect(self.refresh_data)
        component_layout.addWidget(self.refresh_btn)
        
        component_layout.addStretch()
        controls_layout.addLayout(component_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Charts
        self.chart_tabs = QTabWidget()
        
        # Health status timeline
        self.health_chart = LineChartWidget()
        self.chart_tabs.addTab(self.health_chart, "Health Timeline")
        
        # Error rate chart
        self.error_chart = BarChartWidget()
        self.chart_tabs.addTab(self.error_chart, "Error Rate")
        
        # Recovery success chart
        self.recovery_chart = PieChartWidget()
        self.chart_tabs.addTab(self.recovery_chart, "Recovery Success")
        
        # Component comparison
        self.comparison_chart = BarChartWidget()
        self.chart_tabs.addTab(self.comparison_chart, "Component Comparison")
        
        layout.addWidget(self.chart_tabs)
    
    def set_historical_store(self, historical_store: Any):
        """Set historical data store
        
        Args:
            historical_store: HistoricalDataStore instance
        """
        self._historical_store = historical_store
        self.refresh_data()
    
    def _on_time_range_changed(self, text: str):
        """Handle time range selection change"""
        is_custom = text == "Custom"
        self.start_time_edit.setEnabled(is_custom)
        self.end_time_edit.setEnabled(is_custom)
        
        if not is_custom:
            self.refresh_data()
    
    def _on_auto_refresh_changed(self, state: int):
        """Handle auto-refresh toggle"""
        if state == Qt.CheckState.Checked.value:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        if not self._update_timer:
            self._update_timer = QTimer(self)
            self._update_timer.timeout.connect(self.refresh_data)
        
        self._update_timer.start(30000)  # 30 seconds
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self._update_timer:
            self._update_timer.stop()
    
    def _get_time_range(self) -> tuple[float, float]:
        """Get selected time range
        
        Returns:
            (start_time, end_time) tuple
        """
        end_time = time.time()
        
        time_range = self.time_range_combo.currentText()
        
        if time_range == "Last Hour":
            start_time = end_time - 3600
        elif time_range == "Last 6 Hours":
            start_time = end_time - (6 * 3600)
        elif time_range == "Last 24 Hours":
            start_time = end_time - (24 * 3600)
        elif time_range == "Last 7 Days":
            start_time = end_time - (7 * 86400)
        elif time_range == "Last 30 Days":
            start_time = end_time - (30 * 86400)
        else:  # Custom
            start_time = self.start_time_edit.dateTime().toSecsSinceEpoch()
            end_time = self.end_time_edit.dateTime().toSecsSinceEpoch()
        
        return start_time, end_time
    
    def refresh_data(self):
        """Refresh all charts with latest data"""
        if not self._historical_store or not PYQTGRAPH_AVAILABLE:
            return
        
        try:
            start_time, end_time = self._get_time_range()
            component = self.component_combo.currentText()
            
            if component == "All Components":
                component = None
            elif component == "System":
                component = "_system"
            
            # Update health timeline
            self._update_health_timeline(start_time, end_time, component)
            
            # Update error rate
            self._update_error_rate(start_time, end_time, component)
            
            # Update recovery success
            self._update_recovery_success(start_time, end_time, component)
            
            # Update component comparison
            self._update_component_comparison(start_time, end_time)
        
        except Exception as e:
            print(f"Error refreshing data: {e}")
    
    def _update_health_timeline(self, start_time: float, end_time: float, component: Optional[str]):
        """Update health timeline chart"""
        # Query health data
        records = self._historical_store.query_health_history(
            start_time,
            end_time,
            component=component,
            limit=1000
        )
        
        if not records:
            self.health_chart.clear()
            return
        
        # Convert to chart data (status to numeric)
        status_map = {
            'healthy': 100,
            'degraded': 75,
            'unhealthy': 50,
            'critical': 25,
            'unknown': 0
        }
        
        x_data = [r['timestamp'] for r in reversed(records)]
        y_data = [status_map.get(r['status'], 0) for r in reversed(records)]
        
        self.health_chart.set_data(x_data, y_data)
    
    def _update_error_rate(self, start_time: float, end_time: float, component: Optional[str]):
        """Update error rate chart"""
        # Query errors
        errors = self._historical_store.query_errors(
            start_time,
            end_time,
            component=component,
            limit=1000
        )
        
        if not errors:
            self.error_chart.clear()
            return
        
        # Group by hour
        hour_counts = {}
        for error in errors:
            hour = int(error['timestamp'] / 3600) * 3600
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Convert to chart data
        x_data = list(range(len(hour_counts)))
        y_data = list(hour_counts.values())
        
        self.error_chart.set_data(x_data, y_data)
    
    def _update_recovery_success(self, start_time: float, end_time: float, component: Optional[str]):
        """Update recovery success chart"""
        # Query recoveries
        recoveries = self._historical_store.query_recoveries(
            start_time,
            end_time,
            component=component,
            limit=1000
        )
        
        if not recoveries:
            self.recovery_chart.clear()
            return
        
        # Count by status
        status_counts = {}
        for recovery in recoveries:
            status = recovery['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Convert to chart data
        labels = list(status_counts.keys())
        values = list(status_counts.values())
        
        self.recovery_chart.set_data([], values, labels)
    
    def _update_component_comparison(self, start_time: float, end_time: float):
        """Update component comparison chart"""
        # Query all components
        records = self._historical_store.query_health_history(
            start_time,
            end_time,
            limit=10000
        )
        
        if not records:
            self.comparison_chart.clear()
            return
        
        # Count health checks by component
        component_counts = {}
        component_healthy = {}
        
        for record in records:
            component = record['component']
            if component == '_system':
                continue
            
            component_counts[component] = component_counts.get(component, 0) + 1
            
            if record['status'] == 'healthy':
                component_healthy[component] = component_healthy.get(component, 0) + 1
        
        # Calculate success rates
        components = []
        success_rates = []
        
        for component, total in component_counts.items():
            healthy = component_healthy.get(component, 0)
            success_rate = (healthy / total * 100) if total > 0 else 0
            components.append(component)
            success_rates.append(success_rate)
        
        # Update component combo
        current_component = self.component_combo.currentText()
        self.component_combo.clear()
        self.component_combo.addItem("All Components")
        self.component_combo.addItem("System")
        self.component_combo.addItems(components)
        
        # Restore selection
        index = self.component_combo.findText(current_component)
        if index >= 0:
            self.component_combo.setCurrentIndex(index)
        
        # Convert to chart data
        x_data = list(range(len(components)))
        
        self.comparison_chart.set_data(x_data, success_rates, components)


# Testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    viewer = HistoricalDataViewer()
    viewer.setWindowTitle("Historical Data Viewer Test")
    viewer.resize(1000, 700)
    viewer.show()
    
    sys.exit(app.exec())
