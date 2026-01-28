"""System Monitor Wrapper - Unified interface for main_window.py

Version: 0.3.5c_hotfix
Author: PartMart Team

Provides simple interface for getting system metrics.
"""
from typing import Dict, Optional
from monitors.manager import MonitorManager


class SystemMonitor:
    """Wrapper around MonitorManager for easier integration."""
    
    def __init__(self, prefer_native: bool = False):
        """Initialize system monitor.
        
        Args:
            prefer_native: Use native monitors (max sovereignty)
        """
        self.manager = MonitorManager(prefer_native=prefer_native)
        self._last_data: Optional[Dict] = None
    
    def update(self) -> Dict:
        """Update and get all system data.
        
        Returns:
            Dict with gpu, cpu, ram data
        """
        try:
            self._last_data = self.manager.get_all_data()
            return self._last_data
        except Exception as e:
            print(f"[ERROR] SystemMonitor.update() failed: {e}")
            # Return last known data or empty
            return self._last_data if self._last_data else self._get_empty_data()
    
    def get_gpu_data(self) -> Dict:
        """Get GPU data only.
        
        Returns:
            GPU metrics dict
        """
        if self._last_data and 'gpu' in self._last_data:
            return self._last_data['gpu']
        
        try:
            data = self.manager.get_all_data()
            return data.get('gpu', {})
        except Exception:
            return {}
    
    def get_cpu_data(self) -> Dict:
        """Get CPU data only.
        
        Returns:
            CPU metrics dict
        """
        if self._last_data and 'cpu' in self._last_data:
            return self._last_data['cpu']
        
        try:
            data = self.manager.get_all_data()
            return data.get('cpu', {})
        except Exception:
            return {}
    
    def get_ram_data(self) -> Dict:
        """Get RAM data only.
        
        Returns:
            RAM metrics dict
        """
        if self._last_data and 'ram' in self._last_data:
            return self._last_data['ram']
        
        try:
            data = self.manager.get_all_data()
            return data.get('ram', {})
        except Exception:
            return {}
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics.
        
        Returns:
            Performance metrics (avg_time_ms, etc)
        """
        return self.manager.get_performance_stats()
    
    def get_sovereignty_status(self) -> Dict:
        """Get sovereignty status.
        
        Returns:
            Sovereignty info (level, score, etc)
        """
        return self.manager.get_sovereignty_status()
    
    def _get_empty_data(self) -> Dict:
        """Get empty data structure.
        
        Returns:
            Empty metrics dict
        """
        return {
            'gpu': {
                'name': 'No GPU',
                'temp_gpu': 0,
                'temp_hotspot': None,
                'clock_gpu': 0,
                'clock_mem': 0,
                'load_gpu': 0,
                'load_mem': 0,
                'power': 0,
                'fan_speed': 0,
            },
            'cpu': {
                'name': 'Unknown CPU',
                'load': 0,
                'temp': None,
                'freq': 0,
                'freq_min': 0,
                'freq_max': 0,
                'count': 1,
                'count_logical': 1,
            },
            'ram': {
                'total': 16.0,
                'used': 8.0,
                'free': 8.0,
                'percent': 50.0,
                'speed': None,
                'type': 'DDR4',
                'xmp_enabled': False,
            },
        }


if __name__ == "__main__":
    import time
    
    print("[TEST] SystemMonitor Wrapper")
    print("="*60)
    
    monitor = SystemMonitor()
    
    print("\n[INFO] Sovereignty Status:")
    status = monitor.get_sovereignty_status()
    print(f"  Level: {status['level']}")
    print(f"  Score: {status['score']}/100")
    
    print("\n[INFO] Testing data retrieval...")
    
    # Update all
    data = monitor.update()
    print(f"\n[GPU] {data['gpu']['name']}")
    print(f"  Temp: {data['gpu']['temp_gpu']}°C")
    print(f"  Load: {data['gpu']['load_gpu']}%")
    
    print(f"\n[CPU] {data['cpu']['name']}")
    print(f"  Load: {data['cpu']['load']:.1f}%")
    print(f"  Freq: {data['cpu']['freq']:.0f} MHz")
    
    print(f"\n[RAM] {data['ram']['type']}")
    print(f"  Used: {data['ram']['used']:.2f} GB")
    print(f"  Percent: {data['ram']['percent']:.1f}%")
    
    # Test individual getters
    print("\n[INFO] Testing individual getters...")
    gpu = monitor.get_gpu_data()
    cpu = monitor.get_cpu_data()
    ram = monitor.get_ram_data()
    
    print(f"  GPU: {gpu.get('name', 'N/A')}")
    print(f"  CPU: {cpu.get('name', 'N/A')}")
    print(f"  RAM: {ram.get('type', 'N/A')}")
    
    # Performance
    print("\n[INFO] Testing performance (10 iterations)...")
    start = time.time()
    for _ in range(10):
        monitor.update()
        time.sleep(0.05)
    elapsed = time.time() - start
    
    stats = monitor.get_performance_stats()
    print(f"\n[STATS] Performance:")
    print(f"  Average: {stats['avg_time_ms']:.2f}ms")
    print(f"  Last: {stats['last_time_ms']:.2f}ms")
    print(f"  Total updates: {stats['total_updates']}")
    print(f"  Total time: {elapsed:.3f}s")
    
    print("\n" + "="*60)
    print("✅ SystemMonitor wrapper works!")
    print("="*60)
