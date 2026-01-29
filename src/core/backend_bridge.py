#!/usr/bin/env python3
"""Backend Bridge

Version: 0.3.5d (package 3.9a, stage 6/6)

Unified communication layer between backend and frontend.

Package 3.9a Stage 6: New backend-frontend bridge.

Features:
- Command execution
- Query processing
- Event subscription
- Error handling
- Request/response validation
- Operation history
"""
import time
import uuid
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Command:
    """Base command"""
    command_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.perf_counter)
    status: CommandStatus = CommandStatus.PENDING


@dataclass
class CommandResult:
    """Command execution result"""
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.perf_counter)


@dataclass
class QueryResult:
    """Query result"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    row_count: int = 0
    execution_time: float = 0.0


class BackendBridge:
    """Backend-Frontend Communication Bridge
    
    Unified API layer for all backend-frontend communication.
    
    Features:
    - Command execution (backend operations)
    - Query processing (data retrieval)
    - Event subscription (notifications)
    - Error handling
    - Request validation
    - Operation tracking
    
    Usage:
        bridge = BackendBridge.get_instance()
        
        # Execute command
        command = Command('start_monitoring', {'interval': 100})
        result = bridge.execute_command(command)
        
        # Query data
        result = bridge.query_data('performance_metrics', {})
        
        # Subscribe to events
        bridge.subscribe('metrics_updated', callback)
    """
    
    _instance: Optional['BackendBridge'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize backend bridge"""
        # Command handlers
        self._command_handlers: Dict[str, Callable] = {}
        
        # Query handlers
        self._query_handlers: Dict[str, Callable] = {}
        
        # Event subscribers
        self._event_subscribers: Dict[str, List[Callable]] = {}
        
        # Command history (circular buffer)
        self._command_history: deque = deque(maxlen=1000)
        
        # Statistics
        self._stats = {
            'commands_executed': 0,
            'commands_failed': 0,
            'queries_executed': 0,
            'queries_failed': 0,
            'events_published': 0,
        }
        
        # Qt signal bridge (lazy loaded)
        self._qt_signals = None
        
        print("[BackendBridge] Initialized (Stage 6)")
    
    @classmethod
    def get_instance(cls) -> 'BackendBridge':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def register_command_handler(self,
                                 command_type: str,
                                 handler: Callable[[Command], CommandResult]):
        """Register command handler
        
        Args:
            command_type: Command type to handle
            handler: Handler function
        """
        self._command_handlers[command_type] = handler
        print(f"[BackendBridge] Registered handler: {command_type}")
    
    def register_query_handler(self,
                              query_type: str,
                              handler: Callable[[Dict[str, Any]], QueryResult]):
        """Register query handler
        
        Args:
            query_type: Query type to handle
            handler: Handler function
        """
        self._query_handlers[query_type] = handler
        print(f"[BackendBridge] Registered query: {query_type}")
    
    def execute_command(self, command: Command) -> CommandResult:
        """Execute backend command
        
        Args:
            command: Command to execute
        
        Returns:
            Command result
        """
        start_time = time.perf_counter()
        
        try:
            # Update status
            command.status = CommandStatus.RUNNING
            
            # Get handler
            handler = self._command_handlers.get(command.command_type)
            
            if handler is None:
                raise ValueError(f"No handler for command: {command.command_type}")
            
            # Execute
            result = handler(command)
            
            # Update status
            command.status = CommandStatus.COMPLETED if result.success else CommandStatus.FAILED
            
            # Calculate execution time
            result.execution_time = time.perf_counter() - start_time
            
            # Update stats
            self._stats['commands_executed'] += 1
            if not result.success:
                self._stats['commands_failed'] += 1
            
            # Add to history
            self._command_history.append((command, result))
            
            # Publish event
            self.publish_event('command_completed', {
                'request_id': command.request_id,
                'command_type': command.command_type,
                'success': result.success,
            })
            
            return result
        
        except Exception as e:
            # Error handling
            command.status = CommandStatus.FAILED
            
            result = CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e),
                execution_time=time.perf_counter() - start_time
            )
            
            self._stats['commands_failed'] += 1
            
            # Publish error event
            self.publish_event('command_failed', {
                'request_id': command.request_id,
                'command_type': command.command_type,
                'error': str(e),
            })
            
            return result
    
    def query_data(self, query_type: str, params: Dict[str, Any]) -> QueryResult:
        """Query backend data
        
        Args:
            query_type: Type of query
            params: Query parameters
        
        Returns:
            Query result
        """
        start_time = time.perf_counter()
        
        try:
            # Get handler
            handler = self._query_handlers.get(query_type)
            
            if handler is None:
                raise ValueError(f"No handler for query: {query_type}")
            
            # Execute
            result = handler(params)
            
            # Calculate execution time
            result.execution_time = time.perf_counter() - start_time
            
            # Update stats
            self._stats['queries_executed'] += 1
            if not result.success:
                self._stats['queries_failed'] += 1
            
            return result
        
        except Exception as e:
            self._stats['queries_failed'] += 1
            
            return QueryResult(
                success=False,
                error=str(e),
                execution_time=time.perf_counter() - start_time
            )
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to backend events
        
        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type not in self._event_subscribers:
            self._event_subscribers[event_type] = []
        
        self._event_subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from events
        
        Args:
            event_type: Event type
            callback: Callback function
        """
        if event_type in self._event_subscribers:
            try:
                self._event_subscribers[event_type].remove(callback)
            except ValueError:
                pass
    
    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to subscribers
        
        Args:
            event_type: Event type
            data: Event data
        """
        # Call subscribers
        subscribers = self._event_subscribers.get(event_type, [])
        
        for callback in subscribers:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"[BackendBridge] Subscriber error: {e}")
        
        # Emit Qt signal if available
        if self._qt_signals is not None:
            try:
                self._qt_signals.event_published.emit(event_type, data)
            except Exception as e:
                print(f"[BackendBridge] Qt signal error: {e}")
        
        self._stats['events_published'] += 1
    
    def publish_data(self, data_type: str, data: Any):
        """Publish data update
        
        Args:
            data_type: Type of data
            data: Data to publish
        """
        self.publish_event('data_updated', {
            'data_type': data_type,
            'data': data,
            'timestamp': time.perf_counter(),
        })
        
        # Emit Qt signal if available
        if self._qt_signals is not None:
            try:
                self._qt_signals.data_updated.emit(data_type, data)
            except Exception as e:
                print(f"[BackendBridge] Qt signal error: {e}")
    
    def set_qt_signals(self, qt_signals):
        """Set Qt signal bridge
        
        Args:
            qt_signals: QtSignalBridge instance
        """
        self._qt_signals = qt_signals
        print("[BackendBridge] Qt signals connected")
    
    @property
    def qt_signals(self):
        """Get Qt signal bridge"""
        return self._qt_signals
    
    def get_command_history(self, limit: int = 100) -> List[tuple]:
        """Get command history
        
        Args:
            limit: Maximum number of commands
        
        Returns:
            List of (command, result) tuples
        """
        return list(self._command_history)[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics
        
        Returns:
            Statistics dictionary
        """
        return self._stats.copy()
    
    def clear_history(self):
        """Clear command history"""
        self._command_history.clear()
