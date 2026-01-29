# Historical Data System

**Version:** 0.3.5e (Package 3.9a, Stage 7.7b.8.1)

## Overview

The Historical Data System provides time-series storage and retrieval for monitoring data, enabling trend analysis, reporting, and historical views of system health.

## Components

### 1. HistoricalDataStore

**Purpose:** SQLite-based storage for time-series monitoring data.

**Location:** `src/core/historical_data_store.py`

**Features:**
- Time-series data storage
- Separate tables for health, errors, recoveries
- Indexed queries for fast retrieval
- Configurable retention policies
- Automatic cleanup
- Thread-safe operations

### 2. DataAggregator

**Purpose:** Periodic collection and aggregation of monitoring data.

**Location:** `src/core/data_aggregator.py`

**Features:**
- Periodic data collection
- Background thread processing
- Integration with monitoring systems
- Statistics computation
- Configurable intervals

## Database Schema

### health_history

```sql
CREATE TABLE health_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    component TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    metrics TEXT  -- JSON
);

CREATE INDEX idx_health_timestamp ON health_history(timestamp);
CREATE INDEX idx_health_component ON health_history(component);
```

### error_history

```sql
CREATE TABLE error_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    severity TEXT NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT
);

CREATE INDEX idx_error_timestamp ON error_history(timestamp);
CREATE INDEX idx_error_severity ON error_history(severity);
```

### recovery_history

```sql
CREATE TABLE recovery_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    component TEXT NOT NULL,
    strategy TEXT NOT NULL,
    status TEXT NOT NULL,
    duration REAL NOT NULL,
    message TEXT
);

CREATE INDEX idx_recovery_timestamp ON recovery_history(timestamp);
```

### statistics_hourly

```sql
CREATE TABLE statistics_hourly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    hour_start REAL NOT NULL,
    total_checks INTEGER DEFAULT 0,
    successful_checks INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0,
    total_recoveries INTEGER DEFAULT 0,
    metrics TEXT  -- JSON
);

CREATE INDEX idx_statistics_timestamp ON statistics_hourly(timestamp);
```

## Usage

### Basic Setup

```python
from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
from core.data_aggregator import DataAggregator, AggregationConfig

# Create historical data store
store = HistoricalDataStore(
    db_path="data/monitoring_history.db",
    retention_policy=DataRetentionPolicy.DAYS_30
)

# Create aggregator
config = AggregationConfig(
    collection_interval=60.0,  # Collect every minute
    aggregation_interval=3600.0  # Aggregate hourly
)

aggregator = DataAggregator(
    historical_store=store,
    health_monitor=health_monitor,
    error_reporter=error_reporter,
    recovery_coordinator=recovery_coordinator,
    config=config
)

# Start automatic collection
aggregator.start_collection()
```

### Storing Data

```python
# Store health snapshot
store.store_health_snapshot(
    component='PerformanceMonitor',
    status='healthy',
    message='Operating normally',
    metrics={'cpu': 45.2, 'memory': 1024}
)

# Store error
store.store_error(
    severity='error',
    component='GameDetector',
    message='Failed to detect game',
    details='Process not found'
)

# Store recovery
store.store_recovery(
    component='ConfigManager',
    strategy='reload',
    status='success',
    duration=1.23,
    message='Configuration reloaded'
)
```

### Querying Data

```python
import time

# Get last 24 hours
end_time = time.time()
start_time = end_time - 86400  # 24 hours

# Query health history
health_records = store.query_health_history(
    start_time,
    end_time,
    component='PerformanceMonitor',  # Optional filter
    limit=1000
)

# Query errors
errors = store.query_errors(
    start_time,
    end_time,
    severity='error',  # Optional filter
    limit=500
)

# Query recoveries
recoveries = store.query_recoveries(
    start_time,
    end_time,
    status='success',  # Optional filter
    limit=100
)
```

### Getting Statistics

