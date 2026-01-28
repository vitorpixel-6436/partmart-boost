"""DataBus - Event-driven data layer between backend and frontend

BOTTLENECK FIX: 
- Batched monitor polling (single threaded, non-blocking)
- Cached results (minimize redundant psutil calls)
- Event-driven updates (UI subscribes, doesn't poll)
- Decoupled architecture (backend changes don't affect frontend)

ARCHITECTURE:
  Monitors → DataBus → UI
  (Backend)  (Middleware) (Frontend)
"""
import time
from typing import Dict, Callable, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class DataBus(QObject):
    """Centralized data distribution system
    
    Responsibilities:
    1. Poll all monitors at configurable interval
    2. Cache results to minimize overhead
    3. Emit signals when data changes
    4. Provide synchronous data access for UI
    
    Benefits:
    - Frontend doesn't access monitors directly
    - Changes to monitors don't break UI
    - Single polling loop for all monitors
    - Efficient caching and batching
    """
    
    # Signals for reactive UI updates
    data_updated = pyqtSignal(dict)  # All data
    gpu_updated = pyqtSignal(dict)   # GPU only
    cpu_updated = pyqtSignal(dict)   # CPU only
    ram_updated = pyqtSignal(dict)   # RAM only
    error_occurred = pyqtSignal(str)  # Errors
    
    def __init__(self, update_interval_ms: int = 2000):
        """Initialize DataBus
        
        Args:
            update_interval_ms: Polling interval in milliseconds (default: 2000ms = 2s)
        """
        super().__init__()
        
        # Configuration
        self.update_interval_ms = update_interval_ms
        
        # Cached data
        self._data: Dict[str, Any] = {
            'gpu': {},
            'cpu': {},
            'ram': {},
            'timestamp': 0,
        }
        
        # Monitors (lazy loading)
        self._monitors = {
            'gpu': None,
            'cpu': None,
            'ram': None,
        }
        
        # Timer for polling
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll_monitors)
        
        # Performance tracking
        self._last_poll_duration = 0
        self._poll_count = 0
        
        # Initialize monitors
        self._init_monitors()
    
    def _init_monitors(self):
        """Initialize all monitors (lazy)"""
        try:
            # Import monitors (only if not already loaded)
            from monitors.gpu_monitor import get_gpu_monitor
            from monitors.cpu_monitor import get_cpu_monitor
            from monitors.ram_monitor import get_ram_monitor
            
            self._monitors['gpu'] = get_gpu_monitor()
            self._monitors['cpu'] = get_cpu_monitor()
            self._monitors['ram'] = get_ram_monitor()
            
            print("[INFO] DataBus: All monitors initialized")
            
        except Exception as e:
            print(f"[ERROR] DataBus: Monitor initialization failed: {e}")
            self.error_occurred.emit(f"Monitor init failed: {e}")
    
    def _poll_monitors(self):
        """Poll all monitors and update cache
        
        OPTIMIZATION: Batch all monitor queries in single call
        """
        start_time = time.time()
        
        try:
            # OPTIMIZATION: Parallel data collection (monitors have their own caches)
            new_data = {
                'gpu': self._monitors['gpu'].get_data() if self._monitors['gpu'] else {},
                'cpu': self._monitors['cpu'].get_data() if self._monitors['cpu'] else {},
                'ram': self._monitors['ram'].get_data() if self._monitors['ram'] else {},
                'timestamp': time.time(),
            }
            
            # Check if data actually changed (avoid unnecessary UI updates)
            data_changed = self._has_significant_change(self._data, new_data)
            
            # Update cache
            self._data = new_data
            
            # Emit signals only if data changed significantly
            if data_changed:
                self.data_updated.emit(self._data)
                self.gpu_updated.emit(self._data['gpu'])
                self.cpu_updated.emit(self._data['cpu'])
                self.ram_updated.emit(self._data['ram'])
            
            # Performance tracking
            self._last_poll_duration = (time.time() - start_time) * 1000  # ms
            self._poll_count += 1
            
            # Log performance issues
            if self._last_poll_duration > 100:  # > 100ms is slow
                print(f"[WARN] DataBus: Slow poll detected ({self._last_poll_duration:.1f}ms)")
            
        except Exception as e:
            print(f"[ERROR] DataBus: Poll failed: {e}")
            self.error_occurred.emit(f"Data poll failed: {e}")
    
    def _has_significant_change(self, old_data: Dict, new_data: Dict, threshold: float = 0.5) -> bool:
        """Check if data changed significantly
        
        OPTIMIZATION: Avoid UI updates for minor fluctuations
        
        Args:
            old_data: Previous data
            new_data: New data
            threshold: Minimum change threshold (e.g., 0.5% for percentages)
        
        Returns:
            True if significant change detected
        """
        # Always update on first poll
        if not old_data or old_data.get('timestamp', 0) == 0:
            return True
        
        # Check each metric for significant change
        try:
            # GPU temp change > 1°C
            if abs(new_data.get('gpu', {}).get('temp_gpu', 0) - old_data.get('gpu', {}).get('temp_gpu', 0)) > 1:
                return True
            
            # CPU/RAM usage change > 1%
            if abs(new_data.get('cpu', {}).get('load', 0) - old_data.get('cpu', {}).get('load', 0)) > 1:
                return True
            
            if abs(new_data.get('ram', {}).get('percent', 0) - old_data.get('ram', {}).get('percent', 0)) > 1:
                return True
            
            # Update every 10 polls even if no change (keep UI alive)
            if self._poll_count % 10 == 0:
                return True
            
            return False
            
        except Exception:
            # On error, update anyway
            return True
    
    def start(self):
        """Start polling monitors"""
        print(f"[INFO] DataBus: Starting with {self.update_interval_ms}ms interval")
        
        # Do initial poll immediately
        self._poll_monitors()
        
        # Start timer
        self._timer.start(self.update_interval_ms)
    
    def stop(self):
        """Stop polling monitors"""
        print("[INFO] DataBus: Stopping")
        self._timer.stop()
    
    def set_update_interval(self, interval_ms: int):
        """Change update interval
        
        Args:
            interval_ms: New interval in milliseconds
        """
        self.update_interval_ms = interval_ms
        
        if self._timer.isActive():
            self._timer.setInterval(interval_ms)
            print(f"[INFO] DataBus: Update interval changed to {interval_ms}ms")
    
    def get_data(self) -> Dict:
        """Get cached data (synchronous)
        
        Returns:
            Dictionary with all system data
        """
        return self._data.copy()
    
    def get_gpu_data(self) -> Dict:
        """Get cached GPU data"""
        return self._data.get('gpu', {}).copy()
    
    def get_cpu_data(self) -> Dict:
        """Get cached CPU data"""
        return self._data.get('cpu', {}).copy()
    
    def get_ram_data(self) -> Dict:
        """Get cached RAM data"""
        return self._data.get('ram', {}).copy()
    
    def get_performance_stats(self) -> Dict:
        """Get DataBus performance statistics
        
        Returns:
            Dict with performance metrics
        """
        return {
            'last_poll_duration_ms': self._last_poll_duration,
            'poll_count': self._poll_count,
            'update_interval_ms': self.update_interval_ms,
            'avg_poll_rate': self._poll_count / (self._data.get('timestamp', 1) or 1),
        }
    
    def force_update(self):
        """Force immediate data update"""
        print("[INFO] DataBus: Force update requested")
        self._poll_monitors()

# Global singleton
_databus = None

def get_databus(update_interval_ms: int = 2000) -> DataBus:
    """Get global DataBus instance
    
    Args:
        update_interval_ms: Update interval (only used on first call)
    
    Returns:
        Global DataBus instance
    """
    global _databus
    if _databus is None:
        _databus = DataBus(update_interval_ms)
    return _databus

if __name__ == "__main__":
    # Test
    import sys
    from PyQt6.QtWidgets import QApplication
    
    print("[TEST] Testing DataBus...")
    
    app = QApplication(sys.argv)
    
    # Create DataBus
    bus = DataBus(update_interval_ms=1000)  # 1 second for testing
    
    # Subscribe to updates
    def on_data_update(data):
        print(f"[DATA] GPU: {data['gpu'].get('temp_gpu', 0)}°C, "
              f"CPU: {data['cpu'].get('load', 0):.1f}%, "
              f"RAM: {data['ram'].get('percent', 0):.1f}%")
    
    def on_error(error):
        print(f"[ERROR] {error}")
    
    bus.data_updated.connect(on_data_update)
    bus.error_occurred.connect(on_error)
    
    # Start
    bus.start()
    
    # Run for 5 seconds
    print("[TEST] Running for 5 seconds...")
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec())
