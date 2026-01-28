"""Status Indicator Component

Version: 0.3.5c
Features:
- Pulsing animation for active states
- Color-coded statuses
- Smooth transitions
"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt, pyqtProperty, QTimer
from PyQt6.QtGui import QColor
from ui.theme import get_theme
from enum import Enum


class StatusType(Enum):
    """Status types"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    IDLE = "idle"
    ACTIVE = "active"


class StatusIndicator(QLabel):
    """Animated status indicator dot"""
    
    def __init__(self, status: StatusType = StatusType.IDLE, parent=None):
        super().__init__("●", parent)
        
        self._status = status
        self._pulse_opacity = 1.0
        self._is_pulsing = False
        
        self.setFixedSize(24, 24)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Pulse animation
        self.pulse_anim = QPropertyAnimation(self, b"pulse_opacity")
        self.pulse_anim.setDuration(1000)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.pulse_anim.setLoopCount(-1)  # Infinite
        
        self._update_style()
    
    @pyqtProperty(float)
    def pulse_opacity(self):
        return self._pulse_opacity
    
    @pulse_opacity.setter
    def pulse_opacity(self, value):
        self._pulse_opacity = value
        self._update_style()
    
    def set_status(self, status: StatusType, pulse: bool = False):
        """Change status"""
        self._status = status
        
        if pulse and not self._is_pulsing:
            self._start_pulse()
        elif not pulse and self._is_pulsing:
            self._stop_pulse()
        
        self._update_style()
    
    def _start_pulse(self):
        """Start pulsing animation"""
        self._is_pulsing = True
        self.pulse_anim.setStartValue(1.0)
        self.pulse_anim.setEndValue(0.3)
        self.pulse_anim.start()
    
    def _stop_pulse(self):
        """Stop pulsing animation"""
        self._is_pulsing = False
        self.pulse_anim.stop()
        self._pulse_opacity = 1.0
        self._update_style()
    
    def _get_color(self) -> str:
        """Get color for current status"""
        theme = get_theme()
        
        color_map = {
            StatusType.SUCCESS: theme.colors.success,
            StatusType.WARNING: theme.colors.warning,
            StatusType.ERROR: theme.colors.error,
            StatusType.INFO: theme.colors.info,
            StatusType.IDLE: theme.colors.text_tertiary,
            StatusType.ACTIVE: theme.colors.primary,
        }
        
        return color_map.get(self._status, theme.colors.text_tertiary)
    
    def _update_style(self):
        """Update style based on status and opacity"""
        color = self._get_color()
        
        # Parse color and apply opacity
        if color.startswith('#'):
            # Convert hex to rgba
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            a = int(self._pulse_opacity * 255)
            color = f"rgba({r}, {g}, {b}, {a})"
        
        self.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                color: {color};
                background: transparent;
            }}
        """)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
    import sys
    
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setStyleSheet("background: #0D0D0D;")
    layout = QVBoxLayout()
    
    # Test indicators
    row = QHBoxLayout()
    
    statuses = [
        (StatusType.SUCCESS, "Success"),
        (StatusType.WARNING, "Warning"),
        (StatusType.ERROR, "Error"),
        (StatusType.INFO, "Info"),
        (StatusType.IDLE, "Idle"),
        (StatusType.ACTIVE, "Active"),
    ]
    
    for status, label in statuses:
        col = QVBoxLayout()
        
        indicator = StatusIndicator(status)
        col.addWidget(indicator, alignment=Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: white; font-size: 12px;")
        col.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        row.addLayout(col)
    
    layout.addLayout(row)
    
    # Test pulsing
    pulse_indicator = StatusIndicator(StatusType.ACTIVE)
    layout.addWidget(pulse_indicator, alignment=Qt.AlignmentFlag.AlignCenter)
    
    btn = QPushButton("Toggle Pulse")
    btn.setCheckable(True)
    btn.clicked.connect(lambda checked: pulse_indicator.set_status(StatusType.ACTIVE, checked))
    layout.addWidget(btn)
    
    window.setLayout(layout)
    window.resize(600, 300)
    window.show()
    
    sys.exit(app.exec())
