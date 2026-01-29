#!/usr/bin/env python3
"""Tests for ChartWidget

Version: 0.3.5f (package 3.9a, stage 7.7b.8.2/7.7b.8)
"""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from PyQt6.QtWidgets import QApplication
    from ui.widgets.chart_widget import (
        ChartWidget, LineChartWidget, BarChartWidget, PieChartWidget,
        ChartType, PYQTGRAPH_AVAILABLE
    )
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestChartWidget(unittest.TestCase):
    """Test ChartWidget"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test application"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def test_line_chart_creation(self):
        """Test creating line chart"""
        chart = LineChartWidget()
        self.assertIsNotNone(chart)
        self.assertEqual(chart._chart_type, ChartType.LINE)
    
    def test_bar_chart_creation(self):
        """Test creating bar chart"""
        chart = BarChartWidget()
        self.assertIsNotNone(chart)
        self.assertEqual(chart._chart_type, ChartType.BAR)
    
    def test_pie_chart_creation(self):
        """Test creating pie chart"""
        chart = PieChartWidget()
        self.assertIsNotNone(chart)
        self.assertEqual(chart._chart_type, ChartType.PIE)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_set_data(self):
        """Test setting chart data"""
        chart = LineChartWidget()
        
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]
        labels = ['A', 'B', 'C', 'D', 'E']
        
        chart.set_data(x_data, y_data, labels)
        
        self.assertEqual(chart._data_x, x_data)
        self.assertEqual(chart._data_y, y_data)
        self.assertEqual(chart._labels, labels)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_add_data_point(self):
        """Test adding single data point"""
        chart = LineChartWidget()
        
        chart.add_data_point(1, 10)
        self.assertEqual(len(chart._data_x), 1)
        self.assertEqual(len(chart._data_y), 1)
        
        chart.add_data_point(2, 20)
        self.assertEqual(len(chart._data_x), 2)
        self.assertEqual(len(chart._data_y), 2)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_update_data(self):
        """Test updating chart data"""
        chart = LineChartWidget()
        
        # Set initial data
        chart.set_data([1, 2, 3], [10, 20, 30])
        
        # Update data
        new_x = [1, 2, 3, 4]
        new_y = [15, 25, 35, 45]
        chart.update_data(new_x, new_y)
        
        self.assertEqual(chart._data_x, new_x)
        self.assertEqual(chart._data_y, new_y)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_clear(self):
        """Test clearing chart data"""
        chart = LineChartWidget()
        
        # Add data
        chart.set_data([1, 2, 3], [10, 20, 30], ['A', 'B', 'C'])
        
        # Clear
        chart.clear()
        
        self.assertEqual(len(chart._data_x), 0)
        self.assertEqual(len(chart._data_y), 0)
        self.assertEqual(len(chart._labels), 0)
    
    def test_colors_defined(self):
        """Test chart colors are defined"""
        chart = ChartWidget()
        self.assertIsInstance(chart._colors, list)
        self.assertGreater(len(chart._colors), 0)
    
    def test_chart_types(self):
        """Test chart type constants"""
        self.assertEqual(ChartType.LINE, 'line')
        self.assertEqual(ChartType.BAR, 'bar')
        self.assertEqual(ChartType.PIE, 'pie')
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_empty_data_handling(self):
        """Test handling empty data"""
        chart = LineChartWidget()
        
        # Should not crash with empty data
        chart.set_data([], [])
        chart.clear()
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_bar_chart_data(self):
        """Test bar chart with data"""
        chart = BarChartWidget()
        
        x_data = list(range(5))
        y_data = [10, 20, 15, 25, 30]
        labels = ['A', 'B', 'C', 'D', 'E']
        
        chart.set_data(x_data, y_data, labels)
        
        self.assertEqual(len(chart._data_x), 5)
        self.assertEqual(len(chart._data_y), 5)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_pie_chart_data(self):
        """Test pie chart with data"""
        chart = PieChartWidget()
        
        values = [30, 20, 25, 15, 10]
        labels = ['Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5']
        
        chart.set_data([], values, labels)
        
        self.assertEqual(len(chart._data_y), 5)
        self.assertEqual(len(chart._labels), 5)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_large_dataset(self):
        """Test with large dataset"""
        chart = LineChartWidget()
        
        x_data = list(range(1000))
        y_data = [i**2 for i in x_data]
        
        chart.set_data(x_data, y_data)
        
        self.assertEqual(len(chart._data_x), 1000)
        self.assertEqual(len(chart._data_y), 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
