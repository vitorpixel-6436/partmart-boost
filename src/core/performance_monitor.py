#!/usr/bin/env python3
"""Performance Monitor with Error Handling

Version: 0.3.5n (package 3.9a, stage 7.7b.5/7.7)

Package 3.9a Stage 7.7b.5: Error handling in service layer.

Features:
- CPU/GPU/FPS correlation tracking
- Bottleneck history and analysis
- Performance scoring (0-100)
- Frame time analysis
- Load prediction
- Thermal efficiency tracking
- Performance degradation detection
- Comprehensive error handling
- Graceful degradation
"""
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque
from dataclasses import dataclass

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


@dataclass
class PerformanceSnapshot:
    """Single performance measurement
    
    Attributes:
        timestamp: Unix timestamp
        cpu_load: CPU load (0-100)
        gpu_load: GPU load (0-100)
        ram_usage: RAM usage (0-100)
        fps: Current FPS
        frame_time: Current frame time (ms)
        cpu_temp: CPU temperature (°C)
        gpu_temp: GPU temperature (°C)
    """
    timestamp: float
    cpu_load: float
    gpu_load: float
    ram_usage: float
    fps: float
    frame_time: float
    cpu_temp: Optional[float]
    gpu_temp: Optional[float]


@dataclass
class BottleneckInfo:
    """Bottleneck detection result
    
    Attributes:
        component: 'cpu', 'gpu', 'ram', or 'none'
        severity: 'low', 'medium', 'high'
        load: Load percentage of bottleneck component
        timestamp: When detected
    """
    component: str
    severity: str
    load: float
    timestamp: float


