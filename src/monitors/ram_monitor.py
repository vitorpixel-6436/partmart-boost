"""RAM monitoring module with XMP detection and speed reporting"""
from typing import Dict, Optional
import sys
import os
import platform

# Add parent dir to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    if platform.system() == "Windows":
        import wmi
        WMI_AVAILABLE = True
    else:
        WMI_AVAILABLE = False
except ImportError:
    WMI_AVAILABLE = False

try:
    from core.logger import get_logger
    logger = get_logger()
except:
    logger = None


class RAMMonitor:
    """Monitor RAM usage, speed, and XMP status
    
    Features:
    - Memory usage (total, used, free, percentage)
    - Memory speed (MHz) on Windows via WMI
    - XMP detection (heuristic-based)
    - Memory type detection (DDR4, DDR5, etc.)
    - Cross-platform support
    
    Example:
        >>> monitor = RAMMonitor()
        >>> data = monitor.get_data()
        >>> print(f"RAM: {data['used']:.1f} / {data['total']:.1f} GB")
        >>> print(f"Speed: {data['speed']} MHz")
        >>> print(f"XMP: {'Enabled' if data['xmp_enabled'] else 'Disabled'}")
    """
    
    def __init__(self):
        """Initialize RAM monitoring"""
        self._available = PSUTIL_AVAILABLE
        self._wmi_available = WMI_AVAILABLE
        self._platform = platform.system()
        self._wmi_connection = None
        
        # Cache for static data (speed, type)
        self._speed_cache: Optional[int] = None
        self._type_cache: Optional[str] = None
        self._xmp_cache: Optional[bool] = None
        
        if self._available:
            self._log_info(f"RAM monitoring initialized on {self._platform}")
            if self._wmi_available:
                self._init_wmi()
        else:
            self._log_error("psutil not available - RAM monitoring disabled")
    
    def _init_wmi(self):
        """Initialize WMI connection for Windows hardware info"""
        try:
            self._wmi_connection = wmi.WMI()
            self._log_info("WMI connection established")
            
            # Pre-fetch static RAM info
            self._fetch_static_info()
        except Exception as e:
            self._log_warning(f"WMI initialization failed: {e}")
            self._wmi_connection = None
    
    def _fetch_static_info(self):
        """Fetch static RAM info (speed, type, XMP) that won't change
        
        Caches results to avoid repeated WMI queries.
        """
        if not self._wmi_connection:
            return
        
        try:
            for mem in self._wmi_connection.Win32_PhysicalMemory():
                # Get speed (MHz)
                if hasattr(mem, 'ConfiguredClockSpeed') and mem.ConfiguredClockSpeed:
                    self._speed_cache = mem.ConfiguredClockSpeed
                
                # Get memory type (DDR4 = 26, DDR5 = 34)
                if hasattr(mem, 'SMBIOSMemoryType'):
                    type_code = mem.SMBIOSMemoryType
                    type_map = {
                        26: "DDR4",
                        34: "DDR5",
                        24: "DDR3",
                        22: "DDR2",
                        21: "DDR",
                    }
                    self._type_cache = type_map.get(type_code, f"Unknown ({type_code})")
                
                # Only need one stick's info
                break
            
            # Determine XMP status (heuristic)
            if self._speed_cache:
                self._xmp_cache = self._is_xmp_enabled(self._speed_cache, self._type_cache)
            
            self._log_info(f"RAM: {self._type_cache} @ {self._speed_cache} MHz (XMP: {self._xmp_cache})")
            
        except Exception as e:
            self._log_warning(f"Failed to fetch RAM static info: {e}")
    
    def _is_xmp_enabled(self, speed: int, mem_type: Optional[str]) -> bool:
        """Heuristic to determine if XMP/DOCP is enabled
        
        Args:
            speed: Configured RAM speed (MHz)
            mem_type: Memory type (DDR4, DDR5, etc.)
        
        Returns:
            True if speed suggests XMP is enabled
        
        Note:
            This is a heuristic. True detection requires BIOS/SPD reading.
            - DDR4: JEDEC max is 2133 MHz, XMP profiles are 2400-4000+ MHz
            - DDR5: JEDEC max is 4800 MHz, XMP profiles are 5200+ MHz
        """
        if mem_type == "DDR5":
            # DDR5 JEDEC: 4800 MHz default
            return speed > 4800
        elif mem_type == "DDR4":
            # DDR4 JEDEC: 2133 MHz default
            return speed > 2133
        elif mem_type == "DDR3":
            # DDR3 JEDEC: 1333-1600 MHz
            return speed > 1600
        else:
            # Unknown type - assume XMP if speed > 2400
            return speed > 2400
    
    def is_available(self) -> bool:
        """Check if RAM monitoring is available
        
        Returns:
            True if psutil available
        """
        return self._available
    
    def get_data(self) -> Dict:
        """Get all RAM data in one call
        
        Returns:
            Dictionary with RAM metrics:
            - total: Total RAM (GB)
            - used: Used RAM (GB)
            - free: Available RAM (GB)
            - percent: Usage percentage (0-100%)
            - speed: RAM speed (MHz) or 0 if unavailable
            - type: Memory type (DDR4, DDR5, etc.) or None
            - xmp_enabled: True if XMP/DOCP likely enabled
        
        Note:
            Speed and XMP detection only available on Windows with WMI.
        """
        if not self._available:
            return self._get_empty_data()
        
        try:
            # Get dynamic memory usage
            ram = psutil.virtual_memory()
            
            total = ram.total / (1024**3)  # Bytes to GB
            used = ram.used / (1024**3)
            free = ram.available / (1024**3)
            percent = ram.percent
            
            # Get static info from cache (or fetch if not cached)
            if self._speed_cache is None and self._wmi_available and self._wmi_connection:
                self._fetch_static_info()
            
            return {
                "total": total,
                "used": used,
                "free": free,
                "percent": percent,
                "speed": self._speed_cache or 0,
                "type": self._type_cache,
                "xmp_enabled": self._xmp_cache if self._xmp_cache is not None else False,
            }
            
        except Exception as e:
            self._log_error(f"Error reading RAM data: {e}")
            return self._get_empty_data()
    
    def get_detailed_info(self) -> Dict:
        """Get detailed RAM stick information (Windows only)
        
        Returns:
            Dictionary with detailed info about each RAM stick:
            - sticks: List of RAM modules with capacity, speed, manufacturer
        
        Note:
            Only works on Windows with WMI.
        """
        if not self._wmi_connection:
            return {"sticks": []}
        
        sticks = []
        try:
            for mem in self._wmi_connection.Win32_PhysicalMemory():
                stick_info = {}
                
                if hasattr(mem, 'Capacity'):
                    stick_info['capacity_gb'] = int(mem.Capacity) / (1024**3)
                
                if hasattr(mem, 'ConfiguredClockSpeed'):
                    stick_info['speed_mhz'] = mem.ConfiguredClockSpeed
                
                if hasattr(mem, 'Manufacturer'):
                    stick_info['manufacturer'] = mem.Manufacturer.strip()
                
                if hasattr(mem, 'PartNumber'):
                    stick_info['part_number'] = mem.PartNumber.strip()
                
                if hasattr(mem, 'DeviceLocator'):
                    stick_info['slot'] = mem.DeviceLocator
                
                sticks.append(stick_info)
            
        except Exception as e:
            self._log_error(f"Failed to get detailed RAM info: {e}")
        
        return {"sticks": sticks}
    
    def _get_empty_data(self) -> Dict:
        """Return empty data structure when RAM unavailable
        
        Returns:
            Dictionary with all fields set to 0/None
        """
        return {
            "total": 0.0,
            "used": 0.0,
            "free": 0.0,
            "percent": 0.0,
            "speed": 0,
            "type": None,
            "xmp_enabled": False,
        }
    
    # Logging helpers
    def _log_debug(self, message: str):
        if logger:
            logger.debug(f"[RAM Monitor] {message}")
    
    def _log_info(self, message: str):
        if logger:
            logger.info(f"[RAM Monitor] {message}")
        else:
            print(f"[RAM Monitor] INFO: {message}")
    
    def _log_warning(self, message: str):
        if logger:
            logger.warning(f"[RAM Monitor] {message}")
        else:
            print(f"[RAM Monitor] WARNING: {message}")
    
    def _log_error(self, message: str):
        if logger:
            logger.error(f"[RAM Monitor] {message}")
        else:
            print(f"[RAM Monitor] ERROR: {message}")


if __name__ == "__main__":
    # Test RAM monitor
    print("Testing RAM Monitor...\n")
    
    monitor = RAMMonitor()
    
    if monitor.is_available():
        print("✅ RAM Monitoring Available\n")
        
        data = monitor.get_data()
        print("RAM Data:")
        for key, value in data.items():
            if isinstance(value, float):
                print(f"  {key:15s}: {value:.2f}")
            elif value is not None:
                print(f"  {key:15s}: {value}")
            else:
                print(f"  {key:15s}: N/A")
        
        print("\n✅ RAM monitoring working!")
        
        # Detailed info (Windows only)
        if platform.system() == "Windows":
            detailed = monitor.get_detailed_info()
            if detailed['sticks']:
                print("\n=== Detailed RAM Info ===")
                for i, stick in enumerate(detailed['sticks'], 1):
                    print(f"\nStick {i}:")
                    for key, value in stick.items():
                        print(f"  {key:15s}: {value}")
        
        if not data['speed']:
            print("\n⚠️  Speed/XMP unavailable - requires WMI on Windows")
    else:
        print("❌ psutil not available - cannot monitor RAM")
