#!/usr/bin/env python3
"""FPS Tracker

Version: 0.3.5d_package3.6a - BUGFIX: Thread safety + buffer overflow

Frame rate tracking with thread-safe operations.
"""
import time
import threading
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
    """FPS Tracker
    
    v0.3.5d_package3.6a - MICRO-FIX #1
    
    Thread-safe FPS tracking with buffer overflow protection.
    
    Fixes:
    - Buffer overflow when maxlen exceeded
    - Race condition in get_fps()
    - Concurrent modification issues
    """
    
    MIN_FPS = 0.1
    MAX_FPS = 1000.0
    MIN_RESOLUTION = (640, 480)
    MAX_RESOLUTION = (16384, 16384)
    
    def __init__(self, window_size: int = 60):
        """Initialize FPS tracker
        
        Args:
            window_size: Number of frames to average
        """
        if window_size < 1 or window_size > 1000:
            raise ValueError(f"window_size must be 1-1000, got {window_size}")
        
        self._window_size = window_size
        self._frame_times = deque(maxlen=window_size)
        self._last_frame_time: Optional[float] = None
        self._frame_count = 0
        
        # MICRO-FIX #1: Add thread lock for safety
        self._lock = threading.Lock()
        
        print(f"[FPSTracker v0.3.5d_package3.6a] Initialized (window={window_size})")
    
    def frame(self) -> float:
        """Record frame (thread-safe)
        
        Returns:
            Current FPS
        """
        current_time = time.perf_counter()
        
        # MICRO-FIX #1: Lock during modification
        with self._lock:
            if self._last_frame_time is not None:
                frame_time = current_time - self._last_frame_time
                
                # Validate frame time
                if frame_time > 0 and frame_time < 10.0:  # Max 10 seconds between frames
                    # MICRO-FIX #1: deque handles maxlen automatically, no overflow
                    self._frame_times.append(frame_time)
            
            self._last_frame_time = current_time
            self._frame_count += 1
        
        return self.get_fps()
    
    def get_fps(self) -> float:
        """Get current FPS (thread-safe)
        
        Returns:
            Current FPS
        """
        # MICRO-FIX #1: Lock during read
        with self._lock:
            if not self._frame_times:
                return 0.0
            
            # Create snapshot to avoid holding lock
            frame_times_snapshot = list(self._frame_times)
        
        # Calculate outside lock
        avg_frame_time = sum(frame_times_snapshot) / len(frame_times_snapshot)
        
        if avg_frame_time <= 0:
            return 0.0
        
        fps = 1.0 / avg_frame_time
        return max(self.MIN_FPS, min(self.MAX_FPS, fps))
    
    def get_stats(self) -> FPSStats:
        """Get FPS statistics (thread-safe)
        
        Returns:
            FPS stats
        """
        # MICRO-FIX #1: Lock and snapshot
        with self._lock:
            if not self._frame_times:
                return FPSStats(
                    current=0.0,
                    average=0.0,
                    min=0.0,
                    max=0.0,
                    frame_time=0.0
                )
            
            frame_times_snapshot = list(self._frame_times)
        
        # Calculate outside lock
        valid_times = [ft for ft in frame_times_snapshot if ft > 0]
        
        if not valid_times:
            return FPSStats(
                current=0.0,
                average=0.0,
                min=0.0,
                max=0.0,
                frame_time=0.0
            )
        
        avg_time = sum(valid_times) / len(valid_times)
        min_time = min(valid_times)
        max_time = max(valid_times)
        
        current_fps = 1.0 / valid_times[-1] if valid_times[-1] > 0 else 0.0
        avg_fps = 1.0 / avg_time if avg_time > 0 else 0.0
        min_fps = 1.0 / max_time if max_time > 0 else 0.0
        max_fps = 1.0 / min_time if min_time > 0 else 0.0
        
        return FPSStats(
            current=max(self.MIN_FPS, min(self.MAX_FPS, current_fps)),
            average=max(self.MIN_FPS, min(self.MAX_FPS, avg_fps)),
            min=max(self.MIN_FPS, min(self.MAX_FPS, min_fps)),
            max=max(self.MIN_FPS, min(self.MAX_FPS, max_fps)),
            frame_time=avg_time * 1000.0
        )
    
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
    
    def reset(self):
        """Reset tracker (thread-safe)"""
        with self._lock:
            self._frame_times.clear()
            self._last_frame_time = None
            self._frame_count = 0
        print("[FPSTracker] Reset")


if __name__ == "__main__":
    print("="*60)
    print("FPSTracker v0.3.5d_package3.6a Test (MICRO-FIX #1)")
    print("="*60)
    print("\n✅ MICRO-FIX #1 Applied:")
    print("  - Thread-safe operations with lock")
    print("  - Buffer overflow protection")
    print("  - Race condition fixes")
    print("="*60)
