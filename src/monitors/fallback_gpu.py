#!/usr/bin/env python3
"""Fallback GPU monitor without external dependencies

Version: 0.3.5d - Package 2.3

SOVEREIGNTY: Uses native OS APIs, no pynvml dependency
STABILITY: All subprocess calls have timeouts (v0.3.5d)
SCHEMA: 100% consistent with gpu_monitor.py

Supported platforms:
- Windows: WMIC queries
- Linux: sysfs + lspci
- macOS: (limited support)
"""
import platform
import os
import subprocess
from typing import Dict, Optional
from monitors import BaseMonitor


class FallbackGPUMonitor(BaseMonitor):
    """GPU monitoring using native OS tools
    
    This provides basic GPU monitoring without external dependencies
    for maximum sovereignty and reliability.
    
    v0.3.5d Package 2.3 improvements:
    - Consistent schema with gpu_monitor.py
    - All subprocess calls have timeouts (3s)
    - Added memory_total/used/free fields
    - Health status tracking
    - Better error handling
    
    Schema:
    {
        'name': str,
        'temp_gpu': int or 0,
        'temp_hotspot': None,
        'clock_gpu': int or 0,
        'clock_mem': int or 0,
        'load_gpu': int or 0,
        'load_mem': int or 0,
        'power': int or 0,
        'fan_speed': int or 0,
        'memory_total': int or 0,  # v0.3.5d: Added
        'memory_used': int or 0,   # v0.3.5d: Added
        'memory_free': int or 0,   # v0.3.5d: Added
    }
    """
    
    def __init__(self):
        super().__init__()
        self.os_type = platform.system()
        self.available = False
        self.gpu_name = "Unknown GPU"
        self._last_error: Optional[str] = None
        self._detect_gpu()
    
    def _detect_gpu(self):
        """Detect GPU using native OS tools
        
        v0.3.5d: Added timeout to all subprocess calls
        """
        try:
            if self.os_type == "Windows":
                self._detect_windows()
            elif self.os_type == "Linux":
                self._detect_linux()
            else:
                print(f"[Fallback GPU] Not supported on {self.os_type}")
                self._last_error = f"Platform not supported: {self.os_type}"
        except Exception as e:
            print(f"[Fallback GPU] Detection failed: {e}")
            self._last_error = str(e)
    
    def _detect_windows(self):
        """Detect GPU on Windows using WMIC
        
        v0.3.5d: Added timeout and CREATE_NO_WINDOW
        """
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Timeout
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip():
                    self.gpu_name = lines[1].strip()
                    self.available = True
                    print(f"[Fallback GPU] Detected (WMIC): {self.gpu_name}")
                else:
                    self._last_error = "No GPU found in WMIC output"
            else:
                self._last_error = f"WMIC failed: returncode {result.returncode}"
        
        except subprocess.TimeoutExpired:
            print("[Fallback GPU] WMIC timeout")
            self._last_error = "WMIC command timed out"
        except Exception as e:
            print(f"[Fallback GPU] WMIC failed: {e}")
            self._last_error = f"WMIC error: {e}"
    
    def _detect_linux(self):
        """Detect GPU on Linux using lspci
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['lspci'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Timeout
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
                            print(f"[Fallback GPU] Detected (lspci): {self.gpu_name}")
                            return
            
            # Fallback: try glxinfo
            self._detect_linux_glxinfo()
        
        except subprocess.TimeoutExpired:
            print("[Fallback GPU] lspci timeout")
            self._last_error = "lspci command timed out"
        except Exception as e:
            print(f"[Fallback GPU] lspci failed: {e}")
            self._last_error = f"lspci error: {e}"
    
    def _detect_linux_glxinfo(self):
        """Try glxinfo as fallback
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['glxinfo'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Timeout
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'OpenGL renderer string' in line:
                        self.gpu_name = line.split(':', 1)[1].strip()
                        self.available = True
                        print(f"[Fallback GPU] Detected (glxinfo): {self.gpu_name}")
                        return
            
            self._last_error = "No GPU found via lspci or glxinfo"
        
        except subprocess.TimeoutExpired:
            self._last_error = "glxinfo command timed out"
        except Exception as e:
            self._last_error = f"glxinfo error: {e}"
    
    def get_name(self) -> str:
        """Get GPU name/identifier
        
        Returns:
            GPU name string
        """
        return self.gpu_name if self.available else "No GPU detected (Fallback)"
    
    def is_available(self) -> bool:
        """Check if GPU monitoring is available"""
        return self.available
    
    def get_gpu_data_windows(self) -> Dict:
        """Get GPU data on Windows using native APIs
        
        v0.3.5d: Added timeout
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
            "memory_total": 0,  # v0.3.5d: Added
            "memory_used": 0,   # v0.3.5d: Added
            "memory_free": 0,   # v0.3.5d: Added
        }
        
        # Try to get temperature using Windows Performance Counters
        # (This requires admin rights or specific drivers)
        try:
            result = subprocess.run(
                ['wmic', 'path', 'MSAcpi_ThermalZoneTemperature', 'get', 'CurrentTemperature'],
                capture_output=True,
                text=True,
                timeout=3,  # v0.3.5d: Timeout
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip():
                    try:
                        # Temperature is in tenths of Kelvin
                        temp_kelvin = int(lines[1].strip())
                        temp_celsius = (temp_kelvin / 10) - 273.15
                        if 0 < temp_celsius < 150:  # Sanity check
                            data["temp_gpu"] = int(temp_celsius)
                    except ValueError:
                        pass
        
        except subprocess.TimeoutExpired:
            print("[Fallback GPU] Temperature query timeout")
        except Exception as e:
            print(f"[Fallback GPU] Temperature query failed: {e}")
        
        return data
    
    def get_gpu_data_linux(self) -> Dict:
        """Get GPU data on Linux using sysfs
        
        v0.3.5d Package 2.3: Added memory fields
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
            "memory_total": 0,  # v0.3.5d: Added
            "memory_used": 0,   # v0.3.5d: Added
            "memory_free": 0,   # v0.3.5d: Added
        }
        
        # Try to read temperature from sysfs (NVIDIA/AMD)
        sysfs_paths = [
            '/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input',
            '/sys/class/drm/card1/device/hwmon/hwmon1/temp1_input',
            '/sys/class/hwmon/hwmon0/temp1_input',
            '/sys/class/hwmon/hwmon1/temp1_input',
            '/sys/class/hwmon/hwmon2/temp1_input',
        ]
        
        for path in sysfs_paths:
            try:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp_millidegrees = int(f.read().strip())
                        temp_celsius = temp_millidegrees // 1000
                        # v0.3.5d: Sanity check
                        if 0 < temp_celsius < 150:
                            data["temp_gpu"] = temp_celsius
                            break
            except Exception as e:
                print(f"[Fallback GPU] Failed to read {path}: {e}")
        
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
                                    try:
                                        data[key] = int(mhz_str)
                                    except ValueError:
                                        pass
                                    break
            except Exception as e:
                print(f"[Fallback GPU] Failed to read {path}: {e}")
        
        # v0.3.5d: Try to get memory info from sysfs
        memory_paths = [
            '/sys/class/drm/card0/device/mem_info_vram_total',
            '/sys/class/drm/card0/device/mem_info_vram_used',
        ]
        
        try:
            if os.path.exists(memory_paths[0]):
                with open(memory_paths[0], 'r') as f:
                    total_bytes = int(f.read().strip())
                    data['memory_total'] = total_bytes // (1024 * 1024)  # MB
            
            if os.path.exists(memory_paths[1]):
                with open(memory_paths[1], 'r') as f:
                    used_bytes = int(f.read().strip())
                    data['memory_used'] = used_bytes // (1024 * 1024)  # MB
                    data['memory_free'] = data['memory_total'] - data['memory_used']
        except Exception as e:
            print(f"[Fallback GPU] Memory info read failed: {e}")
        
        return data
    
    def get_gpu_data(self) -> Dict:
        """Get GPU data using native OS APIs
        
        Returns:
            Dictionary with GPU metrics (consistent schema with gpu_monitor.py)
        
        v0.3.5d Package 2.3: Consistent schema
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
                "memory_total": 0,  # v0.3.5d: Added
                "memory_used": 0,   # v0.3.5d: Added
                "memory_free": 0,   # v0.3.5d: Added
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
                "memory_total": 0,  # v0.3.5d: Added
                "memory_used": 0,   # v0.3.5d: Added
                "memory_free": 0,   # v0.3.5d: Added
            }
    
    def get_data(self) -> Dict:
        """Alias for get_gpu_data() for interface compatibility
        
        Returns:
            Dictionary with GPU metrics
        """
        return self.get_gpu_data()
    
    def get_health_status(self) -> Dict:
        """Get monitor health status
        
        Returns:
            Health info dictionary
        
        v0.3.5d Package 2.3: New method
        
        Example:
            >>> health = monitor.get_health_status()
            >>> if not health['available']:
            >>>     print(f"Error: {health['error']}")
        """
        return {
            'available': self.available,
            'name': self.get_name(),
            'error': self._last_error,
            'platform': self.os_type,
        }


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("FallbackGPUMonitor v0.3.5d Package 2.3 Test")
    print("="*60)
    
    monitor = FallbackGPUMonitor()
    
    print(f"\n[Info] GPU Name: {monitor.get_name()}")
    print(f"[Info] Available: {monitor.is_available()}")
    
    # Health status
    health = monitor.get_health_status()
    print(f"\n[Health] Status:")
    print(f"  Available: {health['available']}")
    print(f"  Platform: {health['platform']}")
    if health['error']:
        print(f"  Error: {health['error']}")
    
    if monitor.is_available():
        print("\n[Test] GPU Data Schema (v0.3.5d Package 2.3):")
        data = monitor.get_gpu_data()
        
        # Check required fields
        required_fields = [
            'name', 'temp_gpu', 'temp_hotspot', 'clock_gpu', 'clock_mem',
            'load_gpu', 'load_mem', 'power', 'fan_speed',
            'memory_total', 'memory_used', 'memory_free'  # v0.3.5d: New fields
        ]
        
        print("\n  Schema Validation:")
        all_present = True
        for field in required_fields:
            if field in data:
                value = data[field]
                # Show non-zero values
                if value and value != 0:
                    print(f"    ✅ {field}: {value}")
                else:
                    print(f"    ✅ {field}: (empty)")
            else:
                print(f"    ❌ {field}: MISSING")
                all_present = False
        
        if all_present:
            print("\n  ✅ Schema is consistent with gpu_monitor.py")
        else:
            print("\n  ❌ Schema inconsistency detected")
        
        # Show available data
        print("\n  Available Data:")
        print(f"    GPU: {data['name']}")
        if data['temp_gpu'] > 0:
            print(f"    Temperature: {data['temp_gpu']}°C")
        if data['clock_gpu'] > 0:
            print(f"    GPU Clock: {data['clock_gpu']} MHz")
        if data['clock_mem'] > 0:
            print(f"    Memory Clock: {data['clock_mem']} MHz")
        if data['memory_total'] > 0:
            print(f"    Memory: {data['memory_used']}/{data['memory_total']} MB")
    else:
        print("\n[Info] GPU not detected with fallback monitor")
    
    print("\n" + "="*60)
    print("✅ FallbackGPUMonitor v0.3.5d Package 2.3")
    print("  - Schema consistent with gpu_monitor.py")
    print("  - All subprocess calls have timeouts (3s)")
    print("  - Memory fields added (memory_total/used/free)")
    print("  - Health status tracking")
    print("  - No hangs on missing utilities")
    print("="*60)
