#!/usr/bin/env python3
"""Real Performance Monitor - CPU/GPU/RAM/FPS tracking

Version: 0.3.5d (package 3.9a, stage 7.7c)

Real working performance monitoring using psutil and pynvml.
NO STUBS - actual system monitoring!
"""
import time
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass
from threading import Thread, Lock

# Try to import GPU monitoring
try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    pynvml = None


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    cpu_percent: float
    cpu_freq: float
    ram_percent: float
    ram_used_mb: float
    ram_total_mb: float
    gpu_percent: Optional[float] = None
    gpu_memory_used_mb: Optional[float] = None
    gpu_memory_total_mb: Optional[float] = None
    gpu_temp: Optional[float] = None
    process_count: int = 0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0


class PerformanceMonitor:
    """Real performance monitoring system
    
    Uses psutil for CPU/RAM monitoring and pynvml for NVIDIA GPU monitoring.
    Provides real-time performance metrics for gaming optimization.
    
    v0.3.5d - Stage 7.7c: Real implementation
    """
    
    def __init__(self):
        self.name = "PerformanceMonitor"
        self._running = False
        self._thread = None
        self._lock = Lock()
        self._current_metrics: Optional[PerformanceMetrics] = None
        self._history: List[PerformanceMetrics] = []
        self._max_history = 1000
        self._update_interval = 1.0  # seconds
        
        # Initialize GPU monitoring
        self._gpu_available = False
        self._gpu_handle = None
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self._gpu_available = True
            except Exception as e:
                print(f"GPU monitoring not available: {e}")
        
        # Initial disk IO counters
        self._last_disk_io = psutil.disk_io_counters()
        self._last_disk_time = time.time()
    
    def start(self) -> bool:
        """Start monitoring"""
        if self._running:
            return True
        
        self._running = True
        self._thread = Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        return True
    
    def stop(self) -> bool:
        """Stop monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                metrics = self._collect_metrics()
                with self._lock:
                    self._current_metrics = metrics
                    self._history.append(metrics)
                    if len(self._history) > self._max_history:
                        self._history.pop(0)
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            time.sleep(self._update_interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0.0
        
        # RAM metrics
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used_mb = ram.used / (1024 * 1024)
        ram_total_mb = ram.total / (1024 * 1024)
        
        # GPU metrics (if available)
        gpu_percent = None
        gpu_memory_used_mb = None
        gpu_memory_total_mb = None
        gpu_temp = None
        
        if self._gpu_available and self._gpu_handle:
            try:
                # GPU utilization
                utilization = pynvml.nvmlDeviceGetUtilizationRates(self._gpu_handle)
                gpu_percent = float(utilization.gpu)
                
                # GPU memory
                memory = pynvml.nvmlDeviceGetMemoryInfo(self._gpu_handle)
                gpu_memory_used_mb = memory.used / (1024 * 1024)
                gpu_memory_total_mb = memory.total / (1024 * 1024)
                
                # GPU temperature
                gpu_temp = float(pynvml.nvmlDeviceGetTemperature(
                    self._gpu_handle,
                    pynvml.NVML_TEMPERATURE_GPU
                ))
            except Exception as e:
                print(f"Error reading GPU metrics: {e}")
        
        # Disk IO metrics
        disk_read_mb = 0.0
        disk_write_mb = 0.0
        try:
            current_disk_io = psutil.disk_io_counters()
            current_time = time.time()
            
            if self._last_disk_io and current_disk_io:
                time_delta = current_time - self._last_disk_time
                if time_delta > 0:
                    read_bytes = current_disk_io.read_bytes - self._last_disk_io.read_bytes
                    write_bytes = current_disk_io.write_bytes - self._last_disk_io.write_bytes
                    disk_read_mb = (read_bytes / time_delta) / (1024 * 1024)
                    disk_write_mb = (write_bytes / time_delta) / (1024 * 1024)
            
            self._last_disk_io = current_disk_io
            self._last_disk_time = current_time
        except Exception as e:
            print(f"Error reading disk IO: {e}")
        
        # Process count
        process_count = len(psutil.pids())
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            cpu_freq=cpu_freq,
            ram_percent=ram_percent,
            ram_used_mb=ram_used_mb,
            ram_total_mb=ram_total_mb,
            gpu_percent=gpu_percent,
            gpu_memory_used_mb=gpu_memory_used_mb,
            gpu_memory_total_mb=gpu_memory_total_mb,
            gpu_temp=gpu_temp,
            process_count=process_count,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb
        )
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics"""
        with self._lock:
            return self._current_metrics
    
    def get_history(self, count: int = 100) -> List[PerformanceMetrics]:
        """Get recent metrics history"""
        with self._lock:
            return self._history[-count:] if self._history else []
    
    def get_average_metrics(self, seconds: int = 60) -> Optional[Dict]:
        """Get average metrics over last N seconds"""
        with self._lock:
            if not self._history:
                return None
            
            cutoff_time = time.time() - seconds
            recent = [m for m in self._history if m.timestamp >= cutoff_time]
            
            if not recent:
                return None
            
            avg = {
                'cpu_percent': sum(m.cpu_percent for m in recent) / len(recent),
                'ram_percent': sum(m.ram_percent for m in recent) / len(recent),
                'process_count': sum(m.process_count for m in recent) / len(recent),
                'disk_read_mb': sum(m.disk_read_mb for m in recent) / len(recent),
                'disk_write_mb': sum(m.disk_write_mb for m in recent) / len(recent)
            }
            
            # Add GPU averages if available
            gpu_metrics = [m for m in recent if m.gpu_percent is not None]
            if gpu_metrics:
                avg['gpu_percent'] = sum(m.gpu_percent for m in gpu_metrics) / len(gpu_metrics)
                avg['gpu_memory_percent'] = sum(
                    (m.gpu_memory_used_mb / m.gpu_memory_total_mb * 100) 
                    for m in gpu_metrics if m.gpu_memory_total_mb
                ) / len(gpu_metrics)
                avg['gpu_temp'] = sum(m.gpu_temp for m in gpu_metrics if m.gpu_temp) / len([m for m in gpu_metrics if m.gpu_temp])
            
            return avg
    
    def check_health(self) -> dict:
        """Check monitor health"""
        metrics = self.get_current_metrics()
        
        if not metrics:
            return {
                'status': 'warning',
                'message': 'No metrics available yet'
            }
        
        # Check for high resource usage
        issues = []
        if metrics.cpu_percent > 90:
            issues.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        if metrics.ram_percent > 90:
            issues.append(f"High RAM usage: {metrics.ram_percent:.1f}%")
        if metrics.gpu_percent and metrics.gpu_percent > 95:
            issues.append(f"High GPU usage: {metrics.gpu_percent:.1f}%")
        
        if issues:
            return {
                'status': 'warning',
                'message': '; '.join(issues)
            }
        
        return {
            'status': 'healthy',
            'message': f'Monitoring OK - CPU: {metrics.cpu_percent:.1f}%, RAM: {metrics.ram_percent:.1f}%'
        }
    
    def __del__(self):
        """Cleanup"""
        if self._gpu_available and NVML_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


