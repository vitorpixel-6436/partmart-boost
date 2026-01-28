"""Main window - Version 0.3.5b

Fixes:
- Metrics now ALWAYS show even without full data
- Game wizard for easy game adding
- Start of custom UI components
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QApplication, QProgressBar, 
    QGridLayout, QMessageBox, QDialog, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QAction
import sys
import os
import subprocess
import psutil

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from localization import t, set_language, get_current_language
from core.config import get_config
from core.logger import get_logger
from ui.ai_widget import PartMartAIWidget
from ai_optimizer import PartMartAIOptimizer
from system_monitor import SystemMonitor
from ui.settings_dialog import SettingsDialog

# Game Profiles imports
GAMES_AVAILABLE = False
try:
    from profiles.game_profiles import GameProfileManager
    from profiles.game_detector import GameDetector
    from profiles.optimization_applier import ProfileApplier
    from ui.games_widget import GamesWidget
    GAMES_AVAILABLE = True
    print("[OK] Game Profiles system loaded")
except ImportError as e:
    print(f"[WARN] Game Profiles not available: {e}")
    GAMES_AVAILABLE = False


class GameWizard(QDialog):
    """Simple wizard for adding games"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎮 Добавить игру")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        self.game_name = ""
        self.exe_name = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎮 Добавить игру")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #E63946;
        """)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "📖 Как узнать имя .exe:\n"
            "1. Запусти игру\n"
            "2. Открой Task Manager (Ctrl+Shift+Esc)\n"
            "3. Вкладка Details\n"
            "4. Найди процесс игры и скопируй имя"
        )
        instructions.setStyleSheet("""
            font-size: 13px;
            color: #A0A0A0;
            background: #1A1A1A;
            border-radius: 8px;
            padding: 15px;
        """)
        layout.addWidget(instructions)
        
        # Game name input
        name_label = QLabel("🎮 Название игры:")
        name_label.setStyleSheet("font-size: 14px; font-weight: 600; color: white;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Escape From Tarkov")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #1A1A1A;
                border: 2px solid #252525;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                padding: 12px;
            }
            QLineEdit:focus {
                border-color: #E63946;
            }
        """)
        layout.addWidget(self.name_input)
        
        # EXE name input
        exe_label = QLabel("💻 Имя .exe файла:")
        exe_label.setStyleSheet("font-size: 14px; font-weight: 600; color: white;")
        layout.addWidget(exe_label)
        
        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("Например: EscapeFromTarkov.exe")
        self.exe_input.setStyleSheet("""
            QLineEdit {
                background: #1A1A1A;
                border: 2px solid #252525;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                padding: 12px;
            }
            QLineEdit:focus {
                border-color: #E63946;
            }
        """)
        layout.addWidget(self.exe_input)
        
        # Priority select
        priority_label = QLabel("⚡ Приоритет:")
        priority_label.setStyleSheet("font-size: 14px; font-weight: 600; color: white;")
        layout.addWidget(priority_label)
        
        priority_layout = QHBoxLayout()
        
        self.priority_high = QPushButton("🔥 Высокий")
        self.priority_high.setCheckable(True)
        self.priority_high.setChecked(True)
        self.priority_high.setStyleSheet("""
            QPushButton {
                background: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:checked {
                background: #FF4757;
            }
            QPushButton:hover {
                background: #FF4757;
            }
        """)
        
        self.priority_normal = QPushButton("💪 Обычный")
        self.priority_normal.setCheckable(True)
        self.priority_normal.setStyleSheet("""
            QPushButton {
                background: #1A1A1A;
                color: white;
                border: 2px solid #252525;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:checked {
                background: #E63946;
                border-color: #E63946;
            }
            QPushButton:hover {
                border-color: #E63946;
            }
        """)
        
        priority_layout.addWidget(self.priority_high)
        priority_layout.addWidget(self.priority_normal)
        layout.addLayout(priority_layout)
        
        # Buttons
        layout.addStretch()
        
        buttons = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setFixedHeight(50)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #1A1A1A;
                color: white;
                border: 2px solid #252525;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                border-color: #E63946;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        save_btn = QPushButton("✅ Сохранить")
        save_btn.setFixedHeight(50)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #FF4757;
            }
        """)
        save_btn.clicked.connect(self._save)
        buttons.addWidget(save_btn)
        
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
        # Style dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #0D0D0D;
            }
        """)
    
    def _save(self):
        self.game_name = self.name_input.text().strip()
        self.exe_name = self.exe_input.text().strip()
        
        if not self.game_name:
            QMessageBox.warning(self, "Ошибка", "Введите название игры!")
            return
        
        if not self.exe_name:
            QMessageBox.warning(self, "Ошибка", "Введите имя .exe файла!")
            return
        
        if not self.exe_name.endswith('.exe'):
            self.exe_name += '.exe'
        
        self.accept()
    
    def get_data(self):
        priority = "high" if self.priority_high.isChecked() else "normal"
        
        return {
            "game_name": self.game_name,
            "enabled": True,
            "executable_names": [self.exe_name],
            "priority": priority,
            "ram": {
                "enabled": True,
                "cleanup_before_launch": True,
                "reserved_mb": 4096
            },
            "gpu": {
                "enabled": True,
                "power_limit": 100,
                "temp_limit": 85,
                "fan_curve": "aggressive"
            },
            "windows": {
                "game_mode": True,
                "fullscreen_optimizations": False,
                "hags": True,
                "game_bar": False
            }
        }