```python
# Get statistics for time range
stats = store.get_statistics(start_time, end_time)

print(f"Total checks: {stats['total_checks']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Total errors: {stats['total_errors']}")
print(f"Total recoveries: {stats['total_recoveries']}")
print(f"Avg recovery duration: {stats['avg_recovery_duration']:.2f}s")

# Errors by severity
for severity, count in stats['errors_by_severity'].items():
    print(f"  {severity}: {count}")
```

### Data Retention

```python
# Cleanup old data (automatic based on retention policy)
deleted = store.cleanup_old_data()
print(f"Deleted {deleted} old records")

# Manual cleanup with specific retention
deleted = store.cleanup_old_data(retention_days=7)

# Vacuum database to reclaim space
store.vacuum()
```

### Aggregator Statistics

```python
# Get aggregator statistics
stats = aggregator.get_statistics()

print(f"Running: {stats['is_running']}")
print(f"Collections: {stats['collections_count']}")
print(f"Aggregations: {stats['aggregations_count']}")
print(f"Errors: {stats['errors_count']}")
print(f"Last collection: {stats['last_collection_time']}")
```

## Data Retention Policies

### Available Policies

```python
from core.historical_data_store import DataRetentionPolicy

# 7 days retention
DataRetentionPolicy.DAYS_7

# 30 days retention (default)
DataRetentionPolicy.DAYS_30

# 90 days retention
DataRetentionPolicy.DAYS_90

# 1 year retention
DataRetentionPolicy.DAYS_365

# Unlimited (no automatic cleanup)
DataRetentionPolicy.UNLIMITED
```

### Changing Retention Policy

```python
# Create store with custom retention
store = HistoricalDataStore(
    db_path="data/monitoring.db",
    retention_policy=DataRetentionPolicy.DAYS_90
)

# Cleanup with different retention
store.cleanup_old_data(retention_days=30)
```

## Configuration Options

### AggregationConfig

```python
config = AggregationConfig(
    collection_interval=60.0,  # Collect every 60 seconds
    aggregation_interval=3600.0,  # Aggregate every hour
    enable_health_collection=True,  # Collect health data
    enable_error_collection=True,  # Collect errors
    enable_recovery_collection=True  # Collect recoveries
)
```

### Custom Collection Intervals

```python
# Fast collection (every 30 seconds)
config = AggregationConfig(collection_interval=30.0)

# Slow collection (every 5 minutes)
config = AggregationConfig(collection_interval=300.0)

# Hourly aggregation
config = AggregationConfig(aggregation_interval=3600.0)

# Daily aggregation
config = AggregationConfig(aggregation_interval=86400.0)
```

## Performance Considerations

### Database Size

**Typical storage:**
- Health snapshot: ~200 bytes
- Error record: ~150 bytes
- Recovery record: ~100 bytes

**Example with 30-day retention:**
- 1 health check/minute/component: ~260KB/day/component
- 10 errors/hour: ~36KB/day
- 5 recoveries/hour: ~12KB/day

**Total for 5 components:** ~40MB for 30 days

### Query Performance

```python
# Indexes ensure fast queries
# Typical query times:
# - Time range query: <10ms for 1,000 records
# - Component filter: <5ms
# - Statistics: <50ms

# For better performance with large datasets:

# 1. Limit result count
records = store.query_health_history(
    start_time, end_time,
    limit=100  # Limit results
)

# 2. Use specific filters
records = store.query_errors(
    start_time, end_time,
    severity='error',  # Filter by severity
    component='GameDetector'  # Filter by component
)

# 3. Query smaller time ranges
one_hour = 3600
records = store.query_health_history(
    time.time() - one_hour,
    time.time()
)
```

### Memory Usage

```python
# DataAggregator runs in background thread
# Memory overhead: ~5-10MB
# Database connection pool: ~2-5MB

# Monitor database size
size_bytes = store.get_database_size()
size_mb = size_bytes / (1024 * 1024)
print(f"Database size: {size_mb:.2f} MB")

# Optimize regularly
if size_mb > 100:
    store.cleanup_old_data()
    store.vacuum()
```

