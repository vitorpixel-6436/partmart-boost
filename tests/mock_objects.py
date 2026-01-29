#!/usr/bin/env python3
"""Mock Objects for Testing

Version: 0.3.5i (package 3.9a, stage 7.7a/7.7)

Provides mock objects for unit testing.
"""
import time
from typing import Dict, Any, Optional, Callable


class MockPerformanceMonitor:
    """Mock PerformanceMonitor for testing"""
    
    def __init__(self):
        self.monitoring = False
        self.interval_ms = 100
        self.callbacks = []
        self.metrics = {
            'cpu': 50.0,
            'gpu': 60.0,
            'ram': 40.0,
            'fps': 60.0,
            'gpu_temp': 70.0
        }
    
    def start_monitoring(self):
        """Start monitoring"""
        self.monitoring = True
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def is_monitoring(self) -> bool:
        """Check if monitoring"""
        return self.monitoring
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def set_metrics(self, **kwargs):
        """Set metrics (for testing)"""
        self.metrics.update(kwargs)
    
    def set_interval(self, interval_ms: int):
        """Set interval"""
        self.interval_ms = interval_ms
    
    def add_callback(self, callback: Callable):
        """Add callback"""
        self.callbacks.append(callback)
    
    def trigger_callbacks(self):
        """Manually trigger callbacks (for testing)"""
        for callback in self.callbacks:
            callback(self.metrics)


class MockDataBus:
    """Mock DataBus for testing"""
    
    def __init__(self):
        self.subscribers = {}
        self.published_messages = []
        self.message_id = 0
    
    def subscribe(self, topic: str, callback: Callable) -> int:
        """Subscribe to topic"""
        sub_id = len(self.subscribers)
        self.subscribers[sub_id] = (topic, callback)
        return sub_id
    
    def unsubscribe(self, sub_id: int):
        """Unsubscribe"""
        if sub_id in self.subscribers:
            del self.subscribers[sub_id]
    
    def publish(self, topic: str, data: Any, priority: int = 5):
        """Publish message"""
        message = {
            'id': self.message_id,
            'topic': topic,
            'data': data,
            'priority': priority,
            'timestamp': time.time()
        }
        self.message_id += 1
        self.published_messages.append(message)
        
        # Deliver to subscribers
        for sub_id, (sub_topic, callback) in self.subscribers.items():
            if self._match_topic(topic, sub_topic):
                try:
                    callback(type('Message', (), message)())
                except Exception:
                    pass
    
    def _match_topic(self, topic: str, pattern: str) -> bool:
        """Match topic against pattern"""
        if pattern == '**':
            return True
        
        if '*' in pattern:
            pattern_parts = pattern.split('.')
            topic_parts = topic.split('.')
            
            if len(pattern_parts) != len(topic_parts):
                if pattern_parts[-1] == '*':
                    pattern_parts = pattern_parts[:-1]
                else:
                    return False
            
            for p_part, t_part in zip(pattern_parts, topic_parts):
                if p_part != '*' and p_part != t_part:
                    return False
            return True
        
        return topic == pattern
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'subscriptions': len(self.subscribers),
            'messages_published': len(self.published_messages)
        }
    
    def clear(self):
        """Clear all data"""
        self.published_messages.clear()


class MockConfigManager:
    """Mock ConfigManager for testing"""
    
    def __init__(self):
        self.config = {
            'ui.theme': 'dark',
            'ui.language': 'en',
            'ui.show_fps': True,
            'monitor.enabled': True,
            'monitor.interval_ms': 100,
            'performance.boost_enabled': True,
        }
        self.subscribers = []
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """Set value"""
        old_value = self.config.get(key)
        self.config[key] = value
        
        # Notify subscribers
        if old_value != value:
            for pattern, callback in self.subscribers:
                if self._match_pattern(key, pattern):
                    callback(key, value)
        
        return True
    
    def subscribe(self, pattern: str, callback: Callable) -> int:
        """Subscribe to changes"""
        sub_id = len(self.subscribers)
        self.subscribers.append((pattern, callback))
        return sub_id
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Match key against pattern"""
        if pattern == '**':
            return True
        if '*' in pattern:
            prefix = pattern.replace('*', '')
            return key.startswith(prefix)
        return key == pattern
    
    def get_all_keys(self):
        """Get all keys"""
        return list(self.config.keys())
    
    def save(self):
        """Save (no-op for mock)"""
        pass
    
    def load(self, filename: str):
        """Load (no-op for mock)"""
        pass


class MockQtSignals:
    """Mock QtSignalBridge for testing"""
    
    def __init__(self):
        self.emitted_signals = []
    
    def emit_metrics_update(self, metrics: Dict[str, float]):
        """Emit metrics update"""
        self.emitted_signals.append(('metrics_update', metrics))
    
    def emit_status_update(self, status: str):
        """Emit status update"""
        self.emitted_signals.append(('status_update', status))
    
    def emit_error(self, error: str):
        """Emit error"""
        self.emitted_signals.append(('error', error))
    
    def clear(self):
        """Clear emitted signals"""
        self.emitted_signals.clear()
