# DataBus Documentation

**Version:** 0.3.5f (Package 3.9a, Stage 7.4/7.7)

## Overview

DataBus is an advanced event routing and pub/sub messaging system for PartMart Boost.

### Features

- **Topic-based messaging**: Hierarchical topic structure with dot notation
- **Wildcard subscriptions**: Pattern matching with `*` and `**`
- **Message filtering**: Custom filter functions for subscribers
- **Priority queues**: Prioritized message delivery
- **Request/response**: Built-in request/response pattern
- **Message history**: Queryable message history
- **Thread-safe**: Safe for multi-threaded environments

## Basic Usage

### Creating a Bus

```python
from core.data_bus import DataBus

bus = DataBus(max_history=1000)
```

### Publishing Messages

```python
# Simple publish
bus.publish('performance.cpu', {'usage': 65})

# With priority
bus.publish('game.started', {'name': 'Tarkov'}, priority=10)

# With TTL (time-to-live)
bus.publish('temp.alert', {'temp': 90}, ttl=5.0)  # Expires after 5s
```

### Subscribing to Topics

```python
def on_cpu_update(msg):
    print(f"CPU: {msg.data}")

sub_id = bus.subscribe('performance.cpu', on_cpu_update)
```

### Unsubscribing

```python
bus.unsubscribe(sub_id)
```

## Topic Structure

### Naming Convention

Use dot notation for hierarchical topics:

```
performance.cpu.usage
performance.cpu.temperature
performance.gpu.usage
performance.gpu.temperature
performance.ram.usage
game.detected
game.started
game.stopped
config.changed
config.loaded
```

### Wildcard Patterns

#### Single Segment (`*`)

Matches exactly one segment:

```python
# Matches: performance.cpu, performance.gpu, performance.ram
# Does NOT match: performance.cpu.usage
bus.subscribe('performance.*', callback)
```

#### Multiple Segments (`**`)

Matches any number of segments:

```python
# Matches: performance.cpu, performance.cpu.usage, performance.gpu.temp.current
bus.subscribe('performance.**', callback)
```

#### Mixed Patterns

```python
# Matches: game.started, monitoring.started, etc.
bus.subscribe('*.started', callback)

# Matches: performance.cpu.*, performance.gpu.*, etc.
bus.subscribe('performance.*.*', callback)
```

## Message Filtering

### Filter Functions

Add custom logic to filter messages:

```python
def on_high_usage(msg):
    print(f"HIGH: {msg.data}")

bus.subscribe(
    'performance.*',
    on_high_usage,
    filter_func=lambda m: m.data.get('usage', 0) > 80
)
```

### Common Filters

```python
# Filter by value threshold
filter_func=lambda m: m.data.get('value', 0) > threshold

# Filter by sender
filter_func=lambda m: m.sender == 'monitor'

# Filter by data presence
filter_func=lambda m: 'critical' in m.data

# Complex filter
filter_func=lambda m: (
    m.data.get('usage', 0) > 80 and
    m.data.get('temp', 0) > 75
)
```

## Priorities

### Message Priority

Messages with higher priority are delivered first:

```python
# Low priority (0)
bus.publish('log', {'msg': 'Debug'}, priority=0)

# Normal priority (5) - default
bus.publish('data', {'value': 42})

# High priority (10)
bus.publish('alert', {'level': 'critical'}, priority=10)
```

### Subscription Priority

Subscribers with higher priority receive messages first:

```python
bus.subscribe('alert', critical_handler, priority=10)
bus.subscribe('alert', normal_handler, priority=5)
bus.subscribe('alert', logger, priority=1)
```

## Request/Response Pattern

### Server (Responder)

```python
def handle_config_request(msg):
    key = msg.data.get('key')
    value = get_config(key)
    
    # Extract request ID from topic
    parts = msg.topic.split('.')
    if len(parts) >= 3:
        request_id = parts[2]
        bus.publish(f'response.{request_id}', {'value': value})

bus.subscribe('request.config.get.*', handle_config_request)
```

### Client (Requester)

```python
response = bus.request(
    'config.get',
    {'key': 'theme'},
    timeout=5.0
)

if response:
    print(f"Theme: {response.data['value']}")
else:
    print("Request timeout")
```

