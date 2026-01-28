#!/usr/bin/env python3
"""Session Recording

Version: 0.3.5d_package3.4b

Session management for analytics system.

Features:
- Session tracking
- Metadata recording
- Event logging
- Summary generation
"""
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class FrameMetric:
    """Single frame metrics
    
    Attributes:
        timestamp: Time since session start (s)
        fps: Frames per second
        frame_time: Frame time (ms)
        gpu_util: GPU utilization (0-100)
        cpu_util: CPU utilization (0-100)
        temperature: GPU temperature (°C)
        memory_usage: Memory usage (MB)
    """
    timestamp: float
    fps: float
    frame_time: float
    gpu_util: float = 0.0
    cpu_util: float = 0.0
    temperature: float = 0.0
    memory_usage: float = 0.0


@dataclass
class SessionEvent:
    """Session event
    
    Attributes:
        timestamp: Time since session start (s)
        event_type: Event type (e.g., 'quality_change', 'thermal_throttle')
        data: Event data
    """
    timestamp: float
    event_type: str
    data: Dict[str, Any]


@dataclass
class SessionSummary:
    """Session summary statistics
    
    Attributes:
        session_id: Session identifier
        duration: Session duration (s)
        total_frames: Total frames recorded
        avg_fps: Average FPS
        min_fps: Minimum FPS
        max_fps: Maximum FPS
        fps_1_percent: 1% low FPS
        fps_01_percent: 0.1% low FPS
        avg_frame_time: Average frame time (ms)
        avg_gpu_util: Average GPU utilization
        avg_cpu_util: Average CPU utilization
        max_temperature: Maximum temperature
        quality_changes: Number of quality changes
        thermal_events: Number of thermal events
    """
    session_id: str
    duration: float
    total_frames: int
    avg_fps: float
    min_fps: float
    max_fps: float
    fps_1_percent: float
    fps_01_percent: float
    avg_frame_time: float
    avg_gpu_util: float
    avg_cpu_util: float
    max_temperature: float
    quality_changes: int
    thermal_events: int


