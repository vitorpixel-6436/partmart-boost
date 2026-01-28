#!/usr/bin/env python3
"""Sovereignty Manager - Automatic fallback system for maximum autonomy.

Manages dependency fallbacks:
- TIER 1 (FULL): External libraries (psutil, pynvml, wmi)
- TIER 2 (NATIVE): Native OS APIs (WMIC, sysfs, ctypes)
- TIER 3 (MINIMAL): Stub monitors (safe defaults)

Goal: Application works even with ZERO external dependencies.

Author: PartMart Team
Version: 0.3.5c_hotfix
License: MIT
"""

import platform
from typing import Dict, Any, Literal

# FIX: Import BaseMonitor directly
from monitors import BaseMonitor


MonitoringLevel = Literal['FULL', 'NATIVE', 'MINIMAL']


class SovereigntyManager:
    """Manages monitoring fallback hierarchy for maximum autonomy.
    
    Priority:
    1. FULL: psutil + pynvml + wmi (best features)
    2. NATIVE: Native OS APIs (good performance)
    3. MINIMAL: Stub monitors (safe defaults)
    """
    
    def __init__(self, prefer_native: bool = False):
        """Initialize sovereignty manager.
        
        Args:
            prefer_native: If True, use native monitors even if
                         external libraries available (max sovereignty)
        """
        self.prefer_native = prefer_native
        self.platform = platform.system()
        
        # Detect monitoring level
        self.monitoring_level = self._detect_monitoring_level()
        
        print(f"[Sovereignty] Platform: {self.platform}")
        print(f"[Sovereignty] Monitoring Level: {self.monitoring_level}")
        print(f"[Sovereignty] Prefer Native: {prefer_native}")
        print(f"[Sovereignty] Score: {self.get_sovereignty_score()}/100")
    
    def _detect_monitoring_level(self) -> MonitoringLevel:
        """Detect available monitoring level."""
        # If user prefers native, use it
        if self.prefer_native:
            if self._test_native_apis():
                return 'NATIVE'
            else:
                return 'MINIMAL'
        
        # Try external libraries
        if self._test_psutil():
            return 'FULL'
        
        # Try native APIs
        if self._test_native_apis():
            return 'NATIVE'
        
        # Fallback to minimal
        return 'MINIMAL'
    
    def _test_psutil(self) -> bool:
        """Test if psutil is available."""
        try:
            import psutil
            # Quick test
            psutil.cpu_percent(interval=None)
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def _test_native_apis(self) -> bool:
        """Test if native OS APIs are available."""
        try:
            if self.platform == 'Windows':
                # Test WMIC
                import subprocess
                subprocess.check_output(
                    ['wmic', 'cpu', 'get', 'name'],
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=5
                )
                return True
            
            elif self.platform == 'Linux':
                # Test /proc
                with open('/proc/cpuinfo', 'r') as f:
                    f.read()
                return True
            
            elif self.platform == 'Darwin':
                # Test sysctl
                import subprocess
                subprocess.check_output(
                    ['sysctl', '-n', 'hw.physicalcpu'],
                    text=True,
                    timeout=5
                )
                return True
            
            else:
                return False
        
        except Exception:
            return False
    
    # ========== Monitor Factory ==========
    
    def get_gpu_monitor(self) -> BaseMonitor:
        """Get GPU monitor based on availability."""
        if self.monitoring_level == 'FULL' and not self.prefer_native:
            try:
                from monitors.gpu_monitor import GPUMonitor
                return GPUMonitor()
            except Exception as e:
                print(f"[WARN] Failed to load GPUMonitor: {e}")
        
        # Fallback to native
        try:
            from monitors.fallback_gpu import FallbackGPUMonitor
            return FallbackGPUMonitor()
        except Exception as e:
            print(f"[WARN] Failed to load FallbackGPUMonitor: {e}")
        
        # Last resort: stub
        return self._get_stub_monitor('GPU')
    
    def get_cpu_monitor(self) -> BaseMonitor:
        """Get CPU monitor based on availability."""
        if self.monitoring_level == 'FULL' and not self.prefer_native:
            try:
                from monitors.cpu_monitor import CPUMonitor
                return CPUMonitor()
            except Exception as e:
                print(f"[WARN] Failed to load CPUMonitor: {e}")
        
        # Fallback to native
        if self.monitoring_level in ['FULL', 'NATIVE']:
            try:
                from monitors.native_cpu import NativeCPUMonitor
                return NativeCPUMonitor()
            except Exception as e:
                print(f"[WARN] Failed to load NativeCPUMonitor: {e}")
        
        # Last resort: stub
        return self._get_stub_monitor('CPU')
    
    def get_ram_monitor(self) -> BaseMonitor:
        """Get RAM monitor based on availability."""
        if self.monitoring_level == 'FULL' and not self.prefer_native:
            try:
                from monitors.ram_monitor import RAMMonitor
                return RAMMonitor()
            except Exception as e:
                print(f"[WARN] Failed to load RAMMonitor: {e}")
        
        # Fallback to native
        if self.monitoring_level in ['FULL', 'NATIVE']:
            try:
                from monitors.native_ram import NativeRAMMonitor
                return NativeRAMMonitor()
            except Exception as e:
                print(f"[WARN] Failed to load NativeRAMMonitor: {e}")
        
        # Last resort: stub
        return self._get_stub_monitor('RAM')
    
    def _get_stub_monitor(self, monitor_type: str) -> BaseMonitor:
        """Get stub monitor that returns safe defaults.
        
        Args:
            monitor_type: 'GPU', 'CPU', or 'RAM'
        
        Returns:
            Stub monitor with safe default values
        """
        class StubMonitor(BaseMonitor):
            def __init__(self, mtype: str):
                super().__init__()
                self.mtype = mtype
                self.available = False
            
            def get_name(self) -> str:
                return f"Stub {self.mtype} Monitor"
            
            def is_available(self) -> bool:
                return False
            
            def get_data(self) -> Dict[str, Any]:
                if self.mtype == 'GPU':
                    return {
                        'name': 'GPU Unavailable',
                        'temp_gpu': 0,
                        'temp_hotspot': None,
                        'clock_gpu': 0,
                        'clock_mem': 0,
                        'load_gpu': 0,
                        'load_mem': 0,
                        'power': 0.0,
                        'fan_speed': 0,
                    }
                elif self.mtype == 'CPU':
                    return {
                        'name': 'CPU Unavailable',
                        'load': 0.0,
                        'temp': None,
                        'freq': 0.0,
                        'freq_min': 0.0,
                        'freq_max': 0.0,
                        'count': 1,
                        'count_logical': 1,
                    }
                elif self.mtype == 'RAM':
                    return {
                        'total': 16.0,
                        'used': 8.0,
                        'free': 8.0,
                        'percent': 50.0,
                        'speed': None,
                        'type': 'DDR4',
                        'xmp_enabled': False,
                    }
                else:
                    return {}
        
        return StubMonitor(monitor_type)
    
    # ========== Status & Metrics ==========
    
    def get_sovereignty_status(self) -> Dict[str, Any]:
        """Get current sovereignty status."""
        gpu_type = self._get_monitor_type('gpu')
        cpu_type = self._get_monitor_type('cpu')
        ram_type = self._get_monitor_type('ram')
        
        return {
            'level': self.monitoring_level,
            'score': self.get_sovereignty_score(),
            'gpu': gpu_type,
            'cpu': cpu_type,
            'ram': ram_type,
            'external_deps': self._list_external_deps(),
            'native_apis': self.monitoring_level in ['NATIVE', 'FULL'],
            'offline_capable': self.monitoring_level != 'FULL' or self.prefer_native,
        }
    
    def _get_monitor_type(self, component: str) -> str:
        """Get monitor type for component."""
        if self.monitoring_level == 'MINIMAL':
            return 'stub'
        elif self.monitoring_level == 'NATIVE':
            return 'native'
        else:
            if self.prefer_native:
                return 'native'
            else:
                return 'external'
    
    def _list_external_deps(self) -> list:
        """List required external dependencies."""
        if self.monitoring_level == 'MINIMAL':
            return []
        elif self.monitoring_level == 'NATIVE':
            return []
        else:
            deps = []
            if not self.prefer_native:
                deps.extend(['psutil', 'pynvml'])
                if self.platform == 'Windows':
                    deps.append('wmi')
            return deps
    
    def get_sovereignty_score(self) -> int:
        """Calculate sovereignty score (0-100)."""
        if self.monitoring_level == 'MINIMAL':
            return 100  # Pure stdlib!
        elif self.monitoring_level == 'NATIVE':
            return 85   # Native OS APIs
        else:
            if self.prefer_native:
                return 85  # User choice
            else:
                return 50  # External libraries
    
    def print_status(self):
        """Print sovereignty status in human-readable format."""
        status = self.get_sovereignty_status()
        
        print()
        print("="*60)
        print(f"Sovereignty Status")
        print("="*60)
        print(f"Monitoring Level: {status['level']}")
        print(f"Sovereignty Score: {status['score']}/100")
        print()
        print("Components:")
        print(f"  GPU: {status['gpu'].upper()}")
        print(f"  CPU: {status['cpu'].upper()}")
        print(f"  RAM: {status['ram'].upper()}")
        print()
        print(f"External Dependencies: {len(status['external_deps'])}")
        if status['external_deps']:
            for dep in status['external_deps']:
                print(f"  - {dep}")
        print()
        print(f"Native APIs: {'YES' if status['native_apis'] else 'NO'}")
        print(f"Offline Capable: {'YES' if status['offline_capable'] else 'NO'}")
        print("="*60)
        print()


if __name__ == '__main__':
    print("="*60)
    print("Sovereignty Manager Test")
    print("="*60)
    print()
    
    # Test 1: Auto-detect
    print("\nTest 1: Auto-detect (prefer external if available)")
    manager = SovereigntyManager(prefer_native=False)
    manager.print_status()
    
    cpu = manager.get_cpu_monitor()
    print(f"CPU Monitor: {cpu.get_name()}")
    data = cpu.get_data()
    print(f"CPU Load: {data['load']:.1f}%")
    print()
    
    # Test 2: Force native
    print("\nTest 2: Force native (maximum sovereignty)")
    manager_native = SovereigntyManager(prefer_native=True)
    manager_native.print_status()
    
    cpu_native = manager_native.get_cpu_monitor()
    print(f"CPU Monitor: {cpu_native.get_name()}")
    data_native = cpu_native.get_data()
    print(f"CPU Load: {data_native['load']:.1f}%")
    print()
    
    print("="*60)
    print("✅ Sovereignty Manager works!")
    print("="*60)
