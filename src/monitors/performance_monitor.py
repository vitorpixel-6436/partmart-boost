#!/usr/bin/env python3
"""Performance Monitor

Version: 0.3.5d (package 3.9a, stage 3/3)

System performance monitoring with real hardware data.

Package 3.9a Stage 3 Fixes:
- Replaced mock data with real hardware monitoring
- Integrated psutil for CPU/Memory
- Integrated GPUtil for GPU metrics
- Added data bus integration
"""
import time
import threading
import weakref
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from contextlib import contextmanager

# Try to import monitoring libraries
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[PerformanceMonitor] psutil not available, using fallback")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    print("[PerformanceMonitor] GPUtil not available, using fallback")


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    fps: float
    frame_time: float
    gpu_util: float
    cpu_util: float
    memory_used: float
    memory_total: float
    temperature: float
    power_draw: float


class PerformanceMonitor:
    """Performance Monitor v0.3.5d (package 3.9a)
    
    Package 3.9a Stage 3 Fixes:
    - Real hardware data collection
    - Data bus integration
    - Fallback to mock if hardware unavailable
    """
    
    MIN_TEMP = -50.0
    MAX_TEMP = 200.0
    MIN_UTIL = 0.0
    MAX_UTIL = 100.0
    MIN_POWER = 0.0
    MAX_POWER = 1000.0
    HEALTH_CHECK_INTERVAL = 60.0
    
    def __init__(self):
        self._lock = threading.RLock()
        self._running = False
        self._start_time: Optional[float] = None
        self._callbacks: List[weakref.ref] = []
        self._last_health_check: Optional[float] = None
        self._error_count = 0
        self._metric_count = 0
        self._allocated_resources: List[Any] = []
        
        # STAGE 3: Track current FPS for real metrics
        self._current_fps = 0.0
        
        # STAGE 3: Data bus integration
        try:
            from core.data_bus import PerformanceDataBus
            self._data_bus = PerformanceDataBus.get_instance()
        except ImportError:
            self._data_bus = None
            print("[PerformanceMonitor] Data bus not available")
        
        print(f"[PerformanceMonitor v0.3.5d] Initialized (psutil={PSUTIL_AVAILABLE}, GPUtil={GPUTIL_AVAILABLE})")
    
    def start(self) -> bool:
        with self._lock:
            if self._running:
                return False
            
            try:
                self._start_time = time.perf_counter()
                self._last_health_check = self._start_time
                self._running = True
                self._error_count = 0
                self._metric_count = 0
                return True
            except Exception as e:
                print(f"[PerformanceMonitor] Start failed: {e}")
                return False
    
    def stop(self):
        with self._lock:
            if not self._running:
                return
            
            try:
                self._cleanup_resources()
                self._running = False
            except Exception as e:
                print(f"[PerformanceMonitor] Stop error: {e}")
            finally:
                self._running = False
    
    def _cleanup_resources(self):
        for resource in reversed(self._allocated_resources):
            try:
                if hasattr(resource, '__exit__'):
                    resource.__exit__(None, None, None)
                elif hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            except Exception as e:
                print(f"[PerformanceMonitor] Resource cleanup error: {e}")
        
        self._allocated_resources.clear()
        self._callbacks.clear()
    
    def set_fps(self, fps: float):
        """Update current FPS (called by FPSTracker)
        
        Package 3.9a Stage 3: Added for real FPS tracking
        """
        self._current_fps = fps
    
    def get_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics
        
        Package 3.9a Stage 3: Returns real hardware data
        """
        with self._lock:
            if not self._running:
                return None
            
            try:
                self._check_health()
                metrics = self._collect_metrics()
                self._metric_count += 1
                
                # STAGE 3: Publish to data bus
                if self._data_bus:
                    self._data_bus.publish('performance_metrics', metrics)
                
                return metrics
            except Exception as e:
                self._error_count += 1
                print(f"[PerformanceMonitor] Metric error: {e}")
                return self._get_fallback_metrics()
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect real hardware metrics
        
        Package 3.9a Stage 3 Fix:
        - Real GPU data (GPUtil)
        - Real CPU data (psutil)
        - Real memory data (psutil)
        - Fallback to mock if unavailable
        """
        try:
            # STAGE 3 FIX: Collect REAL GPU metrics
            if GPUTIL_AVAILABLE:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # First GPU
                    gpu_util = gpu.load * 100
                    gpu_temp = gpu.temperature
                    gpu_memory_used = gpu.memoryUsed
                    gpu_memory_total = gpu.memoryTotal
                else:
                    # No GPU detected
                    gpu_util = 0.0
                    gpu_temp = 0.0
                    gpu_memory_used = 0.0
                    gpu_memory_total = 0.0
            else:
                # Fallback to mock
                gpu_util = 75.0
                gpu_temp = 65.0
                gpu_memory_used = 4096.0
                gpu_memory_total = 8192.0
            
            # STAGE 3 FIX: Collect REAL CPU metrics
            if PSUTIL_AVAILABLE:
                cpu_util = psutil.cpu_percent(interval=0.1)
                
                # Memory
                memory = psutil.virtual_memory()
                memory_used = memory.used / (1024 * 1024)  # MB
                memory_total = memory.total / (1024 * 1024)  # MB
                
                # Try to get CPU temperature
                try:
                    if hasattr(psutil, 'sensors_temperatures'):
                        temps = psutil.sensors_temperatures()
                        if temps:
                            # Get first available temperature
                            cpu_temp = list(temps.values())[0][0].current
                        else:
                            cpu_temp = 0.0
                    else:
                        cpu_temp = 0.0
                except:
                    cpu_temp = 0.0
            else:
                # Fallback to mock
                cpu_util = 60.0
                memory_used = 4096.0
                memory_total = 16384.0
                cpu_temp = 0.0
            
            # Temperature: prefer GPU, fallback to CPU
            temperature = gpu_temp if gpu_temp > 0 else cpu_temp
            if temperature == 0:
                # Last resort: estimate from load
                temperature = 40.0 + (gpu_util * 0.4)
            
            # Power: estimate from GPU utilization
            # Typical GPU TDP: 150-250W, assume 200W
            power_draw = (gpu_util / 100.0) * 200.0
            
            # FPS from tracker
            fps = self._current_fps
            frame_time = 1000.0 / max(fps, 1.0) if fps > 0 else 0.0
            
            return PerformanceMetrics(
                fps=self._validate_fps(fps),
                frame_time=self._validate_frame_time(frame_time),
                gpu_util=self._validate_percentage(gpu_util),
                cpu_util=self._validate_percentage(cpu_util),
                memory_used=self._validate_memory(memory_used),
                memory_total=self._validate_memory(memory_total),
                temperature=self._validate_temperature(temperature),
                power_draw=self._validate_power(power_draw),
            )
        
        except Exception as e:
            print(f"[PerformanceMonitor] Collection error: {e}")
            return self._get_fallback_metrics()
    
    def _get_fallback_metrics(self) -> PerformanceMetrics:
        """Get fallback metrics (all zeros)"""
        return PerformanceMetrics(
            fps=0.0, frame_time=0.0, gpu_util=0.0, cpu_util=0.0,
            memory_used=0.0, memory_total=0.0, temperature=0.0, power_draw=0.0
        )
    
    def _check_health(self):
        if self._last_health_check is None:
            return
        
        current_time = time.perf_counter()
        elapsed = (current_time - self._last_health_check) % (2**31)
        
        if elapsed >= self.HEALTH_CHECK_INTERVAL:
            error_rate = self._error_count / max(self._metric_count, 1)
            if error_rate > 0.1:
                print(f"[PerformanceMonitor] WARNING: High error rate ({error_rate:.1%})")
            self._last_health_check = current_time
    
    def register_callback(self, callback):
        with self._lock:
            self._callbacks.append(weakref.ref(callback))
    
    def _notify_callbacks(self, metrics: PerformanceMetrics):
        with self._lock:
            callbacks_copy = list(self._callbacks)
            alive_callbacks = []
            
            for callback_ref in callbacks_copy:
                callback = callback_ref()
                if callback is not None:
                    try:
                        callback(metrics)
                        alive_callbacks.append(callback_ref)
                    except Exception as e:
                        print(f"[PerformanceMonitor] Callback error: {e}")
            
            self._callbacks = alive_callbacks
    
    @contextmanager
    def measure_section(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            print(f"[PerformanceMonitor] {name}: {elapsed*1000:.2f}ms")
    
    @staticmethod
    def _validate_fps(fps: float) -> float:
        return max(0.1, min(1000.0, fps))
    
    @staticmethod
    def _validate_frame_time(ft: float) -> float:
        return max(0.001, min(10000.0, ft))
    
    @staticmethod
    def _validate_percentage(value: float) -> float:
        return max(0.0, min(100.0, value))
    
    @staticmethod
    def _validate_temperature(temp: float) -> float:
        return max(-50.0, min(200.0, temp))
    
    @staticmethod
    def _validate_power(power: float) -> float:
        return max(0.0, min(1000.0, power))
    
    @staticmethod
    def _validate_memory(memory: float) -> float:
        return max(0.0, memory)
    
    def get_uptime(self) -> float:
        with self._lock:
            if self._start_time is None:
                return 0.0
            return time.perf_counter() - self._start_time
    
    def get_health_stats(self) -> dict:
        with self._lock:
            return {
                'running': self._running,
                'uptime': self.get_uptime(),
                'metric_count': self._metric_count,
                'error_count': self._error_count,
                'error_rate': self._error_count / max(self._metric_count, 1),
                'callback_count': len(self._callbacks),
                'resource_count': len(self._allocated_resources),
                'psutil': PSUTIL_AVAILABLE,
                'gputil': GPUTIL_AVAILABLE,
            }
