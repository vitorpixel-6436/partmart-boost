"""🐉 PartMart Boost - Главное окно приложения"""

import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QProgressBar,
    QGroupBox, QGridLayout, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QFont


class MainWindow(QMainWindow):
    """Главное окно PartMart Boost"""
    
    # Сигналы
    quick_boost_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 PartMart Boost v0.1.0-dev")
        self.setMinimumSize(1000, 700)
        
        # Загрузка темы
        self.load_theme()
        
        # Создание UI
        self.init_ui()
        
    def load_theme(self):
        """Загрузка Steam-style темы"""
        theme_path = Path(__file__).parent / "theme.qss"
        if theme_path.exists():
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
    
    def init_ui(self):
        """Инициализация UI компонентов"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Быстрый буст кнопка
        quick_boost_btn = QPushButton("⚡ Быстрый Буст")
        quick_boost_btn.setObjectName("quickBoostBtn")
        quick_boost_btn.clicked.connect(self.on_quick_boost)
        main_layout.addWidget(quick_boost_btn)
        
        # Stats Dashboard
        stats_widget = self.create_stats_dashboard()
        main_layout.addWidget(stats_widget)
        
        # Tab Widget
        tabs = self.create_tabs()
        main_layout.addWidget(tabs)
        
        # Status Bar
        self.create_status_bar()
    
    def create_header(self) -> QWidget:
        """Создание header с лого и описанием"""
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setSpacing(5)
        
        # Заголовок
        title = QLabel("🐉 PartMart Boost")
        title.setObjectName("titleLabel")
        layout.addWidget(title)
        
        # Подзаголовок
        subtitle = QLabel("Твой ПК. Твоя мощь.")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        
        return header
    
    def create_stats_dashboard(self) -> QWidget:
        """Создание панели со статистикой"""
        dashboard = QWidget()
        layout = QHBoxLayout(dashboard)
        layout.setSpacing(10)
        
        # Статистические карточки
        cards_data = [
            ("🎮 FPS", "-- FPS", "Текущий"),
            ("🌡️ GPU", "-- °C", "Температура"),
            ("💾 RAM", "-- GB", "Использовано"),
            ("⬆️ Прирост", "-- %", "Оптимизация")
        ]
        
        for title, value, subtitle in cards_data:
            card = self.create_stat_card(title, value, subtitle)
            layout.addWidget(card)
        
        return dashboard
    
    def create_stat_card(self, title: str, value: str, subtitle: str) -> QGroupBox:
        """Создание карточки статистики"""
        card = QGroupBox()
        layout = QVBoxLayout(card)
        
        # Заголовок
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(12)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Значение
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = value_label.font()
        font.setPointSize(20)
        font.setBold(True)
        value_label.setFont(font)
        layout.addWidget(value_label)
        
        # Подзаголовок
        sub_label = QLabel(subtitle)
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_label)
        
        return card
    
    def create_tabs(self) -> QTabWidget:
        """Создание вкладок"""
        tabs = QTabWidget()
        
        # Вкладки
        tabs.addTab(self.create_optimization_tab(), "🚀 Оптимизация")
        tabs.addTab(self.create_monitor_tab(), "📊 Мониторинг")
        tabs.addTab(self.create_games_tab(), "🎮 Игры")
        tabs.addTab(self.create_settings_tab(), "⚙️ Настройки")
        
        return tabs
    
    def create_optimization_tab(self) -> QWidget:
        """Вкладка оптимизации"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # GPU Optimizer
        gpu_group = QGroupBox("🎮 GPU Optimizer")
        gpu_layout = QVBoxLayout(gpu_group)
        
        gpu_btn = QPushButton("Оптимизировать GPU")
        gpu_btn.clicked.connect(lambda: self.show_info("GPU", "GPU оптимизация будет реализована"))
        gpu_layout.addWidget(gpu_btn)
        
        gpu_progress = QProgressBar()
        gpu_progress.setValue(0)
        gpu_layout.addWidget(gpu_progress)
        
        layout.addWidget(gpu_group)
        
        # RAM Optimizer
        ram_group = QGroupBox("💾 RAM Optimizer")
        ram_layout = QVBoxLayout(ram_group)
        
        ram_btn = QPushButton("Оптимизировать RAM")
        ram_btn.clicked.connect(lambda: self.show_info("RAM", "RAM оптимизация будет реализована"))
        ram_layout.addWidget(ram_btn)
        
        ram_progress = QProgressBar()
        ram_progress.setValue(0)
        ram_layout.addWidget(ram_progress)
        
        layout.addWidget(ram_group)
        
        # OS Tweaks
        os_group = QGroupBox("⚙️ OS Tweaks")
        os_layout = QVBoxLayout(os_group)
        
        os_btn = QPushButton("Применить твики")
        os_btn.clicked.connect(lambda: self.show_info("OS", "OS твики будут реализованы"))
        os_layout.addWidget(os_btn)
        
        layout.addWidget(os_group)
        
        layout.addStretch()
        
        return tab
    
    def create_monitor_tab(self) -> QWidget:
        """Вкладка мониторинга"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_label = QLabel("📊 Мониторинг производительности")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = info_label.font()
        font.setPointSize(14)
        info_label.setFont(font)
        layout.addWidget(info_label)
        
        placeholder = QLabel("
Графики FPS, температур и загрузки\nбудут реализованы в следующих версиях")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        return tab
    
    def create_games_tab(self) -> QWidget:
        """Вкладка игр"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_label = QLabel("🎮 Game Launcher")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = info_label.font()
        font.setPointSize(14)
        info_label.setFont(font)
        layout.addWidget(info_label)
        
        placeholder = QLabel("
Автоматическое обнаружение игр\nи индивидуальные профили\nбудут реализованы в следующих версиях")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        return tab
    
    def create_settings_tab(self) -> QWidget:
        """Вкладка настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        info_label = QLabel("⚙️ Настройки")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = info_label.font()
        font.setPointSize(14)
        info_label.setFont(font)
        layout.addWidget(info_label)
        
        placeholder = QLabel("
Настройки приложения\nбудут реализованы в следующих версиях")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        
        return tab
    
    def create_status_bar(self):
        """Создание status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("✅ Готов к оптимизации")
    
    def on_quick_boost(self):
        """Обработчик кнопки Быстрый Буст"""
        self.quick_boost_requested.emit()
        self.show_info(
            "Быстрый Буст",
            "Функция Быстрого Буста будет реализована в следующих версиях.\n"
            "Она автоматически оптимизирует GPU, RAM и OS настройки."
        )
    
    def show_info(self, title: str, message: str):
        """Показать информационное окно"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def update_status(self, message: str):
        """Обновить статус бар"""
        self.statusBar().showMessage(message)
