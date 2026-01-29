#!/usr/bin/env python3
"""GameDetectionService Error Handling Tests

Version: 0.3.5o (package 3.9a, stage 7.7b.5.2/7.7)
"""
import sys
import os
import unittest
import time
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from game_detection_service import (
    GameDetectionService,
    GameDatabase,
    GameInfo,
    DetectionState
)


class TestGameInfo(unittest.TestCase):
    """Test GameInfo data class"""
    
    def test_creation(self):
        """Test GameInfo creation"""
        game = GameInfo(
            name="Test Game",
            process_name="test.exe",
            pid=1234,
            window_title="Test Window",
            is_fullscreen=True,
            timestamp=123.456
        )
        
        self.assertEqual(game.name, "Test Game")
        self.assertEqual(game.pid, 1234)
        self.assertTrue(game.is_fullscreen)
    
    def test_to_dict(self):
        """Test dictionary conversion"""
        game = GameInfo(
            name="Test Game",
            process_name="test.exe",
            pid=1234,
            window_title="Test Window",
            is_fullscreen=False,
            timestamp=123.456
        )
        
        d = game.to_dict()
        
        self.assertEqual(d['name'], "Test Game")
        self.assertEqual(d['pid'], 1234)
        self.assertEqual(d['process_name'], "test.exe")
        self.assertFalse(d['is_fullscreen'])


