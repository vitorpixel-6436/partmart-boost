#!/usr/bin/env python3
"""Performance History - Time-series Data Storage

Version: 0.3.5g (package 3.9a, stage 7.5/7.7)

Package 3.9a Stage 7.5: Advanced monitoring with history tracking.

Features:
- Time-series storage
- Circular buffer (fixed memory)
- Statistical analysis
- Trend detection
- Data aggregation
- Export capabilities
"""
import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import statistics


@dataclass
class PerformanceSnapshot:
    """Single performance measurement
    
    Attributes:
        timestamp: Unix timestamp
        cpu: CPU usage (0-100)
        gpu: GPU usage (0-100)
        ram: RAM usage (0-100)
        fps: Frames per second
        gpu_temp: GPU temperature (°C)
        score: Overall performance score (0-100)
    """
    timestamp: float
    cpu: float = 0.0
    gpu: float = 0.0
    ram: float = 0.0
    fps: float = 0.0
    gpu_temp: float = 0.0
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'cpu': self.cpu,
            'gpu': self.gpu,
            'ram': self.ram,
            'fps': self.fps,
            'gpu_temp': self.gpu_temp,
            'score': self.score,
        }


@dataclass
class PerformanceStats:
    """Statistical summary
    
    Attributes:
        metric: Metric name
        current: Current value
        min: Minimum value
        max: Maximum value
        mean: Average value
        median: Median value
        std_dev: Standard deviation
        trend: Trend direction ('rising', 'falling', 'stable')
        samples: Number of samples
    """
    metric: str
    current: float
    min: float
    max: float
    mean: float
    median: float
    std_dev: float
    trend: str
    samples: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metric': self.metric,
            'current': self.current,
            'min': self.min,
            'max': self.max,
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev,
            'trend': self.trend,
            'samples': self.samples,
        }


