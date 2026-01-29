#!/usr/bin/env python3
"""Configuration Integration

Version: 0.3.5h (package 3.9a, stage 7.6/7.7)

Package 3.9a Stage 7.6: Config integration with other systems.

Features:
- Config → DataBus integration
- Auto-save on changes
- Config-driven monitoring
- Settings synchronization
"""
import os
import threading
from typing import Optional

try:
    from config_manager import ConfigManager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("[ConfigIntegration] ConfigManager not available")


class ConfigIntegration:
    """Configuration integration layer
    
    v0.3.5h (package 3.9a, stage 7.6/7.7)
    
    Features:
    - Publishes config changes to DataBus
    - Auto-saves configuration
    - Applies config to other components
    
    Usage:
        >>> integration = ConfigIntegration(
        ...     config=config_manager,
        ...     data_bus=bus
        ... )
        >>> integration.start()
    """
    
    def __init__(self, config: Optional['ConfigManager'] = None,
                 data_bus=None):
        """Initialize config integration
        
        Args:
            config: ConfigManager instance
            data_bus: DataBus instance
        """
        self._config = config
        self._data_bus = data_bus
        self._active = False
        self._lock = threading.RLock()
        
        print("[ConfigIntegration] Initialized")
    
    def start(self):
        """Start integration"""
        if not self._config:
            print("[ConfigIntegration] No config manager")
            return
        
        with self._lock:
            if self._active:
                print("[ConfigIntegration] Already active")
                return
            
            self._active = True
        
        # Subscribe to all config changes
        self._config.subscribe('**', self._on_config_change)
        
        print("[ConfigIntegration] ✅ Started")
    
    def stop(self):
        """Stop integration"""
        with self._lock:
            self._active = False
        
        print("[ConfigIntegration] Stopped")
    
    def _on_config_change(self, key: str, value):
        """Handle configuration change
        
        Args:
            key: Configuration key
            value: New value
        """
        if not self._active:
            return
        
        # Publish to DataBus
        if self._data_bus:
            try:
                self._data_bus.publish(
                    f'config.changed.{key}',
                    {'key': key, 'value': value},
                    priority=6
                )
            except Exception as e:
                print(f"[ConfigIntegration] DataBus publish error: {e}")
        
        # Auto-save if enabled
        if self._config:
            auto_save = self._config.get('advanced.auto_save', True)
            if auto_save:
                try:
                    self._config.save()
                except Exception as e:
                    print(f"[ConfigIntegration] Auto-save error: {e}")
    
    def apply_monitoring_config(self, monitor):
        """Apply monitoring configuration
        
        Args:
            monitor: PerformanceMonitor instance
        """
        if not self._config or not monitor:
            return
        
        try:
            # Apply interval
            interval = self._config.get('monitor.interval_ms', 100)
            if hasattr(monitor, 'set_interval'):
                monitor.set_interval(interval)
            
            print(f"[ConfigIntegration] Applied monitoring config (interval={interval}ms)")
        
        except Exception as e:
            print(f"[ConfigIntegration] Apply monitoring config error: {e}")
    
    def is_active(self) -> bool:
        """Check if active
        
        Returns:
            True if active
        """
        return self._active


# Testing
if __name__ == '__main__' and CONFIG_AVAILABLE:
    print("="*60)
    print("ConfigIntegration Test")
    print("="*60)
    print()
    
    # Create mock DataBus
    class MockDataBus:
        def publish(self, topic, data, priority=5):
            print(f"  DataBus: {topic} = {data}")
    
    # Create config and integration
    config = ConfigManager()
    bus = MockDataBus()
    integration = ConfigIntegration(config=config, data_bus=bus)
    
    print("Starting integration...")
    integration.start()
    print()
    
    print("Changing config values:")
    config.set('ui.theme', 'light')
    config.set('monitor.interval_ms', 200)
    print()
    
    integration.stop()
    
    print("✅ Test completed!")
