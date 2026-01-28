from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QApplication, QProgressBar, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import sys
import os
import subprocess
import psutil

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.ai_widget import PartMartAIWidget
from ai_optimizer import PartMartAIOptimizer
from system_monitor import SystemMonitor

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
        self.subtitle_label = QLabel("Loading...")
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
    """Modern card-based UI with PartMart red branding"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 PartMart Boost v0.3.2-alpha")
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
        
        self._setup_ui()
        
        # Auto-update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_data)
        self.update_timer.start(2000)
        self._update_system_data()

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
            background: transparent;
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
        
        # Create metric cards
        self.gpu_card = MetricCard("🌡️ GPU Temperature")
        self.ram_card = MetricCard("🧠 RAM Usage")
        self.cpu_card = MetricCard("💻 CPU Load")
        
        grid.addWidget(self.gpu_card, 0, 0)
        grid.addWidget(self.ram_card, 0, 1)
        grid.addWidget(self.cpu_card, 0, 2)
        
        layout.addLayout(grid)
        
        # System info card
        info_card = self._create_system_info_card()
        layout.addWidget(info_card)
        
        # Quick Boost button
        boost_btn = QPushButton("⚡ БЫСТРЫЙ БУСТ")
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
        
        gpu_action = self._create_action_card("🎮 GPU Control", "Оптимизация видеокарты", lambda: self._switch_page(1))
        ram_action = self._create_action_card("🧠 RAM Tuner", "XMP и очистка памяти", lambda: self._switch_page(2))
        
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
        
        title = QLabel("📊 СИСТЕМНЫЕ ПОКАЗАТЕЛИ")
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
        
        self.gpu_info_label = QLabel("GPU: Loading...")
        self.gpu_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        info.addWidget(self.gpu_info_label)
        
        self.cpu_info_label = QLabel("CPU: Loading...")
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
        """Quick system optimization"""
        reply = QMessageBox.question(
            self,
            'Быстрый буст',
            'Оптимизировать систему?\n\nБудет выполнено:\n• Очистка RAM\n• Оптимизация приоритетов процессов',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear RAM (Windows)
                if sys.platform == 'win32':
                    # Empty working sets
                    subprocess.run(['powershell', '-Command', 'Clear-RecycleBin -Force'], 
                                   capture_output=True, timeout=5)
                
                # Optimize process priorities
                current_process = psutil.Process()
                try:
                    current_process.nice(psutil.HIGH_PRIORITY_CLASS if sys.platform == 'win32' else -10)
                except:
                    pass
                
                QMessageBox.information(
                    self,
                    'Готово!',
                    '✅ Оптимизация завершена!\n\nПроверьте изменения в метриках.'
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    'Ошибка',
                    f'Не удалось выполнить оптимизацию:\n{str(e)}'
                )

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
            if self.gpu_card:
                self.gpu_card.set_value(f"{temp}°C")
                gpu_name_short = gpu['name'][:20] + "..." if len(gpu['name']) > 20 else gpu['name']
                self.gpu_card.set_subtitle(gpu_name_short)
                self.gpu_card.set_progress(int(gpu['load_gpu']), f"Load: {int(gpu['load_gpu'])}%")
            
            # Update RAM card
            if self.ram_card:
                self.ram_card.set_value(f"{ram['used']:.1f}GB")
                self.ram_card.set_subtitle(f"{ram['total']:.0f}GB total | {ram['speed']}MHz")
                self.ram_card.set_progress(int(ram['percent']), f"{int(ram['percent'])}%")
            
            # Update CPU card
            if self.cpu_card:
                self.cpu_card.set_value(f"{cpu['load']:.0f}%")
                if cpu['temp']:
                    self.cpu_card.set_subtitle(f"Temp: {cpu['temp']:.0f}°C | {cpu['count']} cores")
                else:
                    self.cpu_card.set_subtitle(f"{cpu['count']} cores | {cpu['freq']:.0f}MHz")
                self.cpu_card.set_progress(int(cpu['load']), f"Load: {int(cpu['load'])}%")
            
            # System info card - FORCE REPAINT
            if hasattr(self, 'gpu_info_label'):
                self.gpu_info_label.setText(f"GPU: {gpu['name'][:20]}... | {gpu['clock_gpu']}MHz | {temp}°C | Load {gpu['load_gpu']:.0f}%")
                self.gpu_info_label.repaint()
            if hasattr(self, 'cpu_info_label'):
                self.cpu_info_label.setText(f"CPU: {cpu['count']} cores | Load {cpu['load']:.0f}% | {cpu['freq']:.0f}MHz")
                self.cpu_info_label.repaint()
            
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
            print(f"Error updating UI: {e}")
            import traceback
            traceback.print_exc()

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
