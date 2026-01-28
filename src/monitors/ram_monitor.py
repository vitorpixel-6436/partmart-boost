"""RAM Monitor - Efficient RAM metrics collection
OPTIMIZED: Cached speed detection, safe WMI usage
SECURITY: Uses SafeWMI wrapper for Windows
"""
import psutil
import platform
from typing import Dict, Optional
from monitors import BaseMonitor

class RAMMonitor(BaseMonitor):
    """Monitor RAM usage, speed, and XMP status"""
    
    def __init__(self):
        super().__init__()
        self._cache_duration = 1.0  # Cache for 1 second
        self._last_data = None
        self._platform = platform.system()
        
        # Static info (cached permanently)
        self._total_ram = psutil.virtual_memory().total / (1024**3)  # GB
        self._ram_speed = None
        self._xmp_enabled = False
        self._ram_type = None
        
        # Detect RAM speed once
        self._detect_ram_info()
    
    def _detect_ram_info(self):
        """Detect RAM speed and XMP status (Windows only)
        
        Uses SafeWMI wrapper for security
        """
        if self._platform != "Windows":
            return
        
        try:
            # SECURITY: Use safe WMI wrapper
            from core.safe_wmi import get_safe_wmi
            
            wmi = get_safe_wmi()
            
            if wmi.is_available():
                # Get RAM speed safely
                self._ram_speed = wmi.get_ram_speed()
                
                if self._ram_speed:
                    # Heuristic: XMP likely enabled if speed > 2400 for DDR4
                    # or > 3200 for DDR5
                    if self._ram_speed > 3200:
                        self._xmp_enabled = True
                        self._ram_type = "DDR5"
                    elif self._ram_speed > 2400:
                        self._xmp_enabled = True
                        self._ram_type = "DDR4"
                    elif self._ram_speed > 1600:
                        self._ram_type = "DDR4"
                    else:
                        self._ram_type = "DDR3"
                
                print(f"[INFO] RAM Speed: {self._ram_speed} MHz ({self._ram_type})")
                if self._xmp_enabled:
                    print(f"[INFO] XMP/DOCP likely enabled")
        
        except ImportError:
            print("[INFO] SafeWMI not available, RAM speed detection disabled")
        except Exception as e:
            print(f"[WARN] RAM speed detection failed: {e}")
    
    def get_data(self) -> Dict:
        """Get RAM metrics
        
        Returns:
            Dictionary with RAM metrics:
            - total: Total RAM in GB
            - used: Used RAM in GB
            - free: Available RAM in GB
            - percent: Usage percentage (0-100%)
            - speed: RAM speed in MHz (or None)
            - xmp_enabled: XMP/DOCP status (heuristic)
            - type: DDR type (DDR3/DDR4/DDR5)
        """
        # OPTIMIZATION: Return cached data if fresh
        if self._is_cache_valid():
            return self._last_data
        
        try:
            # OPTIMIZATION: Single psutil call for all metrics
            ram = psutil.virtual_memory()
            
            data = {
                "total": ram.total / (1024**3),
                "used": ram.used / (1024**3),
                "free": ram.available / (1024**3),
                "percent": ram.percent,
                "speed": self._ram_speed,
                "xmp_enabled": self._xmp_enabled,
                "type": self._ram_type,
            }
            
            # Update cache
            self._update_cache(data)
            
            return data
            
        except Exception as e:
            print(f"[ERROR] RAM data collection failed: {e}")
            return {
                "total": self._total_ram,
                "used": 0,
                "free": self._total_ram,
                "percent": 0,
                "speed": self._ram_speed,
                "xmp_enabled": self._xmp_enabled,
                "type": self._ram_type,
            }
    
    def get_name(self) -> str:
        """Get monitor name"""
        return "RAM Monitor"
    
    def is_available(self) -> bool:
        """Check if RAM monitoring is available"""
        return True  # psutil always available
    
    def get_detailed_info(self) -> Dict:
        """Get detailed RAM information
        
        Returns:
            Extended RAM info
        """
        try:
            ram = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "platform": self._platform,
                "total_bytes": ram.total,
                "available_bytes": ram.available,
                "used_bytes": ram.used,
                "cached_bytes": getattr(ram, 'cached', 0),
                "buffers_bytes": getattr(ram, 'buffers', 0),
                "swap_total": swap.total / (1024**3),
                "swap_used": swap.used / (1024**3),
                "swap_percent": swap.percent,
                "ram_speed_mhz": self._ram_speed,
                "ram_type": self._ram_type,
                "xmp_docp_enabled": self._xmp_enabled,
            }
        except Exception as e:
            print(f"[ERROR] RAM detailed info failed: {e}")
            return {}
    
    def get_optimization_suggestions(self) -> list:
        """Get RAM optimization suggestions based on current state
        
        Returns:
            List of actionable suggestions
        """
        suggestions = []
        
        try:
            data = self.get_data()
            
            # High usage warning
            if data['percent'] > 90:
                suggestions.append("⚠️ RAM critically high (>90%)")
                suggestions.append("🛠️ Close unused applications")
            elif data['percent'] > 80:
                suggestions.append("📄 RAM usage high (>80%)")
                suggestions.append("📝 Consider closing some tabs/apps")
            
            # XMP status
            if self._ram_speed:
                if not self._xmp_enabled:
                    suggestions.append("🚀 XMP/DOCP not enabled")
                    suggestions.append("🛠️ Enable in BIOS for better performance")
                else:
                    suggestions.append("✅ XMP/DOCP enabled")
            
            # Low RAM warning
            if data['total'] < 8:
                suggestions.append("📊 Total RAM: {:.1f}GB (consider upgrade)".format(data['total']))
            
            return suggestions
            
        except Exception as e:
            print(f"[ERROR] RAM suggestions failed: {e}")
            return []

