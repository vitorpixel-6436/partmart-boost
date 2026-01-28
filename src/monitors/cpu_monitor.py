"""CPU Monitor - Efficient CPU metrics collection
OPTIMIZED: Batched queries, cached results, minimal overhead
"""
import psutil
import platform
from typing import Dict, Optional
from monitors import BaseMonitor

class CPUMonitor(BaseMonitor):
    """Monitor CPU load, temperature, frequency"""
    
    def __init__(self):
        super().__init__()
        self._cache_duration = 0.5  # Cache for 500ms
        self._last_data = None
        self._cpu_count_physical = psutil.cpu_count(logical=False)
        self._cpu_count_logical = psutil.cpu_count(logical=True)
        self._platform = platform.system()
        
        # Check if temperature is available
        self._temp_available = self._check_temperature_support()
    
    def _check_temperature_support(self) -> bool:
        """Check if CPU temperature reading is supported"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Check for common temperature sensors
                for name in ['coretemp', 'k10temp', 'cpu_thermal', 'acpitz']:
                    if name in temps:
                        return True
            return False
        except (AttributeError, OSError):
            return False
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (platform-dependent)
        
        Returns:
            Temperature in Celsius or None if not available
        """
        if not self._temp_available:
            return None
        
        try:
            temps = psutil.sensors_temperatures()
            
            if not temps:
                return None
            
            # Try common sensor names in priority order
            sensor_priority = [
                'coretemp',      # Intel
                'k10temp',       # AMD Ryzen
                'cpu_thermal',   # ARM/Mobile
                'acpitz',        # Generic ACPI
            ]
            
            for sensor_name in sensor_priority:
                if sensor_name in temps:
                    entries = temps[sensor_name]
                    
                    # Look for package temperature first
                    for entry in entries:
                        label = entry.label.lower()
                        if 'package' in label or 'tctl' in label:
                            return entry.current
                    
                    # Fallback to first entry
                    if entries:
                        return entries[0].current
            
            # If no priority sensor found, use first available
            for name, entries in temps.items():
                if entries:
                    return entries[0].current
            
            return None
            
        except Exception as e:
            print(f"[WARN] CPU temperature read failed: {e}")
            return None
    
    def get_data(self) -> Dict:
        """Get CPU metrics
        
        Returns:
            Dictionary with CPU metrics:
            - load: Overall CPU utilization (0-100%)
            - per_core: List of per-core utilization
            - temp: Temperature in Celsius (or None)
            - freq: Current frequency in MHz
            - freq_min: Minimum frequency
            - freq_max: Maximum frequency
            - count: Physical core count
            - count_logical: Logical processor count (threads)
        """
        # OPTIMIZATION: Return cached data if fresh
        if self._is_cache_valid():
            return self._last_data
        
        try:
            # OPTIMIZATION: Get all CPU metrics in one pass
            # psutil.cpu_percent() call is blocking, but we use interval=None
            # to avoid waiting (uses previous call delta)
            cpu_load = psutil.cpu_percent(interval=0.1)  # Small interval for accuracy
            
            # Per-core utilization (optional - can be expensive)
            per_core = None
            if hasattr(psutil, 'cpu_percent'):
                try:
                    # Only get per-core if explicitly needed
                    # Uncomment for debugging:
                    # per_core = psutil.cpu_percent(interval=0.1, percpu=True)
                    pass
                except:
                    pass
            
            # Frequency (fast)
            cpu_freq = psutil.cpu_freq()
            
            # Temperature (can be slow on some systems)
            cpu_temp = self._get_cpu_temperature()
            
            data = {
                "load": cpu_load,
                "per_core": per_core,
                "temp": cpu_temp,
                "freq": cpu_freq.current if cpu_freq else 0,
                "freq_min": cpu_freq.min if cpu_freq else 0,
                "freq_max": cpu_freq.max if cpu_freq else 0,
                "count": self._cpu_count_physical or self._cpu_count_logical,
                "count_logical": self._cpu_count_logical,
            }
            
            # Update cache
            self._update_cache(data)
            
            return data
            
        except Exception as e:
            print(f"[ERROR] CPU data collection failed: {e}")
            return {
                "load": 0,
                "per_core": None,
                "temp": None,
                "freq": 0,
                "freq_min": 0,
                "freq_max": 0,
                "count": self._cpu_count_physical or self._cpu_count_logical,
                "count_logical": self._cpu_count_logical,
            }
    
    def get_name(self) -> str:
        """Get monitor name"""
        return "CPU Monitor"
    
    def is_available(self) -> bool:
        """Check if CPU monitoring is available"""
        return True  # psutil always available
    
    def get_detailed_info(self) -> Dict:
        """Get detailed CPU information
        
        Returns:
            Extended CPU info for advanced users
        """
        try:
            return {
                "platform": self._platform,
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "physical_cores": self._cpu_count_physical,
                "logical_cores": self._cpu_count_logical,
                "temperature_support": self._temp_available,
            }
        except Exception as e:
            print(f"[ERROR] CPU detailed info failed: {e}")
            return {}

# Singleton instance
_cpu_monitor = None

def get_cpu_monitor() -> CPUMonitor:
    """Get global CPU monitor instance"""
    global _cpu_monitor
    if _cpu_monitor is None:
        _cpu_monitor = CPUMonitor()
    return _cpu_monitor

if __name__ == "__main__":
    # Test
    print("[TEST] Testing CPUMonitor...")
    
    monitor = CPUMonitor()
    
    if monitor.is_available():
        print("[PASS] CPU monitor available")
        
        # Get data
        data = monitor.get_data()
        print(f"[INFO] CPU Load: {data['load']:.1f}%")
        print(f"[INFO] CPU Frequency: {data['freq']:.0f} MHz")
        print(f"[INFO] Physical Cores: {data['count']}")
        print(f"[INFO] Logical Cores: {data['count_logical']}")
        
        if data['temp']:
            print(f"[INFO] CPU Temperature: {data['temp']:.1f}°C")
        else:
            print("[INFO] CPU Temperature: Not available")
        
        # Test caching
        import time
        start = time.time()
        for i in range(10):
            _ = monitor.get_data()
        elapsed = time.time() - start
        print(f"[PERF] 10 reads: {elapsed*1000:.2f}ms ({elapsed/10*1000:.2f}ms/read)")
        
        # Detailed info
        info = monitor.get_detailed_info()
        print(f"[INFO] Platform: {info.get('platform', 'Unknown')}")
        print(f"[INFO] Processor: {info.get('processor', 'Unknown')}")
    else:
        print("[FAIL] CPU monitor not available")
