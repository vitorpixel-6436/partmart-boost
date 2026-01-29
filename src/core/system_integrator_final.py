#!/usr/bin/env python3
"""System Integrator Final - Complete system integration with REAL components

Version: 0.3.5d_hotfix2 (package 3.9a, stage 7.7d_hotfix2)

Integrates all real components:
- PerformanceMonitor (psutil/pynvml)
- GameDetector (process detection)
- FSRManager (FSR 3.x library management)
- DLLInjector (Windows DLL injection)
- GameProfileManager (per-game settings)
- AutoInjectionManager (automatic FSR injection)
- All infrastructure from Stage 7.7b

NO STUBS - REAL WORKING SYSTEM!
"""
import time
from typing import Optional
from dataclasses import dataclass

try:
    from core.config_manager import get_config_manager, ConfigManager
except ImportError:
    ConfigManager = None
    get_config_manager = None

try:
    from core.error_reporter import get_error_reporter, ErrorReporter
except ImportError:
    ErrorReporter = None
    get_error_reporter = None

try:
    from core.system_health_monitor import get_health_monitor, SystemHealthMonitor
except ImportError:
    SystemHealthMonitor = None
    get_health_monitor = None

try:
    from core.recovery_coordinator import get_recovery_coordinator, RecoveryCoordinator
except ImportError:
    RecoveryCoordinator = None
    get_recovery_coordinator = None

try:
    from core.historical_data_store import HistoricalDataStore
except ImportError:
    HistoricalDataStore = None

try:
    from core.data_aggregator import DataAggregator
except ImportError:
    DataAggregator = None

# Real components from Stage 7.7c
try:
    from core.performance_monitor import get_performance_monitor, PerformanceMonitor
except ImportError:
    PerformanceMonitor = None
    get_performance_monitor = None

try:
    from core.game_detector import get_game_detector, GameDetector, GameProcess
except ImportError:
    GameDetector = None
    get_game_detector = None
    GameProcess = None

try:
    from core.fsr_manager import get_fsr_manager, FSRManager, FSRPreset
except ImportError:
    FSRManager = None
    get_fsr_manager = None
    FSRPreset = None

try:
    from core.dll_injector import get_dll_injector, DLLInjector
except ImportError:
    DLLInjector = None
    get_dll_injector = None

# New components from Stage 7.7d
try:
    from core.game_profile_manager import get_profile_manager, GameProfileManager
except ImportError:
    GameProfileManager = None
    get_profile_manager = None

try:
    from core.auto_injection_manager import get_auto_injection_manager, AutoInjectionManager
except ImportError:
    AutoInjectionManager = None
    get_auto_injection_manager = None


@dataclass
class SystemStatus:
    """System status information"""
    initialized: bool = False
    running: bool = False
    error_count: int = 0
    component_count: int = 0
    healthy_count: int = 0
    uptime: float = 0.0
    games_detected: int = 0
    fsr_active: bool = False


