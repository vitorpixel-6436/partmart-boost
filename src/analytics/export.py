#!/usr/bin/env python3
"""Data Export

Version: 0.3.5d_package3.4b

Export analytics data to various formats.

Formats:
- CSV: Time-series data
- JSON: Structured data with summary
"""
import json
import csv
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .session import Session


def export_to_csv(session: 'Session', filepath: str):
    """Export session data to CSV
    
    Args:
        session: Session to export
        filepath: Output CSV file path
    
    Example:
        >>> export_to_csv(session, "session_data.csv")
    """
    if not session.metrics:
        print(f"[Export] No data to export")
        return
    
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'timestamp',
            'fps',
            'frame_time',
            'gpu_util',
            'cpu_util',
            'temperature',
            'memory_usage',
        ])
        
        # Data
        for metric in session.metrics:
            writer.writerow([
                f"{metric.timestamp:.3f}",
                f"{metric.fps:.2f}",
                f"{metric.frame_time:.2f}",
                f"{metric.gpu_util:.1f}",
                f"{metric.cpu_util:.1f}",
                f"{metric.temperature:.1f}",
                f"{metric.memory_usage:.1f}",
            ])
    
    print(f"[Export] Exported to CSV: {filepath}")
    print(f"  Frames: {len(session.metrics)}")


def export_to_json(session: 'Session', filepath: str):
    """Export session data to JSON
    
    Args:
        session: Session to export
        filepath: Output JSON file path
    
    Example:
        >>> export_to_json(session, "session_data.json")
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Get summary
    summary = session.get_summary()
    
    # Build JSON structure
    data = {
        'session_id': session.session_id,
        'start_time': session.start_time,
        'end_time': session.end_time,
        'duration': summary.duration,
        'metadata': session.metadata,
        'summary': {
            'total_frames': summary.total_frames,
            'avg_fps': round(summary.avg_fps, 2),
            'min_fps': round(summary.min_fps, 2),
            'max_fps': round(summary.max_fps, 2),
            'fps_1_percent': round(summary.fps_1_percent, 2),
            'fps_01_percent': round(summary.fps_01_percent, 2),
            'avg_frame_time': round(summary.avg_frame_time, 2),
            'avg_gpu_util': round(summary.avg_gpu_util, 1),
            'avg_cpu_util': round(summary.avg_cpu_util, 1),
            'max_temperature': round(summary.max_temperature, 1),
            'quality_changes': summary.quality_changes,
            'thermal_events': summary.thermal_events,
        },
        'metrics': [
            {
                'timestamp': round(m.timestamp, 3),
                'fps': round(m.fps, 2),
                'frame_time': round(m.frame_time, 2),
                'gpu_util': round(m.gpu_util, 1),
                'cpu_util': round(m.cpu_util, 1),
                'temperature': round(m.temperature, 1),
                'memory_usage': round(m.memory_usage, 1),
            }
            for m in session.metrics
        ],
        'events': [
            {
                'timestamp': round(e.timestamp, 3),
                'event_type': e.event_type,
                'data': e.data,
            }
            for e in session.events
        ],
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"[Export] Exported to JSON: {filepath}")
    print(f"  Frames: {len(session.metrics)}")
    print(f"  Events: {len(session.events)}")


# ========== TESTING ==========

if __name__ == "__main__":
    from .session import Session
    import numpy as np
    
    print("="*60)
    print("Export v0.3.5d_package3.4b Test")
    print("="*60)
    
    # Create test session
    session = Session("test_export")
    session.start()
    
    for i in range(50):
        session.record_frame(
            fps=60 + np.random.normal(0, 2),
            frame_time=16.67 + np.random.normal(0, 0.5),
            gpu_util=85 + np.random.normal(0, 5)
        )
    
    session.record_event("quality_change", {"quality": "balanced"})
    session.stop()
    
    print("\n[Test 1] Export to CSV")
    export_to_csv(session, "test_data/test_session.csv")
    
    print("\n[Test 2] Export to JSON")
    export_to_json(session, "test_data/test_session.json")
    
    print("\n" + "="*60)
    print("✅ Export - All Tests Passed!")
    print("="*60)
