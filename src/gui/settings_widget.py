#!/usr/bin/env python3
"""Settings Widget

Version: 0.4.0-alpha

Application settings.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QPushButton, QComboBox, QCheckBox,
    QScrollArea
)
from PyQt6.QtCore import Qt


class SettingsWidget(QWidget):
    """Settings Widget
    
    Application configuration.
    """
    
    def __init__(self):
        super().__init__()
        self._create_ui()
    
    def _create_ui(self):
        """Create UI"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Performance Settings
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QVBoxLayout(perf_group)
        
        # Quality preset
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality Preset:"))
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Performance",
            "Balanced",
            "Quality",
            "Ultra"
        ])
        self.quality_combo.setCurrentIndex(1)  # Balanced
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        
        perf_layout.addLayout(quality_layout)
        
        # Frame Generation
        self.framegen_check = QCheckBox("Enable Frame Generation (2x FPS)")
        perf_layout.addWidget(self.framegen_check)
        
        # Upscaling
        self.upscaling_check = QCheckBox("Enable Upscaling (FSR 4)")
        perf_layout.addWidget(self.upscaling_check)
        
        layout.addWidget(perf_group)
        
        # Thermal Settings
        thermal_group = QGroupBox("Thermal Settings")
        thermal_layout = QVBoxLayout(thermal_group)
        
        # Target temperature
        target_temp_layout = QHBoxLayout()
        target_temp_layout.addWidget(QLabel("Target Temperature:"))
        
        self.target_temp_combo = QComboBox()
        self.target_temp_combo.addItems([
            "75°C (Cool)",
            "80°C (Balanced)",
            "85°C (Performance)"
        ])
        self.target_temp_combo.setCurrentIndex(1)
        target_temp_layout.addWidget(self.target_temp_combo)
        target_temp_layout.addStretch()
        
        thermal_layout.addLayout(target_temp_layout)
        
        layout.addWidget(thermal_group)
        
        # Power Settings
        power_group = QGroupBox("Power Settings")
        power_layout = QVBoxLayout(power_group)
        
        # Power mode
        power_mode_layout = QHBoxLayout()
        power_mode_layout.addWidget(QLabel("Power Mode:"))
        
        self.power_mode_combo = QComboBox()
        self.power_mode_combo.addItems([
            "Performance",
            "Balanced",
            "Power Saver"
        ])
        self.power_mode_combo.setCurrentIndex(1)
        power_mode_layout.addWidget(self.power_mode_combo)
        power_mode_layout.addStretch()
        
        power_layout.addLayout(power_mode_layout)
        
        layout.addWidget(power_group)
        
        # Advanced Settings
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.vsync_check = QCheckBox("Enable V-Sync")
        advanced_layout.addWidget(self.vsync_check)
        
        self.hdr_check = QCheckBox("Enable HDR (if supported)")
        advanced_layout.addWidget(self.hdr_check)
        
        layout.addWidget(advanced_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(apply_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_settings)
        buttons_layout.addWidget(reset_btn)
        
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _apply_settings(self):
        """Apply settings"""
        quality = self.quality_combo.currentText()
        framegen = self.framegen_check.isChecked()
        upscaling = self.upscaling_check.isChecked()
        
        print(f"[Settings] Applied: Quality={quality}, FrameGen={framegen}, Upscaling={upscaling}")
    
    def _reset_settings(self):
        """Reset to defaults"""
        self.quality_combo.setCurrentIndex(1)  # Balanced
        self.framegen_check.setChecked(False)
        self.upscaling_check.setChecked(False)
        self.target_temp_combo.setCurrentIndex(1)  # 80°C
        self.power_mode_combo.setCurrentIndex(1)  # Balanced
        self.vsync_check.setChecked(False)
        self.hdr_check.setChecked(False)
        
        print("[Settings] Reset to defaults")
