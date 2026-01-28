#!/usr/bin/env python3
"""
🐉 PartMart Boost - Точка входа в приложение
Игровой оптимизатор для ПК
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from src.ui import MainWindow


def check_requirements():
    """Проверка системных требований"""
    # Проверка операционной системы
    if sys.platform != "win32":
        return False, "Приложение работает только на Windows 10/11"
    
    # Проверка прав администратора
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            return False, "Приложение требует прав администратора для оптимизации GPU/RAM"
    except Exception as e:
        return False, f"Не удалось проверить права администратора: {e}"
    
    return True, ""


def show_error(message: str):
    """Показать окно ошибки"""
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle("Ошибка запуска")
    msg_box.setText(message)
    msg_box.exec()
    sys.exit(1)


def main():
    """Главная функция приложения"""
    # Проверка требований
    success, error_msg = check_requirements()
    if not success:
        show_error(error_msg)
    
    # Создание приложения
    app = QApplication(sys.argv)
    app.setApplicationName("PartMart Boost")
    app.setApplicationVersion("0.1.0-dev")
    app.setOrganizationName("PartMart")
    
    # High DPI support
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Создание и отображение главного окна
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        show_error(f"Не удалось создать главное окно:\n{e}")
    
    # Запуск цикла событий
    sys.exit(app.exec())


if __name__ == "__main__":
    print("🐉 PartMart Boost v0.1.0-dev")
    print("Твой ПК. Твоя мощь.")
    print("="*50)
    main()
