"""Optimized RAM Monitor with caching
PERFORMANCE: <3ms latency, WMI queries cached
SECURITY: Uses SafeWMI wrapper
"""
import psutil
import platform
import time
from typing import Dict, Optional
from monitors import BaseMonitor

class RAMMonitor(BaseMonitor):
    """Fast RAM monitoring with WMI caching"""
    
    def __init__(self):
        super().__init__()
        
        # WMI cache (speed detection is slow)
        self._ram_speed = None
        self._ram_speed_cached = False
        self._ram_speed_cache_time = 0
        self._ram_speed_cache_duration = 60.0  # Cache for 60 seconds
        
        # SafeWMI instance (lazy init)
        self._safe_wmi = None
        
        # Pre-detect if WMI is available
        self._wmi_available = False
        if platform.system() == "Windows":
            self._init_safe_wmi()
    
    def _init_safe_wmi(self):
        """Initialize SafeWMI (lazy, once)"""
        if self._safe_wmi is not None:
            return
        
        try:
            from core.safe_wmi import get_safe_wmi
            self._safe_wmi = get_safe_wmi()
            self._wmi_available = self._safe_wmi.is_available()
            
            if self._wmi_available:
                print("[INFO] SafeWMI initialized for RAM monitoring")
        except ImportError:
            print("[WARN] SafeWMI not available")
        except Exception as e:
            print(f"[WARN] SafeWMI init failed: {e}")
    
    def _get_ram_speed_cached(self) -> Optional[int]:
        """Get RAM speed with caching (slow WMI query)
        
        Returns:
            RAM speed in MHz or None
        """
        # Check cache
        now = time.time()
        if self._ram_speed_cached and (now - self._ram_speed_cache_time) < self._ram_speed_cache_duration:
            return self._ram_speed
        
        # Windows: Use SafeWMI
        if platform.system() == "Windows" and self._wmi_available:
            try:
                speed = self._safe_wmi.get_ram_speed()
                if speed:
                    self._ram_speed = speed
                    self._ram_speed_cached = True
                    self._ram_speed_cache_time = now
                    return speed
            except Exception as e:
                print(f"[WARN] WMI RAM speed query failed: {e}")
        
        # Linux: Try to read from dmidecode (requires root)
        elif platform.system() == "Linux":
            try:
                import subprocess
                result = subprocess.run(
                    ['dmidecode', '-t', 'memory'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False
                )
                
                if result.returncode == 0:
                    # Parse output for "Speed: XXX MHz"
                    for line in result.stdout.split('\n'):
                        if 'Speed:' in line and 'MHz' in line:
                            # Extract number
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == 'MHz' and i > 0:
                                    try:
                                        speed = int(parts[i-1])
                                        self._ram_speed = speed
                                        self._ram_speed_cached = True
                                        self._ram_speed_cache_time = now
                                        return speed
                                    except ValueError:
                                        pass
            except Exception as e:
                print(f"[DEBUG] dmidecode failed: {e}")
        
        # Fallback: mark as checked but unavailable
        self._ram_speed_cached = True
        self._ram_speed_cache_time = now
        return None
    
    def _detect_xmp_status(self, speed: Optional[int]) -> bool:
        """Heuristic: detect if XMP is enabled
        
        Args:
            speed: RAM speed in MHz
        
        Returns:
            True if likely XMP enabled
        """
        if not speed:
            return False
        
        # DDR4: Base speed 2133 MHz, XMP typically 2666+ MHz
        # DDR5: Base speed 4800 MHz, XMP typically 5200+ MHz
        
        if speed >= 4800:
            # DDR5
            return speed > 4800
        else:
            # DDR4 or older
            return speed > 2400
    
    def get_name(self) -> str:
        """Get monitor name"""
        return "RAM Monitor"
    
    def is_available(self) -> bool:
        """Check if RAM monitoring is available"""
        return True  # RAM always available via psutil
    
    def get_data(self) -> Dict:
        """Get RAM data (optimized, fast)
        
        Returns:
            Dictionary with RAM metrics
        """
        try:
            # Fast: psutil RAM usage (non-blocking)
            ram = psutil.virtual_memory()
            
            ram_total = ram.total / (1024**3)  # GB
            ram_used = ram.used / (1024**3)
            ram_free = ram.available / (1024**3)
            ram_percent = ram.percent
            
            # Slow: RAM speed detection (cached)
            ram_speed = self._get_ram_speed_cached()
            
            # Heuristic XMP detection
            xmp_enabled = self._detect_xmp_status(ram_speed)
            
            return {
                "total": ram_total,
                "used": ram_used,
                "free": ram_free,
                "percent": ram_percent,
                "speed": ram_speed if ram_speed else 0,
                "xmp_enabled": xmp_enabled,
            }
        
        except Exception as e:
            print(f"[ERROR] RAM data collection failed: {e}")
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0,
                "speed": 0,
                "xmp_enabled": False,
            }

if __name__ == "__main__":
    # Performance test
    import time
    
    print("[TEST] Testing RAMMonitor performance...")
    monitor = RAMMonitor()
    
    # First call (may be slow due to WMI)
    print("[INFO] First call (uncached):")
    start = time.time()
    data = monitor.get_data()
    elapsed = (time.time() - start) * 1000
    print(f"  Time: {elapsed:.2f}ms")
    
    # Subsequent calls (cached)
    print("\n[INFO] Subsequent calls (cached):")
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        data = monitor.get_data()
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000  # ms
    
    print(f"[RESULT] {iterations} iterations in {elapsed:.3f}s")
    print(f"[RESULT] Average: {avg_time:.2f}ms per call")
    print(f"[RESULT] Target: <3ms - {'PASS \u2705' if avg_time < 3 else 'FAIL \u274c'}")
    
    print("\n[DATA] Sample output:")
    data = monitor.get_data()
    for k, v in data.items():
        print(f"  {k}: {v}")
