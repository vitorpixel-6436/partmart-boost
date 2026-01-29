#!/usr/bin/env python3
"""Application Integration Layer

Version: 0.3.5e (package 3.9a, stage 7/7)

Integration layer that connects all systems together.

Package 3.9a Stage 7: Integration & Debug
- Initialize all systems
- Register handlers
- Connect components
- Setup Qt signals
"""
import sys
from typing import Optional, Dict, Any

print("[AppIntegration] Importing core systems...")

try:
    from core.backend_bridge import BackendBridge, Command, CommandResult, QueryResult
    from core.command_system import (
        StartMonitoringCommand,
        StopMonitoringCommand,
        UpdateSettingsCommand,
        GetMetricsCommand,
        ClearHistoryCommand,
    )
    from core.qt_signal_bridge import QtSignalBridge
    BRIDGE_AVAILABLE = True
except ImportError as e:
    print(f"[AppIntegration] Bridge import error: {e}")
    BRIDGE_AVAILABLE = False

try:
    from monitors.performance_monitor import PerformanceMonitor, PerformanceMetrics
    MONITOR_AVAILABLE = True
except ImportError as e:
    print(f"[AppIntegration] Monitor import error: {e}")
    MONITOR_AVAILABLE = False

try:
    from core.data_bus import PerformanceDataBus
    DATABUS_AVAILABLE = True
except ImportError as e:
    print(f"[AppIntegration] DataBus import error: {e}")
    DATABUS_AVAILABLE = False


