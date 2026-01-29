#!/usr/bin/env python3
"""Data Aggregator - Periodic monitoring data collection

Version: 0.3.5e (package 3.9a, stage 7.7b.8.1/7.7b.8)

Package 3.9a Stage 7.7b.8.1: Data aggregation system.

Features:
- Periodic data collection
- Automatic aggregation
- Background processing
- Integration with monitoring systems
- Statistics computation
"""
import threading
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class AggregationConfig:
    """Configuration for data aggregation"""
    collection_interval: float = 60.0  # seconds
    aggregation_interval: float = 3600.0  # 1 hour
    enable_health_collection: bool = True
    enable_error_collection: bool = True
    enable_recovery_collection: bool = True


class DataAggregator:
    """Aggregate and process monitoring data
    
    v0.3.5e (package 3.9a, stage 7.7b.8.1/7.7b.8)
    
    Features:
    - Periodic data collection from monitoring systems
    - Automatic storage in HistoricalDataStore
    - Background thread processing
    - Configurable intervals
    - Statistics computation
    """
    
    def __init__(
        self,
        historical_store: Any,
        health_monitor: Optional[Any] = None,
        error_reporter: Optional[Any] = None,
        recovery_coordinator: Optional[Any] = None,
        config: Optional[AggregationConfig] = None
    ):
        """Initialize data aggregator
        
        Args:
            historical_store: HistoricalDataStore instance
            health_monitor: SystemHealthMonitor instance
            error_reporter: ErrorReporter instance
            recovery_coordinator: RecoveryCoordinator instance
            config: Aggregation configuration
        """
        self._historical_store = historical_store
        self._health_monitor = health_monitor
        self._error_reporter = error_reporter
        self._recovery_coordinator = recovery_coordinator
        self._config = config or AggregationConfig()
        
        self._collection_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_collection_time = 0.0
        self._last_aggregation_time = 0.0
        
        # Statistics
        self._collections_count = 0
        self._aggregations_count = 0
        self._errors_count = 0
    
    def start_collection(self, interval: Optional[float] = None):
        """Start periodic data collection
        
        Args:
            interval: Collection interval in seconds (uses config if not specified)
        """
        if self._running:
            return
        
        if interval is not None:
            self._config.collection_interval = interval
        
        self._running = True
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True,
            name="DataAggregator"
        )
        self._collection_thread.start()
    
    def stop_collection(self):
        """Stop periodic data collection"""
        self._running = False
        if self._collection_thread:
            self._collection_thread.join(timeout=5.0)
    
    def is_running(self) -> bool:
        """Check if collection is running
        
        Returns:
            True if running
        """
        return self._running
    
    def _collection_loop(self):
        """Main collection loop"""
        while self._running:
            try:
                current_time = time.time()
                
                # Check if it's time to collect
                if current_time - self._last_collection_time >= self._config.collection_interval:
                    self._collect_data()
                    self._last_collection_time = current_time
                    self._collections_count += 1
                
                # Check if it's time to aggregate
                if current_time - self._last_aggregation_time >= self._config.aggregation_interval:
                    self._aggregate_data()
                    self._last_aggregation_time = current_time
                    self._aggregations_count += 1
                
                # Sleep until next check
                time.sleep(min(1.0, self._config.collection_interval / 10))
            
            except Exception as e:
                self._errors_count += 1
                print(f"Error in data aggregation: {e}")
                time.sleep(1.0)
    
    def _collect_data(self):
        """Collect current data from monitoring systems"""
        timestamp = time.time()
        
        # Collect health data
        if self._config.enable_health_collection and self._health_monitor:
            try:
                health_data = self._health_monitor.get_system_health()
                
                # Store overall system health
                self._historical_store.store_health_snapshot(
                    component='_system',
                    status=health_data.get('status', 'unknown'),
                    message=f"{health_data.get('healthy_count', 0)}/{health_data.get('total_components', 0)} healthy",
                    metrics=health_data.get('statistics', {}),
                    timestamp=timestamp
                )
                
                # Store individual component health
                for component_name, component_data in health_data.get('components', {}).items():
                    self._historical_store.store_health_snapshot(
                        component=component_name,
                        status=component_data.get('status', 'unknown'),
                        message=component_data.get('message', ''),
                        metrics=component_data.get('metrics', {}),
                        timestamp=timestamp
                    )
            
            except Exception as e:
                print(f"Error collecting health data: {e}")
        
        # Collect error data
        if self._config.enable_error_collection and self._error_reporter:
            try:
                # Get recent errors (since last collection)
                recent_errors = self._error_reporter.get_errors(
                    limit=100
                )
                
                for error in recent_errors:
                    # Check if we already stored this error
                    if error.get('timestamp', 0) >= self._last_collection_time:
                        self._historical_store.store_error(
                            severity=error.get('severity', 'info'),
                            component=error.get('component', 'unknown'),
                            message=error.get('message', ''),
                            details=error.get('details'),
                            timestamp=error.get('timestamp', timestamp)
                        )
            
            except Exception as e:
                print(f"Error collecting error data: {e}")
        
        # Collect recovery data
        if self._config.enable_recovery_collection and self._recovery_coordinator:
            try:
                # Get recent recoveries (since last collection)
                recent_recoveries = self._recovery_coordinator.get_recovery_history(
                    limit=50
                )
                
                for recovery in recent_recoveries:
                    # Check if we already stored this recovery
                    if recovery.get('timestamp', 0) >= self._last_collection_time:
                        self._historical_store.store_recovery(
                            component=recovery.get('component', 'unknown'),
                            strategy=recovery.get('strategy', 'unknown'),
                            status=recovery.get('status', 'unknown'),
                            duration=recovery.get('duration', 0.0),
                            message=recovery.get('message'),
                            timestamp=recovery.get('timestamp', timestamp)
                        )
            
            except Exception as e:
                print(f"Error collecting recovery data: {e}")
    
    def _aggregate_data(self):
        """Aggregate collected data for the past period"""
        # This could be expanded to create hourly summaries
        # For now, the data is already stored and can be queried
        pass
    
    def collect_now(self):
        """Trigger immediate data collection"""
        self._collect_data()
        self._collections_count += 1
    
    def aggregate_now(self):
        """Trigger immediate aggregation"""
        self._aggregate_data()
        self._aggregations_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregator statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'is_running': self._running,
            'collections_count': self._collections_count,
            'aggregations_count': self._aggregations_count,
            'errors_count': self._errors_count,
            'last_collection_time': self._last_collection_time,
            'last_aggregation_time': self._last_aggregation_time,
            'collection_interval': self._config.collection_interval,
            'aggregation_interval': self._config.aggregation_interval
        }
    
    def get_time_range_statistics(
        self,
        start_time: float,
        end_time: float
    ) -> Dict[str, Any]:
        """Get statistics for a time range
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
        
        Returns:
            Statistics dictionary
        """
        return self._historical_store.get_statistics(start_time, end_time)
    
    def cleanup_old_data(self, retention_days: Optional[int] = None) -> int:
        """Clean up old data
        
        Args:
            retention_days: Retention period in days
        
        Returns:
            Number of records deleted
        """
        deleted = self._historical_store.cleanup_old_data(retention_days)
        
        # Vacuum database to reclaim space
        if deleted > 0:
            self._historical_store.vacuum()
        
        return deleted


# Testing
if __name__ == '__main__':
    import tempfile
    import os
    from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        print("Testing DataAggregator...\n")
        
        # Create store
        store = HistoricalDataStore(db_path, DataRetentionPolicy.DAYS_7)
        
        # Create aggregator
        config = AggregationConfig(
            collection_interval=2.0,  # 2 seconds for testing
            aggregation_interval=5.0  # 5 seconds for testing
        )
        aggregator = DataAggregator(store, config=config)
        
        print("Starting collection...")
        aggregator.start_collection()
        
        # Run for a few seconds
        print("Collecting data for 10 seconds...")
        time.sleep(10)
        
        print("\nStopping collection...")
        aggregator.stop_collection()
        
        # Get statistics
        print("\nAggregator statistics:")
        stats = aggregator.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Get record counts
        print("\nRecord counts:")
        counts = store.get_record_counts()
        for key, value in counts.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Test completed successfully!")
    
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
