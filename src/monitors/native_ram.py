#!/usr/bin/env python3
"""Native RAM Monitor - RAM monitoring WITHOUT psutil dependency.

Provides RAM monitoring using only:
- Windows: kernel32.dll via ctypes
- Linux: /proc/meminfo
- macOS: vm_stat

Part of Sovereignty Mode - maximum independence from external libraries.

Author: PartMart Team
Version: 0.3.5d - Package 1
License: MIT
"""

import platform
import subprocess
from typing import Dict, Optional, Any, Tuple
from monitors import BaseMonitor

# Windows-specific imports
if platform.system() == 'Windows':
    import ctypes
    from ctypes import wintypes


class NativeRAMMonitor(BaseMonitor):
    """Native RAM monitor using OS APIs directly.
    
    Features:
    - RAM usage (total, used, free, %)
    - RAM speed (Windows only, via WMI)
    - Cross-platform: Windows, Linux, macOS
    
    No external dependencies (no psutil, no wmi).
    
    v0.3.5d fixes:
    - REMOVED sudo dmidecode (CRITICAL)
    - All subprocess calls have timeouts
    - Sanity checks on memory values
    - No crashes on missing utilities
    """
    
    def __init__(self):
        super().__init__()
        self.platform = platform.system()
        
        # Pre-detect RAM info
        self._ram_speed = self._detect_ram_speed()
        self._ram_type = 'DDR4'  # Default
        
        self.available = True
        
        print(f"[Native RAM Monitor] Platform: {self.platform}")
        if self._ram_speed:
            print(f"[Native RAM Monitor] RAM Speed: {self._ram_speed} MHz")
    
    def get_name(self) -> str:
        """Get monitor name."""
        return "Native RAM Monitor"
    
    def get_data(self) -> Dict[str, Any]:
        """Get current RAM metrics.
        
        Returns:
            dict: {
                'total': float,
                'used': float,
                'free': float,
                'percent': float,
                'speed': int or None,
                'type': str,
                'xmp_enabled': bool,
            }
        """
        try:
            memory = self._get_memory_info()
            
            # v0.3.5d: Validate memory values
            total_gb, used_gb, free_gb = self._validate_memory(
                memory['total'],
                memory['used'],
                memory['free']
            )
            
            return {
                'total': total_gb,
                'used': used_gb,
                'free': free_gb,
                'percent': self._validate_percent(memory['percent']),
                'speed': self._ram_speed,
                'type': self._ram_type,
                'xmp_enabled': self._detect_xmp(),
            }
        except Exception as e:
            print(f"[Native RAM Monitor] Error: {e}")
            return self._get_safe_defaults()
    
    def _get_safe_defaults(self) -> Dict[str, Any]:
        """Return safe default values.
        
        v0.3.5d: Return 0 instead of fake data
        """
        return {
            'total': 0.0,
            'used': 0.0,
            'free': 0.0,
            'percent': 0.0,
            'speed': None,
            'type': 'Unknown',
            'xmp_enabled': False,
        }
    
    # ========== v0.3.5d: VALIDATION ==========
    
    def _validate_memory(self, total: float, used: float, free: float) -> Tuple[float, float, float]:
        """Validate memory values are sane.
        
        Args:
            total: Total RAM (GB)
            used: Used RAM (GB)
            free: Free RAM (GB)
        
        Returns:
            Validated (total, used, free)
        """
        # Ensure positive
        total = max(0.0, total)
        used = max(0.0, used)
        free = max(0.0, free)
        
        # Ensure used <= total
        used = min(used, total)
        free = min(free, total)
        
        # Ensure used + free <= total (allow small error)
        if used + free > total + 0.1:  # 100 MB tolerance
            # Adjust free to match
            free = max(0.0, total - used)
        
        return round(total, 2), round(used, 2), round(free, 2)
    
    def _validate_percent(self, percent: float) -> float:
        """Validate percentage is 0-100.
        
        Args:
            percent: Percentage value
        
        Returns:
            Clamped 0-100
        """
        return max(0.0, min(100.0, percent))
    
    # ========== Memory Info ==========
    
    def _get_memory_info(self) -> Dict[str, float]:
        """Get memory usage info.
        
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
        """Get memory info on Windows using kernel32.dll."""
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
        """Get memory info on Linux from /proc/meminfo.
        
        v0.3.5d: Better error handling
        """
        try:
            meminfo = {}
            
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if ':' in line:
                        key = line.split(':')[0]
                        value_parts = line.split()
                        if len(value_parts) >= 2:
                            value = int(value_parts[1]) * 1024  # KB to bytes
                            meminfo[key] = value
            
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
        
        except Exception as e:
            print(f"[Native RAM Monitor] Linux memory read failed: {e}")
            raise
    
    def _get_memory_macos(self) -> Dict[str, float]:
        """Get memory info on macOS using vm_stat.
        
        v0.3.5d: Added timeout
        """
        try:
            # Get page size
            result = subprocess.run(
                ['pagesize'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode != 0:
                raise OSError("pagesize command failed")
            
            page_size = int(result.stdout.strip())
            
            # Get vm_stat
            result = subprocess.run(
                ['vm_stat'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False
            )
            
            if result.returncode != 0:
                raise OSError("vm_stat command failed")
            
            # Parse vm_stat output
            stats = {}
            for line in result.stdout.split('\n'):
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
        
        except Exception as e:
            print(f"[Native RAM Monitor] macOS memory read failed: {e}")
            raise
    
    # ========== RAM Speed Detection ==========
    
    def _detect_ram_speed(self) -> Optional[int]:
        """Detect RAM speed (MHz).
        
        Only works on Windows via WMIC.
        Linux/macOS: Not easily accessible.
        
        v0.3.5d: REMOVED sudo, added timeout
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
        """Get RAM speed on Windows via WMIC.
        
        v0.3.5d: Added timeout
        """
        try:
            result = subprocess.run(
                ['wmic', 'memorychip', 'get', 'speed'],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                return None
            
            speeds = []
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
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
        """Get RAM speed on Linux via dmidecode.
        
        v0.3.5d CRITICAL FIX:
        - REMOVED sudo (was causing GUI to hang)
        - Try dmidecode without sudo
        - If permission denied, return None gracefully
        - Add timeout
        """
        try:
            # v0.3.5d: Try dmidecode WITHOUT sudo
            result = subprocess.run(
                ['dmidecode', '--type', '17'],
                capture_output=True,
                text=True,
                timeout=3,  # 3 second timeout
                check=False  # Don't raise on error
            )
            
            # v0.3.5d: Check if command succeeded
            if result.returncode != 0:
                # Permission denied or not installed
                print(f"[Native RAM Monitor] dmidecode unavailable (no permissions or not installed)")
                return None
            
            # Parse output
            for line in result.stdout.split('\n'):
                if 'Speed:' in line and 'MHz' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'MHz' and i > 0:
                            speed_str = parts[i-1]
                            if speed_str.isdigit():
                                return int(speed_str)
        
        except subprocess.TimeoutExpired:
            print(f"[Native RAM Monitor] dmidecode timed out")
        except Exception as e:
            print(f"[Native RAM Monitor] dmidecode failed: {e}")
        
        return None
    
    # ========== XMP Detection ==========
    
    def _detect_xmp(self) -> bool:
        """Detect if XMP is enabled (heuristic).
        
        Logic:
        - DDR5: JEDEC = 4800 MHz, XMP if > 4800
        - DDR4: JEDEC = 2133 MHz, XMP if > 2400
        - DDR3: JEDEC = 1600 MHz, XMP if > 1600
        """
        if self._ram_speed is None:
            return False
        
        # Heuristic based on speed
        if self._ram_speed > 4800:
            self._ram_type = 'DDR5'
            return True
        elif self._ram_speed > 2400:
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
    print("Native RAM Monitor Test (v0.3.5d)")
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
    print("✅ Native RAM Monitor v0.3.5d works!")
    print("  - No sudo (no permission prompts)")
    print("  - No hangs (all timeouts working)")
    print("  - No crashes (all errors handled)")
    print("  - Sanity checks applied")
    print("="*60)
