"""Games Widget - Game profiles management UI

Version: 0.3.5b
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from ui.add_game_dialog import AddGameDialog


class GameCard(QFrame):
    """Card for displaying game status"""
    
    def __init__(self, game_name: str, is_running: bool = False, parent=None):
        super().__init__(parent)
        self.game_name = game_name
        self.is_running = is_running
        
        self.setFixedHeight(100)
        self.setAutoFillBackground(True)
        self._update_style()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Game info
        info_layout = QVBoxLayout()
        
        self.name_label = QLabel(game_name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        info_layout.addWidget(self.name_label)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        self._update_status()
        info_layout.addWidget(self.status_label)
        
        layout.addLayout(info_layout, 1)
        
        # Status indicator
        self.indicator = QLabel("●")
        self.indicator.setStyleSheet("""
            QLabel {
                font-size: 24px;
                background: transparent;
            }
        """)
        self.indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_indicator()
        layout.addWidget(self.indicator)
        
        self.setLayout(layout)
    
    def _update_style(self):
        if self.is_running:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1A2A1A;
                    border-left: 4px solid #4CAF50;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1A1A1A;
                    border-left: 4px solid #666666;
                    border-radius: 12px;
                }
            """)
    
    def _update_status(self):
        if self.is_running:
            self.status_label.setText("✅ Running - Profile applied")
        else:
            self.status_label.setText("⏸️ Ready - Waiting for game")
    
    def _update_indicator(self):
        if self.is_running:
            self.indicator.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    color: #4CAF50;
                    background: transparent;
                }
            """)
        else:
            self.indicator.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    color: #666666;
                    background: transparent;
                }
            """)
    
    def set_running(self, is_running: bool):
        self.is_running = is_running
        self._update_style()
        self._update_status()
        self._update_indicator()


class GamesWidget(QWidget):
    """Games management widget"""
    
    def __init__(self, profile_manager, game_detector, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.game_detector = game_detector
        self.game_cards = {}
        
        self._setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_games)
        self.update_timer.start(1000)  # Update every second
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(24)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("🎮 Игровые профили")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                color: #E63946;
            }
        """)
        header.addWidget(title)
        
        header.addStretch()
        
        # Add game button
        add_btn = QPushButton("➕ Добавить игру")
        add_btn.setFixedHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E63946, stop:1 #FF4757);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF4757, stop:1 #E63946);
            }
        """)
        add_btn.clicked.connect(self._add_game)
        header.addWidget(add_btn)
        
        # Reload button
        reload_btn = QPushButton("🔄 Обновить")
        reload_btn.setFixedHeight(40)
        reload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reload_btn.setStyleSheet("""
            QPushButton {
                background: #666666;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #777777;
            }
        """)
        reload_btn.clicked.connect(self._reload_profiles)
        header.addWidget(reload_btn)
        
        layout.addLayout(header)
        
        # Info
        info = QLabel()
        profiles_count = len(self.profile_manager.get_all_profiles())
        info.setText(f"📊 Загружено профилей: {profiles_count}")
        info.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #A0A0A0;
            }
        """)
        layout.addWidget(info)
        self.info_label = info
        
        # Quick help card
        help_card = QFrame()
        help_card.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-left: 4px solid #E63946;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        help_layout = QVBoxLayout()
        
        help_title = QLabel("💡 Как добавить игру:")
        help_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #FFFFFF;
                background: transparent;
            }
        """)
        help_layout.addWidget(help_title)
        
        help_text = QLabel(
            "1️⃣ Нажмите '➕ Добавить игру'\n"
            "2️⃣ Введите название и имя .exe файла\n"
            "3️⃣ Нажмите '✅ Добавить'\n"
            "4️⃣ Перезапустите PartMart Boost"
        )
        help_text.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                background: transparent;
            }
        """)
        help_layout.addWidget(help_text)
        help_card.setLayout(help_layout)
        layout.addWidget(help_card)
        
        # Scroll area for game cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Container for cards
        container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(12)
        
        # Add cards for each profile
        for profile in self.profile_manager.get_all_profiles():
            card = GameCard(profile.game_name)
            self.game_cards[profile.game_name] = card
            self.cards_layout.addWidget(card)
        
        # If no profiles
        if not self.game_cards:
            empty_label = QLabel(
                "📁 Нет загруженных профилей\n\n"
                "Нажмите '➕ Добавить игру' чтобы начать!"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #666666;
                    padding: 60px;
                }
            """)
            self.cards_layout.addWidget(empty_label)
        
        self.cards_layout.addStretch()
        container.setLayout(self.cards_layout)
        scroll.setWidget(container)
        
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def _add_game(self):
        """Show add game dialog"""
        dialog = AddGameDialog(self)
        if dialog.exec():
            # Show success and reload
            QMessageBox.information(
                self,
                "Успех!",
                "✅ Игра добавлена!\n\n"
                "🔄 Нажмите 'Обновить' чтобы увидеть её в списке.\n"
                "Либо перезапустите PartMart Boost."
            )
    
    def _update_games(self):
        """Update running games status"""
        running_games = {game.profile.game_name for game in self.game_detector.get_detected_games()}
        
        for game_name, card in self.game_cards.items():
            card.set_running(game_name in running_games)
    
    def _reload_profiles(self):
        """Reload profiles from disk"""
        self.profile_manager.reload()
        
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Recreate cards
        self.game_cards.clear()
        for profile in self.profile_manager.get_all_profiles():
            card = GameCard(profile.game_name)
            self.game_cards[profile.game_name] = card
            self.cards_layout.addWidget(card)
        
        if not self.game_cards:
            empty_label = QLabel(
                "📁 Нет загруженных профилей\n\n"
                "Нажмите '➕ Добавить игру' чтобы начать!"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #666666;
                    padding: 60px;
                }
            """)
            self.cards_layout.addWidget(empty_label)
        
        self.cards_layout.addStretch()
        
        # Update info
        profiles_count = len(self.profile_manager.get_all_profiles())
        self.info_label.setText(f"📊 Загружено профилей: {profiles_count}")
        
        QMessageBox.information(
            self,
            "Успех!",
            f"✅ Профили обновлены!\n\n"
            f"Загружено: {profiles_count}"
        )


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Mock objects for testing
    class MockProfileManager:
        def get_all_profiles(self):
            return []
        def reload(self):
            pass
    
    class MockGameDetector:
        def get_detected_games(self):
            return []
    
    widget = GamesWidget(MockProfileManager(), MockGameDetector())
    widget.setStyleSheet("background: #0D0D0D;")
    widget.resize(800, 600)
    widget.show()
    
    sys.exit(app.exec())
