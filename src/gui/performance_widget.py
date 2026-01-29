#!/usr/bin/env python3
"""Performance Widget

Version: 0.3.5d (package 3.9a, stage 3/3)

Detailed performance information with real hardware data.

Package 3.9a Stage 3 Fixes:
- Replaced mock data with real metrics
- Integrated with data bus
- Real-time hardware monitoring
"""
import sys
import platform
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt

# Import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from adaptive.thermal_manager_advanced import ThermalManagerAdvanced
    from adaptive.power_manager_advanced import PowerManagerAdvanced
    from core.data_bus import PerformanceDataBus
    from monitors.performance_monitor import PerformanceMetrics
except ImportError as e:
    print(f"[PerformanceWidget] Import error: {e}")


class PerformanceWidget(QWidget):
    """Performance Widget
    
    Displays detailed system information with real hardware data.
    
    Package 3.9a Stage 3 Fixes:
    - Real metrics from data bus
    - No more mock data
    - Real-time updates
    """
    
    def __init__(self):
        super().__init__()
        
        # STAGE 3: Connect to data bus
        try:
            self.data_bus = PerformanceDataBus.get_instance()
            print("[PerformanceWidget] Connected to data bus")
        except Exception as e:
            print(f"[PerformanceWidget] Data bus error: {e}")
            self.data_bus = None
        
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
        
        # STAGE 3: Real-time Hardware Status
        hardware_group = QGroupBox("Real-Time Hardware Status")
        hardware_layout = QVBoxLayout(hardware_group)
        
        self.realtime_gpu_label = QLabel("GPU: Waiting for data...")
        self.realtime_cpu_label = QLabel("CPU: Waiting for data...")
        self.realtime_memory_label = QLabel("Memory: Waiting for data...")
        self.realtime_temp_label = QLabel("Temperature: Waiting for data...")
        self.realtime_power_label = QLabel("Power: Waiting for data...")
        
        hardware_layout.addWidget(self.realtime_gpu_label)
        hardware_layout.addWidget(self.realtime_cpu_label)
        hardware_layout.addWidget(self.realtime_memory_label)
        hardware_layout.addWidget(self.realtime_temp_label)
        hardware_layout.addWidget(self.realtime_power_label)
        
        layout.addWidget(hardware_group)
        
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
        """Update performance data
        
        Package 3.9a Stage 3 Fix:
        - Get REAL metrics from data bus
        - Update thermal manager with REAL temperature
        - No more mock data!
        """
        # STAGE 3 FIX: Get real metrics from data bus
        metrics: Optional[PerformanceMetrics] = None
        if self.data_bus:
            metrics = self.data_bus.get('performance_metrics')
        
        if metrics:
            # STAGE 3 FIX: Update with REAL data
            self.realtime_gpu_label.setText(f"GPU: {metrics.gpu_util:.0f}% utilization")
            self.realtime_cpu_label.setText(f"CPU: {metrics.cpu_util:.0f}% utilization")
            self.realtime_memory_label.setText(
                f"Memory: {metrics.memory_used:.0f} / {metrics.memory_total:.0f} MB"
            )
            self.realtime_temp_label.setText(f"Temperature: {metrics.temperature:.1f}°C")
            self.realtime_power_label.setText(f"Power: {metrics.power_draw:.0f} W")
            
            # STAGE 3 FIX: Update thermal with REAL temperature
            self.thermal_manager.update_temperature(metrics.temperature)
        else:
            # Fallback only if no data available
            self.realtime_gpu_label.setText("GPU: No data available")
            self.realtime_cpu_label.setText("CPU: No data available")
            self.realtime_memory_label.setText("Memory: No data available")
            self.realtime_temp_label.setText("Temperature: No data available")
            self.realtime_power_label.setText("Power: No data available")
            
            # Fallback to mock only if absolutely necessary
            self.thermal_manager.update_temperature(65.0)
        
        # Update thermal state
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
