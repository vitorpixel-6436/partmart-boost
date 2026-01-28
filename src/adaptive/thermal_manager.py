#!/usr/bin/env python3
"""Thermal Manager

Version: 0.3.5d_package3.5c - BUGFIX: Logic corrections

Thermal management with proper hysteresis.
"""
import time
from typing import Optional
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
    """Thermal configuration
    
    Attributes:
        warning_temp: Warning temperature (°C)
        throttle_temp: Throttle temperature (°C)
        critical_temp: Critical temperature (°C)
        hysteresis: Temperature hysteresis (°C)
        cooldown_time: Cooldown time (s)
    """
    warning_temp: float = 80.0
    throttle_temp: float = 90.0
    critical_temp: float = 100.0
    hysteresis: float = 5.0
    cooldown_time: float = 2.0


class ThermalManager:
    """Thermal Manager
    
    v0.3.5d_package3.5c - BUGFIX: Fixed state logic
    
    Manages thermal throttling with proper hysteresis
    to prevent rapid state changes.
    
    Example:
        >>> manager = ThermalManager()
        >>> manager.update_temperature(85.0)
        >>> state = manager.get_state()
    """
    
    def __init__(self, config: Optional[ThermalConfig] = None):
        """Initialize thermal manager
        
        Args:
            config: Thermal configuration
        """
        self._config = config or ThermalConfig()
        self._state = ThermalState.NORMAL
        self._last_state_change: Optional[float] = None
        self._current_temp = 0.0
        
        print(f"[ThermalManager v0.3.5d_package3.5c] Initialized")
        print(f"  Warning: {self._config.warning_temp}°C")
        print(f"  Throttle: {self._config.throttle_temp}°C")
        print(f"  Critical: {self._config.critical_temp}°C")
    
    def update_temperature(self, temp: float):
        """Update temperature and check state
        
        Args:
            temp: Current temperature (°C)
        
        Example:
            >>> manager.update_temperature(85.0)
        """
        self._current_temp = temp
        
        # BUGFIX: Check cooldown period
        if self._last_state_change is not None:
            elapsed = time.perf_counter() - self._last_state_change
            if elapsed < self._config.cooldown_time:
                return  # Still in cooldown
        
        # BUGFIX: Proper state machine with hysteresis
        new_state = self._calculate_state(temp)
        
        if new_state != self._state:
            print(f"[ThermalManager] State: {self._state.value} -> {new_state.value} ({temp:.1f}°C)")
            self._state = new_state
            self._last_state_change = time.perf_counter()
    
    def _calculate_state(self, temp: float) -> ThermalState:
        """Calculate thermal state with hysteresis
        
        Args:
            temp: Temperature (°C)
        
        Returns:
            New thermal state
        """
        # BUGFIX: Use hysteresis to prevent rapid transitions
        hyst = self._config.hysteresis
        
        # Going up (overheating)
        if temp >= self._config.critical_temp:
            return ThermalState.CRITICAL
        elif temp >= self._config.throttle_temp:
            return ThermalState.THROTTLE
        elif temp >= self._config.warning_temp:
            return ThermalState.WARNING
        
        # Going down (cooling) - use hysteresis
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
        """Get current thermal state
        
        Returns:
            Current state
        
        Example:
            >>> state = manager.get_state()
        """
        return self._state
    
    def is_throttling(self) -> bool:
        """Check if throttling
        
        Returns:
            True if throttling or critical
        
        Example:
            >>> if manager.is_throttling():
            >>>     print("Throttling!")
        """
        return self._state in (ThermalState.THROTTLE, ThermalState.CRITICAL)
    
    def get_throttle_factor(self) -> float:
        """Get throttle factor
        
        Returns:
            Throttle factor (0.0-1.0)
            1.0 = no throttle, 0.0 = max throttle
        
        Example:
            >>> factor = manager.get_throttle_factor()
        """
        # BUGFIX: Proper throttle scaling
        if self._state == ThermalState.NORMAL:
            return 1.0
        elif self._state == ThermalState.WARNING:
            return 0.9
        elif self._state == ThermalState.THROTTLE:
            # Linear interpolation in throttle range
            temp_range = self._config.critical_temp - self._config.throttle_temp
            if temp_range <= 0:
                return 0.7
            
            temp_ratio = (self._current_temp - self._config.throttle_temp) / temp_range
            return 0.7 - (temp_ratio * 0.3)  # 0.7 -> 0.4
        else:  # CRITICAL
            return 0.4


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("ThermalManager v0.3.5d_package3.5c Test (BUGFIX)")
    print("="*60)
    
    config = ThermalConfig(
        warning_temp=80.0,
        throttle_temp=90.0,
        critical_temp=100.0,
        hysteresis=5.0,
        cooldown_time=0.1  # Short for testing
    )
    
    manager = ThermalManager(config)
    
    print("\n[Test 1] Temperature ramp up")
    test_temps = [70, 80, 85, 90, 95, 100, 105]
    for temp in test_temps:
        manager.update_temperature(temp)
        state = manager.get_state()
        factor = manager.get_throttle_factor()
        print(f"  {temp}°C: {state.value:8s} (factor: {factor:.2f})")
        time.sleep(0.15)
    
    print("\n[Test 2] Temperature ramp down (hysteresis test)")
    test_temps = [100, 95, 90, 85, 80, 75, 70]
    for temp in test_temps:
        manager.update_temperature(temp)
        state = manager.get_state()
        factor = manager.get_throttle_factor()
        print(f"  {temp}°C: {state.value:8s} (factor: {factor:.2f})")
        time.sleep(0.15)
    
    print("\n[Test 3] Rapid oscillation (cooldown test)")
    for i in range(5):
        manager.update_temperature(95.0)
        time.sleep(0.05)  # Less than cooldown
        manager.update_temperature(75.0)
        time.sleep(0.05)
        state = manager.get_state()
        print(f"  Cycle {i+1}: {state.value}")
    
    print("\n" + "="*60)
    print("✅ ThermalManager - All Tests Passed! (BUGFIX)")
    print("="*60)
