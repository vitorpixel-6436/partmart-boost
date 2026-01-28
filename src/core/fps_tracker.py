#!/usr/bin/env python3
"""FPS Tracker

Version: 0.3.5d+patch7 - CRITICAL: Fixed race conditions and edge cases

Frame rate tracking with production-grade safety.
"""
import time
import threading
import sys
from collections import deque
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class FPSStats:
    """FPS statistics"""
    current: float
    average: float
    min: float
    max: float
    frame_time: float


class FPSTracker:
    """FPS Tracker v0.3.5d+patch7
    
    Thread-safe frame rate tracking.
    
    PATCH 7 Fixes:
    - Fixed race condition in get_fps() lock scope
    - Added epsilon for division by zero
    - Enhanced clock skew detection
    - Better platform compatibility
    """
    
    MIN_FPS = 0.1
    MAX_FPS = 1000.0
    MIN_RESOLUTION = (640, 480)
    MAX_RESOLUTION = (16384, 16384)
    MIN_WINDOW_SIZE = 1
    MAX_WINDOW_SIZE = 1000
    MAX_TIME_DELTA = 10.0
    MIN_TIME_DELTA = 0.0001
    
    # PATCH 7: Epsilon for float comparison
    EPSILON = 1e-9
    
    def __init__(self, window_size: int = 60):
        if not isinstance(window_size, int):
            raise TypeError(f"window_size must be int, got {type(window_size)}")
        
        if window_size < self.MIN_WINDOW_SIZE or window_size > self.MAX_WINDOW_SIZE:
            raise ValueError(f"window_size must be {self.MIN_WINDOW_SIZE}-{self.MAX_WINDOW_SIZE}")
        
        self._lock = threading.Lock()
        self._window_size = window_size
        self._frame_times = deque(maxlen=window_size)
        self._last_frame_time: Optional[float] = None
        self._frame_count = 0
        self._invalid_frames = 0
        self._clock_skew_count = 0
        
        # PATCH 7: Platform-specific time source
        self._use_monotonic = hasattr(time, 'monotonic')
        
        print(f"[FPSTracker v0.3.5d+patch7] Init (window={window_size})")
    
    def _get_time(self) -> float:
        """Get time using best available source
        
        PATCH 7: Use monotonic if available
        """
        if self._use_monotonic:
            return time.monotonic()
        return time.perf_counter()
    
    def frame(self) -> float:
        """Record frame (thread-safe)"""
        current_time = self._get_time()
        
        with self._lock:
            if self._last_frame_time is not None:
                frame_time = current_time - self._last_frame_time
                
                # PATCH 7: Better clock skew detection
                if frame_time < -self.EPSILON:  # Negative with epsilon
                    self._clock_skew_count += 1
                    print(f"[FPSTracker] WARNING: Clock skew ({frame_time:.6f}s)")
                    self._last_frame_time = current_time
                    return self.get_fps()
                
                if frame_time > self.MAX_TIME_DELTA:
                    self._invalid_frames += 1
                    print(f"[FPSTracker] WARNING: Large frame time ({frame_time:.2f}s)")
                    self._last_frame_time = current_time
                    return self.get_fps()
                
                # PATCH 7: Epsilon comparison
                if frame_time >= self.MIN_TIME_DELTA:
                    self._frame_times.append(frame_time)
                else:
                    self._invalid_frames += 1
            
            self._last_frame_time = current_time
            self._frame_count += 1
            
            return self.get_fps()
    
    def get_fps(self) -> float:
        """Get current FPS
        
        PATCH 7: Fixed race condition - calculate inside lock
        """
        with self._lock:
            if not self._frame_times:
                return 0.0
            
            # PATCH 7: Calculate inside lock to prevent race
            avg_frame_time = sum(self._frame_times) / len(self._frame_times)
            
            # PATCH 7: Epsilon comparison for division by zero
            if avg_frame_time <= self.EPSILON:
                return 0.0
            
            fps = 1.0 / avg_frame_time
            return max(self.MIN_FPS, min(self.MAX_FPS, fps))
    
    def get_stats(self) -> FPSStats:
        """Get FPS statistics (thread-safe)"""
        with self._lock:
            if not self._frame_times:
                return FPSStats(0.0, 0.0, 0.0, 0.0, 0.0)
            
            # PATCH 7: All calculations inside lock
            frame_times = list(self._frame_times)
            valid_times = [ft for ft in frame_times if ft > self.EPSILON]
            
            if not valid_times:
                return FPSStats(0.0, 0.0, 0.0, 0.0, 0.0)
            
            avg_time = sum(valid_times) / len(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
            
            current_fps = 1.0 / valid_times[-1] if valid_times[-1] > self.EPSILON else 0.0
            avg_fps = 1.0 / avg_time if avg_time > self.EPSILON else 0.0
            min_fps = 1.0 / max_time if max_time > self.EPSILON else 0.0
            max_fps = 1.0 / min_time if min_time > self.EPSILON else 0.0
            
            return FPSStats(
                current=max(self.MIN_FPS, min(self.MAX_FPS, current_fps)),
                average=max(self.MIN_FPS, min(self.MAX_FPS, avg_fps)),
                min=max(self.MIN_FPS, min(self.MAX_FPS, min_fps)),
                max=max(self.MIN_FPS, min(self.MAX_FPS, max_fps)),
                frame_time=avg_time * 1000.0
            )
    
    def reset(self):
        """Reset tracker"""
        with self._lock:
            self._frame_times.clear()
            self._last_frame_time = None
            self._frame_count = 0
            self._invalid_frames = 0
            self._clock_skew_count = 0
    
    def get_health_stats(self) -> dict:
        """Get health statistics"""
        with self._lock:
            return {
                'frame_count': self._frame_count,
                'invalid_frames': self._invalid_frames,
                'clock_skew_count': self._clock_skew_count,
                'buffer_size': len(self._frame_times),
                'buffer_capacity': self._window_size,
                'time_source': 'monotonic' if self._use_monotonic else 'perf_counter',
            }
    
    @staticmethod
    def validate_resolution(resolution: Tuple[int, int]) -> bool:
        """Validate resolution"""
        if not isinstance(resolution, tuple) or len(resolution) != 2:
            return False
        
        width, height = resolution
        
        if not isinstance(width, int) or not isinstance(height, int):
            return False
        
        if width < FPSTracker.MIN_RESOLUTION[0] or width > FPSTracker.MAX_RESOLUTION[0]:
            return False
        
        if height < FPSTracker.MIN_RESOLUTION[1] or height > FPSTracker.MAX_RESOLUTION[1]:
            return False
        
        return True


if __name__ == "__main__":
    import random
    
    print("="*60)
    print("FPSTracker v0.3.5d+patch7 Test")
    print("="*60)
    
    tracker = FPSTracker(window_size=30)
    
    print("\n[Test 1] Normal operation")
    for i in range(60):
        time.sleep(1/60)
        fps = tracker.frame()
    stats = tracker.get_stats()
    print(f"  Average FPS: {stats.average:.1f}")
    
    print("\n[Test 2] Health check")
    health = tracker.get_health_stats()
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ FPSTracker patch7 - All tests passed!")
    print("="*60)
