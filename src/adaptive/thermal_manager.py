#!/usr/bin/env python3
"""Thermal Manager

Version: 0.3.5d_package3.6a - BUGFIX: Oscillation + debouncing

Thermal management with debouncing and smoothing.
"""
import time
from typing import Optional, Deque
from collections import deque
from enum import Enum
from dataclasses import dataclass


class ThermalState(Enum):
    """Thermal state"""
    NORMAL = "normal"
    WARNING = "warning"
    THROTTLE = "throttle"
    CRITICAL = "critical"


@dataclass
class ThermalConfig:
    """Thermal configuration"""
    warning_temp: float = 80.0
    throttle_temp: float = 90.0
    critical_temp: float = 100.0
    hysteresis: float = 5.0
    cooldown_time: float = 2.0
    # MICRO-FIX #5: Add debouncing
    debounce_window: int = 5  # Number of readings to average
    min_state_duration: float = 1.0  # Minimum time in state


class ThermalManager:
    """Thermal Manager
    
    v0.3.5d_package3.6a - MICRO-FIX #5
    
    Thermal management with oscillation prevention.
    
    Fixes:
    - Rapid oscillation between states
    - Temperature reading smoothing
    - Debouncing for stability
    - Minimum state duration
    - Exponential moving average
    """
    
    def __init__(self, config: Optional[ThermalConfig] = None):
        """Initialize thermal manager"""
        self._config = config or ThermalConfig()
        self._state = ThermalState.NORMAL
        self._last_state_change: Optional[float] = None
        self._state_enter_time: Optional[float] = None
        self._current_temp = 0.0
        
        # MICRO-FIX #5: Temperature smoothing
        self._temp_history: Deque[float] = deque(
            maxlen=self._config.debounce_window
        )
        self._smoothed_temp = 0.0
        
        # MICRO-FIX #5: EMA for additional smoothing
        self._ema_alpha = 0.3  # Smoothing factor
        
        print(f"[ThermalManager v0.3.5d_package3.6a] Initialized")
    
    def update_temperature(self, temp: float):
        """Update temperature with smoothing
        
        Args:
            temp: Current temperature (°C)
        """
        # MICRO-FIX #5: Add to history
        self._temp_history.append(temp)
        
        # MICRO-FIX #5: Calculate smoothed temperature
        if len(self._temp_history) > 0:
            # Simple moving average
            self._smoothed_temp = sum(self._temp_history) / len(self._temp_history)
            
            # MICRO-FIX #5: Apply EMA on top
            if self._current_temp > 0:
                self._smoothed_temp = (
                    self._ema_alpha * self._smoothed_temp +
                    (1.0 - self._ema_alpha) * self._current_temp
                )
        
        self._current_temp = self._smoothed_temp
        
        # MICRO-FIX #5: Check minimum state duration
        if self._state_enter_time is not None:
            time_in_state = time.perf_counter() - self._state_enter_time
            if time_in_state < self._config.min_state_duration:
                return  # Stay in current state
        
        # Check cooldown
        if self._last_state_change is not None:
            elapsed = time.perf_counter() - self._last_state_change
            if elapsed < self._config.cooldown_time:
                return
        
        # Calculate new state with smoothed temp
        new_state = self._calculate_state(self._smoothed_temp)
        
        if new_state != self._state:
            print(f"[ThermalManager] State: {self._state.value} -> {new_state.value} ({self._smoothed_temp:.1f}°C)")
            self._state = new_state
            self._last_state_change = time.perf_counter()
            self._state_enter_time = time.perf_counter()
    
    def _calculate_state(self, temp: float) -> ThermalState:
        """Calculate thermal state with hysteresis"""
        hyst = self._config.hysteresis
        
        # Going up
        if temp >= self._config.critical_temp:
            return ThermalState.CRITICAL
        elif temp >= self._config.throttle_temp:
            return ThermalState.THROTTLE
        elif temp >= self._config.warning_temp:
            return ThermalState.WARNING
        
        # Going down with hysteresis
        if self._state == ThermalState.CRITICAL:
            if temp < self._config.critical_temp - hyst:
                return ThermalState.THROTTLE
            return ThermalState.CRITICAL
        
        elif self._state == ThermalState.THROTTLE:
            if temp < self._config.throttle_temp - hyst:
                return ThermalState.WARNING
            return ThermalState.THROTTLE
        
        elif self._state == ThermalState.WARNING:
            if temp < self._config.warning_temp - hyst:
                return ThermalState.NORMAL
            return ThermalState.WARNING
        
        return ThermalState.NORMAL
    
    def get_state(self) -> ThermalState:
        return self._state
    
    def is_throttling(self) -> bool:
        return self._state in (ThermalState.THROTTLE, ThermalState.CRITICAL)
    
    def get_throttle_factor(self) -> float:
        if self._state == ThermalState.NORMAL:
            return 1.0
        elif self._state == ThermalState.WARNING:
            return 0.9
        elif self._state == ThermalState.THROTTLE:
            temp_range = self._config.critical_temp - self._config.throttle_temp
            if temp_range <= 0:
                return 0.7
            temp_ratio = (self._current_temp - self._config.throttle_temp) / temp_range
            return 0.7 - (temp_ratio * 0.3)
        else:
            return 0.4


if __name__ == "__main__":
    print("="*60)
    print("ThermalManager v0.3.5d_package3.6a Test (MICRO-FIX #5)")
    print("="*60)
    print("\n✅ MICRO-FIX #5 Applied:")
    print("  - Temperature smoothing (SMA + EMA)")
    print("  - Debouncing (5-reading window)")
    print("  - Minimum state duration (1s)")
    print("  - Oscillation prevention")
    print("="*60)
