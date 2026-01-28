"""Settings dialog for PartMart Boost"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QSlider, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import os

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from localization import t, set_language
from core.config import get_config

class SettingsDialog(QDialog):
    """Settings dialog with language, ML, and other preferences"""
    
    # Signal emitted when settings change
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.setWindowTitle(t('settings_title'))
        self.setModal(True)
        self.setFixedSize(500, 600)
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Setup UI layout"""
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
                border: 2px solid #252525;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
            }
            QComboBox, QSlider {
                background: #1A1A1A;
                color: #FFFFFF;
                border: 2px solid #252525;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #E63946;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
                margin-right: 10px;
            }
            QCheckBox {
                color: #FFFFFF;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #252525;
                border-radius: 4px;
                background: #1A1A1A;
            }
            QCheckBox::indicator:checked {
                background: #E63946;
                border-color: #E63946;
            }
            QPushButton {
                background: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #FF4757;
            }
            QPushButton#cancel_btn {
                background: #252525;
                color: #A0A0A0;
            }
            QPushButton#cancel_btn:hover {
                background: #333333;
                color: #FFFFFF;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Language group
        lang_group = self._create_language_group()
        layout.addWidget(lang_group)
        
        # ML Optimizer group
        ml_group = self._create_ml_group()
        layout.addWidget(ml_group)
        
        # Performance group
        perf_group = self._create_performance_group()
        layout.addWidget(perf_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.save_btn = QPushButton(t('save'))
        self.save_btn.clicked.connect(self._save_settings)
        
        self.cancel_btn = QPushButton(t('cancel'))
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def _create_language_group(self) -> QGroupBox:
        """Create language selection group"""
        group = QGroupBox(t('language'))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Language dropdown
        lang_layout = QHBoxLayout()
        lang_label = QLabel(t('select_language'))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("🌍 " + t('auto_detect'), "auto")
        self.lang_combo.addItem("🇷🇺 Русский", "ru")
        self.lang_combo.addItem("🇬🇧 English", "en")
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_layout)
        
        # Info label
        info_label = QLabel(t('language_restart_required'))
        info_label.setStyleSheet("color: #666666; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
    
    def _create_ml_group(self) -> QGroupBox:
        """Create ML optimizer group"""
        group = QGroupBox(t('ml_optimizer'))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # ML toggle
        self.ml_checkbox = QCheckBox(t('enable_ml'))
        layout.addWidget(self.ml_checkbox)
        
        # Beta warning
        beta_label = QLabel("⚠️ " + t('ml_beta_warning'))
        beta_label.setStyleSheet("color: #FFA500; font-size: 12px;")
        beta_label.setWordWrap(True)
        layout.addWidget(beta_label)
        
        # Info labels
        info_text = t('ml_info')
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
    
    def _create_performance_group(self) -> QGroupBox:
        """Create performance settings group"""
        group = QGroupBox(t('performance'))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Update interval
        interval_layout = QVBoxLayout()
        interval_label = QLabel(t('update_interval'))
        layout.addWidget(interval_label)
        
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(1000)
        self.interval_slider.setMaximum(5000)
        self.interval_slider.setSingleStep(500)
        self.interval_slider.setTickInterval(1000)
        self.interval_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.interval_slider.valueChanged.connect(self._update_interval_label)
        
        self.interval_value_label = QLabel("2000ms")
        self.interval_value_label.setStyleSheet("color: #E63946; font-weight: 600;")
        self.interval_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.interval_slider)
        layout.addWidget(self.interval_value_label)
        
        # Info
        info = QLabel(t('update_interval_info'))
        info.setStyleSheet("color: #666666; font-size: 11px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def _update_interval_label(self, value: int):
        """Update interval display label"""
        self.interval_value_label.setText(f"{value}ms")
    
    def _load_current_settings(self):
        """Load current settings from config"""
        # Language
        current_lang = self.config.get("language", "auto")
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == current_lang:
                self.lang_combo.setCurrentIndex(i)
                break
        
        # ML
        self.ml_checkbox.setChecked(self.config.is_ml_enabled())
        
        # Update interval
        interval = self.config.get_update_interval()
        self.interval_slider.setValue(interval)
        self._update_interval_label(interval)
    
    def _save_settings(self):
        """Save settings to config"""
        # Language
        selected_lang = self.lang_combo.currentData()
        old_lang = self.config.get("language", "auto")
        self.config.set_language(selected_lang)
        
        # ML
        self.config.enable_ml(self.ml_checkbox.isChecked())
        
        # Update interval
        self.config.set_update_interval(self.interval_slider.value())
        
        # Emit signal
        self.settings_changed.emit()
        
        # Show restart message if language changed
        if selected_lang != old_lang:
            QMessageBox.information(
                self,
                t('restart_required'),
                t('restart_required_message'),
                QMessageBox.StandardButton.Ok
            )
        
        self.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()
