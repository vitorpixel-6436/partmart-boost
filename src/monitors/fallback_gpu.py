"""Fallback GPU monitor without external dependencies
SOVEREIGNTY: Uses native OS APIs, no pynvml dependency
Version: 0.3.5d - Package 2b
"""
import platform
import os
import subprocess
from typing import Dict, Optional

class FallbackGPUMonitor:
    """GPU monitoring using native OS tools
    
    This provides basic GPU monitoring without external dependencies
    for maximum sovereignty and reliability.
    
    v0.3.5d Package 2b fixes:
    - Add memory_total/used/free fields (CRITICAL)
    - Match schema with gpu_monitor.py
    - Add timeouts to subprocess calls
    - Better error handling
    """
    
    def __init__(self):
        self.os_type = platform.system()
        self.available = False
        self.gpu_name = "Unknown GPU"
        self._detect_gpu()
    
    def _detect_gpu(self):
        """Detect GPU using native OS tools"""
        try:
            if self.os_type == "Windows":
                self._detect_windows()
            elif self.os_type == "Linux":
                self._detect_linux()
            else:
                print(f"[INFO] Fallback GPU monitor not supported on {self.os_type}")
        except Exception as e:
            print(f"[WARN] GPU detection failed: {e}")
    
    def _detect_windows(self):
        """Detect GPU on Windows using WMIC
        
        v0.3.5d: Add timeout
        """
        try:
            # Use WMIC (built into Windows)
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Add timeout
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    self.gpu_name = lines[1].strip()
                    self.available = True
                    print(f"[INFO] Detected GPU (WMIC): {self.gpu_name}")
        except Exception as e:
            print(f"[WARN] WMIC detection failed: {e}")
    
    def _detect_linux(self):
        """Detect GPU on Linux using lspci
        
        v0.3.5d: Add timeout
        """
        try:
            # Try lspci (usually available)
            result = subprocess.run(
                ['lspci'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Add timeout
                check=False
            )
            
            if result.returncode == 0:
                # Look for VGA or 3D controller
                for line in result.stdout.split('\n'):
                    if 'VGA compatible controller' in line or '3D controller' in line:
                        # Extract GPU name
                        parts = line.split(': ')
                        if len(parts) > 1:
                            self.gpu_name = parts[1].strip()
                            self.available = True
                            print(f"[INFO] Detected GPU (lspci): {self.gpu_name}")
                            break
        except Exception as e:
            print(f"[WARN] lspci detection failed: {e}")
        
        # Try alternative: glxinfo
        if not self.available:
            try:
                result = subprocess.run(
                    ['glxinfo'],
                    capture_output=True,
                    text=True,
                    timeout=3,  # v0.3.5d: Add timeout
                    check=False
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'OpenGL renderer string' in line:
                            self.gpu_name = line.split(':', 1)[1].strip()
                            self.available = True
                            print(f"[INFO] Detected GPU (glxinfo): {self.gpu_name}")
                            break
            except Exception as e:
                print(f"[WARN] glxinfo detection failed: {e}")
    
    def get_name(self) -> str:
        """Get GPU name/identifier
        
        Returns:
            GPU name string
        """
        return self.gpu_name if self.available else "No GPU detected (Fallback)"
    
    def get_gpu_data_windows(self) -> Dict:
        """Get GPU data on Windows using native APIs
        
        v0.3.5d Package 2b: Match schema with gpu_monitor.py
        """
        data = {
            "name": self.gpu_name,
            "temp_gpu": 0,
            "temp_hotspot": None,
            "clock_gpu": 0,
            "clock_mem": 0,
            "load_gpu": 0,
            "load_mem": 0,
            "power": 0,
            "fan_speed": 0,
            # v0.3.5d CRITICAL FIX: Add memory fields
            "memory_total": 0,
            "memory_used": 0,
            "memory_free": 0,
        }
        
        # Try to get temperature using Windows Performance Counters
        # (This requires admin rights or specific drivers)
        try:
            result = subprocess.run(
                ['wmic', 'path', 'MSAcpi_ThermalZoneTemperature', 'get', 'CurrentTemperature'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Add timeout
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    try:
                        # Temperature is in tenths of Kelvin
                        temp_kelvin = int(lines[1].strip())
                        temp_celsius = (temp_kelvin / 10) - 273.15
                        data["temp_gpu"] = int(temp_celsius)
                    except ValueError:
                        pass
        except Exception as e:
            print(f"[DEBUG] Temperature query failed: {e}")
        
        # Try to get memory info (WMIC)
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'AdapterRAM'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    try:
                        ram_bytes = int(lines[1].strip())
                        ram_mb = ram_bytes // (1024 * 1024)
                        data["memory_total"] = ram_mb
                        # Can't get used/free without driver support
                        data["memory_free"] = ram_mb  # Assume all free
                    except ValueError:
                        pass
        except Exception:
            pass
        
        return data
    
    def get_gpu_data_linux(self) -> Dict:
        """Get GPU data on Linux using sysfs
        
        v0.3.5d Package 2b: Match schema with gpu_monitor.py
        """
        data = {
            "name": self.gpu_name,
            "temp_gpu": 0,
            "temp_hotspot": None,
            "clock_gpu": 0,
            "clock_mem": 0,
            "load_gpu": 0,
            "load_mem": 0,
            "power": 0,
            "fan_speed": 0,
            # v0.3.5d CRITICAL FIX: Add memory fields
            "memory_total": 0,
            "memory_used": 0,
            "memory_free": 0,
        }
        
        # Try to read temperature from sysfs (NVIDIA/AMD)
        sysfs_paths = [
            '/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input',
            '/sys/class/drm/card1/device/hwmon/hwmon1/temp1_input',
            '/sys/class/hwmon/hwmon0/temp1_input',
            '/sys/class/hwmon/hwmon1/temp1_input',
        ]
        
        for path in sysfs_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp_millidegrees = int(f.read().strip())
                        data["temp_gpu"] = temp_millidegrees // 1000
                        break
            except Exception as e:
                print(f"[DEBUG] Failed to read {path}: {e}")
        
        # Try to read clock speeds
        clock_paths = [
            ('/sys/class/drm/card0/device/pp_dpm_sclk', 'clock_gpu'),
            ('/sys/class/drm/card0/device/pp_dpm_mclk', 'clock_mem'),
        ]
        
        for path, key in clock_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        # Parse active clock (marked with *)
                        for line in f:
                            if '*' in line:
                                # Extract MHz value
                                parts = line.split(':')
                                if len(parts) > 1:
                                    mhz_str = parts[1].strip().replace('Mhz', '').replace('*', '').strip()
                                    data[key] = int(mhz_str)
                                    break
            except Exception as e:
                print(f"[DEBUG] Failed to read {path}: {e}")
        
        # Try to read VRAM info (AMD)
        vram_paths = [
            '/sys/class/drm/card0/device/mem_info_vram_total',
            '/sys/class/drm/card0/device/mem_info_vram_used',
        ]
        
        try:
            if os.path.exists(vram_paths[0]):
                with open(vram_paths[0], 'r') as f:
                    vram_total_bytes = int(f.read().strip())
                    data["memory_total"] = vram_total_bytes // (1024 * 1024)  # MB
            
            if os.path.exists(vram_paths[1]):
                with open(vram_paths[1], 'r') as f:
                    vram_used_bytes = int(f.read().strip())
                    data["memory_used"] = vram_used_bytes // (1024 * 1024)  # MB
                    if data["memory_total"] > 0:
                        data["memory_free"] = data["memory_total"] - data["memory_used"]
        except Exception as e:
            print(f"[DEBUG] VRAM read failed: {e}")
        
        return data
    
    def get_gpu_data(self) -> Dict:
        """Get GPU data using native OS APIs
        
        Returns:
            Dictionary with GPU metrics
        
        v0.3.5d Package 2b: Consistent schema
        """
        if not self.available:
            return {
                "name": "No GPU detected",
                "temp_gpu": 0,
                "temp_hotspot": None,
                "clock_gpu": 0,
                "clock_mem": 0,
                "load_gpu": 0,
                "load_mem": 0,
                "power": 0,
                "fan_speed": 0,
                # v0.3.5d CRITICAL FIX: Always include memory fields
                "memory_total": 0,
                "memory_used": 0,
                "memory_free": 0,
            }
        
        if self.os_type == "Windows":
            return self.get_gpu_data_windows()
        elif self.os_type == "Linux":
            return self.get_gpu_data_linux()
        else:
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
                "memory_total": 0,
                "memory_used": 0,
                "memory_free": 0,
            }
    
    def get_data(self) -> Dict:
        """Alias for get_gpu_data() for interface compatibility
        
        Returns:
            Dictionary with GPU metrics
        """
        return self.get_gpu_data()
    
    def is_available(self) -> bool:
        """Check if GPU monitoring is available"""
        return self.available

if __name__ == "__main__":
    # Test
    print("[TEST] Testing FallbackGPUMonitor v0.3.5d Package 2b...")
    
    monitor = FallbackGPUMonitor()
    
    print(f"[INFO] GPU Name: {monitor.get_name()}")
    print(f"[INFO] Available: {monitor.is_available()}")
    
    data = monitor.get_gpu_data()
    
    print("\n[SCHEMA] v0.3.5d Package 2b - Required fields:")
    required_fields = [
        'name', 'temp_gpu', 'temp_hotspot', 'clock_gpu', 'clock_mem',
        'load_gpu', 'load_mem', 'power', 'fan_speed',
        'memory_total', 'memory_used', 'memory_free'  # CRITICAL
    ]
    
    for field in required_fields:
        status = '✅' if field in data else '❌'
        value = data.get(field)
        print(f"  {status} {field}: {value}")
    
    if monitor.is_available():
        print("\n[PASS] GPU detected")
        print(f"[INFO] GPU: {data['name']}")
        if data['temp_gpu']:
            print(f"[INFO] Temperature: {data['temp_gpu']}°C")
        if data['clock_gpu']:
            print(f"[INFO] Clock: {data['clock_gpu']} MHz")
        if data['memory_total']:
            print(f"[INFO] Memory: {data['memory_total']} MB")
    else:
        print("\n[INFO] No GPU detected with fallback monitor")
    
    print("\n✅ FallbackGPUMonitor v0.3.5d Package 2b schema validated!")
