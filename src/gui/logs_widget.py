#!/usr/bin/env python3
"""Logs Widget

Version: 0.3.5d (package 3.9a, stage 4/4)

Application logs viewer with modern UI.

Package 3.9a Stage 4: Updated with custom widgets.
"""
import sys
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PyQt6.QtCore import Qt

# Import custom widgets
sys.path.insert(0, str(Path(__file__).parent))
try:
    from custom_widgets import ModernButton
except ImportError:
    print("[LogsWidget] Warning: Custom widgets not available, using standard")
    from PyQt6.QtWidgets import QPushButton as ModernButton


class LogsWidget(QWidget):
    """Logs Widget
    
    Real-time log viewer with modern UI.
    
    Package 3.9a Stage 4: Using custom widgets.
    """
    
    def __init__(self):
        super().__init__()
        self._create_ui()
    
    def _create_ui(self):
        """Create UI with custom widgets"""
        layout = QVBoxLayout(self)
        
        # Log text area with custom styling
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # STAGE 4: Enhanced text edit styling
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10pt;
            }
        """)
        
        layout.addWidget(self.log_text)
        
        # Buttons - STAGE 4: ModernButton
        buttons_layout = QHBoxLayout()
        
        export_btn = ModernButton("Export Logs", color="#0d7377")
        export_btn.clicked.connect(self._export_logs)
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        clear_btn = ModernButton("Clear Logs", color="#ff6b6b")  # Red
        clear_btn.clicked.connect(self._clear_logs)
        buttons_layout.addWidget(clear_btn)
        
        layout.addLayout(buttons_layout)
        
        # Add initial logs
        self.add_log("PartMart Boost v0.3.5d (Package 3.9a) started")
        self.add_log("All modules initialized")
        self.add_log("Custom UI components loaded")
        self.add_log("Monitoring active")
    
    def add_log(self, message: str, level: str = "INFO"):
        """Add log message with styling
        
        Package 3.9a Stage 4: Enhanced log formatting
        """
        timestamp = time.strftime("%H:%M:%S")
        
        # Color based on level
        color_map = {
            "INFO": "#e0e0e0",
            "SUCCESS": "#51cf66",
            "WARNING": "#ffd43b",
            "ERROR": "#ff6b6b",
            "DEBUG": "#a0a0a0",
        }
        
        color = color_map.get(level.upper(), "#e0e0e0")
        
        # Format message
        formatted = f'<span style="color: #0d7377;">[{timestamp}]</span> '
        formatted += f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
        formatted += f'<span style="color: {color};">{message}</span>'
        
        self.log_text.append(formatted)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _clear_logs(self):
        """Clear logs"""
        self.log_text.clear()
        self.add_log("Logs cleared", "WARNING")
    
    def _export_logs(self):
        """Export logs to file (placeholder)"""
        self.add_log("Log export not yet implemented", "WARNING")
        print("[LogsWidget] Export logs clicked")
