"""Main window with full localization and modern UI"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QApplication, QProgressBar, 
    QGridLayout, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QTimer
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
try:
    from profiles.game_profiles import GameProfileManager
    from profiles.game_detector import GameDetector
    from profiles.optimization_applier import ProfileApplier
    from ui.games_widget import GamesWidget
    GAMES_AVAILABLE = True
except ImportError as e:
    print(f"Game Profiles not available: {e}")
    GAMES_AVAILABLE = False

class MetricCard(QFrame):
    """Metric card with localized labels"""
    
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
        self.subtitle_label.setText(t('loading'))
    
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
    """Main application window with full localization"""

    def __init__(self):
        super().__init__()
        
        # Initialize core systems
        self.config = get_config()
        self.logger = get_logger()
        
        # Set language from config
        lang = self.config.get_language()
        set_language(lang)
        self.logger.info(f"Language set to: {lang}")
        
        # Initialize monitoring
        self.system_monitor = SystemMonitor()
        self.ai_engine = PartMartAIOptimizer()
        self.nav_buttons = []
        
        # Metric cards
        self.gpu_card = None
        self.ram_card = None
        self.cpu_card = None
        
        # Initialize Game Profiles system
        if GAMES_AVAILABLE:
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
                GAMES_AVAILABLE = False
        
        self._setup_ui()
        self._create_menu_bar()
        
        # Log startup
        self.logger.log_startup("0.4.0-alpha")
        
        # Auto-update timer
        update_interval = self.config.get_update_interval()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_data)
        self.update_timer.start(update_interval)
        self._update_system_data()
        
        # Game detection timer
        if GAMES_AVAILABLE:
            self.game_timer = QTimer()
            self.game_timer.timeout.connect(self._update_game_detection)
            self.game_timer.start(3000)  # Check every 3 seconds

    def _setup_ui(self):
        self.setWindowTitle(t('window_title', version='0.4.0'))
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
        self.page_gpu = self._create_gpu_page()
        self.page_ram = self._create_placeholder("ram_tuner")
        
        pages = [self.page_home, self.page_gpu, self.page_ram]
        
        # Add Games page if available
        if GAMES_AVAILABLE:
            self.page_games = GamesWidget(self.profile_manager, self.game_detector)
            pages.append(self.page_games)
        else:
            self.page_games = self._create_placeholder("games")
            pages.append(self.page_games)
        
        for page in pages:
            self.content_stack.addWidget(page)
        
        main_layout.addWidget(self.content_stack, 1)
        central.setLayout(main_layout)

    def _create_menu_bar(self):
        """Create menu bar with settings"""
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
        
        # Settings menu
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
            ("home", "🏠", 0),
            ("gpu_control", "🎮", 1),
            ("ram_tuner", "🧠", 2),
            ("games", "🎮", 3),  # NEW!
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
        """Update navigation button texts"""
        tabs = [
            ("home", "🏠"),
            ("gpu_control", "🎮"),
            ("ram_tuner", "🧠"),
            ("games", "🎮"),  # NEW!
        ]
        for btn, (key, icon) in zip(self.nav_buttons, tabs):
            # For "games" key, use fallback if translation missing
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
        
        # Action cards
        actions = QHBoxLayout()
        actions.setSpacing(20)
        
        self.gpu_action = self._create_action_card("gpu_control", "gpu_optimization", lambda: self._switch_page(1))
        self.ram_action = self._create_action_card("ram_tuner", "xmp_and_cleanup", lambda: self._switch_page(2))
        
        # Add Games action card if available
        if GAMES_AVAILABLE:
            self.games_action = self._create_action_card(
                "games", 
                "Auto-optimize games",
                lambda: self._switch_page(3)
            )
            actions.addWidget(self.games_action)
        
        actions.addWidget(self.gpu_action)
        actions.addWidget(self.ram_action)
        
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
        
        self.info_title = QLabel()
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
        
        self.gpu_info_label = QLabel()
        self.gpu_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        info.addWidget(self.gpu_info_label)
        
        self.cpu_info_label = QLabel()
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

    def _create_action_card(self, title_key: str, desc_key: str, callback) -> QFrame:
        card = QFrame()
        card.setFixedHeight(140)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setAutoFillBackground(True)
        card.setProperty('title_key', title_key)
        card.setProperty('desc_key', desc_key)
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
        
        title_label = QLabel()
        title_label.setProperty('title_key', title_key)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 700;
                color: #E63946;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        desc_label = QLabel()
        desc_label.setProperty('desc_key', desc_key)
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
        
        # Store labels for updating
        card.title_label = title_label
        card.desc_label = desc_label
        
        # Set text
        title_text = t(title_key) if title_key != 'games' else "Игры"
        desc_text = desc_key  # Use as-is for now
        title_label.setText(title_text)
        desc_label.setText(desc_text)
        
        return card

    def _create_gpu_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        
        title = QLabel()
        title.setProperty('text_key', 'gpu_control')
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #E63946;
            }
        """)
        layout.addWidget(title)
        
        placeholder = QLabel()
        placeholder.setProperty('text_key', 'coming_soon')
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #A0A0A0;
            }
        """)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        page.setLayout(layout)
        page.title_label = title
        page.placeholder_label = placeholder
        return page

    def _create_placeholder(self, title_key: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        
        title = QLabel()
        title.setProperty('text_key', title_key)
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #E63946;
            }
        """)
        layout.addWidget(title)
        
        placeholder = QLabel()
        placeholder.setProperty('text_key', 'coming_soon')
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #A0A0A0;
            }
        """)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        page.setLayout(layout)
        page.title_label = title
        page.placeholder_label = placeholder
        
        # Set text for games page
        if title_key == 'games':
            title.setText("Игры")
        
        return page

    def _quick_boost(self):
        """Quick optimization with safety checks"""
        reply = QMessageBox.question(
            self,
            t('quick_boost'),
            t('quick_boost_confirm'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.logger.info("Quick Boost started")
                
                # Simple safe optimization
                if sys.platform == 'win32':
                    # Increase process priority
                    import psutil
                    p = psutil.Process()
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                    self.logger.info("Process priority increased")
                
                self.logger.log_optimization("quick_boost", True)
                QMessageBox.information(self, t('success'), t('optimization_complete'))
            
            except Exception as e:
                self.logger.log_error_with_trace("Quick Boost failed", e)
                QMessageBox.critical(self, t('error'), t('optimization_failed'))

    def _update_system_data(self):
        """Update system metrics"""
        try:
            # GPU
            gpu_data = self.system_monitor.get_gpu_data()
            if gpu_data:
                temp = gpu_data.get('temperature', 0)
                load = gpu_data.get('load', 0)
                self.gpu_card.set_value(f"{temp}°C")
                self.gpu_card.set_subtitle(f"{gpu_data.get('name', 'N/A')}")
                self.gpu_card.set_progress(int(temp), f"{temp}°C")
                
                self.gpu_info_label.setText(
                    f"GPU: {gpu_data.get('name', 'N/A')} | "
                    f"{t('clock')}: {gpu_data.get('clock', 0)} MHz"
                )
            
            # RAM
            ram_data = self.system_monitor.get_ram_data()
            if ram_data:
                used = ram_data.get('used_gb', 0)
                total = ram_data.get('total_gb', 0)
                percent = ram_data.get('percent', 0)
                self.ram_card.set_value(f"{percent}%")
                self.ram_card.set_subtitle(f"{used:.1f} / {total:.1f} GB")
                self.ram_card.set_progress(int(percent), f"{percent}%")
            
            # CPU
            cpu_data = self.system_monitor.get_cpu_data()
            if cpu_data:
                load = cpu_data.get('load', 0)
                cores = cpu_data.get('cores', 0)
                self.cpu_card.set_value(f"{load}%")
                self.cpu_card.set_subtitle(t('cpu_cores', count=cores))
                self.cpu_card.set_progress(int(load), f"{load}%")
                
                self.cpu_info_label.setText(
                    f"CPU: {cpu_data.get('name', 'N/A')} | "
                    f"{t('load')}: {load}%"
                )
            
            # Update info card title
            self.info_title.setText(f"📊 {t('system_metrics')}")
        
        except Exception as e:
            self.logger.error(f"Failed to update system data: {e}")
    
    def _update_game_detection(self):
        """Update game detection"""
        if GAMES_AVAILABLE and hasattr(self, 'game_detector'):
            try:
                self.game_detector.update()
            except Exception as e:
                self.logger.error(f"Game detection error: {e}")
    
    def _on_game_started(self, game):
        """Called when game starts"""
        self.logger.info(f"Game started: {game.profile.game_name}")
        
        try:
            # Apply profile
            self.profile_applier.apply_profile(game.profile, game.pid)
            self.game_detector.mark_profile_applied(game.pid)
            
            # Show notification
            QMessageBox.information(
                self,
                "Игра обнаружена",
                f"🎮 {game.profile.game_name}\n\n"
                f"Профиль оптимизации применён!"
            )
        except Exception as e:
            self.logger.error(f"Failed to apply game profile: {e}")
    
    def _on_game_stopped(self, game):
        """Called when game stops"""
        self.logger.info(f"Game stopped: {game.profile.game_name}")
        
        try:
            # Revert optimizations
            self.profile_applier.revert_optimizations()
        except Exception as e:
            self.logger.error(f"Failed to revert optimizations: {e}")

    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload language
            new_lang = self.config.get_language()
            set_language(new_lang)
            self.logger.info(f"Language changed to: {new_lang}")
            
            # Update interval
            new_interval = self.config.get_update_interval()
            self.update_timer.setInterval(new_interval)
            self.logger.info(f"Update interval changed to: {new_interval}ms")
            
            # Refresh UI texts
            self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        """Refresh all UI texts with new language"""
        self.setWindowTitle(t('window_title', version='0.4.0'))
        self._update_nav_texts()
        
        # Update cards
        self.gpu_card.update_texts()
        self.ram_card.update_texts()
        self.cpu_card.update_texts()
        
        # Update buttons
        self.boost_btn.setText(f"⚡ {t('quick_boost')}")
        
        # Update action cards
        cards = [self.gpu_action, self.ram_action]
        if GAMES_AVAILABLE and hasattr(self, 'games_action'):
            cards.append(self.games_action)
        
        for card in cards:
            title_key = card.property('title_key')
            desc_key = card.property('desc_key')
            title_text = t(title_key) if title_key != 'games' else "Игры"
            card.title_label.setText(title_text)
            card.desc_label.setText(desc_key)
        
        # Update placeholder pages
        for page in [self.page_gpu, self.page_ram]:
            if hasattr(page, 'title_label'):
                text_key = page.title_label.property('text_key')
                if text_key:
                    page.title_label.setText(t(text_key))
            if hasattr(page, 'placeholder_label'):
                text_key = page.placeholder_label.property('text_key')
                if text_key:
                    page.placeholder_label.setText(t(text_key))

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            t('about'),
            t('about_text', version='0.4.0')
        )

    def closeEvent(self, event):
        """Handle window close"""
        self.logger.log_shutdown()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PartMartMainWindow()
    window.show()
    sys.exit(app.exec())
