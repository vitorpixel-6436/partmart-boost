#!/usr/bin/env python3
"""Game Card Widget

Version: 0.3.5e (Package 3.9a, Stage 7.8a)

Beautiful game card with:
- Soft rounded corners
- Hover effects
- Status indicators
- Performance metrics
- Steam-inspired design
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath


class GameCard(QWidget):
    """Modern game card widget"""
    
    clicked = pyqtSignal(str)  # Emits game name
    
    def __init__(self, game_name: str, status: str = 'Not Running', parent=None):
        super().__init__(parent)
        self.game_name = game_name
        self.status = status
        self._hover = False
        self._pressed = False
        
        self.setFixedSize(300, 200)
        self.setMouseTracking(True)
        
        self._init_ui()
        self._setup_animations()
    
    def _init_ui(self):
        """Initialize UI elements"""
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
        
        # Metrics row
        metrics_layout = QHBoxLayout()
        
        self.cpu_label = QLabel('CPU: --')
        self.cpu_label.setStyleSheet('font-size: 11px; color: #8C8C8C;')
        metrics_layout.addWidget(self.cpu_label)
        
        self.ram_label = QLabel('RAM: --')
        self.ram_label.setStyleSheet('font-size: 11px; color: #8C8C8C;')
        metrics_layout.addWidget(self.ram_label)
        
        layout.addLayout(metrics_layout)
    
    def _setup_animations(self):
        """Setup hover animations"""
        self._scale = 1.0
        self._elevation = 0
    
    def paintEvent(self, event):
        """Custom paint with glassmorphism"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Card background
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 16, 16)
        
        # Background gradient
        if self._hover:
            bg_color = QColor(30, 30, 30)
        else:
            bg_color = QColor(20, 20, 20)
        
        painter.fillPath(path, bg_color)
        
        # Border
        pen_color = QColor(227, 6, 19) if self._hover else QColor(60, 60, 60)
        painter.setPen(QPen(pen_color, 1))
        painter.drawPath(path)
        
        # Glow effect on hover
        if self._hover:
            glow_rect = rect.adjusted(2, 2, -2, -2)
            glow_path = QPainterPath()
            glow_path.addRoundedRect(glow_rect, 14, 14)
            painter.setPen(QPen(QColor(227, 6, 19, 50), 3))
            painter.drawPath(glow_path)
    
    def enterEvent(self, event):
        """Mouse enter - start hover effect"""
        self._hover = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse leave - end hover effect"""
        self._hover = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Mouse release - emit click"""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            self.clicked.emit(self.game_name)
            self.update()
    
    def update_metrics(self, cpu: float, ram: float):
        """Update performance metrics"""
        self.cpu_label.setText(f'CPU: {cpu:.1f}%')
        self.ram_label.setText(f'RAM: {ram:.0f} MB')
    
    def update_status(self, status: str):
        """Update game status"""
        self.status = status
        self.status_label.setText(status)
