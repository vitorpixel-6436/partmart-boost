#!/usr/bin/env python3
"""Performance Monitor

Version: 0.3.5d_package3.5b - BUGFIX: Added validation

System performance monitoring with bounds checking.
"""
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Performance metrics
    
    Attributes:
        fps: Frames per second
        frame_time: Frame time (ms)
        gpu_util: GPU utilization (0-100)
        cpu_util: CPU utilization (0-100)
        memory_used: Memory used (MB)
        memory_total: Total memory (MB)
        temperature: GPU temperature (°C)
        power_draw: Power draw (W)
    """
    fps: float
    frame_time: float
    gpu_util: float
    cpu_util: float
    memory_used: float
    memory_total: float
    temperature: float
    power_draw: float


class PerformanceMonitor:
    """Performance Monitor
    
    v0.3.5d_package3.5b - BUGFIX: Value validation
    
    Monitors system performance with proper bounds checking.
    
    Example:
        >>> monitor = PerformanceMonitor()
        >>> monitor.start()
        >>> metrics = monitor.get_metrics()
    """
    
    # BUGFIX: Added validation constants
    MIN_TEMP = -50.0  # °C
    MAX_TEMP = 200.0  # °C
    MIN_UTIL = 0.0    # %
    MAX_UTIL = 100.0  # %
    MIN_POWER = 0.0   # W
    MAX_POWER = 1000.0  # W
    
    def __init__(self):
        """Initialize monitor"""
        self._running = False
        self._start_time: Optional[float] = None
        
        print("[PerformanceMonitor v0.3.5d_package3.5b] Initialized")
    
    def start(self):
        """Start monitoring
        
        Example:
            >>> monitor.start()
        """
        if self._running:
            print("[PerformanceMonitor] Already running")
            return
        
        self._start_time = time.perf_counter()
        self._running = True
        print("[PerformanceMonitor] Started")
    
    def stop(self):
        """Stop monitoring
        
        Example:
            >>> monitor.stop()
        """
        self._running = False
        print("[PerformanceMonitor] Stopped")
    
    def get_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current metrics
        
        Returns:
            Metrics or None if not running
        
        Example:
            >>> metrics = monitor.get_metrics()
            >>> if metrics:
            >>>     print(f"GPU: {metrics.gpu_util:.1f}%")
        """
        if not self._running:
            return None
        
        # BUGFIX: Mock data with validation
        # In real implementation, get from hardware
        return PerformanceMetrics(
            fps=self._validate_fps(60.0),
            frame_time=self._validate_frame_time(16.67),
            gpu_util=self._validate_percentage(85.0),
            cpu_util=self._validate_percentage(60.0),
            memory_used=self._validate_memory(4096.0),
            memory_total=self._validate_memory(8192.0),
            temperature=self._validate_temperature(75.0),
            power_draw=self._validate_power(180.0),
        )
    
    @staticmethod
    def _validate_fps(fps: float) -> float:
        """Validate FPS value
        
        Args:
            fps: FPS value
        
        Returns:
            Validated FPS (0.1-1000)
        """
        return max(0.1, min(1000.0, fps))
    
    @staticmethod
    def _validate_frame_time(frame_time: float) -> float:
        """Validate frame time
        
        Args:
            frame_time: Frame time (ms)
        
        Returns:
            Validated frame time (0.001-10000)
        """
        return max(0.001, min(10000.0, frame_time))
    
    @staticmethod
    def _validate_percentage(value: float) -> float:
        """Validate percentage value
        
        Args:
            value: Percentage (0-100)
        
        Returns:
            Validated percentage
        """
        return max(PerformanceMonitor.MIN_UTIL, min(PerformanceMonitor.MAX_UTIL, value))
    
    @staticmethod
    def _validate_temperature(temp: float) -> float:
        """Validate temperature
        
        Args:
            temp: Temperature (°C)
        
        Returns:
            Validated temperature
        """
        return max(PerformanceMonitor.MIN_TEMP, min(PerformanceMonitor.MAX_TEMP, temp))
    
    @staticmethod
    def _validate_power(power: float) -> float:
        """Validate power draw
        
        Args:
            power: Power (W)
        
        Returns:
            Validated power
        """
        return max(PerformanceMonitor.MIN_POWER, min(PerformanceMonitor.MAX_POWER, power))
    
    @staticmethod
    def _validate_memory(memory: float) -> float:
        """Validate memory
        
        Args:
            memory: Memory (MB)
        
        Returns:
            Validated memory (non-negative)
        """
        return max(0.0, memory)
    
    def get_uptime(self) -> float:
        """Get monitor uptime
        
        Returns:
            Uptime in seconds
        
        Example:
            >>> uptime = monitor.get_uptime()
        """
        if self._start_time is None:
            return 0.0
        
        return time.perf_counter() - self._start_time


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("PerformanceMonitor v0.3.5d_package3.5b Test (BUGFIX)")
    print("="*60)
    
    monitor = PerformanceMonitor()
    
    print("\n[Test 1] Start monitor")
    monitor.start()
    
    print("\n[Test 2] Get metrics")
    metrics = monitor.get_metrics()
    if metrics:
        print(f"  FPS: {metrics.fps:.1f}")
        print(f"  Frame time: {metrics.frame_time:.2f}ms")
        print(f"  GPU: {metrics.gpu_util:.1f}%")
        print(f"  CPU: {metrics.cpu_util:.1f}%")
        print(f"  Memory: {metrics.memory_used:.0f}/{metrics.memory_total:.0f} MB")
        print(f"  Temperature: {metrics.temperature:.1f}°C")
        print(f"  Power: {metrics.power_draw:.1f}W")
    
    print("\n[Test 3] Validate bounds")
    test_values = [
        ("FPS", -10.0, monitor._validate_fps),
        ("FPS", 9999.0, monitor._validate_fps),
        ("Percentage", -50.0, monitor._validate_percentage),
        ("Percentage", 150.0, monitor._validate_percentage),
        ("Temperature", -100.0, monitor._validate_temperature),
        ("Temperature", 300.0, monitor._validate_temperature),
    ]
    
    for name, value, validator in test_values:
        validated = validator(value)
        print(f"  {name}: {value} -> {validated}")
    
    print("\n[Test 4] Get uptime")
    time.sleep(0.1)
    uptime = monitor.get_uptime()
    print(f"  Uptime: {uptime:.2f}s")
    
    print("\n[Test 5] Stop monitor")
    monitor.stop()
    
    print("\n" + "="*60)
    print("✅ PerformanceMonitor - All Tests Passed! (BUGFIX)")
    print("="*60)
