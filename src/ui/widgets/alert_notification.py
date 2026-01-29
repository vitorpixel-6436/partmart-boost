#!/usr/bin/env python3
"""Alert Notification Widget

Version: 0.3.5t (package 3.9a, stage 7.7b.7/7.7)

Real-time alert notifications for monitoring systems.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import Optional


class AlertNotification(QFrame):
    """Alert notification popup widget"""
    
    closed = pyqtSignal()
    
    def __init__(self, alert_data: dict, parent=None):
        super().__init__(parent)
        self._alert_data = alert_data
        self._auto_close_timer = None
        self._init_ui()
        self._setup_auto_close()
    
    def _init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMinimumWidth(350)
        self.setMaximumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        level = self._alert_data.get('level', 'info').upper()
        component = self._alert_data.get('component', 'System')
        
        # Level label
        level_label = QLabel(f"⚠ {level}")
        level_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(level_label)
        
        # Component label
        component_label = QLabel(component)
        component_label.setFont(QFont("Arial", 9))
        header_layout.addWidget(component_label)
        
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(
            "QPushButton { border: none; font-size: 16px; font-weight: bold; } "
            "QPushButton:hover { color: red; }"
        )
        close_btn.clicked.connect(self.close_notification)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Message
        message = self._alert_data.get('message', '')
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 9))
        layout.addWidget(message_label)
        
        # Details (if available)
        details = self._alert_data.get('details')
        if details:
            details_label = QLabel(details)
            details_label.setWordWrap(True)
            details_label.setFont(QFont("Arial", 8))
            details_label.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(details_label)
        
        # Style based on level
        colors = {
            'INFO': '#3498db',
            'WARNING': '#f39c12',
            'ERROR': '#e74c3c',
            'CRITICAL': '#c0392b'
        }
        color = colors.get(level, '#3498db')
        
        self.setStyleSheet(f"""
            AlertNotification {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 5px;
            }}
        """)
    
    def _setup_auto_close(self):
        """Setup automatic close timer"""
        level = self._alert_data.get('level', 'info').upper()
        
        # Different durations based on level
        durations = {
            'INFO': 3000,
            'WARNING': 5000,
            'ERROR': 7000,
            'CRITICAL': 10000
        }
        duration = durations.get(level, 5000)
        
        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.timeout.connect(self.close_notification)
        self._auto_close_timer.start(duration)
    
    def close_notification(self):
        """Close notification with animation"""
        if self._auto_close_timer:
            self._auto_close_timer.stop()
        
        # Fade out animation
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.finished.connect(self._on_animation_finished)
        self.animation.start()
    
    def _on_animation_finished(self):
        """Handle animation finished"""
        self.closed.emit()
        self.deleteLater()


class AlertNotificationManager(QWidget):
    """Manager for alert notifications"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._notifications = []
        self._max_notifications = 5
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI"""
        # Position in top-right corner
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)
        self._layout.addStretch()
    
    def show_alert(self, alert_data: dict):
        """Show new alert notification
        
        Args:
            alert_data: Alert data dict with level, component, message, details
        """
        # Remove oldest if at max
        if len(self._notifications) >= self._max_notifications:
            oldest = self._notifications[0]
            oldest.close_notification()
        
        # Create notification
        notification = AlertNotification(alert_data, self)
        notification.closed.connect(lambda: self._on_notification_closed(notification))
        
        # Add to layout
        self._layout.insertWidget(0, notification)
        self._notifications.append(notification)
        
        # Update position
        self._update_position()
        
        # Show
        self.show()
    
    def _on_notification_closed(self, notification: AlertNotification):
        """Handle notification closed"""
        if notification in self._notifications:
            self._notifications.remove(notification)
        
        # Hide if no notifications
        if not self._notifications:
            self.hide()
    
    def _update_position(self):
        """Update widget position"""
        if not self.parent():
            return
        
        parent = self.parent()
        parent_rect = parent.geometry()
        
        # Position in top-right
        x = parent_rect.right() - self.width() - 20
        y = parent_rect.top() + 70
        
        self.move(x, y)
    
    def clear_all(self):
        """Clear all notifications"""
        for notification in list(self._notifications):
            notification.close_notification()


# Testing
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Alert Notification Test")
            self.resize(800, 600)
            
            # Create alert manager
            self.alert_manager = AlertNotificationManager(self)
            
            # Test buttons
            central = QWidget()
            layout = QVBoxLayout(central)
            
            btn_info = QPushButton("Show INFO Alert")
            btn_info.clicked.connect(lambda: self.show_test_alert('INFO'))
            layout.addWidget(btn_info)
            
            btn_warning = QPushButton("Show WARNING Alert")
            btn_warning.clicked.connect(lambda: self.show_test_alert('WARNING'))
            layout.addWidget(btn_warning)
            
            btn_error = QPushButton("Show ERROR Alert")
            btn_error.clicked.connect(lambda: self.show_test_alert('ERROR'))
            layout.addWidget(btn_error)
            
            btn_critical = QPushButton("Show CRITICAL Alert")
            btn_critical.clicked.connect(lambda: self.show_test_alert('CRITICAL'))
            layout.addWidget(btn_critical)
            
            self.setCentralWidget(central)
        
        def show_test_alert(self, level: str):
            alert = {
                'level': level.lower(),
                'component': 'TestComponent',
                'message': f'This is a {level} alert message',
                'details': 'Additional details about the alert'
            }
            self.alert_manager.show_alert(alert)
    
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
