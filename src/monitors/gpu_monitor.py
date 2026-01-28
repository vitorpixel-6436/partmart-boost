"""NVIDIA GPU monitoring module with graceful degradation"""
from typing import Dict, Optional
import sys
import os

# Add parent dir to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    from core.logger import get_logger
    logger = get_logger()
except:
    # Fallback if logger not initialized
    logger = None


class GPUMonitor:
    """Monitor NVIDIA GPU temperature, clock speeds, load, power, fan
    
    Features:
    - Real-time temperature (core + hotspot)
    - Clock speeds (GPU core + memory)
    - Utilization (GPU + VRAM)
    - Power consumption
    - Fan speed
    - Graceful degradation if GPU unavailable
    
    Example:
        >>> monitor = GPUMonitor()
        >>> if monitor.is_available():
        ...     data = monitor.get_data()
        ...     print(f"GPU: {data['temp_gpu']}°C")
        >>> monitor.cleanup()
    """
    
    def __init__(self):
        """Initialize GPU monitoring
        
        Attempts to initialize NVML and detect GPU.
        If unsuccessful, operates in degraded mode.
        """
        self._available = False
        self._handle = None
        self._name = "No GPU detected"
        self._init_attempts = 0
        self._max_init_attempts = 3
        
        self._initialize_nvml()
    
    def _initialize_nvml(self) -> bool:
        """Initialize NVML library and get GPU handle
        
        Returns:
            True if successful, False otherwise
        """
        if not PYNVML_AVAILABLE:
            self._log_info("pynvml library not available")
            return False
        
        try:
            pynvml.nvmlInit()
            self._handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self._name = pynvml.nvmlDeviceGetName(self._handle)
            
            # Decode bytes to string if needed
            if isinstance(self._name, bytes):
                self._name = self._name.decode('utf-8')
            
            self._available = True
            self._log_info(f"GPU detected: {self._name}")
            return True
            
        except Exception as e:
            self._log_warning(f"GPU initialization failed: {e}")
            self._available = False
            return False
    
    def is_available(self) -> bool:
        """Check if GPU is available for monitoring
        
        Returns:
            True if GPU detected and NVML working
        """
        return self._available
    
    def get_name(self) -> str:
        """Get GPU name/model
        
        Returns:
            GPU name string (e.g., 'NVIDIA GeForce RTX 3060')
        """
        return self._name
    
    def get_data(self) -> Dict:
        """Get all GPU data in one call
        
        Returns:
            Dictionary with GPU metrics:
            - name: GPU model name
            - temp_gpu: Core temperature (°C)
            - temp_hotspot: Hotspot temperature (°C) or None
            - clock_gpu: GPU core clock (MHz)
            - clock_mem: Memory clock (MHz)
            - load_gpu: GPU utilization (0-100%)
            - load_mem: Memory utilization (0-100%)
            - power: Power consumption (Watts)
            - fan_speed: Fan speed (0-100%)
        
        Note:
            Returns zeros/None if GPU unavailable
        """
        if not self._available:
            return self._get_empty_data()
        
        try:
            # Temperature readings
            temp_gpu = self._get_temperature()
            temp_hotspot = self._get_hotspot_temperature()
            
            # Clock speeds
            clock_gpu = self._get_clock_speed(pynvml.NVML_CLOCK_GRAPHICS)
            clock_mem = self._get_clock_speed(pynvml.NVML_CLOCK_MEM)
            
            # Utilization
            load_gpu, load_mem = self._get_utilization()
            
            # Power and fan
            power = self._get_power_usage()
            fan_speed = self._get_fan_speed()
            
            return {
                "name": self._name,
                "temp_gpu": temp_gpu,
                "temp_hotspot": temp_hotspot,
                "clock_gpu": clock_gpu,
                "clock_mem": clock_mem,
                "load_gpu": load_gpu,
                "load_mem": load_mem,
                "power": power,
                "fan_speed": fan_speed,
            }
            
        except Exception as e:
            self._log_error(f"Error reading GPU data: {e}")
            # Try to reinitialize (but limit attempts)
            if self._init_attempts < self._max_init_attempts:
                self._init_attempts += 1
                self._log_info(f"Attempting GPU reinitialization ({self._init_attempts}/{self._max_init_attempts})")
                if self._initialize_nvml():
                    self._init_attempts = 0  # Reset on success
            return self._get_empty_data()
    
    def _get_temperature(self) -> int:
        """Get GPU core temperature
        
        Returns:
            Temperature in Celsius
        """
        try:
            return pynvml.nvmlDeviceGetTemperature(
                self._handle, pynvml.NVML_TEMPERATURE_GPU
            )
        except Exception as e:
            self._log_debug(f"Failed to read GPU temperature: {e}")
            return 0
    
    def _get_hotspot_temperature(self) -> Optional[int]:
        """Get GPU hotspot temperature (not available on all GPUs)
        
        Returns:
            Hotspot temperature in Celsius, or None if unavailable
        """
        try:
            return pynvml.nvmlDeviceGetTemperature(
                self._handle, pynvml.NVML_TEMPERATURE_HOTSPOT
            )
        except:
            # Hotspot not available on all GPUs - silent fail
            return None
    
    def _get_clock_speed(self, clock_type: int) -> int:
        """Get GPU clock speed
        
        Args:
            clock_type: NVML clock type (GRAPHICS or MEM)
        
        Returns:
            Clock speed in MHz
        """
        try:
            return pynvml.nvmlDeviceGetClockInfo(self._handle, clock_type)
        except Exception as e:
            self._log_debug(f"Failed to read clock speed: {e}")
            return 0
    
    def _get_utilization(self) -> tuple[int, int]:
        """Get GPU and memory utilization
        
        Returns:
            Tuple of (gpu_load, mem_load) in percentage (0-100)
        """
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self._handle)
            return util.gpu, util.memory
        except Exception as e:
            self._log_debug(f"Failed to read utilization: {e}")
            return 0, 0
    
    def _get_power_usage(self) -> float:
        """Get GPU power consumption
        
        Returns:
            Power in Watts
        """
        try:
            # NVML returns milliwatts
            return pynvml.nvmlDeviceGetPowerUsage(self._handle) / 1000.0
        except:
            # Power reading not available on all GPUs
            return 0.0
    
    def _get_fan_speed(self) -> int:
        """Get GPU fan speed
        
        Returns:
            Fan speed percentage (0-100), or 0 if unavailable
        """
        try:
            return pynvml.nvmlDeviceGetFanSpeed(self._handle)
        except:
            # Fan speed not available on all GPUs
            return 0
    
    def _get_empty_data(self) -> Dict:
        """Return empty data structure when GPU unavailable
        
        Returns:
            Dictionary with all fields set to 0/None
        """
        return {
            "name": self._name,
            "temp_gpu": 0,
            "temp_hotspot": None,
            "clock_gpu": 0,
            "clock_mem": 0,
            "load_gpu": 0,
            "load_mem": 0,
            "power": 0.0,
            "fan_speed": 0,
        }
    
    def cleanup(self):
        """Cleanup NVML resources
        
        Should be called when monitor is no longer needed.
        Safe to call multiple times.
        """
        if self._available:
            try:
                pynvml.nvmlShutdown()
                self._available = False
                self._log_info("GPU monitor shutdown")
            except Exception as e:
                self._log_debug(f"NVML shutdown error (non-critical): {e}")
    
    # Logging helpers
    def _log_debug(self, message: str):
        if logger:
            logger.debug(f"[GPU Monitor] {message}")
    
    def _log_info(self, message: str):
        if logger:
            logger.info(f"[GPU Monitor] {message}")
        else:
            print(f"[GPU Monitor] INFO: {message}")
    
    def _log_warning(self, message: str):
        if logger:
            logger.warning(f"[GPU Monitor] {message}")
        else:
            print(f"[GPU Monitor] WARNING: {message}")
    
    def _log_error(self, message: str):
        if logger:
            logger.error(f"[GPU Monitor] {message}")
        else:
            print(f"[GPU Monitor] ERROR: {message}")
    
    def __del__(self):
        """Destructor - cleanup on object deletion"""
        self.cleanup()


if __name__ == "__main__":
    # Test GPU monitor
    print("Testing GPU Monitor...\n")
    
    monitor = GPUMonitor()
    
    if monitor.is_available():
        print(f"✅ GPU Available: {monitor.get_name()}\n")
        
        data = monitor.get_data()
        print("GPU Data:")
        for key, value in data.items():
            if value is not None:
                print(f"  {key:15s}: {value}")
        
        print("\n✅ GPU monitoring working!")
    else:
        print("❌ No GPU detected or NVML unavailable")
        print(f"   Reason: {monitor._name}")
    
    monitor.cleanup()
    print("\n✅ Cleanup complete")
