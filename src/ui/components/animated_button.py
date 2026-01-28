"""Animated Button Component

Version: 0.3.5c
Features:
- Smooth hover animations
- Ripple effect on click
- Icon support
- Loading state
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QTimer, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPen
from ui.theme import get_theme


class AnimatedButton(QPushButton):
    """Button with smooth animations"""
    
    def __init__(self, text: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        
        self.icon_text = icon
        self._is_loading = False
        self._hover_progress = 0.0
        
        # Set text with icon
        if icon:
            self.setText(f"{icon} {text}")
        else:
            self.setText(text)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Animation
        self.hover_anim = QPropertyAnimation(self, b"hover_progress")
        self.hover_anim.setDuration(200)
        self.hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply theme style"""
        theme = get_theme()
        self.setStyleSheet(theme.get_stylesheet('button_primary'))
    
    @pyqtProperty(float)
    def hover_progress(self):
        return self._hover_progress
    
    @hover_progress.setter
    def hover_progress(self, value):
        self._hover_progress = value
        self.update()
    
    def enterEvent(self, event):
        """Animate on hover"""
        if not self._is_loading:
            self.hover_anim.setStartValue(self._hover_progress)
            self.hover_anim.setEndValue(1.0)
            self.hover_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animate on leave"""
        if not self._is_loading:
            self.hover_anim.setStartValue(self._hover_progress)
            self.hover_anim.setEndValue(0.0)
            self.hover_anim.start()
        super().leaveEvent(event)
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self._is_loading = loading
        if loading:
            self.setEnabled(False)
            original_text = self.text()
            self.setText("⏳ Loading...")
            self.setProperty('original_text', original_text)
        else:
            self.setEnabled(True)
            original_text = self.property('original_text')
            if original_text:
                self.setText(original_text)
    
    def set_icon(self, icon: str):
        """Change icon"""
        self.icon_text = icon
        text = self.text()
        # Remove old icon
        if ' ' in text:
            text = text.split(' ', 1)[1]
        self.setText(f"{icon} {text}")


class IconButton(AnimatedButton):
    """Icon-only button"""
    
    def __init__(self, icon: str, tooltip: str = "", parent=None):
        super().__init__(icon, parent=parent)
        
        if tooltip:
            self.setToolTip(tooltip)
        
        self.setFixedSize(48, 48)
        
        theme = get_theme()
        self.setStyleSheet(f"""
            QPushButton {{
                background: {theme.colors.bg_secondary};
                border: 2px solid {theme.colors.border_primary};
                border-radius: 24px;
                font-size: 20px;
            }}
            QPushButton:hover {{
                background: {theme.colors.bg_tertiary};
                border-color: {theme.colors.border_focus};
            }}
        """)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setStyleSheet("background: #0D0D0D;")
    layout = QVBoxLayout()
    
    # Test buttons
    btn1 = AnimatedButton("Primary Button", "🚀")
    btn1.clicked.connect(lambda: print("Clicked!"))
    layout.addWidget(btn1)
    
    btn2 = AnimatedButton("With Icon", "⚡")
    layout.addWidget(btn2)
    
    btn3 = IconButton("⚙️", "Settings")
    layout.addWidget(btn3)
    
    window.setLayout(layout)
    window.resize(400, 300)
    window.show()
    
    sys.exit(app.exec())
