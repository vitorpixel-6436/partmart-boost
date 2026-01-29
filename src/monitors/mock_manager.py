#!/usr/bin/env python3
"""Mock Monitor Manager

Version: 0.3.5e (package 3.9a, stage 7.2/7.7)

Mock implementation of MonitorManager for testing.

Package 3.9a Stage 7.2: Mock manager for PerformanceMonitor.
"""
import random
import time


class MockMonitorManager:
    """Mock Monitor Manager
    
    Provides mock system metrics for testing.
    """
    
    def __init__(self):
        """Initialize mock manager"""
        self._start_time = time.time()
        self._base_fps = 60.0
        self._base_cpu = 50.0
        self._base_gpu = 60.0
        self._base_ram = 70.0
    
    def get_cpu_load(self) -> float:
        """Get mock CPU load"""
        return self._base_cpu + random.uniform(-10, 10)
    
    def get_gpu_load(self) -> float:
        """Get mock GPU load"""
        return self._base_gpu + random.uniform(-10, 10)
    
    def get_ram_percent(self) -> float:
        """Get mock RAM usage"""
        return self._base_ram + random.uniform(-5, 5)
    
    def get_cpu_temp(self) -> float:
        """Get mock CPU temperature"""
        return 65.0 + random.uniform(-5, 5)
    
    def get_gpu_temp(self) -> float:
        """Get mock GPU temperature"""
        return 70.0 + random.uniform(-5, 5)
    
    def get_fps(self) -> float:
        """Get mock FPS"""
        return self._base_fps + random.uniform(-5, 5)
    
    def get_frame_time(self) -> float:
        """Get mock frame time"""
        fps = self.get_fps()
        return (1000.0 / fps) if fps > 0 else 0.0
    
    def get_uptime(self) -> float:
        """Get uptime in seconds"""
        return time.time() - self._start_time
