#!/usr/bin/env python3
"""Modern Main Window - Standalone Version

Version: 0.3.5d_hotfix8 (Package 3.9a, Stage 7.8a)

Completely standalone - no imports from src!
All widgets and styles defined inline.

Beautiful Liquid Glass UI with:
- MSI-inspired design
- Glass panels
- Game library
- Performance dashboard
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QScrollArea, QPushButton,
    QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QPainterPath
import sys
import random

# ============================================================================
# MSI COLORS (Inline)
# ============================================================================

class MSIColors:
    """MSI color palette"""
    RED_PRIMARY = '#E30613'
    RED_HOVER = '#FF1825'
    
    BG_PRIMARY = '#0A0A0A'
    BG_SECONDARY = '#141414'
    BG_TERTIARY = '#1E1E1E'
    BG_ELEVATED = '#282828'
    
    GLASS_DARK = 'rgba(10, 10, 10, 0.85)'
    
    GRAY_SHARP = '#3C3C3C'
    
    TEXT_PRIMARY = '#FFFFFF'
    TEXT_SECONDARY = '#B4B4B4'
    TEXT_TERTIARY = '#8C8C8C'
    
    GRADIENT_RED = 'qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E30613, stop:1 #8A0409)'
    GRADIENT_DARK = 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141414, stop:1 #0A0A0A)'

# ============================================================================
# GLASS PANEL WIDGET (Inline)
# ============================================================================

class GlassPanel(QWidget):
    """Glass panel widget with blur effect"""
    
    def __init__(self, opacity=0.85, radius=12, parent=None):
        super().__init__(parent)
        self.opacity = opacity
        self.radius = radius
        self.setAutoFillBackground(False)
    
    def paintEvent(self, event):
        """Custom paint with glass effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rect path
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 
                           self.radius, self.radius)
        
        # Background
        bg_color = QColor(10, 10, 10, int(self.opacity * 255))
        painter.fillPath(path, bg_color)
        
        # Border
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawPath(path)

# ============================================================================
# STATUS INDICATOR WIDGET (Inline)
# ============================================================================