class MetricCard(QFrame):
    """Metric card - ALWAYS shows something even without data"""
    
    def __init__(self, title_key: str, icon: str, parent=None):
        super().__init__(parent)
        self.title_key = title_key
        self.icon = icon
        self.setFixedHeight(180)
        self.setAutoFillBackground(True)
        
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
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        layout.addWidget(self.title_label)
        
        # Value
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
        
        # Subtitle
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background: transparent;
            }
        """)
        layout.addWidget(self.subtitle_label)
        
        # Progress
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
        self.update_texts()
    
    def update_texts(self):
        """Update all localized texts"""
        self.title_label.setText(f"{self.icon} {t(self.title_key)}")
        self.subtitle_label.setText("🔄 Loading...")
    
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
    """Main application window - v0.3.5b
    
    Improvements:
    - Metrics ALWAYS show (even if limited)
    - Game wizard for easy adding
    - Better error handling
    """

    def __init__(self):
        super().__init__()
        
        # Initialize core systems
        self.config = get_config()
        self.logger = get_logger()
        
        # Set language
        lang = self.config.get_language()
        set_language(lang)
        self.logger.info(f"Language set to: {lang}")
        
        # Initialize monitoring with debug
        print("[DEBUG] Initializing SystemMonitor...")
        self.system_monitor = SystemMonitor()
        self.system_monitor._debug = True  # Enable debug
        
        # Test monitor immediately
        print("[DEBUG] Testing monitor...")
        test_data = self.system_monitor.get_all_data()
        print(f"[DEBUG] Test GPU: {test_data.get('gpu', {}).get('name')}")
        print(f"[DEBUG] Test CPU: {test_data.get('cpu', {}).get('name')}")
        print(f"[DEBUG] Test RAM: {test_data.get('ram', {}).get('total_gb')} GB")
        
        self.ai_engine = PartMartAIOptimizer()
        self.nav_buttons = []
        
        # Metric cards
        self.gpu_card = None
        self.ram_card = None
        self.cpu_card = None
        
        # Store games availability
        self.games_available = GAMES_AVAILABLE
        
        # Initialize Game Profiles
        if self.games_available:
            try:
                self.profile_manager = GameProfileManager(profiles_dir="config/profiles")
                self.game_detector = GameDetector(self.profile_manager)
                self.profile_applier = ProfileApplier()
                
                # Setup callbacks
                self.game_detector.on_game_started = self._on_game_started
                self.game_detector.on_game_stopped = self._on_game_stopped
                
                self.logger.info("Game Profiles system initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Game Profiles: {e}")
                self.games_available = False
        
        self._setup_ui()
        self._create_menu_bar()
        
        # Log startup
        self.logger.log_startup("0.3.5b")
        
        # Update timer
        update_interval = self.config.get_update_interval()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_data)
        self.update_timer.start(update_interval)
        
        # Initial update
        print("[DEBUG] Doing initial metrics update...")
        self._update_system_data()
        
        # Game detection timer
        if self.games_available:
            self.game_timer = QTimer()
            self.game_timer.timeout.connect(self._update_game_detection)
            self.game_timer.start(3000)

    def _setup_ui(self):
        self.setWindowTitle("PartMart Boost v0.3.5b")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
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
        
        # Content
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background: #0D0D0D;")
        
        self.page_home = self._create_home_page()
        self.page_gpu = self._create_placeholder("gpu_control")
        self.page_ram = self._create_placeholder("ram_tuner")
        
        pages = [self.page_home, self.page_gpu, self.page_ram]
        
        # Add Games page
        if self.games_available:
            self.page_games = GamesWidget(self.profile_manager, self.game_detector)
            # Add wizard button
            self._add_game_wizard_button(self.page_games)
            pages.append(self.page_games)
        else:
            self.page_games = self._create_placeholder("games")
            pages.append(self.page_games)
        
        for page in pages:
            self.content_stack.addWidget(page)
        
        main_layout.addWidget(self.content_stack, 1)
        central.setLayout(main_layout)

    def _add_game_wizard_button(self, games_widget):
        """Add 'Add Game' button to games widget"""
        # Find the header layout
        if hasattr(games_widget, 'layout'):
            layout = games_widget.layout()
            if layout and layout.count() > 0:
                header_layout = layout.itemAt(0)
                if isinstance(header_layout, QHBoxLayout) or hasattr(header_layout, 'layout'):
                    # Add wizard button
                    wizard_btn = QPushButton("➕ Добавить игру")
                    wizard_btn.setFixedHeight(40)
                    wizard_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    wizard_btn.setStyleSheet("""
                        QPushButton {
                            background: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 14px;
                            font-weight: 600;
                            padding: 0 20px;
                        }
                        QPushButton:hover {
                            background: #66BB6A;
                        }
                    """)
                    wizard_btn.clicked.connect(self._show_game_wizard)
                    
                    if hasattr(header_layout, 'addWidget'):
                        header_layout.addWidget(wizard_btn)

    def _show_game_wizard(self):
        """Show game wizard dialog"""
        wizard = GameWizard(self)
        if wizard.exec() == QDialog.DialogCode.Accepted:
            # Save profile
            import json
            from pathlib import Path
            
            data = wizard.get_data()
            
            # Create filename from game name
            filename = data['game_name'].lower().replace(' ', '_').replace(':', '') + '.json'
            filepath = Path('config/profiles') / filename
            
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Reload profiles
                if self.games_available and hasattr(self, 'profile_manager'):
                    self.profile_manager.reload()
                    
                    # Refresh games widget
                    if hasattr(self.page_games, '_reload_profiles'):
                        self.page_games._reload_profiles()
                
                QMessageBox.information(
                    self,
                    "✅ Успех!",
                    f"Игра '{data['game_name']}' добавлена!\n\n"
                    f"Теперь запусти игру и профиль применится автоматически!"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def _create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border-bottom: 1px solid #E63946;
            }
            QMenuBar::item:selected {
                background-color: #E63946;
            }
            QMenu {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #E63946;
            }
            QMenu::item:selected {
                background-color: #E63946;
            }
        """)
        
        settings_menu = menubar.addMenu(t('settings'))
        
        settings_action = QAction(t('preferences'), self)
        settings_action.triggered.connect(self._show_settings)
        settings_menu.addAction(settings_action)
        
        settings_menu.addSeparator()
        
        about_action = QAction(t('about'), self)
        about_action.triggered.connect(self._show_about)
        settings_menu.addAction(about_action)

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
        
        logo = QLabel("🐉 PartMart Boost v0.3.5b")
        logo.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #E63946;
            letter-spacing: 2px;
            background: transparent;
        """)
        layout.addWidget(logo)
        
        layout.addStretch()
        
        tabs = [
            ("home", "🏠", 0),
            ("gpu_control", "🎮", 1),
            ("ram_tuner", "🧠", 2),
            ("games", "🎮", 3),
        ]
        
        for key, icon, index in tabs:
            btn = QPushButton()
            btn.setProperty('nav_index', index)
            btn.setFixedHeight(48)
            btn.setFixedWidth(160)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._get_tab_style(index == 0))
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        self._update_nav_texts()
        
        header.setLayout(layout)
        return header

    def _update_nav_texts(self):
        tabs = [
            ("home", "🏠"),
            ("gpu_control", "🎮"),
            ("ram_tuner", "🧠"),
            ("games", "🎮"),
        ]
        for btn, (key, icon) in zip(self.nav_buttons, tabs):
            text = t(key) if key != 'games' else "Игры"
            btn.setText(f"{icon} {text}")

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
        self.logger.info(f"Switched to page: {index}")

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)
        
        # Metric cards
        grid = QGridLayout()
        grid.setSpacing(20)
        
        self.gpu_card = MetricCard("gpu_temperature", "🌡️")
        self.ram_card = MetricCard("ram_usage", "🧠")
        self.cpu_card = MetricCard("cpu_load", "💻")
        
        grid.addWidget(self.gpu_card, 0, 0)
        grid.addWidget(self.ram_card, 0, 1)
        grid.addWidget(self.cpu_card, 0, 2)
        
        layout.addLayout(grid)
        
        # System info card
        self.info_card = self._create_system_info_card()
        layout.addWidget(self.info_card)
        
        # Quick Boost button
        self.boost_btn = QPushButton()
        self.boost_btn.setText("⚡ Quick Boost")
        self.boost_btn.setFixedHeight(60)
        self.boost_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boost_btn.setStyleSheet("""
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
        self.boost_btn.clicked.connect(self._quick_boost)
        layout.addWidget(self.boost_btn)
        
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
        
        self.info_title = QLabel("📊 System Information")
        self.info_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        layout.addWidget(self.info_title)
        
        info = QHBoxLayout()
        info.setSpacing(32)
        
        self.gpu_info_label = QLabel("🌡️ GPU: Loading...")
        self.gpu_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        info.addWidget(self.gpu_info_label)
        
        self.cpu_info_label = QLabel("💻 CPU: Loading...")
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

    def _create_placeholder(self, title_key: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        
        title = QLabel()
        title.setProperty('text_key', title_key)
        title.setText(t(title_key) if title_key != 'games' else "Игры")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #E63946;
            }
        """)
        layout.addWidget(title)
        
        placeholder = QLabel("🕒 В разработке...")
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #A0A0A0;
            }
        """)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        page.setLayout(layout)
        return page

    def _quick_boost(self):
        try:
            self.logger.info("Quick Boost started")
            
            if sys.platform == 'win32':
                import psutil
                p = psutil.Process()
                p.nice(psutil.HIGH_PRIORITY_CLASS)
                self.logger.info("Process priority increased")
            
            QMessageBox.information(self, "✅ Успех", "Оптимизация применена!")
        
        except Exception as e:
            self.logger.log_error_with_trace("Quick Boost failed", e)
            QMessageBox.critical(self, "Ошибка", f"Не удалось: {e}")

    def _update_system_data(self):
        """Update ALL metrics - ALWAYS show something"""
        try:
            print("[DEBUG] Updating metrics...")
            
            # Get all data
            all_data = self.system_monitor.get_all_data()
            print(f"[DEBUG] Got data: GPU={all_data.get('gpu', {}).get('name')}, CPU={all_data.get('cpu', {}).get('name')}")
            
            # GPU - ALWAYS show name at minimum
            gpu_data = all_data.get('gpu', {})
            gpu_name = gpu_data.get('name', 'N/A')
            gpu_temp = gpu_data.get('temperature', 0)
            gpu_load = gpu_data.get('load', 0)
            gpu_clock = gpu_data.get('clock', 0)
            
            print(f"[DEBUG] GPU: name={gpu_name}, temp={gpu_temp}, load={gpu_load}")
            
            # Show temperature OR load OR just name
            if gpu_temp and gpu_temp > 0:
                self.gpu_card.set_value(f"{int(gpu_temp)}°C")
                self.gpu_card.set_progress(min(int(gpu_temp), 100), f"{int(gpu_temp)}°C")
            elif gpu_load and gpu_load > 0:
                self.gpu_card.set_value(f"{int(gpu_load)}%")
                self.gpu_card.set_progress(int(gpu_load), f"{int(gpu_load)}%")
            else:
                self.gpu_card.set_value("✅ OK")
                self.gpu_card.set_progress(0, "Ready")
            
            self.gpu_card.set_subtitle(gpu_name)
            self.gpu_info_label.setText(f"🌡️ GPU: {gpu_name}")
            
            # RAM - Should ALWAYS work
            ram_data = all_data.get('ram', {})
            ram_percent = ram_data.get('percent', 0)
            ram_used = ram_data.get('used_gb', 0)
            ram_total = ram_data.get('total_gb', 0)
            
            print(f"[DEBUG] RAM: {ram_percent}% ({ram_used}/{ram_total} GB)")
            
            if ram_total > 0:
                self.ram_card.set_value(f"{int(ram_percent)}%")
                self.ram_card.set_subtitle(f"{ram_used:.1f} / {ram_total:.1f} GB")
                self.ram_card.set_progress(int(ram_percent), f"{int(ram_percent)}%")
            else:
                self.ram_card.set_value("❌ N/A")
                self.ram_card.set_subtitle("No data")
            
            # CPU - Should ALWAYS work
            cpu_data = all_data.get('cpu', {})
            cpu_name = cpu_data.get('name', 'N/A')
            cpu_load = cpu_data.get('load', 0)
            cpu_cores = cpu_data.get('cores', 0)
            
            print(f"[DEBUG] CPU: name={cpu_name}, load={cpu_load}, cores={cpu_cores}")
            
            if cpu_load > 0:
                self.cpu_card.set_value(f"{int(cpu_load)}%")
                self.cpu_card.set_progress(int(cpu_load), f"{int(cpu_load)}%")
            else:
                self.cpu_card.set_value("✅ OK")
                self.cpu_card.set_progress(0, "Ready")
            
            self.cpu_card.set_subtitle(f"{cpu_cores} cores" if cpu_cores > 0 else cpu_name)
            self.cpu_info_label.setText(f"💻 CPU: {cpu_name}")
            
            print("[DEBUG] Metrics updated successfully")
        
        except Exception as e:
            print(f"[ERROR] Failed to update metrics: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error state
            self.gpu_card.set_value("❌ Error")
            self.ram_card.set_value("❌ Error")
            self.cpu_card.set_value("❌ Error")
    
    def _update_game_detection(self):
        if self.games_available and hasattr(self, 'game_detector'):
            try:
                self.game_detector.update()
            except Exception as e:
                self.logger.error(f"Game detection error: {e}")
    
    def _on_game_started(self, game):
        self.logger.info(f"Game started: {game.profile.game_name}")
        
        try:
            self.profile_applier.apply_profile(game.profile, game.pid)
            self.game_detector.mark_profile_applied(game.pid)
            
            QMessageBox.information(
                self,
                "🎮 Игра обнаружена!",
                f"{game.profile.game_name}\n\n✅ Профиль применён!"
            )
        except Exception as e:
            self.logger.error(f"Failed to apply profile: {e}")
    
    def _on_game_stopped(self, game):
        self.logger.info(f"Game stopped: {game.profile.game_name}")
        
        try:
            self.profile_applier.revert_optimizations()
        except Exception as e:
            self.logger.error(f"Failed to revert: {e}")

    def _show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_lang = self.config.get_language()
            set_language(new_lang)
            self.logger.info(f"Language changed to: {new_lang}")
            
            new_interval = self.config.get_update_interval()
            self.update_timer.setInterval(new_interval)

    def _show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "PartMart Boost v0.3.5b\n\n"
            "Оптимизация системы и игр\n\n"
            "PartMart Team 2026"
        )

    def closeEvent(self, event):
        self.logger.log_shutdown()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PartMartMainWindow()
    window.show()
    sys.exit(app.exec())
