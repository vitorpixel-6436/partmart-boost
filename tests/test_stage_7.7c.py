#!/usr/bin/env python3
"""Tests for Stage 7.7c - Real Components

Version: 0.3.5d (package 3.9a, stage 7.7c)
"""
import unittest
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import components
try:
    from core.performance_monitor import PerformanceMonitor, PerformanceMetrics
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

try:
    from core.game_detector import GameDetector, GameProcess
    GAME_DETECTOR_AVAILABLE = True
except ImportError:
    GAME_DETECTOR_AVAILABLE = False

try:
    from core.fsr_manager import FSRManager, FSRPreset, FSRConfig
    FSR_MANAGER_AVAILABLE = True
except ImportError:
    FSR_MANAGER_AVAILABLE = False

try:
    from core.dll_injector import DLLInjector
    import sys
    DLL_INJECTOR_AVAILABLE = sys.platform == 'win32'
except ImportError:
    DLL_INJECTOR_AVAILABLE = False


class TestPerformanceMonitor(unittest.TestCase):
    """Test PerformanceMonitor"""
    
    @unittest.skipIf(not PERFORMANCE_MONITOR_AVAILABLE, "PerformanceMonitor not available")
    def test_initialization(self):
        """Test monitor initialization"""
        monitor = PerformanceMonitor()
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.name, "PerformanceMonitor")
    
    @unittest.skipIf(not PERFORMANCE_MONITOR_AVAILABLE, "PerformanceMonitor not available")
    def test_start_stop(self):
        """Test start and stop"""
        monitor = PerformanceMonitor()
        self.assertTrue(monitor.start())
        time.sleep(2)  # Collect some metrics
        self.assertTrue(monitor.stop())
    
    @unittest.skipIf(not PERFORMANCE_MONITOR_AVAILABLE, "PerformanceMonitor not available")
    def test_collect_metrics(self):
        """Test metrics collection"""
        monitor = PerformanceMonitor()
        monitor.start()
        time.sleep(2)
        
        metrics = monitor.get_current_metrics()
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertGreaterEqual(metrics.cpu_percent, 0.0)
        self.assertGreaterEqual(metrics.ram_percent, 0.0)
        
        monitor.stop()
    
    @unittest.skipIf(not PERFORMANCE_MONITOR_AVAILABLE, "PerformanceMonitor not available")
    def test_history(self):
        """Test metrics history"""
        monitor = PerformanceMonitor()
        monitor.start()
        time.sleep(3)
        
        history = monitor.get_history(count=10)
        self.assertGreater(len(history), 0)
        
        monitor.stop()
    
    @unittest.skipIf(not PERFORMANCE_MONITOR_AVAILABLE, "PerformanceMonitor not available")
    def test_health_check(self):
        """Test health check"""
        monitor = PerformanceMonitor()
        monitor.start()
        time.sleep(2)
        
        health = monitor.check_health()
        self.assertIn('status', health)
        self.assertIn('message', health)
        
        monitor.stop()


class TestGameDetector(unittest.TestCase):
    """Test GameDetector"""
    
    @unittest.skipIf(not GAME_DETECTOR_AVAILABLE, "GameDetector not available")
    def test_initialization(self):
        """Test detector initialization"""
        detector = GameDetector()
        self.assertIsNotNone(detector)
        self.assertEqual(detector.name, "GameDetector")
    
    @unittest.skipIf(not GAME_DETECTOR_AVAILABLE, "GameDetector not available")
    def test_start_stop(self):
        """Test start and stop"""
        detector = GameDetector()
        self.assertTrue(detector.start())
        time.sleep(1)
        self.assertTrue(detector.stop())
    
    @unittest.skipIf(not GAME_DETECTOR_AVAILABLE, "GameDetector not available")
    def test_get_detected_games(self):
        """Test getting detected games"""
        detector = GameDetector()
        detector.start()
        time.sleep(3)  # Scan for games
        
        games = detector.get_detected_games()
        self.assertIsInstance(games, list)
        # May or may not detect games depending on what's running
        
        detector.stop()
    
    @unittest.skipIf(not GAME_DETECTOR_AVAILABLE, "GameDetector not available")
    def test_add_custom_game(self):
        """Test adding custom game"""
        detector = GameDetector()
        detector.add_game('test_game.exe', 'Test Game')
        self.assertIn('test_game.exe', detector.KNOWN_GAMES)
        self.assertEqual(detector.KNOWN_GAMES['test_game.exe'], 'Test Game')
    
    @unittest.skipIf(not GAME_DETECTOR_AVAILABLE, "GameDetector not available")
    def test_health_check(self):
        """Test health check"""
        detector = GameDetector()
        health = detector.check_health()
        self.assertIn('status', health)
        self.assertIn('message', health)


