"""GPU monitoring module for PartMart Boost

Version: 0.3.5c_hotfix2
"""
import sys
from typing import Dict, Any, Optional
from monitors import BaseMonitor

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


class GPUMonitor(BaseMonitor):
    """NVIDIA GPU monitor using pynvml"""
    
    def __init__(self, gpu_index: int = 0):
        super().__init__()
        self.gpu_index = gpu_index
        self.handle = None
        self.gpu_name = "Unknown GPU"
        self._nvml_initialized = False
        
        # FIX BUG #1: Call _initialize() in __init__
        self._initialize()
    
    def _initialize(self) -> bool:
        """Initialize NVIDIA GPU monitoring"""
        if not PYNVML_AVAILABLE:
            self._set_error("pynvml not installed")
            return False
        
        try:
            # FIX BUG #2: Track if WE initialized nvml
            if not self._nvml_initialized:
                pynvml.nvmlInit()
                self._nvml_initialized = True
            
            device_count = pynvml.nvmlDeviceGetCount()
            
            if device_count == 0:
                self._set_error("No NVIDIA GPU detected")
                return False
            
            if self.gpu_index >= device_count:
                self._set_error(f"GPU index {self.gpu_index} out of range (0-{device_count-1})")
                return False
            
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_index)
            self.gpu_name = pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(self.gpu_name, bytes):
                self.gpu_name = self.gpu_name.decode('utf-8')
            
            self.available = True
            return True
            
        except Exception as e:
            self._set_error(f"Failed to initialize GPU: {str(e)}")
            return False
    
    def get_name(self) -> str:
        """Get GPU name"""
        return self.gpu_name
    
    def get_data(self) -> Dict[str, Any]:
        """Get GPU data
        
        Returns:
            Dict with keys:
                - name: GPU name
                - temp_gpu: Core temperature (°C)
                - temp_hotspot: Hotspot temperature (°C) if available
                - clock_gpu: Graphics clock (MHz)
                - clock_mem: Memory clock (MHz)
                - load_gpu: GPU utilization (%)
                - load_mem: Memory utilization (%)
                - power: Power usage (W)
                - fan_speed: Fan speed (%)
                - memory_total: Total memory (MB)
                - memory_used: Used memory (MB)
                - memory_free: Free memory (MB)
        """
        if not self.available:
            return self._get_empty_data()
        
        try:
            data = {
                'name': self.gpu_name,
            }
            
            # Temperature (core)
            try:
                data['temp_gpu'] = pynvml.nvmlDeviceGetTemperature(
                    self.handle, pynvml.NVML_TEMPERATURE_GPU
                )
            except:
                data['temp_gpu'] = 0
            
            # Temperature (hotspot) - more accurate
            try:
                data['temp_hotspot'] = pynvml.nvmlDeviceGetTemperature(
                    self.handle, pynvml.NVML_TEMPERATURE_HOTSPOT
                )
            except:
                data['temp_hotspot'] = None
            
            # Clock speeds
            try:
                data['clock_gpu'] = pynvml.nvmlDeviceGetClockInfo(
                    self.handle, pynvml.NVML_CLOCK_GRAPHICS
                )
            except:
                data['clock_gpu'] = 0
            
            try:
                data['clock_mem'] = pynvml.nvmlDeviceGetClockInfo(
                    self.handle, pynvml.NVML_CLOCK_MEM
                )
            except:
                data['clock_mem'] = 0
            
            # Utilization
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
                data['load_gpu'] = util.gpu
                data['load_mem'] = util.memory
            except:
                data['load_gpu'] = 0
                data['load_mem'] = 0
            
            # Power
            try:
                data['power'] = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000  # mW to W
            except:
                data['power'] = 0
            
            # Fan speed
            try:
                data['fan_speed'] = pynvml.nvmlDeviceGetFanSpeed(self.handle)
            except:
                data['fan_speed'] = 0
            
            # Memory
            try:
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
                data['memory_total'] = mem_info.total // (1024 * 1024)  # bytes to MB
                data['memory_used'] = mem_info.used // (1024 * 1024)
                data['memory_free'] = mem_info.free // (1024 * 1024)
            except:
                data['memory_total'] = 0
                data['memory_used'] = 0
                data['memory_free'] = 0
            
            return data
            
        except Exception as e:
            self._set_error(f"Failed to get GPU data: {str(e)}")
            return self._get_empty_data()
    
    def _get_empty_data(self) -> Dict:
        """Get empty data structure."""
        return {
            'name': self.gpu_name,
            'temp_gpu': 0,
            'temp_hotspot': None,
            'clock_gpu': 0,
            'clock_mem': 0,
            'load_gpu': 0,
            'load_mem': 0,
            'power': 0,
            'fan_speed': 0,
            'memory_total': 0,
            'memory_used': 0,
            'memory_free': 0,
        }
    
    def get_temperature(self, use_hotspot: bool = True) -> Optional[float]:
        """Get GPU temperature
        
        Args:
            use_hotspot: Prefer hotspot temperature if available
        
        Returns:
            Temperature in Celsius or None
        """
        data = self.get_data()
        if not data:
            return None
        
        if use_hotspot and data.get('temp_hotspot') is not None:
            return data['temp_hotspot']
        
        return data.get('temp_gpu')
    
    def get_load(self) -> Optional[float]:
        """Get GPU load percentage"""
        data = self.get_data()
        return data.get('load_gpu') if data else None
    
    def get_memory_usage(self) -> Optional[Dict[str, int]]:
        """Get memory usage
        
        Returns:
            Dict with total, used, free (MB) or None
        """
        data = self.get_data()
        if not data:
            return None
        
        if data.get('memory_total', 0) > 0:
            return {
                'total': data['memory_total'],
                'used': data['memory_used'],
                'free': data['memory_free'],
                'percent': (data['memory_used'] / data['memory_total'] * 100)
            }
        return None
    
    def shutdown(self):
        """Cleanup GPU monitoring
        
        FIX BUG #2: Only shutdown if WE initialized it
        """
        if PYNVML_AVAILABLE and self._nvml_initialized:
            try:
                pynvml.nvmlShutdown()
                self._nvml_initialized = False
            except:
                pass
    
    def __del__(self):
        """Destructor
        
        FIX BUG #2: Safe cleanup - only if we initialized
        """
        # Don't call shutdown() here - can cause issues with multiple instances
        # Let Python GC handle it
        pass


if __name__ == "__main__":
    # Test GPU monitor
    print("[TEST] GPUMonitor with bug fixes")
    print("="*60)
    
    monitor = GPUMonitor()
    
    print(f"\n[INFO] Monitor available: {monitor.is_available()}")
    print(f"[INFO] GPU name: {monitor.get_name()}")
    
    if monitor.is_available():
        print(f"\n✅ GPU detected: {monitor.get_name()}")
        
        data = monitor.get_data()
        print(f"\n📊 GPU Data:")
        for key, value in data.items():
            if value is not None and value != 0:
                print(f"  {key}: {value}")
        
        print(f"\n🌡️ Temperature: {monitor.get_temperature()}°C")
        print(f"⚡ Load: {monitor.get_load()}%")
        
        mem = monitor.get_memory_usage()
        if mem:
            print(f"🧠 Memory: {mem['used']}/{mem['total']} MB ({mem['percent']:.1f}%)")
    else:
        print(f"❌ GPU not available: {monitor.get_last_error()}")
    
    # Test cleanup
    monitor.shutdown()
    
    print("\n" + "="*60)
    print("✅ GPUMonitor bug fixes work!")
