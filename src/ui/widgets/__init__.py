#!/usr/bin/env python3
"""UI Widgets Package

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Custom widgets integrated with BackendBridge.
"""

__all__ = [
    'DashboardWidget',
    'SettingsWidget',
]

try:
    from .dashboard_widget import DashboardWidget
    from .settings_widget import SettingsWidget
except ImportError as e:
    print(f"[ui.widgets] Import error: {e}")
