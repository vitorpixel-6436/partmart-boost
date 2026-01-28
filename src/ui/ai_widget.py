from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, 
                             QHBoxLayout, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class AIRecItem(QFrame):
    """
    Individual AI recommendation card.
    """
    def __init__(self, component, action, impact, reason):
        super().__init__()
        self.setObjectName("AIRecItem")
        self.setStyleSheet("""
            #AIRecItem {
                background-color: #2a475e;
                border: 1px solid #66C0F4;
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title_layout = QHBoxLayout()
        comp_lbl = QLabel(f"[{component}]")
        comp_lbl.setStyleSheet("color: #66C0F4; font-weight: bold;")
        action_lbl = QLabel(action)
        action_lbl.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(comp_lbl)
        title_layout.addWidget(action_lbl)
        title_layout.addStretch()
        
        impact_lbl = QLabel(impact)
        impact_lbl.setStyleSheet("color: #5DA130; font-size: 11px;")
        
        reason_lbl = QLabel(reason)
        reason_lbl.setWordWrap(True)
        reason_lbl.setStyleSheet("color: #8f98a0; font-size: 10px; font-style: italic;")
        
        layout.addLayout(title_layout)
        layout.addWidget(impact_lbl)
        layout.addWidget(reason_lbl)

class PartMartAIWidget(QWidget):
    """
    Main AI Widget displaying predictions and recommendations.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("🤖 AI OPTIMIZER INSIGHTS")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #66C0F4; margin-bottom: 5px;")
        self.layout.addWidget(header)
        
        # Prediction Box
        self.pred_box = QFrame()
        self.pred_box.setStyleSheet("background-color: #1b2838; border-radius: 8px; padding: 10px;")
        pred_layout = QVBoxLayout(self.pred_box)
        
        self.fps_gain_lbl = QLabel("PREDICTED FPS GAIN: --")
        self.fps_gain_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.fps_gain_lbl.setStyleSheet("color: #5DA130;")
        
        self.confidence_lbl = QLabel("AI Confidence: 0%")
        self.confidence_lbl.setStyleSheet("color: #8f98a0; font-size: 10px;")
        
        pred_layout.addWidget(self.fps_gain_lbl)
        pred_layout.addWidget(self.confidence_lbl)
        self.layout.addWidget(self.pred_box)
        
        # Recommendations Area
        rec_title = QLabel("RECOMMENDED ACTIONS:")
        rec_title.setStyleSheet("color: #c7d5e0; margin-top: 10px; font-size: 11px;")
        self.layout.addWidget(rec_title)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.rec_layout = QVBoxLayout(self.scroll_content)
        self.rec_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)

    def update_insights(self, ai_report):
        """
        Updates the UI with data from the AI Optimizer report.
        """
        self.fps_gain_lbl.setText(f"PREDICTED FPS GAIN: {ai_report['predicted_fps_gain']}")
        self.confidence_lbl.setText(f"AI Confidence: {int(ai_report['confidence']*100)}%")
        
        # Clear old recommendations
        for i in reversed(range(self.rec_layout.count())): 
            self.rec_layout.itemAt(i).widget().setParent(None)
            
        for rec in ai_report['recommendations']:
            item = AIRecItem(rec['component'], rec['action'], rec['impact'], rec['reason'])
            self.rec_layout.addWidget(item)
            
        if not ai_report['recommendations']:
            none_lbl = QLabel("No optimizations needed. System is peak.")
            none_lbl.setStyleSheet("color: #8f98a0; font-style: italic;")
            self.rec_layout.addWidget(none_lbl)
