# PartMart Boost Architecture

**Version:** 0.3.5d (Package 3.9a)  
**Updated:** 2026-01-29  
**Status:** ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [System Layers](#system-layers)
3. [Communication Flow](#communication-flow)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Thread Safety](#thread-safety)
8. [Error Handling](#error-handling)

---

## Overview

PartMart Boost uses a layered architecture with clear separation between:
- **Frontend** (UI/Presentation)
- **Communication Layer** (API/Bridge)
- **Backend** (Business Logic/Services)

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                       │
│  (PyQt6 Widgets - User Interface)                       │
├─────────────────────────────────────────────────────────┤
│              COMMUNICATION LAYER (NEW!)                 │
│  (Backend Bridge, Commands, Queries, Qt Signals)        │
├─────────────────────────────────────────────────────────┤
│                    BACKEND LAYER                        │
│  (Performance Monitor, OptiScaler, Config, etc.)        │
└─────────────────────────────────────────────────────────┘
```

---

## System Layers

### 1. Frontend Layer

**Location:** `src/gui/`

**Components:**
- `main_window.py` - Main application window
- `dashboard_widget.py` - Dashboard UI
- `performance_widget.py` - Performance monitoring UI
- `settings_widget.py` - Settings UI
- `logs_widget.py` - Log viewer
- `custom_widgets.py` - Custom UI components

**Responsibilities:**
- Display data to user
- Handle user input
- Update UI in response to backend events
- NO business logic

### 2. Communication Layer

**Location:** `src/core/`

**Components:**
- `backend_bridge.py` - Main API layer
- `command_system.py` - Command definitions
- `query_system.py` - Query builder
- `qt_signal_bridge.py` - Qt signal integration
- `data_bus.py` - Event-based data transport
- `event_system.py` - Event handling

**Responsibilities:**
- Unified API for backend access
- Command execution and validation
- Query processing and caching
- Event pub/sub
- Thread-safe communication
- Error handling

### 3. Backend Layer

**Location:** `src/core/`, `src/monitors/`, `src/optimization/`

**Components:**
- `performance_monitor.py` - Performance monitoring
- `fps_tracker.py` - FPS tracking
- `resource_manager.py` - Resource management
- `config.py` - Configuration
- OptiScaler integration
- Thermal management

**Responsibilities:**
- Business logic
- Data collection
- Performance optimization
- System integration
- NO UI code

---

## Communication Flow

### Command Flow (Frontend → Backend)

```
┌──────────────┐
│  UI Widget   │
└──────┬───────┘
       │ 1. Create command
       v
┌──────────────────┐
│  BackendBridge   │
└──────┬───────────┘
       │ 2. Validate
       │ 3. Execute
       v
┌──────────────────┐
│ Command Handler  │
└──────┬───────────┘
       │ 4. Process
       v
┌──────────────────┐
│  Backend Service │
└──────────────────┘
```

### Data Flow (Backend → Frontend)

```
┌──────────────────┐
│  Backend Service │
└──────┬───────────┘
       │ 1. Publish data
       v
┌──────────────────┐
│  BackendBridge   │
└──────┬───────────┘
       │ 2. Emit Qt signal
       v
┌──────────────────┐
│ QtSignalBridge   │
└──────┬───────────┘
       │ 3. UI update (thread-safe)
       v
┌──────────────┐
│  UI Widget   │
└──────────────┘
```

### Query Flow (Frontend ↔ Backend)

```
┌──────────────┐
│  UI Widget   │
└──────┬───────┘
       │ 1. Build query
       v
┌──────────────────┐
│  QueryBuilder    │
└──────┬───────────┘
       │ 2. Execute query
       v
┌──────────────────┐
│  BackendBridge   │
└──────┬───────────┘
       │ 3. Fetch data
       v
┌──────────────────┐
│  Query Handler   │
└──────┬───────────┘
       │ 4. Return result
       v
┌──────────────┐
│  UI Widget   │
└──────────────┘
```

---

## Component Details

### BackendBridge

**Purpose:** Unified API for all backend-frontend communication

**Key Methods:**
```python
# Execute command
execute_command(command: Command) -> CommandResult

# Query data
query_data(query_type: str, params: dict) -> QueryResult

# Subscribe to events
subscribe(event_type: str, callback: Callable)

# Publish data
publish_data(data_type: str, data: Any)
```

**Features:**
- Singleton pattern
- Thread-safe operations
- Command validation
- Error handling
- Operation history
- Statistics tracking

### Command System

**Purpose:** Structured command pattern for backend operations

**Command Types:**
- `StartMonitoringCommand`
- `StopMonitoringCommand`
- `UpdateSettingsCommand`
- `InstallOptiScalerCommand`
- `GetMetricsCommand`
- `ClearHistoryCommand`
- `ExportDataCommand`
- `ApplyProfileCommand`

**Features:**
- Type-safe commands
- Parameter validation
- Command history
- Undo/redo support (future)

### Query System

**Purpose:** SQL-like query builder for data retrieval

**Query Builder:**
```python
QueryBuilder() \
    .select(['fps', 'cpu', 'gpu']) \
    .filter({'timestamp': '>1h'}) \
    .order_by('timestamp', desc=True) \
    .limit(100) \
    .build()
```

**Features:**
- Fluent interface
- Query validation
- Result caching
- Pagination support

### Qt Signal Bridge

**Purpose:** Thread-safe Qt signal/slot integration

**Signals:**
```python
data_updated = pyqtSignal(str, object)
command_completed = pyqtSignal(str, bool)
error_occurred = pyqtSignal(str, str)
progress_updated = pyqtSignal(str, int)
status_changed = pyqtSignal(str, str)
```

**Features:**
- Thread-safe emission
- Automatic Qt integration
- Signal batching
- Priority signals

---

## Data Flow

### Performance Monitoring Data Flow

```
┌─────────────────────┐
│ PerformanceMonitor  │
│ (Backend Thread)    │
└──────────┬──────────┘
           │ Every 100ms
           v
  ┌────────────────┐
  │ Collect Metrics│
  │ - CPU, GPU     │
  │ - Memory, FPS  │
  └────────┬───────┘
           │
           v
  ┌────────────────┐
  │   Data Bus     │
  └────────┬───────┘
           │ Publish
           v
  ┌────────────────┐
  │ BackendBridge  │
  └────────┬───────┘
           │ Emit Qt Signal
           v
  ┌────────────────┐
  │ QtSignalBridge │
  └────────┬───────┘
           │ Thread-safe
           v
  ┌────────────────┐
  │ UI Widgets     │
  │ (Main Thread)  │
  └────────────────┘
```

### Settings Update Flow

```
┌─────────────────┐
│ Settings Widget │
│ (User clicks)   │
└────────┬────────┘
         │
         v
┌─────────────────────┐
│ Create Command      │
│ UpdateSettingsCmd   │
└────────┬────────────┘
         │
         v
┌─────────────────────┐
│ BackendBridge       │
│ - Validate          │
│ - Execute           │
└────────┬────────────┘
         │
         v
┌─────────────────────┐
│ ConfigManager       │
│ - Update config     │
│ - Save to file      │
└────────┬────────────┘
         │
         v
┌─────────────────────┐
│ Publish Event       │
│ 'settings_updated'  │
└────────┬────────────┘
         │
         v
┌─────────────────────┐
│ All subscribed      │
│ widgets update      │
└─────────────────────┘
```

---

## Design Patterns

### 1. Singleton Pattern
**Used in:** BackendBridge, UIFactory
**Purpose:** Single instance for centralized access

### 2. Command Pattern
**Used in:** Command System
**Purpose:** Encapsulate operations as objects

### 3. Observer Pattern
**Used in:** Event System, Qt Signals
**Purpose:** Pub/sub for decoupled communication

### 4. Builder Pattern
**Used in:** QueryBuilder
**Purpose:** Fluent interface for complex objects

### 5. Factory Pattern
**Used in:** UIFactory
**Purpose:** Create objects without specifying exact class

### 6. Facade Pattern
**Used in:** BackendBridge
**Purpose:** Simplified interface to complex subsystem

---

## Thread Safety

### Thread Model

```
┌──────────────────┐
│   Main Thread    │  ← UI, Qt Events
└────────┬─────────┘
         │
         │ Qt Signals (thread-safe)
         │
┌────────┴─────────┐
│ Backend Thread   │  ← Monitoring, Processing
└──────────────────┘
```

### Synchronization

- **QMutex:** Critical sections in backend
- **Qt Signals:** Thread-safe UI updates
- **Command Queue:** Sequential execution
- **Data Bus:** Thread-safe pub/sub

### Thread-Safe Components

✅ BackendBridge  
✅ CommandSystem  
✅ DataBus  
✅ EventSystem  
✅ QtSignalBridge  
✅ PerformanceMonitor  

---

## Error Handling

### Error Propagation

```
Backend Error
     ↓
CommandResult (success=False, error="...")
     ↓
BackendBridge
     ↓
Qt Signal: error_occurred
     ↓
UI Widget shows error dialog
```

### Error Types

1. **Command Errors**
   - Validation failures
   - Execution failures
   - Timeout errors

2. **Query Errors**
   - Invalid query
   - Data not found
   - Access denied

3. **System Errors**
   - Hardware unavailable
   - Permission denied
   - Resource exhausted

### Error Recovery

- Automatic retry (configurable)
- Fallback values
- Graceful degradation
- User notification

---

## Performance

### Optimization Strategies

1. **Lazy Loading**
   - PyQt6 loaded on demand
   - Plugins loaded when needed

2. **Caching**
   - Query result caching
   - Configuration caching
   - UI widget caching

3. **Batching**
   - Event batching
   - Signal batching
   - Update batching

4. **Async Operations**
   - Background monitoring
   - Non-blocking commands
   - Async queries

### Performance Metrics

- **Command latency:** <1ms
- **Query latency:** <5ms
- **UI update frequency:** 10 FPS
- **Memory usage:** ~180 MB
- **CPU usage:** <5%

---

## Summary

**Architecture Benefits:**

✅ Decoupled components  
✅ Thread-safe operations  
✅ Easy to test  
✅ Easy to extend  
✅ Type-safe communication  
✅ Centralized error handling  
✅ Performance optimized  
✅ Production ready  

**Version:** 0.3.5d (Package 3.9a) - COMPLETE!
