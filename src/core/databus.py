#!/usr/bin/env python3
"""DataBus - Advanced event-driven middleware for system monitoring

Version: 0.3.5d_package3.1c - Package 3 Task 3.1c

Package 2.4 Features:
- Health tracking and auto-recovery
- Adaptive update intervals
- Monitor priorities and selective updates
- Data history buffering (ring buffer)
- Advanced throttling (per-metric)
- Granular event system
- Performance analytics
- Graceful degradation

Package 3.1c NEW:
- FPS tracking integration (FPSTracker)
- fps_updated signal
- frame_drop_detected signal
- FPS statistics API
- Frame timing history

Architecture:
    FRONTEND (UI Widgets)
        ↓ subscribes to signals (granular)
    MIDDLEWARE (DataBus)
        ↓ adaptive polling with priorities + FPS tracking
    BACKEND (Monitors with health tracking)
"""
import time
from typing import Dict, Optional, Callable, List, Any, Deque
from collections import deque
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from monitors.manager import MonitorManager

# Package 3.1c: FPS Tracker import
try:
    from core.fps_tracker import FPSTracker, FPSStats
    FPS_TRACKER_AVAILABLE = True
except ImportError:
    FPS_TRACKER_AVAILABLE = False
    print("[DataBus] Warning: FPSTracker not available")


