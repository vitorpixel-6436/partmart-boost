#!/usr/bin/env python3
"""Backend Service Manager

Version: 0.3.5e (package 3.9a, stage 7.2/7.7)

Manages all backend services and integrates with BackendBridge.

Package 3.9a Stage 7.2: Backend services integration.

Features:
- Service lifecycle management
- Command handler registration
- Query handler registration
- Health monitoring
"""
import time
import threading
from typing import Optional, Dict, Any

try:
    from backend_bridge import BackendBridge, Command, CommandResult, QueryResult
    from performance_monitor import PerformanceMonitor
    BRIDGE_AVAILABLE = True
except ImportError as e:
    print(f"[BackendServiceManager] Import error: {e}")
    BRIDGE_AVAILABLE = False


class BackendServiceManager:
    """Backend Service Manager
    
    Manages all backend services and integrates with BackendBridge.
    
    Services:
    - PerformanceMonitor: Performance tracking and analytics
    - ConfigManager: Configuration management (Stage 7.3)
    - ResourceManager: Resource management (Stage 7.3)
    
    Responsibilities:
    - Initialize services
    - Register command handlers
    - Register query handlers
    - Manage service lifecycle
    - Monitor service health
    
    Usage:
        manager = BackendServiceManager()
        manager.initialize()
        
        # Services are now running
        monitor = manager.get_monitor()
    """
    
    def __init__(self):
        """Initialize service manager"""
        self._bridge: Optional[BackendBridge] = None
        self._monitor: Optional[PerformanceMonitor] = None
        self._config = None
        self._resource_manager = None
        
        self._initialized = False
        self._monitoring_active = False
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        print("[BackendServiceManager] Initialized")
    
    def initialize(self) -> bool:
        """Initialize all services
        
        Returns:
            True if successful
        """
        if not BRIDGE_AVAILABLE:
            print("[BackendServiceManager] Bridge not available")
            return False
        
        try:
            # Get BackendBridge
            self._bridge = BackendBridge.get_instance()
            print("[BackendServiceManager] BackendBridge connected")
            
            # Initialize PerformanceMonitor
            self._init_performance_monitor()
            
            # Register handlers
            self._register_command_handlers()
            self._register_query_handlers()
            
            self._initialized = True
            print("[BackendServiceManager] ✅ All services initialized")
            
            return True
        
        except Exception as e:
            print(f"[BackendServiceManager] ❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_performance_monitor(self):
        """Initialize PerformanceMonitor"""
        try:
            # Import monitor manager (mock for now)
            from monitors.mock_manager import MockMonitorManager
            from data_bus import DataBus
            
            manager = MockMonitorManager()
            databus = DataBus.get_instance()
            
            self._monitor = PerformanceMonitor(manager, databus)
            
            print("[BackendServiceManager] ✅ PerformanceMonitor initialized")
        
        except ImportError:
            print("[BackendServiceManager] ⚠️ Using mock PerformanceMonitor")
            
            # Create minimal mock
            class MockPerformanceMonitor:
                def __init__(self):
                    self.running = False
                    self._data = {
                        'fps': 60.0,
                        'cpu': 50.0,
                        'gpu': 60.0,
                        'memory': 70.0,
                    }
                
                def start(self):
                    self.running = True
                
                def stop(self):
                    self.running = False
                
                def update(self):
                    pass
                
                def get_current_metrics(self):
                    return self._data
                
                def get_performance_score(self):
                    return 75.0
                
                def get_current_bottleneck(self):
                    return None
                
                def get_correlation_stats(self):
                    return {'cpu_fps': 0.5, 'gpu_fps': 0.7}
                
                def get_efficiency_report(self):
                    return {'cpu': 80.0, 'gpu': 85.0, 'overall': 82.5}
                
                def get_performance_trends(self):
                    return {
                        'fps_trend': 'stable',
                        'load_trend': 'stable',
                        'thermal_trend': 'stable',
                    }
            
            self._monitor = MockPerformanceMonitor()
    
    def _register_command_handlers(self):
        """Register command handlers"""
        if not self._bridge or not self._monitor:
            return
        
        # Start monitoring
        self._bridge.register_command_handler(
            'start_monitoring',
            self._handle_start_monitoring
        )
        
        # Stop monitoring
        self._bridge.register_command_handler(
            'stop_monitoring',
            self._handle_stop_monitoring
        )
        
        # Get metrics
        self._bridge.register_command_handler(
            'get_metrics',
            self._handle_get_metrics
        )
        
        # Clear history
        self._bridge.register_command_handler(
            'clear_history',
            self._handle_clear_history
        )
        
        print("[BackendServiceManager] ✅ Registered 4 command handlers")
    
    def _register_query_handlers(self):
        """Register query handlers"""
        if not self._bridge or not self._monitor:
            return
        
        # Performance metrics
        self._bridge.register_query_handler(
            'performance_metrics',
            self._handle_query_metrics
        )
        
        # Bottleneck info
        self._bridge.register_query_handler(
            'bottleneck_info',
            self._handle_query_bottleneck
        )
        
        # Correlation stats
        self._bridge.register_query_handler(
            'correlation_stats',
            self._handle_query_correlation
        )
        
        # Efficiency report
        self._bridge.register_query_handler(
            'efficiency_report',
            self._handle_query_efficiency
        )
        
        # Performance trends
        self._bridge.register_query_handler(
            'performance_trends',
            self._handle_query_trends
        )
        
        print("[BackendServiceManager] ✅ Registered 5 query handlers")
    
    # ========================================================================
    # Command Handlers
    # ========================================================================
    
    def _handle_start_monitoring(self, command: Command) -> CommandResult:
        """Handle start monitoring command"""
        try:
            interval = command.params.get('interval', 100)
            
            # Start monitor
            self._monitor.start()
            
            # Start update thread
            if not self._monitoring_active:
                self._monitoring_active = True
                self._stop_event.clear()
                
                self._update_thread = threading.Thread(
                    target=self._monitoring_loop,
                    args=(interval,),
                    daemon=True
                )
                self._update_thread.start()
            
            # Publish event
            self._bridge.publish_event('monitoring_started', {
                'interval': interval,
            })
            
            print(f"[BackendServiceManager] Monitoring started ({interval}ms)")
            
            return CommandResult(
                request_id=command.request_id,
                success=True,
                data={'status': 'started', 'interval': interval}
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    def _handle_stop_monitoring(self, command: Command) -> CommandResult:
        """Handle stop monitoring command"""
        try:
            # Stop monitor
            self._monitor.stop()
            
            # Stop update thread
            if self._monitoring_active:
                self._monitoring_active = False
                self._stop_event.set()
                
                if self._update_thread:
                    self._update_thread.join(timeout=1.0)
            
            # Publish event
            self._bridge.publish_event('monitoring_stopped', {})
            
            print("[BackendServiceManager] Monitoring stopped")
            
            return CommandResult(
                request_id=command.request_id,
                success=True,
                data={'status': 'stopped'}
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    def _handle_get_metrics(self, command: Command) -> CommandResult:
        """Handle get metrics command"""
        try:
            metrics = self._monitor.get_current_metrics()
            
            return CommandResult(
                request_id=command.request_id,
                success=True,
                data=metrics
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    def _handle_clear_history(self, command: Command) -> CommandResult:
        """Handle clear history command"""
        try:
            if hasattr(self._monitor, 'reset'):
                self._monitor.reset()
            
            return CommandResult(
                request_id=command.request_id,
                success=True,
                data={'status': 'cleared'}
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    # Query Handlers
    # ========================================================================
    
    def _handle_query_metrics(self, params: Dict[str, Any]) -> QueryResult:
        """Handle metrics query"""
        try:
            metrics = self._monitor.get_current_metrics()
            
            return QueryResult(
                success=True,
                data=metrics,
                row_count=1
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def _handle_query_bottleneck(self, params: Dict[str, Any]) -> QueryResult:
        """Handle bottleneck query"""
        try:
            bottleneck = self._monitor.get_current_bottleneck()
            
            if bottleneck:
                data = {
                    'component': bottleneck.component,
                    'severity': bottleneck.severity,
                    'load': bottleneck.load,
                }
            else:
                data = None
            
            return QueryResult(
                success=True,
                data=data,
                row_count=1 if data else 0
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def _handle_query_correlation(self, params: Dict[str, Any]) -> QueryResult:
        """Handle correlation stats query"""
        try:
            stats = self._monitor.get_correlation_stats()
            
            return QueryResult(
                success=True,
                data=stats,
                row_count=1
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def _handle_query_efficiency(self, params: Dict[str, Any]) -> QueryResult:
        """Handle efficiency report query"""
        try:
            efficiency = self._monitor.get_efficiency_report()
            
            return QueryResult(
                success=True,
                data=efficiency,
                row_count=1
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def _handle_query_trends(self, params: Dict[str, Any]) -> QueryResult:
        """Handle trends query"""
        try:
            trends = self._monitor.get_performance_trends()
            
            return QueryResult(
                success=True,
                data=trends,
                row_count=1
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    # Monitoring Loop
    # ========================================================================
    
    def _monitoring_loop(self, interval_ms: int):
        """Background monitoring loop
        
        Args:
            interval_ms: Update interval in milliseconds
        """
        interval_sec = interval_ms / 1000.0
        
        print(f"[BackendServiceManager] Monitoring loop started ({interval_ms}ms)")
        
        while not self._stop_event.is_set():
            try:
                # Update monitor
                self._monitor.update()
                
                # Get metrics
                metrics = self._monitor.get_current_metrics()
                
                # Publish data
                self._bridge.publish_data('performance_metrics', metrics)
                
                # Sleep
                time.sleep(interval_sec)
            
            except Exception as e:
                print(f"[BackendServiceManager] Monitoring error: {e}")
                time.sleep(interval_sec)
        
        print("[BackendServiceManager] Monitoring loop stopped")
    
    # ========================================================================
    # Public API
    # ========================================================================
    
    def get_monitor(self) -> Optional[PerformanceMonitor]:
        """Get PerformanceMonitor instance
        
        Returns:
            PerformanceMonitor or None
        """
        return self._monitor
    
    def is_initialized(self) -> bool:
        """Check if initialized
        
        Returns:
            True if initialized
        """
        return self._initialized
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active
        
        Returns:
            True if monitoring
        """
        return self._monitoring_active
    
    def shutdown(self):
        """Shutdown all services"""
        print("[BackendServiceManager] Shutting down...")
        
        # Stop monitoring
        if self._monitoring_active:
            self._monitoring_active = False
            self._stop_event.set()
            
            if self._update_thread:
                self._update_thread.join(timeout=2.0)
        
        # Stop monitor
        if self._monitor:
            self._monitor.stop()
        
        print("[BackendServiceManager] Shutdown complete")
