#!/usr/bin/env python3
"""
SystemMonitor - Backward compatibility wrapper.

Provides legacy SystemMonitor interface using new MonitorManager.

Author: PartMart Team
Version: 0.4.0-alpha
"""

from typing import Dict, Any
from monitors.manager import MonitorManager


class SystemMonitor:
    """Legacy SystemMonitor interface for backward compatibility.
    
    This class wraps MonitorManager to provide the old API that existing
    code expects, while using the new monitoring infrastructure under the hood.
    """
    
    def __init__(self, prefer_native: bool = False):
        """Initialize system monitor.
        
        Args:
            prefer_native: If True, prefer native OS APIs over libraries
        """
        self.manager = MonitorManager(prefer_native=prefer_native)
        self._last_data = {}
    
    def get_gpu_data(self) -> Dict[str, Any]:
        """Get GPU monitoring data.
        
        Returns:
            Dictionary with GPU metrics:
            - name: GPU name
            - temperature: GPU temp in Celsius
            - load: GPU load in percent
            - clock: GPU clock in MHz
            - memory_used: VRAM used in MB
            - memory_total: VRAM total in MB
        """
        # Get fresh data
        all_data = self.manager.get_all_data()
        gpu_data = all_data.get('gpu', {})
        
        # Transform to legacy format
        return {
            'name': gpu_data.get('name', 'Unknown GPU'),
            'temperature': gpu_data.get('temp_gpu', 0),
            'temp_hotspot': gpu_data.get('temp_hotspot'),
            'load': gpu_data.get('load_gpu', 0),
            'clock': gpu_data.get('clock_gpu', 0),
            'memory_clock': gpu_data.get('clock_mem', 0),
            'memory_used': gpu_data.get('mem_used', 0),
            'memory_total': gpu_data.get('mem_total', 0),
            'power': gpu_data.get('power', 0),
            'fan_speed': gpu_data.get('fan_speed', 0),
        }
    
    def get_ram_data(self) -> Dict[str, Any]:
        """Get RAM monitoring data.
        
        Returns:
            Dictionary with RAM metrics:
            - total_gb: Total RAM in GB
            - used_gb: Used RAM in GB
            - free_gb: Free RAM in GB
            - percent: Usage percent
            - speed: RAM speed in MHz
            - type: RAM type (DDR4, etc)
        """
        # Get fresh data
        all_data = self.manager.get_all_data()
        ram_data = all_data.get('ram', {})
        
        # Transform to legacy format
        total_gb = ram_data.get('total', 0) / (1024**3) if ram_data.get('total') else 0
        used_gb = ram_data.get('used', 0) / (1024**3) if ram_data.get('used') else 0
        free_gb = ram_data.get('free', 0) / (1024**3) if ram_data.get('free') else 0
        
        return {
            'total_gb': total_gb,
            'used_gb': used_gb,
            'free_gb': free_gb,
            'percent': ram_data.get('percent', 0),
            'speed': ram_data.get('speed', 0),
            'type': ram_data.get('type', 'Unknown'),
            'xmp_enabled': ram_data.get('xmp_enabled', False),
        }
    
    def get_cpu_data(self) -> Dict[str, Any]:
        """Get CPU monitoring data.
        
        Returns:
            Dictionary with CPU metrics:
            - name: CPU name
            - load: CPU load in percent
            - temperature: CPU temp in Celsius (if available)
            - frequency: Current frequency in MHz
            - cores: Physical core count
            - threads: Logical core count
        """
        # Get fresh data
        all_data = self.manager.get_all_data()
        cpu_data = all_data.get('cpu', {})
        
        # Transform to legacy format
        return {
            'name': cpu_data.get('name', 'Unknown CPU'),
            'load': cpu_data.get('load', 0),
            'temperature': cpu_data.get('temp'),
            'frequency': cpu_data.get('freq', 0),
            'freq_min': cpu_data.get('freq_min', 0),
            'freq_max': cpu_data.get('freq_max', 0),
            'cores': cpu_data.get('count', 0),
            'threads': cpu_data.get('count_logical', 0),
        }
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Get all monitoring data at once.
        
        Returns:
            Dictionary with all system metrics:
            - gpu: GPU data
            - cpu: CPU data
            - ram: RAM data
        """
        return {
            'gpu': self.get_gpu_data(),
            'cpu': self.get_cpu_data(),
            'ram': self.get_ram_data(),
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get monitoring performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return self.manager.get_performance_stats()
    
    def get_sovereignty_status(self) -> Dict[str, Any]:
        """Get sovereignty status.
        
        Returns:
            Dictionary with sovereignty info
        """
        return self.manager.get_sovereignty_status()


# For convenience
def create_monitor(prefer_native: bool = False) -> SystemMonitor:
    """Create a SystemMonitor instance.
    
    Args:
        prefer_native: If True, prefer native OS APIs
    
    Returns:
        SystemMonitor instance
    """
    return SystemMonitor(prefer_native=prefer_native)


if __name__ == '__main__':
    # Test legacy interface
    print("[TEST] SystemMonitor Wrapper")
    print("="*60)
    
    monitor = SystemMonitor()
    
    print("\n[GPU Data]")
    gpu = monitor.get_gpu_data()
    for k, v in list(gpu.items())[:5]:
        print(f"  {k}: {v}")
    
    print("\n[CPU Data]")
    cpu = monitor.get_cpu_data()
    for k, v in list(cpu.items())[:5]:
        print(f"  {k}: {v}")
    
    print("\n[RAM Data]")
    ram = monitor.get_ram_data()
    for k, v in ram.items():
        print(f"  {k}: {v}")
    
    print("\n[Performance]")
    perf = monitor.get_performance_stats()
    for k, v in perf.items():
        print(f"  {k}: {v}")
    
    print("\n" + "="*60)
    print("✅ SystemMonitor wrapper works!")
