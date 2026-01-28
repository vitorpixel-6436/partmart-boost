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
    QLineEdit, QCheckBox, QComboBox, QTextEdit, QDialog,
    QDialogButtonBox, QFormLayout, QFileDialog, QToolTip,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QCursor

from profiles.game_profiles import GameProfile, GameProfileManager
from profiles.game_detector import GameDetector, RunningGame


class ProfileEditorDialog(QDialog):
    """Simple and intuitive profile editor."""
    
    def __init__(self, profile: GameProfile = None, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.is_new = profile is None
        
        self.setWindowTitle("✏️ Редактор профиля" if not self.is_new else "➕ Новый профиль")
        self.setMinimumWidth(600)
        self.setStyleSheet("""
            QDialog {
                background: #1b2838;
            }
            QLabel {
                color: #c7d5e0;
                font-size: 13px;
            }
            QLineEdit, QSpinBox, QComboBox, QTextEdit {
                background: #2a475e;
                color: #ffffff;
                border: 2px solid #1b2838;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #66c0f4;
            }
            QCheckBox {
                color: #c7d5e0;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #2a475e;
                background: #1b2838;
            }
            QCheckBox::indicator:checked {
                background: #66c0f4;
                border-color: #66c0f4;
            }
            QPushButton {
                background: #2a475e;
                color: #66c0f4;
                border: 2px solid #66c0f4;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #66c0f4;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: #4a9dcf;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("🎮 Настройки игрового профиля")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #66c0f4;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Hint
        hint = QLabel(
            "💡 Подсказка: Укажите название игры и путь к .exe файлу. "
            "Остальные настройки опциональны."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("""
            color: #8f98a0;
            font-size: 12px;
            background: rgba(42, 71, 94, 0.3);
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
        """)
        layout.addWidget(hint)
        
        # Form
        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Game name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Cyberpunk 2077")
        self.name_input.setToolTip("Название игры для отображения в списке")
        if self.profile:
            self.name_input.setText(self.profile.game_name)
        form.addRow("🎯 Название игры:", self.name_input)
        
        # Executable with browse button
        exe_layout = QHBoxLayout()
        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("Cyberpunk2077.exe")
        self.exe_input.setToolTip("Имя исполняемого файла игры (только имя файла, не полный путь)")
        if self.profile:
            self.exe_input.setText(self.profile.executable)
        
        browse_btn = QPushButton("📁 Обзор")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.browse_executable)
        browse_btn.setToolTip("Выбрать .exe файл игры")
        
        exe_layout.addWidget(self.exe_input, 1)
        exe_layout.addWidget(browse_btn)
        form.addRow("📂 Исполняемый файл:", exe_layout)
        
        layout.addLayout(form)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #2a475e; margin: 10px 0;")
        layout.addWidget(sep)
        
        # GPU Settings section
        gpu_group = QGroupBox("⚡ Настройки GPU (опционально)")
        gpu_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #66c0f4;
                border: 2px solid #2a475e;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        gpu_layout = QFormLayout()
        gpu_layout.setSpacing(12)
        
        self.gpu_clock = QSpinBox()
        self.gpu_clock.setRange(0, 500)
        self.gpu_clock.setSuffix(" MHz")
        self.gpu_clock.setToolTip("Разгон ядра GPU (0 = не применять)")
        if self.profile and self.profile.gpu_clock_offset:
            self.gpu_clock.setValue(self.profile.gpu_clock_offset)
        gpu_layout.addRow("⚡ Разгон ядра:", self.gpu_clock)
        
        self.gpu_mem = QSpinBox()
        self.gpu_mem.setRange(0, 1000)
        self.gpu_mem.setSuffix(" MHz")
        self.gpu_mem.setToolTip("Разгон памяти GPU (0 = не применять)")
        if self.profile and self.profile.gpu_mem_offset:
            self.gpu_mem.setValue(self.profile.gpu_mem_offset)
        gpu_layout.addRow("💾 Разгон памяти:", self.gpu_mem)
        
        self.gpu_power = QSpinBox()
        self.gpu_power.setRange(0, 150)
        self.gpu_power.setSuffix("%")
        self.gpu_power.setToolTip("Лимит мощности GPU (0 = не применять)")
        if self.profile and self.profile.gpu_power_limit:
            self.gpu_power.setValue(self.profile.gpu_power_limit)
        gpu_layout.addRow("🔋 Лимит мощности:", self.gpu_power)
        
        gpu_group.setLayout(gpu_layout)
        layout.addWidget(gpu_group)
        
        # RAM Settings section
        ram_group = QGroupBox("🧠 Настройки RAM (опционально)")
        ram_group.setStyleSheet(gpu_group.styleSheet())
        
        ram_layout = QFormLayout()
        ram_layout.setSpacing(12)
        
        self.ram_cleanup = QCheckBox("Очистка RAM перед запуском")
        self.ram_cleanup.setToolTip("Освободить память перед запуском игры")
        if self.profile:
            self.ram_cleanup.setChecked(self.profile.ram_cleanup)
        ram_layout.addRow("", self.ram_cleanup)
        
        self.ram_priority = QComboBox()
        self.ram_priority.addItems(["normal", "high", "realtime"])
        self.ram_priority.setToolTip("Приоритет процесса игры")
        if self.profile and self.profile.ram_priority:
            index = self.ram_priority.findText(self.profile.ram_priority)
            if index >= 0:
                self.ram_priority.setCurrentIndex(index)
        ram_layout.addRow("🚀 Приоритет:", self.ram_priority)
        
        ram_group.setLayout(ram_layout)
        layout.addWidget(ram_group)
        
        # Notes
        notes_label = QLabel("📝 Заметки (опционально):")
        layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Например: Лучшие настройки для 1440p")
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setToolTip("Дополнительная информация о профиле")
        if self.profile and self.profile.notes:
            self.notes_input.setPlainText(self.profile.notes)
        layout.addWidget(self.notes_input)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                min-width: 100px;
            }
        """)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def browse_executable(self):
        """Browse for executable file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите исполняемый файл игры",
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        
        if file_path:
            # Extract just the filename
            import os
            filename = os.path.basename(file_path)
            self.exe_input.setText(filename)
    
    def get_profile_data(self) -> dict:
        """Get profile data from inputs."""
        return {
            'game_name': self.name_input.text().strip(),
            'executable': self.exe_input.text().strip(),
            'gpu_clock_offset': self.gpu_clock.value() or None,
            'gpu_mem_offset': self.gpu_mem.value() or None,
            'gpu_power_limit': self.gpu_power.value() or None,
            'ram_cleanup': self.ram_cleanup.isChecked(),
            'ram_priority': self.ram_priority.currentText(),
            'notes': self.notes_input.toPlainText().strip()
        }


class ProfileCard(QFrame):
    """Card widget for displaying a single game profile with improved UX."""
    
    edit_clicked = pyqtSignal(str)  # game_id
    delete_clicked = pyqtSignal(str)  # game_id
    test_clicked = pyqtSignal(str)  # game_id
    
    def __init__(self, profile: GameProfile, is_active: bool = False):
        super().__init__()
        self.profile = profile
        self.is_active = is_active
        self.hovered = False
        
        self.setup_ui()
        
        # Hover animation
        self.setMouseTracking(True)
    
    def enterEvent(self, event):
        """Mouse enter - show quick actions."""
        self.hovered = True
        if not self.is_active and hasattr(self, 'actions_widget'):
            self.actions_widget.show()
    
    def leaveEvent(self, event):
        """Mouse leave - hide quick actions."""
        self.hovered = False
        if hasattr(self, 'actions_widget'):
            self.actions_widget.hide()
    
    def setup_ui(self):
        """Setup card UI."""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        if self.is_active:
            self.setStyleSheet("""
                ProfileCard {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1b2838, stop:1 #2a475e);
                    border: 3px solid #66c0f4;
                    border-radius: 10px;
                    padding: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                ProfileCard {
                    background: #1b2838;
                    border: 2px solid #2a475e;
                    border-radius: 10px;
                    padding: 14px;
                }
                ProfileCard:hover {
                    border: 2px solid #66c0f4;
                    background: #1e3142;
                }
            """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        # Game icon + name
        name_label = QLabel(f"🎮 {self.profile.game_name}")
        name_label.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            color: #ffffff;
        """)
        name_label.setToolTip(f"Игра: {self.profile.game_name}")
        header.addWidget(name_label)
        
        if self.is_active:
            status = QLabel("▶️ АКТИВНА")
            status.setStyleSheet("""
                background: #90ee90;
                color: #000;
                padding: 5px 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            """)
            status.setToolTip("Профиль применён к запущенной игре")
            header.addWidget(status)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Executable
        exe_label = QLabel(f"📂 {self.profile.executable}")
        exe_label.setStyleSheet("color: #8f98a0; font-size: 13px;")
        exe_label.setToolTip(f"Исполняемый файл: {self.profile.executable}")
        layout.addWidget(exe_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #2a475e; margin: 4px 0;")
        layout.addWidget(line)
        
        # Stats grid with icons and tooltips
        stats = QGridLayout()
        stats.setSpacing(10)
        
        row = 0
        has_settings = False
        
        # GPU settings
        if self.profile.gpu_clock_offset:
            has_settings = True
            icon = QLabel("⚡")
            icon.setToolTip("Разгон ядра GPU")
            stats.addWidget(icon, row, 0)
            stats.addWidget(self._create_stat_label("GPU Core:"), row, 1)
            stats.addWidget(self._create_stat_value(f"+{self.profile.gpu_clock_offset} MHz"), row, 2)
            row += 1
        
        if self.profile.gpu_mem_offset:
            has_settings = True
            icon = QLabel("💾")
            icon.setToolTip("Разгон памяти GPU")
            stats.addWidget(icon, row, 0)
            stats.addWidget(self._create_stat_label("GPU Memory:"), row, 1)
            stats.addWidget(self._create_stat_value(f"+{self.profile.gpu_mem_offset} MHz"), row, 2)
            row += 1
        
        if self.profile.gpu_power_limit:
            has_settings = True
            icon = QLabel("🔋")
            icon.setToolTip("Лимит мощности GPU")
            stats.addWidget(icon, row, 0)
            stats.addWidget(self._create_stat_label("Power Limit:"), row, 1)
            stats.addWidget(self._create_stat_value(f"{self.profile.gpu_power_limit}%"), row, 2)
            row += 1
        
        # RAM settings
        if self.profile.ram_cleanup:
            has_settings = True
            icon = QLabel("🧹")
            icon.setToolTip("Очистка RAM")
            stats.addWidget(icon, row, 0)
            stats.addWidget(self._create_stat_label("RAM Cleanup:"), row, 1)
            stats.addWidget(self._create_stat_value("Включено"), row, 2)
            row += 1
        
        if self.profile.ram_priority:
            has_settings = True
            icon = QLabel("🚀")
            icon.setToolTip("Приоритет процесса")
            stats.addWidget(icon, row, 0)
            stats.addWidget(self._create_stat_label("Priority:"), row, 1)
            stats.addWidget(self._create_stat_value(self.profile.ram_priority.upper()), row, 2)
            row += 1
        
        if not has_settings:
            no_opts = QLabel("ℹ️ Без дополнительных настроек")
            no_opts.setStyleSheet("""
                color: #8f98a0;
                font-size: 12px;
                font-style: italic;
            """)
            no_opts.setToolTip("Этот профиль не содержит оптимизаций. Отредактируйте его для добавления настроек.")
            stats.addWidget(no_opts, 0, 0, 1, 3)
        
        layout.addLayout(stats)
        
        # Notes
        if self.profile.notes:
            notes_label = QLabel(f"💡 {self.profile.notes}")
            notes_label.setWordWrap(True)
            notes_label.setStyleSheet("""
                color: #8f98a0;
                font-size: 12px;
                font-style: italic;
                padding: 10px;
                background: rgba(42, 71, 94, 0.3);
                border-radius: 6px;
                margin-top: 4px;
            """)
            notes_label.setToolTip("Заметки к профилю")
            layout.addWidget(notes_label)
        
        # Quick actions (hidden by default, shown on hover)
        if not self.is_active:
            self.actions_widget = QWidget()
            actions = QHBoxLayout()
            actions.setSpacing(8)
            actions.setContentsMargins(0, 8, 0, 0)
            
            edit_btn = QPushButton("✏️ Изменить")
            edit_btn.setStyleSheet(self._get_action_btn_style())
            edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.profile.game_id))
            edit_btn.setToolTip("Редактировать профиль")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            actions.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️ Удалить")
            delete_btn.setStyleSheet(self._get_action_btn_style(danger=True))
            delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.profile.game_id))
            delete_btn.setToolTip("Удалить профиль")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            actions.addWidget(delete_btn)
            
            self.actions_widget.setLayout(actions)
            self.actions_widget.hide()  # Hidden by default
            layout.addWidget(self.actions_widget)
        
        self.setLayout(layout)
    
    def _get_action_btn_style(self, danger=False) -> str:
        """Get button style."""
        if danger:
            return """
                QPushButton {
                    background: #3d1f1f;
                    color: #ff6b6b;
                    border: 2px solid #ff6b6b;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #ff6b6b;
                    color: #ffffff;
                }
            """
        else:
            return """
                QPushButton {
                    background: #2a475e;
                    color: #66c0f4;
                    border: 2px solid #66c0f4;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #66c0f4;
                    color: #ffffff;
                }
            """
    
    def _create_stat_label(self, text: str) -> QLabel:
        """Create stat label."""
        label = QLabel(text)
        label.setStyleSheet("color: #8f98a0; font-size: 13px;")
        return label
    
    def _create_stat_value(self, text: str) -> QLabel:
        """Create stat value label."""
        label = QLabel(text)
        label.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-weight: bold;
        """)
        return label


class GamesWidget(QWidget):
    """Main games widget with improved UX."""
    
    def __init__(self, profile_manager: GameProfileManager, game_detector: GameDetector):
        super().__init__()
        
        self.profile_manager = profile_manager
        self.game_detector = game_detector
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(2000)  # Update every 2 seconds
        
        # Initial update
        self.update_status()
    
    def setup_ui(self):
        """Setup main UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QHBoxLayout()
        
        title = QLabel("🎮 Игровые профили")
        title.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
            color: #ffffff;
        """)
        title.setToolTip("Управление профилями оптимизации для игр")
        header.addWidget(title)
        
        header.addStretch()
        
        # Auto-optimize status
        self.auto_status = QLabel("⚡ Авто-оптимизация: Активна")
        self.auto_status.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #90ee90, stop:1 #7dce7d);
            color: #000;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
        """)
        self.auto_status.setToolTip(
            "Профили применяются автоматически при запуске игры!\n"
            "Просто запустите игру - всё остальное сделаем мы."
        )
        header.addWidget(self.auto_status)
        
        layout.addLayout(header)
        
        # Description with better formatting
        desc = QLabel(
            "✨ <b>Как это работает:</b><br>"
            "1️⃣ Создайте профиль для игры<br>"
            "2️⃣ Запустите игру<br>"
            "3️⃣ Профиль применится автоматически!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            color: #c7d5e0;
            font-size: 14px;
            background: rgba(42, 71, 94, 0.4);
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid #66c0f4;
        """)
        layout.addWidget(desc)
        
        # Active games section
        self.active_group = QGroupBox("▶️ Активные игры")
        self.active_group.setStyleSheet("""
            QGroupBox {
                font-size: 19px;
                font-weight: bold;
                color: #66c0f4;
                border: 3px solid #66c0f4;
                border-radius: 10px;
                margin-top: 14px;
                padding-top: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        self.active_layout = QVBoxLayout()
        self.active_layout.setSpacing(14)
        
        # Placeholder
        self.no_games_label = QLabel(
            "🎯 <b>Нет активных игр</b><br>"
            "Запустите игру из списка ниже, и профиль применится автоматически!"
        )
        self.no_games_label.setWordWrap(True)
        self.no_games_label.setStyleSheet("""
            color: #8f98a0;
            font-size: 14px;
            padding: 30px;
            background: rgba(42, 71, 94, 0.3);
            border-radius: 8px;
        """)
        self.no_games_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_layout.addWidget(self.no_games_label)
        
        self.active_group.setLayout(self.active_layout)
        layout.addWidget(self.active_group)
        
        # All profiles section with better header
        profiles_header = QHBoxLayout()
        
        profiles_label = QLabel("📚 Все профили")
        profiles_label.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #ffffff;
            margin-top: 12px;
        """)
        profiles_header.addWidget(profiles_label)
        
        # Profile count
        self.profile_count_label = QLabel()
        self.profile_count_label.setStyleSheet("""
            font-size: 13px;
            color: #8f98a0;
            margin-top: 14px;
        """)
        profiles_header.addWidget(self.profile_count_label)
        
        profiles_header.addStretch()
        layout.addLayout(profiles_header)
        
        # Scrollable profiles list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1b2838;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #66c0f4;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #85d0ff;
            }
        """)
        
        scroll_widget = QWidget()
        self.profiles_layout = QVBoxLayout()
        self.profiles_layout.setSpacing(14)
        
        # Load all profiles
        self.load_profiles()
        
        scroll_widget.setLayout(self.profiles_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)  # Stretch factor
        
        # Add new profile button with better styling
        add_btn = QPushButton("➕ Создать новый профиль")
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #66c0f4, stop:1 #5ab8e8);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #85d0ff, stop:1 #6cc5f2);
            }
            QPushButton:pressed {
                background: #4a9dcf;
            }
        """)
        add_btn.clicked.connect(self.create_new_profile)
        add_btn.setToolTip("Создать профиль для новой игры")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
        
        if not profiles:
            # Empty state
            empty = QLabel(
                "📭 <b>Пока нет профилей</b><br>"
                "Создайте первый профиль, нажав кнопку ниже!"
            )
            empty.setWordWrap(True)
            empty.setStyleSheet("""
                color: #8f98a0;
                font-size: 14px;
                padding: 40px;
                background: rgba(42, 71, 94, 0.3);
                border-radius: 8px;
            """)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.profiles_layout.addWidget(empty)
        else:
            for profile in profiles:
                card = ProfileCard(profile, is_active=False)
                card.edit_clicked.connect(self.edit_profile)
                card.delete_clicked.connect(self.delete_profile)
                self.profiles_layout.addWidget(card)
        
        # Update count
        count = len(profiles)
        self.profile_count_label.setText(f"({count} {self._plural(count, 'профиль', 'профиля', 'профилей')})")
        
        # Stretch at end
        self.profiles_layout.addStretch()
    
    def _plural(self, n: int, one: str, few: str, many: str) -> str:
        """Russian plural forms."""
        if n % 10 == 1 and n % 100 != 11:
            return one
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return few
        else:
            return many
    
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
            dialog = ProfileEditorDialog(profile, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Update profile
                data = dialog.get_profile_data()
                
                if not data['game_name'] or not data['executable']:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        "Название игры и исполняемый файл обязательны!"
                    )
                    return
                
                # Update existing profile
                updated_profile = GameProfile(
                    game_id=profile.game_id,
                    **data
                )
                self.profile_manager.save_profile(updated_profile)
                
                # Reload UI
                self.load_profiles()
                
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Профиль '{data['game_name']}' обновлён!"
                )
    
    def delete_profile(self, game_id: str):
        """Delete profile with confirmation."""
        profile = self.profile_manager.get_profile(game_id)
        if not profile:
            return
        
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить профиль '{profile.game_name}'?\n\n"
            f"Это действие необратимо.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profile_manager.delete_profile(game_id)
            self.load_profiles()
            
            QMessageBox.information(
                self,
                "Успех",
                f"Профиль '{profile.game_name}' удалён."
            )
    
    def create_new_profile(self):
        """Create new profile."""
        dialog = ProfileEditorDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_profile_data()
            
            if not data['game_name'] or not data['executable']:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Название игры и исполняемый файл обязательны!"
                )
                return
            
            # Create new profile
            import time
            profile = GameProfile(
                game_id=f"game_{int(time.time())}",
                **data
            )
            self.profile_manager.save_profile(profile)
            
            # Reload UI
            self.load_profiles()
            
            QMessageBox.information(
                self,
                "Успех",
                f"Профиль '{data['game_name']}' создан!\n\n"
                f"Теперь просто запустите игру, и оптимизации применятся автоматически."
            )


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
    widget.setMinimumSize(900, 700)
    widget.show()
    
    sys.exit(app.exec())
