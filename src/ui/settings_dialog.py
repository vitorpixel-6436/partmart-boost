"""Settings dialog for user preferences"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QCheckBox, QGroupBox, QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt

import sys
import os
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from localization import t, get_current_language
from core.config import get_config

class SettingsDialog(QDialog):
    """Settings dialog with language, ML, and interval options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.setWindowTitle(t('settings'))
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #0D0D0D;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QGroupBox {
                color: #E63946;
                font-size: 16px;
                font-weight: 600;
                border: 2px solid #E63946;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QComboBox, QSpinBox {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #E63946;
                border-radius: 4px;
                padding: 5px;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #E63946;
                width: 10px;
                height: 10px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
            }
            QCheckBox {
                color: #A0A0A0;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #E63946;
                border-radius: 4px;
                background-color: #1A1A1A;
            }
            QCheckBox::indicator:checked {
                background-color: #E63946;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #1A1A1A;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #E63946;
                border: none;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QPushButton {
                background-color: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #FF4757;
            }
            QPushButton#cancel_btn {
                background-color: #1A1A1A;
                border: 1px solid #666666;
            }
            QPushButton#cancel_btn:hover {
                background-color: #252525;
            }
        """)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Language settings
        lang_group = QGroupBox(f"🌍 {t('language')}")
        lang_layout = QFormLayout()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🌐 Auto-detect", "auto")
        self.lang_combo.addItem("🇬🇧 English", "en")
        self.lang_combo.addItem("🇷🇺 Русский", "ru")
        
        lang_layout.addRow(t('select_language') + ":", self.lang_combo)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # Performance settings
        perf_group = QGroupBox(f"⚡ {t('performance')}")
        perf_layout = QVBoxLayout()
        
        # Update interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel(t('update_interval') + ":")
        interval_layout.addWidget(interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1000, 5000)
        self.interval_spin.setSingleStep(500)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setValue(2000)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        
        perf_layout.addLayout(interval_layout)
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        # ML Optimizer settings
        ml_group = QGroupBox(f"🤖 {t('ml_optimizer')} (Beta)")
        ml_layout = QVBoxLayout()
        
        self.ml_checkbox = QCheckBox(t('enable_ml'))
        ml_layout.addWidget(self.ml_checkbox)
        
        ml_warning = QLabel(t('ml_warning'))
        ml_warning.setStyleSheet("color: #FF8800; font-size: 12px;")
        ml_warning.setWordWrap(True)
        ml_layout.addWidget(ml_warning)
        
        ml_group.setLayout(ml_layout)
        layout.addWidget(ml_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(t('cancel'))
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton(t('save'))
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _load_settings(self):
        """Load current settings from config"""
        # Language
        current_lang = self.config.get('language', 'auto')
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == current_lang:
                self.lang_combo.setCurrentIndex(i)
                break
        
        # Update interval
        interval = self.config.get_update_interval()
        self.interval_spin.setValue(interval)
        
        # ML optimizer
        ml_enabled = self.config.is_ml_enabled()
        self.ml_checkbox.setChecked(ml_enabled)
    
    def _save_settings(self):
        """Save settings to config"""
        # Language
        new_lang = self.lang_combo.currentData()
        self.config.set_language(new_lang)
        
        # Update interval
        new_interval = self.interval_spin.value()
        self.config.set_update_interval(new_interval)
        
        # ML optimizer
        ml_enabled = self.ml_checkbox.isChecked()
        self.config.enable_ml(ml_enabled)
        
        self.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()