class AppIntegrator:
    """Application Integrator
    
    Connects all systems together:
    - BackendBridge
    - PerformanceMonitor  
    - CommandSystem
    - QuerySystem
    - QtSignalBridge
    - DataBus
    
    Usage:
        integrator = AppIntegrator()
        integrator.initialize()
        
        # Now all systems are connected
        bridge = BackendBridge.get_instance()
        command = StartMonitoringCommand()
        bridge.execute_command(command)
    """
    
    def __init__(self):
        """Initialize integrator"""
        self.bridge: Optional[BackendBridge] = None
        self.qt_signals: Optional[QtSignalBridge] = None
        self.monitor: Optional[PerformanceMonitor] = None
        self.data_bus: Optional[PerformanceDataBus] = None
        self.initialized = False
        
        print("[AppIntegrator] Created (Stage 7)")
    
    def initialize(self) -> bool:
        """Initialize all systems
        
        Returns:
            True if successful, False otherwise
        """
        if self.initialized:
            print("[AppIntegrator] Already initialized")
            return True
        
        try:
            print("[AppIntegrator] Initializing systems...")
            
            # Step 1: Create BackendBridge
            if not self._init_backend_bridge():
                return False
            
            # Step 2: Create QtSignalBridge
            if not self._init_qt_signals():
                return False
            
            # Step 3: Create PerformanceMonitor
            if not self._init_performance_monitor():
                return False
            
            # Step 4: Create DataBus
            if not self._init_data_bus():
                return False
            
            # Step 5: Register command handlers
            if not self._register_command_handlers():
                return False
            
            # Step 6: Register query handlers
            if not self._register_query_handlers():
                return False
            
            # Step 7: Connect systems
            if not self._connect_systems():
                return False
            
            self.initialized = True
            print("[AppIntegrator] ✅ All systems initialized!")
            return True
        
        except Exception as e:
            print(f"[AppIntegrator] ❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _init_backend_bridge(self) -> bool:
        """Initialize BackendBridge"""
        if not BRIDGE_AVAILABLE:
            print("[AppIntegrator] BackendBridge not available")
            return False
        
        try:
            self.bridge = BackendBridge.get_instance()
            print("[AppIntegrator] ✅ BackendBridge initialized")
            return True
        except Exception as e:
            print(f"[AppIntegrator] BackendBridge init error: {e}")
            return False
    
    def _init_qt_signals(self) -> bool:
        """Initialize QtSignalBridge"""
        if not BRIDGE_AVAILABLE:
            return False
        
        try:
            self.qt_signals = QtSignalBridge()
            
            # Connect to BackendBridge
            if self.bridge:
                self.bridge.set_qt_signals(self.qt_signals)
            
            print("[AppIntegrator] ✅ QtSignalBridge initialized")
            return True
        except Exception as e:
            print(f"[AppIntegrator] QtSignalBridge init error: {e}")
            # Qt not available - not critical
            return True
    
    def _init_performance_monitor(self) -> bool:
        """Initialize PerformanceMonitor"""
        if not MONITOR_AVAILABLE:
            print("[AppIntegrator] PerformanceMonitor not available")
            return False
        
        try:
            self.monitor = PerformanceMonitor()
            print("[AppIntegrator] ✅ PerformanceMonitor initialized")
            return True
        except Exception as e:
            print(f"[AppIntegrator] PerformanceMonitor init error: {e}")
            return False
    
    def _init_data_bus(self) -> bool:
        """Initialize DataBus"""
        if not DATABUS_AVAILABLE:
            print("[AppIntegrator] DataBus not available")
            return True  # Not critical
        
        try:
            self.data_bus = PerformanceDataBus.get_instance()
            print("[AppIntegrator] ✅ DataBus initialized")
            return True
        except Exception as e:
            print(f"[AppIntegrator] DataBus init error: {e}")
            return True  # Not critical
    
    def _register_command_handlers(self) -> bool:
        """Register command handlers"""
        if not self.bridge or not self.monitor:
            return False
        
        try:
            # Start monitoring command
            self.bridge.register_command_handler(
                'start_monitoring',
                self._handle_start_monitoring
            )
            
            # Stop monitoring command
            self.bridge.register_command_handler(
                'stop_monitoring',
                self._handle_stop_monitoring
            )
            
            # Get metrics command
            self.bridge.register_command_handler(
                'get_metrics',
                self._handle_get_metrics
            )
            
            # Update settings command
            self.bridge.register_command_handler(
                'update_settings',
                self._handle_update_settings
            )
            
            # Clear history command
            self.bridge.register_command_handler(
                'clear_history',
                self._handle_clear_history
            )
            
            print("[AppIntegrator] ✅ Command handlers registered")
            return True
        
        except Exception as e:
            print(f"[AppIntegrator] Command handler registration error: {e}")
            return False
    
    def _register_query_handlers(self) -> bool:
        """Register query handlers"""
        if not self.bridge or not self.monitor:
            return False
        
        try:
            # Performance metrics query
            self.bridge.register_query_handler(
                'performance_metrics',
                self._handle_metrics_query
            )
            
            # System stats query
            self.bridge.register_query_handler(
                'system_stats',
                self._handle_stats_query
            )
            
            # Health status query
            self.bridge.register_query_handler(
                'health_status',
                self._handle_health_query
            )
            
            print("[AppIntegrator] ✅ Query handlers registered")
            return True
        
        except Exception as e:
            print(f"[AppIntegrator] Query handler registration error: {e}")
            return False
    
    def _connect_systems(self) -> bool:
        """Connect all systems together"""
        try:
            # Subscribe DataBus to monitor events
            if self.data_bus and self.monitor:
                self.data_bus.subscribe('performance_metrics', self._on_metrics_updated)
            
            # Subscribe Bridge to DataBus events
            if self.bridge and self.data_bus:
                self.data_bus.subscribe('performance_metrics', 
                                        lambda topic, data: self.bridge.publish_data('performance_metrics', data))
            
            print("[AppIntegrator] ✅ Systems connected")
            return True
        
        except Exception as e:
            print(f"[AppIntegrator] Connection error: {e}")
            return True  # Not critical
    
    # ========================================================================
    # COMMAND HANDLERS
    # ========================================================================
    
    def _handle_start_monitoring(self, command: Command) -> CommandResult:
        """Handle start monitoring command"""
        try:
            if not self.monitor:
                return CommandResult(
                    request_id=command.request_id,
                    success=False,
                    error="Monitor not available"
                )
            
            # Start monitor
            success = self.monitor.start()
            
            if success:
                # Publish event
                if self.bridge:
                    self.bridge.publish_event('monitoring_started', {
                        'interval': command.params.get('interval', 100),
                    })
                
                return CommandResult(
                    request_id=command.request_id,
                    success=True,
                    data={'status': 'started'}
                )
            else:
                return CommandResult(
                    request_id=command.request_id,
                    success=False,
                    error="Failed to start monitor"
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
            if not self.monitor:
                return CommandResult(
                    request_id=command.request_id,
                    success=False,
                    error="Monitor not available"
                )
            
            # Stop monitor
            self.monitor.stop()
            
            # Publish event
            if self.bridge:
                self.bridge.publish_event('monitoring_stopped', {})
            
            return CommandResult(
                request_id=command.request_id,
                success=True
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
            if not self.monitor:
                return CommandResult(
                    request_id=command.request_id,
                    success=False,
                    error="Monitor not available"
                )
            
            # Get metrics
            metrics = self.monitor.get_metrics()
            
            if metrics:
                return CommandResult(
                    request_id=command.request_id,
                    success=True,
                    data={
                        'fps': metrics.fps,
                        'cpu': metrics.cpu_util,
                        'gpu': metrics.gpu_util,
                        'memory': metrics.memory_used,
                        'temperature': metrics.temperature,
                    }
                )
            else:
                return CommandResult(
                    request_id=command.request_id,
                    success=False,
                    error="No metrics available"
                )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    def _handle_update_settings(self, command: Command) -> CommandResult:
        """Handle update settings command"""
        try:
            settings = command.params.get('settings', {})
            
            # TODO: Update settings via ConfigManager
            
            # Publish event
            if self.bridge:
                self.bridge.publish_event('settings_updated', settings)
            
            return CommandResult(
                request_id=command.request_id,
                success=True,
                data={'settings': settings}
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
            # Clear bridge history
            if self.bridge:
                self.bridge.clear_history()
            
            return CommandResult(
                request_id=command.request_id,
                success=True
            )
        
        except Exception as e:
            return CommandResult(
                request_id=command.request_id,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    # QUERY HANDLERS
    # ========================================================================
    
    def _handle_metrics_query(self, params: Dict[str, Any]) -> QueryResult:
        """Handle performance metrics query"""
        try:
            if not self.monitor:
                return QueryResult(
                    success=False,
                    error="Monitor not available"
                )
            
            # Get current metrics
            metrics = self.monitor.get_metrics()
            
            if metrics:
                data = {
                    'fps': metrics.fps,
                    'frame_time': metrics.frame_time,
                    'cpu': metrics.cpu_util,
                    'gpu': metrics.gpu_util,
                    'memory_used': metrics.memory_used,
                    'memory_total': metrics.memory_total,
                    'temperature': metrics.temperature,
                    'power': metrics.power_draw,
                }
                
                return QueryResult(
                    success=True,
                    data=data,
                    row_count=1
                )
            else:
                return QueryResult(
                    success=False,
                    error="No metrics available"
                )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    def _handle_stats_query(self, params: Dict[str, Any]) -> QueryResult:
        """Handle system stats query"""
        try:
            if not self.monitor:
                return QueryResult(
                    success=False,
                    error="Monitor not available"
                )
            
            # Get health stats
            stats = self.monitor.get_health_stats()
            
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
    
    def _handle_health_query(self, params: Dict[str, Any]) -> QueryResult:
        """Handle health status query"""
        try:
            # Get health status from all systems
            health = {
                'bridge': self.bridge is not None,
                'monitor': self.monitor is not None and self.monitor._running,
                'qt_signals': self.qt_signals is not None,
                'data_bus': self.data_bus is not None,
                'integrated': self.initialized,
            }
            
            return QueryResult(
                success=True,
                data=health,
                row_count=1
            )
        
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def _on_metrics_updated(self, topic: str, data: Any):
        """Handle metrics update from DataBus"""
        try:
            if self.bridge:
                self.bridge.publish_event('metrics_updated', data)
        except Exception as e:
            print(f"[AppIntegrator] Metrics update error: {e}")
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def get_bridge(self) -> Optional[BackendBridge]:
        """Get BackendBridge instance"""
        return self.bridge
    
    def get_monitor(self) -> Optional[PerformanceMonitor]:
        """Get PerformanceMonitor instance"""
        return self.monitor
    
    def get_qt_signals(self) -> Optional[QtSignalBridge]:
        """Get QtSignalBridge instance"""
        return self.qt_signals
    
    def is_ready(self) -> bool:
        """Check if all systems are ready"""
        return self.initialized and self.bridge is not None and self.monitor is not None


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_integrator_instance: Optional[AppIntegrator] = None

def get_integrator() -> AppIntegrator:
    """Get or create AppIntegrator singleton"""
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = AppIntegrator()
    return _integrator_instance


def initialize_app() -> bool:
    """Initialize application (convenience function)
    
    Returns:
        True if successful, False otherwise
    """
    integrator = get_integrator()
    return integrator.initialize()
