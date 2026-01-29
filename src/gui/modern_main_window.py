#!/usr/bin/env python3
"""Modern Main Window - Liquid Glass UI

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

Beautiful main window with:
- Game library grid
- Glass panels
- Performance dashboard
- MSI-inspired design
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QScrollArea, QPushButton,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.ui.widgets import GameCard, GlassPanel, ModernButton, StatusIndicator
from src.ui.themes import MSIColors


class ModernMainWindow(QMainWindow):
    """Modern main window with Liquid Glass UI"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PartMart Boost - Gaming Performance Optimizer')
        self.setMinimumSize(1200, 800)
        
        # Sample game data
        self.games = [
            {'name': 'GTA V', 'status': 'Running'},
            {'name': 'Counter-Strike 2', 'status': 'Not Running'},
            {'name': 'Escape from Tarkov', 'status': 'Not Running'},
            {'name': 'PUBG', 'status': 'Not Running'},
            {'name': 'Cyberpunk 2077', 'status': 'Not Running'},
            {'name': 'The Witcher 3', 'status': 'Not Running'},
            {'name': 'Red Dead 2', 'status': 'Not Running'},
            {'name': 'Fortnite', 'status': 'Not Running'},
        ]
        
        self._init_ui()
        self._setup_monitoring()
    
    def _init_ui(self):
        """Initialize UI"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # System status panel
        status_panel = self._create_status_panel()
        main_layout.addWidget(status_panel)
        
        # Game library
        library = self._create_game_library()
        main_layout.addWidget(library, stretch=1)
        
        # Control buttons
        controls = self._create_controls()
        main_layout.addWidget(controls)
    
    def _create_header(self) -> QWidget:
        """Create header with title and version"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel('PartMart Boost')
        title.setProperty('class', 'heading')
        title_font = QFont('Segoe UI', 32, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f'color: white;')
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Version
        version = QLabel('v0.3.5e')
        version.setStyleSheet(f'color: {MSIColors.RED_PRIMARY}; font-size: 14px; font-weight: 600;')
        layout.addWidget(version)
        
        return header
    
    def _create_status_panel(self) -> GlassPanel:
        """Create system status panel"""
        panel = GlassPanel(opacity=0.85, radius=12)
        panel.setFixedHeight(120)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(40)
        
        # Status indicator
        status_container = QVBoxLayout()
        status_container.setSpacing(8)
        
        status_header = QHBoxLayout()
        self.status_dot = StatusIndicator('active')
        status_header.addWidget(self.status_dot)
        status_header.addWidget(QLabel('System Status'))
        status_header.addStretch()
        status_container.addLayout(status_header)
        
        self.status_text = QLabel('All Systems Running')
        self.status_text.setStyleSheet(f'color: {MSIColors.TEXT_PRIMARY}; font-size: 16px; font-weight: 600;')
        status_container.addWidget(self.status_text)
        
        layout.addLayout(status_container)
        
        # Divider
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.VLine)
        divider1.setStyleSheet(f'background-color: {MSIColors.GRAY_SHARP}; max-width: 1px;')
        layout.addWidget(divider1)
        
        # CPU metric
        cpu_container = self._create_metric_display('CPU Usage', '0.0%')
        layout.addLayout(cpu_container)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.VLine)
        divider2.setStyleSheet(f'background-color: {MSIColors.GRAY_SHARP}; max-width: 1px;')
        layout.addWidget(divider2)
        
        # RAM metric
        ram_container = self._create_metric_display('RAM Usage', '0 MB')
        layout.addLayout(ram_container)
        
        # Divider
        divider3 = QFrame()
        divider3.setFrameShape(QFrame.Shape.VLine)
        divider3.setStyleSheet(f'background-color: {MSIColors.GRAY_SHARP}; max-width: 1px;')
        layout.addWidget(divider3)
        
        # GPU metric
        gpu_container = self._create_metric_display('GPU Usage', '0.0%')
        layout.addLayout(gpu_container)
        
        layout.addStretch()
        
        return panel
    
    def _create_metric_display(self, label: str, initial_value: str) -> QVBoxLayout:
        """Create metric display"""
        container = QVBoxLayout()
        container.setSpacing(8)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f'color: {MSIColors.TEXT_TERTIARY}; font-size: 11px;')
        container.addWidget(label_widget)
        
        # Value
        value_widget = QLabel(initial_value)
        value_widget.setStyleSheet(f'color: {MSIColors.TEXT_PRIMARY}; font-size: 24px; font-weight: 700;')
        container.addWidget(value_widget)
        
        # Store reference
        if label == 'CPU Usage':
            self.cpu_value = value_widget
        elif label == 'RAM Usage':
            self.ram_value = value_widget
        elif label == 'GPU Usage':
            self.gpu_value = value_widget
        
        return container
    
    def _create_game_library(self) -> QWidget:
        """Create game library grid"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Header
        header = QLabel('Game Library')
        header.setProperty('class', 'subheading')
        header_font = QFont('Segoe UI', 20, QFont.Weight.DemiBold)
        header.setFont(header_font)
        header.setStyleSheet(f'color: {MSIColors.TEXT_PRIMARY};')
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet('background: transparent;')
        
        # Grid container
        grid_container = QWidget()
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add game cards
        self.game_cards = []
        for i, game in enumerate(self.games):
            card = GameCard(game['name'], game['status'])
            card.clicked.connect(self._on_game_card_clicked)
            self.game_cards.append(card)
            
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(card, row, col)
        
        scroll.setWidget(grid_container)
        layout.addWidget(scroll)
        
        return container
    
    def _create_controls(self) -> QWidget:
        """Create control buttons"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Start/Stop button
        self.start_button = ModernButton('Start Monitoring', primary=True)
        self.start_button.setMinimumWidth(200)
        self.start_button.clicked.connect(self._toggle_monitoring)
        layout.addWidget(self.start_button)
        
        # Settings button
        settings_btn = ModernButton('Settings')
        settings_btn.setMinimumWidth(150)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        # Stats
        stats = QLabel('40+ Games Supported  •  FSR 3.x Ready')
        stats.setStyleSheet(f'color: {MSIColors.TEXT_TERTIARY}; font-size: 12px;')
        layout.addWidget(stats)
        
        return container
    
    def _setup_monitoring(self):
        """Setup monitoring timer"""
        self.monitoring_active = False
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._update_metrics)
    
    def _toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if not self.monitoring_active:
            # Start monitoring
            self.monitoring_active = True
            self.start_button.setText('Stop Monitoring')
            self.status_dot.set_status('active')
            self.status_text.setText('Monitoring Active')
            self.monitor_timer.start(1000)  # Update every second
        else:
            # Stop monitoring
            self.monitoring_active = False
            self.start_button.setText('Start Monitoring')
            self.status_dot.set_status('inactive')
            self.status_text.setText('Monitoring Stopped')
            self.monitor_timer.stop()
    
    def _update_metrics(self):
        """Update performance metrics (mock data)"""
        import random
        
        # Mock CPU
        cpu = random.uniform(20, 60)
        self.cpu_value.setText(f'{cpu:.1f}%')
        
        # Mock RAM
        ram = random.uniform(2000, 8000)
        self.ram_value.setText(f'{ram:.0f} MB')
        
        # Mock GPU
        gpu = random.uniform(30, 80)
        self.gpu_value.setText(f'{gpu:.1f}%')
        
        # Update game cards
        for card in self.game_cards:
            if card.status == 'Running':
                card.update_metrics(
                    cpu=random.uniform(10, 50),
                    ram=random.uniform(1000, 4000)
                )
    
    def _on_game_card_clicked(self, game_name: str):
        """Handle game card click"""
        print(f'Clicked: {game_name}')
        # TODO: Show game details/settings


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    from src.ui.themes import apply_theme
    
    app = QApplication(sys.argv)
    apply_theme(app)
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())
