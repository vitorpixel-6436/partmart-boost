#!/usr/bin/env python3
"""Tests for HistoricalDataViewer

Version: 0.3.5f (package 3.9a, stage 7.7b.8.2/7.7b.8)
"""
import unittest
import sys
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from PyQt6.QtWidgets import QApplication
    from ui.widgets.historical_data_viewer import (
        HistoricalDataViewer, PYQTGRAPH_AVAILABLE
    )
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

try:
    from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
    STORE_AVAILABLE = True
except ImportError:
    STORE_AVAILABLE = False


@unittest.skipIf(not PYQT_AVAILABLE, "PyQt6 not available")
class TestHistoricalDataViewer(unittest.TestCase):
    """Test HistoricalDataViewer"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test application"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])
    
    def setUp(self):
        """Set up test fixtures"""
        if STORE_AVAILABLE:
            # Create temporary database
            self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
            self.db_path = self.temp_file.name
            self.temp_file.close()
            
            self.store = HistoricalDataStore(
                self.db_path,
                DataRetentionPolicy.DAYS_7
            )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if STORE_AVAILABLE and os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_viewer_creation(self):
        """Test creating viewer"""
        viewer = HistoricalDataViewer()
        self.assertIsNotNone(viewer)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_ui_elements(self):
        """Test UI elements exist"""
        viewer = HistoricalDataViewer()
        
        self.assertIsNotNone(viewer.time_range_combo)
        self.assertIsNotNone(viewer.component_combo)
        self.assertIsNotNone(viewer.auto_refresh_checkbox)
        self.assertIsNotNone(viewer.refresh_btn)
        self.assertIsNotNone(viewer.chart_tabs)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_charts_exist(self):
        """Test all charts are created"""
        viewer = HistoricalDataViewer()
        
        self.assertIsNotNone(viewer.health_chart)
        self.assertIsNotNone(viewer.error_chart)
        self.assertIsNotNone(viewer.recovery_chart)
        self.assertIsNotNone(viewer.comparison_chart)
    
    @unittest.skipIf(not STORE_AVAILABLE or not PYQTGRAPH_AVAILABLE, "Store or PyQtGraph not available")
    def test_set_historical_store(self):
        """Test setting historical store"""
        viewer = HistoricalDataViewer()
        viewer.set_historical_store(self.store)
        
        self.assertEqual(viewer._historical_store, self.store)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_time_range_options(self):
        """Test time range options"""
        viewer = HistoricalDataViewer()
        
        # Check options exist
        self.assertGreater(viewer.time_range_combo.count(), 0)
        
        # Check default selection
        self.assertEqual(viewer.time_range_combo.currentText(), "Last 24 Hours")
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_time_range_calculation(self):
        """Test time range calculation"""
        viewer = HistoricalDataViewer()
        
        # Test "Last Hour"
        viewer.time_range_combo.setCurrentText("Last Hour")
        start, end = viewer._get_time_range()
        self.assertAlmostEqual(end - start, 3600, delta=10)
        
        # Test "Last 24 Hours"
        viewer.time_range_combo.setCurrentText("Last 24 Hours")
        start, end = viewer._get_time_range()
        self.assertAlmostEqual(end - start, 86400, delta=10)
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_auto_refresh_toggle(self):
        """Test auto-refresh toggle"""
        viewer = HistoricalDataViewer()
        
        # Enable
        viewer.auto_refresh_checkbox.setChecked(True)
        # Timer should be created
        
        # Disable
        viewer.auto_refresh_checkbox.setChecked(False)
        # Timer should stop
    
    @unittest.skipIf(not STORE_AVAILABLE or not PYQTGRAPH_AVAILABLE, "Store or PyQtGraph not available")
    def test_refresh_data_with_store(self):
        """Test refreshing data with store"""
        viewer = HistoricalDataViewer()
        
        # Add test data to store
        timestamp = time.time()
        self.store.store_health_snapshot(
            'Component1', 'healthy', 'OK',
            timestamp=timestamp
        )
        self.store.store_error(
            'error', 'Component1', 'Test error',
            timestamp=timestamp
        )
        self.store.store_recovery(
            'Component1', 'restart', 'success', 1.0,
            timestamp=timestamp
        )
        
        # Set store and refresh
        viewer.set_historical_store(self.store)
        viewer.refresh_data()
        
        # Should not crash
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_refresh_without_store(self):
        """Test refreshing without store (should not crash)"""
        viewer = HistoricalDataViewer()
        viewer.refresh_data()
        # Should not crash
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_custom_time_range_disabled_by_default(self):
        """Test custom time range disabled by default"""
        viewer = HistoricalDataViewer()
        
        self.assertFalse(viewer.start_time_edit.isEnabled())
        self.assertFalse(viewer.end_time_edit.isEnabled())
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_custom_time_range_enable(self):
        """Test enabling custom time range"""
        viewer = HistoricalDataViewer()
        
        viewer.time_range_combo.setCurrentText("Custom")
        
        self.assertTrue(viewer.start_time_edit.isEnabled())
        self.assertTrue(viewer.end_time_edit.isEnabled())
    
    @unittest.skipIf(not PYQTGRAPH_AVAILABLE, "PyQtGraph not available")
    def test_component_combo_default(self):
        """Test component combo default value"""
        viewer = HistoricalDataViewer()
        
        self.assertGreater(viewer.component_combo.count(), 0)
        self.assertEqual(viewer.component_combo.itemText(0), "All Components")
    
    @unittest.skipIf(not STORE_AVAILABLE or not PYQTGRAPH_AVAILABLE, "Store or PyQtGraph not available")
    def test_component_filtering(self):
        """Test component filtering"""
        viewer = HistoricalDataViewer()
        
        # Add test data with different components
        timestamp = time.time()
        self.store.store_health_snapshot('Component1', 'healthy', 'OK', timestamp=timestamp)
        self.store.store_health_snapshot('Component2', 'degraded', 'Warning', timestamp=timestamp)
        
        viewer.set_historical_store(self.store)
        
        # Select specific component
        viewer.component_combo.setCurrentText("Component1")
        viewer.refresh_data()
        
        # Should filter data (no crash)


if __name__ == '__main__':
    unittest.main(verbosity=2)