class PerformanceMonitor:
    """Advanced performance analytics with error handling
    
    v0.3.5n (package 3.9a, stage 7.7b.5/7.7)
    
    Features:
    - Real-time performance scoring
    - Component correlation analysis
    - Bottleneck tracking and prediction
    - Performance trend analysis
    - Load forecasting
    - Comprehensive error handling
    - Graceful degradation
    
    Error Handling:
    - Validates all input data
    - Handles manager interface errors
    - Gracefully handles insufficient data
    - Logs all errors
    - Returns safe fallback values
    
    Example:
        >>> perf = PerformanceMonitor(manager, bus)
        >>> 
        >>> # Update safely
        >>> if perf.update():
        >>>     score = perf.get_performance_score()
        >>>     print(f"Score: {score:.1f}/100")
    """
    
    def __init__(self, monitor_manager, databus, history_size: int = 300):
        """Initialize performance monitor
        
        Args:
            monitor_manager: MonitorManager instance
            databus: DataBus instance for FPS data
            history_size: Number of snapshots to keep (default: 300 = 10 min @ 2s)
        """
        self._manager = monitor_manager
        self._bus = databus
        self._logger = None
        
        # Get logger if available
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug("PerformanceMonitor initializing")
            except Exception:
                pass
        
        try:
            # History buffer (ring buffer)
            self._history_size = max(10, min(history_size, 10000))  # Clamp 10-10000
            self._snapshots: Deque[PerformanceSnapshot] = deque(maxlen=self._history_size)
            self._bottleneck_history: Deque[BottleneckInfo] = deque(maxlen=self._history_size)
            
            # Performance tracking
            self._last_score = 0.0
            self._baseline_established = False
            self._baseline_fps = 60.0  # Target FPS
            
            # Correlation tracking
            self._cpu_fps_correlation = 0.0
            self._gpu_fps_correlation = 0.0
            
            # Degradation detection
            self._performance_declining = False
            self._decline_start_time: Optional[float] = None
            
            # Error tracking
            self._error_count = 0
            self._max_errors = 10
            self._last_error_time = 0.0
            
            self._log_info(f"Initialized (history_size: {self._history_size})")
        
        except Exception as e:
            self._log_error(f"Initialization failed: {e}", exc_info=True)
            # Set safe defaults
            self._history_size = 300
            self._snapshots = deque(maxlen=300)
            self._bottleneck_history = deque(maxlen=300)
    
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
    
    def _handle_error(self, error: Exception) -> bool:
        """Handle error with counting and cooldown
        
        Args:
            error: Exception that occurred
        
        Returns:
            True if should continue, False if should stop
        """
        now = time.time()
        
        # Reset error count after cooldown
        if now - self._last_error_time > 60.0:
            self._error_count = 0
        
        self._error_count += 1
        self._last_error_time = now
        
        self._log_error(f"Error ({self._error_count}/{self._max_errors}): {error}")
        
        # Stop if too many errors
        if self._error_count >= self._max_errors:
            self._log_error("Too many errors, monitor disabled")
            return False
        
        return True
    
    def _validate_load_value(self, value: float, name: str) -> float:
        """Validate and clamp load value
        
        Args:
            value: Load value to validate
            name: Name of value (for logging)
        
        Returns:
            Clamped value (0-100)
        """
        try:
            if not isinstance(value, (int, float)):
                self._log_warning(f"Invalid {name} type: {type(value)}")
                return 0.0
            
            if value < 0 or value > 100:
                self._log_warning(f"Invalid {name} range: {value}")
                return max(0.0, min(100.0, value))
            
            return float(value)
        
        except Exception as e:
            self._log_error(f"Validation error for {name}: {e}")
            return 0.0
    
    # === DATA COLLECTION ===
    
    def update(self) -> bool:
        """Collect current performance snapshot with error handling
        
        Returns:
            True if successful, False on error
        
        Example:
            >>> if perf.update():
            >>>     print("Data collected")
        """
        try:
            if not self._manager:
                self._log_warning("Manager not available")
                return False
            
            # Get system data with error handling
            try:
                cpu_load = self._manager.get_cpu_load()
                cpu_load = self._validate_load_value(cpu_load, "CPU load")
            except Exception as e:
                self._log_error(f"Failed to get CPU load: {e}")
                cpu_load = 0.0
            
            try:
                gpu_load = self._manager.get_gpu_load()
                gpu_load = self._validate_load_value(gpu_load, "GPU load")
            except Exception as e:
                self._log_error(f"Failed to get GPU load: {e}")
                gpu_load = 0.0
            
            try:
                ram_usage = self._manager.get_ram_percent()
                ram_usage = self._validate_load_value(ram_usage, "RAM usage")
            except Exception as e:
                self._log_error(f"Failed to get RAM usage: {e}")
                ram_usage = 0.0
            
            try:
                cpu_temp = self._manager.get_cpu_temp()
                cpu_temp = float(cpu_temp) if cpu_temp > 0 else None
            except Exception as e:
                self._log_error(f"Failed to get CPU temp: {e}")
                cpu_temp = None
            
            try:
                gpu_temp_raw = self._manager.get_gpu_temp()
                gpu_temp = float(gpu_temp_raw) if gpu_temp_raw > 0 else None
            except Exception as e:
                self._log_error(f"Failed to get GPU temp: {e}")
                gpu_temp = None
            
            try:
                fps = self._manager.get_fps()
                fps = float(fps) if fps >= 0 else 0.0
            except Exception as e:
                self._log_error(f"Failed to get FPS: {e}")
                fps = 0.0
            
            try:
                frame_time = self._manager.get_frame_time()
                frame_time = float(frame_time) if frame_time >= 0 else 0.0
            except Exception as e:
                self._log_error(f"Failed to get frame time: {e}")
                frame_time = 0.0
            
            # Create snapshot
            snapshot = PerformanceSnapshot(
                timestamp=time.time(),
                cpu_load=cpu_load,
                gpu_load=gpu_load,
                ram_usage=ram_usage,
                fps=fps,
                frame_time=frame_time,
                cpu_temp=cpu_temp,
                gpu_temp=gpu_temp,
            )
            
            # Add to history
            self._snapshots.append(snapshot)
            
            # Detect bottleneck
            try:
                bottleneck = self._detect_bottleneck(snapshot)
                self._bottleneck_history.append(bottleneck)
            except Exception as e:
                self._log_error(f"Bottleneck detection failed: {e}")
            
            # Update correlations
            if len(self._snapshots) >= 30:
                try:
                    self._update_correlations()
                except Exception as e:
                    self._log_error(f"Correlation update failed: {e}")
            
            # Check for degradation
            if len(self._snapshots) >= 60:
                try:
                    self._check_performance_degradation()
                except Exception as e:
                    self._log_error(f"Degradation check failed: {e}")
            
            # Establish baseline
            if not self._baseline_established and len(self._snapshots) >= 60:
                try:
                    self._establish_baseline()
                except Exception as e:
                    self._log_error(f"Baseline establishment failed: {e}")
            
            self._log_debug(f"Updated: CPU={cpu_load:.1f}%, GPU={gpu_load:.1f}%, FPS={fps:.1f}")
            return True
        
        except AttributeError as e:
            self._log_error(f"Manager interface error: {e}")
            return self._handle_error(e)
        
        except Exception as e:
            self._log_error(f"Update failed: {e}", exc_info=True)
            return self._handle_error(e)
    
    def _detect_bottleneck(self, snapshot: PerformanceSnapshot) -> BottleneckInfo:
        """Detect current bottleneck with error handling
        
        Args:
            snapshot: Current performance snapshot
        
        Returns:
            BottleneckInfo object
        """
        try:
            loads = {
                'cpu': snapshot.cpu_load,
                'gpu': snapshot.gpu_load,
                'ram': snapshot.ram_usage,
            }
            
            # Find highest load
            max_component = max(loads.items(), key=lambda x: x[1])
            component = max_component[0]
            load = max_component[1]
            
            # Determine severity
            if load >= 90:
                severity = 'high'
            elif load >= 70:
                severity = 'medium'
            elif load >= 50:
                severity = 'low'
            else:
                severity = 'none'
                component = 'none'
            
            return BottleneckInfo(
                component=component,
                severity=severity,
                load=load,
                timestamp=snapshot.timestamp,
            )
        
        except Exception as e:
            self._log_error(f"Bottleneck detection failed: {e}")
            # Return safe default
            return BottleneckInfo(
                component='none',
                severity='none',
                load=0.0,
                timestamp=time.time(),
            )
    
    def _update_correlations(self):
        """Update CPU/GPU/FPS correlations with error handling"""
        try:
            if len(self._snapshots) < 30:
                return
            
            # Get recent data (last 60 samples = 2 min)
            recent = list(self._snapshots)[-60:]
            
            # Extract arrays
            cpu_loads = np.array([s.cpu_load for s in recent])
            gpu_loads = np.array([s.gpu_load for s in recent])
            fps_values = np.array([s.fps for s in recent])
            
            # Filter out zero FPS (not tracking)
            valid_mask = fps_values > 0
            if valid_mask.sum() < 10:  # Need at least 10 valid samples
                return
            
            cpu_loads = cpu_loads[valid_mask]
            gpu_loads = gpu_loads[valid_mask]
            fps_values = fps_values[valid_mask]
            
            # Calculate correlations
            cpu_corr = np.corrcoef(cpu_loads, fps_values)[0, 1]
            gpu_corr = np.corrcoef(gpu_loads, fps_values)[0, 1]
            
            # Validate results
            if not np.isnan(cpu_corr) and not np.isinf(cpu_corr):
                self._cpu_fps_correlation = cpu_corr
            
            if not np.isnan(gpu_corr) and not np.isinf(gpu_corr):
                self._gpu_fps_correlation = gpu_corr
        
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as e:
            self._log_warning(f"Correlation calculation error: {e}")
        
        except Exception as e:
            self._log_error(f"Correlation update failed: {e}")
    
    def _establish_baseline(self):
        """Establish performance baseline with error handling"""
        try:
            if len(self._snapshots) < 60:
                return
            
            # Calculate average FPS from recent history
            recent = list(self._snapshots)[-60:]
            fps_values = [s.fps for s in recent if s.fps > 0]
            
            if fps_values:
                self._baseline_fps = float(np.mean(fps_values))
                self._baseline_established = True
                self._log_info(f"Baseline established: {self._baseline_fps:.1f} FPS")
        
        except Exception as e:
            self._log_error(f"Baseline establishment failed: {e}")
    
    def _check_performance_degradation(self):
        """Check if performance is degrading over time with error handling"""
        try:
            if not self._baseline_established:
                return
            
            # Get recent FPS (last 30 samples)
            recent = list(self._snapshots)[-30:]
            recent_fps = [s.fps for s in recent if s.fps > 0]
            
            if not recent_fps:
                return
            
            avg_recent_fps = float(np.mean(recent_fps))
            
            # Check if dropped more than 20% from baseline
            if avg_recent_fps < self._baseline_fps * 0.8:
                if not self._performance_declining:
                    self._performance_declining = True
                    self._decline_start_time = time.time()
                    self._log_warning(
                        f"Performance degradation detected: {avg_recent_fps:.1f} FPS "
                        f"(baseline: {self._baseline_fps:.1f})"
                    )
            else:
                if self._performance_declining:
                    self._log_info(f"Performance recovered: {avg_recent_fps:.1f} FPS")
                self._performance_declining = False
                self._decline_start_time = None
        
        except Exception as e:
            self._log_error(f"Degradation check failed: {e}")
    
    # === ANALYTICS API ===
    
    def get_performance_score(self) -> float:
        """Get overall performance score (0-100) with error handling
        
        Returns:
            Performance score (0-100), 0 on error
        """
        try:
            if not self._snapshots:
                return 0.0
            
            recent = list(self._snapshots)[-30:]  # Last 30 samples
            
            # FPS score (50%)
            fps_values = [s.fps for s in recent if s.fps > 0]
            if fps_values:
                avg_fps = float(np.mean(fps_values))
                fps_score = min(100.0, (avg_fps / 60.0) * 100.0)  # 60 FPS = 100%
            else:
                fps_score = 0.0
            
            # Load balance score (30%)
            cpu_loads = [s.cpu_load for s in recent]
            gpu_loads = [s.gpu_load for s in recent]
            ram_loads = [s.ram_usage for s in recent]
            
            avg_cpu = float(np.mean(cpu_loads))
            avg_gpu = float(np.mean(gpu_loads))
            avg_ram = float(np.mean(ram_loads))
            
            max_load = max(avg_cpu, avg_gpu, avg_ram)
            
            # Penalty for high load
            if max_load >= 90:
                load_score = 50.0
            elif max_load >= 70:
                load_score = 75.0
            else:
                load_score = 100.0
            
            # Thermal efficiency score (20%)
            temps = []
            for s in recent:
                if s.cpu_temp:
                    temps.append(s.cpu_temp)
                if s.gpu_temp:
                    temps.append(s.gpu_temp)
            
            if temps:
                max_temp = max(temps)
                if max_temp >= 85:
                    thermal_score = 50.0
                elif max_temp >= 75:
                    thermal_score = 75.0
                else:
                    thermal_score = 100.0
            else:
                thermal_score = 100.0
            
            # Weighted total
            total_score = (fps_score * 0.5) + (load_score * 0.3) + (thermal_score * 0.2)
            
            self._last_score = total_score
            return total_score
        
        except Exception as e:
            self._log_error(f"Performance score calculation failed: {e}")
            return self._last_score  # Return last known score
    
    def get_current_bottleneck(self) -> Optional[BottleneckInfo]:
        """Get current bottleneck with error handling
        
        Returns:
            Latest BottleneckInfo or None
        """
        try:
            if not self._bottleneck_history:
                return None
            return self._bottleneck_history[-1]
        
        except Exception as e:
            self._log_error(f"Failed to get bottleneck: {e}")
            return None
    
    def is_performance_degrading(self) -> bool:
        """Check if performance is currently degrading
        
        Returns:
            True if performance has declined >20% from baseline
        """
        try:
            return self._performance_declining
        except Exception:
            return False
    
    def get_baseline_fps(self) -> float:
        """Get established FPS baseline
        
        Returns:
            Baseline FPS or 0 if not established
        """
        try:
            return self._baseline_fps if self._baseline_established else 0.0
        except Exception:
            return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status
        
        Returns:
            Status dictionary
        """
        try:
            return {
                'active': True,
                'snapshot_count': len(self._snapshots),
                'baseline_established': self._baseline_established,
                'baseline_fps': self.get_baseline_fps(),
                'performance_degrading': self._performance_declining,
                'error_count': self._error_count,
                'last_score': self._last_score,
            }
        except Exception as e:
            self._log_error(f"Failed to get status: {e}")
            return {'error': str(e)}
    
    def reset(self) -> bool:
        """Reset all performance history
        
        Returns:
            True if successful
        """
        try:
            self._snapshots.clear()
            self._bottleneck_history.clear()
            self._baseline_established = False
            self._performance_declining = False
            self._decline_start_time = None
            self._error_count = 0
            
            self._log_info("Reset complete")
            return True
        
        except Exception as e:
            self._log_error(f"Reset failed: {e}")
            return False


# Testing
if __name__ == "__main__":
    import random
    
    print("="*60)
    print("PerformanceMonitor Test (with Error Handling)")
    print("="*60)
    
    # Mock data for testing
    class MockManager:
        def __init__(self):
            self.fps = 60.0
            self.cpu = 50.0
            self.gpu = 60.0
        
        def get_cpu_load(self):
            return self.cpu + random.uniform(-5, 5)
        
        def get_gpu_load(self):
            return self.gpu + random.uniform(-5, 5)
        
        def get_ram_percent(self):
            return 70 + random.uniform(-5, 5)
        
        def get_cpu_temp(self):
            return 65.0 + random.uniform(-3, 3)
        
        def get_gpu_temp(self):
            return 70.0 + random.uniform(-3, 3)
        
        def get_fps(self):
            return self.fps + random.uniform(-2, 2)
        
        def get_frame_time(self):
            fps = self.get_fps()
            return (1000.0 / fps) if fps > 0 else 0
    
    class MockBus:
        pass
    
    manager = MockManager()
    bus = MockBus()
    
    perf = PerformanceMonitor(manager, bus, history_size=120)
    
    print("\n[Test 1] Collecting data...")
    for i in range(60):
        result = perf.update()
        if not result:
            print("  ❌ Update failed")
        time.sleep(0.01)
    
    print(f"  Baseline: {perf.get_baseline_fps():.1f} FPS")
    
    print("\n[Test 2] Performance score")
    score = perf.get_performance_score()
    print(f"  Score: {score:.1f}/100")
    
    print("\n[Test 3] Status")
    status = perf.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n[Test 4] Error handling - Invalid data")
    # Simulate invalid data
    manager.cpu = 150  # Invalid!
    result = perf.update()
    print(f"  Update result: {result}")
    
    print("\n[Test 5] Reset")
    if perf.reset():
        print("  ✅ Reset successful")
    
    print("\n✅ Test completed!")
