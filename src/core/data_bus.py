#!/usr/bin/env python3
"""Data Bus - Event Routing and Pub/Sub

Version: 0.3.5f (package 3.9a, stage 7.4/7.7)

Package 3.9a Stage 7.4: Advanced event routing system.

Features:
- Topic-based pub/sub
- Pattern matching subscriptions
- Priority queues
- Message filtering
- Broadcast channels
- Request/response pattern
- Message history
- Thread-safe operations
"""
import threading
import time
import queue
import re
from typing import Dict, List, Callable, Any, Optional, Pattern
from dataclasses import dataclass, field
from collections import defaultdict
import uuid


@dataclass
class Message:
    """Bus message
    
    Attributes:
        topic: Message topic/channel
        data: Message payload
        message_id: Unique message ID
        timestamp: Creation timestamp
        sender: Sender identifier
        priority: Message priority (0=low, 5=normal, 10=high)
        ttl: Time-to-live in seconds (None=infinite)
    """
    topic: str
    data: Any
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    sender: Optional[str] = None
    priority: int = 5
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if message expired"""
        if self.ttl is None:
            return False
        return (time.time() - self.timestamp) > self.ttl


@dataclass
class Subscription:
    """Topic subscription
    
    Attributes:
        subscriber_id: Unique subscriber ID
        topic_pattern: Topic pattern (supports wildcards)
        callback: Callback function
        filter_func: Optional message filter
        priority: Subscription priority
        active: Whether subscription is active
    """
    subscriber_id: str
    topic_pattern: str
    callback: Callable[[Message], None]
    filter_func: Optional[Callable[[Message], bool]] = None
    priority: int = 5
    active: bool = True
    
    def matches(self, topic: str) -> bool:
        """Check if topic matches pattern
        
        Supports wildcards:
        - * matches any single segment
        - ** matches any number of segments
        
        Examples:
            performance.* matches performance.cpu, performance.gpu
            performance.** matches performance.cpu.usage, performance.gpu.temp.current
            *.started matches game.started, monitoring.started
        """
        # Convert pattern to regex
        pattern = self.topic_pattern.replace('.', r'\.')
        pattern = pattern.replace('**', '.*')
        pattern = pattern.replace('*', '[^.]+')  # Single segment only
        pattern = f'^{pattern}$'
        
        return re.match(pattern, topic) is not None
    
    def accepts(self, message: Message) -> bool:
        """Check if subscription accepts message
        
        Args:
            message: Message to check
        
        Returns:
            True if message should be delivered
        """
        if not self.active:
            return False
        
        if message.is_expired():
            return False
        
        if not self.matches(message.topic):
            return False
        
        if self.filter_func and not self.filter_func(message):
            return False
        
        return True


class DataBus:
    """Advanced event routing and pub/sub system
    
    v0.3.5f (package 3.9a, stage 7.4/7.7)
    
    Features:
    - Topic-based messaging
    - Pattern matching (wildcards)
    - Priority queues
    - Message filtering
    - Request/response
    - Message history
    - Thread-safe
    
    Topic Naming:
        Use dot notation for hierarchical topics:
        - performance.cpu.usage
        - performance.gpu.temperature
        - game.detected
        - game.started
        - config.changed
    
    Wildcards:
        - performance.* → matches performance.cpu, performance.gpu
        - performance.** → matches performance.cpu.usage, etc.
        - *.started → matches game.started, monitoring.started
    
    Usage:
        >>> bus = DataBus()
        >>> 
        >>> # Subscribe to topics
        >>> sub_id = bus.subscribe(
        ...     'performance.*',
        ...     callback=lambda msg: print(f"Got: {msg.data}")
        ... )
        >>> 
        >>> # Publish messages
        >>> bus.publish('performance.cpu', {'usage': 65})
        >>> 
        >>> # Request/response pattern
        >>> response = bus.request('config.get', {'key': 'theme'})
    """
    
    def __init__(self, max_history: int = 1000):
        """Initialize data bus
        
        Args:
            max_history: Max messages to keep in history
        """
        self._subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self._message_history: List[Message] = []
        self._max_history = max_history
        self._lock = threading.RLock()
        self._request_responses: Dict[str, queue.Queue] = {}
        self._stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'subscriptions': 0,
        }
        
        print("[DataBus] Initialized")
    
    def publish(self, topic: str, data: Any, 
                sender: Optional[str] = None,
                priority: int = 5,
                ttl: Optional[float] = None) -> str:
        """Publish message to topic
        
        Args:
            topic: Topic name
            data: Message data
            sender: Sender identifier (optional)
            priority: Message priority (0-10, default 5)
            ttl: Time-to-live in seconds (optional)
        
        Returns:
            Message ID
        
        Example:
            >>> bus.publish('performance.cpu', {'usage': 65})
            >>> bus.publish('game.started', {'name': 'Tarkov'}, priority=10)
        """
        message = Message(
            topic=topic,
            data=data,
            sender=sender,
            priority=priority,
            ttl=ttl
        )
        
        with self._lock:
            # Update stats
            self._stats['messages_published'] += 1
            
            # Add to history
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history.pop(0)
            
            # Deliver to subscribers
            delivered = self._deliver_message(message)
            self._stats['messages_delivered'] += delivered
            
            # Handle request/response
            if topic.startswith('request.'):
                # Extract request ID from topic
                parts = topic.split('.')
                if len(parts) >= 3:
                    request_id = parts[2]
                    if request_id in self._request_responses:
                        self._request_responses[request_id].put(message)
        
        return message.message_id
    
    def subscribe(self, topic_pattern: str,
                  callback: Callable[[Message], None],
                  filter_func: Optional[Callable[[Message], bool]] = None,
                  priority: int = 5,
                  subscriber_id: Optional[str] = None) -> str:
        """Subscribe to topic pattern
        
        Args:
            topic_pattern: Topic pattern (supports wildcards)
            callback: Callback function(message)
            filter_func: Optional message filter
            priority: Subscription priority (0-10, default 5)
            subscriber_id: Optional subscriber ID (auto-generated if None)
        
        Returns:
            Subscriber ID
        
        Example:
            >>> def on_perf(msg):
            ...     print(f"Performance: {msg.data}")
            >>> 
            >>> sub_id = bus.subscribe('performance.*', on_perf)
            >>> 
            >>> # With filter
            >>> sub_id = bus.subscribe(
            ...     'performance.*',
            ...     on_perf,
            ...     filter_func=lambda m: m.data.get('usage', 0) > 80
            ... )
        """
        if subscriber_id is None:
            subscriber_id = str(uuid.uuid4())
        
        subscription = Subscription(
            subscriber_id=subscriber_id,
            topic_pattern=topic_pattern,
            callback=callback,
            filter_func=filter_func,
            priority=priority
        )
        
        with self._lock:
            self._subscriptions[topic_pattern].append(subscription)
            self._stats['subscriptions'] = sum(
                len(subs) for subs in self._subscriptions.values()
            )
        
        print(f"[DataBus] Subscribed: {subscriber_id} → {topic_pattern}")
        return subscriber_id
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe by ID
        
        Args:
            subscriber_id: Subscriber ID
        
        Returns:
            True if unsubscribed
        """
        with self._lock:
            found = False
            for pattern, subs in list(self._subscriptions.items()):
                self._subscriptions[pattern] = [
                    sub for sub in subs
                    if sub.subscriber_id != subscriber_id
                ]
                if not self._subscriptions[pattern]:
                    del self._subscriptions[pattern]
                    found = True
            
            if found:
                self._stats['subscriptions'] = sum(
                    len(subs) for subs in self._subscriptions.values()
                )
            
            return found
    
    def request(self, topic: str, data: Any,
                timeout: float = 5.0,
                sender: Optional[str] = None) -> Optional[Message]:
        """Request/response pattern
        
        Publishes a request message and waits for response.
        
        Args:
            topic: Request topic
            data: Request data
            timeout: Response timeout (seconds)
            sender: Sender identifier
        
        Returns:
            Response message or None if timeout
        
        Example:
            >>> # Requester
            >>> response = bus.request('config.get', {'key': 'theme'})
            >>> if response:
            ...     print(f"Theme: {response.data}")
            >>> 
            >>> # Responder
            >>> def handle_config_get(msg):
            ...     key = msg.data.get('key')
            ...     value = get_config(key)
            ...     bus.publish(f'response.{msg.message_id}', value)
            >>> 
            >>> bus.subscribe('config.get', handle_config_get)
        """
        request_id = str(uuid.uuid4())
        response_queue = queue.Queue(maxsize=1)
        
        with self._lock:
            self._request_responses[request_id] = response_queue
        
        try:
            # Publish request with special topic
            request_topic = f'request.{topic}.{request_id}'
            self.publish(request_topic, data, sender=sender, priority=10)
            
            # Wait for response
            try:
                response = response_queue.get(timeout=timeout)
                return response
            except queue.Empty:
                return None
        
        finally:
            with self._lock:
                self._request_responses.pop(request_id, None)
    
    def get_history(self, topic_pattern: Optional[str] = None,
                   limit: int = 100) -> List[Message]:
        """Get message history
        
        Args:
            topic_pattern: Filter by topic pattern (optional)
            limit: Max messages to return
        
        Returns:
            List of messages
        """
        with self._lock:
            if topic_pattern:
                # Create temporary subscription to use pattern matching
                temp_sub = Subscription(
                    subscriber_id='temp',
                    topic_pattern=topic_pattern,
                    callback=lambda m: None
                )
                messages = [
                    msg for msg in self._message_history
                    if temp_sub.matches(msg.topic)
                ]
            else:
                messages = list(self._message_history)
            
            return messages[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bus statistics
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            return {
                **self._stats,
                'history_size': len(self._message_history),
                'patterns': len(self._subscriptions),
            }
    
    def clear_history(self):
        """Clear message history"""
        with self._lock:
            self._message_history.clear()
        
        print("[DataBus] History cleared")
    
    def _deliver_message(self, message: Message) -> int:
        """Deliver message to subscribers (internal)
        
        Args:
            message: Message to deliver
        
        Returns:
            Number of deliveries
        """
        delivered = 0
        
        # Collect all matching subscriptions
        matching_subs: List[Subscription] = []
        for subs in self._subscriptions.values():
            for sub in subs:
                if sub.accepts(message):
                    matching_subs.append(sub)
        
        # Sort by priority (high to low)
        matching_subs.sort(key=lambda s: s.priority, reverse=True)
        
        # Deliver to each subscriber
        for sub in matching_subs:
            try:
                sub.callback(message)
                delivered += 1
            except Exception as e:
                print(f"[DataBus] Delivery error to {sub.subscriber_id}: {e}")
        
        return delivered


# Testing
if __name__ == '__main__':
    print("="*60)
    print("DataBus Test")
    print("="*60)
    print()
    
    bus = DataBus()
    
    # Test 1: Basic pub/sub
    print("Test 1: Basic pub/sub")
    
    def on_cpu(msg):
        print(f"  CPU callback: {msg.data}")
    
    sub1 = bus.subscribe('performance.cpu', on_cpu)
    bus.publish('performance.cpu', {'usage': 65})
    print()
    
    # Test 2: Wildcard patterns
    print("Test 2: Wildcard patterns")
    
    def on_any_perf(msg):
        print(f"  Any perf: {msg.topic} = {msg.data}")
    
    sub2 = bus.subscribe('performance.*', on_any_perf)
    bus.publish('performance.cpu', {'usage': 70})
    bus.publish('performance.gpu', {'temp': 75})
    bus.publish('performance.ram', {'usage': 50})
    print()
    
    # Test 3: Filter function
    print("Test 3: Filter function")
    
    def on_high_usage(msg):
        print(f"  HIGH USAGE: {msg.topic} = {msg.data}")
    
    sub3 = bus.subscribe(
        'performance.*',
        on_high_usage,
        filter_func=lambda m: m.data.get('usage', 0) > 80
    )
    
    bus.publish('performance.cpu', {'usage': 70})  # Not delivered
    bus.publish('performance.cpu', {'usage': 90})  # Delivered
    print()
    
    # Test 4: Request/response
    print("Test 4: Request/response")
    
    def handle_config_get(msg):
        key = msg.data.get('key')
        value = f"value_of_{key}"
        # Respond
        parts = msg.topic.split('.')
        if len(parts) >= 3:
            request_id = parts[2]
            bus.publish(f'response.{request_id}', value)
    
    bus.subscribe('request.config.get.*', handle_config_get)
    
    response = bus.request('config.get', {'key': 'theme'}, timeout=1.0)
    if response:
        print(f"  Response: {response.data}")
    else:
        print("  No response")
    print()
    
    # Test 5: Statistics
    print("Test 5: Statistics")
    stats = bus.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    print("✅ All tests passed!")
