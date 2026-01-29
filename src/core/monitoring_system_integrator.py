#!/usr/bin/env python3
"""Monitoring System Integrator - Complete integration of all monitoring components

Version: 0.3.6 (package 3.9a, stage 7.7b.9 - FINALIZATION)

Package 3.9a Stage 7.7b.9: Complete system integration.

Integrates:
- ErrorReporter (Stage 7.7b.6.1)
- SystemHealthMonitor (Stage 7.7b.6.2)
- RecoveryCoordinator (Stage 7.7b.6.3)
- MonitoringPanel (Stage 7.7b.7)
- HistoricalDataStore (Stage 7.7b.8.1)
- DataAggregator (Stage 7.7b.8.1)
- ChartWidget (Stage 7.7b.8.2)
- HistoricalDataViewer (Stage 7.7b.8.2)

Provides:
- Unified monitoring interface
- Complete lifecycle management
- Configuration management
- Status reporting
- Performance monitoring
"""
import os
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import threading

# Import all monitoring components
try:
    from core.error_reporter import ErrorReporter
    ERROR_REPORTER_AVAILABLE = True
except ImportError:
    ERROR_REPORTER_AVAILABLE = False

try:
    from core.system_health_monitor import SystemHealthMonitor
    HEALTH_MONITOR_AVAILABLE = True
except ImportError:
    HEALTH_MONITOR_AVAILABLE = False

try:
    from core.recovery_coordinator import RecoveryCoordinator
    RECOVERY_AVAILABLE = True
except ImportError:
    RECOVERY_AVAILABLE = False

try:
    from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
    from core.data_aggregator import DataAggregator, AggregationConfig
    HISTORICAL_AVAILABLE = True
except ImportError:
    HISTORICAL_AVAILABLE = False


@dataclass
class MonitoringConfig:
    """Complete monitoring system configuration"""
    
    # Error reporting
    enable_error_reporting: bool = True
    max_error_history: int = 1000
    
    # Health monitoring
    enable_health_monitoring: bool = True
    health_check_interval: float = 5.0
    
    # Recovery
    enable_auto_recovery: bool = True
    max_recovery_attempts: int = 3
    
    # Historical data
    enable_historical_data: bool = True
    historical_db_path: str = "data/monitoring_history.db"
    data_retention_days: int = 30
    
    # Data aggregation
    enable_data_aggregation: bool = True
    collection_interval: float = 60.0
    aggregation_interval: float = 3600.0
    
    # Performance
    enable_performance_monitoring: bool = True
    
    # GUI
    enable_gui_integration: bool = True


@dataclass
class SystemStatus:
    """Complete system status"""
    
    # Overall status
    is_running: bool
    uptime: float
    
    # Component status
    error_reporter_active: bool
    health_monitor_active: bool
    recovery_coordinator_active: bool
    historical_store_active: bool
    data_aggregator_active: bool
    
    # Statistics
    total_errors: int
    total_recoveries: int
    total_health_checks: int
    success_rate: float
    
    # Performance
    memory_usage_mb: float
    cpu_usage_percent: float


