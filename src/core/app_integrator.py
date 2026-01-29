#!/usr/bin/env python3
"""Application Integrator

Version: 0.3.5g (package 3.9a, stage 7.5/7.7)

Unified access point for all application components.

Package 3.9a Stage 7.5: Advanced monitoring integration.

Features:
- Unified component access
- Lazy loading
- Health monitoring
- Graceful degradation
- Service manager access
- DataBus pub/sub system
- Performance history and analytics (NEW)
"""
import time
from typing import Optional, Dict, Any
import threading


class AppIntegrator:
    """Application Integration Layer
    
    Provides unified access to all application components.
    
    Components:
    - BackendBridge: API for backend operations
    - QtSignalBridge: Thread-safe Qt signals
    - BackendServiceManager: Backend services
    - PerformanceMonitor: Performance monitoring
    - ConfigManager: Configuration management
    - DataBus: Event-based pub/sub system
    - MonitoringIntegration: Performance history and analytics (NEW in Stage 7.5)
    
    Usage:
        integrator = AppIntegrator()
        
        # Get components
        bridge = integrator.get_bridge()
        qt_signals = integrator.get_qt_signals()
        monitor = integrator.get_monitor()
        bus = integrator.get_data_bus()
        monitoring = integrator.get_monitoring_integration()  # NEW
        
        # Get analytics report
        report = monitoring.get_latest_report()
        
        # Check health
        health = integrator.get_health()
        
        # Check if ready
        if integrator.is_ready():
            # Use components
    """
    
    _instance: Optional['AppIntegrator'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize integrator"""
        self._bridge = None
        self._qt_signals = None
        self._service_manager = None
        self._monitor = None
        self._config = None
        self._data_bus = None
        self._bus_integration = None
        self._monitoring_integration = None
        
        self._initialized = False
        self._init_time = time.perf_counter()
        
        print("[AppIntegrator] Initialized")
        
        # Initialize components
        self._init_components()
    
    def _init_components(self):
        """Initialize components"""
        try:
            # Get BackendBridge
            from backend_bridge import BackendBridge
            self._bridge = BackendBridge.get_instance()
            print("[AppIntegrator] ✅ BackendBridge connected")
        except Exception as e:
            print(f"[AppIntegrator] ⚠️ BackendBridge unavailable: {e}")
        
        try:
            # Get QtSignalBridge from BackendBridge
            if self._bridge:
                self._qt_signals = self._bridge.qt_signals
                if self._qt_signals:
                    print("[AppIntegrator] ✅ QtSignalBridge connected")
                else:
                    print("[AppIntegrator] ⚠️ QtSignalBridge not set")
        except Exception as e:
            print(f"[AppIntegrator] ⚠️ QtSignalBridge error: {e}")
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'AppIntegrator':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def set_service_manager(self, service_manager):
        """Set BackendServiceManager
        
        Args:
            service_manager: BackendServiceManager instance
        """
        self._service_manager = service_manager
        
        # Get monitor from service manager
        if service_manager:
            self._monitor = service_manager.get_monitor()
            print("[AppIntegrator] ✅ ServiceManager connected")
    
    def set_data_bus(self, data_bus):
        """Set DataBus
        
        Args:
            data_bus: DataBus instance
        """
        self._data_bus = data_bus
        print("[AppIntegrator] ✅ DataBus connected")
    
    def set_bus_integration(self, bus_integration):
        """Set DataBusIntegration
        
        Args:
            bus_integration: DataBusIntegration instance
        """
        self._bus_integration = bus_integration
        print("[AppIntegrator] ✅ BusIntegration connected")
    
    def set_monitoring_integration(self, monitoring_integration):
        """Set MonitoringIntegration (Stage 7.5)
        
        Args:
            monitoring_integration: MonitoringIntegration instance
        """
        self._monitoring_integration = monitoring_integration
        print("[AppIntegrator] ✅ MonitoringIntegration connected")
    
    def get_bridge(self):
        """Get BackendBridge
        
        Returns:
            BackendBridge instance or None
        """
        return self._bridge
    
    def get_qt_signals(self):
        """Get QtSignalBridge
        
        Returns:
            QtSignalBridge instance or None
        """
        return self._qt_signals
    
    def get_service_manager(self):
        """Get BackendServiceManager
        
        Returns:
            BackendServiceManager instance or None
        """
        return self._service_manager
    
    def get_monitor(self):
        """Get PerformanceMonitor
        
        Returns:
            PerformanceMonitor instance or None
        """
        return self._monitor
    
    def get_config(self):
        """Get ConfigManager (Stage 7.3+)
        
        Returns:
            ConfigManager instance or None
        """
        return self._config
    
    def get_data_bus(self):
        """Get DataBus
        
        Returns:
            DataBus instance or None
        """
        return self._data_bus
    
    def get_bus_integration(self):
        """Get DataBusIntegration
        
        Returns:
            DataBusIntegration instance or None
        """
        return self._bus_integration
    
    def get_monitoring_integration(self):
        """Get MonitoringIntegration (Stage 7.5)
        
        Returns:
            MonitoringIntegration instance or None
        """
        return self._monitoring_integration
    
    def is_ready(self) -> bool:
        """Check if system is ready
        
        Returns:
            True if all critical components available
        """
        return self._initialized and self._bridge is not None
    
    def get_health(self) -> Dict[str, str]:
        """Get system health status
        
        Returns:
            Dictionary with component health status
        """
        health = {
            'integrator': 'ok' if self._initialized else 'error',
            'bridge': 'ok' if self._bridge else 'unavailable',
            'qt_signals': 'ok' if self._qt_signals else 'unavailable',
            'service_manager': 'ok' if self._service_manager else 'unavailable',
            'monitor': 'ok' if self._monitor else 'unavailable',
            'config': 'pending' if self._config is None else 'ok',
            'data_bus': 'ok' if self._data_bus else 'pending',
            'bus_integration': 'ok' if self._bus_integration else 'pending',
            'monitoring_integration': 'ok' if self._monitoring_integration else 'pending',
        }
        
        return health
    
    def get_uptime(self) -> float:
        """Get uptime in seconds
        
        Returns:
            Uptime in seconds
        """
        return time.perf_counter() - self._init_time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive stats (Stage 7.5)
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'uptime_seconds': self.get_uptime(),
            'ready': self.is_ready(),
            'components': self.get_health(),
        }
        
        # Add DataBus stats if available
        if self._data_bus:
            try:
                stats['bus'] = self._data_bus.get_stats()
            except Exception:
                pass
        
        # Add monitor stats if available
        if self._monitor:
            try:
                stats['monitor'] = {
                    'active': self._monitor.is_monitoring(),
                    'interval_ms': getattr(self._monitor, 'interval_ms', None),
                }
            except Exception:
                pass
        
        # Add monitoring integration stats if available (NEW in Stage 7.5)
        if self._monitoring_integration:
            try:
                history = self._monitoring_integration.get_history()
                if history:
                    stats['history'] = {
                        'samples': history.get_count(),
                        'uptime': history.get_uptime(),
                    }
                
                report = self._monitoring_integration.get_latest_report()
                if report:
                    stats['analytics'] = {
                        'score': report.score,
                        'efficiency': report.efficiency,
                        'bottleneck': report.bottleneck.type.value,
                    }
            except Exception:
                pass
        
        return stats
    
    def print_status(self):
        """Print system status"""
        print("\n" + "="*50)
        print("APPLICATION STATUS")
        print("="*50)
        
        health = self.get_health()
        
        for component, status in health.items():
            if status == 'ok':
                icon = "✅"
            elif status == 'pending':
                icon = "⏳"
            else:
                icon = "❌"
            
            print(f"{icon} {component}: {status}")
        
        print(f"\n⏱️  Uptime: {self.get_uptime():.1f}s")
        print(f"🔄 Ready: {self.is_ready()}")
        
        # Print DataBus stats if available
        if self._data_bus:
            try:
                bus_stats = self._data_bus.get_stats()
                print(f"\n📊 DataBus Stats:")
                print(f"   Messages: {bus_stats.get('messages_published', 0)} published, "
                      f"{bus_stats.get('messages_delivered', 0)} delivered")
                print(f"   Subscriptions: {bus_stats.get('subscriptions', 0)}")
                print(f"   History: {bus_stats.get('history_size', 0)} messages")
            except Exception:
                pass
        
        # Print monitoring integration stats if available (NEW in Stage 7.5)
        if self._monitoring_integration:
            try:
                history = self._monitoring_integration.get_history()
                if history:
                    print(f"\n📈 Performance History:")
                    print(f"   Samples: {history.get_count()}")
                    print(f"   Uptime: {history.get_uptime():.1f}s")
                
                report = self._monitoring_integration.get_latest_report()
                if report:
                    print(f"\n🎯 Analytics:")
                    print(f"   Score: {report.score:.1f}/100")
                    print(f"   Efficiency: {report.efficiency:.1f}/100")
                    print(f"   Bottleneck: {report.bottleneck.type.value}")
            except Exception:
                pass
        
        print("="*50 + "\n")
