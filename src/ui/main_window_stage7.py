#!/usr/bin/env python3
"""Main Window with Error Handling

Version: 0.3.5m (package 3.9a, stage 7.7b.4/7.7)

Package 3.9a Stage 7.7b.4: Error handling in UI components.

Features:
- Uses AppIntegrator for component access
- Distributes bridge/signals to widgets
- Real-time performance monitoring
- Comprehensive error handling
- Graceful degradation
- User-friendly error messages
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QCloseEvent
import sys
import os
import traceback

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
    from core.logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

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
    """Main window with error handling
    
    v0.3.5m (package 3.9a, stage 7.7b.4/7.7)
    
    Features:
    - Comprehensive error handling
    - Graceful degradation
    - Logging integration
    - User-friendly error messages
    - Automatic recovery
    
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
        
        # Get logger if available
        self._logger = None
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug("MainWindow initializing")
            except Exception as e:
                print(f"[MainWindow] Logger initialization failed: {e}")
        
        # Initialize state
        self._integrator = None
        self._bridge = None
        self._qt_signals = None
        self._service_manager = None
        self._status_indicator = None
        self._connection_label = None
        self._status_label = None
        self._tabs = None
        
        try:
            # Get integrator
            if integrator is None and INTEGRATOR_AVAILABLE:
                try:
                    integrator = AppIntegrator.get_instance()
                    self._log_debug("Retrieved AppIntegrator instance")
                except Exception as e:
                    self._log_warning(f"Failed to get integrator: {e}")
            
            self._integrator = integrator
            
            # Extract components from integrator
            if self._integrator:
                self._extract_components()
            else:
                self._log_warning("No integrator provided, running in degraded mode")
            
            # UI setup
            self._init_ui()
            
            # Auto-start monitoring
            QTimer.singleShot(100, self._auto_start_monitoring)
            
            self._log_info("Initialized successfully")
        
        except Exception as e:
            self._log_error(f"Initialization failed: {e}", exc_info=True)
            # Show basic UI even on error
            try:
                self._init_minimal_ui()
            except Exception as e2:
                self._log_error(f"Even minimal UI failed: {e2}", exc_info=True)
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="MainWindow")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="MainWindow")
        else:
            print(f"[MainWindow] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="MainWindow")
        else:
            print(f"[MainWindow] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="MainWindow", exc_info=exc_info)
        else:
            print(f"[MainWindow] ERROR: {message}")
            if exc_info:
                traceback.print_exc()
    
    def _extract_components(self):
        """Extract components from integrator with error handling"""
        try:
            self._bridge = self._integrator.get_bridge()
            self._log_debug(f"Bridge: {type(self._bridge).__name__ if self._bridge else 'None'}")
        except Exception as e:
            self._log_error(f"Failed to get bridge: {e}")
        
        try:
            self._qt_signals = self._integrator.get_qt_signals()
            self._log_debug(f"Qt signals: {type(self._qt_signals).__name__ if self._qt_signals else 'None'}")
        except Exception as e:
            self._log_error(f"Failed to get Qt signals: {e}")
        
        try:
            self._service_manager = self._integrator.get_service_manager()
            self._log_debug(f"Service manager: {type(self._service_manager).__name__ if self._service_manager else 'None'}")
        except Exception as e:
            self._log_error(f"Failed to get service manager: {e}")
    
    def _init_ui(self):
        """Initialize UI with error handling"""
        try:
            self.setWindowTitle("PartMart Boost v0.3.5m (Stage 7.7b.4)")
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
            try:
                header = self._create_header()
                layout.addWidget(header)
            except Exception as e:
                self._log_error(f"Failed to create header: {e}", exc_info=True)
            
            # Tab widget
            try:
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
            
            except Exception as e:
                self._log_error(f"Failed to create tabs: {e}", exc_info=True)
                # Add error placeholder
                error_label = QLabel("Failed to load tabs. Check logs for details.")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet("color: #F44336; font-size: 14pt;")
                layout.addWidget(error_label)
            
            # Status bar
            try:
                self._create_status_bar()
            except Exception as e:
                self._log_error(f"Failed to create status bar: {e}", exc_info=True)
        
        except Exception as e:
            self._log_error(f"UI initialization failed: {e}", exc_info=True)
            raise
    
    def _init_minimal_ui(self):
        """Initialize minimal UI on error"""
        self.setWindowTitle("PartMart Boost - Error")
        self.setGeometry(100, 100, 600, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        error_label = QLabel("⚠️ Application Error")
        error_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        error_label.setStyleSheet("color: #F44336;")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(error_label)
        
        msg_label = QLabel("Failed to initialize application.\nCheck logs for details.")
        msg_label.setFont(QFont("Segoe UI", 12))
        msg_label.setStyleSheet("color: #666;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_label)
    
    def _create_header(self) -> QWidget:
        """Create header with error handling"""
        try:
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
            version = QLabel("v0.3.5m (Stage 7.7b.4)")
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
        
        except Exception as e:
            self._log_error(f"Header creation failed: {e}", exc_info=True)
            # Return minimal header
            header = QWidget()
            header.setFixedHeight(80)
            return header
    
    def _create_tabs(self):
        """Create tab pages with error handling"""
        # Dashboard tab
        try:
            if WIDGETS_AVAILABLE and self._bridge and self._qt_signals:
                dashboard = DashboardWidget(self._bridge, self._qt_signals)
                self._tabs.addTab(dashboard, "🏠 Dashboard")
                self._log_debug("Dashboard tab created")
            else:
                dashboard = self._create_placeholder("Dashboard", "Backend integration not available")
                self._tabs.addTab(dashboard, "🏠 Dashboard")
                self._log_warning("Dashboard created as placeholder")
        
        except Exception as e:
            self._log_error(f"Failed to create dashboard: {e}", exc_info=True)
            error_widget = self._create_error_placeholder("Dashboard", str(e))
            self._tabs.addTab(error_widget, "🏠 Dashboard")
        
        # Performance tab
        try:
            if PERFORMANCE_WIDGET_AVAILABLE and self._qt_signals:
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(20, 20, 20, 20)
                
                perf_widget = PerformanceWidget(self._qt_signals)
                container_layout.addWidget(perf_widget, alignment=Qt.AlignmentFlag.AlignCenter)
                container_layout.addStretch()
                
                self._tabs.addTab(container, "📊 Performance")
                self._log_debug("Performance tab created")
            else:
                perf = self._create_placeholder("Performance", "Performance monitoring not available")
                self._tabs.addTab(perf, "📊 Performance")
                self._log_warning("Performance created as placeholder")
        
        except Exception as e:
            self._log_error(f"Failed to create performance tab: {e}", exc_info=True)
            error_widget = self._create_error_placeholder("Performance", str(e))
            self._tabs.addTab(error_widget, "📊 Performance")
        
        # Settings tab
        try:
            if WIDGETS_AVAILABLE and self._bridge and self._qt_signals:
                settings = SettingsWidget(self._bridge, self._qt_signals)
                self._tabs.addTab(settings, "⚙️ Settings")
                self._log_debug("Settings tab created")
            else:
                settings = self._create_placeholder("Settings", "Settings not available")
                self._tabs.addTab(settings, "⚙️ Settings")
                self._log_warning("Settings created as placeholder")
        
        except Exception as e:
            self._log_error(f"Failed to create settings: {e}", exc_info=True)
            error_widget = self._create_error_placeholder("Settings", str(e))
            self._tabs.addTab(error_widget, "⚙️ Settings")
    
    def _create_placeholder(self, title: str, message: str) -> QWidget:
        """Create placeholder widget"""
        try:
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
        
        except Exception as e:
            self._log_error(f"Placeholder creation failed: {e}")
            return QWidget()  # Empty widget fallback
    
    def _create_error_placeholder(self, title: str, error: str) -> QWidget:
        """Create error placeholder widget"""
        try:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title_label = QLabel(f"⚠️ {title} Error")
            title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #F44336;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            error_label = QLabel(f"Failed to load {title.lower()}.")
            error_label.setFont(QFont("Segoe UI", 12))
            error_label.setStyleSheet("color: #888;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            
            detail_label = QLabel(f"Error: {error[:100]}")
            detail_label.setFont(QFont("Segoe UI", 10))
            detail_label.setStyleSheet("color: #555;")
            detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_label.setWordWrap(True)
            layout.addWidget(detail_label)
            
            return widget
        
        except Exception:
            return QWidget()  # Empty widget fallback
    
    def _create_status_bar(self):
        """Create status bar with error handling"""
        try:
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
        
        except Exception as e:
            self._log_error(f"Status bar creation failed: {e}", exc_info=True)
    
    def _update_connection_status(self):
        """Update connection status with error handling"""
        try:
            if not self._connection_label:
                return
            
            if self._integrator and self._integrator.is_ready():
                self._connection_label.setText("✅ Connected")
                self._connection_label.setStyleSheet("color: #4CAF50;")
                
                if self._status_indicator:
                    self._status_indicator.setText("✅ Active")
                    self._status_indicator.setStyleSheet("color: #4CAF50;")
            else:
                self._connection_label.setText("❌ Disconnected")
                self._connection_label.setStyleSheet("color: #F44336;")
                
                if self._status_indicator:
                    self._status_indicator.setText("❌ Inactive")
                    self._status_indicator.setStyleSheet("color: #F44336;")
        
        except Exception as e:
            self._log_error(f"Connection status update failed: {e}")
    
    def _auto_start_monitoring(self):
        """Auto-start monitoring with error handling"""
        try:
            if not self._bridge:
                self._log_warning("Bridge not available, cannot start monitoring")
                if self._status_label:
                    self._status_label.setText("Monitoring unavailable")
                return
            
            # Start monitoring with 100ms interval
            command = StartMonitoringCommand(interval=100)
            result = self._bridge.execute_command(command)
            
            if result.success:
                self._log_info("Monitoring started automatically")
                if self._status_label:
                    self._status_label.setText("Monitoring active (100ms)")
            else:
                error = result.error or "Unknown error"
                self._log_warning(f"Monitoring start failed: {error}")
                if self._status_label:
                    self._status_label.setText(f"Monitoring failed: {error}")
        
        except AttributeError as e:
            self._log_error(f"Command interface error: {e}")
            if self._status_label:
                self._status_label.setText("Command system error")
        
        except Exception as e:
            self._log_error(f"Auto-start failed: {e}", exc_info=True)
            if self._status_label:
                self._status_label.setText(f"Error: {str(e)[:50]}")
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close with cleanup
        
        Args:
            event: Close event
        """
        try:
            self._log_info("Window closing, cleaning up...")
            
            # Stop monitoring
            if self._integrator:
                try:
                    # Could add cleanup logic here
                    self._log_debug("Integrator cleanup")
                except Exception as e:
                    self._log_error(f"Cleanup error: {e}")
            
            self._log_info("Window closed successfully")
            event.accept()
        
        except Exception as e:
            self._log_error(f"Close event error: {e}", exc_info=True)
            event.accept()  # Close anyway
    
    def show_error_dialog(self, title: str, message: str, details: str = None):
        """Show error dialog to user
        
        Args:
            title: Dialog title
            message: Error message
            details: Detailed error info (optional)
        """
        try:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if details:
                msg_box.setDetailedText(details)
            
            msg_box.exec()
        
        except Exception as e:
            self._log_error(f"Error dialog failed: {e}")


# Testing
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    print("="*60)
    print("MainWindow Test (with Error Handling)")
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
            traceback.print_exc()
            window = MainWindowStage7()
    else:
        window = MainWindowStage7()
    
    window.show()
    
    print("\n✅ Window launched!")
    print("Close window to exit.\n")
    
    sys.exit(app.exec())
