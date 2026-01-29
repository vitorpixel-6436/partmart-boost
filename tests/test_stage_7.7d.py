#!/usr/bin/env python3
"""Tests for Stage 7.7d - Game Profiles

Version: 0.3.5d (package 3.9a, stage 7.7d)
"""
import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import components
try:
    from core.game_profile_manager import (
        GameProfileManager, GameProfile, AutoInjectMode, OptimizationLevel
    )
    from core.fsr_manager import FSRVersion, FSRPreset
    PROFILE_MANAGER_AVAILABLE = True
except ImportError:
    PROFILE_MANAGER_AVAILABLE = False

try:
    from core.auto_injection_manager import AutoInjectionManager
    AUTO_INJECTION_AVAILABLE = True
except ImportError:
    AUTO_INJECTION_AVAILABLE = False


class TestGameProfileManager(unittest.TestCase):
    """Test GameProfileManager"""
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_initialization(self):
        """Test manager initialization"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        self.assertIsNotNone(manager)
        self.assertEqual(manager.name, "GameProfileManager")
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_create_profile(self):
        """Test profile creation"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        profile = manager.create_profile(
            game_name='TestGame',
            executable='test.exe',
            display_name='Test Game'
        )
        
        self.assertIsInstance(profile, GameProfile)
        self.assertEqual(profile.game_name, 'TestGame')
        self.assertEqual(profile.executable, 'test.exe')
        self.assertEqual(profile.display_name, 'Test Game')
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_save_load_profile(self):
        """Test save and load profile"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        # Create and save
        profile = manager.create_profile(
            game_name='TestGame',
            executable='test.exe',
            auto_inject=AutoInjectMode.AUTO,
            optimization_level=OptimizationLevel.AGGRESSIVE
        )
        self.assertTrue(manager.save_profile(profile))
        
        # Load
        loaded = manager.load_profile('TestGame')
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.game_name, 'TestGame')
        self.assertEqual(loaded.auto_inject, AutoInjectMode.AUTO)
        self.assertEqual(loaded.optimization_level, OptimizationLevel.AGGRESSIVE)
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_get_profile_by_executable(self):
        """Test get profile by executable"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        profile = manager.create_profile(
            game_name='TestGame',
            executable='test.exe'
        )
        manager.save_profile(profile)
        
        # Get by executable
        found = manager.get_profile_by_executable('test.exe')
        self.assertIsNotNone(found)
        self.assertEqual(found.game_name, 'TestGame')
        
        # Case insensitive
        found2 = manager.get_profile_by_executable('TEST.EXE')
        self.assertIsNotNone(found2)
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_list_profiles(self):
        """Test list profiles"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        # Create multiple profiles
        for i in range(3):
            profile = manager.create_profile(
                game_name=f'Game{i}',
                executable=f'game{i}.exe'
            )
            manager.save_profile(profile)
        
        # List
        profiles = manager.list_profiles()
        self.assertEqual(len(profiles), 3)
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_delete_profile(self):
        """Test delete profile"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        profile = manager.create_profile(
            game_name='TestGame',
            executable='test.exe'
        )
        manager.save_profile(profile)
        
        # Delete
        self.assertTrue(manager.delete_profile('TestGame'))
        
        # Verify deleted
        loaded = manager.load_profile('TestGame')
        self.assertIsNone(loaded)
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_should_auto_inject(self):
        """Test auto-inject check"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        # Create profile with auto-inject
        profile = manager.create_profile(
            game_name='TestGame',
            executable='test.exe',
            fsr_enabled=True,
            auto_inject=AutoInjectMode.AUTO
        )
        manager.save_profile(profile)
        
        # Should auto-inject
        self.assertTrue(manager.should_auto_inject('TestGame'))
        
        # Disable FSR
        profile.fsr_enabled = False
        manager.save_profile(profile)
        self.assertFalse(manager.should_auto_inject('TestGame'))
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_create_default_profile(self):
        """Test default profile creation"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        
        profile = manager.create_default_profile('TestGame', 'test.exe')
        
        self.assertIsNotNone(profile)
        self.assertTrue(profile.fsr_enabled)
        self.assertEqual(profile.auto_inject, AutoInjectMode.ASK)
        self.assertEqual(profile.optimization_level, OptimizationLevel.BALANCED)
        self.assertIsNotNone(profile.fsr_config)
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')
    
    @unittest.skipIf(not PROFILE_MANAGER_AVAILABLE, "GameProfileManager not available")
    def test_health_check(self):
        """Test health check"""
        manager = GameProfileManager(profiles_dir='test_profiles')
        health = manager.check_health()
        self.assertIn('status', health)
        self.assertIn('message', health)
        
        # Cleanup
        import shutil
        if Path('test_profiles').exists():
            shutil.rmtree('test_profiles')


class TestAutoInjectionManager(unittest.TestCase):
    """Test AutoInjectionManager"""
    
    @unittest.skipIf(not AUTO_INJECTION_AVAILABLE, "AutoInjectionManager not available")
    def test_initialization(self):
        """Test manager initialization"""
        manager = AutoInjectionManager()
        self.assertIsNotNone(manager)
        self.assertEqual(manager.name, "AutoInjectionManager")
    
    @unittest.skipIf(not AUTO_INJECTION_AVAILABLE, "AutoInjectionManager not available")
    def test_get_injected_games(self):
        """Test get injected games"""
        manager = AutoInjectionManager()
        injected = manager.get_injected_games()
        self.assertIsInstance(injected, dict)
    
    @unittest.skipIf(not AUTO_INJECTION_AVAILABLE, "AutoInjectionManager not available")
    def test_is_injected(self):
        """Test is injected check"""
        manager = AutoInjectionManager()
        # Should not be injected
        self.assertFalse(manager.is_injected(99999))
    
    @unittest.skipIf(not AUTO_INJECTION_AVAILABLE, "AutoInjectionManager not available")
    def test_health_check(self):
        """Test health check"""
        manager = AutoInjectionManager()
        health = manager.check_health()
        self.assertIn('status', health)
        self.assertIn('message', health)


if __name__ == '__main__':
    unittest.main(verbosity=2)
