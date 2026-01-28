"""DataBus - Event-driven middleware between backend and frontend

Architecture:
    FRONTEND (UI Widgets) 
        ↓ subscribes to signals
    MIDDLEWARE (DataBus) 
        ↓ polls monitors
    BACKEND (Monitors)

Benefits:
- Frontend never calls hardware directly
- Backend changes don't break UI
- Event-driven reactivity
- Performance caching
- Easy to add new monitors

Version: 0.3.5d - Package 2b
"""
import time
from typing import Dict, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from monitors.manager import MonitorManager

class DataBus(QObject):
    """Central event bus for system data
    
    Emits signals when data changes:
    - data_updated: All data updated
    - gpu_updated: GPU data changed
    - cpu_updated: CPU data changed
    - ram_updated: RAM data changed
    - error_occurred: Error happened
    
    v0.3.5d Package 2b improvements:
    - Health status tracking
    - Better error recovery
    - Monitor availability logging
    """
    
    # Signals
    data_updated = pyqtSignal(dict)  # Full data
    gpu_updated = pyqtSignal(dict)   # GPU only
    cpu_updated = pyqtSignal(dict)   # CPU only
    ram_updated = pyqtSignal(dict)   # RAM only
    error_occurred = pyqtSignal(str) # Errors
    
    def __init__(self, update_interval: int = 2000):
        """Initialize DataBus
        
        Args:
            update_interval: Update interval in milliseconds (default: 2000ms = 2s)
        """
        super().__init__()
        
        # Backend
        self._manager = MonitorManager()
        
        # Cache
        self._cached_data: Optional[Dict] = None
        self._last_update_time = 0
        
        # Update timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._update_interval = update_interval
        
        # Performance tracking
        self._update_count = 0
        self._total_time = 0.0
        
        # Throttling (only emit if changed significantly)
        self._throttle_enabled = True
        self._throttle_threshold = 0.01  # 1% change
        
        # v0.3.5d Package 2b: Health tracking
        self._health_status = {
            'gpu': {'available': False, 'name': 'Unknown'},
            'cpu': {'available': False, 'name': 'Unknown'},
            'ram': {'available': False, 'name': 'Unknown'},
        }
        self._degraded_mode = False
    
    def start(self):
        """Start automatic updates"""
        print(f"[DataBus] Starting updates every {self._update_interval}ms")
        # First update (synchronous)
        self._update()
        # Start timer for subsequent updates
        self._timer.start(self._update_interval)
    
    def stop(self):
        """Stop automatic updates"""
        print("[DataBus] Stopping updates")
        self._timer.stop()
    
    def set_update_interval(self, interval_ms: int):
        """Change update interval
        
        Args:
            interval_ms: New interval in milliseconds
        """
        self._update_interval = interval_ms
        if self._timer.isActive():
            self._timer.setInterval(interval_ms)
            print(f"[DataBus] Update interval changed to {interval_ms}ms")
    
    def set_throttling(self, enabled: bool, threshold: float = 0.01):
        """Enable/disable smart update throttling
        
        Args:
            enabled: Enable throttling
            threshold: Minimum change to emit update (default: 1%)
        """
        self._throttle_enabled = enabled
        self._throttle_threshold = threshold
    
    def _update(self):
        """Internal update method (called by timer)
        
        v0.3.5d Package 2b: Better error handling and health tracking
        """
        start_time = time.time()
        
        try:
            # Get data from backend
            new_data = self._manager.get_all_data()
            
            # v0.3.5d Package 2b: Update health status
            self._update_health_status(new_data)
            
            # Check if data changed significantly
            if self._should_emit(new_data):
                # Update cache
                old_data = self._cached_data
                self._cached_data = new_data
                
                # Emit signals
                self._emit_updates(new_data, old_data)
            
            # Track performance
            elapsed = time.time() - start_time
            self._last_update_time = elapsed
            self._update_count += 1
            self._total_time += elapsed
        
        except Exception as e:
            print(f"[DataBus] Update error: {e}")
            self.error_occurred.emit(str(e))
            
            # v0.3.5d: Try to continue with cached data
            if self._cached_data is not None:
                print("[DataBus] Using cached data after error")
            else:
                print("[DataBus] No cached data available")
    
    def _update_health_status(self, data: Dict):
        """Update health status tracking
        
        Args:
            data: Current monitor data
        
        v0.3.5d Package 2b: New method
        """
        any_degraded = False
        
        for monitor_type in ['gpu', 'cpu', 'ram']:
            if monitor_type in data:
                health = data[monitor_type].get('_monitor_health', {})
                self._health_status[monitor_type] = {
                    'available': health.get('available', False),
                    'name': health.get('name', 'Unknown'),
                    'error': health.get('error'),
                }
                
                if not health.get('available', False):
                    any_degraded = True
        
        # Log degraded mode changes
        if any_degraded and not self._degraded_mode:
            print("[DataBus] ⚠️  Entering degraded mode (some monitors unavailable)")
            self._log_health_status()
            self._degraded_mode = True
        elif not any_degraded and self._degraded_mode:
            print("[DataBus] ✅ Exiting degraded mode (all monitors available)")
            self._degraded_mode = False
    
    def _log_health_status(self):
        """Log current health status
        
        v0.3.5d Package 2b: New method
        """
        print("[DataBus] Health Status:")
        for monitor_type, status in self._health_status.items():
            icon = '✅' if status['available'] else '❌'
            print(f"  {icon} {monitor_type}: {status['name']}")
            if status.get('error'):
                print(f"      Error: {status['error']}")
    
    def _should_emit(self, new_data: Dict) -> bool:
        """Check if data changed enough to emit
        
        Args:
            new_data: New data to check
        
        Returns:
            True if should emit update
        """
        # First update always emits
        if self._cached_data is None:
            return True
        
        # Throttling disabled - always emit
        if not self._throttle_enabled:
            return True
        
        # Check if any value changed significantly
        old_data = self._cached_data
        
        for key in ['gpu', 'cpu', 'ram']:
            if key not in new_data or key not in old_data:
                continue
            
            new_values = new_data[key]
            old_values = old_data[key]
            
            for metric, new_val in new_values.items():
                # v0.3.5d: Skip health metadata
                if metric == '_monitor_health':
                    continue
                
                if metric not in old_values:
                    continue
                
                old_val = old_values[metric]
                
                # Skip None/string values
                if new_val is None or old_val is None:
                    continue
                if isinstance(new_val, str) or isinstance(old_val, str):
                    continue
                
                # Check percentage change
                try:
                    if old_val == 0:
                        # Avoid division by zero
                        if new_val != 0:
                            return True
                    else:
                        change = abs((new_val - old_val) / old_val)
                        if change > self._throttle_threshold:
                            return True
                except (TypeError, ZeroDivisionError):
                    pass
        
        # No significant change
        return False
    
    def _emit_updates(self, new_data: Dict, old_data: Optional[Dict]):
        """Emit update signals
        
        Args:
            new_data: New data
            old_data: Previous data (for change detection)
        """
        # Full update
        self.data_updated.emit(new_data)
        
        # Individual updates (only if changed)
        if 'gpu' in new_data:
            if old_data is None or new_data['gpu'] != old_data.get('gpu'):
                self.gpu_updated.emit(new_data['gpu'])
        
        if 'cpu' in new_data:
            if old_data is None or new_data['cpu'] != old_data.get('cpu'):
                self.cpu_updated.emit(new_data['cpu'])
        
        if 'ram' in new_data:
            if old_data is None or new_data['ram'] != old_data.get('ram'):
                self.ram_updated.emit(new_data['ram'])
    
    def get_data(self) -> Dict:
        """Get current cached data (synchronous)
        
        Returns:
            Current system data (may be slightly outdated)
        """
        if self._cached_data is None:
            # First call - get data synchronously
            self._cached_data = self._manager.get_all_data()
            self._update_health_status(self._cached_data)  # v0.3.5d
        
        return self._cached_data
    
    def force_update(self):
        """Force immediate update (bypass throttling)"""
        old_throttle = self._throttle_enabled
        self._throttle_enabled = False
        self._update()
        self._throttle_enabled = old_throttle
    
    def get_health_status(self) -> Dict:
        """Get current health status of all monitors
        
        Returns:
            Health status dict
        
        v0.3.5d Package 2b: New method
        """
        return {
            'monitors': self._health_status.copy(),
            'degraded_mode': self._degraded_mode,
        }
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics
        
        Returns:
            Dictionary with performance metrics
        """
        if self._update_count == 0:
            return {
                "avg_time_ms": 0,
                "last_time_ms": 0,
                "total_updates": 0,
                "update_interval_ms": self._update_interval,
            }
        
        avg_time = (self._total_time / self._update_count) * 1000
        last_time = self._last_update_time * 1000
        
        return {
            "avg_time_ms": avg_time,
            "last_time_ms": last_time,
            "total_updates": self._update_count,
            "update_interval_ms": self._update_interval,
        }

# Singleton instance
_databus_instance: Optional[DataBus] = None

def get_databus() -> DataBus:
    """Get singleton DataBus instance
    
    Returns:
        DataBus instance
    """
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

if __name__ == "__main__":
    # Test DataBus
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    bus = get_databus()
    
    # Connect signals
    def on_data_update(data):
        print("\n[DATA UPDATE]")
        for key, values in data.items():
            print(f"  {key.upper()}:")
            for metric, value in values.items():
                if metric != '_monitor_health' and value is not None:
                    print(f"    {metric}: {value}")
    
    def on_gpu_update(data):
        temp = data.get('temp_gpu', 0)
        load = data.get('load_gpu', 0)
        mem = data.get('memory_total', 0)
        print(f"[GPU] Temp: {temp}°C, Load: {load}%, VRAM: {mem}MB")
    
    def on_error(msg):
        print(f"[ERROR] {msg}")
    
    bus.data_updated.connect(on_data_update)
    bus.gpu_updated.connect(on_gpu_update)
    bus.error_occurred.connect(on_error)
    
    # Start updates
    bus.start()
    
    # Show health status after 2 seconds
    def show_health():
        health = bus.get_health_status()
        print("\n[HEALTH STATUS]")
        print(f"  Degraded mode: {health['degraded_mode']}")
        for monitor, status in health['monitors'].items():
            icon = '✅' if status['available'] else '❌'
            print(f"  {icon} {monitor}: {status['name']}")
    
    QTimer.singleShot(2000, show_health)
    
    # Run for 10 seconds
    QTimer.singleShot(10000, app.quit)
    
    print("[TEST] Running DataBus v0.3.5d Package 2b for 10 seconds...")
    sys.exit(app.exec())