class TestFSRManager(unittest.TestCase):
    """Test FSRManager"""
    
    @unittest.skipIf(not FSR_MANAGER_AVAILABLE, "FSRManager not available")
    def test_initialization(self):
        """Test manager initialization"""
        manager = FSRManager(data_dir='test_fsr')
        self.assertIsNotNone(manager)
        self.assertEqual(manager.name, "FSRManager")
        
        # Cleanup
        import shutil
        if Path('test_fsr').exists():
            shutil.rmtree('test_fsr')
    
    @unittest.skipIf(not FSR_MANAGER_AVAILABLE, "FSRManager not available")
    def test_create_config(self):
        """Test config creation"""
        manager = FSRManager(data_dir='test_fsr')
        config = manager.create_config(FSRPreset.QUALITY)
        
        self.assertIsInstance(config, FSRConfig)
        self.assertEqual(config.preset, FSRPreset.QUALITY)
        self.assertEqual(config.render_scale, 0.67)
        
        # Cleanup
        import shutil
        if Path('test_fsr').exists():
            shutil.rmtree('test_fsr')
    
    @unittest.skipIf(not FSR_MANAGER_AVAILABLE, "FSRManager not available")
    def test_save_load_config(self):
        """Test save and load config"""
        manager = FSRManager(data_dir='test_fsr')
        config = manager.create_config(FSRPreset.BALANCED, sharpness=0.8)
        
        # Save
        self.assertTrue(manager.save_game_config('TestGame', config))
        
        # Load
        loaded = manager.load_game_config('TestGame')
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.preset, FSRPreset.BALANCED)
        self.assertEqual(loaded.sharpness, 0.8)
        
        # Cleanup
        import shutil
        if Path('test_fsr').exists():
            shutil.rmtree('test_fsr')
    
    @unittest.skipIf(not FSR_MANAGER_AVAILABLE, "FSRManager not available")
    def test_health_check(self):
        """Test health check"""
        manager = FSRManager(data_dir='test_fsr')
        health = manager.check_health()
        self.assertIn('status', health)
        self.assertIn('message', health)
        
        # Cleanup
        import shutil
        if Path('test_fsr').exists():
            shutil.rmtree('test_fsr')


class TestDLLInjector(unittest.TestCase):
    """Test DLLInjector"""
    
    @unittest.skipIf(not DLL_INJECTOR_AVAILABLE, "DLLInjector not available (Windows only)")
    def test_initialization(self):
        """Test injector initialization"""
        injector = DLLInjector()
        self.assertIsNotNone(injector)
        self.assertEqual(injector.name, "DLLInjector")
    
    @unittest.skipIf(not DLL_INJECTOR_AVAILABLE, "DLLInjector not available (Windows only)")
    def test_is_admin(self):
        """Test admin check"""
        injector = DLLInjector()
        is_admin = injector.is_admin()
        self.assertIsInstance(is_admin, bool)
    
    @unittest.skipIf(not DLL_INJECTOR_AVAILABLE, "DLLInjector not available (Windows only)")
    def test_health_check(self):
        """Test health check"""
        injector = DLLInjector()
        health = injector.check_health()
        self.assertIn('status', health)
        self.assertIn('message', health)


if __name__ == '__main__':
    unittest.main(verbosity=2)
