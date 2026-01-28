"""Simple dialog for adding games

Version: 0.3.5b
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import Qt
import json
from pathlib import Path


class AddGameDialog(QDialog):
    """Simple dialog for adding game profiles"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("➕ Добавить игру")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0D0D0D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 2px solid #252525;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #E63946;
            }
            QPushButton {
                background-color: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #FF4757;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("🎮 Добавить новую игру")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #E63946;
                margin-bottom: 16px;
            }
        """)
        layout.addWidget(title)
        
        # Instruction
        instruction = QLabel(
            "📝 Заполните информацию об игре.\n"
            "Все поля обязательны для заполнения."
        )
        instruction.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #A0A0A0;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(instruction)
        
        # Game name
        layout.addWidget(QLabel("Название игры:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Escape From Tarkov")
        layout.addWidget(self.name_input)
        
        # EXE name with browse button
        layout.addWidget(QLabel("Имя .exe файла:"))
        
        exe_layout = QHBoxLayout()
        self.exe_input = QLineEdit()
        self.exe_input.setPlaceholderText("Например: EscapeFromTarkov.exe")
        exe_layout.addWidget(self.exe_input, 1)
        
        browse_btn = QPushButton("📁 Обзор")
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self._browse_exe)
        exe_layout.addWidget(browse_btn)
        
        layout.addLayout(exe_layout)
        
        # Help text
        help_text = QLabel(
            "💡 Как найти имя .exe:\n"
            "1. Запустите игру\n"
            "2. Откройте Task Manager (Ctrl+Shift+Esc)\n"
            "3. Вкладка Details → найдите процесс игры\n"
            "4. Скопируйте точное имя файла"
        )
        help_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background-color: #1A1A1A;
                padding: 12px;
                border-radius: 8px;
                border-left: 3px solid #E63946;
            }
        """)
        layout.addWidget(help_text)
        
        # Priority
        layout.addWidget(QLabel("Приоритет процесса:"))
        priority_layout = QHBoxLayout()
        
        priorities = [
            ("🔥 Высокий (рекомендуется)", "high"),
            ("⚡ Выше среднего", "above_normal"),
            ("📊 Обычный", "normal"),
        ]
        
        self.priority_buttons = {}
        for text, value in priorities:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty('priority_value', value)
            btn.clicked.connect(lambda checked, b=btn: self._select_priority(b))
            priority_layout.addWidget(btn)
            self.priority_buttons[value] = btn
        
        # Select 'high' by default
        self.priority_buttons['high'].setChecked(True)
        self.selected_priority = 'high'
        
        layout.addLayout(priority_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("✅ Добавить игру")
        add_btn.clicked.connect(self._add_game)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _browse_exe(self):
        """Browse for executable file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите .exe файл игры",
            "",
            "Executable Files (*.exe)"
        )
        
        if file_path:
            # Extract just the filename
            exe_name = Path(file_path).name
            self.exe_input.setText(exe_name)
    
    def _select_priority(self, button):
        """Handle priority button selection"""
        # Uncheck all other buttons
        for btn in self.priority_buttons.values():
            if btn != button:
                btn.setChecked(False)
        
        # Ensure this button stays checked
        button.setChecked(True)
        self.selected_priority = button.property('priority_value')
    
    def _add_game(self):
        """Add the game profile"""
        # Validate inputs
        game_name = self.name_input.text().strip()
        exe_name = self.exe_input.text().strip()
        
        if not game_name:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите название игры!"
            )
            return
        
        if not exe_name:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите имя .exe файла!"
            )
            return
        
        if not exe_name.endswith('.exe'):
            exe_name += '.exe'
        
        # Create profile
        profile = {
            "game_name": game_name,
            "enabled": True,
            "executable_names": [exe_name],
            "priority": self.selected_priority,
            "affinity": "auto",
            "gpu": {
                "enabled": True,
                "power_limit": 100,
                "temp_limit": 85,
                "fan_curve": "aggressive"
            },
            "ram": {
                "enabled": True,
                "cleanup_before_launch": True,
                "reserved_mb": 2048
            },
            "windows": {
                "game_mode": True,
                "fullscreen_optimizations": False,
                "hags": True,
                "game_bar": False
            }
        }
        
        # Save to file
        try:
            profiles_dir = Path("config/profiles")
            profiles_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename from game name
            filename = game_name.lower().replace(' ', '_').replace(':', '') + '.json'
            filepath = profiles_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Успех!",
                f"✅ Игра '{game_name}' добавлена!\n\n"
                f"Файл: {filename}\n\n"
                f"Перезапустите PartMart Boost для применения."
            )
            
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить профиль:\n{e}"
            )
    
    def get_profile_data(self):
        """Get the created profile data"""
        return {
            'game_name': self.name_input.text().strip(),
            'exe_name': self.exe_input.text().strip(),
            'priority': self.selected_priority,
        }


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = AddGameDialog()
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("Game added:", dialog.get_profile_data())
    
    sys.exit()
