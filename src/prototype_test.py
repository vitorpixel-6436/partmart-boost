import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QProgressBar, 
                             QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

class BoostWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str, str)
    finished = pyqtSignal()

    def run(self):
        steps = [
            ("Initializing AI Engine...", "#66C0F4"),
            ("Scanning System Hardware...", "white"),
            ("Analyzing GPU Workload...", "white"),
            ("Detecting RAM Bottlenecks...", "white"),
            ("Applying Optimization Profile: 'GAMING_MAX'...", "#5DA130"),
            ("Cleaning Standby Memory...", "white"),
            ("Optimizing Power Delivery...", "white"),
            ("Boosting FPS Performance...", "#E63946"),
            ("Finalizing Tweaks...", "white")
        ]
        
        for i, (msg, color) in enumerate(steps):
            self.log.emit(msg, color)
            for p in range(i * 11, (i + 1) * 11):
                self.progress.emit(p)
                time.sleep(0.05)
        
        self.progress.emit(100)
        self.log.emit("
🚀 BOOST COMPLETE! SYSTEM OPTIMIZED.", "#5DA130")
        self.finished.emit()

class QuickTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PartMart Boost - MVP Prototype")
        self.setFixedSize(700, 500)
        self.setStyleSheet("""
            QMainWindow { background-color: #171a21; }
            QLabel { color: #c7d5e0; font-family: 'Segoe UI'; }
            QPushButton { 
                background-color: #5DA130; 
                color: white; 
                border-radius: 4px; 
                padding: 10px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #70c43a; }
            QProgressBar { 
                border: 1px solid #3d4450; 
                border-radius: 5px; 
                text-align: center; 
                color: white;
                background-color: #2a475e;
            }
            QProgressBar::chunk { background-color: #66C0F4; }
            QTextEdit { 
                background-color: #0d1117; 
                color: #8f98a0; 
                border: 1px solid #3d4450; 
                font-family: 'Consolas'; 
                font-size: 12px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QLabel("🐉 PARTMART BOOST - PROTOTYPE v0.1")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #66C0F4; margin-bottom: 10px;")
        layout.addWidget(header)

        # Stats Area
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: #1b2838; border-radius: 8px; padding: 15px;")
        stats_layout = QHBoxLayout(stats_frame)
        
        self.gpu_label = QLabel("GPU: RTX 2060 SUPER | 54°C")
        self.ram_label = QLabel("RAM: 12.4GB / 32GB")
        self.fps_label = QLabel("PREDICTED FPS: +45%")
        
        for lbl in [self.gpu_label, self.ram_label, self.fps_label]:
            lbl.setFont(QFont("Segoe UI", 10))
            stats_layout.addWidget(lbl)
        
        layout.addWidget(stats_frame)

        # Terminal/Log
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.append("<span style='color: #8f98a0;'>[SYSTEM] Ready for optimization...</span>")
        layout.addWidget(self.terminal)

        # Progress
        self.pbar = QProgressBar()
        layout.addWidget(self.pbar)

        # Action Button
        self.btn = QPushButton("🚀 START QUICK BOOST")
        self.btn.clicked.connect(self.start_boost)
        layout.addWidget(self.btn)

    def _log(self, text, color="white"):
        self.terminal.append(f"<span style='color: {color};'>{text}</span>")

    def start_boost(self):
        self.btn.setEnabled(False)
        self.btn.setText("OPTIMIZING...")
        self.worker = BoostWorker()
        self.worker.progress.connect(self.pbar.setValue)
        self.worker.log.connect(self._log)
        self.worker.finished.connect(lambda: self.btn.setText("SYSTEM BOOSTED!"))
        
        self._log("
--- STARTING AI ANALYSIS ---", "#F79F1A")
        self.worker.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QuickTestWindow()
    window.show()
    sys.exit(app.exec())
