"""Fallback Manager - Ensures maximum independence from external dependencies

Provides graceful fallbacks for:
- Missing Python packages
- Failed hardware detection
- Unsupported platforms
- Security restrictions
"""

import sys
import subprocess
import platform
from typing import Optional, Dict, Any, List
from pathlib import Path


class FallbackManager:
    """Manages fallback strategies for dependencies and hardware access"""
    
    def __init__(self):
        self.platform = platform.system()
        self._import_cache = {}
        self._feature_status = {}
    
    # ==================== IMPORT FALLBACKS ====================
    
    def try_import(self, module_name: str, feature: str = None) -> Optional[Any]:
        """Try to import a module with fallback
        
        Args:
            module_name: Module to import (e.g., 'pynvml')
            feature: Feature this enables (for logging)
        
        Returns:
            Module if successful, None if failed
        """
        if module_name in self._import_cache:
            return self._import_cache[module_name]
        
        try:
            module = __import__(module_name)
            self._import_cache[module_name] = module
            
            if feature:
                self._feature_status[feature] = 'available'
            
            print(f"[FallbackManager] {module_name} loaded successfully")
            return module
        
        except ImportError as e:
            self._import_cache[module_name] = None
            
            if feature:
                self._feature_status[feature] = 'unavailable'
            
            print(f"[FallbackManager] {module_name} unavailable: {e}")
            print(f"[FallbackManager] Feature '{feature}' will use fallback")
            return None
    
    # ==================== GPU FALLBACKS ====================
    
    def get_gpu_monitor_fallback(self) -> Optional[Any]:
        """Get GPU monitor with fallbacks
        
        Priority:
        1. pynvml (NVIDIA official)
        2. Native OS tools (fallback_gpu.py)
        3. Minimal stub (temperature only)
        """
        # Try official NVIDIA library
        pynvml = self.try_import('pynvml', 'NVIDIA GPU')
        if pynvml:
            try:
                from monitors.gpu_monitor import GPUMonitor
                return GPUMonitor()
            except Exception as e:
                print(f"[FallbackManager] GPUMonitor failed: {e}")
        
        # Try native fallback
        try:
            from monitors.fallback_gpu import FallbackGPUMonitor
            return FallbackGPUMonitor()
        except Exception as e:
            print(f"[FallbackManager] FallbackGPUMonitor failed: {e}")
        
        # Minimal stub
        return self._create_stub_gpu_monitor()
    
    def _create_stub_gpu_monitor(self):
        """Create minimal GPU monitor stub"""
        class StubGPUMonitor:
            def get_name(self):
                return "GPU Monitor (Stub)"
            
            def is_available(self):
                return False
            
            def get_data(self):
                return {
                    'name': 'No GPU Detected',
                    'temp_gpu': 0,
                    'temp_hotspot': None,
                    'load_gpu': 0,
                    'load_mem': 0,
                    'clock_gpu': 0,
                    'clock_mem': 0,
                    'power': 0,
                    'fan_speed': 0,
                    'mem_used': 0,
                    'mem_total': 0,
                    'status': 'unavailable',
                }
        
        print("[FallbackManager] Using stub GPU monitor (no GPU access)")
        return StubGPUMonitor()
    
    # ==================== WMI FALLBACKS ====================
    
    def get_wmi_fallback(self):
        """Get WMI access with fallbacks
        
        Priority:
        1. SafeWMI (secure wrapper)
        2. Direct wmi (legacy)
        3. Subprocess calls
        4. None (feature disabled)
        """
        if self.platform != 'Windows':
            return None
        
        # Try SafeWMI
        try:
            from core.safe_wmi import SafeWMI
            return SafeWMI()
        except Exception as e:
            print(f"[FallbackManager] SafeWMI unavailable: {e}")
        
        # Try direct wmi (not recommended)
        wmi_module = self.try_import('wmi', 'WMI')
        if wmi_module:
            print("[FallbackManager] WARNING: Using direct WMI (less secure)")
            try:
                return wmi_module.WMI()
            except Exception as e:
                print(f"[FallbackManager] Direct WMI failed: {e}")
        
        # Subprocess fallback
        print("[FallbackManager] Using subprocess for WMI queries")
        return self._create_subprocess_wmi()
    
    def _create_subprocess_wmi(self):
        """Create subprocess-based WMI wrapper"""
        class SubprocessWMI:
            def get_ram_speed(self) -> Optional[int]:
                try:
                    result = subprocess.run(
                        ['wmic', 'memorychip', 'get', 'speed'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        speed = int(lines[1].strip())
                        return speed
                except Exception as e:
                    print(f"[SubprocessWMI] Failed: {e}")
                
                return None
        
        return SubprocessWMI()
    
    # ==================== CPU FALLBACKS ====================
    
    def get_cpu_temp_fallback(self) -> Optional[float]:
        """Get CPU temperature with platform-specific fallbacks"""
        if self.platform == 'Linux':
            return self._get_cpu_temp_linux()
        elif self.platform == 'Windows':
            return self._get_cpu_temp_windows()
        elif self.platform == 'Darwin':
            return self._get_cpu_temp_macos()
        
        return None
    
    def _get_cpu_temp_linux(self) -> Optional[float]:
        """Linux: Read from /sys/class/thermal"""
        try:
            # Try common paths
            paths = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/hwmon/hwmon0/temp1_input',
                '/sys/class/hwmon/hwmon1/temp1_input',
            ]
            
            for path in paths:
                if Path(path).exists():
                    with open(path) as f:
                        temp = float(f.read().strip())
                        # Convert to Celsius if needed
                        if temp > 200:
                            temp /= 1000
                        return temp
        
        except Exception as e:
            print(f"[Fallback] Linux CPU temp failed: {e}")
        
        return None
    
    def _get_cpu_temp_windows(self) -> Optional[float]:
        """Windows: Try WMI or external tools"""
        try:
            # Try WMI
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'temperature'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1 and lines[1].strip():
                return float(lines[1].strip())
        
        except Exception:
            pass
        
        # WMI doesn't expose CPU temp on most systems
        return None
    
    def _get_cpu_temp_macos(self) -> Optional[float]:
        """macOS: Use powermetrics or other tools"""
        try:
            result = subprocess.run(
                ['powermetrics', '--samplers', 'cpu_power', '-n', '1'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            # Parse output for temperature
            # (powermetrics output format varies)
            for line in result.stdout.split('\n'):
                if 'temperature' in line.lower():
                    # Extract number
                    import re
                    match = re.search(r'(\d+\.?\d*)\s*C', line)
                    if match:
                        return float(match.group(1))
        
        except Exception:
            pass
        
        return None
    
    # ==================== FEATURE STATUS ====================
    
    def get_feature_status(self) -> Dict[str, str]:
        """Get status of all features
        
        Returns:
            Dict mapping feature name to status:
            - 'available': Working normally
            - 'fallback': Using fallback implementation
            - 'unavailable': Feature disabled
        """
        return self._feature_status.copy()
    
    def print_status(self):
        """Print feature availability status"""
        print("\n" + "="*60)
        print("[FallbackManager] Feature Status:")
        print("="*60)
        
        for feature, status in sorted(self._feature_status.items()):
            icon = {
                'available': '✅',
                'fallback': '⚠️',
                'unavailable': '❌',
            }.get(status, '❓')
            
            print(f"{icon} {feature:30s} {status}")
        
        print("="*60 + "\n")
    
    # ==================== DEPENDENCY CHECK ====================
    
    def check_all_dependencies(self) -> Dict[str, bool]:
        """Check all optional dependencies
        
        Returns:
            Dict mapping package name to availability
        """
        packages = {
            'pynvml': 'NVIDIA GPU support',
            'wmi': 'Windows Management (RAM speed)',
            'psutil': 'System monitoring',
            'sklearn': 'ML optimizer',
        }
        
        results = {}
        
        print("\n[FallbackManager] Checking dependencies...\n")
        
        for package, purpose in packages.items():
            module = self.try_import(package)
            results[package] = (module is not None)
            
            status = '✅ Available' if results[package] else '❌ Missing'
            print(f"  {status:15s} {package:15s} ({purpose})")
        
        print()
        return results
    
    # ==================== SINGLETON ====================
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'FallbackManager':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# ==================== CONVENIENCE FUNCTIONS ====================

def get_fallback_manager() -> FallbackManager:
    """Get global FallbackManager instance"""
    return FallbackManager.get_instance()


def check_dependencies() -> Dict[str, bool]:
    """Check all dependencies (convenience function)"""
    return get_fallback_manager().check_all_dependencies()


# ==================== MAIN ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PartMart Boost - Fallback Manager Test")
    print("="*60)
    
    manager = FallbackManager()
    
    # Check dependencies
    deps = manager.check_all_dependencies()
    
    # Test GPU fallback
    print("\n[Test] GPU Monitor Fallback:")
    gpu_monitor = manager.get_gpu_monitor_fallback()
    print(f"  Monitor: {gpu_monitor.get_name()}")
    print(f"  Available: {gpu_monitor.is_available()}")
    print(f"  Data: {gpu_monitor.get_data()}")
    
    # Test WMI fallback
    if platform.system() == 'Windows':
        print("\n[Test] WMI Fallback:")
        wmi = manager.get_wmi_fallback()
        if wmi:
            print(f"  WMI instance: {type(wmi).__name__}")
        else:
            print("  WMI unavailable")
    
    # Test CPU temp fallback
    print("\n[Test] CPU Temperature Fallback:")
    temp = manager.get_cpu_temp_fallback()
    if temp:
        print(f"  Temperature: {temp:.1f}°C")
    else:
        print("  Temperature unavailable")
    
    # Print status
    manager.print_status()
    
    print("\n[Result] Fallback system operational!")
    print("\nPartMart Boost can run even with missing dependencies.\n")