class PerformanceHistory:
    """Performance history tracker
    
    v0.3.5g (package 3.9a, stage 7.5/7.7)
    
    Features:
    - Circular buffer (fixed memory)
    - Real-time statistics
    - Trend detection
    - Data aggregation
    - Thread-safe
    
    Usage:
        >>> history = PerformanceHistory(max_samples=1000)
        >>> 
        >>> # Add snapshot
        >>> history.add_snapshot(cpu=65, gpu=78, ram=50, fps=60, score=87)
        >>> 
        >>> # Get statistics
        >>> stats = history.get_stats('cpu')
        >>> print(f"CPU avg: {stats.mean:.1f}%")
        >>> 
        >>> # Get recent data
        >>> recent = history.get_recent(seconds=60)
    """
    
    def __init__(self, max_samples: int = 1000):
        """Initialize history
        
        Args:
            max_samples: Maximum number of samples to store
        """
        self._max_samples = max_samples
        self._snapshots: deque[PerformanceSnapshot] = deque(maxlen=max_samples)
        self._lock = threading.RLock()
        self._start_time = time.time()
        
        print(f"[PerformanceHistory] Initialized (max {max_samples} samples)")
    
    def add_snapshot(self, cpu: float = 0.0, gpu: float = 0.0,
                    ram: float = 0.0, fps: float = 0.0,
                    gpu_temp: float = 0.0, score: float = 0.0) -> None:
        """Add performance snapshot
        
        Args:
            cpu: CPU usage (0-100)
            gpu: GPU usage (0-100)
            ram: RAM usage (0-100)
            fps: Frames per second
            gpu_temp: GPU temperature (°C)
            score: Overall score (0-100)
        """
        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            cpu=cpu,
            gpu=gpu,
            ram=ram,
            fps=fps,
            gpu_temp=gpu_temp,
            score=score
        )
        
        with self._lock:
            self._snapshots.append(snapshot)
    
    def get_stats(self, metric: str) -> Optional[PerformanceStats]:
        """Get statistics for metric
        
        Args:
            metric: Metric name ('cpu', 'gpu', 'ram', 'fps', 'gpu_temp', 'score')
        
        Returns:
            PerformanceStats or None
        """
        with self._lock:
            if len(self._snapshots) == 0:
                return None
            
            # Extract values
            values = []
            for snap in self._snapshots:
                if metric == 'cpu':
                    values.append(snap.cpu)
                elif metric == 'gpu':
                    values.append(snap.gpu)
                elif metric == 'ram':
                    values.append(snap.ram)
                elif metric == 'fps':
                    values.append(snap.fps)
                elif metric == 'gpu_temp':
                    values.append(snap.gpu_temp)
                elif metric == 'score':
                    values.append(snap.score)
                else:
                    return None
            
            # Filter zeros
            values = [v for v in values if v > 0]
            if not values:
                return None
            
            # Calculate statistics
            current = values[-1]
            min_val = min(values)
            max_val = max(values)
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            
            # Standard deviation
            try:
                std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
            except statistics.StatisticsError:
                std_dev = 0.0
            
            # Trend detection
            trend = self._detect_trend(values)
            
            return PerformanceStats(
                metric=metric,
                current=current,
                min=min_val,
                max=max_val,
                mean=mean_val,
                median=median_val,
                std_dev=std_dev,
                trend=trend,
                samples=len(values)
            )
    
    def get_recent(self, seconds: float = 60) -> List[PerformanceSnapshot]:
        """Get recent snapshots
        
        Args:
            seconds: Time window (seconds)
        
        Returns:
            List of snapshots
        """
        cutoff = time.time() - seconds
        
        with self._lock:
            return [snap for snap in self._snapshots if snap.timestamp >= cutoff]
    
    def get_all(self) -> List[PerformanceSnapshot]:
        """Get all snapshots
        
        Returns:
            List of all snapshots
        """
        with self._lock:
            return list(self._snapshots)
    
    def get_aggregated(self, window_seconds: float = 60,
                      aggregate_func: str = 'mean') -> List[Tuple[float, Dict[str, float]]]:
        """Get time-aggregated data
        
        Args:
            window_seconds: Aggregation window (seconds)
            aggregate_func: Aggregation function ('mean', 'min', 'max')
        
        Returns:
            List of (timestamp, aggregated_values)
        """
        with self._lock:
            if len(self._snapshots) == 0:
                return []
            
            # Group by time windows
            windows: Dict[int, List[PerformanceSnapshot]] = {}
            
            for snap in self._snapshots:
                window_idx = int(snap.timestamp / window_seconds)
                if window_idx not in windows:
                    windows[window_idx] = []
                windows[window_idx].append(snap)
            
            # Aggregate each window
            result = []
            for window_idx in sorted(windows.keys()):
                snaps = windows[window_idx]
                timestamp = window_idx * window_seconds
                
                # Extract values
                cpu_vals = [s.cpu for s in snaps if s.cpu > 0]
                gpu_vals = [s.gpu for s in snaps if s.gpu > 0]
                ram_vals = [s.ram for s in snaps if s.ram > 0]
                fps_vals = [s.fps for s in snaps if s.fps > 0]
                
                # Aggregate
                if aggregate_func == 'mean':
                    agg_func = statistics.mean
                elif aggregate_func == 'min':
                    agg_func = min
                elif aggregate_func == 'max':
                    agg_func = max
                else:
                    agg_func = statistics.mean
                
                aggregated = {
                    'cpu': agg_func(cpu_vals) if cpu_vals else 0,
                    'gpu': agg_func(gpu_vals) if gpu_vals else 0,
                    'ram': agg_func(ram_vals) if ram_vals else 0,
                    'fps': agg_func(fps_vals) if fps_vals else 0,
                }
                
                result.append((timestamp, aggregated))
            
            return result
    
    def clear(self) -> None:
        """Clear all history"""
        with self._lock:
            self._snapshots.clear()
            self._start_time = time.time()
        
        print("[PerformanceHistory] Cleared")
    
    def get_uptime(self) -> float:
        """Get uptime in seconds
        
        Returns:
            Uptime in seconds
        """
        return time.time() - self._start_time
    
    def get_count(self) -> int:
        """Get number of snapshots
        
        Returns:
            Number of snapshots
        """
        with self._lock:
            return len(self._snapshots)
    
    def export_csv(self, filename: str) -> bool:
        """Export to CSV
        
        Args:
            filename: Output filename
        
        Returns:
            True if successful
        """
        try:
            import csv
            
            with self._lock:
                snapshots = list(self._snapshots)
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'cpu', 'gpu', 'ram', 'fps', 'gpu_temp', 'score'
                ])
                writer.writeheader()
                
                for snap in snapshots:
                    writer.writerow(snap.to_dict())
            
            print(f"[PerformanceHistory] Exported {len(snapshots)} samples to {filename}")
            return True
        
        except Exception as e:
            print(f"[PerformanceHistory] Export failed: {e}")
            return False
    
    def _detect_trend(self, values: List[float]) -> str:
        """Detect trend in values
        
        Args:
            values: List of values
        
        Returns:
            Trend direction ('rising', 'falling', 'stable')
        """
        if len(values) < 3:
            return 'stable'
        
        # Use recent values for trend
        recent = values[-min(10, len(values)):]
        
        # Linear regression (simple)
        n = len(recent)
        x = list(range(n))
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(recent)
        
        # Slope
        numerator = sum((x[i] - mean_x) * (recent[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Classify trend
        threshold = 0.5  # Adjust sensitivity
        if slope > threshold:
            return 'rising'
        elif slope < -threshold:
            return 'falling'
        else:
            return 'stable'


# Testing
if __name__ == '__main__':
    import random
    
    print("="*60)
    print("PerformanceHistory Test")
    print("="*60)
    print()
    
    history = PerformanceHistory(max_samples=100)
    
    # Simulate data
    print("Generating test data...")
    for i in range(50):
        history.add_snapshot(
            cpu=50 + random.uniform(-10, 10),
            gpu=70 + random.uniform(-5, 5),
            ram=60 + random.uniform(-15, 15),
            fps=60 + random.uniform(-10, 10),
            gpu_temp=75 + random.uniform(-5, 5),
            score=80 + random.uniform(-10, 10)
        )
        time.sleep(0.01)
    
    print(f"Collected {history.get_count()} samples\n")
    
    # Get statistics
    print("Statistics:")
    for metric in ['cpu', 'gpu', 'ram', 'fps']:
        stats = history.get_stats(metric)
        if stats:
            print(f"  {metric.upper()}: "
                  f"current={stats.current:.1f}, "
                  f"mean={stats.mean:.1f}, "
                  f"min={stats.min:.1f}, "
                  f"max={stats.max:.1f}, "
                  f"trend={stats.trend}")
    
    print()
    
    # Recent data
    recent = history.get_recent(seconds=1.0)
    print(f"Recent (last 1s): {len(recent)} samples")
    
    print()
    print("✅ Test completed!")
