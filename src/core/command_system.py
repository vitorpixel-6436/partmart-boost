#!/usr/bin/env python3
"""Command System

Version: 0.3.5e (package 3.9a, stage 7.3/7.7)

Package 3.9a Stage 7.3: Command classes for frontend integration.

Features:
- Command base class
- Command result
- Built-in commands
- Extensible architecture
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid


@dataclass
class Command:
    """Base command class
    
    All commands inherit from this class.
    
    Attributes:
        name: Command name
        params: Command parameters
        request_id: Unique request ID
        timestamp: Creation timestamp
    """
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


@dataclass
class CommandResult:
    """Command execution result
    
    Attributes:
        request_id: Request ID (matches command)
        success: Whether command succeeded
        data: Result data (optional)
        error: Error message (if failed)
        execution_time_ms: Execution time in milliseconds
    """
    request_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


# ============================================================================
# Built-in Commands
# ============================================================================

class StartMonitoringCommand(Command):
    """Start performance monitoring
    
    Params:
        interval: Update interval in milliseconds (default: 100)
    
    Example:
        >>> command = StartMonitoringCommand(interval=100)
        >>> result = bridge.execute_command(command)
    """
    
    def __init__(self, interval: int = 100):
        super().__init__(
            name='start_monitoring',
            params={'interval': interval}
        )


class StopMonitoringCommand(Command):
    """Stop performance monitoring
    
    Example:
        >>> command = StopMonitoringCommand()
        >>> result = bridge.execute_command(command)
    """
    
    def __init__(self):
        super().__init__(
            name='stop_monitoring',
            params={}
        )


class GetMetricsCommand(Command):
    """Get current performance metrics
    
    Example:
        >>> command = GetMetricsCommand()
        >>> result = bridge.execute_command(command)
        >>> metrics = result.data
    """
    
    def __init__(self):
        super().__init__(
            name='get_metrics',
            params={}
        )


class ClearHistoryCommand(Command):
    """Clear performance history
    
    Example:
        >>> command = ClearHistoryCommand()
        >>> result = bridge.execute_command(command)
    """
    
    def __init__(self):
        super().__init__(
            name='clear_history',
            params={}
        )


class ResetBaselineCommand(Command):
    """Reset performance baseline
    
    Example:
        >>> command = ResetBaselineCommand()
        >>> result = bridge.execute_command(command)
    """
    
    def __init__(self):
        super().__init__(
            name='reset_baseline',
            params={}
        )


# ============================================================================
# Command Registry
# ============================================================================

COMMAND_REGISTRY = {
    'start_monitoring': StartMonitoringCommand,
    'stop_monitoring': StopMonitoringCommand,
    'get_metrics': GetMetricsCommand,
    'clear_history': ClearHistoryCommand,
    'reset_baseline': ResetBaselineCommand,
}


def get_command_class(name: str):
    """Get command class by name
    
    Args:
        name: Command name
    
    Returns:
        Command class or None
    """
    return COMMAND_REGISTRY.get(name)
