#!/usr/bin/env python3
"""Performance Monitor Service with Error Handling

Version: 0.3.5n (package 3.9a, stage 7.7b.5.1/7.7)

Package 3.9a Stage 7.7b.5.1: Error handling in PerformanceMonitor service.

Features:
- Real-time hardware metrics collection
- CPU, GPU, RAM, FPS monitoring
- Thread-safe operation
- Comprehensive error handling
- Automatic recovery
- Metrics validation
"""
import threading
import time
import psutil
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

# GPU monitoring (optional)
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class MonitorState(Enum):
    """Monitor state enum"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot
    
    Attributes:
        cpu: CPU usage (0-100%)
        gpu: GPU usage (0-100%)
        ram: RAM usage (0-100%)
        fps: Current FPS
        cpu_temp: CPU temperature (°C)
        gpu_temp: GPU temperature (°C)
        score: Performance score (0-100)
        timestamp: Unix timestamp
    """
    cpu: float
    gpu: float
    ram: float
    fps: float
    cpu_temp: float
    gpu_temp: float
    score: float
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'cpu': self.cpu,
            'gpu': self.gpu,
            'ram': self.ram,
            'fps': self.fps,
            'cpu_temp': self.cpu_temp,
            'gpu_temp': self.gpu_temp,
            'score': self.score,
            'timestamp': self.timestamp,
        }
    
    def is_valid(self) -> bool:
        """Check if metrics are valid
        
        Returns:
            True if all values are in valid ranges
        """
        return (
            0 <= self.cpu <= 100 and
            0 <= self.gpu <= 100 and
            0 <= self.ram <= 100 and
            0 <= self.fps <= 500 and
            0 <= self.cpu_temp <= 150 and
            0 <= self.gpu_temp <= 150 and
            0 <= self.score <= 100
        )


