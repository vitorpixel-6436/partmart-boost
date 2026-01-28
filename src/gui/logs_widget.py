#!/usr/bin/env python3
"""Logs Widget

Version: 0.4.0-alpha

Application logs viewer.
"""
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt


class LogsWidget(QWidget):
    """Logs Widget
    
    Real-time log viewer.
    """
    
    def __init__(self):
        super().__init__()
        self._create_ui()
    
    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout(self)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self._clear_logs)
        buttons_layout.addWidget(clear_btn)
        
        layout.addLayout(buttons_layout)
        
        # Add initial log
        self.add_log("PartMart Boost started")
        self.add_log("All modules initialized")
        self.add_log("Monitoring active")
    
    def add_log(self, message: str):
        """Add log message"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _clear_logs(self):
        """Clear logs"""
        self.log_text.clear()
        self.add_log("Logs cleared")
