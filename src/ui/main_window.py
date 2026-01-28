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
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys
import os

# Add src directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Absolute imports from src package
from ui.ai_widget import PartMartAIWidget
from ai_optimizer import PartMartAIOptimizer

class PartMartMainWindow(QMainWindow):
    """Steam-like main window for PartMart Boost"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 PartMart Boost")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)
        
        self.ai_engine = PartMartAIOptimizer()
        self.nav_button_group = []
        
        self._load_theme()
        self._setup_ui()
        self._initial_analysis()

    def _load_theme(self) -> None:
        """Load QSS theme"""
        try:
            theme_path = os.path.join(os.path.dirname(__file__), "theme.qss")
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            # Fallback: basic background
            self.setStyleSheet("QMainWindow { background-color: #1B2838; }")

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: #1B2838;")

        # Pages
        self.page_home = self._create_home_page()
        self.page_gpu = self._create_gpu_page()
        self.page_ram = QLabel("RAM PAGE (TODO)")
        self.page_framegen = QLabel("FRAMEGEN PAGE (TODO)")
        self.page_games = QLabel("GAMES PAGE (TODO)")
        self.page_settings = QLabel("SETTINGS PAGE (TODO)")

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

    def _initial_analysis(self):
        sample_data = {"gpu_temp": 55, "ram_usage_percent": 90, "cpu_load": 45, "current_fps": 120}
        report = self.ai_engine.analyze_system(sample_data)
        pass

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2A475E, stop:1 #1B2838);
                border-right: 2px solid #2A475E;
            }
            """
        )

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 24, 16, 24)

        logo_label = QLabel("🐉")
        logo_label.setStyleSheet("font-size: 48px; color: #E63946;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        title_label = QLabel("PartMart Boost")
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: white;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Твой ПК. Твоя мощь.")
        subtitle_label.setStyleSheet(
            "font-size: 11px; color: #B8B6B4; margin-bottom: 20px;"
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        nav_buttons = [
            ("🏠", "ГЛАВНАЯ", 0),
            ("⚡", "GPU", 1),
            ("🧠", "RAM", 2),
            ("🎮", "FrameGen", 3),
            ("🎯", "ИГРЫ", 4),
            ("⚙️", "НАСТРОЙКИ", 5),
        ]

        for emoji, text, index in nav_buttons:
            btn = self._create_nav_button(emoji, text, index)
            layout.addWidget(btn)
            self.nav_button_group.append(btn)

        layout.addStretch()

        version_label = QLabel("v0.1.0-dev")
        version_label.setStyleSheet("color: #8B8B8B; font-size: 10px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        sidebar.setLayout(layout)
        return sidebar

    def _create_nav_button(self, emoji: str, text: str, index: int) -> QPushButton:
        btn = QPushButton(f"{emoji} {text}")
        btn.setFixedHeight(50)
        btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                color: #B8B6B4;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding-left: 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2A475E;
                color: white;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #E63946, stop:1 #C11F28);
                color: white;
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
                        stop:0 #E63946, stop:1 #C11F28);
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                        padding-left: 16px;
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
                        color: #B8B6B4;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                        padding-left: 16px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #2A475E;
                        color: white;
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
            "font-size: 32px; font-weight: 700; color: white; margin-bottom: 8px;"
        )
        layout.addWidget(header)

        subtitle = QLabel("Оптимизируй свой ПК в один клик")
        subtitle.setStyleSheet("font-size: 16px; color: #B8B6B4;")
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
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        layout.addWidget(title)
        
        # Adding AI Insights to GPU page
        layout.addSpacing(20)
        ai_insights = PartMartAIWidget()
        ai_insights.update_insights(self.ai_engine.analyze_system({"gpu_temp": 75, "ram_usage_percent": 45}))
        layout.addWidget(ai_insights)
        
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_status_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(180)
        card.setStyleSheet(
            """
            QFrame#card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2A475E, stop:1 #1B2838);
                border: 2px solid #2A475E;
                border-radius: 12px;
                padding: 24px;
            }
            """
        )
        layout = QVBoxLayout()
        title = QLabel("💻 СТАТУС СИСТЕМЫ")
        title.setStyleSheet(
            "font-size: 18px; font-weight: 600; color: #66C0F4;"
        )
        layout.addWidget(title)
        layout.addSpacing(12)

        gpu_label = QLabel("🎮 GPU: NVIDIA RTX 3060 (stock settings)")
        gpu_label.setStyleSheet("font-size: 14px; color: white;")
        layout.addWidget(gpu_label)

        ram_label = QLabel("🧠 RAM: 16GB DDR4-3200 MHz (XMP: ❌ ВЫКЛЮЧЕН)")
        ram_label.setStyleSheet("font-size: 14px; color: #F79F1A;")
        layout.addWidget(ram_label)

        temp_label = QLabel("🌡️ Температура: GPU 42°C | CPU 38°C")
        temp_label.setStyleSheet("font-size: 14px; color: #5DA130;")
        layout.addWidget(temp_label)

        layout.addStretch()
        card.setLayout(layout)
        return card

    def _create_quick_boost_card(self) -> QFrame:
        card = QFrame()
        card.setFixedHeight(220)
        card.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #E63946, stop:1 #C11F28);
                border-radius: 12px;
                padding: 32px;
            }
            """
        )
        layout = QVBoxLayout()
        title = QLabel("⚡ БЫСТРЫЙ БУСТ")
        title.setStyleSheet(
            """
            font-size: 24px;
            font-weight: 700;
            color: white;
            text-transform: uppercase;
            """
        )
        layout.addWidget(title)

        desc = QLabel("GPU + RAM + FrameGen + Очистка")
        desc.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")
        layout.addWidget(desc)

        layout.addSpacing(12)
        expected = QLabel("📈 Ожидаемый прирост: +40-60 FPS")
        expected.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: white;"
        )
        layout.addWidget(expected)

        layout.addSpacing(16)
        boost_btn = QPushButton("ЗАПУСТИТЬ ОПТИМИЗАЦИЮ")
        boost_btn.setFixedHeight(60)
        boost_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                color: #E63946;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: #F1FAEE;
            }
            QPushButton:pressed {
                background: #E0E0E0;
            }
            """
        )
        layout.addWidget(boost_btn)
        card.setLayout(layout)
        return card

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = PartMartMainWindow()
    window.show()
    sys.exit(app.exec())
