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

# Импорты наших компонентов
from src.ui.ai_widget import PartMartAIWidget

class MainWindow(QMainWindow):
    """Главное окно PartMart Boost"""

    # Сигналы
    quick_boost_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐉 PartMart Boost v0.1.0-dev")
        self.setMinimumSize(1050, 750)

        # Загрузка темы
        self.load_theme()

        # Создание UI
        self.init_ui()

    def load_theme(self):
        """Загрузка Steam-style QSS"""
        theme_path = Path(__file__).parent / "theme.qss"
        if theme_path.exists():
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный вертикальный лейаут
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- HEADER ---
        self.header = QWidget()
        self.header.setObjectName("header")
        self.header.setFixedHeight(80)
        header_layout = QHBoxLayout(self.header)
        
        logo_lbl = QLabel("🐉 PARTMART BOOST")
        logo_lbl.setObjectName("logo_label")
        logo_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        
        header_layout.addWidget(logo_lbl)
        header_layout.addStretch()
        
        self.main_layout.addWidget(self.header)

        # --- CONTENT AREA (Tabs) ---
        self.tabs = QTabWidget()
        self.tabs.setObjectName("main_tabs")
        
        # Вкладка "Дашборд"
        self.dashboard_tab = QWidget()
        self.init_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "🚀 ДАШБОРД")

        # Вкладка "AI Оптимизация" (НОВАЯ)
        self.ai_tab = QWidget()
        self.init_ai_tab()
        self.tabs.addTab(self.ai_tab, "🤖 AI OPTIMIZER")

        # Вкладка "Инструменты"
        self.tools_tab = QWidget()
        self.tabs.addTab(self.tools_tab, "🛠 ИНСТРУМЕНТЫ")

        self.main_layout.addWidget(self.tabs)

        # --- STATUS BAR ---
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready to boost performance.")

    def init_dashboard_tab(self):
        layout = QHBoxLayout(self.dashboard_tab)
        
        # Левая колонка: Статистика
        left_panel = QVBoxLayout()
        
        stats_group = QGroupBox("ТЕКУЩИЕ ПОКАЗАТЕЛИ")
        stats_layout = QGridLayout(stats_group)
        
        stats_layout.addWidget(QLabel("GPU Load:"), 0, 0)
        self.gpu_pbar = QProgressBar()
        self.gpu_pbar.setValue(45)
        stats_layout.addWidget(self.gpu_pbar, 0, 1)
        
        stats_layout.addWidget(QLabel("RAM Usage:"), 1, 0)
        self.ram_pbar = QProgressBar()
        self.ram_pbar.setValue(30)
        stats_layout.addWidget(self.ram_pbar, 1, 1)
        
        left_panel.addWidget(stats_group)
        left_panel.addStretch()
        
        # Правая колонка: Кнопки действий
        right_panel = QVBoxLayout()
        
        boost_btn = QPushButton("🚀 QUICK BOOST")
        boost_btn.setObjectName("boost_button")
        boost_btn.setFixedHeight(60)
        boost_btn.clicked.connect(self.on_quick_boost)
        
        right_panel.addWidget(boost_btn)
        right_panel.addStretch()
        
        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)

    def init_ai_tab(self):
        """Инициализация вкладки AI Optimizer"""
        layout = QVBoxLayout(self.ai_tab)
        self.ai_widget = PartMartAIWidget()
        layout.addWidget(self.ai_widget)

    def on_quick_boost(self):
        """Обработка нажатия Quick Boost"""
        # QMessageBox.information(self, "Boost", "Optimization started! Checking system state...")
        self.quick_boost_requested.emit()

    def update_ai_view(self, ai_report):
        """Обновление AI виджета новыми данными"""
        if hasattr(self, 'ai_widget'):
            self.ai_widget.update_insights(ai_report)
