"""Circular Progress Ring

Version: 0.3.5c
Features:
- Smooth animations
- Customizable colors
- Gradient support
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QRectF, pyqtProperty
from PyQt6.QtGui import QPainter, QPen, QConicalGradient, QColor
from ui.theme import get_theme


class ProgressRing(QWidget):
    """Circular progress indicator"""
    
    def __init__(self, size: int = 120, parent=None):
        super().__init__(parent)
        
        self._value = 0
        self._max_value = 100
        self._thickness = 8
        
        self.setFixedSize(size, size)
        
        # Animation
        self.anim = QPropertyAnimation(self, b"value")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @pyqtProperty(int)
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = max(0, min(val, self._max_value))
        self.update()
    
    def set_value(self, val: int, animate: bool = True):
        """Set value with optional animation"""
        if animate:
            self.anim.setStartValue(self._value)
            self.anim.setEndValue(val)
            self.anim.start()
        else:
            self.value = val
    
    def paintEvent(self, event):
        """Draw progress ring"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme = get_theme()
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        side = min(width, height)
        
        painter.translate(width / 2, height / 2)
        painter.scale(side / 200.0, side / 200.0)
        
        # Background circle
        pen = QPen()
        pen.setWidth(self._thickness)
        pen.setColor(QColor(theme.colors.bg_tertiary))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(QRectF(-90, -90, 180, 180), 0, 360 * 16)
        
        # Progress arc with gradient
        gradient = QConicalGradient(0, 0, 90)
        gradient.setColorAt(0.0, QColor(theme.colors.primary))
        gradient.setColorAt(1.0, QColor(theme.colors.primary_light))
        
        pen.setBrush(gradient)
        pen.setColor(QColor(theme.colors.primary))
        painter.setPen(pen)
        
        # Calculate angle
        angle = int((self._value / self._max_value) * 360 * 16)
        painter.drawArc(QRectF(-90, -90, 180, 180), 90 * 16, -angle)
        
        painter.end()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton
    import sys
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setStyleSheet("background: #0D0D0D;")
    layout = QVBoxLayout()
    
    ring = ProgressRing(150)
    layout.addWidget(ring, alignment=Qt.AlignmentFlag.AlignCenter)
    
    # Test button
    btn = QPushButton("Set to 75%")
    btn.clicked.connect(lambda: ring.set_value(75))
    layout.addWidget(btn)
    
    window.setLayout(layout)
    window.resize(400, 400)
    window.show()
    
    # Animate to 50% on start
    ring.set_value(50)
    
    sys.exit(app.exec())
