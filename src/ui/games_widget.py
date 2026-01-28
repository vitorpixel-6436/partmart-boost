#!/usr/bin/env python3
"""
Games Widget - UI for game profiles management.

Shows:
- Active games and applied profiles
- List of all available profiles
- Profile editor
- Auto-optimization status

Author: PartMart Team
Version: 0.4.0-alpha
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGroupBox, QGridLayout, QSpinBox,
    QLineEdit, QCheckBox, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from profiles.game_profiles import GameProfile, GameProfileManager
from profiles.game_detector import GameDetector, RunningGame


class ProfileCard(QFrame):
    """Card widget for displaying a single game profile."""
    
    edit_clicked = pyqtSignal(str)  # game_id
    
    def __init__(self, profile: GameProfile, is_active: bool = False):
        super().__init__()
        self.profile = profile
        self.is_active = is_active
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup card UI."""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        if self.is_active:
            self.setStyleSheet("""
                ProfileCard {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1b2838, stop:1 #2a475e);
                    border: 2px solid #66c0f4;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                ProfileCard {
                    background: #1b2838;
                    border: 1px solid #2a475e;
                    border-radius: 8px;
                    padding: 12px;
                }
                ProfileCard:hover {
                    border: 1px solid #66c0f4;
                }
            """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        # Game icon + name
        name_label = QLabel(f"🎮 {self.profile.game_name}")
        name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #ffffff;
        """)
        header.addWidget(name_label)
        
        if self.is_active:
            status = QLabel("▶️ ACTIVE")
            status.setStyleSheet("""
                background: #90ee90;
                color: #000;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            """)
            header.addWidget(status)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Executable
        exe_label = QLabel(f"📁 {self.profile.executable}")
        exe_label.setStyleSheet("color: #8f98a0; font-size: 12px;")
        layout.addWidget(exe_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #2a475e;")
        layout.addWidget(line)
        
        # Stats grid
        stats = QGridLayout()
        stats.setSpacing(8)
        
        row = 0
        
        # GPU settings
        if self.profile.gpu_clock_offset:
            stats.addWidget(self._create_stat_label("⚡ GPU Core:"), row, 0)
            stats.addWidget(self._create_stat_value(f"+{self.profile.gpu_clock_offset} MHz"), row, 1)
            row += 1
        
        if self.profile.gpu_mem_offset:
            stats.addWidget(self._create_stat_label("💾 GPU Memory:"), row, 0)
            stats.addWidget(self._create_stat_value(f"+{self.profile.gpu_mem_offset} MHz"), row, 1)
            row += 1
        
        if self.profile.gpu_power_limit:
            stats.addWidget(self._create_stat_label("🔋 Power Limit:"), row, 0)
            stats.addWidget(self._create_stat_value(f"{self.profile.gpu_power_limit}%"), row, 1)
            row += 1
        
        # RAM settings
        if self.profile.ram_cleanup:
            stats.addWidget(self._create_stat_label("🧹 RAM Cleanup:"), row, 0)
            stats.addWidget(self._create_stat_value("Enabled"), row, 1)
            row += 1
        
        if self.profile.ram_priority:
            stats.addWidget(self._create_stat_label("🚀 Priority:"), row, 0)
            stats.addWidget(self._create_stat_value(self.profile.ram_priority.upper()), row, 1)
            row += 1
        
        layout.addLayout(stats)
        
        # Notes
        if self.profile.notes:
            notes_label = QLabel(f"💡 {self.profile.notes}")
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("""
                color: #8f98a0;
                font-size: 11px;
                font-style: italic;
                padding: 8px;
                background: rgba(42, 71, 94, 0.3);
                border-radius: 4px;
            """)
            layout.addWidget(notes_label)
        
        # Edit button
        if not self.is_active:
            edit_btn = QPushButton("⚙️ Edit Profile")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2a475e;
                    color: #66c0f4;
                    border: 1px solid #66c0f4;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #66c0f4;
                    color: #ffffff;
                }
            """)
            edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.profile.game_id))
            layout.addWidget(edit_btn)
        
        self.setLayout(layout)
    
    def _create_stat_label(self, text: str) -> QLabel:
        """Create stat label."""
        label = QLabel(text)
        label.setStyleSheet("color: #8f98a0; font-size: 12px;")
        return label
    
    def _create_stat_value(self, text: str) -> QLabel:
        """Create stat value label."""
        label = QLabel(text)
        label.setStyleSheet("""
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
        """)
        return label


class GamesWidget(QWidget):
    """Main games widget with profile management."""
    
    def __init__(self, profile_manager: GameProfileManager, game_detector: GameDetector):
        super().__init__()
        
        self.profile_manager = profile_manager
        self.game_detector = game_detector
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
    
    def setup_ui(self):
        """Setup main UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("🎮 Game Profiles")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
        """)
        header.addWidget(title)
        
        header.addStretch()
        
        # Auto-optimize status
        self.auto_status = QLabel("⚡ Auto-Optimize: Active")
        self.auto_status.setStyleSheet("""
            background: #90ee90;
            color: #000;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 14px;
        """)
        header.addWidget(self.auto_status)
        
        layout.addLayout(header)
        
        # Description
        desc = QLabel(
            "Автоматическая оптимизация для поддерживаемых игр. "
            "Запусти игру — профиль применится автоматически!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8f98a0; font-size: 14px;")
        layout.addWidget(desc)
        
        # Active games section
        self.active_group = QGroupBox("▶️ Активные игры")
        self.active_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #66c0f4;
                border: 2px solid #66c0f4;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        self.active_layout = QVBoxLayout()
        self.active_layout.setSpacing(12)
        
        # Placeholder
        self.no_games_label = QLabel("🎯 Нет активных игр. Запусти игру из списка ниже!")
        self.no_games_label.setStyleSheet("""
            color: #8f98a0;
            font-size: 14px;
            padding: 20px;
            background: rgba(42, 71, 94, 0.3);
            border-radius: 6px;
        """)
        self.no_games_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_layout.addWidget(self.no_games_label)
        
        self.active_group.setLayout(self.active_layout)
        layout.addWidget(self.active_group)
        
        # All profiles section
        profiles_label = QLabel("📚 Все профили")
        profiles_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            margin-top: 10px;
        """)
        layout.addWidget(profiles_label)
        
        # Scrollable profiles list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        self.profiles_layout = QVBoxLayout()
        self.profiles_layout.setSpacing(12)
        
        # Load all profiles
        self.load_profiles()
        
        scroll_widget.setLayout(self.profiles_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Stretch factor
        
        # Add new profile button
        add_btn = QPushButton("➕ Создать новый профиль")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #66c0f4;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #85d0ff;
            }
        """)
        add_btn.clicked.connect(self.create_new_profile)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)
    
    def load_profiles(self):
        """Load all profiles into UI."""
        # Clear existing
        while self.profiles_layout.count():
            item = self.profiles_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add profile cards
        profiles = self.profile_manager.list_profiles()
        
        for profile in profiles:
            card = ProfileCard(profile, is_active=False)
            card.edit_clicked.connect(self.edit_profile)
            self.profiles_layout.addWidget(card)
        
        # Stretch at end
        self.profiles_layout.addStretch()
    
    def update_status(self):
        """Update active games status."""
        # Get running games
        running = self.game_detector.running_games
        
        # Clear active section
        while self.active_layout.count():
            item = self.active_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if running:
            # Hide placeholder
            self.no_games_label.hide()
            
            # Show active games
            for game in running.values():
                card = ProfileCard(game.profile, is_active=True)
                self.active_layout.addWidget(card)
        else:
            # Show placeholder
            self.active_layout.addWidget(self.no_games_label)
            self.no_games_label.show()
    
    def edit_profile(self, game_id: str):
        """Open profile editor."""
        profile = self.profile_manager.get_profile(game_id)
        if profile:
            # TODO: Open profile editor dialog
            print(f"[UI] Edit profile: {profile.game_name}")
    
    def create_new_profile(self):
        """Create new profile."""
        # TODO: Open profile creator dialog
        print("[UI] Create new profile")


# ========== Testing ==========

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Setup managers
    profile_manager = GameProfileManager(profiles_dir="config/profiles")
    game_detector = GameDetector(profile_manager)
    
    # Create widget
    widget = GamesWidget(profile_manager, game_detector)
    widget.setStyleSheet("""
        QWidget {
            background: #171a21;
            color: #c7d5e0;
        }
    """)
    widget.setMinimumSize(800, 600)
    widget.show()
    
    sys.exit(app.exec())