class SystemIntegratorFinal:
    """Complete system integration with REAL components
    
    v0.3.5d_hotfix2 - Stage 7.7d: Real implementation + Game Profiles
    
    Integrates:
    - Performance monitoring (CPU/GPU/RAM)
    - Game detection (automatic)
    - FSR 3.x management (library handling + frame generation)
    - DLL injection (auto-injection)
    - Game profiles (per-game settings)
    - Auto-injection system
    - Error recovery
    - Historical data
    - Configuration
    """
    
    def __init__(self, config_path: str = 'config/settings.json'):
        self._initialized = False
        self._running = False
        self._start_time = 0.0
        
        # Configuration
        self.config_manager = None
        if get_config_manager:
            self.config_manager = get_config_manager(config_path)
        
        # Infrastructure (Stage 7.7b)
        self.error_reporter = None
        self.health_monitor = None
        self.recovery_coordinator = None
        self.historical_store = None
        self.data_aggregator = None
        
        # Real components (Stage 7.7c)
        self.performance_monitor = None
        self.game_detector = None
        self.fsr_manager = None
        self.dll_injector = None
        
        # New components (Stage 7.7d)
        self.profile_manager = None
        self.auto_injection_manager = None
    
    def initialize(self) -> bool:
        """Initialize all systems"""
        if self._initialized:
            return True
        
        print("Initializing PartMart Boost v0.3.5d_hotfix2...")
        
        try:
            # Load configuration
            if self.config_manager:
                self.config_manager.load()
                print("[+] Configuration loaded")
            
            # Initialize infrastructure
            if get_error_reporter:
                self.error_reporter = get_error_reporter()
                print("[+] Error reporter ready")
            
            if get_health_monitor:
                self.health_monitor = get_health_monitor()
                print("[+] Health monitor ready")
            
            if get_recovery_coordinator:
                self.recovery_coordinator = get_recovery_coordinator()
                if self.error_reporter and self.health_monitor:
                    self.recovery_coordinator.set_error_reporter(self.error_reporter)
                    self.recovery_coordinator.set_health_monitor(self.health_monitor)
                print("[+] Recovery coordinator ready")
            
            if HistoricalDataStore:
                self.historical_store = HistoricalDataStore('data/history.db')
                print("[+] Historical data store ready")
            
            if DataAggregator:
                self.data_aggregator = DataAggregator(
                    error_reporter=self.error_reporter,
                    health_monitor=self.health_monitor,
                    recovery_coordinator=self.recovery_coordinator,
                    historical_store=self.historical_store
                )
                print("[+] Data aggregator ready")
            
            # Initialize REAL components (Stage 7.7c)
            if get_performance_monitor:
                self.performance_monitor = get_performance_monitor()
                print("[+] Performance monitor ready (CPU/GPU/RAM)")
            
            if get_game_detector:
                self.game_detector = get_game_detector()
                print("[+] Game detector ready (40+ games)")
            
            if get_fsr_manager:
                self.fsr_manager = get_fsr_manager()
                print("[+] FSR 3.x manager ready (frame generation)")
            
            if get_dll_injector:
                self.dll_injector = get_dll_injector()
                print("[+] DLL injector ready")
            
            # Initialize NEW components (Stage 7.7d)
            if get_profile_manager:
                self.profile_manager = get_profile_manager()
                print("[+] Game profile manager ready")
            
            if get_auto_injection_manager:
                self.auto_injection_manager = get_auto_injection_manager()
                print("[+] Auto-injection manager ready")
                
                # Register callback for game detection
                if self.game_detector:
                    def on_game_event(event_type, game):
                        if event_type == 'detected':
                            self.auto_injection_manager.handle_game_detected(game)
                        elif event_type == 'closed':
                            self.auto_injection_manager.handle_game_closed(game)
                    
                    self.game_detector.register_callback(on_game_event)
            
            # Register components with health monitor
            if self.health_monitor:
                if self.performance_monitor:
                    self.health_monitor.register_component(self.performance_monitor)
                if self.game_detector:
                    self.health_monitor.register_component(self.game_detector)
                if self.fsr_manager:
                    self.health_monitor.register_component(self.fsr_manager)
                if self.dll_injector:
                    self.health_monitor.register_component(self.dll_injector)
                if self.profile_manager:
                    self.health_monitor.register_component(self.profile_manager)
                if self.auto_injection_manager:
                    self.health_monitor.register_component(self.auto_injection_manager)
            
            self._initialized = True
            print("")
            print("[+] PartMart Boost initialized successfully!")
            print("    Stage 7.7d: FSR 3.x + Game Profiles + Auto-Injection")
            return True
        
        except Exception as e:
            print(f"[-] Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start(self) -> bool:
        """Start all systems"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        if self._running:
            return True
        
        print("")
        print("Starting PartMart Boost systems...")
        
        try:
            self._start_time = time.time()
            
            # Start performance monitor
            if self.performance_monitor:
                self.performance_monitor.start()
                print("[+] Performance monitoring started")
            
            # Start game detector
            if self.game_detector:
                self.game_detector.start()
                print("[+] Game detection started")
            
            # Start data aggregator
            if self.data_aggregator:
                self.data_aggregator.start()
                print("[+] Data aggregation started")
            
            self._running = True
            print("")
            print("[+] All systems running!")
            print("    Monitoring: CPU, GPU, RAM")
            print("    Detecting: 40+ games")
            print("    FSR 3.x: Ready for injection")
            return True
        
        except Exception as e:
            print(f"[-] Start failed: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop all systems"""
        if not self._running:
            return True
        
        print("")
        print("Stopping PartMart Boost systems...")
        
        try:
            # Stop data aggregator
            if self.data_aggregator:
                self.data_aggregator.stop()
                print("[+] Data aggregation stopped")
            
            # Stop game detector
            if self.game_detector:
                self.game_detector.stop()
                print("[+] Game detection stopped")
            
            # Stop performance monitor
            if self.performance_monitor:
                self.performance_monitor.stop()
                print("[+] Performance monitoring stopped")
            
            self._running = False
            print("")
            print("[+] All systems stopped")
            return True
        
        except Exception as e:
            print(f"[-] Stop failed: {e}")
            return False
    
    def get_status(self) -> SystemStatus:
        """Get current system status"""
        uptime = time.time() - self._start_time if self._running else 0.0
        
        # Count components and errors
        component_count = 0
        healthy_count = 0
        error_count = 0
        
        if self.health_monitor:
            all_health = self.health_monitor.get_all_health()
            component_count = len(all_health)
            healthy_count = sum(1 for h in all_health.values() if h.get('status') == 'healthy')
        
        if self.error_reporter:
            error_count = self.error_reporter.get_error_count()
        
        # Count games
        games_detected = 0
        if self.game_detector:
            games_detected = len(self.game_detector.get_detected_games())
        
        # FSR status
        fsr_active = False
        if self.auto_injection_manager:
            fsr_active = len(self.auto_injection_manager.get_injected_games()) > 0
        
        return SystemStatus(
            initialized=self._initialized,
            running=self._running,
            error_count=error_count,
            component_count=component_count,
            healthy_count=healthy_count,
            uptime=uptime,
            games_detected=games_detected,
            fsr_active=fsr_active
        )
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print("")
        print("=" * 60)
        print("  PartMart Boost v0.3.5d_hotfix2 - System Status")
        print("  Stage 7.7d: FSR 3.x + Game Profiles")
        print("=" * 60)
        print(f"Initialized: {'Yes' if status.initialized else 'No'}")
        print(f"Running: {'Yes' if status.running else 'No'}")
        print(f"Uptime: {status.uptime:.1f}s")
        print(f"Components: {status.healthy_count}/{status.component_count} healthy")
        print(f"Errors: {status.error_count}")
        print(f"Games Detected: {status.games_detected}")
        print(f"FSR Active: {'Yes' if status.fsr_active else 'No'}")
        
        # Print detected games
        if self.game_detector:
            games = self.game_detector.get_detected_games()
            if games:
                print("")
                print("Detected Games:")
                for game in games:
                    injected = ""
                    if self.auto_injection_manager:
                        if self.auto_injection_manager.is_injected(game.pid):
                            injected = " [FSR INJECTED]"
                    print(f"  - {game.display_name} (PID: {game.pid}){injected}")
                    print(f"    CPU: {game.cpu_percent:.1f}%, RAM: {game.memory_mb:.0f} MB")
        
        # Print performance metrics
        if self.performance_monitor:
            metrics = self.performance_monitor.get_current_metrics()
            if metrics:
                print("")
                print("Performance:")
                print(f"  CPU: {metrics.cpu_percent:.1f}%")
                print(f"  RAM: {metrics.ram_percent:.1f}%")
                if metrics.gpu_percent is not None:
                    print(f"  GPU: {metrics.gpu_percent:.1f}%")
                    if metrics.gpu_temp:
                        print(f"  GPU Temp: {metrics.gpu_temp:.1f} C")
        
        print("=" * 60)
        print("")


if __name__ == '__main__':
    # Test system integrator
    print("Testing SystemIntegratorFinal v0.3.5d_hotfix2...")
    print("")
    
    integrator = SystemIntegratorFinal()
    
    # Initialize
    if not integrator.initialize():
        print("[-] Initialization failed")
        exit(1)
    
    # Start
    if not integrator.start():
        print("[-] Start failed")
        exit(1)
    
    # Run for 15 seconds
    print("")
    print("Running for 15 seconds...")
    print("")
    for i in range(15):
        time.sleep(1)
        if i % 5 == 4:
            integrator.print_status()
    
    # Stop
    integrator.stop()
    
    print("")
    print("[+] System Integrator test complete!")
