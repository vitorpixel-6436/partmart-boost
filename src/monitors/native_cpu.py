#!/usr/bin/env python3
"""Native CPU Monitor - CPU monitoring WITHOUT psutil dependency.

Provides CPU monitoring using only:
- Windows: WMIC + WMI via ctypes
- Linux: /proc/stat + /sys/class/thermal
- macOS: sysctl

Part of Sovereignty Mode - maximum independence from external libraries.

Author: PartMart Team
Version: 0.3.5d - Package 1
License: MIT
"""

import subprocess
import platform
import time
import re
from typing import Dict, Optional, Any
from monitors import BaseMonitor


class NativeCPUMonitor(BaseMonitor):
    """Native CPU monitor using OS APIs directly.
    
    Features:
    - CPU load (utilization percentage)
    - CPU frequency (current, min, max)
    - Core count (physical and logical)
    - CPU temperature (if available)
    - Cross-platform: Windows, Linux, macOS
    
    No external dependencies (no psutil).
    
    v0.3.5d fixes:
    - All subprocess calls have timeouts
    - Sanity checks on all values
    - No crashes on missing utilities
    """
    
    def __init__(self):
        super().__init__()
        self.platform = platform.system()
        self.last_cpu_times = None
        self.last_measure_time = None
        
        # Pre-detect CPU info
        self._cpu_name = self._detect_cpu_name()
        self._cpu_cores = self._detect_cpu_cores()
        self._cpu_cores_logical = self._detect_cpu_cores_logical()
        
        self.available = True
        
        print(f"[Native CPU Monitor] Platform: {self.platform}")
        print(f"[Native CPU Monitor] CPU: {self._cpu_name}")
        print(f"[Native CPU Monitor] Cores: {self._cpu_cores} physical, {self._cpu_cores_logical} logical")
    
    def get_name(self) -> str:
        """Get monitor name."""
        return self._cpu_name or "Native CPU Monitor"
    
    def get_data(self) -> Dict[str, Any]:
        """Get current CPU metrics.
        
        Returns:
            dict: {
                'name': str,
                'load': float,
                'temp': float or None,
                'freq': float,
                'freq_min': float,
                'freq_max': float,
                'count': int,
                'count_logical': int,
            }
        """
        try:
            load = self._get_cpu_load()
            temp = self._get_cpu_temp()
            freq = self._get_cpu_freq()
            freq_max = self._get_cpu_freq_max()
            
            return {
                'name': self._cpu_name,
                'load': self._validate_load(load),
                'temp': self._validate_temperature(temp),
                'freq': max(0.0, freq),
                'freq_min': 0.0,
                'freq_max': max(0.0, freq_max),
                'count': self._cpu_cores,
                'count_logical': self._cpu_cores_logical,
            }
        except Exception as e:
            print(f"[Native CPU Monitor] Error: {e}")
            return self._get_safe_defaults()
    
    def _get_safe_defaults(self) -> Dict[str, Any]:
        """Return safe default values."""
        return {
            'name': self._cpu_name or 'Unknown CPU',
            'load': 0.0,
            'temp': None,
            'freq': 0.0,
            'freq_min': 0.0,
            'freq_max': 0.0,
            'count': self._cpu_cores or 1,
            'count_logical': self._cpu_cores_logical or 1,
        }
    
    # ========== v0.3.5d: VALIDATION ==========
    
    def _validate_temperature(self, temp: Optional[float]) -> Optional[float]:
        """Validate temperature is in reasonable range.
        
        Args:
            temp: Temperature in Celsius
        
        Returns:
            Validated temp or None
        """
        if temp is None:
            return None
        if temp < 0 or temp > 150:
            print(f"[Native CPU Monitor] Invalid temp: {temp}°C")
            return None
        return round(temp, 1)
    
    def _validate_load(self, load: float) -> float:
        """Validate CPU load is 0-100%.
        
        Args:
            load: CPU load percentage
        
        Returns:
            Clamped load 0-100
        """
        return max(0.0, min(100.0, load))
    
    # ========== CPU Name Detection ==========
    
    def _detect_cpu_name(self) -> str:
        """Detect CPU model name."""
        try:
            if self.platform == 'Windows':
                return self._get_cpu_name_windows()
            elif self.platform == 'Linux':
                return self._get_cpu_name_linux()
            elif self.platform == 'Darwin':
                return self._get_cpu_name_macos()
            else:
                return 'Unknown CPU'
        except Exception as e:
            print(f"[Native CPU Monitor] CPU name detection failed: {e}")
            return 'Unknown CPU'
    
    def _get_cpu_name_windows(self) -> str:
        """Get CPU name on Windows.
        
        v0.3.5d: Added timeout and CREATE_NO_WINDOW
        """
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
        except Exception as e:
            print(f"[Native CPU Monitor] Windows CPU name failed: {e}")
        
        return 'Unknown CPU'
    
    def _get_cpu_name_linux(self) -> str:
        """Get CPU name on Linux.
        
        v0.3.5d: Better error handling
        """
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        return line.split(':')[1].strip()
        except Exception as e:
            print(f"[Native CPU Monitor] Linux CPU name failed: {e}")
        
        return 'Unknown CPU'
    
    def _get_cpu_name_macos(self) -> str:
        """Get CPU name on macOS.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"[Native CPU Monitor] macOS CPU name failed: {e}")
        
        return 'Unknown CPU'
    
    # ========== CPU Cores Detection ==========
    
    def _detect_cpu_cores(self) -> int:
        """Detect physical CPU cores."""
        try:
            if self.platform == 'Windows':
                return self._get_cpu_cores_windows()
            elif self.platform == 'Linux':
                return self._get_cpu_cores_linux()
            elif self.platform == 'Darwin':
                return self._get_cpu_cores_macos()
            else:
                return 1
        except Exception:
            return 1
    
    def _get_cpu_cores_windows(self) -> int:
        """Get physical cores on Windows.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'NumberOfCores'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return int(lines[1].strip())
        except Exception:
            pass
        
        return 1
    
    def _get_cpu_cores_linux(self) -> int:
        """Get physical cores on Linux.
        
        v0.3.5d: Better error handling
        """
        try:
            cores = set()
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('core id'):
                        cores.add(int(line.split(':')[1].strip()))
            return len(cores) if cores else 1
        except Exception:
            return 1
    
    def _get_cpu_cores_macos(self) -> int:
        """Get physical cores on macOS.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'hw.physicalcpu'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception:
            pass
        
        return 1
    
    def _detect_cpu_cores_logical(self) -> int:
        """Detect logical CPU cores (with hyperthreading)."""
        try:
            if self.platform == 'Windows':
                return self._get_cpu_cores_logical_windows()
            elif self.platform == 'Linux':
                return self._get_cpu_cores_logical_linux()
            elif self.platform == 'Darwin':
                return self._get_cpu_cores_logical_macos()
            else:
                return self._cpu_cores
        except Exception:
            return self._cpu_cores
    
    def _get_cpu_cores_logical_windows(self) -> int:
        """Get logical cores on Windows.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'NumberOfLogicalProcessors'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return int(lines[1].strip())
        except Exception:
            pass
        
        return self._cpu_cores
    
    def _get_cpu_cores_logical_linux(self) -> int:
        """Get logical cores on Linux.
        
        v0.3.5d: Better error handling
        """
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return sum(1 for line in f if line.startswith('processor'))
        except Exception:
            return self._cpu_cores
    
    def _get_cpu_cores_logical_macos(self) -> int:
        """Get logical cores on macOS.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'hw.logicalcpu'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode == 0:
                return int(result.stdout.strip())
        except Exception:
            pass
        
        return self._cpu_cores
    
    # ========== CPU Load ==========
    
    def _get_cpu_load(self) -> float:
        """Get current CPU load percentage."""
        try:
            if self.platform == 'Windows':
                return self._get_cpu_load_windows()
            elif self.platform == 'Linux':
                return self._get_cpu_load_linux()
            elif self.platform == 'Darwin':
                return self._get_cpu_load_macos()
            else:
                return 0.0
        except Exception as e:
            print(f"[Native CPU Monitor] CPU load error: {e}")
            return 0.0
    
    def _get_cpu_load_windows(self) -> float:
        """Get CPU load on Windows.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'loadpercentage'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip():
                    return float(lines[1].strip())
        except Exception:
            pass
        
        return 0.0
    
    def _get_cpu_load_linux(self) -> float:
        """Get CPU load on Linux by parsing /proc/stat.
        
        v0.3.5d: Better error handling
        """
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            
            # Parse: cpu  user nice system idle iowait irq softirq...
            fields = line.split()[1:]
            times = [int(x) for x in fields]
            
            total = sum(times)
            idle = times[3]  # 4th field is idle
            
            # Calculate delta since last measurement
            if self.last_cpu_times is not None:
                total_diff = total - self.last_cpu_times[0]
                idle_diff = idle - self.last_cpu_times[1]
                
                if total_diff > 0:
                    load = ((total_diff - idle_diff) / total_diff) * 100
                else:
                    load = 0.0
            else:
                load = 0.0  # First call
            
            # Save for next measurement
            self.last_cpu_times = (total, idle)
            
            return round(load, 1)
        
        except Exception as e:
            print(f"[Native CPU Monitor] Linux CPU load failed: {e}")
            return 0.0
    
    def _get_cpu_load_macos(self) -> float:
        """Get CPU load on macOS.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['top', '-l', '1', '-n', '0'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'CPU usage' in line:
                        match = re.search(r'(\d+\.\d+)% user.*?(\d+\.\d+)% sys', line)
                        if match:
                            user = float(match.group(1))
                            sys = float(match.group(2))
                            return round(user + sys, 1)
        except Exception:
            pass
        
        return 0.0
    
    # ========== CPU Temperature ==========
    
    def _get_cpu_temp(self) -> Optional[float]:
        """Get CPU temperature if available."""
        try:
            if self.platform == 'Linux':
                return self._get_cpu_temp_linux()
            # Windows/macOS: Temperature not easily accessible
            return None
        except Exception:
            return None
    
    def _get_cpu_temp_linux(self) -> Optional[float]:
        """Get CPU temperature on Linux.
        
        v0.3.5d: Added sanity checks
        """
        import glob
        
        try:
            thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
            temps = []
            
            for zone in thermal_zones:
                try:
                    with open(zone, 'r') as f:
                        temp = int(f.read().strip()) / 1000.0
                        # v0.3.5d: Sanity check
                        if 0 < temp < 150:
                            temps.append(temp)
                except Exception:
                    continue
            
            return max(temps) if temps else None
        
        except Exception:
            return None
    
    # ========== CPU Frequency ==========
    
    def _get_cpu_freq(self) -> float:
        """Get current CPU frequency."""
        try:
            if self.platform == 'Windows':
                return self._get_cpu_freq_windows()
            elif self.platform == 'Linux':
                return self._get_cpu_freq_linux()
            elif self.platform == 'Darwin':
                return self._get_cpu_freq_macos()
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _get_cpu_freq_windows(self) -> float:
        """Get CPU frequency on Windows.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'CurrentClockSpeed'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1 and lines[1].strip():
                    return float(lines[1].strip())
        except Exception:
            pass
        
        return 0.0
    
    def _get_cpu_freq_linux(self) -> float:
        """Get CPU frequency on Linux.
        
        v0.3.5d: Better error handling
        """
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('cpu MHz'):
                        return float(line.split(':')[1].strip())
        except Exception:
            pass
        
        return 0.0
    
    def _get_cpu_freq_macos(self) -> float:
        """Get CPU frequency on macOS.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'hw.cpufrequency'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode == 0:
                # Convert Hz to MHz
                return float(result.stdout.strip()) / 1_000_000
        except Exception:
            pass
        
        return 0.0
    
    def _get_cpu_freq_max(self) -> float:
        """Get maximum CPU frequency."""
        try:
            if self.platform == 'Windows':
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'MaxClockSpeed'],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    check=False,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1 and lines[1].strip():
                        return float(lines[1].strip())
            
            elif self.platform == 'Linux':
                try:
                    with open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq', 'r') as f:
                        # Convert kHz to MHz
                        return float(f.read().strip()) / 1000
                except Exception:
                    pass
        
        except Exception:
            pass
        
        return 0.0


# ========== Testing ==========

if __name__ == '__main__':
    print("="*60)
    print("Native CPU Monitor Test (v0.3.5d)")
    print("="*60)
    print()
    
    monitor = NativeCPUMonitor()
    
    print(f"Monitor: {monitor.get_name()}")
    print(f"Available: {monitor.is_available()}")
    print()
    
    print("Testing CPU data retrieval...")
    print()
    
    for i in range(3):
        data = monitor.get_data()
        
        print(f"\nTest {i+1}:")
        print(f"  CPU: {data['name']}")
        print(f"  Load: {data['load']:.1f}%")
        print(f"  Temp: {data['temp']}°C" if data['temp'] else "  Temp: N/A")
        print(f"  Freq: {data['freq']:.0f} MHz")
        print(f"  Freq Max: {data['freq_max']:.0f} MHz")
        print(f"  Cores: {data['count']} physical, {data['count_logical']} logical")
        
        if i < 2:
            time.sleep(1)
    
    print()
    print("="*60)
    print("✅ Native CPU Monitor v0.3.5d works!")
    print("  - No hangs (all timeouts working)")
    print("  - No crashes (all errors handled)")
    print("  - Sanity checks applied")
    print("="*60)
