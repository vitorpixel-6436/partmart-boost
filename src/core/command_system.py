#!/usr/bin/env python3
"""Command System

Version: 0.3.5d (package 3.9a, stage 6/6)

Structured command pattern for backend operations.

Package 3.9a Stage 6: Command system for backend-frontend communication.

Features:
- Type-safe commands
- Parameter validation
- Command history
- Undo/redo support (future)
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time

from backend_bridge import Command, CommandResult


# ============================================================================
# COMMAND DEFINITIONS
# ============================================================================

@dataclass
class StartMonitoringCommand(Command):
    """Start performance monitoring"""
    
    def __init__(self, interval: int = 100, metrics: Optional[list] = None):
        super().__init__(
            command_type='start_monitoring',
            params={
                'interval': interval,
                'metrics': metrics or ['cpu', 'gpu', 'memory', 'fps'],
            }
        )


@dataclass
class StopMonitoringCommand(Command):
    """Stop performance monitoring"""
    
    def __init__(self):
        super().__init__(command_type='stop_monitoring')


@dataclass
class UpdateSettingsCommand(Command):
    """Update application settings"""
    
    def __init__(self, settings: Dict[str, Any]):
        super().__init__(
            command_type='update_settings',
            params={'settings': settings}
        )


@dataclass
class InstallOptiScalerCommand(Command):
    """Install OptiScaler"""
    
    def __init__(self, version: Optional[str] = None, force: bool = False):
        super().__init__(
            command_type='install_optiscaler',
            params={
                'version': version,
                'force': force,
            }
        )


@dataclass
class UninstallOptiScalerCommand(Command):
    """Uninstall OptiScaler"""
    
    def __init__(self):
        super().__init__(command_type='uninstall_optiscaler')


@dataclass
class GetMetricsCommand(Command):
    """Get performance metrics"""
    
    def __init__(self, time_range: Optional[str] = None, limit: int = 100):
        super().__init__(
            command_type='get_metrics',
            params={
                'time_range': time_range,
                'limit': limit,
            }
        )


@dataclass
class ClearHistoryCommand(Command):
    """Clear performance history"""
    
    def __init__(self):
        super().__init__(command_type='clear_history')


@dataclass
class ExportDataCommand(Command):
    """Export performance data"""
    
    def __init__(self, file_path: str, format: str = 'csv'):
        super().__init__(
            command_type='export_data',
            params={
                'file_path': file_path,
                'format': format,
            }
        )


@dataclass
class ApplyProfileCommand(Command):
    """Apply performance profile"""
    
    def __init__(self, profile_name: str):
        super().__init__(
            command_type='apply_profile',
            params={'profile_name': profile_name}
        )


# ============================================================================
# COMMAND VALIDATOR
# ============================================================================

class CommandValidator:
    """Validate command parameters"""
    
    @staticmethod
    def validate(command: Command) -> tuple[bool, Optional[str]]:
        """Validate command
        
        Args:
            command: Command to validate
        
        Returns:
            (valid, error_message)
        """
        if command.command_type == 'start_monitoring':
            return CommandValidator._validate_start_monitoring(command)
        
        elif command.command_type == 'update_settings':
            return CommandValidator._validate_update_settings(command)
        
        elif command.command_type == 'install_optiscaler':
            return CommandValidator._validate_install_optiscaler(command)
        
        elif command.command_type == 'export_data':
            return CommandValidator._validate_export_data(command)
        
        # Default: valid
        return True, None
    
    @staticmethod
    def _validate_start_monitoring(command: Command) -> tuple[bool, Optional[str]]:
        """Validate start monitoring command"""
        interval = command.params.get('interval', 100)
        
        if not isinstance(interval, int):
            return False, "Interval must be integer"
        
        if interval < 10 or interval > 10000:
            return False, "Interval must be between 10 and 10000 ms"
        
        return True, None
    
    @staticmethod
    def _validate_update_settings(command: Command) -> tuple[bool, Optional[str]]:
        """Validate update settings command"""
        settings = command.params.get('settings')
        
        if not isinstance(settings, dict):
            return False, "Settings must be dictionary"
        
        return True, None
    
    @staticmethod
    def _validate_install_optiscaler(command: Command) -> tuple[bool, Optional[str]]:
        """Validate install OptiScaler command"""
        version = command.params.get('version')
        
        if version is not None and not isinstance(version, str):
            return False, "Version must be string"
        
        return True, None
    
    @staticmethod
    def _validate_export_data(command: Command) -> tuple[bool, Optional[str]]:
        """Validate export data command"""
        file_path = command.params.get('file_path')
        format = command.params.get('format', 'csv')
        
        if not isinstance(file_path, str):
            return False, "File path must be string"
        
        if format not in ['csv', 'json', 'xlsx']:
            return False, "Format must be csv, json, or xlsx"
        
        return True, None
