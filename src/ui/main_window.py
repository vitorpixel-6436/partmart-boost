from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QStackedWidget,
    QApplication,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys
import os

# Add src directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Absolute imports from src package
from ui.ai_widget import PartMartAIWidget
from ai_optimizer import PartMartAIOptimizer
from system_monitor import SystemMonitor

class PartMartMainWindow(QMainWindow):
    """Steam Big Picture inspired main window for PartMart Boost"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 PartMart Boost v0.2-alpha")
        self.setGeometry(100, 100, 1280, 800)
        self.setMinimumSize(1000, 600)
        
        # Initialize monitoring
        self.system_monitor = SystemMonitor()
        self.ai_engine = PartMartAIOptimizer()
        self.nav_button_group = []
        
        # Store UI elements for updates
        self.gpu_temp_label = None
        self.cpu_temp_label = None
        self.ram_label = None
        self.gpu_name_label = None
        self.gpu_load_bar = None
        self.ram_usage_bar = None
        
        self._load_theme()
        self._setup_ui()
        
        # Setup auto-update timer (2 seconds)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_data)
        self.update_timer.start(2000)
        
        # Initial update
        self._update_system_data()

    def _load_theme(self) -> None:
        """Load Steam-inspired QSS theme"""
        theme = """
        QMainWindow {
            background-color: #171a21;
        }
        
        QLabel {
            color: #c7d5e0;
        }
        
        QProgressBar {
            border: none;
            background: #1b2838;
            border-radius: 4px;
            text-align: center;
            color: white;
            height: 20px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5c7e10, stop:1 #7cb02a);
            border-radius: 4px;
        }
        """
        self.setStyleSheet(theme)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: #171a21;")

        # Pages
        self.page_home = self._create_home_page()
        self.page_gpu = self._create_gpu_page()
        self.page_ram = QLabel("🧠 RAM OPTIMIZER (Coming Soon)")
        self.page_framegen = QLabel("🎮 FRAMEGEN (Coming Soon)")
        self.page_games = QLabel("🎯 GAME PROFILES (Coming Soon)")
        self.page_settings = QLabel("⚙️ SETTINGS (Coming Soon)")
        
        for lbl in [self.page_ram, self.page_framegen, self.page_games, self.page_settings]:
            lbl.setStyleSheet("font-size: 24px; color: #66c0f4; padding: 40px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for page in (
            self.page_home,
            self.page_gpu,
            self.page_ram,
            self.page_framegen,
            self.page_games,
            self.page_settings,
        ):
            self.content_stack.addWidget(page)

        main_layout.addWidget(self.content_stack)
        central.setLayout(main_layout)

    def _update_system_data(self):
        """Update system data from real sensors"""
        try:
            data = self.system_monitor.get_all_data()
            
            # Update GPU data
            gpu = data["gpu"]
            temp_display = f"{gpu['temp_gpu']}°C"
            if gpu['temp_hotspot'] is not None:
                temp_display = f"{gpu['temp_hotspot']}°C (hotspot)"
            
            if self.gpu_temp_label:
                self.gpu_temp_label.setText(f"🌡️ GPU: {temp_display}")
            
            if self.gpu_name_label:
                status = "stock settings" if gpu['load_gpu'] < 50 else f"{gpu['load_gpu']}% load"
                self.gpu_name_label.setText(f"🎮 GPU: {gpu['name']} ({status})")
            
            if self.gpu_load_bar:
                self.gpu_load_bar.setValue(int(gpu['load_gpu']))
            
            # Update CPU data
            cpu = data["cpu"]
            if self.cpu_temp_label:
                if cpu['temp'] is not None:
                    self.cpu_temp_label.setText(f"💻 CPU: {cpu['temp']:.0f}°C | Load: {cpu['load']:.0f}%")
                else:
                    self.cpu_temp_label.setText(f"💻 CPU: Load {cpu['load']:.0f}%")
            
            # Update RAM data
            ram = data["ram"]
            xmp_status = "✅ ВКЛЮЧЕН" if ram['xmp_enabled'] else "❌ ВЫКЛЮЧЕН"
            xmp_color = "#5DA130" if ram['xmp_enabled'] else "#F79F1A"
            
            if self.ram_label:
                speed_text = f"{ram['speed']} MHz" if ram['speed'] > 0 else "Unknown"
                self.ram_label.setText(
                    f"🧠 RAM: {ram['used']:.1f}GB / {ram['total']:.1f}GB ({speed_text})"
                )
                self.ram_label.setStyleSheet(f"font-size: 14px; color: {xmp_color};")
            
            if self.ram_usage_bar:
                self.ram_usage_bar.setValue(int(ram['percent']))
            
        except Exception as e:
            print(f"Error updating system data: {e}")

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1b2838, stop:1 #171a21);
                border-right: 1px solid #2a475e;
            }
            """
        )

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(16, 24, 16, 24)

        logo_label = QLabel("🐉")
        logo_label.setStyleSheet("font-size: 64px; color: #66c0f4;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        title_label = QLabel("PartMart Boost")
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #66c0f4; letter-spacing: 2px;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Твой ПК. Твоя мощь.")
        subtitle_label.setStyleSheet(
            "font-size: 11px; color: #8f98a0; margin-bottom: 20px;"
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(20)

        nav_buttons = [
            ("🏠", "ГЛАВНАЯ", 0),
            ("⚡", "GPU CONTROL", 1),
            ("🧠", "RAM TUNER", 2),
            ("🎮", "FRAMEGEN", 3),
            ("🎯", "ИГРЫ", 4),
            ("⚙️", "НАСТРОЙКИ", 5),
        ]

        for emoji, text, index in nav_buttons:
            btn = self._create_nav_button(emoji, text, index)
            layout.addWidget(btn)
            self.nav_button_group.append(btn)

        layout.addStretch()

        version_label = QLabel("v0.2.0-alpha")
        version_label.setStyleSheet("color: #8f98a0; font-size: 10px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        sidebar.setLayout(layout)
        return sidebar

    def _create_nav_button(self, emoji: str, text: str, index: int) -> QPushButton:
        btn = QPushButton(f"{emoji}  {text}")
        btn.setFixedHeight(56)
        btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: #8f98a0;
                border: none;
                border-left: 4px solid transparent;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #1b2838;
                color: #c7d5e0;
                border-left: 4px solid #66c0f4;
            }
            """
        )
        btn.clicked.connect(lambda: self._switch_page(index))
        return btn

    def _switch_page(self, index: int) -> None:
        for i, btn in enumerate(self.nav_button_group):
            if i == index:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1b2838, stop:1 #2a475e);
                        color: #66c0f4;
                        border: none;
                        border-left: 4px solid #66c0f4;
                        text-align: left;
                        padding-left: 20px;
                        font-size: 14px;
                        font-weight: 600;
                    }
                    """
                )
            else:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background: transparent;
                        color: #8f98a0;
                        border: none;
                        border-left: 4px solid transparent;
                        text-align: left;
                        padding-left: 20px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #1b2838;
                        color: #c7d5e0;
                        border-left: 4px solid #66c0f4;
                    }
                    """
                )
        self.content_stack.setCurrentIndex(index)

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        header = QLabel("🚀 БЫСТРЫЙ СТАРТ")
        header.setStyleSheet(
            "font-size: 36px; font-weight: 700; color: #66c0f4; letter-spacing: 2px;"
        )
        layout.addWidget(header)

        subtitle = QLabel("Оптимизируй свой ПК в один клик")
        subtitle.setStyleSheet("font-size: 16px; color: #8f98a0;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)
        status_card = self._create_status_card()
        layout.addWidget(status_card)

        layout.addSpacing(20)
        boost_card = self._create_quick_boost_card()
        layout.addWidget(boost_card)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_gpu_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("⚡ GPU CONTROL")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #66c0f4;")
        layout.addWidget(title)
        
        # GPU Load bar
        load_label = QLabel("GPU Load:")
        load_label.setStyleSheet("font-size: 14px; color: #8f98a0; margin-top: 20px;")
        layout.addWidget(load_label)
        
        self.gpu_load_bar = QProgressBar()
        self.gpu_load_bar.setRange(0, 100)
        self.gpu_load_bar.setValue(0)
        layout.addWidget(self.gpu_load_bar)
        
        # AI Insights
        layout.addSpacing(20)
        ai_insights = PartMartAIWidget()
        ai_insights.update_insights(self.ai_engine.analyze_system({"gpu_temp": 70, "ram_usage_percent": 45}))
        layout.addWidget(ai_insights)
        
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_status_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(200)
        card.setStyleSheet(
            """
            QFrame#card {
                background: #1b2838;
                border: 1px solid #2a475e;
                border-radius: 16px;
                padding: 24px;
            }
            """
        )
        layout = QVBoxLayout()
        
        title = QLabel("💻 СТАТУС СИСТЕМЫ (РЕАЛЬНЫЕ ДАННЫЕ)")
        title.setStyleSheet(
            "font-size: 18px; font-weight: 600; color: #66c0f4;"
        )
        layout.addWidget(title)
        layout.addSpacing(12)

        self.gpu_name_label = QLabel("🎮 GPU: Loading...")
        self.gpu_name_label.setStyleSheet("font-size: 14px; color: white;")
        layout.addWidget(self.gpu_name_label)

        self.ram_label = QLabel("🧠 RAM: Loading...")
        self.ram_label.setStyleSheet("font-size: 14px; color: #F79F1A;")
        layout.addWidget(self.ram_label)
        
        # RAM usage bar
        self.ram_usage_bar = QProgressBar()
        self.ram_usage_bar.setRange(0, 100)
        self.ram_usage_bar.setValue(0)
        self.ram_usage_bar.setFixedHeight(16)
        layout.addWidget(self.ram_usage_bar)

        self.gpu_temp_label = QLabel("🌡️ GPU: --°C")
        self.gpu_temp_label.setStyleSheet("font-size: 14px; color: #5DA130; margin-top: 8px;")
        layout.addWidget(self.gpu_temp_label)
        
        self.cpu_temp_label = QLabel("💻 CPU: --°C")
        self.cpu_temp_label.setStyleSheet("font-size: 14px; color: #5DA130;")
        layout.addWidget(self.cpu_temp_label)

        layout.addStretch()
        card.setLayout(layout)
        return card

    def _create_quick_boost_card(self) -> QFrame:
        card = QFrame()
        card.setFixedHeight(240)
        card.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #5c7e10, stop:1 #7cb02a);
                border-radius: 16px;
                padding: 32px;
            }
            """
        )
        layout = QVBoxLayout()
        title = QLabel("⚡ БЫСТРЫЙ БУСТ")
        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: 700;
            color: white;
            letter-spacing: 2px;
            """
        )
        layout.addWidget(title)

        desc = QLabel("GPU Optimize + RAM Cleanup + System Tweaks")
        desc.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        layout.addWidget(desc)

        layout.addSpacing(12)
        expected = QLabel("📈 Ожидаемый прирост: +30-50 FPS")
        expected.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: white;"
        )
        layout.addWidget(expected)

        layout.addSpacing(16)
        boost_btn = QPushButton("🚀 ЗАПУСТИТЬ ОПТИМИЗАЦИЮ")
        boost_btn.setFixedHeight(64)
        boost_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                color: #5c7e10;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
            QPushButton:pressed {
                background: #e0e0e0;
            }
            """
        )
        layout.addWidget(boost_btn)
        card.setLayout(layout)
        return card
    
    def closeEvent(self, event):
        """Cleanup on close"""
        self.update_timer.stop()
        self.system_monitor.cleanup()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = PartMartMainWindow()
    window.show()
    sys.exit(app.exec())