class StatusIndicator(QWidget):
    """Status indicator dot"""
    
    def __init__(self, status='inactive', parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)
    
    def set_status(self, status: str):
        """Set status (active/inactive/warning/error)"""
        self.status = status
        self.update()
    
    def paintEvent(self, event):
        """Paint status dot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color based on status
        colors = {
            'active': QColor(0, 214, 57),
            'inactive': QColor(140, 140, 140),
            'warning': QColor(255, 184, 0),
            'error': QColor(227, 6, 19)
        }
        
        color = colors.get(self.status, colors['inactive'])
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 8, 8)

# ============================================================================
# MODERN BUTTON WIDGET (Inline)
# ============================================================================

class ModernButton(QPushButton):
    """Modern styled button"""
    
    def __init__(self, text: str, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self._hover = False
        self.setMouseTracking(True)
        self._apply_style()
    
    def _apply_style(self):
        """Apply button style"""
        if self.primary:
            style = f"""
                QPushButton {{
                    background: {MSIColors.GRADIENT_RED};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {MSIColors.RED_HOVER};
                }}
                QPushButton:pressed {{
                    background: #C00510;
                }}
            """
        else:
            style = f"""
                QPushButton {{
                    background: {MSIColors.BG_TERTIARY};
                    color: {MSIColors.TEXT_PRIMARY};
                    border: 1px solid {MSIColors.GRAY_SHARP};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {MSIColors.BG_ELEVATED};
                    border-color: {MSIColors.RED_PRIMARY};
                }}
                QPushButton:pressed {{
                    background: {MSIColors.BG_SECONDARY};
                }}
            """
        
        self.setStyleSheet(style)

# ============================================================================
# GAME CARD WIDGET (Inline)
# ============================================================================

class GameCard(QWidget):
    """Game card widget"""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, game_name: str, status: str = 'Not Running', parent=None):
        super().__init__(parent)
        self.game_name = game_name
        self.status = status
        self._hover = False
        
        self.setFixedSize(300, 200)
        self.setMouseTracking(True)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Game name
        self.name_label = QLabel(self.game_name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: white;
            }
        """)
        layout.addWidget(self.name_label)
        
        # Status
        self.status_label = QLabel(self.status)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #B4B4B4;
            }
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Metrics
        metrics_layout = QHBoxLayout()
        
        self.cpu_label = QLabel('CPU: --')
        self.cpu_label.setStyleSheet('font-size: 11px; color: #8C8C8C;')
        metrics_layout.addWidget(self.cpu_label)
        
        self.ram_label = QLabel('RAM: --')
        self.ram_label.setStyleSheet('font-size: 11px; color: #8C8C8C;')
        metrics_layout.addWidget(self.ram_label)
        
        layout.addLayout(metrics_layout)
    
    def paintEvent(self, event):
        """Custom paint"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 16, 16)
        
        bg_color = QColor(30, 30, 30) if self._hover else QColor(20, 20, 20)
        painter.fillPath(path, bg_color)
        
        pen_color = QColor(227, 6, 19) if self._hover else QColor(60, 60, 60)
        painter.setPen(QPen(pen_color, 1))
        painter.drawPath(path)
        
        if self._hover:
            glow_rect = rect.adjusted(2, 2, -2, -2)
            glow_path = QPainterPath()
            glow_path.addRoundedRect(glow_rect, 14, 14)
            painter.setPen(QPen(QColor(227, 6, 19, 50), 3))
            painter.drawPath(glow_path)
    
    def enterEvent(self, event):
        self._hover = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._hover = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.game_name)
    
    def update_metrics(self, cpu: float, ram: float):
        """Update metrics"""
        self.cpu_label.setText(f'CPU: {cpu:.1f}%')
        self.ram_label.setText(f'RAM: {ram:.0f} MB')

# ============================================================================
# MODERN MAIN WINDOW (Standalone)
# ============================================================================

class ModernMainWindow(QMainWindow):
    """Modern main window - completely standalone"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PartMart Boost - Gaming Performance Optimizer')
        self.setMinimumSize(1200, 800)
        
        # Sample games
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
        self._apply_theme()
    
    def _init_ui(self):
        """Initialize UI"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Status panel
        status_panel = self._create_status_panel()
        main_layout.addWidget(status_panel)
        
        # Game library
        library = self._create_game_library()
        main_layout.addWidget(library, stretch=1)
        
        # Controls
        controls = self._create_controls()
        main_layout.addWidget(controls)
    
    def _create_header(self) -> QWidget:
        """Create header"""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel('PartMart Boost')
        title_font = QFont('Segoe UI', 32, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet('color: white;')
        layout.addWidget(title)
        
        layout.addStretch()
        
        version = QLabel('v0.3.5d_hotfix8')
        version.setStyleSheet(f'color: {MSIColors.RED_PRIMARY}; font-size: 14px; font-weight: 600;')
        layout.addWidget(version)
        
        return header
    
    def _create_status_panel(self) -> GlassPanel:
        """Create status panel"""
        panel = GlassPanel(opacity=0.85, radius=12)
        panel.setFixedHeight(120)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(40)
        
        # Status
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
        
        # Dividers and metrics
        self._add_divider(layout)
        cpu_container = self._create_metric('CPU Usage', '0.0%')
        layout.addLayout(cpu_container)
        
        self._add_divider(layout)
        ram_container = self._create_metric('RAM Usage', '0 MB')
        layout.addLayout(ram_container)
        
        self._add_divider(layout)
        gpu_container = self._create_metric('GPU Usage', '0.0%')
        layout.addLayout(gpu_container)
        
        layout.addStretch()
        
        return panel
    
    def _add_divider(self, layout):
        """Add vertical divider"""
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet(f'background-color: {MSIColors.GRAY_SHARP}; max-width: 1px;')
        layout.addWidget(divider)
    
    def _create_metric(self, label: str, initial_value: str) -> QVBoxLayout:
        """Create metric display"""
        container = QVBoxLayout()
        container.setSpacing(8)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f'color: {MSIColors.TEXT_TERTIARY}; font-size: 11px;')
        container.addWidget(label_widget)
        
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
        """Create game library"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        header = QLabel('Game Library')
        header_font = QFont('Segoe UI', 20, QFont.Weight.DemiBold)
        header.setFont(header_font)
        header.setStyleSheet(f'color: {MSIColors.TEXT_PRIMARY};')
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet('background: transparent;')
        
        grid_container = QWidget()
        self.grid_layout = QGridLayout(grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
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
        """Create controls"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self.start_button = ModernButton('Start Monitoring', primary=True)
        self.start_button.setMinimumWidth(200)
        self.start_button.clicked.connect(self._toggle_monitoring)
        layout.addWidget(self.start_button)
        
        settings_btn = ModernButton('Settings')
        settings_btn.setMinimumWidth(150)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        stats = QLabel('40+ Games Supported  •  FSR 3.x Ready')
        stats.setStyleSheet(f'color: {MSIColors.TEXT_TERTIARY}; font-size: 12px;')
        layout.addWidget(stats)
        
        return container
    
    def _setup_monitoring(self):
        """Setup monitoring"""
        self.monitoring_active = False
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._update_metrics)
    
    def _toggle_monitoring(self):
        """Toggle monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.start_button.setText('Stop Monitoring')
            self.status_dot.set_status('active')
            self.status_text.setText('Monitoring Active')
            self.monitor_timer.start(1000)
        else:
            self.monitoring_active = False
            self.start_button.setText('Start Monitoring')
            self.status_dot.set_status('inactive')
            self.status_text.setText('Monitoring Stopped')
            self.monitor_timer.stop()
    
    def _update_metrics(self):
        """Update metrics (mock data)"""
        cpu = random.uniform(20, 60)
        self.cpu_value.setText(f'{cpu:.1f}%')
        
        ram = random.uniform(2000, 8000)
        self.ram_value.setText(f'{ram:.0f} MB')
        
        gpu = random.uniform(30, 80)
        self.gpu_value.setText(f'{gpu:.1f}%')
        
        for card in self.game_cards:
            if card.status == 'Running':
                card.update_metrics(
                    cpu=random.uniform(10, 50),
                    ram=random.uniform(1000, 4000)
                )
    
    def _on_game_card_clicked(self, game_name: str):
        """Handle game card click"""
        print(f'Clicked: {game_name}')
    
    def _apply_theme(self):
        """Apply global theme"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {MSIColors.GRADIENT_DARK};
            }}
            QWidget {{
                background-color: transparent;
                color: {MSIColors.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
            QScrollBar:vertical {{
                background: {MSIColors.BG_SECONDARY};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {MSIColors.GRAY_SHARP};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {MSIColors.RED_PRIMARY};
            }}
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set global font
    font = QFont('Segoe UI', 13)
    app.setFont(font)
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())
