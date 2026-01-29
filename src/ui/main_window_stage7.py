#!/usr/bin/env python3
"""Main Window - Stage 7 Integration

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Package 3.9a Stage 7.3: Integrated with BackendBridge and widgets.

Features:
- Uses AppIntegrator for component access
- Distributes bridge/signals to widgets
- Real-time performance monitoring
- Clean separation of concerns
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.app_integrator import AppIntegrator
    from core.command_system import StartMonitoringCommand
    INTEGRATOR_AVAILABLE = True
except ImportError as e:
    print(f"[MainWindow] Integrator not available: {e}")
    INTEGRATOR_AVAILABLE = False

try:
    from ui.performance_widget import PerformanceWidget
    PERFORMANCE_WIDGET_AVAILABLE = True
except ImportError:
    PERFORMANCE_WIDGET_AVAILABLE = False

try:
    from ui.widgets.dashboard_widget import DashboardWidget
    from ui.widgets.settings_widget import SettingsWidget
    WIDGETS_AVAILABLE = True
except ImportError:
    WIDGETS_AVAILABLE = False


class MainWindowStage7(QMainWindow):
    """Main window with Stage 7 integration
    
    v0.3.5e (package 3.9a, stage 7.3/7.7)
    
    Features:
    - Receives integrator in constructor
    - Distributes bridge/signals to widgets
    - Real-time updates
    - Clean architecture
    
    Usage:
        >>> from core.system_init import SystemInitializer
        >>> 
        >>> init = SystemInitializer()
        >>> result = init.initialize()
        >>> 
        >>> if result.success:
        >>>     integrator = init.get_integrator()
        >>>     window = MainWindowStage7(integrator)
        >>>     window.show()
    """
    
    def __init__(self, integrator=None, parent=None):
        """Initialize main window
        
        Args:
            integrator: AppIntegrator instance (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Get integrator
        if integrator is None and INTEGRATOR_AVAILABLE:
            integrator = AppIntegrator.get_instance()
        
        self._integrator = integrator
        self._bridge = None
        self._qt_signals = None
        self._service_manager = None
        
        # Extract components from integrator
        if self._integrator:
            self._bridge = self._integrator.get_bridge()
            self._qt_signals = self._integrator.get_qt_signals()
            self._service_manager = self._integrator.get_service_manager()
            
            print("[MainWindow] ✅ Components extracted from integrator")
            print(f"[MainWindow]   Bridge: {type(self._bridge).__name__ if self._bridge else 'None'}")
            print(f"[MainWindow]   Qt signals: {type(self._qt_signals).__name__ if self._qt_signals else 'None'}")
            print(f"[MainWindow]   Service manager: {type(self._service_manager).__name__ if self._service_manager else 'None'}")
        else:
            print("[MainWindow] ⚠️ No integrator provided")
        
        # UI setup
        self._init_ui()
        
        # Auto-start monitoring
        self._auto_start_monitoring()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("PartMart Boost v0.3.5e (Stage 7)")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D0D0D;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: #0D0D0D;
            }
            QTabBar::tab {
                background: #1A1A1A;
                color: #aaa;
                padding: 10px 20px;
                border: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #E63946;
                color: white;
            }
            QTabBar::tab:hover {
                background: #252525;
                color: white;
            }
        """)
        
        # Create tabs
        self._create_tabs()
        
        layout.addWidget(self._tabs)
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self) -> QWidget:
        """Create header"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A1A1A, stop:1 #0D0D0D);
                border-bottom: 2px solid #E63946;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 15, 30, 15)
        
        # Logo
        logo = QLabel("🐉 PartMart Boost")
        logo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        logo.setStyleSheet("color: #E63946;")
        layout.addWidget(logo)
        
        # Version
        version = QLabel("v0.3.5e (Stage 7.3)")
        version.setFont(QFont("Segoe UI", 10))
        version.setStyleSheet("color: #666;")
        layout.addWidget(version)
        
        layout.addStretch()
        
        # Status indicator
        self._status_indicator = QLabel("⏳ Initializing...")
        self._status_indicator.setFont(QFont("Segoe UI", 10))
        self._status_indicator.setStyleSheet("color: #FFC107;")
        layout.addWidget(self._status_indicator)
        
        return header
    
    def _create_tabs(self):
        """Create tab pages"""
        # Dashboard tab
        if WIDGETS_AVAILABLE and self._bridge and self._qt_signals:
            dashboard = DashboardWidget(self._bridge, self._qt_signals)
            self._tabs.addTab(dashboard, "🏠 Dashboard")
        else:
            dashboard = self._create_placeholder("Dashboard", "Integrator not available")
            self._tabs.addTab(dashboard, "🏠 Dashboard")
        
        # Performance tab
        if PERFORMANCE_WIDGET_AVAILABLE and self._qt_signals:
            # Container for performance widget
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(20, 20, 20, 20)
            
            perf_widget = PerformanceWidget(self._qt_signals)
            container_layout.addWidget(perf_widget, alignment=Qt.AlignmentFlag.AlignCenter)
            container_layout.addStretch()
            
            self._tabs.addTab(container, "📊 Performance")
        else:
            perf = self._create_placeholder("Performance", "Performance widget not available")
            self._tabs.addTab(perf, "📊 Performance")
        
        # Settings tab
        if WIDGETS_AVAILABLE and self._bridge and self._qt_signals:
            settings = SettingsWidget(self._bridge, self._qt_signals)
            self._tabs.addTab(settings, "⚙️ Settings")
        else:
            settings = self._create_placeholder("Settings", "Settings widget not available")
            self._tabs.addTab(settings, "⚙️ Settings")
    
    def _create_placeholder(self, title: str, message: str) -> QWidget:
        """Create placeholder widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #E63946;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        msg_label = QLabel(message)
        msg_label.setFont(QFont("Segoe UI", 14))
        msg_label.setStyleSheet("color: #666;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_label)
        
        return widget
    
    def _create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #1A1A1A;
                color: #aaa;
                border-top: 1px solid #252525;
            }
        """)
        
        self._status_label = QLabel("Ready")
        status_bar.addWidget(self._status_label)
        
        status_bar.addPermanentWidget(QLabel("  |  "))
        
        # Connection status
        self._connection_label = QLabel()
        self._update_connection_status()
        status_bar.addPermanentWidget(self._connection_label)
        
        self.setStatusBar(status_bar)
    
    def _update_connection_status(self):
        """Update connection status"""
        if not self._connection_label:
            return
        
        if self._integrator and self._integrator.is_ready():
            self._connection_label.setText("✅ Connected")
            self._connection_label.setStyleSheet("color: #4CAF50;")
            self._status_indicator.setText("✅ Active")
            self._status_indicator.setStyleSheet("color: #4CAF50;")
        else:
            self._connection_label.setText("❌ Disconnected")
            self._connection_label.setStyleSheet("color: #F44336;")
            self._status_indicator.setText("❌ Inactive")
            self._status_indicator.setStyleSheet("color: #F44336;")
    
    def _auto_start_monitoring(self):
        """Auto-start monitoring"""
        if not self._bridge:
            print("[MainWindow] ⚠️ Bridge not available, cannot start monitoring")
            return
        
        try:
            # Start monitoring with 100ms interval
            command = StartMonitoringCommand(interval=100)
            result = self._bridge.execute_command(command)
            
            if result.success:
                print("[MainWindow] ✅ Monitoring started automatically")
                self._status_label.setText("Monitoring active (100ms)")
            else:
                error = result.error or "Unknown error"
                print(f"[MainWindow] ⚠️ Monitoring start failed: {error}")
                self._status_label.setText(f"Monitoring failed: {error}")
        
        except Exception as e:
            print(f"[MainWindow] ❌ Auto-start failed: {e}")
            self._status_label.setText(f"Error: {e}")


# Testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    print("="*60)
    print("MainWindow Stage 7 Test")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    # Initialize system
    if INTEGRATOR_AVAILABLE:
        try:
            from core.system_init import SystemInitializer
            
            init = SystemInitializer()
            result = init.initialize()
            
            if result.success:
                integrator = init.get_integrator()
                window = MainWindowStage7(integrator)
            else:
                print(f"Initialization failed: {result.error}")
                window = MainWindowStage7()
        
        except Exception as e:
            print(f"Initialization error: {e}")
            window = MainWindowStage7()
    else:
        window = MainWindowStage7()
    
    window.show()
    
    print("\n✅ Window launched!")
    print("Close window to exit.\n")
    
    sys.exit(app.exec())