## Message History

### Query History

```python
# Get all messages
all_msgs = bus.get_history()

# Get messages matching pattern
perf_msgs = bus.get_history('performance.*')

# Limit number of results
recent_msgs = bus.get_history(limit=10)
```

### Clear History

```python
bus.clear_history()
```

## Statistics

```python
stats = bus.get_stats()
print(stats)
# {
#     'messages_published': 1234,
#     'messages_delivered': 5678,
#     'subscriptions': 15,
#     'history_size': 987,
#     'patterns': 8
# }
```

## Integration with BackendBridge

### Automatic Forwarding

DataBusIntegration automatically forwards BackendBridge events to DataBus:

```python
from core.backend_bridge import BackendBridge
from core.data_bus import DataBus
from core.data_bus_integration import DataBusIntegration

bridge = BackendBridge()
bus = DataBus()
integration = DataBusIntegration(bridge, bus)

integration.start()

# Subscribe to bus topics
bus.subscribe('data.*', lambda msg: print(msg.data))

# Publish from bridge (automatically forwarded)
bridge.publish_data('performance_metrics', {'score': 87})
# DataBus receives on topic: 'data.performance_metrics'
```

### Topic Mapping

| Bridge Event | DataBus Topic |
|--------------|---------------|
| `publish_data('performance_metrics', ...)` | `data.performance_metrics` |
| `publish_event('monitoring_started', ...)` | `event.monitoring_started` |
| Qt signal `data_updated(...)` | `ui.data.*` |
| Qt signal `event_received(...)` | `ui.event.*` |

## Best Practices

### Topic Naming

1. Use lowercase
2. Use dots for hierarchy
3. Be specific but not too deep
4. Group related topics

```python
# Good
'performance.cpu.usage'
'game.started'
'config.theme.changed'

# Avoid
'PERFORMANCE_CPU_USAGE'  # Too noisy
'p.c.u'  # Too cryptic
'system.subsystem.component.metric.value'  # Too deep
```

### Subscription Patterns

```python
# Subscribe to specific topics when possible
bus.subscribe('performance.cpu', handler)  # Good

# Use wildcards only when needed
bus.subscribe('performance.*', handler)  # OK if needed
bus.subscribe('**', handler)  # Use sparingly
```

### Message Data

```python
# Use dictionaries for structured data
bus.publish('perf', {'cpu': 65, 'gpu': 78})  # Good

# Avoid large payloads
bus.publish('data', huge_object)  # Avoid

# Use references for large data
bus.publish('data.ready', {'id': 'data_123'})  # Good
```

### Memory Management

```python
# Limit history size
bus = DataBus(max_history=1000)

# Use TTL for temporary messages
bus.publish('temp', data, ttl=5.0)

# Clear history periodically
bus.clear_history()
```

## Examples

See `examples/databus_usage.py` for comprehensive examples.

## Architecture

```
Application
├─ BackendBridge
│  ├─ publish_data() ────┐
│  └─ publish_event() ───┤
│                         │
├─ DataBusIntegration ◄──┘
│  └─ forwards to DataBus
│
├─ DataBus
│  ├─ Message queue
│  ├─ Subscriptions
│  ├─ History
│  └─ Routing logic
│
└─ Subscribers
   ├─ UI Widgets
   ├─ Services
   └─ Handlers
```

## Thread Safety

DataBus is fully thread-safe:

- All operations use `threading.RLock()`
- Safe to publish/subscribe from any thread
- Callbacks execute synchronously in publishing thread

## Performance

- **Publish latency:** <0.1ms
- **Delivery latency:** <1ms per subscriber
- **Pattern matching:** O(n) where n = number of patterns
- **Memory:** ~50 bytes per message in history

## Troubleshooting

### Messages not delivered

1. Check topic name spelling
2. Verify wildcard pattern
3. Check filter function
4. Verify message not expired (TTL)

### Performance issues

1. Reduce max_history
2. Use specific topics (avoid `**`)
3. Limit number of subscribers
4. Clear history periodically

### Memory leaks

1. Set appropriate max_history
2. Use TTL for temporary messages
3. Unsubscribe when done
4. Clear history regularly
