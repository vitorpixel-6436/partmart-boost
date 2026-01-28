"""GPU monitoring module for PartMart Boost"""
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
        self.gpu_index = gpu_index
        self.handle = None
        self.gpu_name = "Unknown GPU"
        super().__init__()
    
    def _initialize(self) -> bool:
        """Initialize NVIDIA GPU monitoring"""
        if not PYNVML_AVAILABLE:
            self._set_error("pynvml not installed")
            return False
        
        try:
            pynvml.nvmlInit()
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
                - temperature: Core temperature (°C)
                - temperature_hotspot: Hotspot temperature (°C) if available
                - clock_graphics: Graphics clock (MHz)
                - clock_memory: Memory clock (MHz)
                - load_gpu: GPU utilization (%)
                - load_memory: Memory utilization (%)
                - power_usage: Power usage (W)
                - power_limit: Power limit (W)
                - fan_speed: Fan speed (%)
                - memory_total: Total memory (MB)
                - memory_used: Used memory (MB)
                - memory_free: Free memory (MB)
        """
        if not self.available:
            return {}
        
        try:
            data = {
                'name': self.gpu_name,
            }
            
            # Temperature (core)
            try:
                data['temperature'] = pynvml.nvmlDeviceGetTemperature(
                    self.handle, pynvml.NVML_TEMPERATURE_GPU
                )
            except:
                data['temperature'] = None
            
            # Temperature (hotspot) - more accurate
            try:
                data['temperature_hotspot'] = pynvml.nvmlDeviceGetTemperature(
                    self.handle, pynvml.NVML_TEMPERATURE_HOTSPOT
                )
            except:
                data['temperature_hotspot'] = None
            
            # Clock speeds
            try:
                data['clock_graphics'] = pynvml.nvmlDeviceGetClockInfo(
                    self.handle, pynvml.NVML_CLOCK_GRAPHICS
                )
            except:
                data['clock_graphics'] = None
            
            try:
                data['clock_memory'] = pynvml.nvmlDeviceGetClockInfo(
                    self.handle, pynvml.NVML_CLOCK_MEM
                )
            except:
                data['clock_memory'] = None
            
            # Utilization
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
                data['load_gpu'] = util.gpu
                data['load_memory'] = util.memory
            except:
                data['load_gpu'] = None
                data['load_memory'] = None
            
            # Power
            try:
                data['power_usage'] = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000  # mW to W
            except:
                data['power_usage'] = None
            
            try:
                data['power_limit'] = pynvml.nvmlDeviceGetPowerManagementLimit(self.handle) / 1000
            except:
                data['power_limit'] = None
            
            # Fan speed
            try:
                data['fan_speed'] = pynvml.nvmlDeviceGetFanSpeed(self.handle)
            except:
                data['fan_speed'] = None
            
            # Memory
            try:
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
                data['memory_total'] = mem_info.total // (1024 * 1024)  # bytes to MB
                data['memory_used'] = mem_info.used // (1024 * 1024)
                data['memory_free'] = mem_info.free // (1024 * 1024)
            except:
                data['memory_total'] = None
                data['memory_used'] = None
                data['memory_free'] = None
            
            return data
            
        except Exception as e:
            self._set_error(f"Failed to get GPU data: {str(e)}")
            return {}
    
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
        
        if use_hotspot and data.get('temperature_hotspot') is not None:
            return data['temperature_hotspot']
        
        return data.get('temperature')
    
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
        
        if data.get('memory_total') is not None:
            return {
                'total': data['memory_total'],
                'used': data['memory_used'],
                'free': data['memory_free'],
                'percent': (data['memory_used'] / data['memory_total'] * 100) if data['memory_total'] > 0 else 0
            }
        return None
    
    def shutdown(self):
        """Cleanup GPU monitoring"""
        if PYNVML_AVAILABLE and self.available:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
    
    def __del__(self):
        """Destructor"""
        self.shutdown()

if __name__ == "__main__":
    # Test GPU monitor
    monitor = GPUMonitor()
    
    if monitor.is_available():
        print(f"✅ GPU detected: {monitor.get_name()}")
        
        data = monitor.get_data()
        print(f"\n📊 GPU Data:")
        for key, value in data.items():
            if value is not None:
                print(f"  {key}: {value}")
        
        print(f"\n🌡️ Temperature: {monitor.get_temperature()}°C")
        print(f"⚡ Load: {monitor.get_load()}%")
        
        mem = monitor.get_memory_usage()
        if mem:
            print(f"🧠 Memory: {mem['used']}/{mem['total']} MB ({mem['percent']:.1f}%)")
    else:
        print(f"❌ GPU not available: {monitor.get_last_error()}")
    
    monitor.shutdown()