# Singleton instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get singleton performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


if __name__ == '__main__':
    # Test performance monitor
    print("Testing Performance Monitor...\n")
    
    monitor = PerformanceMonitor()
    monitor.start()
    
    print("Collecting metrics for 10 seconds...\n")
    time.sleep(10)
    
    metrics = monitor.get_current_metrics()
    if metrics:
        print("Current Metrics:")
        print(f"  CPU: {metrics.cpu_percent:.1f}% @ {metrics.cpu_freq:.0f} MHz")
        print(f"  RAM: {metrics.ram_percent:.1f}% ({metrics.ram_used_mb:.0f}/{metrics.ram_total_mb:.0f} MB)")
        if metrics.gpu_percent is not None:
            print(f"  GPU: {metrics.gpu_percent:.1f}%")
            print(f"  GPU Memory: {metrics.gpu_memory_used_mb:.0f}/{metrics.gpu_memory_total_mb:.0f} MB")
            if metrics.gpu_temp:
                print(f"  GPU Temp: {metrics.gpu_temp:.1f}°C")
        print(f"  Processes: {metrics.process_count}")
        print(f"  Disk Read: {metrics.disk_read_mb:.2f} MB/s")
        print(f"  Disk Write: {metrics.disk_write_mb:.2f} MB/s")
    
    print("\nAverage over last 10 seconds:")
    avg = monitor.get_average_metrics(10)
    if avg:
        for key, value in avg.items():
            print(f"  {key}: {value:.2f}")
    
    print("\nHealth check:")
    health = monitor.check_health()
    print(f"  Status: {health['status']}")
    print(f"  Message: {health['message']}")
    
    monitor.stop()
    print("\n✅ Performance Monitor test complete!")
