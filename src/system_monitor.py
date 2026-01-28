#!/usr/bin/env python3
"""SystemMonitor - Backward compatibility wrapper.

Provides legacy SystemMonitor interface using new MonitorManager.

Author: PartMart Team
Version: 0.3.5b
"""

from typing import Dict, Any
from monitors.manager import MonitorManager
import traceback


class SystemMonitor:
    """Legacy SystemMonitor interface for backward compatibility.
    
    This class wraps MonitorManager to provide the old API that existing
    code expects, while using the new monitoring infrastructure under the hood.
    """
    
    def __init__(self, prefer_native: bool = False, debug: bool = True):
        """Initialize system monitor.
        
        Args:
            prefer_native: If True, prefer native OS APIs over libraries
            debug: Enable debug output
        """
        self.manager = MonitorManager(prefer_native=prefer_native)
        self._last_data = {}
        self._debug = debug
        
        print(f"[SystemMonitor] Initialized (debug={'ON' if debug else 'OFF'})")
    
    def get_gpu_data(self) -> Dict[str, Any]:
        """Get GPU monitoring data.
        
        Returns:
            Dictionary with GPU metrics
        """
        try:
            # Get fresh data
            all_data = self.manager.get_all_data()
            gpu_raw = all_data.get('gpu', {})
            
            if self._debug:
                print(f"[DEBUG] Raw GPU data keys: {list(gpu_raw.keys())}")
                print(f"[DEBUG] GPU name: {gpu_raw.get('name')}")
            
            # Map keys from various possible sources
            result = {
                'name': gpu_raw.get('name', 'Unknown GPU'),
                'temperature': (
                    gpu_raw.get('temperature') or 
                    gpu_raw.get('temp_gpu') or 
                    gpu_raw.get('temp_hotspot') or 
                    0
                ),
                'temp_hotspot': gpu_raw.get('temperature_hotspot') or gpu_raw.get('temp_hotspot'),
                'load': (
                    gpu_raw.get('load_gpu') or 
                    gpu_raw.get('load') or 
                    0
                ),
                'clock': (
                    gpu_raw.get('clock_graphics') or 
                    gpu_raw.get('clock_gpu') or 
                    0
                ),
                'memory_clock': (
                    gpu_raw.get('clock_memory') or 
                    gpu_raw.get('clock_mem') or 
                    0
                ),
                'memory_used': (
                    gpu_raw.get('memory_used') or 
                    gpu_raw.get('mem_used') or 
                    0
                ),
                'memory_total': (
                    gpu_raw.get('memory_total') or 
                    gpu_raw.get('mem_total') or 
                    0
                ),
                'power': (
                    gpu_raw.get('power_usage') or 
                    gpu_raw.get('power') or 
                    0
                ),
                'fan_speed': gpu_raw.get('fan_speed', 0),
            }
            
            if self._debug:
                print(f"[DEBUG] Mapped GPU - temp={result['temperature']}, load={result['load']}, clock={result['clock']}")
            
            return result
        
        except Exception as e:
            print(f"[ERROR] get_gpu_data failed: {e}")
            traceback.print_exc()
            return {
                'name': 'Error',
                'temperature': 0,
                'temp_hotspot': None,
                'load': 0,
                'clock': 0,
                'memory_clock': 0,
                'memory_used': 0,
                'memory_total': 0,
                'power': 0,
                'fan_speed': 0,
            }
    
    def get_ram_data(self) -> Dict[str, Any]:
        """Get RAM monitoring data."""
        try:
            all_data = self.manager.get_all_data()
            ram_data = all_data.get('ram', {})
            
            if self._debug:
                print(f"[DEBUG] RAM keys: {list(ram_data.keys())}")
            
            total_gb = ram_data.get('total', 0) / (1024**3) if ram_data.get('total') else 0
            used_gb = ram_data.get('used', 0) / (1024**3) if ram_data.get('used') else 0
            free_gb = ram_data.get('free', 0) / (1024**3) if ram_data.get('free') else 0
            
            result = {
                'total_gb': total_gb,
                'used_gb': used_gb,
                'free_gb': free_gb,
                'percent': ram_data.get('percent', 0),
                'speed': ram_data.get('speed', 0),
                'type': ram_data.get('type', 'Unknown'),
                'xmp_enabled': ram_data.get('xmp_enabled', False),
            }
            
            if self._debug:
                print(f"[DEBUG] RAM - {used_gb:.1f}/{total_gb:.1f} GB ({result['percent']}%)")
            
            return result
        
        except Exception as e:
            print(f"[ERROR] get_ram_data failed: {e}")
            traceback.print_exc()
            return {
                'total_gb': 0,
                'used_gb': 0,
                'free_gb': 0,
                'percent': 0,
                'speed': 0,
                'type': 'Error',
                'xmp_enabled': False,
            }
    
    def get_cpu_data(self) -> Dict[str, Any]:
        """Get CPU monitoring data."""
        try:
            all_data = self.manager.get_all_data()
            cpu_data = all_data.get('cpu', {})
            
            if self._debug:
                print(f"[DEBUG] CPU keys: {list(cpu_data.keys())}")
            
            result = {
                'name': cpu_data.get('name', 'Unknown CPU'),
                'load': cpu_data.get('load', 0),
                'temperature': cpu_data.get('temp'),
                'frequency': cpu_data.get('freq', 0),
                'freq_min': cpu_data.get('freq_min', 0),
                'freq_max': cpu_data.get('freq_max', 0),
                'cores': cpu_data.get('count', 0),
                'threads': cpu_data.get('count_logical', 0),
            }
            
            if self._debug:
                print(f"[DEBUG] CPU - load={result['load']}%, cores={result['cores']}")
            
            return result
        
        except Exception as e:
            print(f"[ERROR] get_cpu_data failed: {e}")
            traceback.print_exc()
            return {
                'name': 'Error',
                'load': 0,
                'temperature': None,
                'frequency': 0,
                'freq_min': 0,
                'freq_max': 0,
                'cores': 0,
                'threads': 0,
            }
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Get all monitoring data at once."""
        return {
            'gpu': self.get_gpu_data(),
            'cpu': self.get_cpu_data(),
            'ram': self.get_ram_data(),
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get monitoring performance statistics."""
        return self.manager.get_performance_stats()
    
    def get_sovereignty_status(self) -> Dict[str, Any]:
        """Get sovereignty status."""
        return self.manager.get_sovereignty_status()


def create_monitor(prefer_native: bool = False, debug: bool = True) -> SystemMonitor:
    """Create a SystemMonitor instance."""
    return SystemMonitor(prefer_native=prefer_native, debug=debug)


if __name__ == '__main__':
    print("[TEST] SystemMonitor Wrapper v0.3.5b")
    print("="*60)
    
    monitor = SystemMonitor(debug=True)
    
    print("\n[GPU Data]")
    gpu = monitor.get_gpu_data()
    for k, v in gpu.items():
        if v:
            print(f"  {k}: {v}")
    
    print("\n[CPU Data]")
    cpu = monitor.get_cpu_data()
    for k, v in cpu.items():
        if v:
            print(f"  {k}: {v}")
    
    print("\n[RAM Data]")
    ram = monitor.get_ram_data()
    for k, v in ram.items():
        print(f"  {k}: {v}")
    
    print("\n" + "="*60)
    print("✅ SystemMonitor v0.3.5b works!")
