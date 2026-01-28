#!/usr/bin/env python3
"""Analytics Engine

Version: 0.3.5d_package3.4b

Main analytics engine for PartMart Boost.

Features:
- Session management
- Data collection
- Export handling
- Statistical analysis
"""
from typing import Optional, Dict, Any
from pathlib import Path

from .session import Session, SessionSummary
from .export import export_to_csv, export_to_json


class AnalyticsEngine:
    """Analytics Engine
    
    v0.3.5d_package3.4b - Performance Analytics
    
    Main engine for collecting and analyzing performance data.
    Manages sessions, records metrics, and exports data.
    
    Example:
        >>> engine = AnalyticsEngine()
        >>> 
        >>> # Start recording
        >>> engine.start_session("gameplay_session")
        >>> engine.set_metadata("power_mode", "balanced")
        >>> 
        >>> # Record data
        >>> engine.record_frame(fps=60.5, frame_time=16.5, gpu_util=85.2)
        >>> 
        >>> # Export
        >>> engine.stop_session()
        >>> engine.export_csv("data/session.csv")
        >>> engine.export_json("data/session.json")
    """
    
    def __init__(self, output_dir: str = "analytics_data"):
        """Initialize analytics engine
        
        Args:
            output_dir: Directory for exported data
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        
        self._current_session: Optional[Session] = None
        self._sessions: Dict[str, Session] = {}
        
        print(f"[AnalyticsEngine v0.3.5d_package3.4b] Initialized")
        print(f"  Output directory: {self._output_dir}")
    
    # === SESSION MANAGEMENT ===
    
    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start new analytics session
        
        Args:
            session_id: Optional session ID (auto-generated if None)
        
        Returns:
            Session ID
        
        Example:
            >>> session_id = engine.start_session("test_session")
        """
        # Stop current session if running
        if self._current_session and self._current_session._running:
            self.stop_session()
        
        # Create new session
        session = Session(session_id)
        session.start()
        
        self._current_session = session
        self._sessions[session.session_id] = session
        
        print(f"[AnalyticsEngine] Session started: {session.session_id}")
        return session.session_id
    
    def stop_session(self):
        """Stop current session
        
        Example:
            >>> engine.stop_session()
        """
        if self._current_session is None:
            print("[AnalyticsEngine] No active session")
            return
        
        self._current_session.stop()
        print(f"[AnalyticsEngine] Session stopped: {self._current_session.session_id}")
    
    def get_current_session(self) -> Optional[Session]:
        """Get current active session
        
        Returns:
            Current session or None
        """
        return self._current_session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID
        
        Args:
            session_id: Session ID
        
        Returns:
            Session or None
        
        Example:
            >>> session = engine.get_session("test_session")
        """
        return self._sessions.get(session_id)
    
    # === DATA RECORDING ===
    
    def record_frame(self, fps: float, frame_time: float, **kwargs):
        """Record frame metrics
        
        Args:
            fps: Current FPS
            frame_time: Frame time (ms)
            **kwargs: Additional metrics
        
        Example:
            >>> engine.record_frame(fps=60.5, frame_time=16.5, gpu_util=85.2)
        """
        if self._current_session is None:
            return
        
        self._current_session.record_frame(fps, frame_time, **kwargs)
    
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """Record event
        
        Args:
            event_type: Event type
            data: Event data
        
        Example:
            >>> engine.record_event("quality_change", {"quality": "balanced"})
        """
        if self._current_session is None:
            return
        
        self._current_session.record_event(event_type, data)
    
    def set_metadata(self, key: str, value: Any):
        """Set session metadata
        
        Args:
            key: Metadata key
            value: Metadata value
        
        Example:
            >>> engine.set_metadata("power_mode", "balanced")
        """
        if self._current_session is None:
            return
        
        self._current_session.set_metadata(key, value)
    
    # === EXPORT ===
    
    def export_csv(self, filename: Optional[str] = None):
        """Export current session to CSV
        
        Args:
            filename: Output filename (auto-generated if None)
        
        Example:
            >>> engine.export_csv("session_data.csv")
        """
        if self._current_session is None:
            print("[AnalyticsEngine] No active session to export")
            return
        
        if filename is None:
            filename = f"{self._current_session.session_id}.csv"
        
        filepath = self._output_dir / filename
        export_to_csv(self._current_session, str(filepath))
    
    def export_json(self, filename: Optional[str] = None):
        """Export current session to JSON
        
        Args:
            filename: Output filename (auto-generated if None)
        
        Example:
            >>> engine.export_json("session_data.json")
        """
        if self._current_session is None:
            print("[AnalyticsEngine] No active session to export")
            return
        
        if filename is None:
            filename = f"{self._current_session.session_id}.json"
        
        filepath = self._output_dir / filename
        export_to_json(self._current_session, str(filepath))
    
    # === ANALYSIS ===
    
    def get_summary(self) -> Optional[SessionSummary]:
        """Get current session summary
        
        Returns:
            Session summary or None
        
        Example:
            >>> summary = engine.get_summary()
            >>> print(f"Avg FPS: {summary.avg_fps:.1f}")
        """
        if self._current_session is None:
            return None
        
        return self._current_session.get_summary()
    
    def print_summary(self):
        """Print current session summary
        
        Example:
            >>> engine.print_summary()
        """
        summary = self.get_summary()
        if summary is None:
            print("[AnalyticsEngine] No active session")
            return
        
        print("\n" + "="*60)
        print(f"Session Summary: {summary.session_id}")
        print("="*60)
        print(f"Duration: {summary.duration:.1f}s")
        print(f"Total Frames: {summary.total_frames}")
        print(f"\nFPS Statistics:")
        print(f"  Average: {summary.avg_fps:.1f}")
        print(f"  Minimum: {summary.min_fps:.1f}")
        print(f"  Maximum: {summary.max_fps:.1f}")
        print(f"  1% Low: {summary.fps_1_percent:.1f}")
        print(f"  0.1% Low: {summary.fps_01_percent:.1f}")
        print(f"\nUtilization:")
        print(f"  GPU: {summary.avg_gpu_util:.1f}%")
        print(f"  CPU: {summary.avg_cpu_util:.1f}%")
        print(f"\nTemperature:")
        print(f"  Max: {summary.max_temperature:.1f}°C")
        print(f"\nEvents:")
        print(f"  Quality Changes: {summary.quality_changes}")
        print(f"  Thermal Throttles: {summary.thermal_events}")
        print("="*60)


# ========== TESTING ==========

if __name__ == "__main__":
    import numpy as np
    import time
    
    print("="*60)
    print("AnalyticsEngine v0.3.5d_package3.4b Test")
    print("="*60)
    
    engine = AnalyticsEngine(output_dir="test_analytics")
    
    print("\n[Test 1] Start session")
    session_id = engine.start_session("test_session")
    print(f"  Session ID: {session_id}")
    
    print("\n[Test 2] Set metadata")
    engine.set_metadata("power_mode", "balanced")
    engine.set_metadata("resolution", "1920x1080")
    
    print("\n[Test 3] Record frames")
    for i in range(100):
        fps = 60 + np.random.normal(0, 3)
        frame_time = 1000 / fps
        engine.record_frame(
            fps=fps,
            frame_time=frame_time,
            gpu_util=85 + np.random.normal(0, 5),
            cpu_util=60 + np.random.normal(0, 3),
            temperature=75 + np.random.normal(0, 2)
        )
    print(f"  Recorded 100 frames")
    
    print("\n[Test 4] Record events")
    engine.record_event("quality_change", {"quality": "balanced"})
    engine.record_event("thermal_throttle", {"temperature": 92})
    
    print("\n[Test 5] Get summary")
    engine.print_summary()
    
    print("\n[Test 6] Export data")
    engine.export_csv()
    engine.export_json()
    
    print("\n[Test 7] Stop session")
    engine.stop_session()
    
    print("\n" + "="*60)
    print("✅ AnalyticsEngine - All Tests Passed!")
    print("="*60)
