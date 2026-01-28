"""Monitor Manager for unified system monitoring with sovereignty fallback.

PERFORMANCE: Orchestrates all monitors efficiently with automatic fallback.

Supports:
- FULL mode: psutil + pynvml + wmi
- NATIVE mode: Native OS APIs (WMIC, sysfs, ctypes)
- MINIMAL mode: Stub monitors (safe defaults)
"""
import time
from typing import Dict, List, Optional
from monitors import BaseMonitor
from core.sovereignty import SovereigntyManager


class MonitorManager:
    """Manages all system monitors with sovereignty fallback."""
    
    def __init__(self, prefer_native: bool = False):
        """
        Initialize monitor manager.
        
        Args:
            prefer_native: If True, use native monitors for max sovereignty
        """
        self.prefer_native = prefer_native
        self.sovereignty = SovereigntyManager(prefer_native=prefer_native)
        self.monitors: Dict[str, BaseMonitor] = {}
        
        self._init_monitors()
        
        # Performance tracking
        self._last_update_time = 0
        self._update_count = 0
        self._total_time = 0.0
        
        # Print sovereignty status
        print(f"\n[MonitorManager] Sovereignty Score: {self.sovereignty.get_sovereignty_score()}/100")
    
    def _init_monitors(self):
        """Initialize all monitors with sovereignty fallback."""
        try:
            self.monitors['gpu'] = self.sovereignty.get_gpu_monitor()
            print(f"[OK] GPU Monitor: {self.monitors['gpu'].get_name()}")
            print(f"     Available: {self.monitors['gpu'].is_available()}")
        except Exception as e:
            print(f"[ERROR] GPU Monitor init failed: {e}")
        
        try:
            self.monitors['cpu'] = self.sovereignty.get_cpu_monitor()
            print(f"[OK] CPU Monitor: {self.monitors['cpu'].get_name()}")
            print(f"     Available: {self.monitors['cpu'].is_available()}")
        except Exception as e:
            print(f"[ERROR] CPU Monitor init failed: {e}")
        
        try:
            self.monitors['ram'] = self.sovereignty.get_ram_monitor()
            print(f"[OK] RAM Monitor: {self.monitors['ram'].get_name()}")
            print(f"     Available: {self.monitors['ram'].is_available()}")
        except Exception as e:
            print(f"[ERROR] RAM Monitor init failed: {e}")
    
    def get_all_data(self) -> Dict:
        """Get data from all monitors (optimized).
        
        Returns:
            Dictionary with all system data
        """
        start_time = time.time()
        
        data = {}
        
        # Collect from each monitor
        for name, monitor in self.monitors.items():
            try:
                if monitor.is_available():
                    data[name] = monitor.get_data()
                else:
                    data[name] = self._get_unavailable_data(name)
            except Exception as e:
                print(f"[ERROR] Failed to get {name} data: {e}")
                data[name] = self._get_unavailable_data(name)
        
        # Track performance
        elapsed = time.time() - start_time
        self._last_update_time = elapsed
        self._update_count += 1
        self._total_time += elapsed
        
        return data
    
    def _get_unavailable_data(self, monitor_type: str) -> Dict:
        """Get placeholder data for unavailable monitor.
        
        Args:
            monitor_type: Type of monitor (gpu, cpu, ram)
        
        Returns:
            Empty data dict
        """
        if monitor_type == 'gpu':
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
            }
        elif monitor_type == 'cpu':
            return {
                "name": "Unknown CPU",
                "load": 0,
                "temp": None,
                "freq": 0,
                "freq_min": 0,
                "freq_max": 0,
                "count": 0,
                "count_logical": 0,
            }
        elif monitor_type == 'ram':
            return {
                "total": 0,
                "used": 0,
                "free": 0,
                "percent": 0,
                "speed": 0,
                "type": "Unknown",
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
            if monitor.is_available()
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
    print("[TEST] MonitorManager Performance Benchmark")
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
    
    # Warmup
    print("\n[INFO] Warmup (10 iterations)...")
    for _ in range(10):
        manager.get_all_data()
        time.sleep(0.1)
    
    # Benchmark
    print("\n[INFO] Benchmark (100 iterations)...")
    iterations = 100
    start = time.time()
    
    for _ in range(iterations):
        data = manager.get_all_data()
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000
    
    print(f"\n[RESULT] {iterations} iterations in {elapsed:.3f}s")
    print(f"[RESULT] Average: {avg_time:.2f}ms per call")
    print(f"[RESULT] Target: <10ms")
    print(f"[RESULT] Status: {'PASS ✅' if avg_time < 10 else 'FAIL ❌'}")
    
    # Performance stats from manager
    stats = manager.get_performance_stats()
    print(f"\n[STATS] Manager internal metrics:")
    print(f"  Average time: {stats['avg_time_ms']:.2f}ms")
    print(f"  Last update: {stats['last_time_ms']:.2f}ms")
    print(f"  Total updates: {stats['total_updates']}")
    
    # Sample data
    print("\n[DATA] Sample output:")
    data = manager.get_all_data()
    for monitor_name, monitor_data in data.items():
        print(f"\n  {monitor_name.upper()}:")
        for k, v in list(monitor_data.items())[:5]:  # First 5 keys
            print(f"    {k}: {v}")
    
    # Test 2: Native mode (max sovereignty)
    print("\n" + "="*60)
    print("\n[TEST 2] NATIVE MODE (MAX SOVEREIGNTY)")
    manager_native = MonitorManager(prefer_native=True)
    
    status_native = manager_native.get_sovereignty_status()
    print("\n[INFO] Sovereignty Status:")
    print(f"  Level: {status_native['level']}")
    print(f"  Score: {status_native['score']}/100")
    print(f"  GPU: {status_native['gpu']}")
    print(f"  CPU: {status_native['cpu']}")
    print(f"  RAM: {status_native['ram']}")
    
    # Test data retrieval
    print("\n[INFO] Testing native monitors...")
    data_native = manager_native.get_all_data()
    print(f"  CPU Load: {data_native['cpu']['load']:.1f}%")
    print(f"  RAM Used: {data_native['ram']['used']:.2f} GB")
    
    print("\n" + "="*60)
    print("✅ MonitorManager with Sovereignty works!")
    print("="*60)