## Integration with Monitoring Systems

### Complete Integration Example

```python
from core.error_reporter import ErrorReporter
from core.system_health_monitor import SystemHealthMonitor
from core.recovery_coordinator import RecoveryCoordinator
from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
from core.data_aggregator import DataAggregator, AggregationConfig

class MonitoringApplication:
    def __init__(self):
        # Create monitoring systems
        self.error_reporter = ErrorReporter()
        self.health_monitor = SystemHealthMonitor(
            check_interval=5.0,
            error_reporter=self.error_reporter
        )
        self.recovery_coordinator = RecoveryCoordinator(
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter
        )
        
        # Create historical data system
        self.historical_store = HistoricalDataStore(
            db_path="data/monitoring_history.db",
            retention_policy=DataRetentionPolicy.DAYS_30
        )
        
        # Create aggregator
        self.aggregator = DataAggregator(
            historical_store=self.historical_store,
            health_monitor=self.health_monitor,
            error_reporter=self.error_reporter,
            recovery_coordinator=self.recovery_coordinator,
            config=AggregationConfig(
                collection_interval=60.0,
                aggregation_interval=3600.0
            )
        )
    
    def start(self):
        """Start monitoring with historical data collection"""
        self.health_monitor.start()
        self.recovery_coordinator.enable_auto_recovery()
        self.aggregator.start_collection()
        print("Monitoring started with historical data collection")
    
    def stop(self):
        """Stop monitoring"""
        self.aggregator.stop_collection()
        self.health_monitor.stop()
        print("Monitoring stopped")
    
    def get_historical_report(self, hours=24):
        """Get historical report for last N hours"""
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        stats = self.historical_store.get_statistics(start_time, end_time)
        
        return {
            'time_range': f"Last {hours} hours",
            'statistics': stats,
            'health_records': self.historical_store.query_health_history(
                start_time, end_time, limit=100
            ),
            'errors': self.historical_store.query_errors(
                start_time, end_time, limit=50
            ),
            'recoveries': self.historical_store.query_recoveries(
                start_time, end_time, limit=50
            )
        }
```

## Troubleshooting

### Database Locked Error

```python
# If you see "database is locked" error:
# 1. Ensure only one DataAggregator instance
# 2. Use context managers for manual queries
# 3. Increase timeout (if using custom connections)

# The store uses threading.Lock for thread safety
# Multiple threads can safely access the same store
```

### Large Database Size

```python
# Regular maintenance
def maintain_database(store):
    # Get current size
    size = store.get_database_size()
    print(f"Current size: {size / 1024 / 1024:.2f} MB")
    
    # Cleanup old data
    deleted = store.cleanup_old_data()
    print(f"Deleted {deleted} old records")
    
    # Vacuum
    store.vacuum()
    
    # Check new size
    new_size = store.get_database_size()
    print(f"New size: {new_size / 1024 / 1024:.2f} MB")
    print(f"Saved: {(size - new_size) / 1024 / 1024:.2f} MB")

# Run weekly
import schedule
schedule.every().week.do(lambda: maintain_database(store))
```

### Slow Queries

```python
# If queries are slow:
# 1. Check database size
# 2. Use smaller time ranges
# 3. Add more filters
# 4. Reduce limit

# Good query
records = store.query_health_history(
    time.time() - 3600,  # Last hour only
    time.time(),
    component='SpecificComponent',  # Specific component
    limit=100  # Reasonable limit
)

# Slow query
records = store.query_health_history(
    0,  # All time
    time.time(),
    limit=100000  # Large limit
)
```

## See Also

- [ErrorReporter Documentation](ERROR_REPORTING.md)
- [SystemHealthMonitor Documentation](SYSTEM_HEALTH.md)
- [RecoveryCoordinator Documentation](RECOVERY_SYSTEM.md)
- [Stage 7.7b.8 Plan](STAGE_7.7b.8_PLAN.md)
