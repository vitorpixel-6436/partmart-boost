#!/usr/bin/env python3
"""Chart Widget - Data visualization using PyQtGraph

Version: 0.3.5f (package 3.9a, stage 7.7b.8.2/7.7b.8)

Package 3.9a Stage 7.7b.8.2: Charts and visualization.

Features:
- Line charts for time series
- Bar charts for comparisons
- Pie charts for distributions
- Real-time updates
- Interactive features (zoom, pan, tooltips)
- Export to image
"""
try:
    import pyqtgraph as pg
    from pyqtgraph import PlotWidget
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    PlotWidget = None

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from typing import List, Dict, Any, Optional, Tuple
import time
import math


class ChartType:
    """Chart types"""
    LINE = 'line'
    BAR = 'bar'
    PIE = 'pie'


class ChartWidget(QWidget):
    """Base chart widget using PyQtGraph
    
    v0.3.5f (package 3.9a, stage 7.7b.8.2/7.7b.8)
    
    Features:
    - Multiple chart types (line, bar, pie)
    - Interactive controls
    - Real-time updates
    - Export functionality
    - Customizable appearance
    """
    
    def __init__(self, chart_type: str = ChartType.LINE, parent=None):
        super().__init__(parent)
        self._chart_type = chart_type
        self._data_x = []
        self._data_y = []
        self._labels = []
        self._colors = [
            '#3498db',  # Blue
            '#2ecc71',  # Green
            '#f39c12',  # Orange
            '#e74c3c',  # Red
            '#9b59b6',  # Purple
            '#1abc9c',  # Turquoise
            '#34495e',  # Dark gray
        ]
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Check PyQtGraph availability
        if not PYQTGRAPH_AVAILABLE:
            error_label = QLabel(
                "PyQtGraph not available.\n"
                "Install with: pip install pyqtgraph"
            )
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            return
        
        # Configure PyQtGraph
        pg.setConfigOptions(antialias=True)
        
        # Create plot widget based on type
        if self._chart_type == ChartType.PIE:
            # Pie chart uses custom drawing
            self.plot_widget = QWidget()
            self.plot_widget.paintEvent = self._paint_pie_chart
        else:
            self.plot_widget = PlotWidget()
            self.plot_widget.setBackground('w')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
            
            # Enable mouse interaction
            self.plot_widget.setMouseEnabled(x=True, y=True)
        
        layout.addWidget(self.plot_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export Image")
        self.export_btn.clicked.connect(self._export_image)
        controls_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
    
    def set_data(
        self,
        x_data: List[float],
        y_data: List[float],
        labels: Optional[List[str]] = None
    ):
        """Set chart data
        
        Args:
            x_data: X-axis data
            y_data: Y-axis data
            labels: Data labels (optional)
        """
        self._data_x = x_data
        self._data_y = y_data
        self._labels = labels or []
        
        self._update_chart()
    
    def update_data(self, x_data: List[float], y_data: List[float]):
        """Update chart with new data
        
        Args:
            x_data: New X-axis data
            y_data: New Y-axis data
        """
        self.set_data(x_data, y_data, self._labels)
    
    def add_data_point(self, x: float, y: float):
        """Add single data point
        
        Args:
            x: X value
            y: Y value
        """
        self._data_x.append(x)
        self._data_y.append(y)
        self._update_chart()
    
    def clear(self):
        """Clear all data"""
        self._data_x = []
        self._data_y = []
        self._labels = []
        self._update_chart()
    
    def _update_chart(self):
        """Update chart display"""
        if not PYQTGRAPH_AVAILABLE:
            return
        
        if self._chart_type == ChartType.LINE:
            self._update_line_chart()
        elif self._chart_type == ChartType.BAR:
            self._update_bar_chart()
        elif self._chart_type == ChartType.PIE:
            self.plot_widget.update()
    
    def _update_line_chart(self):
        """Update line chart"""
        self.plot_widget.clear()
        
        if not self._data_x or not self._data_y:
            return
        
        # Plot line
        pen = pg.mkPen(color=self._colors[0], width=2)
        self.plot_widget.plot(
            self._data_x,
            self._data_y,
            pen=pen,
            symbol='o',
            symbolSize=5,
            symbolBrush=self._colors[0]
        )
        
        # Set labels
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.setLabel('left', 'Value')
    
    def _update_bar_chart(self):
        """Update bar chart"""
        self.plot_widget.clear()
        
        if not self._data_x or not self._data_y:
            return
        
        # Create bar chart
        width = 0.8
        bargraph = pg.BarGraphItem(
            x=self._data_x,
            height=self._data_y,
            width=width,
            brush=self._colors[0]
        )
        self.plot_widget.addItem(bargraph)
        
        # Set labels
        self.plot_widget.setLabel('bottom', 'Category')
        self.plot_widget.setLabel('left', 'Value')
    
    def _paint_pie_chart(self, event):
        """Paint pie chart"""
        if not self._data_y:
            return
        
        painter = QPainter(self.plot_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center and radius
        width = self.plot_widget.width()
        height = self.plot_widget.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 40
        
        # Calculate total
        total = sum(self._data_y)
        if total == 0:
            return
        
        # Draw slices
        start_angle = 0
        for i, value in enumerate(self._data_y):
            angle = int((value / total) * 360 * 16)  # Qt uses 1/16th degree
            
            # Set color
            color = QColor(self._colors[i % len(self._colors)])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            
            # Draw slice
            painter.drawPie(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
                start_angle,
                angle
            )
            
            # Draw label
            if self._labels and i < len(self._labels):
                # Calculate label position
                mid_angle = (start_angle + angle / 2) / 16 * math.pi / 180
                label_x = center_x + radius * 0.7 * math.cos(mid_angle)
                label_y = center_y - radius * 0.7 * math.sin(mid_angle)
                
                painter.setPen(QPen(Qt.GlobalColor.black))
                painter.drawText(
                    int(label_x - 20),
                    int(label_y - 10),
                    40,
                    20,
                    Qt.AlignmentFlag.AlignCenter,
                    self._labels[i]
                )
            
            start_angle += angle
    
    def _export_image(self):
        """Export chart as image"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chart",
            f"chart_{int(time.time())}.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if filename:
            if PYQTGRAPH_AVAILABLE and self._chart_type != ChartType.PIE:
                exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
                exporter.export(filename)
            else:
                # For pie charts, use widget screenshot
                pixmap = self.plot_widget.grab()
                pixmap.save(filename)
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Chart exported to {filename}"
            )


class LineChartWidget(ChartWidget):
    """Line chart widget"""
    
    def __init__(self, parent=None):
        super().__init__(ChartType.LINE, parent)


class BarChartWidget(ChartWidget):
    """Bar chart widget"""
    
    def __init__(self, parent=None):
        super().__init__(ChartType.BAR, parent)


class PieChartWidget(ChartWidget):
    """Pie chart widget"""
    
    def __init__(self, parent=None):
        super().__init__(ChartType.PIE, parent)


# Testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Chart Widget Test")
    window.resize(800, 600)
    
    tabs = QTabWidget()
    
    # Line chart
    line_chart = LineChartWidget()
    x_data = list(range(10))
    y_data = [i**2 for i in x_data]
    line_chart.set_data(x_data, y_data)
    tabs.addTab(line_chart, "Line Chart")
    
    # Bar chart
    bar_chart = BarChartWidget()
    bar_chart.set_data(
        list(range(5)),
        [10, 25, 15, 30, 20],
        ['A', 'B', 'C', 'D', 'E']
    )
    tabs.addTab(bar_chart, "Bar Chart")
    
    # Pie chart
    pie_chart = PieChartWidget()
    pie_chart.set_data(
        [],
        [30, 20, 25, 15, 10],
        ['Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5']
    )
    tabs.addTab(pie_chart, "Pie Chart")
    
    window.setCentralWidget(tabs)
    window.show()
    
    sys.exit(app.exec())
