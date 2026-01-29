#!/usr/bin/env python3
"""System Initialization

Version: 0.3.5e (package 3.9a, stage 7.1/7.6)

Centralized initialization system for all components.

Package 3.9a Stage 7.1: System initialization with error recovery.

Features:
- Stage-by-stage initialization
- Dependency validation
- Error recovery
- Lazy loading
- Status tracking
"""
import sys
import os
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
import importlib.util


class InitializationError(Exception):
    """Initialization error"""
    pass


class SystemInitializer:
    """System Initialization Manager
    
    Centralized initialization for all system components.
    
    Initialization Stages:
    1. Core System (Python, dependencies, logging)
    2. Backend Services (Bridge, DataBus, Events)
    3. Performance Monitor (Hardware monitoring)
    4. Config & Resources (Settings, paths)
    5. Frontend (Lazy - UI components)
    
    Usage:
        initializer = SystemInitializer.get_instance()
        if initializer.initialize_all():
            bridge = initializer.get_bridge()
            monitor = initializer.get_monitor()
    """
    
    _instance: Optional['SystemInitializer'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize system initializer"""
        # Initialization state
        self._initialized = False
        self._stage = 0
        self._errors: List[str] = []
        self._start_time = 0.0
        
        # Component references
        self._bridge = None
        self._qt_signals = None
        self._data_bus = None
        self._event_system = None
        self._monitor = None
        self._config = None
        
        # Feature flags
        self._has_pyqt6 = False
        self._has_gpu = False
        self._headless_mode = False
        
        print("[SystemInitializer] Created (Stage 7.1)")
    
    @classmethod
    def get_instance(cls) -> 'SystemInitializer':
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def initialize_all(self, headless: bool = False) -> bool:
        """Initialize all systems
        
        Args:
            headless: Run without GUI
        
        Returns:
            True if successful
        """
        if self._initialized:
            print("[SystemInitializer] Already initialized")
            return True
        
        self._start_time = time.perf_counter()
        self._headless_mode = headless
        
        print("[SystemInitializer] Starting initialization...")
        
        try:
            # Stage 1: Core System
            if not self._init_stage_1_core():
                return False
            
            # Stage 2: Backend Services
            if not self._init_stage_2_backend():
                return False
            
            # Stage 3: Performance Monitor
            if not self._init_stage_3_monitor():
                return False
            
            # Stage 4: Config & Resources
            if not self._init_stage_4_config():
                return False
            
            # Stage 5: Frontend (if not headless)
            if not headless:
                if not self._init_stage_5_frontend():
                    print("[SystemInitializer] WARNING: Frontend init failed, continuing in headless mode")
                    self._headless_mode = True
            
            # Success!
            self._initialized = True
            elapsed = (time.perf_counter() - self._start_time) * 1000
            print(f"[SystemInitializer] ✅ Initialized in {elapsed:.1f} ms")
            
            return True
        
        except Exception as e:
            self._errors.append(f"Fatal error: {e}")
            print(f"[SystemInitializer] ❌ Initialization failed: {e}")
            return False
    
    def _init_stage_1_core(self) -> bool:
        """Stage 1: Core System"""
        print("[SystemInitializer] Stage 1/5: Core System")
        self._stage = 1
        
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                raise InitializationError(f"Python 3.8+ required, got {sys.version_info.major}.{sys.version_info.minor}")
            
            print(f"[SystemInitializer] ✓ Python {sys.version_info.major}.{sys.version_info.minor}")
            
            # Check core dependencies
            required = ['numpy', 'psutil']
            missing = []
            
            for pkg in required:
                if importlib.util.find_spec(pkg) is None:
                    missing.append(pkg)
            
            if missing:
                raise InitializationError(f"Missing dependencies: {', '.join(missing)}")
            
            print(f"[SystemInitializer] ✓ Core dependencies")
            
            # Check optional dependencies
            self._has_gpu = importlib.util.find_spec('GPUtil') is not None
            self._has_pyqt6 = importlib.util.find_spec('PyQt6') is not None
            
            if self._has_gpu:
                print("[SystemInitializer] ✓ GPU support available")
            else:
                print("[SystemInitializer] ⚠ GPU support not available (GPUtil missing)")
            
            if self._has_pyqt6:
                print("[SystemInitializer] ✓ PyQt6 available")
            else:
                print("[SystemInitializer] ⚠ PyQt6 not available (headless mode only)")
                self._headless_mode = True
            
            return True
        
        except Exception as e:
            self._errors.append(f"Stage 1 error: {e}")
            print(f"[SystemInitializer] ❌ Stage 1 failed: {e}")
            return False
    
    def _init_stage_2_backend(self) -> bool:
        """Stage 2: Backend Services"""
        print("[SystemInitializer] Stage 2/5: Backend Services")
        self._stage = 2
        
        try:
            # Import backend modules
            from backend_bridge import BackendBridge
            
            # Initialize BackendBridge
            self._bridge = BackendBridge.get_instance()
            print("[SystemInitializer] ✓ BackendBridge")
            
            # Initialize QtSignalBridge (if PyQt6 available)
            if self._has_pyqt6:
                from qt_signal_bridge import QtSignalBridge
                self._qt_signals = QtSignalBridge()
                self._bridge.set_qt_signals(self._qt_signals)
                print("[SystemInitializer] ✓ QtSignalBridge")
            
            # Initialize DataBus
            try:
                from data_bus import DataBus
                self._data_bus = DataBus.get_instance()
                print("[SystemInitializer] ✓ DataBus")
            except ImportError:
                print("[SystemInitializer] ⚠ DataBus not available")
            
            # Initialize EventSystem
            try:
                from event_system import EventSystem
                self._event_system = EventSystem.get_instance()
                print("[SystemInitializer] ✓ EventSystem")
            except ImportError:
                print("[SystemInitializer] ⚠ EventSystem not available")
            
            return True
        
        except Exception as e:
            self._errors.append(f"Stage 2 error: {e}")
            print(f"[SystemInitializer] ❌ Stage 2 failed: {e}")
            return False
    
    def _init_stage_3_monitor(self) -> bool:
        """Stage 3: Performance Monitor"""
        print("[SystemInitializer] Stage 3/5: Performance Monitor")
        self._stage = 3
        
        try:
            # Add parent to path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            # Import performance monitor
            try:
                from monitors.performance_monitor import PerformanceMonitor
                self._monitor = PerformanceMonitor()
                print("[SystemInitializer] ✓ PerformanceMonitor")
                
                # Register command handlers if bridge available
                if self._bridge:
                    self._register_monitor_handlers()
                    print("[SystemInitializer] ✓ Monitor handlers registered")
            
            except ImportError as e:
                print(f"[SystemInitializer] ⚠ PerformanceMonitor not available: {e}")
                # Not critical, continue
            
            return True
        
        except Exception as e:
            self._errors.append(f"Stage 3 error: {e}")
            print(f"[SystemInitializer] ⚠ Stage 3 partial failure: {e}")
            return True  # Non-critical, continue
    
    def _init_stage_4_config(self) -> bool:
        """Stage 4: Config & Resources"""
        print("[SystemInitializer] Stage 4/5: Config & Resources")
        self._stage = 4
        
        try:
            # Import config
            try:
                from core.config import Config
                self._config = Config()
                print("[SystemInitializer] ✓ Config")
            except ImportError:
                print("[SystemInitializer] ⚠ Config not available")
            
            # Setup paths
            project_root = Path(__file__).parent.parent.parent
            paths = {
                'root': project_root,
                'src': project_root / 'src',
                'data': project_root / 'data',
                'logs': project_root / 'logs',
            }
            
            # Create directories if needed
            for path in paths.values():
                path.mkdir(parents=True, exist_ok=True)
            
            print("[SystemInitializer] ✓ Paths configured")
            
            return True
        
        except Exception as e:
            self._errors.append(f"Stage 4 error: {e}")
            print(f"[SystemInitializer] ⚠ Stage 4 partial failure: {e}")
            return True  # Non-critical, continue
    
    def _init_stage_5_frontend(self) -> bool:
        """Stage 5: Frontend (Lazy)"""
        print("[SystemInitializer] Stage 5/5: Frontend (Lazy)")
        self._stage = 5
        
        if not self._has_pyqt6:
            print("[SystemInitializer] ⚠ Skipping frontend (PyQt6 not available)")
            return False
        
        try:
            # Lazy load PyQt6 (don't initialize yet)
            from PyQt6.QtWidgets import QApplication
            print("[SystemInitializer] ✓ PyQt6 loaded (lazy)")
            
            # Load UI Factory
            try:
                from core.ui_minimal import UIFactory
                print("[SystemInitializer] ✓ UIFactory available")
            except ImportError:
                print("[SystemInitializer] ⚠ UIFactory not available")
            
            return True
        
        except Exception as e:
            self._errors.append(f"Stage 5 error: {e}")
            print(f"[SystemInitializer] ❌ Stage 5 failed: {e}")
            return False
    
    def _register_monitor_handlers(self):
        """Register PerformanceMonitor command handlers"""
        if not self._bridge or not self._monitor:
            return
        
        from backend_bridge import Command, CommandResult
        
        # Start monitoring handler
        def handle_start_monitoring(command: Command) -> CommandResult:
            try:
                interval = command.params.get('interval', 100)
                self._monitor.start()
                
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
        
        # Stop monitoring handler
        def handle_stop_monitoring(command: Command) -> CommandResult:
            try:
                self._monitor.stop()
                
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
        
        # Register handlers
        self._bridge.register_command_handler('start_monitoring', handle_start_monitoring)
        self._bridge.register_command_handler('stop_monitoring', handle_stop_monitoring)
    
    # ========================================================================
    # PUBLIC GETTERS
    # ========================================================================
    
    def get_bridge(self):
        """Get BackendBridge instance"""
        return self._bridge
    
    def get_qt_signals(self):
        """Get QtSignalBridge instance"""
        return self._qt_signals
    
    def get_data_bus(self):
        """Get DataBus instance"""
        return self._data_bus
    
    def get_event_system(self):
        """Get EventSystem instance"""
        return self._event_system
    
    def get_monitor(self):
        """Get PerformanceMonitor instance"""
        return self._monitor
    
    def get_config(self):
        """Get Config instance"""
        return self._config
    
    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self._initialized
    
    def is_headless(self) -> bool:
        """Check if running in headless mode"""
        return self._headless_mode
    
    def has_gpu_support(self) -> bool:
        """Check if GPU support available"""
        return self._has_gpu
    
    def has_pyqt6(self) -> bool:
        """Check if PyQt6 available"""
        return self._has_pyqt6
    
    def get_errors(self) -> List[str]:
        """Get initialization errors"""
        return self._errors.copy()
    
    def get_stage(self) -> int:
        """Get current initialization stage"""
        return self._stage
    
    def shutdown(self):
        """Shutdown all systems"""
        print("[SystemInitializer] Shutting down...")
        
        try:
            # Stop monitor
            if self._monitor:
                self._monitor.stop()
            
            # Clear references
            self._bridge = None
            self._qt_signals = None
            self._data_bus = None
            self._event_system = None
            self._monitor = None
            self._config = None
            
            self._initialized = False
            print("[SystemInitializer] ✓ Shutdown complete")
        
        except Exception as e:
            print(f"[SystemInitializer] ⚠ Shutdown error: {e}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def initialize(headless: bool = False) -> SystemInitializer:
    """Initialize system and return initializer
    
    Args:
        headless: Run without GUI
    
    Returns:
        SystemInitializer instance
    """
    initializer = SystemInitializer.get_instance()
    initializer.initialize_all(headless=headless)
    return initializer


def get_bridge():
    """Get BackendBridge (initialize if needed)"""
    return SystemInitializer.get_instance().get_bridge()


def get_monitor():
    """Get PerformanceMonitor (initialize if needed)"""
    return SystemInitializer.get_instance().get_monitor()


if __name__ == '__main__':
    # Test initialization
    import sys
    
    if '--check' in sys.argv:
        print("Checking system...")
        initializer = initialize(headless=True)
        
        print(f"\nInitialized: {initializer.is_initialized()}")
        print(f"Stage: {initializer.get_stage()}/5")
        print(f"Headless: {initializer.is_headless()}")
        print(f"GPU Support: {initializer.has_gpu_support()}")
        print(f"PyQt6: {initializer.has_pyqt6()}")
        
        errors = initializer.get_errors()
        if errors:
            print(f"\nErrors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\n✓ No errors")
        
        initializer.shutdown()
    else:
        print("Usage: python system_init.py --check")
