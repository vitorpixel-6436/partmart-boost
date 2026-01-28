"""Optimized CPU Monitor with non-blocking calls
PERFORMANCE: <5ms latency, non-blocking CPU measurement
"""
import psutil
import platform
import time
from typing import Dict, Optional
from monitors import BaseMonitor

class CPUMonitor(BaseMonitor):
    """Fast CPU monitoring with caching and non-blocking calls"""
    
    def __init__(self):
        super().__init__()
        self._last_temp_check = 0
        self._cached_temp = None
        self._temp_cache_duration = 5.0  # Cache temp for 5 seconds
        
        self._last_percent = None
        self._percent_init_time = time.time()
        
        # Pre-detect temperature sensor availability
        self._temp_available = False
        self._temp_sensor_name = None
        self._detect_temperature_sensor()
        
        # Initialize first CPU measurement (blocking once)
        # This primes psutil's internal state
        psutil.cpu_percent(interval=0.1)
    
    def _detect_temperature_sensor(self):
        """Detect available temperature sensor (once at init)"""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return
            
            system = platform.system()
            
            if system == "Windows":
                # Look for CPU package sensor
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        for entry in entries:
                            if 'package' in entry.label.lower() or entry.label == '':
                                self._temp_available = True
                                self._temp_sensor_name = (name, entry.label)
                                return
            
            elif system == "Linux":
                # Linux: usually 'coretemp'
                if 'coretemp' in temps:
                    self._temp_available = True
                    self._temp_sensor_name = ('coretemp', 0)
                # Fallback: k10temp for AMD
                elif 'k10temp' in temps:
                    self._temp_available = True
                    self._temp_sensor_name = ('k10temp', 0)
            
            elif system == "Darwin":
                # macOS
                if temps:
                    # Take first available
                    first_sensor = list(temps.keys())[0]
                    self._temp_available = True
                    self._temp_sensor_name = (first_sensor, 0)
        
        except Exception as e:
            print(f"[DEBUG] CPU temp sensor detection failed: {e}")
    
    def _get_temperature_fast(self) -> Optional[float]:
        """Get CPU temperature with caching (fast)
        
        Returns:
            Temperature in Celsius or None
        """
        if not self._temp_available:
            return None
        
        # Check cache
        now = time.time()
        if self._cached_temp is not None and (now - self._last_temp_check) < self._temp_cache_duration:
            return self._cached_temp
        
        # Update cache
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            
            sensor_name, label_or_index = self._temp_sensor_name
            
            if sensor_name in temps:
                entries = temps[sensor_name]
                
                if isinstance(label_or_index, int):
                    # Use index
                    if len(entries) > label_or_index:
                        self._cached_temp = entries[label_or_index].current
                else:
                    # Search by label
                    for entry in entries:
                        if entry.label == label_or_index or label_or_index == '':
                            self._cached_temp = entry.current
                            break
            
            self._last_temp_check = now
            return self._cached_temp
        
        except Exception as e:
            print(f"[DEBUG] CPU temp read failed: {e}")
            return None
    
    def get_name(self) -> str:
        """Get monitor name"""
        return "CPU Monitor"
    
    def is_available(self) -> bool:
        """Check if CPU monitoring is available"""
        return True  # CPU always available
    
    def get_data(self) -> Dict:
        """Get CPU data (optimized, non-blocking)
        
        Returns:
            Dictionary with CPU metrics
        """
        try:
            # NON-BLOCKING CPU percent (uses previous measurement)
            # This is the KEY optimization!
            cpu_load = psutil.cpu_percent(interval=None)
            
            # If interval=None returns 0.0, use interval=0 fallback
            if cpu_load == 0.0 and self._last_percent is None:
                # First call after init - use blocking once
                cpu_load = psutil.cpu_percent(interval=0.1)
            
            self._last_percent = cpu_load
            
            # Get frequency (fast)
            cpu_freq = psutil.cpu_freq()
            
            # Get core counts (cached internally by psutil)
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Get per-core usage (optional, can be slow)
            # per_core = psutil.cpu_percent(interval=None, percpu=True)
            
            # Get temperature with caching
            cpu_temp = self._get_temperature_fast()
            
            return {
                "load": cpu_load,
                "temp": cpu_temp,
                "freq": cpu_freq.current if cpu_freq else 0,
                "freq_min": cpu_freq.min if cpu_freq else 0,
                "freq_max": cpu_freq.max if cpu_freq else 0,
                "count": cpu_count_physical if cpu_count_physical else cpu_count_logical,
                "count_logical": cpu_count_logical,
                # "per_core": per_core,  # Optional
            }
        
        except Exception as e:
            print(f"[ERROR] CPU data collection failed: {e}")
            return {
                "load": 0,
                "temp": None,
                "freq": 0,
                "freq_min": 0,
                "freq_max": 0,
                "count": 0,
                "count_logical": 0,
            }

if __name__ == "__main__":
    # Performance test
    import time
    
    print("[TEST] Testing CPUMonitor performance...")
    monitor = CPUMonitor()
    
    # Warmup
    monitor.get_data()
    time.sleep(0.5)
    
    # Benchmark
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        data = monitor.get_data()
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000  # ms
    
    print(f"[RESULT] {iterations} iterations in {elapsed:.3f}s")
    print(f"[RESULT] Average: {avg_time:.2f}ms per call")
    print(f"[RESULT] Target: <5ms - {'PASS \u2705' if avg_time < 5 else 'FAIL \u274c'}")
    
    print("\n[DATA] Sample output:")
    data = monitor.get_data()
    for k, v in data.items():
        print(f"  {k}: {v}")
