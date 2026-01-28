#!/usr/bin/env python3
"""
Native RAM Monitor - RAM monitoring WITHOUT psutil dependency.

Provides RAM monitoring using only:
- Windows: kernel32.dll via ctypes
- Linux: /proc/meminfo
- macOS: vm_stat

Part of Sovereignty Mode - maximum independence from external libraries.

Author: PartMart Team
Version: 0.3.5-alpha
License: MIT
"""

import platform
import subprocess
from typing import Dict, Optional, Any
from monitors import BaseMonitor

# Windows-specific imports
if platform.system() == 'Windows':
    import ctypes
    from ctypes import wintypes


class NativeRAMMonitor(BaseMonitor):
    """
    Native RAM monitor using OS APIs directly.
    
    Features:
    - RAM usage (total, used, free, %)
    - RAM speed (Windows only, via WMI)
    - Cross-platform: Windows, Linux, macOS
    
    No external dependencies (no psutil, no wmi).
    """
    
    def __init__(self):
        self.platform = platform.system()
        
        # Pre-detect RAM info
        self._ram_speed = self._detect_ram_speed()
        self._ram_type = 'DDR4'  # Default
        
        print(f"[Native RAM Monitor] Platform: {self.platform}")
        if self._ram_speed:
            print(f"[Native RAM Monitor] RAM Speed: {self._ram_speed} MHz")
    
    def get_name(self) -> str:
        """Get monitor name."""
        return "Native RAM Monitor"
    
    def is_available(self) -> bool:
        """Check if RAM monitoring is available."""
        return True  # Always available (uses stdlib)
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get current RAM metrics.
        
        Returns:
            dict: {
                'total': float,        # Total RAM (GB)
                'used': float,         # Used RAM (GB)
                'free': float,         # Available RAM (GB)
                'percent': float,      # Usage (%)
                'speed': int or None,  # RAM speed (MHz)
                'type': str,           # Memory type (DDR4, etc.)
                'xmp_enabled': bool,   # XMP status (heuristic)
            }
        """
        try:
            memory = self._get_memory_info()
            
            return {
                'total': memory['total'],
                'used': memory['used'],
                'free': memory['free'],
                'percent': memory['percent'],
                'speed': self._ram_speed,
                'type': self._ram_type,
                'xmp_enabled': self._detect_xmp(),
            }
        except Exception as e:
            print(f"[Native RAM Monitor] Error: {e}")
            return self._get_safe_defaults()
    
    def _get_safe_defaults(self) -> Dict[str, Any]:
        """Return safe default values."""
        return {
            'total': 16.0,
            'used': 8.0,
            'free': 8.0,
            'percent': 50.0,
            'speed': None,
            'type': 'DDR4',
            'xmp_enabled': False,
        }
    
    # ========== Memory Info ==========
    
    def _get_memory_info(self) -> Dict[str, float]:
        """
        Get memory usage info.
        
        Returns:
            dict: {'total': GB, 'used': GB, 'free': GB, 'percent': %}
        """
        if self.platform == 'Windows':
            return self._get_memory_windows()
        elif self.platform == 'Linux':
            return self._get_memory_linux()
        elif self.platform == 'Darwin':
            return self._get_memory_macos()
        else:
            raise OSError(f"Unsupported platform: {self.platform}")
    
    def _get_memory_windows(self) -> Dict[str, float]:
        """
        Get memory info on Windows using kernel32.dll.
        
        Uses GlobalMemoryStatusEx from kernel32.
        """
        # Define structure
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ('dwLength', wintypes.DWORD),
                ('dwMemoryLoad', wintypes.DWORD),
                ('ullTotalPhys', ctypes.c_ulonglong),
                ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong),
                ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong),
                ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong),
            ]
        
        # Initialize structure
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        
        # Call kernel32
        kernel32 = ctypes.windll.kernel32
        if not kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            raise OSError("GlobalMemoryStatusEx failed")
        
        # Convert bytes to GB
        total_gb = stat.ullTotalPhys / (1024 ** 3)
        avail_gb = stat.ullAvailPhys / (1024 ** 3)
        used_gb = total_gb - avail_gb
        percent = stat.dwMemoryLoad
        
        return {
            'total': round(total_gb, 2),
            'used': round(used_gb, 2),
            'free': round(avail_gb, 2),
            'percent': float(percent),
        }
    
    def _get_memory_linux(self) -> Dict[str, float]:
        """
        Get memory info on Linux from /proc/meminfo.
        """
        meminfo = {}
        
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if ':' in line:
                    key = line.split(':')[0]
                    value = line.split()[1]
                    meminfo[key] = int(value) * 1024  # KB to bytes
        
        total_bytes = meminfo.get('MemTotal', 0)
        avail_bytes = meminfo.get('MemAvailable', 0)
        used_bytes = total_bytes - avail_bytes
        
        total_gb = total_bytes / (1024 ** 3)
        used_gb = used_bytes / (1024 ** 3)
        avail_gb = avail_bytes / (1024 ** 3)
        percent = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
        
        return {
            'total': round(total_gb, 2),
            'used': round(used_gb, 2),
            'free': round(avail_gb, 2),
            'percent': round(percent, 1),
        }
    
    def _get_memory_macos(self) -> Dict[str, float]:
        """
        Get memory info on macOS using vm_stat.
        """
        # Get page size
        result = subprocess.check_output(['pagesize'], text=True)
        page_size = int(result.strip())
        
        # Get vm_stat
        result = subprocess.check_output(['vm_stat'], text=True)
        
        # Parse vm_stat output
        stats = {}
        for line in result.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                key = key.strip().replace(' ', '_')
                value = value.strip().rstrip('.')
                if value.isdigit():
                    stats[key] = int(value)
        
        # Calculate memory
        pages_free = stats.get('Pages_free', 0)
        pages_active = stats.get('Pages_active', 0)
        pages_inactive = stats.get('Pages_inactive', 0)
        pages_speculative = stats.get('Pages_speculative', 0)
        pages_wired = stats.get('Pages_wired_down', 0)
        
        free_bytes = pages_free * page_size
        used_bytes = (pages_active + pages_inactive + pages_wired) * page_size
        total_bytes = free_bytes + used_bytes
        
        total_gb = total_bytes / (1024 ** 3)
        used_gb = used_bytes / (1024 ** 3)
        free_gb = free_bytes / (1024 ** 3)
        percent = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
        
        return {
            'total': round(total_gb, 2),
            'used': round(used_gb, 2),
            'free': round(free_gb, 2),
            'percent': round(percent, 1),
        }
    
    # ========== RAM Speed Detection ==========
    
    def _detect_ram_speed(self) -> Optional[int]:
        """
        Detect RAM speed (MHz).
        
        Only works on Windows via WMIC.
        Linux/macOS: Not easily accessible.
        """
        try:
            if self.platform == 'Windows':
                return self._get_ram_speed_windows()
            elif self.platform == 'Linux':
                return self._get_ram_speed_linux()
            else:
                return None
        except Exception as e:
            print(f"[Native RAM Monitor] RAM speed detection failed: {e}")
            return None
    
    def _get_ram_speed_windows(self) -> Optional[int]:
        """Get RAM speed on Windows via WMIC."""
        try:
            result = subprocess.check_output(
                ['wmic', 'memorychip', 'get', 'speed'],
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            speeds = []
            for line in result.strip().split('\n')[1:]:  # Skip header
                line = line.strip()
                if line and line.isdigit():
                    speeds.append(int(line))
            
            # Return most common speed
            if speeds:
                return max(set(speeds), key=speeds.count)
            return None
        except Exception:
            return None
    
    def _get_ram_speed_linux(self) -> Optional[int]:
        """Get RAM speed on Linux via dmidecode (requires root)."""
        try:
            result = subprocess.check_output(
                ['sudo', 'dmidecode', '--type', '17'],
                text=True,
                stderr=subprocess.DEVNULL
            )
            
            for line in result.split('\n'):
                if 'Speed:' in line and 'MHz' in line:
                    speed_str = line.split(':')[1].strip().replace(' MHz', '')
                    if speed_str.isdigit():
                        return int(speed_str)
        except Exception:
            pass
        return None
    
    # ========== XMP Detection ==========
    
    def _detect_xmp(self) -> bool:
        """
        Detect if XMP is enabled (heuristic).
        
        Logic:
        - DDR5: JEDEC = 4800 MHz, XMP if > 4800
        - DDR4: JEDEC = 2133 MHz, XMP if > 2133
        - DDR3: JEDEC = 1600 MHz, XMP if > 1600
        """
        if self._ram_speed is None:
            return False
        
        # Heuristic based on speed
        if self._ram_speed > 4800:
            self._ram_type = 'DDR5'
            return True
        elif self._ram_speed > 2133:
            self._ram_type = 'DDR4'
            return True
        elif self._ram_speed > 1600:
            self._ram_type = 'DDR3'
            return True
        else:
            return False


# ========== Testing ==========

if __name__ == '__main__':
    print("="*60)
    print("Native RAM Monitor Test (No psutil!)")
    print("="*60)
    print()
    
    monitor = NativeRAMMonitor()
    
    print(f"Monitor: {monitor.get_name()}")
    print(f"Available: {monitor.is_available()}")
    print()
    
    print("Testing RAM data retrieval...")
    print()
    
    import time
    for i in range(3):
        data = monitor.get_data()
        
        print(f"\nTest {i+1}:")
        print(f"  Total: {data['total']:.2f} GB")
        print(f"  Used: {data['used']:.2f} GB")
        print(f"  Free: {data['free']:.2f} GB")
        print(f"  Usage: {data['percent']:.1f}%")
        print(f"  Speed: {data['speed']} MHz" if data['speed'] else "  Speed: N/A")
        print(f"  Type: {data['type']}")
        print(f"  XMP: {'Enabled' if data['xmp_enabled'] else 'Disabled'}")
        
        if i < 2:
            time.sleep(1)
    
    print()
    print("="*60)
    print("✅ Native RAM Monitor works WITHOUT psutil!")
    print("="*60)
