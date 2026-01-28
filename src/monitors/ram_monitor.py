"""Optimized RAM Monitor with caching
PERFORMANCE: <3ms latency, WMI queries cached
SECURITY: Uses SafeWMI wrapper
Version: 0.3.5d - Package 2
"""
import psutil
import platform
import time
from typing import Dict, Optional
from monitors import BaseMonitor

class RAMMonitor(BaseMonitor):
    """Fast RAM monitoring with WMI caching
    
    v0.3.5d Package 2 fixes:
    - Add 'type' field to schema
    - Return None instead of 0 for unavailable speed
    - Better DDR type detection
    """
    
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
        
        v0.3.5d: Return None instead of 0 when unavailable
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
                    timeout=3,  # v0.3.5d: Add timeout
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
        # v0.3.5d FIX: Return None instead of 0
        return None
    
    def _detect_ram_type(self, speed: Optional[int]) -> str:
        """Detect RAM type based on speed
        
        Args:
            speed: RAM speed in MHz
        
        Returns:
            RAM type string (DDR5, DDR4, DDR3, DDR2, or Unknown)
        
        v0.3.5d: New method for better type detection
        """
        if speed is None:
            return 'Unknown'
        
        # DDR5: 4800+ MHz
        if speed >= 4800:
            return 'DDR5'
        # DDR4: 1600-4799 MHz
        elif speed >= 1600:
            return 'DDR4'
        # DDR3: 800-1599 MHz
        elif speed >= 800:
            return 'DDR3'
        # DDR2: 400-799 MHz
        elif speed >= 400:
            return 'DDR2'
        else:
            return 'Unknown'
    
    def _detect_xmp_status(self, speed: Optional[int], ram_type: str) -> bool:
        """Heuristic: detect if XMP is enabled
        
        Args:
            speed: RAM speed in MHz
            ram_type: RAM type (DDR5, DDR4, etc.)
        
        Returns:
            True if likely XMP enabled
        
        v0.3.5d: Improved logic based on type
        """
        if not speed:
            return False
        
        # JEDEC base speeds by type
        jedec_speeds = {
            'DDR5': 4800,
            'DDR4': 2133,
            'DDR3': 1333,
            'DDR2': 667,
        }
        
        base_speed = jedec_speeds.get(ram_type, 2133)
        
        # XMP if speed > base speed + margin
        # DDR4: XMP if > 2400 (gives some margin)
        # DDR5: XMP if > 4800
        if ram_type == 'DDR5':
            return speed > 4800
        elif ram_type == 'DDR4':
            return speed > 2400
        elif ram_type == 'DDR3':
            return speed > 1600
        else:
            return speed > base_speed
    
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
        
        v0.3.5d Package 2 schema:
        - total: float (GB)
        - used: float (GB)
        - free: float (GB)
        - percent: float (0-100)
        - speed: int or None (MHz)
        - type: str (DDR5/DDR4/DDR3/DDR2/Unknown)
        - xmp_enabled: bool
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
            
            # v0.3.5d FIX: Detect RAM type
            ram_type = self._detect_ram_type(ram_speed)
            
            # Heuristic XMP detection
            xmp_enabled = self._detect_xmp_status(ram_speed, ram_type)
            
            return {
                "total": round(ram_total, 2),
                "used": round(ram_used, 2),
                "free": round(ram_free, 2),
                "percent": round(ram_percent, 1),
                "speed": ram_speed,  # v0.3.5d: None if unavailable, not 0
                "type": ram_type,  # v0.3.5d FIX: Add type field
                "xmp_enabled": xmp_enabled,
            }
        
        except Exception as e:
            print(f"[ERROR] RAM data collection failed: {e}")
            return {
                "total": 0.0,
                "used": 0.0,
                "free": 0.0,
                "percent": 0.0,
                "speed": None,  # v0.3.5d: None, not 0
                "type": "Unknown",  # v0.3.5d FIX: Add type field
                "xmp_enabled": False,
            }

if __name__ == "__main__":
    # Performance test
    import time
    
    print("[TEST] Testing RAMMonitor v0.3.5d Package 2...")
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
    print(f"[RESULT] Target: <3ms - {'PASS ✅' if avg_time < 3 else 'FAIL ❌'}")
    
    print("\n[DATA] Sample output (v0.3.5d schema):")
    data = monitor.get_data()
    for k, v in data.items():
        print(f"  {k}: {v}")
    
    print("\n[SCHEMA] Required fields present:")
    required_fields = ['total', 'used', 'free', 'percent', 'speed', 'type', 'xmp_enabled']
    for field in required_fields:
        status = '✅' if field in data else '❌'
        print(f"  {status} {field}")
