"""Card Components

Version: 0.3.5c
Features:
- Animated hover effects
- Shadow on hover
- Customizable border
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, pyqtProperty
from PyQt6.QtGui import QColor
from ui.theme import get_theme


class Card(QFrame):
    """Base card component with animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._elevation = 0
        self.setAutoFillBackground(True)
        
        # Shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.shadow)
        
        # Animation
        self.shadow_anim = QPropertyAnimation(self, b"elevation")
        self.shadow_anim.setDuration(200)
        self.shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply theme style"""
        theme = get_theme()
        self.setStyleSheet(theme.get_stylesheet('card'))
    
    @pyqtProperty(int)
    def elevation(self):
        return self._elevation
    
    @elevation.setter
    def elevation(self, value):
        self._elevation = value
        self.shadow.setBlurRadius(value)
        self.shadow.setOffset(0, value // 4)
    
    def enterEvent(self, event):
        """Animate shadow on hover"""
        self.shadow_anim.setStartValue(self._elevation)
        self.shadow_anim.setEndValue(20)
        self.shadow_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Remove shadow on leave"""
        self.shadow_anim.setStartValue(self._elevation)
        self.shadow_anim.setEndValue(0)
        self.shadow_anim.start()
        super().leaveEvent(event)


class MetricCard(Card):
    """Card for displaying metrics"""
    
    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        
        self.setFixedHeight(180)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        self.title_label = QLabel()
        theme = get_theme()
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {theme.colors.text_secondary};
                background: transparent;
            }}
        """)
        self._set_title(title, icon)
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                font-weight: 700;
                color: {theme.colors.primary};
                background: transparent;
            }}
        """)
        layout.addWidget(self.value_label)
        
        # Subtitle
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {theme.colors.text_tertiary};
                background: transparent;
            }}
        """)
        layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _set_title(self, title: str, icon: str):
        """Set title with icon"""
        if icon:
            self.title_label.setText(f"{icon} {title}")
        else:
            self.title_label.setText(title)
    
    def set_value(self, value: str):
        """Update value"""
        self.value_label.setText(value)
    
    def set_subtitle(self, text: str):
        """Update subtitle"""
        self.subtitle_label.setText(text)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget
    import sys
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setStyleSheet("background: #0D0D0D;")
    layout = QHBoxLayout()
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(20)
    
    # Test cards
    card1 = MetricCard("GPU Temperature", "🌡️")
    card1.set_value("65°C")
    card1.set_subtitle("RTX 4090")
    layout.addWidget(card1)
    
    card2 = MetricCard("RAM Usage", "🧠")
    card2.set_value("67%")
    card2.set_subtitle("16.2 / 32.0 GB")
    layout.addWidget(card2)
    
    card3 = MetricCard("CPU Load", "💻")
    card3.set_value("42%")
    card3.set_subtitle("AMD Ryzen 9")
    layout.addWidget(card3)
    
    window.setLayout(layout)
    window.resize(1000, 300)
    window.show()
    
    sys.exit(app.exec())
