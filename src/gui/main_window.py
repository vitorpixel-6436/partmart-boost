#!/usr/bin/env python3
"""PartMart Boost - Main Window

Version: 0.3.5d+patch4

Main application window with tabs and real-time monitoring.
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QIcon

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import tab widgets
from gui.dashboard_widget import DashboardWidget
from gui.performance_widget import PerformanceWidget
from gui.settings_widget import SettingsWidget
from gui.logs_widget import LogsWidget


class MainWindow(QMainWindow):
    """Main Application Window
    
    Features:
    - Tabbed interface
    - Real-time monitoring
    - System tray integration
    - Menu bar
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PartMart Boost v0.3.5d+patch4")
        self.setMinimumSize(1200, 800)
        
        # Apply dark theme
        self._apply_dark_theme()
        
        # Create UI
        self._create_menu_bar()
        self._create_tabs()
        self._create_status_bar()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # Update every 100ms
        
        print("[MainWindow] Initialized successfully")
    
    def _apply_dark_theme(self):
        """Apply dark theme stylesheet"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial;
            font-size: 10pt;
        }
        QTabWidget::pane {
            border: 1px solid #3a3a3a;
            background-color: #252525;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #e0e0e0;
            padding: 8px 20px;
            margin-right: 2px;
            border: 1px solid #3a3a3a;
        }
        QTabBar::tab:selected {
            background-color: #0d7377;
            color: white;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background-color: #3a3a3a;
        }
        QPushButton {
            background-color: #0d7377;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #14a2aa;
        }
        QPushButton:pressed {
            background-color: #0a5c5f;
        }
        QGroupBox {
            border: 2px solid #3a3a3a;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 10px;
            font-weight: bold;
            color: #0d7377;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QLabel {
            color: #e0e0e0;
        }
        QComboBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3a3a3a;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox:hover {
            border: 1px solid #0d7377;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            color: #e0e0e0;
            selection-background-color: #0d7377;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #3a3a3a;
            border-radius: 3px;
            background-color: #2d2d2d;
        }
        QCheckBox::indicator:checked {
            background-color: #0d7377;
            border-color: #0d7377;
        }
        QTextEdit {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 5px;
        }
        QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QMenuBar::item:selected {
            background-color: #0d7377;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3a3a3a;
        }
        QMenu::item:selected {
            background-color: #0d7377;
        }
        QStatusBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._force_refresh)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_tabs(self):
        """Create tab widget with all tabs"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.dashboard_widget = DashboardWidget()
        self.performance_widget = PerformanceWidget()
        self.settings_widget = SettingsWidget()
        self.logs_widget = LogsWidget()
        
        # Add tabs
        self.tabs.addTab(self.dashboard_widget, "Dashboard")
        self.tabs.addTab(self.performance_widget, "Performance")
        self.tabs.addTab(self.settings_widget, "Settings")
        self.tabs.addTab(self.logs_widget, "Logs")
    
    def _create_status_bar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")
    
    def _update_ui(self):
        """Update UI (called by timer)"""
        try:
            # Update dashboard
            self.dashboard_widget.update_data()
            
            # Update performance
            self.performance_widget.update_data()
            
            # Update status bar
            fps = self.dashboard_widget.get_current_fps()
            self.statusBar().showMessage(f"FPS: {fps:.1f} | Status: Running")
        except Exception as e:
            print(f"[MainWindow] Update error: {e}")
    
    def _force_refresh(self):
        """Force refresh all data"""
        self.dashboard_widget.clear_history()
        self.logs_widget.add_log("Refreshed all data")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>PartMart Boost v0.3.5d+patch4</h2>
        <p>Performance optimization tool with real-time monitoring.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
        <li>Real-time FPS tracking</li>
        <li>Performance monitoring</li>
        <li>Frame generation</li>
        <li>Upscaling (FSR 4)</li>
        <li>Thermal management</li>
        <li>Power management</li>
        </ul>
        <br>
        <p><b>Python:</b> 3.8+ (including 3.14/3.15)</p>
        <p><b>License:</b> MIT</p>
        """
        
        QMessageBox.about(self, "About PartMart Boost", about_text)
    
    def closeEvent(self, event):
        """Handle window close"""
        try:
            # Stop timer
            self.update_timer.stop()
            
            # Stop monitors
            if hasattr(self.dashboard_widget, 'performance_monitor'):
                self.dashboard_widget.performance_monitor.stop()
            
            print("[MainWindow] Closed successfully")
        except Exception as e:
            print(f"[MainWindow] Close error: {e}")
        
        # Accept close
        event.accept()
