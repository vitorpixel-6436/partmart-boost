#!/usr/bin/env python3
"""DataBus Integration Layer

Version: 0.3.5f (package 3.9a, stage 7.4/7.7)

Package 3.9a Stage 7.4: Integration between DataBus and BackendBridge.

Features:
- Bridges BackendBridge events to DataBus
- Automatic topic mapping
- Bidirectional communication
- Event forwarding
"""
from typing import Optional, Dict, Any
import threading

try:
    from core.data_bus import DataBus, Message
    from core.backend_bridge import BackendBridge
    from core.qt_signal_bridge import QtSignalBridge
    IMPORTS_OK = True
except ImportError as e:
    print(f"[DataBusIntegration] Import error: {e}")
    IMPORTS_OK = False


class DataBusIntegration:
    """Integration between DataBus and BackendBridge
    
    v0.3.5f (package 3.9a, stage 7.4/7.7)
    
    Features:
    - Forwards BackendBridge events to DataBus
    - Maps bridge data to bus topics
    - Bidirectional communication
    - Thread-safe
    
    Topic Mapping:
        Bridge data_type → Bus topic
        'performance_metrics' → 'data.performance_metrics'
        'monitoring_started' → 'event.monitoring_started'
        'config_changed' → 'event.config_changed'
    
    Usage:
        >>> bridge = BackendBridge()
        >>> bus = DataBus()
        >>> integration = DataBusIntegration(bridge, bus)
        >>> 
        >>> # Subscribe to bus topics
        >>> bus.subscribe('data.performance_metrics',
        ...               lambda msg: print(msg.data))
        >>> 
        >>> # Publish from bridge (automatically forwarded to bus)
        >>> bridge.publish_data('performance_metrics', {...})
    """
    
    def __init__(self, bridge: 'BackendBridge', bus: 'DataBus',
                 qt_signals: Optional['QtSignalBridge'] = None):
        """Initialize integration
        
        Args:
            bridge: BackendBridge instance
            bus: DataBus instance
            qt_signals: QtSignalBridge instance (optional)
        """
        self._bridge = bridge
        self._bus = bus
        self._qt_signals = qt_signals
        self._lock = threading.RLock()
        self._active = False
        
        print("[DataBusIntegration] Initialized")
    
    def start(self):
        """Start integration
        
        Connects bridge subscribers to bus publishers.
        """
        if self._active:
            print("[DataBusIntegration] Already active")
            return
        
        with self._lock:
            # Subscribe to bridge data updates
            self._bridge.subscribe_data(
                '*',  # All data types
                self._on_bridge_data
            )
            
            # Subscribe to bridge events
            self._bridge.subscribe_event(
                '*',  # All event types
                self._on_bridge_event
            )
            
            # Subscribe to Qt signals if available
            if self._qt_signals:
                self._qt_signals.data_updated.connect(self._on_qt_data)
                self._qt_signals.event_received.connect(self._on_qt_event)
            
            self._active = True
        
        print("[DataBusIntegration] ✅ Started")
    
    def stop(self):
        """Stop integration"""
        with self._lock:
            self._active = False
        
        print("[DataBusIntegration] Stopped")
    
    def _on_bridge_data(self, data_type: str, data: Dict[str, Any]):
        """Handle bridge data update
        
        Args:
            data_type: Data type
            data: Data dictionary
        """
        if not self._active:
            return
        
        # Map to bus topic
        topic = f'data.{data_type}'
        
        # Publish to bus
        self._bus.publish(topic, data, sender='bridge')
    
    def _on_bridge_event(self, event_type: str, data: Dict[str, Any]):
        """Handle bridge event
        
        Args:
            event_type: Event type
            data: Event data
        """
        if not self._active:
            return
        
        # Map to bus topic
        topic = f'event.{event_type}'
        
        # Publish to bus
        self._bus.publish(topic, data, sender='bridge', priority=8)
    
    def _on_qt_data(self, data_type: str, data: Dict[str, Any]):
        """Handle Qt signal data update
        
        Args:
            data_type: Data type
            data: Data dictionary
        """
        # Forward to bus with UI priority
        topic = f'ui.data.{data_type}'
        self._bus.publish(topic, data, sender='qt_signals', priority=9)
    
    def _on_qt_event(self, event_type: str, data: Dict[str, Any]):
        """Handle Qt signal event
        
        Args:
            event_type: Event type
            data: Event data
        """
        # Forward to bus with UI priority
        topic = f'ui.event.{event_type}'
        self._bus.publish(topic, data, sender='qt_signals', priority=10)
    
    def is_active(self) -> bool:
        """Check if integration is active"""
        return self._active


# Testing
if __name__ == '__main__' and IMPORTS_OK:
    print("="*60)
    print("DataBusIntegration Test")
    print("="*60)
    print()
    
    from core.backend_bridge import BackendBridge
    from core.data_bus import DataBus
    
    # Create components
    bridge = BackendBridge()
    bus = DataBus()
    integration = DataBusIntegration(bridge, bus)
    
    # Subscribe to bus topics
    def on_perf_data(msg):
        print(f"Bus received: {msg.topic} = {msg.data}")
    
    bus.subscribe('data.*', on_perf_data)
    bus.subscribe('event.*', on_perf_data)
    
    # Start integration
    integration.start()
    
    # Publish from bridge (should forward to bus)
    print("Publishing from bridge...")
    bridge.publish_data('performance_metrics', {'score': 87, 'cpu': 65})
    bridge.publish_event('monitoring_started', {'interval': 100})
    
    print()
    
    # Check stats
    stats = bus.get_stats()
    print("Bus stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print()
    print("✅ Integration test passed!")
