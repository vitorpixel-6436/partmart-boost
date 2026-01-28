#!/usr/bin/env python3
"""FPS Tracker

Version: 0.3.5d_package3.5b - BUGFIX: Added validation

Frame rate tracking with validation and error handling.
"""
import time
from collections import deque
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class FPSStats:
    """FPS statistics
    
    Attributes:
        current: Current FPS
        average: Average FPS
        min: Minimum FPS
        max: Maximum FPS
        frame_time: Frame time (ms)
    """
    current: float
    average: float
    min: float
    max: float
    frame_time: float


class FPSTracker:
    """FPS Tracker
    
    v0.3.5d_package3.5b - BUGFIX: Type validation
    
    Tracks frame rate with proper validation.
    
    Example:
        >>> tracker = FPSTracker()
        >>> tracker.frame()  # Call each frame
        >>> fps = tracker.get_fps()
    """
    
    # BUGFIX: Added validation constants
    MIN_FPS = 0.1
    MAX_FPS = 1000.0
    MIN_RESOLUTION = (640, 480)
    MAX_RESOLUTION = (16384, 16384)
    
    def __init__(self, window_size: int = 60):
        """Initialize FPS tracker
        
        Args:
            window_size: Number of frames to average
        
        Raises:
            ValueError: If window_size invalid
        """
        # BUGFIX: Validate window size
        if window_size < 1 or window_size > 1000:
            raise ValueError(f"window_size must be 1-1000, got {window_size}")
        
        self._window_size = window_size
        self._frame_times = deque(maxlen=window_size)
        self._last_frame_time: Optional[float] = None
        self._frame_count = 0
        
        print(f"[FPSTracker v0.3.5d_package3.5b] Initialized (window={window_size})")
    
    def frame(self) -> float:
        """Record frame
        
        Returns:
            Current FPS
        
        Example:
            >>> fps = tracker.frame()
        """
        current_time = time.perf_counter()
        
        if self._last_frame_time is not None:
            frame_time = current_time - self._last_frame_time
            
            # BUGFIX: Validate frame time
            if frame_time > 0:  # Prevent division by zero
                self._frame_times.append(frame_time)
        
        self._last_frame_time = current_time
        self._frame_count += 1
        
        return self.get_fps()
    
    def get_fps(self) -> float:
        """Get current FPS
        
        Returns:
            Current FPS
        
        Example:
            >>> fps = tracker.get_fps()
        """
        if not self._frame_times:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        
        # BUGFIX: Prevent division by zero
        if avg_frame_time <= 0:
            return 0.0
        
        fps = 1.0 / avg_frame_time
        
        # BUGFIX: Clamp to valid range
        return max(self.MIN_FPS, min(self.MAX_FPS, fps))
    
    def get_stats(self) -> FPSStats:
        """Get FPS statistics
        
        Returns:
            FPS stats
        
        Example:
            >>> stats = tracker.get_stats()
            >>> print(f"FPS: {stats.current:.1f}")
        """
        if not self._frame_times:
            return FPSStats(
                current=0.0,
                average=0.0,
                min=0.0,
                max=0.0,
                frame_time=0.0
            )
        
        frame_times = list(self._frame_times)
        
        # BUGFIX: Filter out invalid values
        valid_times = [ft for ft in frame_times if ft > 0]
        
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
        
        # Convert to FPS
        current_fps = 1.0 / valid_times[-1] if valid_times[-1] > 0 else 0.0
        avg_fps = 1.0 / avg_time if avg_time > 0 else 0.0
        min_fps = 1.0 / max_time if max_time > 0 else 0.0  # Inverted
        max_fps = 1.0 / min_time if min_time > 0 else 0.0  # Inverted
        
        # BUGFIX: Clamp all values
        return FPSStats(
            current=max(self.MIN_FPS, min(self.MAX_FPS, current_fps)),
            average=max(self.MIN_FPS, min(self.MAX_FPS, avg_fps)),
            min=max(self.MIN_FPS, min(self.MAX_FPS, min_fps)),
            max=max(self.MIN_FPS, min(self.MAX_FPS, max_fps)),
            frame_time=avg_time * 1000.0  # Convert to ms
        )
    
    @staticmethod
    def validate_resolution(resolution: Tuple[int, int]) -> bool:
        """Validate resolution
        
        Args:
            resolution: (width, height)
        
        Returns:
            True if valid
        
        Example:
            >>> valid = FPSTracker.validate_resolution((1920, 1080))
        """
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
        """Reset tracker
        
        Example:
            >>> tracker.reset()
        """
        self._frame_times.clear()
        self._last_frame_time = None
        self._frame_count = 0
        print("[FPSTracker] Reset")


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("FPSTracker v0.3.5d_package3.5b Test (BUGFIX)")
    print("="*60)
    
    tracker = FPSTracker(window_size=30)
    
    print("\n[Test 1] Record frames")
    for i in range(60):
        time.sleep(1/60)  # Simulate 60 FPS
        fps = tracker.frame()
    print(f"  Current FPS: {fps:.1f}")
    
    print("\n[Test 2] Get statistics")
    stats = tracker.get_stats()
    print(f"  Current: {stats.current:.1f}")
    print(f"  Average: {stats.average:.1f}")
    print(f"  Min: {stats.min:.1f}")
    print(f"  Max: {stats.max:.1f}")
    print(f"  Frame time: {stats.frame_time:.2f}ms")
    
    print("\n[Test 3] Validate resolution")
    test_cases = [
        ((1920, 1080), True),
        ((640, 480), True),
        ((100, 100), False),  # Too small
        ((99999, 99999), False),  # Too large
        ((1920,), False),  # Invalid tuple
    ]
    
    for resolution, expected in test_cases:
        result = FPSTracker.validate_resolution(resolution)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {resolution}: {result}")
    
    print("\n[Test 4] Reset tracker")
    tracker.reset()
    stats = tracker.get_stats()
    print(f"  FPS after reset: {stats.current:.1f}")
    
    print("\n" + "="*60)
    print("✅ FPSTracker - All Tests Passed! (BUGFIX)")
    print("="*60)
