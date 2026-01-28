"""PartMart Boost main window with full localization and ML integration"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QApplication, QProgressBar, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys
import os
import subprocess
import psutil

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Core imports
from localization import t, set_language, init_localization
from core.config import get_config, init_config
from core.logger import get_logger, init_logger

# UI imports
try:
    from ui.settings_dialog import SettingsDialog
except ImportError:
    SettingsDialog = None

# System imports
from ui.ai_widget import PartMartAIWidget
from ai_optimizer import PartMartAIOptimizer
from system_monitor import SystemMonitor

# ML imports (optional)
try:
    from optimizers.ml_optimizer import get_ml_optimizer, init_ml_optimizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class MetricCard(QFrame):
    """Standalone metric card with guaranteed text visibility"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)
        self.setAutoFillBackground(True)
        
        # Style
        self.setStyleSheet("""
            MetricCard {
                background-color: #1A1A1A;
                border-left: 4px solid #E63946;
                border-radius: 16px;
            }
            MetricCard:hover {
                background-color: #252525;
            }
        """)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title - GUARANTEED VISIBLE
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        layout.addWidget(self.title_label)
        
        # Value - LARGE AND VISIBLE
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: 700;
                color: #E63946;
                background: transparent;
            }
        """)
        layout.addWidget(self.value_label)
        
        # Subtitle - VISIBLE
        self.subtitle_label = QLabel(t('loading'))
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background: transparent;
            }
        """)
        layout.addWidget(self.subtitle_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #0D0D0D;
                border-radius: 8px;
                text-align: center;
                color: white;
                height: 24px;
                font-weight: 600;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E63946, stop:1 #FF4757);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
    
    def set_title(self, title: str):
        self.title_label.setText(title)
        self.title_label.repaint()
    
    def set_value(self, value: str):
        self.value_label.setText(value)
        self.value_label.repaint()
    
    def set_subtitle(self, text: str):
        self.subtitle_label.setText(text)
        self.subtitle_label.repaint()
    
    def set_progress(self, value: int, text: str = ""):
        self.progress.setValue(value)
        if text:
            self.progress.setFormat(text)
        self.progress.repaint()

class PartMartMainWindow(QMainWindow):
    """Modern card-based UI with full localization and ML integration"""

    def __init__(self, version: str = "0.3.4-alpha"):
        super().__init__()
        self.version = version
        
        # Initialize core systems
        self.config = init_config()
        self.logger = init_logger(log_level=self.config.get("log_level", "INFO"))
        
        # Initialize localization
        lang = self.config.get_language()
        init_localization(lang)
        
        # Log startup
        self.logger.log_startup(version)
        
        # Initialize ML optimizer (if enabled)
        if ML_AVAILABLE:
            self.ml_optimizer = init_ml_optimizer(self.config.is_ml_enabled())
        else:
            self.ml_optimizer = None
        
        # Window setup
        self.setWindowTitle(t('window_title', version=version))
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Initialize monitoring
        self.system_monitor = SystemMonitor()
        self.ai_engine = PartMartAIOptimizer()
        self.nav_buttons = []
        
        # Metric cards
        self.gpu_card = None
        self.ram_card = None
        self.cpu_card = None
        
        # Last state for ML
        self.last_state = None
        
        self._setup_ui()
        
        # Auto-update timer
        interval = self.config.get_update_interval()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_data)
        self.update_timer.start(interval)
        self._update_system_data()
        
        self.logger.info("Application initialized successfully")

    def _setup_ui(self):
        # Main stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D0D0D;
            }
            * {
                font-family: "Segoe UI", "Arial", sans-serif;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: #0D0D0D;")
        
        self.page_home = self._create_home_page()
        self.page_gpu = self._create_gpu_page()
        self.page_ram = self._create_placeholder(t('coming_soon'))
        
        for page in [self.page_home, self.page_gpu, self.page_ram]:
            self.content_stack.addWidget(page)
        
        main_layout.addWidget(self.content_stack, 1)
        central.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A1A1A, stop:1 #0D0D0D);
                border-bottom: 2px solid #E63946;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(32, 16, 32, 16)
        
        # Logo
        logo = QLabel("🐉 PartMart Boost")
        logo.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #E63946;
            letter-spacing: 2px;
            background: transparent;
        """)
        layout.addWidget(logo)
        
        layout.addStretch()
        
        # Navigation tabs
        tabs = [
            ("🏠 " + t('nav_home'), 0),
            ("🎮 " + t('nav_gpu'), 1),
            ("🧠 " + t('nav_ram'), 2),
        ]
        
        for text, index in tabs:
            btn = QPushButton(text)
            btn.setFixedHeight(48)
            btn.setFixedWidth(140)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._get_tab_style(index == 0))
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        # Settings button
        if SettingsDialog:
            settings_btn = QPushButton("⚙️")
            settings_btn.setFixedSize(48, 48)
            settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            settings_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #A0A0A0;
                    border: 2px solid #252525;
                    border-radius: 12px;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background: #1A1A1A;
                    color: #E63946;
                    border-color: #E63946;
                }
            """)
            settings_btn.clicked.connect(self._open_settings)
            layout.addWidget(settings_btn)
        
        header.setLayout(layout)
        return header

    def _get_tab_style(self, active=False) -> str:
        if active:
            return """
                QPushButton {
                    background: #E63946;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #FF4757;
                }
            """
        else:
            return """
                QPushButton {
                    background: transparent;
                    color: #A0A0A0;
                    border: 2px solid #252525;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #1A1A1A;
                    color: #FFFFFF;
                    border-color: #E63946;
                }
            """

    def _switch_page(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.setStyleSheet(self._get_tab_style(i == index))
        self.content_stack.setCurrentIndex(index)

    def _open_settings(self):
        """Open settings dialog"""
        if not SettingsDialog:
            return
        
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()
    
    def _on_settings_changed(self):
        """Handle settings changes"""
        # Update update interval
        new_interval = self.config.get_update_interval()
        self.update_timer.setInterval(new_interval)
        self.logger.info(f"Update interval changed to {new_interval}ms")
        
        # Reinitialize ML optimizer if enabled/disabled
        if ML_AVAILABLE:
            ml_enabled = self.config.is_ml_enabled()
            if self.ml_optimizer:
                self.ml_optimizer.enabled = ml_enabled
            else:
                self.ml_optimizer = init_ml_optimizer(ml_enabled)
            self.logger.info(f"ML optimizer {'enabled' if ml_enabled else 'disabled'}")

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)
        
        # Grid layout for cards
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Create metric cards
        self.gpu_card = MetricCard(t('metric_gpu_temp'))
        self.ram_card = MetricCard(t('metric_ram_usage'))
        self.cpu_card = MetricCard(t('metric_cpu_load'))
        
        grid.addWidget(self.gpu_card, 0, 0)
        grid.addWidget(self.ram_card, 0, 1)
        grid.addWidget(self.cpu_card, 0, 2)
        
        layout.addLayout(grid)
        
        # System info card
        info_card = self._create_system_info_card()
        layout.addWidget(info_card)
        
        # ML Recommendations (if enabled)
        if self.ml_optimizer and self.ml_optimizer.enabled:
            ml_card = self._create_ml_recommendations_card()
            layout.addWidget(ml_card)
        
        # Quick Boost button
        boost_btn = QPushButton("⚡ " + t('quick_boost'))
        boost_btn.setFixedHeight(60)
        boost_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        boost_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E63946, stop:1 #FF4757);
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 20px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF4757, stop:1 #E63946);
            }
        """)
        boost_btn.clicked.connect(self._quick_boost)
        layout.addWidget(boost_btn)
        
        # Bottom action cards
        actions = QHBoxLayout()
        actions.setSpacing(20)
        
        gpu_action = self._create_action_card(
            t('action_gpu_control'),
            t('action_gpu_desc'),
            lambda: self._switch_page(1)
        )
        ram_action = self._create_action_card(
            t('action_ram_tuner'),
            t('action_ram_desc'),
            lambda: self._switch_page(2)
        )
        
        actions.addWidget(gpu_action)
        actions.addWidget(ram_action)
        
        layout.addLayout(actions)
        layout.addStretch()
        
        page.setLayout(layout)
        return page

    def _create_system_info_card(self) -> QFrame:
        card = QFrame()
        card.setFixedHeight(120)
        card.setAutoFillBackground(True)
        card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-left: 4px solid #E63946;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("📊 " + t('system_info_title'))
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        layout.addWidget(title)
        
        info = QHBoxLayout()
        info.setSpacing(32)
        
        self.gpu_info_label = QLabel(t('loading'))
        self.gpu_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        info.addWidget(self.gpu_info_label)
        
        self.cpu_info_label = QLabel(t('loading'))
        self.cpu_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        info.addWidget(self.cpu_info_label)
        
        layout.addLayout(info)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def _create_ml_recommendations_card(self) -> QFrame:
        """Create ML recommendations card (shown only if ML enabled)"""
        card = QFrame()
        card.setFixedHeight(100)
        card.setAutoFillBackground(True)
        card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-left: 4px solid #FFA500;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🤖 " + t('ml_optimizer'))
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #FFA500;
                background: transparent;
            }
        """)
        layout.addWidget(title)
        
        self.ml_recommendations_label = QLabel(t('ai_learning'))
        self.ml_recommendations_label.setWordWrap(True)
        self.ml_recommendations_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        layout.addWidget(self.ml_recommendations_label)
        
        card.setLayout(layout)
        return card

    def _create_action_card(self, title: str, desc: str, callback) -> QFrame:
        card = QFrame()
        card.setFixedHeight(140)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setAutoFillBackground(True)
        card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border: 2px solid #252525;
                border-radius: 16px;
            }
            QFrame:hover {
                background-color: #252525;
                border-color: #E63946;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: #E63946;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        arrow = QLabel("→")
        arrow.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #E63946;
                background: transparent;
            }
        """)
        arrow.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(arrow)
        
        card.setLayout(layout)
        card.mousePressEvent = lambda e: callback()
        return card

    def _quick_boost(self):
        """Quick system optimization with ML tracking"""
        reply = QMessageBox.question(
            self,
            t('quick_boost_title'),
            t('quick_boost_msg'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Record state before optimization
            before_state = self._get_current_state()
            
            try:
                # Optimize process priorities
                current_process = psutil.Process()
                try:
                    if sys.platform == 'win32':
                        current_process.nice(psutil.HIGH_PRIORITY_CLASS)
                    else:
                        current_process.nice(-10)
                except:
                    pass
                
                # Log optimization
                self.logger.log_optimization("quick_boost", True, "Process priority optimized")
                
                # Record state after optimization
                after_state = self._get_current_state()
                
                # Train ML model (if enabled)
                if self.ml_optimizer and self.ml_optimizer.enabled:
                    self.ml_optimizer.record_optimization(
                        before_state,
                        after_state,
                        success=True
                    )
                
                QMessageBox.information(
                    self,
                    t('success'),
                    t('quick_boost_success')
                )
            except Exception as e:
                self.logger.log_error_with_trace("Quick boost failed", e)
                
                # Record failed optimization
                if self.ml_optimizer and self.ml_optimizer.enabled:
                    self.ml_optimizer.record_optimization(
                        before_state,
                        {},
                        success=False
                    )
                
                QMessageBox.warning(
                    self,
                    t('error'),
                    t('quick_boost_error', error=str(e))
                )
    
    def _get_current_state(self) -> dict:
        """Get current system state for ML"""
        try:
            data = self.system_monitor.get_all_data()
            return {
                'gpu_temp': data['gpu']['temp_hotspot'] or data['gpu']['temp_gpu'],
                'gpu_load': data['gpu']['load_gpu'],
                'cpu_load': data['cpu']['load'],
                'ram_percent': data['ram']['percent'],
            }
        except:
            return {}

    def _create_gpu_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        
        title = QLabel("⚡ " + t('gpu_control_title'))
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #E63946;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # GPU info card
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background: #1A1A1A;
                border-left: 4px solid #E63946;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        
        info_layout = QVBoxLayout()
        
        self.gpu_detail_label = QLabel(t('gpu_loading'))
        self.gpu_detail_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        info_layout.addWidget(self.gpu_detail_label)
        
        self.gpu_detail_load = QProgressBar()
        self.gpu_detail_load.setRange(0, 100)
        self.gpu_detail_load.setStyleSheet("""
            QProgressBar {
                border: none;
                background: #0D0D0D;
                border-radius: 8px;
                text-align: center;
                color: white;
                height: 24px;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E63946, stop:1 #FF4757);
                border-radius: 8px;
            }
        """)
        info_layout.addWidget(self.gpu_detail_load)
        
        info_card.setLayout(info_layout)
        layout.addWidget(info_card)
        
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_placeholder(self, name: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(f"🚧 {name}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-size: 32px;
            font-weight: 700;
            color: #666666;
        """)
        layout.addWidget(label)
        
        page.setLayout(layout)
        return page

    def _update_system_data(self):
        try:
            data = self.system_monitor.get_all_data()
            gpu = data["gpu"]
            cpu = data["cpu"]
            ram = data["ram"]
            
            # Update GPU card
            temp = gpu['temp_hotspot'] if gpu['temp_hotspot'] else gpu['temp_gpu']
            if self.gpu_card:
                self.gpu_card.set_value(f"{temp}°C")
                gpu_name_short = gpu['name'][:20] + "..." if len(gpu['name']) > 20 else gpu['name']
                self.gpu_card.set_subtitle(gpu_name_short)
                self.gpu_card.set_progress(int(gpu['load_gpu']), t('load_progress', value=int(gpu['load_gpu'])))
            
            # Update RAM card
            if self.ram_card:
                self.ram_card.set_value(f"{ram['used']:.1f}{t('unit_gb')}")
                self.ram_card.set_subtitle(f"{ram['total']:.0f}{t('unit_gb')} total | {ram['speed']}{t('unit_mhz')}")
                self.ram_card.set_progress(int(ram['percent']), f"{int(ram['percent'])}{t('unit_percent')}")
            
            # Update CPU card
            if self.cpu_card:
                self.cpu_card.set_value(f"{cpu['load']:.0f}{t('unit_percent')}")
                if cpu['temp']:
                    self.cpu_card.set_subtitle(t('cpu_temp', temp=cpu['temp']) + f" | {cpu['count']} cores")
                else:
                    self.cpu_card.set_subtitle(t('cpu_cores', count=cpu['count']) + f" | {cpu['freq']:.0f}{t('unit_mhz')}")
                self.cpu_card.set_progress(int(cpu['load']), t('load_progress', value=int(cpu['load'])))
            
            # System info card
            if hasattr(self, 'gpu_info_label'):
                self.gpu_info_label.setText(t('gpu_info', 
                    name=gpu['name'][:20] + "...",
                    clock=gpu['clock_gpu'],
                    temp=temp,
                    load=gpu['load_gpu']
                ))
                self.gpu_info_label.repaint()
            if hasattr(self, 'cpu_info_label'):
                self.cpu_info_label.setText(t('cpu_info',
                    cores=cpu['count'],
                    load=cpu['load'],
                    freq=cpu['freq']
                ))
                self.cpu_info_label.repaint()
            
            # ML Recommendations (if enabled)
            if self.ml_optimizer and self.ml_optimizer.enabled and hasattr(self, 'ml_recommendations_label'):
                current_state = {
                    'gpu_temp': temp,
                    'gpu_load': gpu['load_gpu'],
                    'cpu_load': cpu['load'],
                    'ram_percent': ram['percent'],
                }
                recommendations = self.ml_optimizer.get_recommendations(current_state)
                if recommendations:
                    self.ml_recommendations_label.setText("\n".join(recommendations[:2]))  # Show top 2
                else:
                    self.ml_recommendations_label.setText(t('ai_learning'))
                self.ml_recommendations_label.repaint()
            
            # GPU page
            if hasattr(self, 'gpu_detail_label'):
                self.gpu_detail_label.setText(
                    f"{gpu['name']}\n"
                    f"Temp: {temp}°C | Clock: {gpu['clock_gpu']}MHz | Memory: {gpu['clock_mem']}MHz\n"
                    f"Load: {gpu['load_gpu']:.0f}% | Power: {gpu['power']:.1f}W"
                )
                self.gpu_detail_label.repaint()
            if hasattr(self, 'gpu_detail_load'):
                self.gpu_detail_load.setValue(int(gpu['load_gpu']))
                self.gpu_detail_load.setFormat(f"GPU Load: {int(gpu['load_gpu'])}%")
                self.gpu_detail_load.repaint()
                
        except Exception as e:
            self.logger.error(f"Error updating UI: {e}")

    def closeEvent(self, event):
        self.logger.log_shutdown()
        self.update_timer.stop()
        self.system_monitor.cleanup()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = PartMartMainWindow()
    window.show()
    sys.exit(app.exec())
