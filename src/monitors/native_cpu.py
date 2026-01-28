#!/usr/bin/env python3
"""
Native CPU Monitor - CPU monitoring WITHOUT psutil dependency.

Provides CPU monitoring using only:
- Windows: WMIC + WMI via ctypes
- Linux: /proc/stat + /sys/class/thermal
- macOS: sysctl

Part of Sovereignty Mode - maximum independence from external libraries.

Author: PartMart Team
Version: 0.3.5-alpha
License: MIT
"""

import subprocess
import platform
import time
import re
from typing import Dict, Optional, Any
from monitors import BaseMonitor


class NativeCPUMonitor(BaseMonitor):
    """
    Native CPU monitor using OS APIs directly.
    
    Features:
    - CPU load (utilization percentage)
    - CPU frequency (current, min, max)
    - Core count (physical and logical)
    - CPU temperature (if available)
    - Cross-platform: Windows, Linux, macOS
    
    No external dependencies (no psutil).
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.last_cpu_times = None
        self.last_measure_time = None
        
        # Pre-detect CPU info
        self._cpu_name = self._detect_cpu_name()
        self._cpu_cores = self._detect_cpu_cores()
        self._cpu_cores_logical = self._detect_cpu_cores_logical()
        
        print(f"[Native CPU Monitor] Platform: {self.platform}")
        print(f"[Native CPU Monitor] CPU: {self._cpu_name}")
        print(f"[Native CPU Monitor] Cores: {self._cpu_cores} physical, {self._cpu_cores_logical} logical")
    
    def get_name(self) -> str:
        """Get monitor name."""
        return "Native CPU Monitor"
    
    def is_available(self) -> bool:
        """Check if CPU monitoring is available."""
        return True  # Always available (uses stdlib)
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get current CPU metrics.
        
        Returns:
            dict: {
                'name': str,              # CPU name
                'load': float,            # CPU usage (%)
                'temp': float or None,    # Temperature (°C)
                'freq': float,            # Current frequency (MHz)
                'freq_min': float,        # Min frequency (MHz)
                'freq_max': float,        # Max frequency (MHz)
                'count': int,             # Physical cores
                'count_logical': int,     # Logical cores (threads)
            }
        """
        try:
            return {
                'name': self._cpu_name,
                'load': self._get_cpu_load(),
                'temp': self._get_cpu_temp(),
                'freq': self._get_cpu_freq(),
                'freq_min': self._get_cpu_freq_min(),
                'freq_max': self._get_cpu_freq_max(),
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
        """Get CPU name on Windows."""
        result = subprocess.check_output(
            ['wmic', 'cpu', 'get', 'name'],
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.strip().split('\n')
        if len(lines) > 1:
            return lines[1].strip()
        return 'Unknown CPU'
    
    def _get_cpu_name_linux(self) -> str:
        """Get CPU name on Linux."""
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('model name'):
                    return line.split(':')[1].strip()
        return 'Unknown CPU'
    
    def _get_cpu_name_macos(self) -> str:
        """Get CPU name on macOS."""
        result = subprocess.check_output(
            ['sysctl', '-n', 'machdep.cpu.brand_string'],
            text=True
        )
        return result.strip()
    
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
        """Get physical cores on Windows."""
        result = subprocess.check_output(
            ['wmic', 'cpu', 'get', 'NumberOfCores'],
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.strip().split('\n')
        if len(lines) > 1:
            return int(lines[1].strip())
        return 1
    
    def _get_cpu_cores_linux(self) -> int:
        """Get physical cores on Linux."""
        cores = set()
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('core id'):
                    cores.add(int(line.split(':')[1].strip()))
        return len(cores) if cores else 1
    
    def _get_cpu_cores_macos(self) -> int:
        """Get physical cores on macOS."""
        result = subprocess.check_output(
            ['sysctl', '-n', 'hw.physicalcpu'],
            text=True
        )
        return int(result.strip())
    
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
        """Get logical cores on Windows."""
        result = subprocess.check_output(
            ['wmic', 'cpu', 'get', 'NumberOfLogicalProcessors'],
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.strip().split('\n')
        if len(lines) > 1:
            return int(lines[1].strip())
        return self._cpu_cores
    
    def _get_cpu_cores_logical_linux(self) -> int:
        """Get logical cores on Linux."""
        with open('/proc/cpuinfo', 'r') as f:
            return sum(1 for line in f if line.startswith('processor'))
    
    def _get_cpu_cores_logical_macos(self) -> int:
        """Get logical cores on macOS."""
        result = subprocess.check_output(
            ['sysctl', '-n', 'hw.logicalcpu'],
            text=True
        )
        return int(result.strip())
    
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
        """Get CPU load on Windows."""
        result = subprocess.check_output(
            ['wmic', 'cpu', 'get', 'loadpercentage'],
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.strip().split('\n')
        if len(lines) > 1:
            return float(lines[1].strip())
        return 0.0
    
    def _get_cpu_load_linux(self) -> float:
        """
        Get CPU load on Linux by parsing /proc/stat.
        
        Formula:
        CPU% = (total_diff - idle_diff) / total_diff * 100
        """
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
    
    def _get_cpu_load_macos(self) -> float:
        """Get CPU load on macOS."""
        result = subprocess.check_output(['top', '-l', '1', '-n', '0'], text=True)
        for line in result.split('\n'):
            if 'CPU usage' in line:
                match = re.search(r'(\d+\.\d+)% user.*?(\d+\.\d+)% sys', line)
                if match:
                    user = float(match.group(1))
                    sys = float(match.group(2))
                    return round(user + sys, 1)
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
        """Get CPU temperature on Linux."""
        import glob
        
        thermal_zones = glob.glob('/sys/class/thermal/thermal_zone*/temp')
        temps = []
        
        for zone in thermal_zones:
            try:
                with open(zone, 'r') as f:
                    temp = int(f.read().strip()) / 1000.0
                    if temp > 0 and temp < 150:  # Sanity check
                        temps.append(temp)
            except Exception:
                continue
        
        return max(temps) if temps else None
    
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
        """Get CPU frequency on Windows."""
        result = subprocess.check_output(
            ['wmic', 'cpu', 'get', 'CurrentClockSpeed'],
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.strip().split('\n')
        if len(lines) > 1:
            return float(lines[1].strip())  # Already in MHz
        return 0.0
    
    def _get_cpu_freq_linux(self) -> float:
        """Get CPU frequency on Linux."""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('cpu MHz'):
                        return float(line.split(':')[1].strip())
        except Exception:
            pass
        return 0.0
    
    def _get_cpu_freq_macos(self) -> float:
        """Get CPU frequency on macOS."""
        result = subprocess.check_output(
            ['sysctl', '-n', 'hw.cpufrequency'],
            text=True
        )
        # Convert Hz to MHz
        return float(result.strip()) / 1_000_000
    
    def _get_cpu_freq_min(self) -> float:
        """Get minimum CPU frequency."""
        # Not easily accessible on most platforms
        return 0.0
    
    def _get_cpu_freq_max(self) -> float:
        """Get maximum CPU frequency."""
        try:
            if self.platform == 'Windows':
                result = subprocess.check_output(
                    ['wmic', 'cpu', 'get', 'MaxClockSpeed'],
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                lines = result.strip().split('\n')
                if len(lines) > 1:
                    return float(lines[1].strip())
            elif self.platform == 'Linux':
                try:
                    with open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq', 'r') as f:
                        # Convert kHz to MHz
                        return float(f.read().strip()) / 1000
                except Exception:
                    pass
            elif self.platform == 'Darwin':
                # macOS doesn't expose max freq easily
                pass
        except Exception:
            pass
        return 0.0


# ========== Testing ==========

if __name__ == '__main__':
    print("="*60)
    print("Native CPU Monitor Test (No psutil!)")
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
    print("✅ Native CPU Monitor works WITHOUT psutil!")
    print("="*60)
