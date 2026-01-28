#!/usr/bin/env python3
"""Analytics & Telemetry System

Version: 0.3.5d_package3.4b

Performance analytics and telemetry for PartMart Boost.

Components:
- engine: Analytics engine for data collection
- session: Session recording and management
- export: Data export (CSV, JSON)
- stats: Statistical analysis

Example:
    >>> from analytics import AnalyticsEngine
    >>> 
    >>> analytics = AnalyticsEngine()
    >>> analytics.start_session("test_session")
    >>> 
    >>> # Record data
    >>> analytics.record_frame(fps=60.5, frame_time=16.5)
    >>> 
    >>> # Export data
    >>> analytics.export_csv("session_data.csv")
    >>> analytics.export_json("session_data.json")
"""

from .engine import AnalyticsEngine
from .session import Session, SessionSummary
from .export import export_to_csv, export_to_json

__version__ = "0.3.5d_package3.4b"
__all__ = [
    'AnalyticsEngine',
    'Session',
    'SessionSummary',
    'export_to_csv',
    'export_to_json',
]
