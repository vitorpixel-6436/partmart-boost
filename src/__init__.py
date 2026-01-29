#!/usr/bin/env python3
"""PartMart Boost Package

Version: 0.3.5e (package 3.9a, stage 7.1/7.6)

Main package initialization.
"""

__version__ = '0.3.5e'
__package_version__ = '3.9a'
__stage__ = '7.1/7.6'

# Auto-initialize on import
from core.system_init import SystemInitializer, initialize

# Export main classes
try:
    from core.backend_bridge import BackendBridge
    from core.command_system import (
        StartMonitoringCommand,
        StopMonitoringCommand,
        UpdateSettingsCommand,
    )
    from core.query_system import QueryBuilder
except ImportError:
    # Not yet initialized
    pass

# Convenience functions
def get_bridge():
    """Get BackendBridge instance"""
    return SystemInitializer.get_instance().get_bridge()

def get_monitor():
    """Get PerformanceMonitor instance"""
    return SystemInitializer.get_instance().get_monitor()

def get_version():
    """Get version string"""
    return f"{__version__} (Package {__package_version__}, Stage {__stage__})"

print(f"[PartMart Boost] Version {get_version()}")
