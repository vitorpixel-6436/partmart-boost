#!/usr/bin/env python3
"""System Initialization

Version: 0.3.5f (package 3.9a, stage 7.4/7.7)

System initialization manager for proper startup sequence.

Package 3.9a Stage 7.4: DataBus integration.

Features:
- Dependency validation
- Component initialization
- Backend services integration
- DataBus pub/sub system (NEW)
- Error recovery
- Health checks
"""
import sys
import time
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
    
    Manages proper initialization of all system components.
    
    Initialization Order (Stage 7.4):
    1. Check dependencies
    2. Initialize BackendBridge
    3. Create QtSignalBridge
    4. Initialize DataBus (NEW)
    5. Create DataBusIntegration (NEW)
    6. Initialize BackendServiceManager
    7. Register command handlers
    8. Register query handlers
    9. Start monitoring
    10. Create AppIntegrator
    11. Ready for UI
    
    Usage:
        init = SystemInitializer()
        result = init.initialize()
        
        if result.success:
            app_integrator = init.get_integrator()
            # Use integrator to access components
    """
    
    def __init__(self, mode: str = 'full'):
        """Initialize system initializer
        
        Args:
            mode: Initialization mode ('full', 'minimal', 'diagnostic')
        """
        self.mode = mode
        self.results: List[InitResult] = []
        self._integrator = None
        self._service_manager = None
        self._data_bus = None
        self._bus_integration = None
        
        print(f"[SystemInit] Mode: {mode}")
    
    def initialize(self) -> InitResult:
        """Initialize all systems
        
        Returns:
            Overall initialization result
        """
        start_time = time.perf_counter()
        
        print("[SystemInit] Starting initialization...")
        
        try:
            # Step 1: Check dependencies
            dep_result = self._check_dependencies()
            self.results.append(dep_result)
            
            if not dep_result.success:
                return InitResult(
                    success=False,
                    component='dependencies',
                    error=dep_result.error,
                    warnings=dep_result.warnings,
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            
            # Step 2: Initialize BackendBridge
            bridge_result = self._init_backend_bridge()
            self.results.append(bridge_result)
            
            if not bridge_result.success:
                return InitResult(
                    success=False,
                    component='backend_bridge',
                    error=bridge_result.error,
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            
            # Step 3: Initialize QtSignalBridge
            qt_result = self._init_qt_signals()
            self.results.append(qt_result)
            
            if not qt_result.success:
                return InitResult(
                    success=False,
                    component='qt_signals',
                    error=qt_result.error,
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            
            # Step 4: Initialize DataBus (NEW in Stage 7.4)
            bus_result = self._init_data_bus()
            self.results.append(bus_result)
            
            if not bus_result.success:
                print(f"[SystemInit] ⚠️ DataBus failed (non-critical)")
            
            # Step 5: Initialize backend services
            services_result = self._init_backend_services()
            self.results.append(services_result)
            
            if not services_result.success:
                print(f"[SystemInit] ⚠️ Backend services failed (non-critical)")
            
            # Step 6: Create AppIntegrator
            integrator_result = self._create_integrator()
            self.results.append(integrator_result)
            
            if not integrator_result.success:
                return InitResult(
                    success=False,
                    component='integrator',
                    error=integrator_result.error,
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            
            # Collect all warnings
            all_warnings = []
            for result in self.results:
                all_warnings.extend(result.warnings)
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            print(f"[SystemInit] ✅ Initialized in {elapsed_ms:.1f} ms")
            
            return InitResult(
                success=True,
                component='system',
                warnings=all_warnings,
                time_ms=elapsed_ms
            )
        
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[SystemInit] ❌ Initialization failed: {error_msg}")
            traceback.print_exc()
            
            return InitResult(
                success=False,
                component='system',
                error=error_msg,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def _check_dependencies(self) -> InitResult:
        """Check dependencies"""
        start_time = time.perf_counter()
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
                    error=f"Missing packages: {', '.join(check_result.missing)}",
                    warnings=check_result.warnings,
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            
            # Check optional dependencies
            if not checker.has_gpu_support():
                warnings.append("GPU monitoring unavailable (GPUtil not found)")
            
            if not checker.has_wmi_support():
                if sys.platform == 'win32':
                    warnings.append("WMI not available (advanced Windows features disabled)")
            
            print(f"[SystemInit] ✅ Dependencies OK ({len(warnings)} warnings)")
            
            return InitResult(
                success=True,
                component='dependencies',
                warnings=warnings,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except ImportError:
            # DependencyChecker not available, do basic checks
            print("[SystemInit] DependencyChecker not available, using basic checks")
            
            # Check critical imports
            try:
                import numpy
                import psutil
                print("[SystemInit] ✅ Core dependencies OK")
                
                return InitResult(
                    success=True,
                    component='dependencies',
                    warnings=["DependencyChecker not available"],
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            
            except ImportError as e:
                return InitResult(
                    success=False,
                    component='dependencies',
                    error=f"Critical dependency missing: {e}",
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
    
    def _init_backend_bridge(self) -> InitResult:
        """Initialize BackendBridge"""
        start_time = time.perf_counter()
        
        print("[SystemInit] Initializing BackendBridge...")
        
        try:
            from backend_bridge import BackendBridge
            
            # Get singleton instance
            bridge = BackendBridge.get_instance()
            
            print("[SystemInit] ✅ BackendBridge initialized")
            
            return InitResult(
                success=True,
                component='backend_bridge',
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except Exception as e:
            return InitResult(
                success=False,
                component='backend_bridge',
                error=str(e),
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def _init_qt_signals(self) -> InitResult:
        """Initialize QtSignalBridge"""
        start_time = time.perf_counter()
        warnings = []
        
        print("[SystemInit] Initializing QtSignalBridge...")
        
        try:
            from qt_signal_bridge import QtSignalBridge
            from backend_bridge import BackendBridge
            
            # Create Qt signal bridge
            qt_signals = QtSignalBridge()
            
            # Connect to BackendBridge
            bridge = BackendBridge.get_instance()
            bridge.set_qt_signals(qt_signals)
            
            print("[SystemInit] ✅ QtSignalBridge initialized")
            
            return InitResult(
                success=True,
                component='qt_signals',
                warnings=warnings,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except ImportError:
            warnings.append("PyQt6 not available, Qt signals disabled")
            
            print("[SystemInit] ⚠️ QtSignalBridge unavailable")
            
            return InitResult(
                success=True,  # Not critical
                component='qt_signals',
                warnings=warnings,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except Exception as e:
            return InitResult(
                success=False,
                component='qt_signals',
                error=str(e),
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def _init_data_bus(self) -> InitResult:
        """Initialize DataBus (Stage 7.4)"""
        start_time = time.perf_counter()
        warnings = []
        
        print("[SystemInit] Initializing DataBus...")
        
        try:
            from data_bus import DataBus
            from data_bus_integration import DataBusIntegration
            from backend_bridge import BackendBridge
            from qt_signal_bridge import QtSignalBridge
            
            # Create DataBus
            self._data_bus = DataBus(max_history=1000)
            
            # Create integration
            bridge = BackendBridge.get_instance()
            qt_signals = bridge.get_qt_signals()
            
            self._bus_integration = DataBusIntegration(
                bridge=bridge,
                bus=self._data_bus,
                qt_signals=qt_signals
            )
            
            # Start integration
            self._bus_integration.start()
            
            print("[SystemInit] ✅ DataBus initialized")
            
            return InitResult(
                success=True,
                component='data_bus',
                warnings=warnings,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except ImportError as e:
            warnings.append(f"DataBus unavailable: {e}")
            
            print(f"[SystemInit] ⚠️ DataBus unavailable: {e}")
            
            return InitResult(
                success=False,
                component='data_bus',
                warnings=warnings,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except Exception as e:
            return InitResult(
                success=False,
                component='data_bus',
                error=str(e),
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def _init_backend_services(self) -> InitResult:
        """Initialize backend services"""
        start_time = time.perf_counter()
        warnings = []
        
        print("[SystemInit] Initializing backend services...")
        
        try:
            from backend_service_manager import BackendServiceManager
            
            # Create service manager
            self._service_manager = BackendServiceManager()
            
            # Initialize services
            success = self._service_manager.initialize()
            
            if success:
                print("[SystemInit] ✅ Backend services initialized")
                
                return InitResult(
                    success=True,
                    component='backend_services',
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
            else:
                warnings.append("Backend services initialization failed")
                
                return InitResult(
                    success=False,
                    component='backend_services',
                    error="Initialization failed",
                    warnings=warnings,
                    time_ms=(time.perf_counter() - start_time) * 1000
                )
        
        except ImportError as e:
            warnings.append(f"Backend services unavailable: {e}")
            
            print(f"[SystemInit] ⚠️ Backend services unavailable: {e}")
            
            return InitResult(
                success=False,
                component='backend_services',
                warnings=warnings,
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except Exception as e:
            return InitResult(
                success=False,
                component='backend_services',
                error=str(e),
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def _create_integrator(self) -> InitResult:
        """Create AppIntegrator"""
        start_time = time.perf_counter()
        
        print("[SystemInit] Creating AppIntegrator...")
        
        try:
            from app_integrator import AppIntegrator
            
            self._integrator = AppIntegrator()
            
            # Set service manager if available
            if self._service_manager:
                self._integrator.set_service_manager(self._service_manager)
            
            # Set DataBus if available (NEW in Stage 7.4)
            if self._data_bus:
                self._integrator.set_data_bus(self._data_bus)
            
            print("[SystemInit] ✅ AppIntegrator created")
            
            return InitResult(
                success=True,
                component='integrator',
                time_ms=(time.perf_counter() - start_time) * 1000
            )
        
        except Exception as e:
            return InitResult(
                success=False,
                component='integrator',
                error=str(e),
                time_ms=(time.perf_counter() - start_time) * 1000
            )
    
    def get_integrator(self):
        """Get AppIntegrator instance
        
        Returns:
            AppIntegrator instance or None
        """
        return self._integrator
    
    def get_service_manager(self):
        """Get BackendServiceManager instance
        
        Returns:
            BackendServiceManager instance or None
        """
        return self._service_manager
    
    def get_data_bus(self):
        """Get DataBus instance (Stage 7.4)
        
        Returns:
            DataBus instance or None
        """
        return self._data_bus
    
    def get_bus_integration(self):
        """Get DataBusIntegration instance (Stage 7.4)
        
        Returns:
            DataBusIntegration instance or None
        """
        return self._bus_integration
    
    def get_results(self) -> List[InitResult]:
        """Get initialization results
        
        Returns:
            List of initialization results
        """
        return self.results
    
    def print_summary(self):
        """Print initialization summary"""
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


# Command-line interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='PartMart Boost System Initialization')
    parser.add_argument('--check', action='store_true', help='Check dependencies only')
    parser.add_argument('--diagnose', action='store_true', help='Diagnostic mode')
    parser.add_argument('--minimal', action='store_true', help='Minimal mode')
    
    args = parser.parse_args()
    
    if args.check:
        # Check dependencies only
        print("Checking dependencies...\n")
        
        try:
            from dependency_checker import DependencyChecker
            checker = DependencyChecker()
            result = checker.check_all()
            
            if result.success:
                print("✅ All dependencies OK")
            else:
                print(f"❌ Missing: {', '.join(result.missing)}")
            
            sys.exit(0 if result.success else 1)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    # Full initialization
    mode = 'diagnostic' if args.diagnose else ('minimal' if args.minimal else 'full')
    
    init = SystemInitializer(mode=mode)
    result = init.initialize()
    
    init.print_summary()
    
    sys.exit(0 if result.success else 1)