class PerformanceMonitor:
    """Performance monitor service with error handling
    
    v0.3.5n (package 3.9a, stage 7.7b.5.1/7.7)
    
    Features:
    - Real-time hardware monitoring
    - Thread-safe operation
    - Comprehensive error handling
    - Automatic recovery
    - Metrics validation
    - Callback system
    
    Usage:
        >>> monitor = PerformanceMonitor(interval=100)
        >>> monitor.add_callback(lambda m: print(f"CPU: {m.cpu}%"))
        >>> monitor.start()
        >>> 
        >>> # Get current metrics
        >>> metrics = monitor.get_current_metrics()
        >>> print(f"CPU: {metrics['cpu']}%")
        >>> 
        >>> # Stop monitoring
        >>> monitor.stop()
    """
    
    def __init__(self, interval: int = 100):
        """Initialize monitor
        
        Args:
            interval: Update interval in milliseconds (10-5000)
        """
        self._interval = max(10, min(5000, interval))  # Clamp to valid range
        self._state = MonitorState.STOPPED
        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None
        self._logger = None
        
        # Current metrics
        self._current_metrics: Optional[PerformanceMetrics] = None
        self._last_valid_metrics: Optional[PerformanceMetrics] = None
        
        # Callbacks
        self._callbacks: List[Callable[[PerformanceMetrics], None]] = []
        
        # Error tracking
        self._error_count = 0
        self._max_errors = 10
        self._last_error_time = 0.0
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5
        
        # Performance tracking
        self._update_count = 0
        self._last_update_time = 0.0
        
        # Get logger if available
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug(f"PerformanceMonitor initializing (interval: {self._interval}ms)")
            except Exception:
                pass
        
        # Initialize psutil
        try:
            # First call to initialize
            psutil.cpu_percent(interval=None)
            self._log_debug("psutil initialized")
        except Exception as e:
            self._log_error(f"psutil initialization failed: {e}")
        
        self._log_info(f"Initialized (interval: {self._interval}ms, GPU: {GPU_AVAILABLE})")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="PerformanceMonitor")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="PerformanceMonitor")
        else:
            print(f"[PerformanceMonitor] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="PerformanceMonitor")
        else:
            print(f"[PerformanceMonitor] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="PerformanceMonitor", exc_info=exc_info)
        else:
            print(f"[PerformanceMonitor] ERROR: {message}")
    
    def start(self) -> bool:
        """Start monitoring
        
        Returns:
            True if started successfully
        """
        try:
            with self._lock:
                if self._state == MonitorState.RUNNING:
                    self._log_info("Already running")
                    return True
                
                if self._state == MonitorState.STARTING:
                    self._log_warning("Already starting")
                    return False
                
                self._state = MonitorState.STARTING
                self._error_count = 0
                self._consecutive_errors = 0
            
            # Start worker thread
            self._thread = threading.Thread(
                target=self._worker,
                name='PerformanceMonitor',
                daemon=True
            )
            self._thread.start()
            
            # Wait for first update
            time.sleep(0.1)
            
            with self._lock:
                if self._state == MonitorState.RUNNING:
                    self._log_info("Started successfully")
                    return True
                else:
                    self._log_error("Failed to start")
                    return False
        
        except Exception as e:
            self._log_error(f"Start failed: {e}", exc_info=True)
            with self._lock:
                self._state = MonitorState.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop monitoring
        
        Returns:
            True if stopped successfully
        """
        try:
            with self._lock:
                if self._state == MonitorState.STOPPED:
                    self._log_debug("Already stopped")
                    return True
                
                self._state = MonitorState.STOPPING
            
            # Wait for thread to stop
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)
                
                if self._thread.is_alive():
                    self._log_warning("Thread did not stop gracefully")
                    return False
            
            with self._lock:
                self._state = MonitorState.STOPPED
            
            self._log_info("Stopped successfully")
            return True
        
        except Exception as e:
            self._log_error(f"Stop failed: {e}", exc_info=True)
            return False
    
    def _worker(self):
        """Worker thread with error handling"""
        self._log_debug("Worker thread started")
        
        with self._lock:
            self._state = MonitorState.RUNNING
        
        interval_sec = self._interval / 1000.0
        
        while True:
            with self._lock:
                if self._state != MonitorState.RUNNING:
                    break
            
            try:
                # Check error threshold
                if self._consecutive_errors >= self._max_consecutive_errors:
                    self._log_error(f"Too many consecutive errors ({self._consecutive_errors}), stopping")
                    break
                
                # Collect metrics
                start_time = time.time()
                metrics = self._collect_metrics()
                
                # Validate and store
                if metrics and metrics.is_valid():
                    with self._lock:
                        self._current_metrics = metrics
                        self._last_valid_metrics = metrics
                        self._consecutive_errors = 0
                        self._update_count += 1
                        self._last_update_time = time.time()
                    
                    # Notify callbacks
                    self._notify_callbacks(metrics)
                else:
                    self._handle_invalid_metrics(metrics)
                
                # Sleep for remaining interval
                elapsed = time.time() - start_time
                sleep_time = max(0, interval_sec - elapsed)
                time.sleep(sleep_time)
            
            except Exception as e:
                self._handle_worker_error(e)
        
        with self._lock:
            self._state = MonitorState.STOPPED
        
        self._log_debug("Worker thread stopped")
    
    def _collect_metrics(self) -> Optional[PerformanceMetrics]:
        """Collect hardware metrics with error handling
        
        Returns:
            PerformanceMetrics or None on error
        """
        try:
            # CPU usage
            cpu = self._get_cpu_usage()
            
            # GPU usage
            gpu = self._get_gpu_usage()
            
            # RAM usage
            ram = self._get_ram_usage()
            
            # FPS (placeholder for now)
            fps = 0.0
            
            # Temperatures
            cpu_temp = self._get_cpu_temp()
            gpu_temp = self._get_gpu_temp()
            
            # Calculate score
            score = self._calculate_score(cpu, gpu, ram, fps)
            
            # Create metrics
            metrics = PerformanceMetrics(
                cpu=cpu,
                gpu=gpu,
                ram=ram,
                fps=fps,
                cpu_temp=cpu_temp,
                gpu_temp=gpu_temp,
                score=score,
                timestamp=time.time()
            )
            
            return metrics
        
        except Exception as e:
            self._log_error(f"Metrics collection failed: {e}", exc_info=True)
            return None
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage with error handling
        
        Returns:
            CPU usage percentage (0-100)
        """
        try:
            cpu = psutil.cpu_percent(interval=None)
            return max(0.0, min(100.0, cpu))
        
        except Exception as e:
            self._log_warning(f"CPU usage failed: {e}")
            # Return last known value or 0
            if self._last_valid_metrics:
                return self._last_valid_metrics.cpu
            return 0.0
    
    def _get_gpu_usage(self) -> float:
        """Get GPU usage with error handling
        
        Returns:
            GPU usage percentage (0-100)
        """
        try:
            if not GPU_AVAILABLE:
                return 0.0
            
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0].load * 100
                return max(0.0, min(100.0, gpu))
            
            return 0.0
        
        except Exception as e:
            self._log_warning(f"GPU usage failed: {e}")
            if self._last_valid_metrics:
                return self._last_valid_metrics.gpu
            return 0.0
    
    def _get_ram_usage(self) -> float:
        """Get RAM usage with error handling
        
        Returns:
            RAM usage percentage (0-100)
        """
        try:
            memory = psutil.virtual_memory()
            return max(0.0, min(100.0, memory.percent))
        
        except Exception as e:
            self._log_warning(f"RAM usage failed: {e}")
            if self._last_valid_metrics:
                return self._last_valid_metrics.ram
            return 0.0
    
    def _get_cpu_temp(self) -> float:
        """Get CPU temperature with error handling
        
        Returns:
            CPU temperature in Celsius (0-150)
        """
        try:
            temps = psutil.sensors_temperatures()
            
            # Try to find CPU temp
            for name, entries in temps.items():
                if 'cpu' in name.lower() or 'core' in name.lower():
                    if entries:
                        temp = entries[0].current
                        return max(0.0, min(150.0, temp))
            
            return 0.0
        
        except AttributeError:
            # sensors_temperatures not supported on this platform
            return 0.0
        
        except Exception as e:
            self._log_warning(f"CPU temp failed: {e}")
            return 0.0
    
    def _get_gpu_temp(self) -> float:
        """Get GPU temperature with error handling
        
        Returns:
            GPU temperature in Celsius (0-150)
        """
        try:
            if not GPU_AVAILABLE:
                return 0.0
            
            gpus = GPUtil.getGPUs()
            if gpus:
                temp = gpus[0].temperature
                return max(0.0, min(150.0, temp))
            
            return 0.0
        
        except Exception as e:
            self._log_warning(f"GPU temp failed: {e}")
            return 0.0
    
    def _calculate_score(self, cpu: float, gpu: float, ram: float, fps: float) -> float:
        """Calculate performance score
        
        Args:
            cpu: CPU usage
            gpu: GPU usage
            ram: RAM usage
            fps: FPS
        
        Returns:
            Performance score (0-100)
        """
        try:
            # Invert usage percentages (lower is better)
            cpu_score = 100 - cpu
            gpu_score = 100 - gpu
            ram_score = 100 - ram
            fps_score = min(100, fps * 1.67)  # 60 FPS = 100 score
            
            # Weighted average
            score = (
                cpu_score * 0.3 +
                gpu_score * 0.3 +
                ram_score * 0.2 +
                fps_score * 0.2
            )
            
            return max(0.0, min(100.0, score))
        
        except Exception as e:
            self._log_warning(f"Score calculation failed: {e}")
            return 50.0  # Default middle score
    
    def _handle_invalid_metrics(self, metrics: Optional[PerformanceMetrics]):
        """Handle invalid metrics
        
        Args:
            metrics: Invalid metrics or None
        """
        self._consecutive_errors += 1
        
        if metrics:
            self._log_warning(f"Invalid metrics: {metrics.to_dict()}")
        else:
            self._log_warning("Metrics collection returned None")
        
        # Use last valid metrics if available
        if self._last_valid_metrics:
            with self._lock:
                self._current_metrics = self._last_valid_metrics
    
    def _handle_worker_error(self, error: Exception):
        """Handle worker thread error
        
        Args:
            error: Exception that occurred
        """
        now = time.time()
        
        # Reset error count if enough time has passed
        if now - self._last_error_time > 60.0:
            self._error_count = 0
        
        self._error_count += 1
        self._consecutive_errors += 1
        self._last_error_time = now
        
        self._log_error(
            f"Worker error ({self._error_count}/{self._max_errors}, consecutive: {self._consecutive_errors}): {error}",
            exc_info=True
        )
        
        # Sleep longer after error
        time.sleep(1.0)
    
    def _notify_callbacks(self, metrics: PerformanceMetrics):
        """Notify callbacks with error isolation
        
        Args:
            metrics: Performance metrics
        """
        for callback in self._callbacks:
            try:
                callback(metrics)
            except Exception as e:
                self._log_error(f"Callback error: {e}", exc_info=True)
    
    def add_callback(self, callback: Callable[[PerformanceMetrics], None]) -> int:
        """Add metrics callback
        
        Args:
            callback: Callback function(metrics)
        
        Returns:
            Callback ID
        """
        try:
            with self._lock:
                callback_id = len(self._callbacks)
                self._callbacks.append(callback)
                self._log_debug(f"Added callback (ID: {callback_id})")
                return callback_id
        
        except Exception as e:
            self._log_error(f"Failed to add callback: {e}")
            return -1
    
    def remove_callback(self, callback_id: int):
        """Remove callback
        
        Args:
            callback_id: Callback ID
        """
        try:
            with self._lock:
                if 0 <= callback_id < len(self._callbacks):
                    self._callbacks[callback_id] = lambda m: None  # No-op
                    self._log_debug(f"Removed callback (ID: {callback_id})")
        
        except Exception as e:
            self._log_error(f"Failed to remove callback: {e}")
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current metrics as dictionary
        
        Returns:
            Metrics dictionary or None if not available
        """
        try:
            with self._lock:
                if self._current_metrics:
                    return self._current_metrics.to_dict()
                return None
        
        except Exception as e:
            self._log_error(f"Failed to get current metrics: {e}")
            return None
    
    def get_state(self) -> MonitorState:
        """Get current state
        
        Returns:
            Current monitor state
        """
        try:
            with self._lock:
                return self._state
        except Exception:
            return MonitorState.ERROR
    
    def is_running(self) -> bool:
        """Check if monitoring is running
        
        Returns:
            True if running
        """
        return self.get_state() == MonitorState.RUNNING
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status
        
        Returns:
            Status dictionary
        """
        try:
            with self._lock:
                return {
                    'state': self._state.value,
                    'interval': self._interval,
                    'update_count': self._update_count,
                    'error_count': self._error_count,
                    'consecutive_errors': self._consecutive_errors,
                    'has_metrics': self._current_metrics is not None,
                    'gpu_available': GPU_AVAILABLE,
                    'last_update': self._last_update_time,
                }
        
        except Exception as e:
            self._log_error(f"Failed to get status: {e}")
            return {'error': str(e)}


# Testing
if __name__ == '__main__':
    print("="*60)
    print("PerformanceMonitor Test (with Error Handling)")
    print("="*60)
    print()
    
    # Create monitor
    monitor = PerformanceMonitor(interval=100)
    
    # Add callback
    def print_metrics(metrics: PerformanceMetrics):
        print(f"CPU: {metrics.cpu:.1f}%, GPU: {metrics.gpu:.1f}%, RAM: {metrics.ram:.1f}%, Score: {metrics.score:.1f}")
    
    monitor.add_callback(print_metrics)
    
    # Start monitoring
    print("Starting monitor...")
    if monitor.start():
        print("✅ Started\n")
    else:
        print("❌ Failed to start\n")
    
    # Run for 10 seconds
    print("Monitoring for 10 seconds...\n")
    time.sleep(10)
    
    # Get status
    status = monitor.get_status()
    print("\nStatus:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Stop
    print("\nStopping monitor...")
    if monitor.stop():
        print("✅ Stopped")
    else:
        print("❌ Failed to stop")
    
    print()
    print("✅ Test completed!")
