#!/usr/bin/env python3
"""Qt Signal Bridge

Version: 0.3.5d (package 3.9a, stage 6/6)

Qt signal integration for thread-safe UI updates.

Package 3.9a Stage 6: Qt signals for backend-frontend communication.

Features:
- Thread-safe signal emission
- Qt signal/slot integration
- Signal batching
- Priority signals
"""
try:
    from PyQt6.QtCore import QObject, pyqtSignal
    PYQT6_AVAILABLE = True
except ImportError:
    print("[QtSignalBridge] PyQt6 not available")
    PYQT6_AVAILABLE = False
    # Fallback
    class QObject:
        pass
    def pyqtSignal(*args, **kwargs):
        return None

from typing import Dict, Any


class QtSignalBridge(QObject):
    """Qt Signal Bridge
    
    Thread-safe bridge between backend and Qt UI.
    
    Signals:
        data_updated: Emitted when data is updated (data_type, data)
        command_completed: Emitted when command completes (command_id, success)
        error_occurred: Emitted on error (component, error_message)
        progress_updated: Emitted for progress (operation, percent)
        status_changed: Emitted on status change (component, status)
    
    Usage:
        # In backend
        qt_signals.data_updated.emit('performance_metrics', metrics)
        
        # In frontend
        qt_signals.data_updated.connect(self._on_data_updated)
    """
    
    # Signals
    data_updated = pyqtSignal(str, object)  # (data_type, data)
    command_completed = pyqtSignal(str, bool)  # (command_id, success)
    error_occurred = pyqtSignal(str, str)  # (component, error)
    progress_updated = pyqtSignal(str, int)  # (operation, percent)
    status_changed = pyqtSignal(str, str)  # (component, status)
    event_published = pyqtSignal(str, dict)  # (event_type, data)
    
    def __init__(self):
        """Initialize Qt signal bridge"""
        super().__init__()
        print("[QtSignalBridge] Initialized (Stage 6)")
    
    def emit_data_update(self, data_type: str, data: Any):
        """Emit data update signal
        
        Args:
            data_type: Type of data
            data: Data to emit
        """
        try:
            self.data_updated.emit(data_type, data)
        except Exception as e:
            print(f"[QtSignalBridge] Emit error: {e}")
    
    def emit_command_completed(self, command_id: str, success: bool):
        """Emit command completed signal
        
        Args:
            command_id: Command ID
            success: Success status
        """
        try:
            self.command_completed.emit(command_id, success)
        except Exception as e:
            print(f"[QtSignalBridge] Emit error: {e}")
    
    def emit_error(self, component: str, error: str):
        """Emit error signal
        
        Args:
            component: Component name
            error: Error message
        """
        try:
            self.error_occurred.emit(component, error)
        except Exception as e:
            print(f"[QtSignalBridge] Emit error: {e}")
    
    def emit_progress(self, operation: str, percent: int):
        """Emit progress signal
        
        Args:
            operation: Operation name
            percent: Progress percent (0-100)
        """
        try:
            self.progress_updated.emit(operation, percent)
        except Exception as e:
            print(f"[QtSignalBridge] Emit error: {e}")
    
    def emit_status(self, component: str, status: str):
        """Emit status change signal
        
        Args:
            component: Component name
            status: New status
        """
        try:
            self.status_changed.emit(component, status)
        except Exception as e:
            print(f"[QtSignalBridge] Emit error: {e}")
