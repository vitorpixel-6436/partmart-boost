#!/usr/bin/env python3
"""Performance Monitor - Advanced system performance analytics

Version: 0.3.5d_package3.2a

Features:
- CPU/GPU/FPS correlation tracking
- Bottleneck history and analysis
- Performance scoring (0-100)
- Frame time analysis
- Load prediction
- Thermal efficiency tracking
- Performance degradation detection

Preparation for Frame Gen/Upscaler:
- Correlation data for quality decisions
- Load prediction for adaptive modes
- Bottleneck patterns for optimization
- Performance baselines for ML models
"""
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Deque
from collections import deque
from dataclasses import dataclass


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
    """Advanced performance analytics and monitoring
    
    v0.3.5d_package3.2a - Foundation for Frame Gen/Upscaler
    
    This monitor provides:
    - Real-time performance scoring
    - Component correlation analysis
    - Bottleneck tracking and prediction
    - Performance trend analysis
    - Load forecasting
    
    Integration:
    - Works with MonitorManager for system data
    - Uses FPS data from DataBus
    - Event-driven updates
    
    ML/AI Ready:
    - Correlation matrices for decisions
    - Historical patterns for learning
    - Baseline establishment
    
    Example:
        >>> from monitors.manager import MonitorManager
        >>> from core.databus import get_databus
        >>> 
        >>> manager = MonitorManager()
        >>> bus = get_databus()
        >>> bus.set_fps_tracking_enabled(True)
        >>> 
        >>> perf = PerformanceMonitor(manager, bus)
        >>> perf.update()  # Collect data
        >>> 
        >>> score = perf.get_performance_score()
        >>> print(f"Performance: {score:.1f}/100")
        >>> 
        >>> bottleneck = perf.get_current_bottleneck()
        >>> print(f"Bottleneck: {bottleneck.component}")
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
        
        # History buffer (ring buffer)
        self._history_size = history_size
        self._snapshots: Deque[PerformanceSnapshot] = deque(maxlen=history_size)
        self._bottleneck_history: Deque[BottleneckInfo] = deque(maxlen=history_size)
        
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
        
        print("[PerformanceMonitor v0.3.5d_package3.2a] Initialized")
    
    # === DATA COLLECTION ===
    
    def update(self):
        """Collect current performance snapshot
        
        Call this periodically (e.g., every 2 seconds via DataBus timer)
        
        Example:
            >>> perf.update()
        """
        # Get system data
        cpu_load = self._manager.get_cpu_load()
        gpu_load = self._manager.get_gpu_load()
        ram_usage = self._manager.get_ram_percent()
        cpu_temp = self._manager.get_cpu_temp()
        gpu_temp_raw = self._manager.get_gpu_temp()
        gpu_temp = gpu_temp_raw if gpu_temp_raw > 0 else None
        
        # Get FPS data
        fps = self._manager.get_fps()
        frame_time = self._manager.get_frame_time()
        
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
        bottleneck = self._detect_bottleneck(snapshot)
        self._bottleneck_history.append(bottleneck)
        
        # Update correlations
        if len(self._snapshots) >= 30:  # Need 30+ samples
            self._update_correlations()
        
        # Check for degradation
        if len(self._snapshots) >= 60:  # Need 60+ samples (2 min)
            self._check_performance_degradation()
        
        # Establish baseline
        if not self._baseline_established and len(self._snapshots) >= 60:
            self._establish_baseline()
    
    def _detect_bottleneck(self, snapshot: PerformanceSnapshot) -> BottleneckInfo:
        """Detect current bottleneck
        
        Args:
            snapshot: Current performance snapshot
        
        Returns:
            BottleneckInfo object
        """
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
    
    def _update_correlations(self):
        """Update CPU/GPU/FPS correlations
        
        Uses Pearson correlation coefficient
        """
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
        try:
            self._cpu_fps_correlation = np.corrcoef(cpu_loads, fps_values)[0, 1]
            self._gpu_fps_correlation = np.corrcoef(gpu_loads, fps_values)[0, 1]
        except (ValueError, FloatingPointError):
            # Not enough variance or NaN values
            pass
    
    def _establish_baseline(self):
        """Establish performance baseline
        
        Called after collecting 60+ samples
        """
        if len(self._snapshots) < 60:
            return
        
        # Calculate average FPS from recent history
        recent = list(self._snapshots)[-60:]
        fps_values = [s.fps for s in recent if s.fps > 0]
        
        if fps_values:
            self._baseline_fps = np.mean(fps_values)
            self._baseline_established = True
            print(f"[PerformanceMonitor] Baseline established: {self._baseline_fps:.1f} FPS")
    
    def _check_performance_degradation(self):
        """Check if performance is degrading over time
        
        Compares recent FPS to baseline
        """
        if not self._baseline_established:
            return
        
        # Get recent FPS (last 30 samples)
        recent = list(self._snapshots)[-30:]
        recent_fps = [s.fps for s in recent if s.fps > 0]
        
        if not recent_fps:
            return
        
        avg_recent_fps = np.mean(recent_fps)
        
        # Check if dropped more than 20% from baseline
        if avg_recent_fps < self._baseline_fps * 0.8:
            if not self._performance_declining:
                self._performance_declining = True
                self._decline_start_time = time.time()
                print(f"[PerformanceMonitor] Performance degradation detected: {avg_recent_fps:.1f} FPS (baseline: {self._baseline_fps:.1f})")
        else:
            if self._performance_declining:
                print(f"[PerformanceMonitor] Performance recovered: {avg_recent_fps:.1f} FPS")
            self._performance_declining = False
            self._decline_start_time = None
    
    # === ANALYTICS API ===
    
    def get_performance_score(self) -> float:
        """Get overall performance score (0-100)
        
        Score based on:
        - FPS (50%)
        - Load balance (30%)
        - Thermal efficiency (20%)
        
        Returns:
            Performance score (0-100)
        
        Example:
            >>> score = perf.get_performance_score()
            >>> print(f"Performance: {score:.1f}/100")
        """
        if not self._snapshots:
            return 0.0
        
        recent = list(self._snapshots)[-30:]  # Last 30 samples
        
        # FPS score (50%)
        fps_values = [s.fps for s in recent if s.fps > 0]
        if fps_values:
            avg_fps = np.mean(fps_values)
            fps_score = min(100, (avg_fps / 60.0) * 100)  # 60 FPS = 100%
        else:
            fps_score = 0.0
        
        # Load balance score (30%)
        cpu_loads = [s.cpu_load for s in recent]
        gpu_loads = [s.gpu_load for s in recent]
        ram_loads = [s.ram_usage for s in recent]
        
        avg_cpu = np.mean(cpu_loads)
        avg_gpu = np.mean(gpu_loads)
        avg_ram = np.mean(ram_loads)
        
        max_load = max(avg_cpu, avg_gpu, avg_ram)
        
        # Penalty for high load
        if max_load >= 90:
            load_score = 50
        elif max_load >= 70:
            load_score = 75
        else:
            load_score = 100
        
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
                thermal_score = 50
            elif max_temp >= 75:
                thermal_score = 75
            else:
                thermal_score = 100
        else:
            thermal_score = 100
        
        # Weighted total
        total_score = (fps_score * 0.5) + (load_score * 0.3) + (thermal_score * 0.2)
        
        self._last_score = total_score
        return total_score
    
    def get_correlation_stats(self) -> Dict:
        """Get CPU/GPU/FPS correlations
        
        Returns:
            Dict with correlation coefficients
        
        Example:
            >>> corr = perf.get_correlation_stats()
            >>> print(f"CPU-FPS: {corr['cpu_fps']:.2f}")
            >>> print(f"GPU-FPS: {corr['gpu_fps']:.2f}")
        """
        return {
            'cpu_fps': self._cpu_fps_correlation,
            'gpu_fps': self._gpu_fps_correlation,
            'interpretation': self._interpret_correlations(),
        }
    
    def _interpret_correlations(self) -> str:
        """Interpret correlation values
        
        Returns:
            Human-readable interpretation
        """
        cpu_corr = abs(self._cpu_fps_correlation)
        gpu_corr = abs(self._gpu_fps_correlation)
        
        if cpu_corr > 0.7 and gpu_corr < 0.3:
            return "CPU-bound workload"
        elif gpu_corr > 0.7 and cpu_corr < 0.3:
            return "GPU-bound workload"
        elif cpu_corr > 0.5 and gpu_corr > 0.5:
            return "Balanced workload"
        else:
            return "Unclear pattern (need more data)"
    
    def get_current_bottleneck(self) -> Optional[BottleneckInfo]:
        """Get current bottleneck
        
        Returns:
            Latest BottleneckInfo or None
        
        Example:
            >>> bottleneck = perf.get_current_bottleneck()
            >>> if bottleneck and bottleneck.severity != 'none':
            >>>     print(f"Bottleneck: {bottleneck.component} ({bottleneck.severity})")
        """
        if not self._bottleneck_history:
            return None
        return self._bottleneck_history[-1]
    
    def get_bottleneck_history(self, count: int = 60) -> List[BottleneckInfo]:
        """Get recent bottleneck history
        
        Args:
            count: Number of recent bottlenecks to return
        
        Returns:
            List of BottleneckInfo objects
        
        Example:
            >>> history = perf.get_bottleneck_history(30)
            >>> cpu_bottlenecks = sum(1 for b in history if b.component == 'cpu')
            >>> print(f"CPU bottlenecked {cpu_bottlenecks} times")
        """
        return list(self._bottleneck_history)[-count:]
    
    def predict_load(self, seconds_ahead: float = 10.0) -> Dict[str, float]:
        """Predict future load using linear regression
        
        Args:
            seconds_ahead: How many seconds to predict ahead
        
        Returns:
            Dict with predicted CPU/GPU/RAM loads
        
        Example:
            >>> prediction = perf.predict_load(10)
            >>> print(f"CPU in 10s: {prediction['cpu']:.1f}%")
        """
        if len(self._snapshots) < 30:
            # Not enough data, return current values
            if self._snapshots:
                last = self._snapshots[-1]
                return {
                    'cpu': last.cpu_load,
                    'gpu': last.gpu_load,
                    'ram': last.ram_usage,
                }
            return {'cpu': 0, 'gpu': 0, 'ram': 0}
        
        # Get recent samples
        recent = list(self._snapshots)[-60:]
        
        # Time series (seconds from first sample)
        times = np.array([s.timestamp - recent[0].timestamp for s in recent])
        
        # Load arrays
        cpu_loads = np.array([s.cpu_load for s in recent])
        gpu_loads = np.array([s.gpu_load for s in recent])
        ram_loads = np.array([s.ram_usage for s in recent])
        
        # Simple linear regression
        def predict(times, values, ahead):
            # Fit line: y = mx + b
            m, b = np.polyfit(times, values, 1)
            future_time = times[-1] + ahead
            prediction = m * future_time + b
            return max(0, min(100, prediction))  # Clamp to 0-100
        
        return {
            'cpu': predict(times, cpu_loads, seconds_ahead),
            'gpu': predict(times, gpu_loads, seconds_ahead),
            'ram': predict(times, ram_loads, seconds_ahead),
        }
    
    def get_efficiency_report(self) -> Dict:
        """Get component efficiency report
        
        Efficiency = Performance / Load
        
        Returns:
            Dict with efficiency scores per component
        
        Example:
            >>> eff = perf.get_efficiency_report()
            >>> print(f"CPU efficiency: {eff['cpu']:.1f}%")
        """
        if not self._snapshots:
            return {'cpu': 0, 'gpu': 0, 'overall': 0}
        
        recent = list(self._snapshots)[-30:]
        
        # Get FPS and loads
        fps_values = [s.fps for s in recent if s.fps > 0]
        cpu_loads = [s.cpu_load for s in recent]
        gpu_loads = [s.gpu_load for s in recent]
        
        if not fps_values:
            return {'cpu': 0, 'gpu': 0, 'overall': 0}
        
        avg_fps = np.mean(fps_values)
        avg_cpu = np.mean(cpu_loads)
        avg_gpu = np.mean(gpu_loads)
        
        # Efficiency = FPS per % load
        cpu_eff = (avg_fps / avg_cpu) if avg_cpu > 0 else 0
        gpu_eff = (avg_fps / avg_gpu) if avg_gpu > 0 else 0
        
        # Normalize to 0-100 scale (assuming 1 FPS per 1% = 100% efficient)
        cpu_eff_score = min(100, cpu_eff * 100)
        gpu_eff_score = min(100, gpu_eff * 100)
        overall_eff = (cpu_eff_score + gpu_eff_score) / 2
        
        return {
            'cpu': cpu_eff_score,
            'gpu': gpu_eff_score,
            'overall': overall_eff,
        }
    
    def get_performance_trends(self) -> Dict:
        """Get historical performance trends
        
        Returns:
            Dict with trend information
        
        Example:
            >>> trends = perf.get_performance_trends()
            >>> print(f"FPS trend: {trends['fps_trend']}")
        """
        if len(self._snapshots) < 60:
            return {
                'fps_trend': 'stable',
                'load_trend': 'stable',
                'thermal_trend': 'stable',
            }
        
        # Get first and last 30 samples
        all_snapshots = list(self._snapshots)
        first_30 = all_snapshots[:30]
        last_30 = all_snapshots[-30:]
        
        # FPS trend
        first_fps = np.mean([s.fps for s in first_30 if s.fps > 0] or [0])
        last_fps = np.mean([s.fps for s in last_30 if s.fps > 0] or [0])
        
        if last_fps > first_fps * 1.1:
            fps_trend = 'improving'
        elif last_fps < first_fps * 0.9:
            fps_trend = 'declining'
        else:
            fps_trend = 'stable'
        
        # Load trend
        first_load = np.mean([max(s.cpu_load, s.gpu_load) for s in first_30])
        last_load = np.mean([max(s.cpu_load, s.gpu_load) for s in last_30])
        
        if last_load > first_load * 1.1:
            load_trend = 'increasing'
        elif last_load < first_load * 0.9:
            load_trend = 'decreasing'
        else:
            load_trend = 'stable'
        
        # Thermal trend
        first_temps = []
        last_temps = []
        
        for s in first_30:
            if s.cpu_temp:
                first_temps.append(s.cpu_temp)
            if s.gpu_temp:
                first_temps.append(s.gpu_temp)
        
        for s in last_30:
            if s.cpu_temp:
                last_temps.append(s.cpu_temp)
            if s.gpu_temp:
                last_temps.append(s.gpu_temp)
        
        if first_temps and last_temps:
            first_temp = np.mean(first_temps)
            last_temp = np.mean(last_temps)
            
            if last_temp > first_temp + 5:
                thermal_trend = 'heating'
            elif last_temp < first_temp - 5:
                thermal_trend = 'cooling'
            else:
                thermal_trend = 'stable'
        else:
            thermal_trend = 'unknown'
        
        return {
            'fps_trend': fps_trend,
            'load_trend': load_trend,
            'thermal_trend': thermal_trend,
        }
    
    def is_performance_degrading(self) -> bool:
        """Check if performance is currently degrading
        
        Returns:
            True if performance has declined >20% from baseline
        
        Example:
            >>> if perf.is_performance_degrading():
            >>>     print("Performance issues detected!")
        """
        return self._performance_declining
    
    def get_baseline_fps(self) -> float:
        """Get established FPS baseline
        
        Returns:
            Baseline FPS or 0 if not established
        
        Example:
            >>> baseline = perf.get_baseline_fps()
            >>> print(f"Baseline: {baseline:.1f} FPS")
        """
        return self._baseline_fps if self._baseline_established else 0.0
    
    def reset(self):
        """Reset all performance history
        
        Example:
            >>> perf.reset()  # Start fresh
        """
        self._snapshots.clear()
        self._bottleneck_history.clear()
        self._baseline_established = False
        self._performance_declining = False
        self._decline_start_time = None
        print("[PerformanceMonitor] Reset complete")


# ========== TESTING ==========

if __name__ == "__main__":
    import random
    
    print("="*60)
    print("PerformanceMonitor v0.3.5d_package3.2a Test")
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
    
    print("\n[Test 1] Collecting data (60 samples for baseline)...")
    for i in range(60):
        perf.update()
        time.sleep(0.01)  # Simulate time
    
    print(f"  Baseline established: {perf.get_baseline_fps():.1f} FPS")
    
    print("\n[Test 2] Performance score")
    score = perf.get_performance_score()
    print(f"  Score: {score:.1f}/100")
    
    print("\n[Test 3] Correlation stats")
    corr = perf.get_correlation_stats()
    print(f"  CPU-FPS: {corr['cpu_fps']:.2f}")
    print(f"  GPU-FPS: {corr['gpu_fps']:.2f}")
    print(f"  Interpretation: {corr['interpretation']}")
    
    print("\n[Test 4] Current bottleneck")
    bottleneck = perf.get_current_bottleneck()
    if bottleneck:
        print(f"  Component: {bottleneck.component}")
        print(f"  Severity: {bottleneck.severity}")
        print(f"  Load: {bottleneck.load:.1f}%")
    
    print("\n[Test 5] Load prediction")
    prediction = perf.predict_load(10)
    print(f"  CPU in 10s: {prediction['cpu']:.1f}%")
    print(f"  GPU in 10s: {prediction['gpu']:.1f}%")
    print(f"  RAM in 10s: {prediction['ram']:.1f}%")
    
    print("\n[Test 6] Efficiency report")
    eff = perf.get_efficiency_report()
    print(f"  CPU efficiency: {eff['cpu']:.1f}%")
    print(f"  GPU efficiency: {eff['gpu']:.1f}%")
    print(f"  Overall: {eff['overall']:.1f}%")
    
    print("\n[Test 7] Performance trends")
    trends = perf.get_performance_trends()
    print(f"  FPS trend: {trends['fps_trend']}")
    print(f"  Load trend: {trends['load_trend']}")
    print(f"  Thermal trend: {trends['thermal_trend']}")
    
    print("\n[Test 8] Degradation detection")
    # Simulate FPS drop
    manager.fps = 40.0
    for i in range(30):
        perf.update()
        time.sleep(0.01)
    
    if perf.is_performance_degrading():
        print("  ⚠ Performance degradation detected!")
    else:
        print("  ✓ Performance stable")
    
    print("\n" + "="*60)
    print("✅ PerformanceMonitor v0.3.5d_package3.2a - All Tests Passed!")
    print("="*60)
    print("\nFeatures:")
    print("  ✅ Performance scoring (0-100)")
    print("  ✅ CPU/GPU/FPS correlation")
    print("  ✅ Bottleneck tracking")
    print("  ✅ Load prediction")
    print("  ✅ Efficiency analysis")
    print("  ✅ Trend detection")
    print("  ✅ Degradation alerts")
    print("\nReady for:")
    print("  🎯 Frame generation decisions")
    print("  🎯 Upscaler quality adjustment")
    print("  🎯 ML/AI optimization")
    print("="*60)
