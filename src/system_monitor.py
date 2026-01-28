"""Real-time system monitoring for GPU, CPU, RAM"""
import pynvml
import psutil
import platform
from typing import Dict, Optional


class SystemMonitor:
    """Monitor GPU, CPU, RAM in real-time"""
    
    def __init__(self):
        self.gpu_available = False
        self.gpu_handle = None
        self.gpu_name = "No GPU detected"
        
        try:
            pynvml.nvmlInit()
            self.gpu_available = True
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.gpu_name = pynvml.nvmlDeviceGetName(self.gpu_handle)
            if isinstance(self.gpu_name, bytes):
                self.gpu_name = self.gpu_name.decode('utf-8')
        except Exception as e:
            print(f"GPU not available: {e}")
    
    def get_gpu_data(self) -> Dict:
        """Get GPU temperature, clock, load, memory"""
        if not self.gpu_available:
            return {
                "name": self.gpu_name,
                "temp_gpu": 0,
                "temp_hotspot": None,
                "clock_gpu": 0,
                "clock_mem": 0,
                "load_gpu": 0,
                "load_mem": 0,
                "power": 0,
                "fan_speed": 0,
            }
        
        try:
            # Temperature
            temp_gpu = pynvml.nvmlDeviceGetTemperature(
                self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU
            )
            
            # Try to get hotspot temperature (may not be available on all GPUs)
            temp_hotspot = None
            try:
                temp_hotspot = pynvml.nvmlDeviceGetTemperature(
                    self.gpu_handle, pynvml.NVML_TEMPERATURE_HOTSPOT
                )
            except:
                pass
            
            # Clock speeds
            clock_gpu = pynvml.nvmlDeviceGetClockInfo(
                self.gpu_handle, pynvml.NVML_CLOCK_GRAPHICS
            )
            clock_mem = pynvml.nvmlDeviceGetClockInfo(
                self.gpu_handle, pynvml.NVML_CLOCK_MEM
            )
            
            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
            load_gpu = util.gpu
            load_mem = util.memory
            
            # Power draw
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle) / 1000  # mW to W
            except:
                power = 0
            
            # Fan speed
            try:
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(self.gpu_handle)
            except:
                fan_speed = 0
            
            return {
                "name": self.gpu_name,
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
            print(f"Error reading GPU data: {e}")
            return {
                "name": self.gpu_name,
                "temp_gpu": 0,
                "temp_hotspot": None,
                "clock_gpu": 0,
                "clock_mem": 0,
                "load_gpu": 0,
                "load_mem": 0,
                "power": 0,
                "fan_speed": 0,
            }
    
    def get_cpu_data(self) -> Dict:
        """Get CPU load and temperature"""
        cpu_load = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count(logical=True)
        
        # Temperature (platform dependent)
        cpu_temp = None
        try:
            if platform.system() == "Windows":
                # Windows: try OpenHardwareMonitor or CoreTemp
                # This requires external software running
                # Fallback: use psutil.sensors_temperatures() if available
                temps = psutil.sensors_temperatures()
                if temps:
                    # Look for CPU package temperature
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or 'core' in name.lower():
                            for entry in entries:
                                if 'package' in entry.label.lower() or entry.label == '':
                                    cpu_temp = entry.current
                                    break
                            if cpu_temp:
                                break
            else:
                # Linux/Mac: psutil usually works
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    cpu_temp = temps['coretemp'][0].current
        except:
            pass
        
        return {
            "load": cpu_load,
            "temp": cpu_temp,
            "freq": cpu_freq.current if cpu_freq else 0,
            "count": cpu_count,
        }
    
    def get_ram_data(self) -> Dict:
        """Get RAM usage and speed"""
        ram = psutil.virtual_memory()
        
        ram_total = ram.total / (1024**3)  # GB
        ram_used = ram.used / (1024**3)
        ram_free = ram.available / (1024**3)
        ram_percent = ram.percent
        
        # Try to detect RAM speed and XMP status (Windows only)
        ram_speed = 0
        xmp_enabled = False
        
        if platform.system() == "Windows":
            try:
                import wmi
                w = wmi.WMI()
                for mem in w.Win32_PhysicalMemory():
                    if hasattr(mem, 'ConfiguredClockSpeed') and mem.ConfiguredClockSpeed:
                        ram_speed = mem.ConfiguredClockSpeed  # MHz
                        break
                
                # Heuristic: if speed > 2133 for DDR4 or > 1600 for DDR3, XMP likely enabled
                if ram_speed > 2133:
                    xmp_enabled = True
            except:
                pass
        
        return {
            "total": ram_total,
            "used": ram_used,
            "free": ram_free,
            "percent": ram_percent,
            "speed": ram_speed,
            "xmp_enabled": xmp_enabled,
        }
    
    def get_all_data(self) -> Dict:
        """Get all system data in one call"""
        return {
            "gpu": self.get_gpu_data(),
            "cpu": self.get_cpu_data(),
            "ram": self.get_ram_data(),
        }
    
    def cleanup(self):
        """Cleanup NVML"""
        if self.gpu_available:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


if __name__ == "__main__":
    # Test
    monitor = SystemMonitor()
    data = monitor.get_all_data()
    
    print("=== GPU ===")
    for k, v in data["gpu"].items():
        print(f"{k}: {v}")
    
    print("\n=== CPU ===")
    for k, v in data["cpu"].items():
        print(f"{k}: {v}")
    
    print("\n=== RAM ===")
    for k, v in data["ram"].items():
        print(f"{k}: {v}")
    
    monitor.cleanup()
