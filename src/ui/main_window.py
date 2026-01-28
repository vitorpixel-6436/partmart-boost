from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QApplication, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.ai_widget import PartMartAIWidget
from ai_optimizer import PartMartAIOptimizer
from system_monitor import SystemMonitor

class PartMartMainWindow(QMainWindow):
    """Modern card-based UI with PartMart red branding"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 PartMart Boost v0.3-alpha")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Initialize monitoring
        self.system_monitor = SystemMonitor()
        self.ai_engine = PartMartAIOptimizer()
        self.nav_buttons = []
        
        # UI elements for updates
        self.gpu_temp_label = None
        self.cpu_load_label = None
        self.ram_value_label = None
        self.gpu_name_label = None
        self.cpu_temp_label = None
        self.ram_subtitle_label = None
        self.gpu_load_bar = None
        self.ram_usage_bar = None
        self.cpu_load_bar = None
        
        self._setup_ui()
        
        # Auto-update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_data)
        self.update_timer.start(2000)
        self._update_system_data()

    def _setup_ui(self):
        # Main stylesheet with PartMart red branding
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D0D0D;
            }
            QLabel {
                color: #FFFFFF;
            }
            QProgressBar {
                border: none;
                background: #1A1A1A;
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
        self.page_ram = self._create_placeholder("RAM TUNER")
        
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
        """)
        layout.addWidget(logo)
        
        layout.addStretch()
        
        # Navigation tabs
        tabs = [
            ("🏠 Главная", 0),
            ("🎮 GPU", 1),
            ("🧠 RAM", 2),
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

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)
        
        # Grid layout for cards
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # GPU Card
        gpu_card, self.gpu_temp_label, self.gpu_name_label, self.gpu_load_bar = self._create_metric_card(
            "🌡️ GPU Temperature",
            "--°C",
            "Loading..."
        )
        grid.addWidget(gpu_card, 0, 0)
        
        # RAM Card
        ram_card, self.ram_value_label, self.ram_subtitle_label, self.ram_usage_bar = self._create_metric_card(
            "🧠 RAM Usage",
            "--GB",
            "Loading..."
        )
        grid.addWidget(ram_card, 0, 1)
        
        # CPU Card
        cpu_card, self.cpu_load_label, self.cpu_temp_label, self.cpu_load_bar = self._create_metric_card(
            "💻 CPU Load",
            "--%",
            "Loading..."
        )
        grid.addWidget(cpu_card, 0, 2)
        
        layout.addLayout(grid)
        
        # System info card
        info_card = self._create_system_info_card()
        layout.addWidget(info_card)
        
        # Bottom action cards
        actions = QHBoxLayout()
        actions.setSpacing(20)
        
        gpu_action = self._create_action_card("🎮 GPU Control", "Оптимизация видеокарты", lambda: self._switch_page(1))
        ram_action = self._create_action_card("🧠 RAM Tuner", "XMP и очистка памяти", lambda: self._switch_page(2))
        
        actions.addWidget(gpu_action)
        actions.addWidget(ram_action)
        
        layout.addLayout(actions)
        layout.addStretch()
        
        page.setLayout(layout)
        return page

    def _create_metric_card(self, title: str, value: str, subtitle: str):
        """Create metric card and return (card, value_label, subtitle_label, progress_bar)"""
        card = QFrame()
        card.setFixedHeight(180)
        card.setStyleSheet("""
            QFrame {
                background: #1A1A1A;
                border-left: 4px solid #E63946;
                border-radius: 16px;
                padding: 20px;
            }
            QFrame:hover {
                background: #252525;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #A0A0A0;
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 36px;
            font-weight: 700;
            color: #E63946;
        """)
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #666666;
        """)
        layout.addWidget(subtitle_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        layout.addWidget(progress)
        
        card.setLayout(layout)
        return card, value_label, subtitle_label, progress

    def _create_system_info_card(self) -> QFrame:
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A1A1A, stop:1 #252525);
                border-left: 4px solid #E63946;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("📊 СИСТЕМНЫЕ ПОКАЗАТЕЛИ")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
        layout.addWidget(title)
        
        info = QHBoxLayout()
        info.setSpacing(32)
        
        self.gpu_info_label = QLabel("GPU: Loading...")
        self.gpu_info_label.setStyleSheet("font-size: 13px; color: #A0A0A0;")
        info.addWidget(self.gpu_info_label)
        
        self.cpu_info_label = QLabel("CPU: Loading...")
        self.cpu_info_label.setStyleSheet("font-size: 13px; color: #A0A0A0;")
        info.addWidget(self.cpu_info_label)
        
        layout.addLayout(info)
        layout.addStretch()
        
        card.setLayout(layout)
        return card

    def _create_action_card(self, title: str, desc: str, callback) -> QFrame:
        card = QFrame()
        card.setFixedHeight(140)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background: #1A1A1A;
                border: 2px solid #252525;
                border-radius: 16px;
                padding: 20px;
            }
            QFrame:hover {
                background: #252525;
                border-color: #E63946;
            }
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #E63946;
        """)
        layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("""
            font-size: 13px;
            color: #A0A0A0;
        """)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        arrow = QLabel("→")
        arrow.setStyleSheet("font-size: 24px; color: #E63946;")
        arrow.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(arrow)
        
        card.setLayout(layout)
        card.mousePressEvent = lambda e: callback()
        return card

    def _create_gpu_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        
        title = QLabel("⚡ GPU CONTROL")
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
        
        self.gpu_detail_label = QLabel("Loading GPU info...")
        self.gpu_detail_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        info_layout.addWidget(self.gpu_detail_label)
        
        self.gpu_detail_load = QProgressBar()
        self.gpu_detail_load.setRange(0, 100)
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
        
        label = QLabel(f"🚧 {name}\n\nComing Soon")
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
            if self.gpu_temp_label:
                self.gpu_temp_label.setText(f"{temp}°C")
            if self.gpu_name_label:
                gpu_name_short = gpu['name'][:25] + "..." if len(gpu['name']) > 25 else gpu['name']
                self.gpu_name_label.setText(gpu_name_short)
            if self.gpu_load_bar:
                self.gpu_load_bar.setValue(int(gpu['load_gpu']))
                self.gpu_load_bar.setFormat(f"Load: {int(gpu['load_gpu'])}%")
            
            # Update RAM card
            if self.ram_value_label:
                self.ram_value_label.setText(f"{ram['used']:.1f}GB")
            if self.ram_subtitle_label:
                self.ram_subtitle_label.setText(f"{ram['total']:.0f}GB total | {ram['speed']}MHz")
            if self.ram_usage_bar:
                self.ram_usage_bar.setValue(int(ram['percent']))
                self.ram_usage_bar.setFormat(f"{int(ram['percent'])}%")
            
            # Update CPU card
            if self.cpu_load_label:
                self.cpu_load_label.setText(f"{cpu['load']:.0f}%")
            if self.cpu_temp_label:
                if cpu['temp']:
                    self.cpu_temp_label.setText(f"Temp: {cpu['temp']:.0f}°C | {cpu['count']} cores")
                else:
                    self.cpu_temp_label.setText(f"{cpu['count']} cores | {cpu['freq']:.0f}MHz")
            if self.cpu_load_bar:
                self.cpu_load_bar.setValue(int(cpu['load']))
                self.cpu_load_bar.setFormat(f"{int(cpu['load'])}%")
            
            # System info card
            if hasattr(self, 'gpu_info_label'):
                self.gpu_info_label.setText(f"GPU: {gpu['name'][:20]}... | {gpu['clock_gpu']}MHz | {temp}°C | Load {gpu['load_gpu']:.0f}%")
            if hasattr(self, 'cpu_info_label'):
                self.cpu_info_label.setText(f"CPU: {cpu['count']} cores | Load {cpu['load']:.0f}% | {cpu['freq']:.0f}MHz")
            
            # GPU page
            if hasattr(self, 'gpu_detail_label'):
                self.gpu_detail_label.setText(
                    f"{gpu['name']}\n"
                    f"Temp: {temp}°C | Clock: {gpu['clock_gpu']}MHz | Memory: {gpu['clock_mem']}MHz\n"
                    f"Load: {gpu['load_gpu']:.0f}% | Power: {gpu['power']:.1f}W"
                )
            if hasattr(self, 'gpu_detail_load'):
                self.gpu_detail_load.setValue(int(gpu['load_gpu']))
                self.gpu_detail_load.setFormat(f"GPU Load: {int(gpu['load_gpu'])}%")
                
        except Exception as e:
            print(f"Error updating UI: {e}")

    def closeEvent(self, event):
        self.update_timer.stop()
        self.system_monitor.cleanup()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = PartMartMainWindow()
    window.show()
    sys.exit(app.exec())
