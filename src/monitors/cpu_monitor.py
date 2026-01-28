"""CPU monitoring module with cross-platform temperature support"""
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
    from core.logger import get_logger
    logger = get_logger()
except:
    logger = None


class CPUMonitor:
    """Monitor CPU load, temperature, frequency, and core count
    
    Features:
    - CPU utilization percentage
    - Temperature (if available)
    - Current frequency
    - Physical core count (not hyperthreading)
    - Logical core count (with hyperthreading)
    - Cross-platform support (Windows/Linux/Mac)
    
    Example:
        >>> monitor = CPUMonitor()
        >>> data = monitor.get_data()
        >>> print(f"CPU Load: {data['load']}%")
        >>> print(f"Cores: {data['count']}")
    """
    
    def __init__(self):
        """Initialize CPU monitoring"""
        self._available = PSUTIL_AVAILABLE
        self._platform = platform.system()
        self._cpu_name = self._get_cpu_name()
        self._temp_available = False
        
        # Check if temperature sensors available
        self._check_temperature_support()
        
        if self._available:
            self._log_info(f"CPU monitoring initialized on {self._platform}")
            if self._temp_available:
                self._log_info("CPU temperature monitoring available")
            else:
                self._log_warning("CPU temperature monitoring unavailable")
        else:
            self._log_error("psutil not available - CPU monitoring disabled")
    
    def _get_cpu_name(self) -> str:
        """Get CPU model name
        
        Returns:
            CPU model string (e.g., 'AMD Ryzen 5 5600X')
        """
        try:
            if self._platform == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name = winreg.QueryValueEx(key, "ProcessorNameString")[0]
                winreg.CloseKey(key)
                return cpu_name.strip()
            else:
                # Linux/Mac
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
        except:
            pass
        return "Unknown CPU"
    
    def _check_temperature_support(self) -> bool:
        """Check if CPU temperature sensors are available
        
        Returns:
            True if temperature can be read
        """
        if not self._available:
            return False
        
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return False
            
            # Check for known temperature sensor names
            temp_keys = temps.keys()
            if self._platform == "Windows":
                # Windows: check for common sensor names
                # Usually requires OpenHardwareMonitor or similar
                if any(key.lower() in ['cpu', 'coretemp', 'package'] for key in temp_keys):
                    self._temp_available = True
                    return True
            else:
                # Linux: coretemp, k10temp (AMD), etc.
                if 'coretemp' in temp_keys or 'k10temp' in temp_keys:
                    self._temp_available = True
                    return True
        except:
            pass
        
        self._temp_available = False
        return False
    
    def is_available(self) -> bool:
        """Check if CPU monitoring is available
        
        Returns:
            True if psutil available
        """
        return self._available
    
    def get_name(self) -> str:
        """Get CPU model name
        
        Returns:
            CPU name string
        """
        return self._cpu_name
    
    def get_data(self) -> Dict:
        """Get all CPU data in one call
        
        Returns:
            Dictionary with CPU metrics:
            - name: CPU model name
            - load: CPU utilization (0-100%)
            - temp: Temperature (°C) or None if unavailable
            - freq: Current frequency (MHz)
            - count: Physical core count
            - count_logical: Logical core count (with HT)
        
        Note:
            Temperature may be None if sensors unavailable
        """
        if not self._available:
            return self._get_empty_data()
        
        try:
            # CPU load (quick sample)
            load = self._get_load()
            
            # Temperature
            temp = self._get_temperature()
            
            # Frequency
            freq = self._get_frequency()
            
            # Core counts
            count_physical, count_logical = self._get_core_counts()
            
            return {
                "name": self._cpu_name,
                "load": load,
                "temp": temp,
                "freq": freq,
                "count": count_physical,
                "count_logical": count_logical,
            }
            
        except Exception as e:
            self._log_error(f"Error reading CPU data: {e}")
            return self._get_empty_data()
    
    def _get_load(self) -> float:
        """Get CPU utilization percentage
        
        Returns:
            CPU load (0-100%)
        """
        try:
            # interval=0.1 for quick non-blocking read
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            self._log_debug(f"Failed to read CPU load: {e}")
            return 0.0
    
    def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature
        
        Returns:
            Temperature in Celsius, or None if unavailable
        
        Note:
            On Windows, requires OpenHardwareMonitor, HWiNFO, or CoreTemp
            running in background. Otherwise returns None.
        """
        if not self._temp_available:
            return None
        
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            
            # Search for CPU package temperature
            for sensor_name, entries in temps.items():
                sensor_lower = sensor_name.lower()
                
                # Check for known CPU sensor names
                if any(keyword in sensor_lower for keyword in ['cpu', 'core', 'package', 'k10temp']):
                    for entry in entries:
                        label_lower = entry.label.lower()
                        
                        # Prioritize package/CPU temperature
                        if 'package' in label_lower or 'cpu' in label_lower or label_lower == '':
                            return entry.current
                    
                    # Fallback: return first temperature from CPU sensor
                    if entries:
                        return entries[0].current
            
            return None
            
        except Exception as e:
            self._log_debug(f"Failed to read CPU temperature: {e}")
            return None
    
    def _get_frequency(self) -> float:
        """Get current CPU frequency
        
        Returns:
            Frequency in MHz, or 0 if unavailable
        """
        try:
            freq = psutil.cpu_freq()
            return freq.current if freq else 0.0
        except Exception as e:
            self._log_debug(f"Failed to read CPU frequency: {e}")
            return 0.0
    
    def _get_core_counts(self) -> tuple[int, int]:
        """Get physical and logical core counts
        
        Returns:
            Tuple of (physical_cores, logical_cores)
            Physical = actual cores, Logical = with hyperthreading
        """
        try:
            physical = psutil.cpu_count(logical=False)
            logical = psutil.cpu_count(logical=True)
            
            # Fallback if physical count unavailable
            if physical is None:
                physical = logical
            
            return physical, logical
            
        except Exception as e:
            self._log_debug(f"Failed to read core counts: {e}")
            return 0, 0
    
    def _get_empty_data(self) -> Dict:
        """Return empty data structure when CPU unavailable
        
        Returns:
            Dictionary with all fields set to 0/None
        """
        return {
            "name": self._cpu_name,
            "load": 0.0,
            "temp": None,
            "freq": 0.0,
            "count": 0,
            "count_logical": 0,
        }
    
    # Logging helpers
    def _log_debug(self, message: str):
        if logger:
            logger.debug(f"[CPU Monitor] {message}")
    
    def _log_info(self, message: str):
        if logger:
            logger.info(f"[CPU Monitor] {message}")
        else:
            print(f"[CPU Monitor] INFO: {message}")
    
    def _log_warning(self, message: str):
        if logger:
            logger.warning(f"[CPU Monitor] {message}")
        else:
            print(f"[CPU Monitor] WARNING: {message}")
    
    def _log_error(self, message: str):
        if logger:
            logger.error(f"[CPU Monitor] {message}")
        else:
            print(f"[CPU Monitor] ERROR: {message}")


if __name__ == "__main__":
    # Test CPU monitor
    print("Testing CPU Monitor...\n")
    
    monitor = CPUMonitor()
    
    if monitor.is_available():
        print(f"✅ CPU Monitoring Available")
        print(f"   Model: {monitor.get_name()}\n")
        
        data = monitor.get_data()
        print("CPU Data:")
        for key, value in data.items():
            if value is not None:
                print(f"  {key:15s}: {value}")
            else:
                print(f"  {key:15s}: N/A")
        
        print("\n✅ CPU monitoring working!")
        
        if data['temp'] is None:
            print("\n⚠️  Temperature unavailable - may need OpenHardwareMonitor on Windows")
    else:
        print("❌ psutil not available - cannot monitor CPU")