class MonitoringSystemIntegrator:
    """Complete monitoring system integration
    
    v0.3.6 (package 3.9a, stage 7.7b.9 - FINALIZATION)
    
    Provides unified interface for all monitoring components.
    
    Features:
    - Complete component lifecycle
    - Configuration management
    - Status monitoring
    - Performance tracking
    - Error handling
    - Graceful shutdown
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        """Initialize integrator
        
        Args:
            config: Monitoring configuration (optional)
        """
        self.config = config or MonitoringConfig()
        
        # Components
        self._error_reporter: Optional[ErrorReporter] = None
        self._health_monitor: Optional[SystemHealthMonitor] = None
        self._recovery_coordinator: Optional[RecoveryCoordinator] = None
        self._historical_store: Optional[HistoricalDataStore] = None
        self._data_aggregator: Optional[DataAggregator] = None
        
        # State
        self._is_running = False
        self._start_time = 0.0
        self._lock = threading.Lock()
        
        # Performance tracking
        self._performance_stats = {
            'initialization_time': 0.0,
            'startup_time': 0.0,
            'errors_handled': 0,
            'recoveries_performed': 0,
            'health_checks_performed': 0
        }
    
    def initialize(self) -> bool:
        """Initialize all monitoring components
        
        Returns:
            True if initialization successful
        """
        init_start = time.time()
        
        try:
            # Create data directory
            os.makedirs('data', exist_ok=True)
            
            # Initialize error reporter
            if self.config.enable_error_reporting and ERROR_REPORTER_AVAILABLE:
                self._error_reporter = ErrorReporter(
                    max_history=self.config.max_error_history
                )
                print("✅ ErrorReporter initialized")
            
            # Initialize health monitor
            if self.config.enable_health_monitoring and HEALTH_MONITOR_AVAILABLE:
                self._health_monitor = SystemHealthMonitor(
                    check_interval=self.config.health_check_interval,
                    error_reporter=self._error_reporter
                )
                print("✅ SystemHealthMonitor initialized")
            
            # Initialize recovery coordinator
            if self.config.enable_auto_recovery and RECOVERY_AVAILABLE:
                self._recovery_coordinator = RecoveryCoordinator(
                    health_monitor=self._health_monitor,
                    error_reporter=self._error_reporter,
                    max_attempts=self.config.max_recovery_attempts
                )
                print("✅ RecoveryCoordinator initialized")
            
            # Initialize historical data store
            if self.config.enable_historical_data and HISTORICAL_AVAILABLE:
                retention_policy = self._get_retention_policy(
                    self.config.data_retention_days
                )
                
                self._historical_store = HistoricalDataStore(
                    db_path=self.config.historical_db_path,
                    retention_policy=retention_policy
                )
                print("✅ HistoricalDataStore initialized")
            
            # Initialize data aggregator
            if self.config.enable_data_aggregation and HISTORICAL_AVAILABLE:
                agg_config = AggregationConfig(
                    collection_interval=self.config.collection_interval,
                    aggregation_interval=self.config.aggregation_interval
                )
                
                self._data_aggregator = DataAggregator(
                    historical_store=self._historical_store,
                    health_monitor=self._health_monitor,
                    error_reporter=self._error_reporter,
                    recovery_coordinator=self._recovery_coordinator,
                    config=agg_config
                )
                print("✅ DataAggregator initialized")
            
            # Track initialization time
            self._performance_stats['initialization_time'] = time.time() - init_start
            
            return True
        
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start all monitoring components
        
        Returns:
            True if startup successful
        """
        if self._is_running:
            print("⚠️ System already running")
            return False
        
        startup_start = time.time()
        
        try:
            with self._lock:
                # Start health monitor
                if self._health_monitor:
                    self._health_monitor.start()
                    print("▶️ Health monitoring started")
                
                # Enable auto-recovery
                if self._recovery_coordinator:
                    self._recovery_coordinator.enable_auto_recovery()
                    print("▶️ Auto-recovery enabled")
                
                # Start data aggregation
                if self._data_aggregator:
                    self._data_aggregator.start_collection()
                    print("▶️ Data collection started")
                
                self._is_running = True
                self._start_time = time.time()
                self._performance_stats['startup_time'] = time.time() - startup_start
                
                print(f"\n✅ Monitoring system started in {self._performance_stats['startup_time']:.3f}s")
                return True
        
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            return False
    
    def stop(self):
        """Stop all monitoring components gracefully"""
        if not self._is_running:
            return
        
        try:
            with self._lock:
                print("\nStopping monitoring system...")
                
                # Stop data aggregation
                if self._data_aggregator:
                    self._data_aggregator.stop_collection()
                    print("⏹️ Data collection stopped")
                
                # Disable auto-recovery
                if self._recovery_coordinator:
                    self._recovery_coordinator.disable_auto_recovery()
                    print("⏹️ Auto-recovery disabled")
                
                # Stop health monitor
                if self._health_monitor:
                    self._health_monitor.stop()
                    print("⏹️ Health monitoring stopped")
                
                # Cleanup historical data
                if self._historical_store:
                    deleted = self._historical_store.cleanup_old_data()
                    print(f"🧹 Cleaned up {deleted} old records")
                
                self._is_running = False
                
                uptime = time.time() - self._start_time
                print(f"\n✅ System stopped gracefully (uptime: {uptime:.1f}s)")
        
        except Exception as e:
            print(f"❌ Shutdown error: {e}")
    
    def get_status(self) -> SystemStatus:
        """Get complete system status
        
        Returns:
            SystemStatus object
        """
        uptime = time.time() - self._start_time if self._is_running else 0.0
        
        # Get statistics
        total_errors = 0
        total_recoveries = 0
        total_checks = 0
        success_rate = 0.0
        
        if self._historical_store:
            try:
                counts = self._historical_store.get_record_counts()
                total_checks = counts.get('health_records', 0)
                total_errors = counts.get('error_records', 0)
                total_recoveries = counts.get('recovery_records', 0)
                
                if total_checks > 0:
                    success_rate = ((total_checks - total_errors) / total_checks) * 100
            except:
                pass
        
        # Get performance metrics
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)
        
        return SystemStatus(
            is_running=self._is_running,
            uptime=uptime,
            error_reporter_active=self._error_reporter is not None,
            health_monitor_active=self._health_monitor is not None and self._health_monitor.is_running(),
            recovery_coordinator_active=self._recovery_coordinator is not None,
            historical_store_active=self._historical_store is not None,
            data_aggregator_active=self._data_aggregator is not None and self._data_aggregator.is_running(),
            total_errors=total_errors,
            total_recoveries=total_recoveries,
            total_health_checks=total_checks,
            success_rate=success_rate,
            memory_usage_mb=memory_mb,
            cpu_usage_percent=cpu_percent
        )
    
    def print_status(self):
        """Print formatted system status"""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("MONITORING SYSTEM STATUS")
        print("="*60)
        print(f"Status: {'RUNNING ▶️' if status.is_running else 'STOPPED ⏹️'}")
        print(f"Uptime: {status.uptime:.1f}s")
        print()
        print("Components:")
        print(f"  ErrorReporter:        {'ACTIVE ✅' if status.error_reporter_active else 'INACTIVE ❌'}")
        print(f"  HealthMonitor:        {'ACTIVE ✅' if status.health_monitor_active else 'INACTIVE ❌'}")
        print(f"  RecoveryCoordinator:  {'ACTIVE ✅' if status.recovery_coordinator_active else 'INACTIVE ❌'}")
        print(f"  HistoricalStore:      {'ACTIVE ✅' if status.historical_store_active else 'INACTIVE ❌'}")
        print(f"  DataAggregator:       {'ACTIVE ✅' if status.data_aggregator_active else 'INACTIVE ❌'}")
        print()
        print("Statistics:")
        print(f"  Health Checks: {status.total_health_checks}")
        print(f"  Errors:        {status.total_errors}")
        print(f"  Recoveries:    {status.total_recoveries}")
        print(f"  Success Rate:  {status.success_rate:.1f}%")
        print()
        print("Performance:")
        print(f"  Memory Usage:  {status.memory_usage_mb:.1f} MB")
        print(f"  CPU Usage:     {status.cpu_usage_percent:.1f}%")
        print("="*60)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics
        
        Returns:
            Performance statistics dictionary
        """
        return self._performance_stats.copy()
    
    def _get_retention_policy(self, days: int) -> 'DataRetentionPolicy':
        """Convert days to retention policy
        
        Args:
            days: Number of days
        
        Returns:
            DataRetentionPolicy
        """
        if days <= 7:
            return DataRetentionPolicy.DAYS_7
        elif days <= 30:
            return DataRetentionPolicy.DAYS_30
        elif days <= 90:
            return DataRetentionPolicy.DAYS_90
        elif days <= 365:
            return DataRetentionPolicy.DAYS_365
        else:
            return DataRetentionPolicy.UNLIMITED
    
    # Accessors for components
    
    def get_error_reporter(self) -> Optional[ErrorReporter]:
        """Get error reporter instance"""
        return self._error_reporter
    
    def get_health_monitor(self) -> Optional[SystemHealthMonitor]:
        """Get health monitor instance"""
        return self._health_monitor
    
    def get_recovery_coordinator(self) -> Optional[RecoveryCoordinator]:
        """Get recovery coordinator instance"""
        return self._recovery_coordinator
    
    def get_historical_store(self) -> Optional[HistoricalDataStore]:
        """Get historical store instance"""
        return self._historical_store
    
    def get_data_aggregator(self) -> Optional[DataAggregator]:
        """Get data aggregator instance"""
        return self._data_aggregator
    
    def is_running(self) -> bool:
        """Check if system is running"""
        return self._is_running


# Testing
if __name__ == '__main__':
    print("Monitoring System Integrator Test")
    print("=" * 60)
    
    # Create integrator
    config = MonitoringConfig(
        health_check_interval=2.0,
        collection_interval=5.0
    )
    
    integrator = MonitoringSystemIntegrator(config)
    
    # Initialize
    print("\nInitializing...")
    if integrator.initialize():
        print("\u2705 Initialization successful\n")
    else:
        print("❌ Initialization failed")
        exit(1)
    
    # Start
    print("Starting...")
    if integrator.start():
        # Print status
        integrator.print_status()
        
        # Run for a bit
        print("\nRunning for 10 seconds...")
        time.sleep(10)
        
        # Print final status
        integrator.print_status()
        
        # Stop
        integrator.stop()
    else:
        print("❌ Startup failed")
