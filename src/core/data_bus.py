#!/usr/bin/env python3
"""Performance Data Bus

Version: 0.3.5d (package 3.9a, stage 3/3)

Event-based data transport system using pub/sub pattern.

Package 3.9a Stage 3: New component for improved data transport.
"""
import threading
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
import weakref


@dataclass
class DataEvent:
    """Data event"""
    name: str
    data: Any
    timestamp: float


class PerformanceDataBus:
    """Performance Data Bus (Singleton)
    
    Event-based data transport using pub/sub pattern.
    Decouples components and reduces duplicate data collection.
    
    Features:
    - Subscribe to data events
    - Publish data to subscribers
    - Cached data access
    - Weak references to prevent memory leaks
    - Thread-safe operations
    """
    
    _instance: Optional['PerformanceDataBus'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._subscribers: Dict[str, List[weakref.ref]] = {}
        self._cache: Dict[str, Any] = {}
        self._data_lock = threading.RLock()
        print("[DataBus] Initialized")
    
    @classmethod
    def get_instance(cls) -> 'PerformanceDataBus':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def subscribe(self, event: str, callback: Callable[[Any], None]):
        """Subscribe to data updates
        
        Args:
            event: Event name (e.g., 'performance_metrics', 'thermal_state')
            callback: Function to call when event is published
        """
        with self._data_lock:
            if event not in self._subscribers:
                self._subscribers[event] = []
            
            # Use weak reference to prevent memory leaks
            callback_ref = weakref.ref(callback)
            self._subscribers[event].append(callback_ref)
            
            print(f"[DataBus] Subscribed to '{event}' (total: {len(self._subscribers[event])})")
    
    def unsubscribe(self, event: str, callback: Callable[[Any], None]):
        """Unsubscribe from data updates
        
        Args:
            event: Event name
            callback: Callback to remove
        """
        with self._data_lock:
            if event not in self._subscribers:
                return
            
            # Remove matching callbacks
            self._subscribers[event] = [
                ref for ref in self._subscribers[event]
                if ref() is not None and ref() != callback
            ]
            
            print(f"[DataBus] Unsubscribed from '{event}'")
    
    def publish(self, event: str, data: Any):
        """Publish data to subscribers
        
        Args:
            event: Event name
            data: Data to publish
        """
        with self._data_lock:
            # Update cache
            self._cache[event] = data
            
            # Notify subscribers
            if event in self._subscribers:
                alive_subscribers = []
                
                for callback_ref in self._subscribers[event]:
                    callback = callback_ref()
                    
                    if callback is not None:
                        try:
                            callback(data)
                            alive_subscribers.append(callback_ref)
                        except Exception as e:
                            print(f"[DataBus] Callback error for '{event}': {e}")
                    # If callback is None, it was garbage collected
                
                # Update subscribers list (remove dead refs)
                self._subscribers[event] = alive_subscribers
    
    def get(self, event: str) -> Optional[Any]:
        """Get cached data
        
        Args:
            event: Event name
        
        Returns:
            Cached data or None if not available
        """
        with self._data_lock:
            return self._cache.get(event)
    
    def has(self, event: str) -> bool:
        """Check if event has cached data
        
        Args:
            event: Event name
        
        Returns:
            True if data is cached
        """
        with self._data_lock:
            return event in self._cache
    
    def clear(self, event: Optional[str] = None):
        """Clear cached data
        
        Args:
            event: Event name to clear, or None to clear all
        """
        with self._data_lock:
            if event is None:
                self._cache.clear()
                print("[DataBus] Cleared all cached data")
            elif event in self._cache:
                del self._cache[event]
                print(f"[DataBus] Cleared '{event}'")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get data bus statistics
        
        Returns:
            Statistics dictionary
        """
        with self._data_lock:
            return {
                'events': list(self._cache.keys()),
                'subscriber_count': {
                    event: len(subs)
                    for event, subs in self._subscribers.items()
                },
                'cache_size': len(self._cache),
            }
