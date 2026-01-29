#!/usr/bin/env python3
"""DataBus Usage Examples

Version: 0.3.5f (package 3.9a, stage 7.4/7.7)

Examples demonstrating DataBus pub/sub system usage.
"""
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.data_bus import DataBus, Message


def example_1_basic_pubsub():
    """Example 1: Basic pub/sub"""
    print("="*60)
    print("Example 1: Basic Pub/Sub")
    print("="*60)
    print()
    
    bus = DataBus()
    
    # Subscribe to a topic
    def on_cpu_update(msg: Message):
        print(f"CPU Update: {msg.data}")
    
    sub_id = bus.subscribe('performance.cpu', on_cpu_update)
    print(f"Subscribed with ID: {sub_id}")
    print()
    
    # Publish messages
    bus.publish('performance.cpu', {'usage': 65, 'temp': 72})
    bus.publish('performance.cpu', {'usage': 70, 'temp': 75})
    
    print()


def example_2_wildcards():
    """Example 2: Wildcard patterns"""
    print("="*60)
    print("Example 2: Wildcard Patterns")
    print("="*60)
    print()
    
    bus = DataBus()
    
    # Subscribe to all performance topics
    def on_any_performance(msg: Message):
        print(f"Performance [{msg.topic}]: {msg.data}")
    
    bus.subscribe('performance.*', on_any_performance)
    print("Subscribed to 'performance.*'")
    print()
    
    # Publish to different sub-topics
    bus.publish('performance.cpu', {'usage': 65})
    bus.publish('performance.gpu', {'temp': 78})
    bus.publish('performance.ram', {'usage': 50})
    
    print()


def example_3_filters():
    """Example 3: Message filtering"""
    print("="*60)
    print("Example 3: Message Filtering")
    print("="*60)
    print()
    
    bus = DataBus()
    
    # Subscribe with filter (only high CPU usage)
    def on_high_cpu(msg: Message):
        print(f"HIGH CPU: {msg.data}")
    
    bus.subscribe(
        'performance.cpu',
        on_high_cpu,
        filter_func=lambda m: m.data.get('usage', 0) > 80
    )
    print("Subscribed with filter (usage > 80)")
    print()
    
    # Publish messages
    print("Publishing usage=65 (should be filtered out):")
    bus.publish('performance.cpu', {'usage': 65})
    
    print("Publishing usage=90 (should trigger callback):")
    bus.publish('performance.cpu', {'usage': 90})
    
    print()


def example_4_priorities():
    """Example 4: Message priorities"""
    print("="*60)
    print("Example 4: Message Priorities")
    print("="*60)
    print()
    
    bus = DataBus()
    
    # Multiple subscribers with different priorities
    def handler_low(msg: Message):
        print(f"  [Priority 3] Received: {msg.data}")
    
    def handler_normal(msg: Message):
        print(f"  [Priority 5] Received: {msg.data}")
    
    def handler_high(msg: Message):
        print(f"  [Priority 10] Received: {msg.data}")
    
    bus.subscribe('test', handler_low, priority=3)
    bus.subscribe('test', handler_normal, priority=5)
    bus.subscribe('test', handler_high, priority=10)
    
    print("Subscribed 3 handlers with different priorities")
    print("Publishing message (handlers execute high to low):")
    print()
    
    bus.publish('test', {'value': 42})
    
    print()


def example_5_request_response():
    """Example 5: Request/response pattern"""
    print("="*60)
    print("Example 5: Request/Response Pattern")
    print("="*60)
    print()
    
    bus = DataBus()
    
    # Set up responder
    def handle_get_config(msg: Message):
        key = msg.data.get('key')
        print(f"Responder: Received request for key '{key}'")
        
        # Simulate config lookup
        config_values = {
            'theme': 'dark',
            'language': 'en',
            'interval': 100,
        }
        
        value = config_values.get(key, 'not found')
        
        # Send response
        parts = msg.topic.split('.')
        if len(parts) >= 3:
            request_id = parts[2]
            bus.publish(f'response.{request_id}', {'value': value})
            print(f"Responder: Sent response '{value}'")
    
    bus.subscribe('request.config.get.*', handle_get_config)
    print("Responder registered\n")
    
    # Make request
    print("Requester: Sending request for 'theme'...")
    response = bus.request('config.get', {'key': 'theme'}, timeout=1.0)
    
    if response:
        print(f"Requester: Got response: {response.data}")
    else:
        print("Requester: Timeout - no response")
    
    print()


def example_6_history():
    """Example 6: Message history"""
    print("="*60)
    print("Example 6: Message History")
    print("="*60)
    print()
    
    bus = DataBus(max_history=5)
    
    # Publish some messages
    bus.publish('test.1', {'value': 1})
    bus.publish('test.2', {'value': 2})
    bus.publish('other', {'value': 3})
    bus.publish('test.3', {'value': 4})
    
    print("Published 4 messages\n")
    
    # Get all history
    all_msgs = bus.get_history()
    print(f"All history ({len(all_msgs)} messages):")
    for msg in all_msgs:
        print(f"  {msg.topic}: {msg.data}")
    print()
    
    # Get filtered history
    test_msgs = bus.get_history('test.*')
    print(f"Filtered history 'test.*' ({len(test_msgs)} messages):")
    for msg in test_msgs:
        print(f"  {msg.topic}: {msg.data}")
    print()


def example_7_integration():
    """Example 7: Integration with BackendBridge"""
    print("="*60)
    print("Example 7: Integration with BackendBridge")
    print("="*60)
    print()
    
    try:
        from core.backend_bridge import BackendBridge
        from core.data_bus_integration import DataBusIntegration
        
        # Create components
        bridge = BackendBridge()
        bus = DataBus()
        integration = DataBusIntegration(bridge, bus)
        
        # Subscribe to bus topics
        def on_data(msg: Message):
            print(f"Bus: {msg.topic} = {msg.data}")
        
        bus.subscribe('data.*', on_data)
        bus.subscribe('event.*', on_data)
        
        # Start integration
        integration.start()
        print("Integration started\n")
        
        # Publish from bridge (automatically forwarded to bus)
        print("Publishing from bridge:")
        bridge.publish_data('test_metric', {'value': 42})
        bridge.publish_event('test_event', {'status': 'ok'})
        
        print()
        print("Data flowed: Bridge → Integration → Bus → Subscribers")
    
    except ImportError as e:
        print(f"Integration example requires BackendBridge: {e}")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "#"*60)
    print("DataBus Usage Examples")
    print("Version: 0.3.5f (Package 3.9a, Stage 7.4/7.7)")
    print("#"*60 + "\n")
    
    examples = [
        example_1_basic_pubsub,
        example_2_wildcards,
        example_3_filters,
        example_4_priorities,
        example_5_request_response,
        example_6_history,
        example_7_integration,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
            time.sleep(0.5)  # Brief pause between examples
        except Exception as e:
            print(f"Example {i} error: {e}\n")
    
    print("="*60)
    print("✅ All examples completed!")
    print("="*60)


if __name__ == '__main__':
    main()