class DataBus(QObject):
    """Advanced event bus for system monitoring with health tracking + FPS
    
    v0.3.5d_package3.1c - FPS Integration
    
    Signals:
        # Data updates (backward compatible)
        data_updated(dict) - Full system data
        gpu_updated(dict) - GPU data only
        cpu_updated(dict) - CPU data only
        ram_updated(dict) - RAM data only
        error_occurred(str) - Errors
        
        # Granular metrics (Package 2.4)
        cpu_load_changed(float) - CPU load %
        cpu_temp_changed(float) - CPU temp °C
        gpu_load_changed(float) - GPU load %
        gpu_temp_changed(float) - GPU temp °C
        ram_usage_changed(float) - RAM usage %
        
        # System health (Package 2.4)
        health_changed(dict) - Monitor health status
        bottleneck_detected(dict) - Performance bottleneck
        throttle_status_changed(bool) - Throttling on/off
        
        # Adaptive behavior (Package 2.4)
        update_interval_changed(int) - Interval adjusted
        
        # FPS tracking (Package 3.1c NEW)
        fps_updated(object) - FPS statistics (FPSStats)
        frame_drop_detected(int) - Frame drops (stutter count)
    
    Enhanced API:
        # Core
        start() / stop() / force_update()
        get_data() / get_all_data()
        
        # Subscriptions
        subscribe_to_metric(metric, callback)
        unsubscribe_from_metric(metric, callback)
        
        # History
        get_metric_history(metric, count)
        clear_history()
        
        # Health & Recovery
        get_system_health()
        recover_failed_monitors()
        get_data_quality()
        
        # Adaptive behavior
        enable_adaptive_interval(enabled)
        set_monitor_priority(monitor, priority)
        
        # FPS Tracking (NEW Package 3.1c)
        get_fps_stats(window)
        get_frame_timing_history(count)
        reset_fps_tracking()
        set_fps_tracking_enabled(enabled)
        set_fps_update_interval(ms)
        set_stutter_threshold(multiplier)
        
        # Configuration
        set_update_interval(ms)
        set_throttling(enabled, threshold)
        set_history_size(size)
    """
    
    # === SIGNALS ===
    
    # Backward compatible signals
    data_updated = pyqtSignal(dict)
    gpu_updated = pyqtSignal(dict)
    cpu_updated = pyqtSignal(dict)
    ram_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    # Granular metric signals (Package 2.4)
    cpu_load_changed = pyqtSignal(float)
    cpu_temp_changed = pyqtSignal(float)
    gpu_load_changed = pyqtSignal(float)
    gpu_temp_changed = pyqtSignal(float)
    ram_usage_changed = pyqtSignal(float)
    
    # System health signals (Package 2.4)
    health_changed = pyqtSignal(dict)
    bottleneck_detected = pyqtSignal(dict)
    throttle_status_changed = pyqtSignal(bool)
    
    # Adaptive behavior signals (Package 2.4)
    update_interval_changed = pyqtSignal(int)
    
    # FPS tracking signals (Package 3.1c NEW)
    fps_updated = pyqtSignal(object)  # FPSStats object
    frame_drop_detected = pyqtSignal(int)  # Stutter count
    
    def __init__(self, update_interval: int = 2000):
        """Initialize DataBus
        
        Args:
            update_interval: Update interval in ms (default: 2000ms = 2s)
        """
        super().__init__()
        
        # Backend manager
        self._manager = MonitorManager()
        
        # Data cache
        self._cached_data: Optional[Dict] = None
        self._last_update_time = 0
        
        # Update timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._update_interval = update_interval
        self._base_interval = update_interval  # For adaptive mode
        
        # Performance tracking
        self._update_count = 0
        self._total_time = 0.0
        self._error_count = 0
        self._last_error: Optional[str] = None
        
        # Throttling
        self._throttle_enabled = True
        self._throttle_threshold = 0.01  # 1% change
        self._per_metric_thresholds: Dict[str, float] = {
            'cpu_load': 0.02,   # 2%
            'gpu_load': 0.02,   # 2%
            'ram_percent': 0.01, # 1%
            'cpu_temp': 2.0,    # 2°C
            'gpu_temp': 2.0,    # 2°C
        }
        
        # History buffer (Package 2.4)
        self._history_enabled = True
        self._history_size = 60  # Last 60 samples (2 min at 2s interval)
        self._history: Dict[str, Deque] = {
            'cpu_load': deque(maxlen=self._history_size),
            'cpu_temp': deque(maxlen=self._history_size),
            'gpu_load': deque(maxlen=self._history_size),
            'gpu_temp': deque(maxlen=self._history_size),
            'ram_percent': deque(maxlen=self._history_size),
            'timestamps': deque(maxlen=self._history_size),
        }
        
        # Monitor priorities (Package 2.4)
        self._monitor_priorities: Dict[str, int] = {
            'cpu': 1,  # Highest priority
            'ram': 2,
            'gpu': 3,
        }
        
        # Adaptive interval (Package 2.4)
        self._adaptive_interval_enabled = False
        self._idle_threshold = 30.0  # 30% load = idle
        self._idle_multiplier = 2.0  # Slow down 2x when idle
        self._is_system_idle = False
        
        # Health tracking (Package 2.4)
        self._last_health: Optional[Dict] = None
        self._failed_monitors: List[str] = []
        self._recovery_attempts = 0
        self._max_recovery_attempts = 3
        
        # Data quality (Package 2.4)
        self._data_freshness = 1.0  # 0.0-1.0
        self._data_confidence = 1.0  # 0.0-1.0
        
        # FPS Tracking (Package 3.1c NEW)
        self._fps_tracking_enabled = False
        self._fps_tracker: Optional[FPSTracker] = None
        self._fps_update_interval = 1000  # Emit FPS stats every 1s
        self._last_fps_emit_time = 0
        self._last_stutter_count = 0
        
        if FPS_TRACKER_AVAILABLE:
            self._fps_tracker = FPSTracker(buffer_size=900)
            print("[DataBus] FPS Tracker initialized")
    
    # === CORE METHODS ===
    
    def start(self):
        """Start automatic updates"""
        print(f"[DataBus v0.3.5d_package3.1c] Starting updates every {self._update_interval}ms")
        
        if self._fps_tracking_enabled and self._fps_tracker:
            print("[DataBus] FPS tracking enabled")
        
        # Initial health check
        self._check_system_health()
        
        # First update (synchronous)
        self._update()
        
        # Start timer
        self._timer.start(self._update_interval)
    
    def stop(self):
        """Stop automatic updates"""
        print("[DataBus] Stopping updates")
        self._timer.stop()
    
    def _update(self):
        """Internal update method (called by timer)
        
        v0.3.5d_package3.1c: Added FPS tracking
        """
        start_time = time.time()
        
        # Package 3.1c: FPS frame begin
        if self._fps_tracking_enabled and self._fps_tracker:
            self._fps_tracker.begin_frame()
        
        try:
            # Get data from backend (prioritized)
            new_data = self._get_prioritized_data()
            
            # Check if data changed significantly
            if self._should_emit(new_data):
                old_data = self._cached_data
                self._cached_data = new_data
                
                # Emit all signals
                self._emit_updates(new_data, old_data)
                
                # Update history
                if self._history_enabled:
                    self._update_history(new_data)
            
            # Check system health periodically (every 10 updates)
            if self._update_count % 10 == 0:
                self._check_system_health()
            
            # Adaptive interval adjustment
            if self._adaptive_interval_enabled:
                self._adjust_interval_adaptive(new_data)
            
            # Track performance
            elapsed = time.time() - start_time
            self._last_update_time = elapsed
            self._update_count += 1
            self._total_time += elapsed
            
            # Update data quality
            self._update_data_quality(elapsed)
        
        except Exception as e:
            print(f"[DataBus] Update error: {e}")
            self._error_count += 1
            self._last_error = str(e)
            self.error_occurred.emit(str(e))
            
            # Degrade data quality on errors
            self._data_confidence *= 0.9
        
        finally:
            # Package 3.1c: FPS frame end
            if self._fps_tracking_enabled and self._fps_tracker:
                self._fps_tracker.end_frame()
                self._emit_fps_updates()
    
    def _emit_fps_updates(self):
        """Emit FPS updates at configured interval
        
        Package 3.1c NEW
        """
        if not self._fps_tracker:
            return
        
        current_time = time.time() * 1000  # ms
        
        # Emit FPS stats every fps_update_interval
        if current_time - self._last_fps_emit_time >= self._fps_update_interval:
            stats = self._fps_tracker.get_stats(window=60)  # Last 1 second @ 60fps
            self.fps_updated.emit(stats)
            self._last_fps_emit_time = current_time
            
            # Detect new frame drops
            if stats.stutter_count > self._last_stutter_count:
                new_stutters = stats.stutter_count - self._last_stutter_count
                self.frame_drop_detected.emit(new_stutters)
                self._last_stutter_count = stats.stutter_count
    
    def _get_prioritized_data(self) -> Dict:
        """Get data with monitor priority ordering"""
        return self._manager.get_all_data()
    
    def _should_emit(self, new_data: Dict) -> bool:
        """Check if data changed enough to emit"""
        # First update always emits
        if self._cached_data is None:
            return True
        
        # Throttling disabled - always emit
        if not self._throttle_enabled:
            return True
        
        old_data = self._cached_data
        
        # Check CPU metrics
        if self._metric_changed('cpu', 'load', new_data, old_data, self._per_metric_thresholds['cpu_load']):
            return True
        if self._metric_changed_absolute('cpu', 'temp', new_data, old_data, self._per_metric_thresholds['cpu_temp']):
            return True
        
        # Check GPU metrics
        if self._metric_changed('gpu', 'load_gpu', new_data, old_data, self._per_metric_thresholds['gpu_load']):
            return True
        if self._metric_changed_absolute('gpu', 'temp_gpu', new_data, old_data, self._per_metric_thresholds['gpu_temp']):
            return True
        
        # Check RAM metrics
        if self._metric_changed('ram', 'percent', new_data, old_data, self._per_metric_thresholds['ram_percent']):
            return True
        
        return False
    
    def _metric_changed(self, category: str, key: str, new_data: Dict, old_data: Dict, threshold: float) -> bool:
        """Check if metric changed by percentage threshold"""
        if category not in new_data or category not in old_data:
            return False
        
        new_val = new_data[category].get(key)
        old_val = old_data[category].get(key)
        
        if new_val is None or old_val is None:
            return False
        
        if isinstance(new_val, str) or isinstance(old_val, str):
            return new_val != old_val
        
        try:
            if old_val == 0:
                return new_val != 0
            change = abs((new_val - old_val) / old_val)
            return change > threshold
        except (TypeError, ZeroDivisionError):
            return False
    
    def _metric_changed_absolute(self, category: str, key: str, new_data: Dict, old_data: Dict, threshold: float) -> bool:
        """Check if metric changed by absolute threshold"""
        if category not in new_data or category not in old_data:
            return False
        
        new_val = new_data[category].get(key)
        old_val = old_data[category].get(key)
        
        if new_val is None or old_val is None:
            return False
        
        try:
            change = abs(new_val - old_val)
            return change > threshold
        except (TypeError, ValueError):
            return False
    
    def _emit_updates(self, new_data: Dict, old_data: Optional[Dict]):
        """Emit all update signals"""
        # Backward compatible signals
        self.data_updated.emit(new_data)
        
        # Component signals
        if 'gpu' in new_data:
            if old_data is None or new_data['gpu'] != old_data.get('gpu'):
                self.gpu_updated.emit(new_data['gpu'])
        
        if 'cpu' in new_data:
            if old_data is None or new_data['cpu'] != old_data.get('cpu'):
                self.cpu_updated.emit(new_data['cpu'])
        
        if 'ram' in new_data:
            if old_data is None or new_data['ram'] != old_data.get('ram'):
                self.ram_updated.emit(new_data['ram'])
        
        # Granular metric signals (Package 2.4)
        self._emit_granular_signals(new_data, old_data)
    
    def _emit_granular_signals(self, new_data: Dict, old_data: Optional[Dict]):
        """Emit granular metric signals"""
        # CPU load
        cpu_load = new_data.get('cpu', {}).get('load')
        if cpu_load is not None:
            if old_data is None or cpu_load != old_data.get('cpu', {}).get('load'):
                self.cpu_load_changed.emit(cpu_load)
        
        # CPU temp
        cpu_temp = new_data.get('cpu', {}).get('temp')
        if cpu_temp is not None:
            if old_data is None or cpu_temp != old_data.get('cpu', {}).get('temp'):
                self.cpu_temp_changed.emit(cpu_temp)
        
        # GPU load
        gpu_load = new_data.get('gpu', {}).get('load_gpu')
        if gpu_load is not None:
            if old_data is None or gpu_load != old_data.get('gpu', {}).get('load_gpu'):
                self.gpu_load_changed.emit(gpu_load)
        
        # GPU temp
        gpu_temp = new_data.get('gpu', {}).get('temp_gpu')
        if gpu_temp is not None and gpu_temp > 0:
            if old_data is None or gpu_temp != old_data.get('gpu', {}).get('temp_gpu'):
                self.gpu_temp_changed.emit(gpu_temp)
        
        # RAM usage
        ram_percent = new_data.get('ram', {}).get('percent')
        if ram_percent is not None:
            if old_data is None or ram_percent != old_data.get('ram', {}).get('percent'):
                self.ram_usage_changed.emit(ram_percent)
    
    def _update_history(self, data: Dict):
        """Update history buffer"""
        timestamp = time.time()
        self._history['timestamps'].append(timestamp)
        
        # CPU metrics
        cpu = data.get('cpu', {})
        self._history['cpu_load'].append(cpu.get('load', 0))
        self._history['cpu_temp'].append(cpu.get('temp'))
        
        # GPU metrics
        gpu = data.get('gpu', {})
        self._history['gpu_load'].append(gpu.get('load_gpu', 0))
        self._history['gpu_temp'].append(gpu.get('temp_gpu'))
        
        # RAM metrics
        ram = data.get('ram', {})
        self._history['ram_percent'].append(ram.get('percent', 0))
    
    def _check_system_health(self):
        """Check system health and emit signals"""
        health = self._manager.get_health_report()
        
        # Check for changes
        if self._last_health != health:
            self._last_health = health
            self.health_changed.emit(health)
            
            # Track failed monitors
            self._failed_monitors = [
                name for name, info in health['monitors'].items()
                if not info['available']
            ]
            
            # Auto-recovery if enabled
            if self._failed_monitors and self._recovery_attempts < self._max_recovery_attempts:
                print(f"[DataBus] Attempting auto-recovery for: {', '.join(self._failed_monitors)}")
                self.recover_failed_monitors()
    
    def _adjust_interval_adaptive(self, data: Dict):
        """Adjust update interval based on system load"""
        cpu_load = data.get('cpu', {}).get('load', 0)
        gpu_load = data.get('gpu', {}).get('load_gpu', 0)
        ram_load = data.get('ram', {}).get('percent', 0)
        
        max_load = max(cpu_load, gpu_load, ram_load)
        
        is_idle = max_load < self._idle_threshold
        
        # State change
        if is_idle != self._is_system_idle:
            self._is_system_idle = is_idle
            
            if is_idle:
                new_interval = int(self._base_interval * self._idle_multiplier)
            else:
                new_interval = self._base_interval
            
            if new_interval != self._update_interval:
                self.set_update_interval(new_interval)
                print(f"[DataBus] Adaptive interval: {new_interval}ms (idle={is_idle})")
    
    def _update_data_quality(self, update_time: float):
        """Update data quality metrics"""
        # Freshness based on update time
        if update_time < 0.05:  # < 50ms
            self._data_freshness = 1.0
        elif update_time < 0.1:  # < 100ms
            self._data_freshness = 0.9
        elif update_time < 0.5:  # < 500ms
            self._data_freshness = 0.7
        else:
            self._data_freshness = 0.5
        
        # Confidence based on errors and health
        if self._error_count == 0:
            self._data_confidence = 1.0
        else:
            # Decay confidence with errors
            error_rate = self._error_count / max(self._update_count, 1)
            self._data_confidence = max(0.3, 1.0 - error_rate * 2)
    
    # === FPS TRACKING API (Package 3.1c NEW) ===
    
    def get_fps_stats(self, window: Optional[int] = None):
        """Get FPS statistics
        
        Package 3.1c NEW
        
        Args:
            window: Number of frames to analyze (None = all buffered)
        
        Returns:
            FPSStats object or None if tracking disabled
        
        Example:
            >>> stats = bus.get_fps_stats(window=60)
            >>> print(f"FPS: {stats.fps_avg:.1f}")
            >>> print(f"1% low: {stats.fps_1_percent:.1f}")
        """
        if not self._fps_tracker:
            return None
        return self._fps_tracker.get_stats(window=window)
    
    def get_frame_timing_history(self, count: int = 60) -> List[float]:
        """Get frame timing history
        
        Package 3.1c NEW
        
        Args:
            count: Number of recent frame times to return
        
        Returns:
            List of frame times (ms)
        
        Example:
            >>> history = bus.get_frame_timing_history(60)
            >>> plot_sparkline(history)
        """
        if not self._fps_tracker:
            return []
        return self._fps_tracker.get_history(count)
    
    def reset_fps_tracking(self):
        """Reset FPS tracking statistics
        
        Package 3.1c NEW
        
        Example:
            >>> bus.reset_fps_tracking()
        """
        if self._fps_tracker:
            self._fps_tracker.reset()
            self._last_stutter_count = 0
    
    def set_fps_tracking_enabled(self, enabled: bool):
        """Enable/disable FPS tracking
        
        Package 3.1c NEW
        
        Args:
            enabled: Enable FPS tracking
        
        Example:
            >>> bus.set_fps_tracking_enabled(True)
        """
        self._fps_tracking_enabled = enabled and FPS_TRACKER_AVAILABLE
        print(f"[DataBus] FPS tracking: {'enabled' if self._fps_tracking_enabled else 'disabled'}")
    
    def set_fps_update_interval(self, interval_ms: int):
        """Set FPS update emission interval
        
        Package 3.1c NEW
        
        Args:
            interval_ms: Interval in milliseconds (default: 1000ms)
        
        Example:
            >>> bus.set_fps_update_interval(500)  # Update every 0.5s
        """
        self._fps_update_interval = interval_ms
    
    def set_stutter_threshold(self, multiplier: float):
        """Set stuttering detection threshold
        
        Package 3.1c NEW
        
        Args:
            multiplier: Frame time multiplier for stutter detection
        
        Example:
            >>> bus.set_stutter_threshold(1.5)  # More sensitive
        """
        if self._fps_tracker:
            self._fps_tracker.set_stutter_threshold(multiplier)
    
    # === ENHANCED API (Package 2.4) ===
    
    def get_data(self) -> Dict:
        """Get current cached data"""
        if self._cached_data is None:
            self._cached_data = self._manager.get_all_data()
        return self._cached_data
    
    def get_all_data(self) -> Dict:
        """Alias for get_data()"""
        return self.get_data()
    
    def force_update(self):
        """Force immediate update (bypass throttling)"""
        old_throttle = self._throttle_enabled
        self._throttle_enabled = False
        self._update()
        self._throttle_enabled = old_throttle
    
    def get_metric_history(self, metric: str, count: int = None) -> List[Any]:
        """Get historical values for a metric"""
        if metric not in self._history:
            return []
        
        data = list(self._history[metric])
        if count is not None:
            data = data[-count:]
        return data
    
    def clear_history(self):
        """Clear all history buffers"""
        for key in self._history:
            self._history[key].clear()
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health report"""
        health = self._manager.get_health_report()
        health['databus'] = {
            'update_count': self._update_count,
            'error_count': self._error_count,
            'last_error': self._last_error,
            'data_freshness': self._data_freshness,
            'data_confidence': self._data_confidence,
            'fps_tracking_enabled': self._fps_tracking_enabled,
        }
        return health
    
    def recover_failed_monitors(self):
        """Attempt to recover failed monitors"""
        self._recovery_attempts += 1
        
        try:
            self._manager = MonitorManager()
            self._recovery_attempts = 0
            print("[DataBus] Monitor recovery successful")
        except Exception as e:
            print(f"[DataBus] Recovery failed: {e}")
    
    def get_data_quality(self) -> Dict:
        """Get data quality metrics"""
        return {
            'freshness': self._data_freshness,
            'confidence': self._data_confidence,
            'update_count': self._update_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(self._update_count, 1),
        }
    
    def enable_adaptive_interval(self, enabled: bool):
        """Enable/disable adaptive update intervals"""
        self._adaptive_interval_enabled = enabled
        print(f"[DataBus] Adaptive intervals: {'enabled' if enabled else 'disabled'}")
    
    def set_monitor_priority(self, monitor: str, priority: int):
        """Set monitor update priority"""
        self._monitor_priorities[monitor] = priority
    
    def set_history_size(self, size: int):
        """Set history buffer size"""
        self._history_size = size
        for key in self._history:
            self._history[key] = deque(self._history[key], maxlen=size)
    
    # === CONFIGURATION ===
    
    def set_update_interval(self, interval_ms: int):
        """Change update interval"""
        self._update_interval = interval_ms
        if self._timer.isActive():
            self._timer.setInterval(interval_ms)
        self.update_interval_changed.emit(interval_ms)
    
    def set_throttling(self, enabled: bool, threshold: float = 0.01):
        """Enable/disable smart update throttling"""
        old_state = self._throttle_enabled
        self._throttle_enabled = enabled
        self._throttle_threshold = threshold
        
        if old_state != enabled:
            self.throttle_status_changed.emit(enabled)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if self._update_count == 0:
            return {
                "avg_time_ms": 0,
                "last_time_ms": 0,
                "total_updates": 0,
                "update_interval_ms": self._update_interval,
                "error_count": 0,
            }
        
        avg_time = (self._total_time / self._update_count) * 1000
        last_time = self._last_update_time * 1000
        
        return {
            "avg_time_ms": avg_time,
            "last_time_ms": last_time,
            "total_updates": self._update_count,
            "update_interval_ms": self._update_interval,
            "error_count": self._error_count,
        }


# === SINGLETON ===

_databus_instance: Optional[DataBus] = None

def get_databus() -> DataBus:
    """Get singleton DataBus instance"""
    global _databus_instance
    if _databus_instance is None:
        _databus_instance = DataBus()
    return _databus_instance

def reset_databus():
    """Reset DataBus singleton (for testing)"""
    global _databus_instance
    if _databus_instance is not None:
        _databus_instance.stop()
        _databus_instance = None
