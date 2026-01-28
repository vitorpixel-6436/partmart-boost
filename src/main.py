#!/usr/bin/env python3
"""
PartMart Boost - Main Entry Point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# Ensure imports work from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import PartMartMainWindow

def main():
    app = QApplication(sys.argv)
    
    # Global Font Setup
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = PartMartMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
