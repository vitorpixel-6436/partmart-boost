#!/usr/bin/env python3
"""Performance Widget

Version: 0.4.0-alpha

Detailed performance information.
"""
import sys
import platform
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt

# Import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from adaptive.thermal_manager_advanced import ThermalManagerAdvanced
from adaptive.power_manager_advanced import PowerManagerAdvanced


class PerformanceWidget(QWidget):
    """Performance Widget
    
    Displays detailed system information.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.thermal_manager = ThermalManagerAdvanced()
        self.power_manager = PowerManagerAdvanced()
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create UI"""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # System Information
        sys_group = QGroupBox("System Information")
        sys_layout = QVBoxLayout(sys_group)
        
        self.os_label = QLabel(f"OS: {platform.system()} {platform.release()}")
        self.python_label = QLabel(f"Python: {platform.python_version()}")
        self.arch_label = QLabel(f"Architecture: {platform.machine()}")
        self.processor_label = QLabel(f"Processor: {platform.processor()}")
        
        sys_layout.addWidget(self.os_label)
        sys_layout.addWidget(self.python_label)
        sys_layout.addWidget(self.arch_label)
        sys_layout.addWidget(self.processor_label)
        
        layout.addWidget(sys_group)
        
        # Thermal Status
        thermal_group = QGroupBox("Thermal Status")
        thermal_layout = QVBoxLayout(thermal_group)
        
        self.thermal_state_label = QLabel("State: Normal")
        self.thermal_temp_label = QLabel("Temperature: 0°C")
        self.thermal_throttle_label = QLabel("Throttle Factor: 1.00")
        
        thermal_layout.addWidget(self.thermal_state_label)
        thermal_layout.addWidget(self.thermal_temp_label)
        thermal_layout.addWidget(self.thermal_throttle_label)
        
        layout.addWidget(thermal_group)
        
        # Power Status
        power_group = QGroupBox("Power Status")
        power_layout = QVBoxLayout(power_group)
        
        self.power_state_label = QLabel("State: Unknown")
        self.power_mode_label = QLabel("Mode: Balanced")
        
        power_layout.addWidget(self.power_state_label)
        power_layout.addWidget(self.power_mode_label)
        
        layout.addWidget(power_group)
        
        # Health Statistics
        health_group = QGroupBox("Health Statistics")
        health_layout = QVBoxLayout(health_group)
        
        self.thermal_health_label = QLabel("Thermal Health: ...")
        self.power_health_label = QLabel("Power Health: ...")
        
        health_layout.addWidget(self.thermal_health_label)
        health_layout.addWidget(self.power_health_label)
        
        layout.addWidget(health_group)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def update_data(self):
        """Update performance data"""
        # Update thermal
        self.thermal_manager.update_temperature(75.0)  # Mock temp
        
        thermal_state = self.thermal_manager.get_state()
        thermal_temp = self.thermal_manager.get_current_temp()
        thermal_factor = self.thermal_manager.get_throttle_factor()
        
        self.thermal_state_label.setText(f"State: {thermal_state.value.title()}")
        self.thermal_temp_label.setText(f"Temperature: {thermal_temp:.1f}°C")
        self.thermal_throttle_label.setText(f"Throttle Factor: {thermal_factor:.2f}")
        
        # Update power
        self.power_manager.update()
        
        power_state = self.power_manager.get_power_state()
        power_mode = self.power_manager.get_power_mode()
        
        self.power_state_label.setText(f"State: {power_state.value.replace('_', ' ').title()}")
        self.power_mode_label.setText(f"Mode: {power_mode.value.replace('_', ' ').title()}")
        
        # Health stats
        thermal_health = self.thermal_manager.get_health_stats()
        power_health = self.power_manager.get_health_stats()
        
        self.thermal_health_label.setText(
            f"Transitions: {thermal_health['transition_count']}, "
            f"Spikes Filtered: {thermal_health['spikes_filtered']}"
        )
        
        self.power_health_label.setText(
            f"State Changes: {power_health['state_changes']}, "
            f"Mode Changes: {power_health['mode_changes']}"
        )
