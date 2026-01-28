"""Monitor Manager for unified system monitoring with sovereignty fallback.

PERFORMANCE: Orchestrates all monitors efficiently with automatic fallback.

Supports:
- FULL mode: psutil + pynvml + wmi
- NATIVE mode: Native OS APIs (WMIC, sysfs, ctypes)
- MINIMAL mode: Stub monitors (safe defaults)

Version: 0.3.5d - Package 2
"""
import time
from typing import Dict, List, Optional

# FIX: Import BaseMonitor directly from local module
from monitors import BaseMonitor


class MonitorManager:
    """Manages all system monitors with sovereignty fallback.
    
    v0.3.5d Package 2 improvements:
    - Consistent data schemas across all monitors
    - Health status tracking
    - Fixed stub data (0 instead of fake values)
    - Better error recovery
    """
    
    def __init__(self, prefer_native: bool = False):
        """Initialize monitor manager.
        
        Args:
            prefer_native: If True, use native monitors for max sovereignty
        """
        self.prefer_native = prefer_native
        
        # FIX: Import SovereigntyManager here to avoid circular import
        from core.sovereignty import SovereigntyManager
        self.sovereignty = SovereigntyManager(prefer_native=prefer_native)
        
        self.monitors: Dict[str, BaseMonitor] = {}
        
        self._init_monitors()
        
        # Performance tracking
        self._last_update_time = 0
        self._update_count = 0
        self._total_time = 0.0
        
        # Print sovereignty status
        score = self.sovereignty.get_sovereignty_score()
        print(f"\n[MonitorManager] Sovereignty Score: {score}/100")
    
    def _init_monitors(self):
        """Initialize all monitors with sovereignty fallback."""
        # GPU
        try:
            self.monitors['gpu'] = self.sovereignty.get_gpu_monitor()
            if self.monitors['gpu'] is not None:
                print(f"[OK] GPU Monitor: {self.monitors['gpu'].get_name()}")
                print(f"     Available: {self.monitors['gpu'].is_available()}")
            else:
                print("[WARN] GPU Monitor returned None")
                self.monitors['gpu'] = self._create_stub_monitor('gpu')
        except Exception as e:
            print(f"[ERROR] GPU Monitor init failed: {e}")
            self.monitors['gpu'] = self._create_stub_monitor('gpu')
        
        # CPU
        try:
            self.monitors['cpu'] = self.sovereignty.get_cpu_monitor()
            if self.monitors['cpu'] is not None:
                print(f"[OK] CPU Monitor: {self.monitors['cpu'].get_name()}")
                print(f"     Available: {self.monitors['cpu'].is_available()}")
            else:
                print("[WARN] CPU Monitor returned None")
                self.monitors['cpu'] = self._create_stub_monitor('cpu')
        except Exception as e:
            print(f"[ERROR] CPU Monitor init failed: {e}")
            self.monitors['cpu'] = self._create_stub_monitor('cpu')
        
        # RAM
        try:
            self.monitors['ram'] = self.sovereignty.get_ram_monitor()
            if self.monitors['ram'] is not None:
                print(f"[OK] RAM Monitor: {self.monitors['ram'].get_name()}")
                print(f"     Available: {self.monitors['ram'].is_available()}")
            else:
                print("[WARN] RAM Monitor returned None")
                self.monitors['ram'] = self._create_stub_monitor('ram')
        except Exception as e:
            print(f"[ERROR] RAM Monitor init failed: {e}")
            self.monitors['ram'] = self._create_stub_monitor('ram')
    
    def _create_stub_monitor(self, monitor_type: str) -> BaseMonitor:
        """Create stub monitor for fallback.
        
        Args:
            monitor_type: Type (gpu, cpu, ram)
        
        Returns:
            Stub monitor instance
        """
        class StubMonitor(BaseMonitor):
            def __init__(self, mtype: str):
                super().__init__()
                self.mtype = mtype
                self.available = False
            
            def get_name(self) -> str:
                return f"Stub {self.mtype.upper()} Monitor"
            
            def is_available(self) -> bool:
                return False
            
            def get_data(self) -> Dict:
                """v0.3.5d: Consistent schema with real monitors"""
                if self.mtype == 'gpu':
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
                        "memory_total": 0,  # v0.3.5d: Add memory fields
                        "memory_used": 0,
                        "memory_free": 0,
                    }
                elif self.mtype == 'cpu':
                    return {
                        "name": "Unknown CPU",
                        "load": 0.0,
                        "temp": None,
                        "freq": 0.0,
                        "freq_min": 0.0,
                        "freq_max": 0.0,
                        "count": 0,
                        "count_logical": 0,
                    }
                elif self.mtype == 'ram':
                    # v0.3.5d FIX: Return 0 instead of fake 16GB
                    return {
                        "total": 0.0,
                        "used": 0.0,
                        "free": 0.0,
                        "percent": 0.0,
                        "speed": None,  # v0.3.5d: None, not 0
                        "type": "Unknown",  # v0.3.5d: Add type field
                        "xmp_enabled": False,
                    }
                return {}
        
        return StubMonitor(monitor_type)
    
    def get_all_data(self) -> Dict:
        """Get data from all monitors (optimized).
        
        Returns:
            Dictionary with all system data
        
        v0.3.5d Package 2:
        - Add _monitor_health to each section
        - Better error recovery
        - Consistent schemas
        """
        start_time = time.time()
        
        data = {}
        
        # Collect from each monitor
        for name, monitor in self.monitors.items():
            try:
                # FIX: Always try to get data, even if not available
                monitor_data = monitor.get_data()
                
                if monitor_data:
                    # v0.3.5d: Add health status
                    monitor_data['_monitor_health'] = {
                        'available': monitor.is_available(),
                        'name': monitor.get_name(),
                        'error': monitor.get_last_error() if hasattr(monitor, 'get_last_error') else None,
                    }
                    data[name] = monitor_data
                else:
                    # Empty data from monitor
                    data[name] = self._get_empty_data(name)
                    data[name]['_monitor_health'] = {
                        'available': False,
                        'name': monitor.get_name(),
                        'error': 'Monitor returned empty data',
                    }
            
            except Exception as e:
                print(f"[ERROR] Failed to get {name} data: {e}")
                data[name] = self._get_empty_data(name)
                data[name]['_monitor_health'] = {
                    'available': False,
                    'name': f"{name} monitor",
                    'error': str(e),
                }
        
        # Track performance
        elapsed = time.time() - start_time
        self._last_update_time = elapsed
        self._update_count += 1
        self._total_time += elapsed
        
        return data
    
    def _get_empty_data(self, monitor_type: str) -> Dict:
        """Get empty data dict for monitor type.
        
        Args:
            monitor_type: Type of monitor (gpu, cpu, ram)
        
        Returns:
            Empty data dict
        
        v0.3.5d Package 2: Consistent with stub monitors
        """
        if monitor_type == 'gpu':
            return {
                "name": "No GPU",
                "temp_gpu": 0,
                "temp_hotspot": None,
                "clock_gpu": 0,
                "clock_mem": 0,
                "load_gpu": 0,
                "load_mem": 0,
                "power": 0,
                "fan_speed": 0,
                "memory_total": 0,  # v0.3.5d: Add memory fields
                "memory_used": 0,
                "memory_free": 0,
            }
        elif monitor_type == 'cpu':
            return {
                "name": "Unknown CPU",
                "load": 0.0,
                "temp": None,
                "freq": 0.0,
                "freq_min": 0.0,
                "freq_max": 0.0,
                "count": 0,
                "count_logical": 0,
            }
        elif monitor_type == 'ram':
            # v0.3.5d FIX: Return 0 instead of fake 16GB/50%
            return {
                "total": 0.0,
                "used": 0.0,
                "free": 0.0,
                "percent": 0.0,
                "speed": None,  # v0.3.5d: None, not 0
                "type": "Unknown",  # v0.3.5d: Add type field
                "xmp_enabled": False,
            }
        
        return {}
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics.
        
        Returns:
            Dictionary with perf stats
        """
        if self._update_count == 0:
            return {
                "avg_time_ms": 0,
                "last_time_ms": 0,
                "total_updates": 0,
            }
        
        avg_time = (self._total_time / self._update_count) * 1000
        last_time = self._last_update_time * 1000
        
        return {
            "avg_time_ms": avg_time,
            "last_time_ms": last_time,
            "total_updates": self._update_count,
        }
    
    def get_sovereignty_status(self) -> Dict:
        """Get sovereignty status.
        
        Returns:
            Sovereignty status dict
        """
        return self.sovereignty.get_sovereignty_status()
    
    def list_monitors(self) -> List[str]:
        """Get list of available monitors.
        
        Returns:
            List of monitor names
        """
        return [
            name for name, monitor in self.monitors.items()
            if monitor and monitor.is_available()
        ]
    
    def get_monitor(self, name: str) -> Optional[BaseMonitor]:
        """Get specific monitor.
        
        Args:
            name: Monitor name (gpu, cpu, ram)
        
        Returns:
            Monitor instance or None
        """
        return self.monitors.get(name)


if __name__ == "__main__":
    # Benchmark
    print("[TEST] MonitorManager v0.3.5d Package 2")
    print("="*60)
    
    # Test 1: Default (auto-detect)
    print("\n[TEST 1] AUTO-DETECT MODE")
    manager = MonitorManager(prefer_native=False)
    
    print("\n[INFO] Available monitors:")
    for monitor_name in manager.list_monitors():
        print(f"  - {monitor_name}")
    
    # Show sovereignty status
    status = manager.get_sovereignty_status()
    print("\n[INFO] Sovereignty Status:")
    print(f"  Level: {status['level']}")
    print(f"  Score: {status['score']}/100")
    print(f"  GPU: {status['gpu']}")
    print(f"  CPU: {status['cpu']}")
    print(f"  RAM: {status['ram']}")
    
    # Test data schema
    print("\n[TEST] Data Schema Validation (v0.3.5d):")
    data = manager.get_all_data()
    
    # Check GPU schema
    gpu_required = ['name', 'temp_gpu', 'load_gpu', 'memory_total', 'memory_used', 'memory_free']
    print("\n  GPU Schema:")
    for field in gpu_required:
        status = '✅' if field in data.get('gpu', {}) else '❌'
        print(f"    {status} {field}")
    
    # Check CPU schema
    cpu_required = ['name', 'load', 'temp', 'freq', 'count', 'count_logical']
    print("\n  CPU Schema:")
    for field in cpu_required:
        status = '✅' if field in data.get('cpu', {}) else '❌'
        print(f"    {status} {field}")
    
    # Check RAM schema
    ram_required = ['total', 'used', 'free', 'percent', 'speed', 'type', 'xmp_enabled']
    print("\n  RAM Schema:")
    for field in ram_required:
        status = '✅' if field in data.get('ram', {}) else '❌'
        value = data.get('ram', {}).get(field)
        print(f"    {status} {field}: {value}")
    
    # Check health status
    print("\n  Health Status:")
    for monitor_name in ['gpu', 'cpu', 'ram']:
        health = data.get(monitor_name, {}).get('_monitor_health', {})
        status = '✅' if health.get('available') else '❌'
        print(f"    {status} {monitor_name}: {health.get('name')}")
    
    print("\n" + "="*60)
    print("✅ MonitorManager v0.3.5d Package 2 works!")
    print("="*60)
