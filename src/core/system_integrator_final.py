#!/usr/bin/env python3
"""System Integrator Final - Complete system integration

Version: 0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)

Package 3.9a Stage 7.7b.9.1: Final system integration.

Features:
- Unified startup/shutdown
- All systems integration
- Health checks
- Status reporting
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time

try:
    from core.config_manager import ConfigManager, get_config_manager
except ImportError:
    ConfigManager = None
    get_config_manager = None

try:
    from core.error_reporter import ErrorReporter
    from core.system_health_monitor import SystemHealthMonitor
    from core.recovery_coordinator import RecoveryCoordinator
    from core.historical_data_store import HistoricalDataStore, DataRetentionPolicy
    from core.data_aggregator import DataAggregator, AggregationConfig
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False


@dataclass
class SystemStatus:
    """System status information"""
    initialized: bool = False
    running: bool = False
    error_count: int = 0
    component_count: int = 0
    healthy_count: int = 0
    uptime: float = 0.0
    version: str = "0.3.5g"
    package: str = "3.9a"
    stage: str = "7.7b.9.1"


class SystemIntegratorFinal:
    """Complete system integration
    
    v0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)
    
    Integrates:
    - Error reporting
    - Health monitoring
    - Recovery coordination
    - Historical data storage
    - Data aggregation
    - Configuration management
    """
    
    def __init__(self):
        self.config_manager: Optional[ConfigManager] = None
        self.error_reporter: Optional[ErrorReporter] = None
        self.health_monitor: Optional[SystemHealthMonitor] = None
        self.recovery_coordinator: Optional[RecoveryCoordinator] = None
        self.historical_store: Optional[HistoricalDataStore] = None
        self.data_aggregator: Optional[DataAggregator] = None
        
        self._start_time = time.time()
        self._initialized = False
        self._running = False
    
    def initialize(self) -> bool:
        """Initialize all systems
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        try:
            print("Initializing PartMart Boost...")
            
            # Load configuration
            if get_config_manager:
                self.config_manager = get_config_manager()
                config = self.config_manager.config
                print(f"✅ Configuration loaded: v{config.version}")
            else:
                print("⚠️  ConfigManager not available")
            
            if not MONITORING_AVAILABLE:
                print("⚠️  Monitoring systems not available")
                self._initialized = True
                return True
            
            # Initialize error reporter
            self.error_reporter = ErrorReporter()
            print("✅ Error reporter initialized")
            
            # Initialize health monitor
            check_interval = 5.0
            if self.config_manager:
                check_interval = self.config_manager.get(
                    'monitoring.check_interval',
                    5.0
                )
            
            self.health_monitor = SystemHealthMonitor(
                check_interval=check_interval,
                error_reporter=self.error_reporter
            )
            print(f"✅ Health monitor initialized (interval: {check_interval}s)")
            
            # Initialize recovery coordinator
            self.recovery_coordinator = RecoveryCoordinator(
                health_monitor=self.health_monitor,
                error_reporter=self.error_reporter
            )
            print("✅ Recovery coordinator initialized")
            
            # Initialize historical data store
            if self.config_manager and self.config_manager.get('historical_data.enabled', True):
                retention_days = self.config_manager.get('historical_data.retention_days', 30)
                
                # Map retention days to policy
                if retention_days <= 7:
                    policy = DataRetentionPolicy.DAYS_7
                elif retention_days <= 30:
                    policy = DataRetentionPolicy.DAYS_30
                elif retention_days <= 90:
                    policy = DataRetentionPolicy.DAYS_90
                else:
                    policy = DataRetentionPolicy.DAYS_365
                
                self.historical_store = HistoricalDataStore(
                    db_path="data/monitoring_history.db",
                    retention_policy=policy
                )
                print(f"✅ Historical data store initialized ({retention_days} days)")
                
                # Initialize data aggregator
                if self.config_manager:
                    agg_config = AggregationConfig(
                        collection_interval=self.config_manager.get(
                            'historical_data.collection_interval', 60.0
                        ),
                        aggregation_interval=self.config_manager.get(
                            'historical_data.aggregation_interval', 3600.0
                        ),
                        enable_health_collection=self.config_manager.get(
                            'historical_data.enable_health_collection', True
                        ),
                        enable_error_collection=self.config_manager.get(
                            'historical_data.enable_error_collection', True
                        ),
                        enable_recovery_collection=self.config_manager.get(
                            'historical_data.enable_recovery_collection', True
                        )
                    )
                else:
                    agg_config = AggregationConfig()
                
                self.data_aggregator = DataAggregator(
                    historical_store=self.historical_store,
                    health_monitor=self.health_monitor,
                    error_reporter=self.error_reporter,
                    recovery_coordinator=self.recovery_coordinator,
                    config=agg_config
                )
                print("✅ Data aggregator initialized")
            else:
                print("⚠️  Historical data disabled in configuration")
            
            self._initialized = True
            print("\n✅ System initialization complete!\n")
            return True
        
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start(self) -> bool:
        """Start all systems
        
        Returns:
            True if started successfully
        """
        if not self._initialized:
            if not self.initialize():
                return False
        
        if self._running:
            return True
        
        try:
            print("Starting PartMart Boost systems...")
            
            if not MONITORING_AVAILABLE:
                self._running = True
                return True
            
            # Start health monitoring
            if self.health_monitor:
                self.health_monitor.start()
                print("✅ Health monitoring started")
            
            # Enable auto-recovery
            if self.recovery_coordinator:
                auto_recovery = True
                if self.config_manager:
                    auto_recovery = self.config_manager.get(
                        'monitoring.enable_auto_recovery', True
                    )
                
                if auto_recovery:
                    self.recovery_coordinator.enable_auto_recovery()
                    print("✅ Auto-recovery enabled")
            
            # Start data collection
            if self.data_aggregator:
                self.data_aggregator.start_collection()
                print("✅ Data collection started")
            
            self._running = True
            self._start_time = time.time()
            print("\n✅ All systems running!\n")
            return True
        
        except Exception as e:
            print(f"❌ Start failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop(self) -> bool:
        """Stop all systems
        
        Returns:
            True if stopped successfully
        """
        if not self._running:
            return True
        
        try:
            print("\nStopping PartMart Boost systems...")
            
            if not MONITORING_AVAILABLE:
                self._running = False
                return True
            
            # Stop data collection
            if self.data_aggregator:
                self.data_aggregator.stop_collection()
                print("✅ Data collection stopped")
            
            # Disable auto-recovery
            if self.recovery_coordinator:
                self.recovery_coordinator.disable_auto_recovery()
                print("✅ Auto-recovery disabled")
            
            # Stop health monitoring
            if self.health_monitor:
                self.health_monitor.stop()
                print("✅ Health monitoring stopped")
            
            # Save configuration
            if self.config_manager:
                if self.config_manager.save():
                    print("✅ Configuration saved")
            
            self._running = False
            print("\n✅ All systems stopped cleanly\n")
            return True
        
        except Exception as e:
            print(f"❌ Stop failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_status(self) -> SystemStatus:
        """Get system status
        
        Returns:
            SystemStatus object
        """
        status = SystemStatus(
            initialized=self._initialized,
            running=self._running,
            uptime=time.time() - self._start_time if self._running else 0.0
        )
        
        if self.health_monitor and MONITORING_AVAILABLE:
            health = self.health_monitor.get_system_health()
            status.component_count = health.get('total_components', 0)
            status.healthy_count = health.get('healthy_count', 0)
        
        if self.error_reporter and MONITORING_AVAILABLE:
            errors = self.error_reporter.get_errors()
            status.error_count = len(errors)
        
        return status
    
    def print_status(self):
        """Print system status"""
        status = self.get_status()
        
        print("="*60)
        print(f"PartMart Boost v{status.version} (Package {status.package})")
        print(f"Stage: {status.stage}")
        print("="*60)
        print(f"Initialized: {status.initialized}")
        print(f"Running: {status.running}")
        print(f"Uptime: {status.uptime:.1f}s")
        print(f"Components: {status.healthy_count}/{status.component_count} healthy")
        print(f"Errors: {status.error_count}")
        print("="*60)
        print()


# Testing
if __name__ == '__main__':
    integrator = SystemIntegratorFinal()
    
    # Initialize
    if integrator.initialize():
        print("✅ Initialization successful")
    
    # Start
    if integrator.start():
        print("✅ Start successful")
    
    # Print status
    integrator.print_status()
    
    # Wait a bit
    import time
    time.sleep(2)
    
    # Stop
    if integrator.stop():
        print("✅ Stop successful")
