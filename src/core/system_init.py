#!/usr/bin/env python3
"""System Initialization

Version: 0.3.5h (package 3.9a, stage 7.6/7.7)

Package 3.9a Stage 7.6: Configuration management integration.

Features:
- Dependency validation
- Component initialization
- Backend services integration
- DataBus pub/sub system
- Performance history and analytics
- Configuration management (NEW)
- Error recovery
- Health checks
"""
import sys
import time
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class InitResult:
    """Initialization result"""
    success: bool
    component: str
    error: Optional[str] = None
    warnings: List[str] = None
    time_ms: float = 0.0
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class SystemInitializer:
    """System Initialization Manager
    
    Initialization Order (Stage 7.6):
    1. Check dependencies
    2. Initialize ConfigManager (NEW)
    3. Initialize BackendBridge
    4. Create QtSignalBridge
    5. Initialize DataBus
    6. Create DataBusIntegration
    7. Initialize ConfigIntegration (NEW)
    8. Initialize BackendServiceManager
    9. Initialize MonitoringIntegration
    10. Create AppIntegrator
    11. Ready for UI
    """
    
    def __init__(self, mode: str = 'full', config_file: Optional[str] = None):
        """Initialize
        
        Args:
            mode: Mode ('full', 'minimal', 'diagnostic')
            config_file: Config file path (default: config/config.json)
        """
        self.mode = mode
        self._config_file = config_file or 'config/config.json'
        self.results: List[InitResult] = []
        
        # Components
        self._config = None
        self._config_integration = None
        self._integrator = None
        self._service_manager = None
        self._data_bus = None
        self._bus_integration = None
        self._monitoring_integration = None
        
        print(f"[SystemInit] Mode: {mode}")
    
    def initialize(self) -> InitResult:
        """Initialize all systems"""
        start_time = time.perf_counter()
        print("[SystemInit] Starting initialization...")
        
        try:
            # Step 1: Dependencies
            self.results.append(self._check_dependencies())
            if not self.results[-1].success:
                return self._fail_result('dependencies', start_time)
            
            # Step 2: ConfigManager (NEW in Stage 7.6)
            self.results.append(self._init_config())
            
            # Step 3: BackendBridge
            self.results.append(self._init_backend_bridge())
            if not self.results[-1].success:
                return self._fail_result('backend_bridge', start_time)
            
            # Step 4: QtSignalBridge
            self.results.append(self._init_qt_signals())
            
            # Step 5: DataBus
            self.results.append(self._init_data_bus())
            
            # Step 6: ConfigIntegration (NEW in Stage 7.6)
            self.results.append(self._init_config_integration())
            
            # Step 7: Backend services
            self.results.append(self._init_backend_services())
            
            # Step 8: Monitoring integration
            self.results.append(self._init_monitoring_integration())
            
            # Step 9: AppIntegrator
            self.results.append(self._create_integrator())
            if not self.results[-1].success:
                return self._fail_result('integrator', start_time)
            
            # Success!
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            print(f"[SystemInit] ✅ Initialized in {elapsed_ms:.1f} ms")
            
            return InitResult(
                success=True,
                component='system',
                warnings=self._collect_warnings(),
                time_ms=elapsed_ms
            )
        
        except Exception as e:
            import traceback
            print(f"[SystemInit] ❌ Failed: {e}")
            traceback.print_exc()
            return InitResult(
                success=False,
                component='system',
                error=str(e),
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def _fail_result(self, component: str, start_time: float) -> InitResult:
        """Create failure result"""
        result = self.results[-1]
        return InitResult(
            success=False,
            component=component,
            error=result.error,
            warnings=self._collect_warnings(),
            time_ms=(time.perf_counter() - start_time) * 1000
        )
    
    def _collect_warnings(self) -> List[str]:
        """Collect all warnings"""
        warnings = []
        for result in self.results:
            warnings.extend(result.warnings)
        return warnings
    
    def _check_dependencies(self) -> InitResult:
        """Check dependencies"""
        start = time.perf_counter()
        warnings = []
        print("[SystemInit] Checking dependencies...")
        
        try:
            from dependency_checker import DependencyChecker
            checker = DependencyChecker()
            check_result = checker.check_all()
            
            if not check_result.success:
                return InitResult(
                    success=False,
                    component='dependencies',
                    error=f"Missing: {', '.join(check_result.missing)}",
                    warnings=check_result.warnings,
                    time_ms=(time.perf_counter() - start) * 1000
                )
            
            print(f"[SystemInit] ✅ Dependencies OK")
            return InitResult(
                success=True,
                component='dependencies',
                warnings=warnings,
                time_ms=(time.perf_counter() - start) * 1000
            )
        
        except ImportError:
            print("[SystemInit] ✅ Basic dependencies OK")
            return InitResult(
                success=True,
                component='dependencies',
                warnings=["DependencyChecker not available"],
                time_ms=(time.perf_counter() - start) * 1000
            )
    
    def _init_config(self) -> InitResult:
        """Initialize ConfigManager (Stage 7.6)"""
        start = time.perf_counter()
        warnings = []
        print("[SystemInit] Initializing ConfigManager...")
        
        try:
            from config_manager import ConfigManager
            self._config = ConfigManager(self._config_file)
            print(f"[SystemInit] ✅ ConfigManager initialized")
            return InitResult(
                success=True,
                component='config',
                time_ms=(time.perf_counter() - start) * 1000
            )
        
        except Exception as e:
            warnings.append(f"ConfigManager error: {e}")
            print(f"[SystemInit] ⚠️ ConfigManager unavailable: {e}")
            return InitResult(
                success=False,
                component='config',
                warnings=warnings,
                time_ms=(time.perf_counter() - start) * 1000
            )
    
    def _init_backend_bridge(self) -> InitResult:
        """Initialize BackendBridge"""
        start = time.perf_counter()
        print("[SystemInit] Initializing BackendBridge...")
        
        try:
            from backend_bridge import BackendBridge
            BackendBridge.get_instance()
            print("[SystemInit] ✅ BackendBridge initialized")
            return InitResult(success=True, component='backend_bridge',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return InitResult(success=False, component='backend_bridge',
                            error=str(e), time_ms=(time.perf_counter() - start) * 1000)
    
    def _init_qt_signals(self) -> InitResult:
        """Initialize QtSignalBridge"""
        start = time.perf_counter()
        print("[SystemInit] Initializing QtSignalBridge...")
        
        try:
            from qt_signal_bridge import QtSignalBridge
            from backend_bridge import BackendBridge
            
            qt_signals = QtSignalBridge()
            BackendBridge.get_instance().set_qt_signals(qt_signals)
            print("[SystemInit] ✅ QtSignalBridge initialized")
            return InitResult(success=True, component='qt_signals',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception:
            return InitResult(success=True, component='qt_signals',
                            warnings=["Qt signals unavailable"],
                            time_ms=(time.perf_counter() - start) * 1000)
    
    def _init_data_bus(self) -> InitResult:
        """Initialize DataBus"""
        start = time.perf_counter()
        print("[SystemInit] Initializing DataBus...")
        
        try:
            from data_bus import DataBus
            from data_bus_integration import DataBusIntegration
            from backend_bridge import BackendBridge
            
            self._data_bus = DataBus(max_history=1000)
            bridge = BackendBridge.get_instance()
            qt_signals = bridge.get_qt_signals()
            
            self._bus_integration = DataBusIntegration(bridge, self._data_bus, qt_signals)
            self._bus_integration.start()
            
            print("[SystemInit] ✅ DataBus initialized")
            return InitResult(success=True, component='data_bus',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return InitResult(success=False, component='data_bus',
                            warnings=[f"DataBus unavailable: {e}"],
                            time_ms=(time.perf_counter() - start) * 1000)
    
    def _init_config_integration(self) -> InitResult:
        """Initialize ConfigIntegration (Stage 7.6)"""
        start = time.perf_counter()
        print("[SystemInit] Initializing ConfigIntegration...")
        
        try:
            from config_integration import ConfigIntegration
            
            self._config_integration = ConfigIntegration(
                config=self._config,
                data_bus=self._data_bus
            )
            
            if self._config:
                self._config_integration.start()
                print("[SystemInit] ✅ ConfigIntegration initialized")
            else:
                print("[SystemInit] ⚠️ ConfigIntegration created but not started")
            
            return InitResult(success=True, component='config_integration',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return InitResult(success=False, component='config_integration',
                            warnings=[f"ConfigIntegration error: {e}"],
                            time_ms=(time.perf_counter() - start) * 1000)
    
    def _init_backend_services(self) -> InitResult:
        """Initialize backend services"""
        start = time.perf_counter()
        print("[SystemInit] Initializing backend services...")
        
        try:
            from backend_service_manager import BackendServiceManager
            self._service_manager = BackendServiceManager()
            self._service_manager.initialize()
            print("[SystemInit] ✅ Backend services initialized")
            return InitResult(success=True, component='backend_services',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return InitResult(success=False, component='backend_services',
                            warnings=[f"Backend services error: {e}"],
                            time_ms=(time.perf_counter() - start) * 1000)
    
    def _init_monitoring_integration(self) -> InitResult:
        """Initialize monitoring integration"""
        start = time.perf_counter()
        print("[SystemInit] Initializing monitoring integration...")
        
        try:
            from monitoring_integration import MonitoringIntegration
            
            monitor = self._service_manager.get_monitor() if self._service_manager else None
            self._monitoring_integration = MonitoringIntegration(
                monitor=monitor,
                data_bus=self._data_bus,
                history_size=1000
            )
            
            if monitor:
                self._monitoring_integration.start()
                print("[SystemInit] ✅ Monitoring integration initialized")
            
            return InitResult(success=True, component='monitoring_integration',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return InitResult(success=False, component='monitoring_integration',
                            warnings=[f"Monitoring integration error: {e}"],
                            time_ms=(time.perf_counter() - start) * 1000)
    
    def _create_integrator(self) -> InitResult:
        """Create AppIntegrator"""
        start = time.perf_counter()
        print("[SystemInit] Creating AppIntegrator...")
        
        try:
            from app_integrator import AppIntegrator
            
            self._integrator = AppIntegrator()
            
            # Connect components
            if self._service_manager:
                self._integrator.set_service_manager(self._service_manager)
            if self._data_bus:
                self._integrator.set_data_bus(self._data_bus)
            if self._monitoring_integration:
                self._integrator.set_monitoring_integration(self._monitoring_integration)
            if self._config:  # NEW in Stage 7.6
                self._integrator.set_config(self._config)
            
            print("[SystemInit] ✅ AppIntegrator created")
            return InitResult(success=True, component='integrator',
                            time_ms=(time.perf_counter() - start) * 1000)
        except Exception as e:
            return InitResult(success=False, component='integrator',
                            error=str(e), time_ms=(time.perf_counter() - start) * 1000)
    
    # Getters
    def get_integrator(self): return self._integrator
    def get_config(self): return self._config
    def get_service_manager(self): return self._service_manager
    def get_data_bus(self): return self._data_bus
    def get_bus_integration(self): return self._bus_integration
    def get_monitoring_integration(self): return self._monitoring_integration
    def get_config_integration(self): return self._config_integration
    def get_results(self) -> List[InitResult]: return self.results
    
    def print_summary(self):
        """Print summary"""
        print("\n" + "="*60)
        print("SYSTEM INITIALIZATION SUMMARY")
        print("="*60)
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.component}: {result.time_ms:.1f} ms")
            if result.error:
                print(f"   Error: {result.error}")
            for warning in result.warnings:
                print(f"   ⚠️ {warning}")
        print("="*60 + "\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    
    init = SystemInitializer()
    result = init.initialize()
    init.print_summary()
    sys.exit(0 if result.success else 1)
