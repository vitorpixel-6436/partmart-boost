#!/usr/bin/env python3
"""Settings Widget

Version: 0.3.5d (package 3.9a, stage 4/4)

Application settings with modern UI components.

Package 3.9a Stage 4: Updated with custom widgets.
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt

# Import custom widgets
sys.path.insert(0, str(Path(__file__).parent))
try:
    from custom_widgets import ModernButton, ToggleSwitch, ModernComboBox, ModernSlider
except ImportError:
    print("[SettingsWidget] Warning: Custom widgets not available, using standard")
    from PyQt6.QtWidgets import QPushButton as ModernButton
    from PyQt6.QtWidgets import QCheckBox as ToggleSwitch
    from PyQt6.QtWidgets import QComboBox as ModernComboBox
    from PyQt6.QtWidgets import QSlider as ModernSlider


class SettingsWidget(QWidget):
    """Settings Widget
    
    Application configuration with modern UI.
    
    Package 3.9a Stage 4: Using custom widgets.
    """
    
    def __init__(self):
        super().__init__()
        self._create_ui()
    
    def _create_ui(self):
        """Create UI with custom widgets"""
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
        quality_label = QLabel("Quality Preset:")
        quality_label.setStyleSheet("font-weight: bold;")
        quality_layout.addWidget(quality_label)
        
        # STAGE 4: ModernComboBox
        self.quality_combo = ModernComboBox()
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
        
        # Frame Generation - STAGE 4: ToggleSwitch
        framegen_layout = QHBoxLayout()
        self.framegen_check = ToggleSwitch()
        self.framegen_check.setText("Enable Frame Generation (2x FPS)")
        framegen_layout.addWidget(self.framegen_check)
        framegen_layout.addStretch()
        perf_layout.addLayout(framegen_layout)
        
        # Upscaling - STAGE 4: ToggleSwitch
        upscaling_layout = QHBoxLayout()
        self.upscaling_check = ToggleSwitch()
        self.upscaling_check.setText("Enable Upscaling (FSR 4)")
        upscaling_layout.addWidget(self.upscaling_check)
        upscaling_layout.addStretch()
        perf_layout.addLayout(upscaling_layout)
        
        layout.addWidget(perf_group)
        
        # Thermal Settings
        thermal_group = QGroupBox("Thermal Settings")
        thermal_layout = QVBoxLayout(thermal_group)
        
        # Target temperature
        target_temp_layout = QHBoxLayout()
        target_temp_label = QLabel("Target Temperature:")
        target_temp_label.setStyleSheet("font-weight: bold;")
        target_temp_layout.addWidget(target_temp_label)
        
        # STAGE 4: ModernComboBox
        self.target_temp_combo = ModernComboBox()
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
        power_mode_label = QLabel("Power Mode:")
        power_mode_label.setStyleSheet("font-weight: bold;")
        power_mode_layout.addWidget(power_mode_label)
        
        # STAGE 4: ModernComboBox
        self.power_mode_combo = ModernComboBox()
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
        
        # V-Sync - STAGE 4: ToggleSwitch
        vsync_layout = QHBoxLayout()
        self.vsync_check = ToggleSwitch()
        self.vsync_check.setText("Enable V-Sync")
        vsync_layout.addWidget(self.vsync_check)
        vsync_layout.addStretch()
        advanced_layout.addLayout(vsync_layout)
        
        # HDR - STAGE 4: ToggleSwitch
        hdr_layout = QHBoxLayout()
        self.hdr_check = ToggleSwitch()
        self.hdr_check.setText("Enable HDR (if supported)")
        hdr_layout.addWidget(self.hdr_check)
        hdr_layout.addStretch()
        advanced_layout.addLayout(hdr_layout)
        
        layout.addWidget(advanced_group)
        
        # Buttons - STAGE 4: ModernButton
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        apply_btn = ModernButton("Apply Settings", color="#51cf66")  # Green
        apply_btn.clicked.connect(self._apply_settings)
        buttons_layout.addWidget(apply_btn)
        
        reset_btn = ModernButton("Reset to Defaults", color="#ff6b6b")  # Red
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