class TestGameDatabase(unittest.TestCase):
    """Test GameDatabase error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use temp file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.db = GameDatabase(db_path=self.temp_file.name)
    
    def tearDown(self):
        """Clean up"""
        try:
            os.unlink(self.temp_file.name)
        except Exception:
            pass
    
    def test_initialization(self):
        """Test database initialization"""
        # Should have default games
        games = self.db.get_all_process_names()
        self.assertGreater(len(games), 0)
        
        # Should have common games
        self.assertIn('csgo.exe', games)
        self.assertIn('gta5.exe', games)
    
    def test_add_game(self):
        """Test adding game"""
        result = self.db.add_game('test.exe', 'Test Game')
        self.assertTrue(result)
        
        # Should be retrievable
        name = self.db.lookup('test.exe')
        self.assertEqual(name, 'Test Game')
    
    def test_add_invalid_game(self):
        """Test adding invalid game"""
        # Empty name
        result = self.db.add_game('', 'Test')
        self.assertFalse(result)
        
        # Empty game name
        result = self.db.add_game('test.exe', '')
        self.assertFalse(result)
    
    def test_lookup(self):
        """Test game lookup"""
        self.db.add_game('game.exe', 'My Game')
        
        # Should find game
        name = self.db.lookup('game.exe')
        self.assertEqual(name, 'My Game')
        
        # Case insensitive
        name = self.db.lookup('GAME.EXE')
        self.assertEqual(name, 'My Game')
        
        # Not found
        name = self.db.lookup('notfound.exe')
        self.assertIsNone(name)
    
    def test_save_and_load(self):
        """Test save and load from file"""
        # Add custom game
        self.db.add_game('custom.exe', 'Custom Game')
        
        # Save
        result = self.db.save_to_file()
        self.assertTrue(result)
        
        # Create new database with same file
        db2 = GameDatabase(db_path=self.temp_file.name)
        
        # Should have custom game
        name = db2.lookup('custom.exe')
        self.assertEqual(name, 'Custom Game')
    
    def test_get_all_process_names(self):
        """Test getting all process names"""
        self.db.add_game('test1.exe', 'Test 1')
        self.db.add_game('test2.exe', 'Test 2')
        
        names = self.db.get_all_process_names()
        
        self.assertIn('test1.exe', names)
        self.assertIn('test2.exe', names)


class TestGameDetectionService(unittest.TestCase):
    """Test GameDetectionService error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = GameDetectionService(interval=100)
    
    def tearDown(self):
        """Clean up"""
        if self.service.is_running():
            self.service.stop()
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.service.get_state(), DetectionState.STOPPED)
        self.assertFalse(self.service.is_running())
    
    def test_interval_clamping(self):
        """Test interval is clamped to valid range"""
        # Too low
        service1 = GameDetectionService(interval=50)
        status1 = service1.get_status()
        self.assertEqual(status1['interval'], 100)  # Clamped to min
        
        # Too high
        service2 = GameDetectionService(interval=20000)
        status2 = service2.get_status()
        self.assertEqual(status2['interval'], 10000)  # Clamped to max
    
    def test_start_stop(self):
        """Test basic start/stop"""
        # Start
        result = self.service.start()
        self.assertTrue(result)
        self.assertEqual(self.service.get_state(), DetectionState.RUNNING)
        
        # Wait
        time.sleep(0.2)
        
        # Stop
        result = self.service.stop()
        self.assertTrue(result)
        self.assertEqual(self.service.get_state(), DetectionState.STOPPED)
    
    def test_start_already_running(self):
        """Test starting when already running"""
        self.service.start()
        
        # Second start should return True
        result = self.service.start()
        self.assertTrue(result)
        
        self.service.stop()
    
    def test_stop_already_stopped(self):
        """Test stopping when already stopped"""
        # Should return True
        result = self.service.stop()
        self.assertTrue(result)
    
    def test_callback_system(self):
        """Test callback system"""
        received = []
        
        def callback(game: GameInfo):
            received.append(game)
        
        # Add callback
        callback_id = self.service.add_callback(callback)
        self.assertGreaterEqual(callback_id, 0)
        
        # Mock game detection
        with patch.object(self.service, '_detect_game') as mock_detect:
            mock_detect.return_value = GameInfo(
                name="Test Game",
                process_name="test.exe",
                pid=1234,
                window_title="Test",
                is_fullscreen=False,
                timestamp=time.time()
            )
            
            self.service.start()
            time.sleep(0.3)
            self.service.stop()
        
        # Should have received at least one callback
        self.assertGreater(len(received), 0)
    
    def test_callback_error_isolation(self):
        """Test that callback errors don't break detection"""
        received_good = []
        
        def bad_callback(game: GameInfo):
            raise Exception("Bad callback!")
        
        def good_callback(game: GameInfo):
            received_good.append(game)
        
        # Add both callbacks
        self.service.add_callback(bad_callback)
        self.service.add_callback(good_callback)
        
        # Mock game detection
        with patch.object(self.service, '_detect_game') as mock_detect:
            mock_detect.return_value = GameInfo(
                name="Test",
                process_name="test.exe",
                pid=1234,
                window_title="Test",
                is_fullscreen=False,
                timestamp=time.time()
            )
            
            self.service.start()
            time.sleep(0.3)
            self.service.stop()
        
        # Good callback should still work
        self.assertGreater(len(received_good), 0)
    
    def test_get_current_game(self):
        """Test getting current game"""
        # No game initially
        game = self.service.get_current_game()
        self.assertIsNone(game)
        
        # Mock detection
        with patch.object(self.service, '_detect_game') as mock_detect:
            mock_detect.return_value = GameInfo(
                name="Test Game",
                process_name="test.exe",
                pid=1234,
                window_title="Test",
                is_fullscreen=True,
                timestamp=time.time()
            )
            
            self.service.start()
            time.sleep(0.2)
            
            game = self.service.get_current_game()
            self.assertIsNotNone(game)
            self.assertEqual(game['name'], "Test Game")
            self.assertEqual(game['pid'], 1234)
            self.assertTrue(game['is_fullscreen'])
            
            self.service.stop()
    
    def test_get_status(self):
        """Test status reporting"""
        status = self.service.get_status()
        
        self.assertIn('state', status)
        self.assertIn('interval', status)
        self.assertIn('detection_count', status)
        self.assertIn('error_count', status)
        
        self.assertEqual(status['state'], 'stopped')
    
    def test_add_game_to_database(self):
        """Test adding game to database"""
        result = self.service.add_game_to_database('newgame.exe', 'New Game')
        self.assertTrue(result)
    
    @patch('psutil.process_iter')
    def test_process_enumeration_error(self, mock_iter):
        """Test handling process enumeration errors"""
        # Mock error
        mock_iter.side_effect = Exception("Enumeration error!")
        
        # Should not crash
        games = self.service._get_game_processes()
        
        # Should return empty list
        self.assertEqual(len(games), 0)
    
    def test_process_access_denied(self):
        """Test handling process access denied"""
        import psutil
        
        # Create mock process that raises AccessDenied
        mock_proc = Mock()
        mock_proc.info = {'name': 'test.exe', 'pid': 1234}
        mock_proc.name.side_effect = psutil.AccessDenied()
        
        with patch('psutil.process_iter', return_value=[mock_proc]):
            # Should not crash
            games = self.service._get_game_processes()
            # Should handle error gracefully
            self.assertIsInstance(games, list)


if __name__ == '__main__':
    unittest.main()
