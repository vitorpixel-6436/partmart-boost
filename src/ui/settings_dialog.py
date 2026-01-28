"""Settings dialog for PartMart Boost"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QSlider, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from localization import t, set_language, get_current_language
from core.config import get_config

class SettingsDialog(QDialog):
    """Settings dialog with language, ML, and other options"""
    
    settings_changed = pyqtSignal()  # Emitted when settings change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.setWindowTitle(t('settings_title'))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("⚙️ " + t('settings_title'))
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #E63946;
        """)
        layout.addWidget(title)
        
        # Language section
        lang_group = self._create_language_section()
        layout.addWidget(lang_group)
        
        # Performance section
        perf_group = self._create_performance_section()
        layout.addWidget(perf_group)
        
        # ML section
        ml_group = self._create_ml_section()
        layout.addWidget(ml_group)
        
        layout.addStretch()
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        save_btn = QPushButton(t('save'))
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(120)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #E63946;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #FF4757;
            }
        """)
        save_btn.clicked.connect(self._save_settings)
        buttons.addWidget(save_btn)
        
        cancel_btn = QPushButton(t('cancel'))
        cancel_btn.setFixedHeight(40)
        cancel_btn.setFixedWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #252525;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #353535;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
        # Dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #0D0D0D;
            }
            QLabel {
                color: #FFFFFF;
            }
            QGroupBox {
                border: 2px solid #252525;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                color: #FFFFFF;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
            }
            QComboBox {
                background: #1A1A1A;
                color: white;
                border: 2px solid #252525;
                border-radius: 8px;
                padding: 8px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #E63946;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1A1A1A;
                color: white;
                selection-background-color: #E63946;
            }
            QCheckBox {
                color: #FFFFFF;
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
            QSlider::groove:horizontal {
                height: 8px;
                background: #1A1A1A;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #E63946;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #FF4757;
            }
        """)
    
    def _create_language_section(self) -> QGroupBox:
        group = QGroupBox("🌍 " + t('language'))
        layout = QVBoxLayout()
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_label = QLabel(t('select_language') + ":")
        lang_layout.addWidget(lang_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("🔄 " + t('auto_detect'), "auto")
        self.language_combo.addItem("🇬🇧 English", "en")
        self.language_combo.addItem("🇷🇺 Русский", "ru")
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        
        layout.addLayout(lang_layout)
        
        # Info label
        info = QLabel("ℹ️ " + t('language_change_note'))
        info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        group.setLayout(layout)
        return group
    
    def _create_performance_section(self) -> QGroupBox:
        group = QGroupBox("⚡ " + t('performance'))
        layout = QVBoxLayout()
        
        # Update interval
        interval_layout = QVBoxLayout()
        interval_label = QLabel(t('update_interval') + ":")
        interval_layout.addWidget(interval_label)
        
        slider_layout = QHBoxLayout()
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setMinimum(1000)
        self.interval_slider.setMaximum(5000)
        self.interval_slider.setSingleStep(500)
        self.interval_slider.setValue(2000)
        self.interval_slider.valueChanged.connect(self._update_interval_label)
        slider_layout.addWidget(self.interval_slider)
        
        self.interval_value_label = QLabel("2000ms")
        self.interval_value_label.setStyleSheet("color: #E63946; font-weight: 600;")
        self.interval_value_label.setMinimumWidth(60)
        slider_layout.addWidget(self.interval_value_label)
        
        interval_layout.addLayout(slider_layout)
        
        interval_hint = QLabel(t('interval_hint'))
        interval_hint.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        interval_hint.setWordWrap(True)
        interval_layout.addWidget(interval_hint)
        
        layout.addLayout(interval_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_ml_section(self) -> QGroupBox:
        group = QGroupBox("🤖 " + t('ml_optimizer'))
        layout = QVBoxLayout()
        
        # ML enable checkbox
        self.ml_checkbox = QCheckBox(t('enable_ml'))
        layout.addWidget(self.ml_checkbox)
        
        # ML info
        ml_info = QLabel(
            "ℹ️ " + t('ml_info') + "\n" +
            "• " + t('ml_local') + "\n" +
            "• " + t('ml_lightweight') + "\n" +
            "• " + t('ml_learns')
        )
        ml_info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        ml_info.setWordWrap(True)
        layout.addWidget(ml_info)
        
        # Warning
        ml_warning = QLabel("⚠️ " + t('ml_beta_warning'))
        ml_warning.setStyleSheet("color: #FFA500; font-size: 11px; font-weight: 600;")
        ml_warning.setWordWrap(True)
        layout.addWidget(ml_warning)
        
        group.setLayout(layout)
        return group
    
    def _update_interval_label(self, value: int):
        self.interval_value_label.setText(f"{value}ms")
    
    def _load_current_settings(self):
        """Load current settings from config"""
        # Language
        current_lang = self.config.get("language", "auto")
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
        
        # Update interval
        interval = self.config.get_update_interval()
        self.interval_slider.setValue(interval)
        
        # ML optimizer
        ml_enabled = self.config.is_ml_enabled()
        self.ml_checkbox.setChecked(ml_enabled)
    
    def _save_settings(self):
        """Save settings to config"""
        # Check if language changed
        old_lang = self.config.get("language", "auto")
        new_lang = self.language_combo.currentData()
        lang_changed = (old_lang != new_lang)
        
        # Save language
        self.config.set_language(new_lang)
        
        # Save update interval
        interval = self.interval_slider.value()
        self.config.set_update_interval(interval)
        
        # Save ML preference
        ml_enabled = self.ml_checkbox.isChecked()
        self.config.enable_ml(ml_enabled)
        
        # Emit signal
        self.settings_changed.emit()
        
        # Show restart message if language changed
        if lang_changed:
            QMessageBox.information(
                self,
                t('language_changed_title'),
                t('language_changed_msg')
            )
            # Apply language immediately
            set_language(new_lang if new_lang != "auto" else self.config.get_language())
            # Close and signal to refresh UI
        
        self.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    from core.config import init_config
    from localization import init_localization
    
    app = QApplication(sys.argv)
    init_config()
    init_localization("en")
    
    dialog = SettingsDialog()
    dialog.exec()