# Singleton instance
_ram_monitor = None

def get_ram_monitor() -> RAMMonitor:
    """Get global RAM monitor instance"""
    global _ram_monitor
    if _ram_monitor is None:
        _ram_monitor = RAMMonitor()
    return _ram_monitor

if __name__ == "__main__":
    # Test
    print("[TEST] Testing RAMMonitor...")
    
    monitor = RAMMonitor()
    
    if monitor.is_available():
        print("[PASS] RAM monitor available")
        
        # Get data
        data = monitor.get_data()
        print(f"[INFO] RAM Total: {data['total']:.1f} GB")
        print(f"[INFO] RAM Used: {data['used']:.1f} GB")
        print(f"[INFO] RAM Free: {data['free']:.1f} GB")
        print(f"[INFO] RAM Usage: {data['percent']:.1f}%")
        
        if data['speed']:
            print(f"[INFO] RAM Speed: {data['speed']} MHz")
            print(f"[INFO] RAM Type: {data['type']}")
            print(f"[INFO] XMP Enabled: {data['xmp_enabled']}")
        else:
            print("[INFO] RAM Speed: Not available")
        
        # Test caching
        import time
        start = time.time()
        for i in range(10):
            _ = monitor.get_data()
        elapsed = time.time() - start
        print(f"[PERF] 10 reads: {elapsed*1000:.2f}ms ({elapsed/10*1000:.2f}ms/read)")
        
        # Detailed info
        info = monitor.get_detailed_info()
        print(f"[INFO] Swap Total: {info.get('swap_total', 0):.1f} GB")
        print(f"[INFO] Swap Used: {info.get('swap_used', 0):.1f} GB")
        
        # Suggestions
        suggestions = monitor.get_optimization_suggestions()
        if suggestions:
            print("\n[SUGGESTIONS]")
            for s in suggestions:
                print(f"  {s}")
    else:
        print("[FAIL] RAM monitor not available")
