#!/usr/bin/env python3
"""Application Integrator

Version: 0.3.5e (package 3.9a, stage 7.1/7.7)

Unified access point for all application components.

Package 3.9a Stage 7.1: Application integration layer.

Features:
- Unified component access
- Lazy loading
- Health monitoring
- Graceful degradation
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
    - PerformanceMonitor: Performance monitoring (Stage 7.2)
    - ConfigManager: Configuration management (Stage 7.2)
    - DataBus: Event-based data transport
    
    Usage:
        integrator = AppIntegrator()
        
        # Get components
        bridge = integrator.get_bridge()
        qt_signals = integrator.get_qt_signals()
        
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
        self._monitor = None
        self._config = None
        self._data_bus = None
        
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
        
        # Backend services will be initialized in Stage 7.2
        
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'AppIntegrator':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
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
    
    def get_monitor(self):
        """Get PerformanceMonitor (Stage 7.2)
        
        Returns:
            PerformanceMonitor instance or None
        """
        return self._monitor
    
    def get_config(self):
        """Get ConfigManager (Stage 7.2)
        
        Returns:
            ConfigManager instance or None
        """
        return self._config
    
    def get_data_bus(self):
        """Get DataBus (Stage 7.4)
        
        Returns:
            DataBus instance or None
        """
        return self._data_bus
    
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
            'monitor': 'pending' if self._monitor is None else 'ok',
            'config': 'pending' if self._config is None else 'ok',
            'data_bus': 'pending' if self._data_bus is None else 'ok',
        }
        
        return health
    
    def get_uptime(self) -> float:
        """Get uptime in seconds
        
        Returns:
            Uptime in seconds
        """
        return time.perf_counter() - self._init_time
    
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
        print("="*50 + "\n")