class Session:
    """Analytics session
    
    v0.3.5d_package3.4b
    
    Tracks performance metrics and events for a recording session.
    
    Example:
        >>> session = Session("test_session")
        >>> session.start()
        >>> 
        >>> session.record_frame(fps=60.5, frame_time=16.5)
        >>> session.record_event("quality_change", {"quality": "balanced"})
        >>> 
        >>> session.stop()
        >>> summary = session.get_summary()
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize session
        
        Args:
            session_id: Optional session ID (auto-generated if None)
        """
        if session_id is None:
            # Auto-generate ID: YYYYMMdd_HHmmSS
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.session_id = session_id
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Data storage
        self.metrics: List[FrameMetric] = []
        self.events: List[SessionEvent] = []
        
        # Metadata
        self.metadata: Dict[str, Any] = {}
        
        self._running = False
    
    def start(self):
        """Start session recording
        
        Example:
            >>> session.start()
        """
        if self._running:
            print(f"[Session {self.session_id}] Already running")
            return
        
        self.start_time = time.perf_counter()
        self._running = True
        
        print(f"[Session {self.session_id}] Started")
    
    def stop(self):
        """Stop session recording
        
        Example:
            >>> session.stop()
        """
        if not self._running:
            return
        
        self.end_time = time.perf_counter()
        self._running = False
        
        duration = self.get_duration()
        print(f"[Session {self.session_id}] Stopped (duration: {duration:.1f}s)")
    
    def record_frame(self, fps: float, frame_time: float, **kwargs):
        """Record frame metrics
        
        Args:
            fps: Current FPS
            frame_time: Frame time (ms)
            **kwargs: Additional metrics (gpu_util, cpu_util, etc.)
        
        Example:
            >>> session.record_frame(fps=60.5, frame_time=16.5, gpu_util=85.2)
        """
        if not self._running:
            return
        
        timestamp = time.perf_counter() - self.start_time
        
        metric = FrameMetric(
            timestamp=timestamp,
            fps=fps,
            frame_time=frame_time,
            gpu_util=kwargs.get('gpu_util', 0.0),
            cpu_util=kwargs.get('cpu_util', 0.0),
            temperature=kwargs.get('temperature', 0.0),
            memory_usage=kwargs.get('memory_usage', 0.0),
        )
        
        self.metrics.append(metric)
    
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Record event
        
        Args:
            event_type: Event type
            data: Event data
        
        Example:
            >>> session.record_event("quality_change", {"quality": "balanced"})
        """
        if not self._running:
            return
        
        timestamp = time.perf_counter() - self.start_time
        
        event = SessionEvent(
            timestamp=timestamp,
            event_type=event_type,
            data=data
        )
        
        self.events.append(event)
    
    def set_metadata(self, key: str, value: Any):
        """Set session metadata
        
        Args:
            key: Metadata key
            value: Metadata value
        
        Example:
            >>> session.set_metadata("power_mode", "balanced")
        """
        self.metadata[key] = value
    
    def get_duration(self) -> float:
        """Get session duration
        
        Returns:
            Duration in seconds
        
        Example:
            >>> duration = session.get_duration()
        """
        if self.start_time is None:
            return 0.0
        
        if self.end_time is not None:
            return self.end_time - self.start_time
        
        return time.perf_counter() - self.start_time
    
    def get_summary(self) -> SessionSummary:
        """Get session summary
        
        Returns:
            Session summary with statistics
        
        Example:
            >>> summary = session.get_summary()
            >>> print(f"Avg FPS: {summary.avg_fps:.1f}")
        """
        import numpy as np
        
        if not self.metrics:
            return SessionSummary(
                session_id=self.session_id,
                duration=0.0,
                total_frames=0,
                avg_fps=0.0,
                min_fps=0.0,
                max_fps=0.0,
                fps_1_percent=0.0,
                fps_01_percent=0.0,
                avg_frame_time=0.0,
                avg_gpu_util=0.0,
                avg_cpu_util=0.0,
                max_temperature=0.0,
                quality_changes=0,
                thermal_events=0,
            )
        
        # Extract FPS values
        fps_values = [m.fps for m in self.metrics]
        frame_times = [m.frame_time for m in self.metrics]
        gpu_utils = [m.gpu_util for m in self.metrics]
        cpu_utils = [m.cpu_util for m in self.metrics]
        temps = [m.temperature for m in self.metrics]
        
        # Calculate percentiles
        fps_sorted = sorted(fps_values)
        fps_1_percent = fps_sorted[max(0, int(len(fps_sorted) * 0.01))]
        fps_01_percent = fps_sorted[max(0, int(len(fps_sorted) * 0.001))]
        
        # Count events
        quality_changes = sum(1 for e in self.events if e.event_type == 'quality_change')
        thermal_events = sum(1 for e in self.events if e.event_type == 'thermal_throttle')
        
        return SessionSummary(
            session_id=self.session_id,
            duration=self.get_duration(),
            total_frames=len(self.metrics),
            avg_fps=np.mean(fps_values),
            min_fps=min(fps_values),
            max_fps=max(fps_values),
            fps_1_percent=fps_1_percent,
            fps_01_percent=fps_01_percent,
            avg_frame_time=np.mean(frame_times),
            avg_gpu_util=np.mean(gpu_utils) if gpu_utils else 0.0,
            avg_cpu_util=np.mean(cpu_utils) if cpu_utils else 0.0,
            max_temperature=max(temps) if temps else 0.0,
            quality_changes=quality_changes,
            thermal_events=thermal_events,
        )


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("Session v0.3.5d_package3.4b Test")
    print("="*60)
    
    session = Session("test_session")
    
    print("\n[Test 1] Start session")
    session.start()
    
    print("\n[Test 2] Record frames")
    import numpy as np
    for i in range(100):
        fps = 60 + np.random.normal(0, 2)
        frame_time = 1000 / fps
        session.record_frame(
            fps=fps,
            frame_time=frame_time,
            gpu_util=85 + np.random.normal(0, 5),
            cpu_util=60 + np.random.normal(0, 3),
            temperature=75 + np.random.normal(0, 2)
        )
    print(f"  Recorded {len(session.metrics)} frames")
    
    print("\n[Test 3] Record events")
    session.record_event("quality_change", {"quality": "balanced"})
    session.record_event("thermal_throttle", {"temperature": 92})
    print(f"  Recorded {len(session.events)} events")
    
    print("\n[Test 4] Set metadata")
    session.set_metadata("power_mode", "balanced")
    session.set_metadata("resolution", "1920x1080")
    
    print("\n[Test 5] Stop session")
    session.stop()
    
    print("\n[Test 6] Get summary")
    summary = session.get_summary()
    print(f"  Duration: {summary.duration:.1f}s")
    print(f"  Total frames: {summary.total_frames}")
    print(f"  Avg FPS: {summary.avg_fps:.1f}")
    print(f"  Min FPS: {summary.min_fps:.1f}")
    print(f"  Max FPS: {summary.max_fps:.1f}")
    print(f"  1% Low: {summary.fps_1_percent:.1f}")
    print(f"  Quality changes: {summary.quality_changes}")
    
    print("\n" + "="*60)
    print("✅ Session - All Tests Passed!")
    print("="*60)
