#!/usr/bin/env python3
"""Game Detection Service with Error Handling

Version: 0.3.5o (package 3.9a, stage 7.7b.5.2/7.7)

Package 3.9a Stage 7.7b.5.2: Error handling in GameDetectionService.

Features:
- Automatic game detection
- Process monitoring
- Window enumeration
- Game database
- Thread-safe operation
- Comprehensive error handling
"""
import os
import threading
import time
import psutil
from typing import Dict, Any, Optional, Callable, List, Set
from dataclasses import dataclass
from enum import Enum
import json

try:
    from logger import AppLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

# Windows-specific imports (optional)
try:
    import win32gui
    import win32process
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class DetectionState(Enum):
    """Detection service state"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class GameInfo:
    """Game information
    
    Attributes:
        name: Game name
        process_name: Process executable name
        pid: Process ID
        window_title: Window title
        is_fullscreen: Fullscreen status
        timestamp: Detection timestamp
    """
    name: str
    process_name: str
    pid: int
    window_title: str
    is_fullscreen: bool
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'process_name': self.process_name,
            'pid': self.pid,
            'window_title': self.window_title,
            'is_fullscreen': self.is_fullscreen,
            'timestamp': self.timestamp,
        }


class GameDatabase:
    """Game database with error handling
    
    Manages known games and their process names.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database
        
        Args:
            db_path: Path to database file
        """
        self._db_path = db_path or "data/games.json"
        self._games: Dict[str, str] = {}  # process_name -> game_name
        self._lock = threading.RLock()
        self._logger = None
        
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
            except Exception:
                pass
        
        # Load default games
        self._load_defaults()
        
        # Load from file
        self._load_from_file()
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="GameDatabase")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="GameDatabase")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="GameDatabase")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="GameDatabase", exc_info=exc_info)
    
    def _load_defaults(self):
        """Load default game list"""
        defaults = {
            # Popular games
            'csgo.exe': 'Counter-Strike: Global Offensive',
            'valorant.exe': 'Valorant',
            'league of legends.exe': 'League of Legends',
            'dota2.exe': 'Dota 2',
            'fortnite.exe': 'Fortnite',
            'minecraft.exe': 'Minecraft',
            'gta5.exe': 'Grand Theft Auto V',
            'EscapeFromTarkov.exe': 'Escape from Tarkov',
            'RainbowSix.exe': 'Rainbow Six Siege',
            'overwatch.exe': 'Overwatch',
            # Steam
            'hl2.exe': 'Half-Life 2',
            'portal2.exe': 'Portal 2',
            # Epic Games
            'FortniteLauncher.exe': 'Fortnite Launcher',
        }
        
        with self._lock:
            self._games.update(defaults)
        
        self._log_debug(f"Loaded {len(defaults)} default games")
    
    def _load_from_file(self):
        """Load games from file with error handling"""
        try:
            if not os.path.exists(self._db_path):
                self._log_debug(f"Database file not found: {self._db_path}")
                return
            
            with open(self._db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                self._log_warning("Invalid database format")
                return
            
            with self._lock:
                self._games.update(data)
            
            self._log_info(f"Loaded {len(data)} games from file")
        
        except json.JSONDecodeError as e:
            self._log_error(f"Failed to parse database: {e}")
        
        except Exception as e:
            self._log_error(f"Failed to load database: {e}", exc_info=True)
    
    def save_to_file(self) -> bool:
        """Save games to file with error handling
        
        Returns:
            True if saved successfully
        """
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
            
            # Write to temp file first
            temp_path = f"{self._db_path}.tmp"
            
            with self._lock:
                data = dict(self._games)
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Replace original file
            if os.path.exists(self._db_path):
                os.replace(temp_path, self._db_path)
            else:
                os.rename(temp_path, self._db_path)
            
            self._log_debug("Database saved")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to save database: {e}", exc_info=True)
            return False
    
    def add_game(self, process_name: str, game_name: str) -> bool:
        """Add game to database
        
        Args:
            process_name: Process executable name
            game_name: Game display name
        
        Returns:
            True if added successfully
        """
        try:
            if not process_name or not game_name:
                self._log_warning("Invalid game data")
                return False
            
            process_name = process_name.lower()
            
            with self._lock:
                self._games[process_name] = game_name
            
            self._log_debug(f"Added game: {process_name} -> {game_name}")
            return True
        
        except Exception as e:
            self._log_error(f"Failed to add game: {e}")
            return False
    
    def lookup(self, process_name: str) -> Optional[str]:
        """Lookup game name by process
        
        Args:
            process_name: Process executable name
        
        Returns:
            Game name or None if not found
        """
        try:
            process_name = process_name.lower()
            
            with self._lock:
                return self._games.get(process_name)
        
        except Exception as e:
            self._log_error(f"Lookup failed: {e}")
            return None
    
    def get_all_process_names(self) -> Set[str]:
        """Get all known process names
        
        Returns:
            Set of process names
        """
        try:
            with self._lock:
                return set(self._games.keys())
        
        except Exception as e:
            self._log_error(f"Failed to get process names: {e}")
            return set()


class GameDetectionService:
    """Game detection service with error handling
    
    v0.3.5o (package 3.9a, stage 7.7b.5.2/7.7)
    
    Features:
    - Automatic game detection
    - Process monitoring
    - Window enumeration
    - Game database
    - Thread-safe operation
    - Comprehensive error handling
    
    Usage:
        >>> service = GameDetectionService(interval=1000)
        >>> service.add_callback(lambda g: print(f"Detected: {g.name}"))
        >>> service.start()
        >>> 
        >>> # Get current game
        >>> game = service.get_current_game()
        >>> if game:
        ...     print(f"Playing: {game['name']}")
        >>> 
        >>> service.stop()
    """
    
    def __init__(self, interval: int = 1000, db_path: Optional[str] = None):
        """Initialize service
        
        Args:
            interval: Detection interval in milliseconds (100-10000)
            db_path: Path to game database
        """
        self._interval = max(100, min(10000, interval))
        self._state = DetectionState.STOPPED
        self._lock = threading.RLock()
        self._thread: Optional[threading.Thread] = None
        self._logger = None
        
        # Game database
        self._database = GameDatabase(db_path)
        
        # Current game
        self._current_game: Optional[GameInfo] = None
        self._last_game: Optional[GameInfo] = None
        
        # Callbacks
        self._callbacks: List[Callable[[GameInfo], None]] = []
        
        # Error tracking
        self._error_count = 0
        self._max_errors = 10
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5
        self._last_error_time = 0.0
        
        # Detection stats
        self._detection_count = 0
        self._last_detection_time = 0.0
        
        # Get logger
        if LOGGER_AVAILABLE:
            try:
                self._logger = AppLogger.get_instance()
                self._log_debug(f"GameDetectionService initializing (interval: {self._interval}ms)")
            except Exception:
                pass
        
        self._log_info(f"Initialized (interval: {self._interval}ms, Windows API: {WINDOWS_AVAILABLE})")
    
    def _log_debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message, component="GameDetection")
    
    def _log_info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message, component="GameDetection")
        else:
            print(f"[GameDetection] {message}")
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message, component="GameDetection")
        else:
            print(f"[GameDetection] WARNING: {message}")
    
    def _log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        if self._logger:
            self._logger.error(message, component="GameDetection", exc_info=exc_info)
        else:
            print(f"[GameDetection] ERROR: {message}")
    
    def start(self) -> bool:
        """Start detection
        
        Returns:
            True if started successfully
        """
        try:
            with self._lock:
                if self._state == DetectionState.RUNNING:
                    self._log_info("Already running")
                    return True
                
                if self._state == DetectionState.STARTING:
                    self._log_warning("Already starting")
                    return False
                
                self._state = DetectionState.STARTING
                self._error_count = 0
                self._consecutive_errors = 0
            
            # Start worker thread
            self._thread = threading.Thread(
                target=self._worker,
                name='GameDetection',
                daemon=True
            )
            self._thread.start()
            
            # Wait for startup
            time.sleep(0.1)
            
            with self._lock:
                if self._state == DetectionState.RUNNING:
                    self._log_info("Started successfully")
                    return True
                else:
                    self._log_error("Failed to start")
                    return False
        
        except Exception as e:
            self._log_error(f"Start failed: {e}", exc_info=True)
            with self._lock:
                self._state = DetectionState.ERROR
            return False
    
    def stop(self) -> bool:
        """Stop detection
        
        Returns:
            True if stopped successfully
        """
        try:
            with self._lock:
                if self._state == DetectionState.STOPPED:
                    self._log_debug("Already stopped")
                    return True
                
                self._state = DetectionState.STOPPING
            
            # Wait for thread
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=2.0)
                
                if self._thread.is_alive():
                    self._log_warning("Thread did not stop gracefully")
                    return False
            
            with self._lock:
                self._state = DetectionState.STOPPED
            
            self._log_info("Stopped successfully")
            return True
        
        except Exception as e:
            self._log_error(f"Stop failed: {e}", exc_info=True)
            return False
    
    def _worker(self):
        """Worker thread with error handling"""
        self._log_debug("Worker thread started")
        
        with self._lock:
            self._state = DetectionState.RUNNING
        
        interval_sec = self._interval / 1000.0
        
        while True:
            with self._lock:
                if self._state != DetectionState.RUNNING:
                    break
            
            try:
                # Check error threshold
                if self._consecutive_errors >= self._max_consecutive_errors:
                    self._log_error(f"Too many consecutive errors ({self._consecutive_errors}), stopping")
                    break
                
                # Detect games
                start_time = time.time()
                game = self._detect_game()
                
                # Update current game
                with self._lock:
                    old_game = self._current_game
                    self._current_game = game
                    
                    if game:
                        self._last_game = game
                        self._consecutive_errors = 0
                        self._detection_count += 1
                        self._last_detection_time = time.time()
                
                # Notify on game change
                if game and (not old_game or old_game.pid != game.pid):
                    self._notify_callbacks(game)
                
                # Sleep
                elapsed = time.time() - start_time
                sleep_time = max(0, interval_sec - elapsed)
                time.sleep(sleep_time)
            
            except Exception as e:
                self._handle_worker_error(e)
        
        with self._lock:
            self._state = DetectionState.STOPPED
        
        self._log_debug("Worker thread stopped")
    
    def _detect_game(self) -> Optional[GameInfo]:
        """Detect running game with error handling
        
        Returns:
            GameInfo or None if no game detected
        """
        try:
            # Get running processes
            processes = self._get_game_processes()
            
            if not processes:
                return None
            
            # Use first detected game
            process, game_name = processes[0]
            
            # Get window info
            window_title = self._get_window_title(process.pid)
            is_fullscreen = self._is_fullscreen(process.pid)
            
            return GameInfo(
                name=game_name,
                process_name=process.name(),
                pid=process.pid,
                window_title=window_title,
                is_fullscreen=is_fullscreen,
                timestamp=time.time()
            )
        
        except Exception as e:
            self._log_error(f"Detection failed: {e}", exc_info=True)
            return None
    
    def _get_game_processes(self) -> List[tuple]:
        """Get running game processes with error handling
        
        Returns:
            List of (process, game_name) tuples
        """
        games = []
        known_processes = self._database.get_all_process_names()
        
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    if proc_name in known_processes:
                        game_name = self._database.lookup(proc_name)
                        if game_name:
                            games.append((proc, game_name))
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process terminated or access denied
                    continue
                
                except Exception as e:
                    self._log_warning(f"Error checking process: {e}")
                    continue
        
        except Exception as e:
            self._log_error(f"Process enumeration failed: {e}", exc_info=True)
        
        return games
    
    def _get_window_title(self, pid: int) -> str:
        """Get window title with error handling
        
        Args:
            pid: Process ID
        
        Returns:
            Window title or empty string
        """
        try:
            if not WINDOWS_AVAILABLE:
                return ""
            
            def callback(hwnd, titles):
                try:
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            titles.append(title)
                except Exception:
                    pass
            
            titles = []
            win32gui.EnumWindows(callback, titles)
            
            return titles[0] if titles else ""
        
        except Exception as e:
            self._log_warning(f"Failed to get window title: {e}")
            return ""
    
    def _is_fullscreen(self, pid: int) -> bool:
        """Check if window is fullscreen with error handling
        
        Args:
            pid: Process ID
        
        Returns:
            True if fullscreen
        """
        try:
            if not WINDOWS_AVAILABLE:
                return False
            
            # Simple check: look for fullscreen window
            # (This is a simplified version)
            return False
        
        except Exception as e:
            self._log_warning(f"Fullscreen check failed: {e}")
            return False
    
    def _handle_worker_error(self, error: Exception):
        """Handle worker thread error
        
        Args:
            error: Exception that occurred
        """
        now = time.time()
        
        # Reset error count after cooldown
        if now - self._last_error_time > 60.0:
            self._error_count = 0
        
        self._error_count += 1
        self._consecutive_errors += 1
        self._last_error_time = now
        
        self._log_error(
            f"Worker error ({self._error_count}/{self._max_errors}, consecutive: {self._consecutive_errors}): {error}",
            exc_info=True
        )
        
        # Sleep longer after error
        time.sleep(1.0)
    
    def _notify_callbacks(self, game: GameInfo):
        """Notify callbacks with error isolation
        
        Args:
            game: Detected game info
        """
        for callback in self._callbacks:
            try:
                callback(game)
            except Exception as e:
                self._log_error(f"Callback error: {e}", exc_info=True)
    
    def add_callback(self, callback: Callable[[GameInfo], None]) -> int:
        """Add detection callback
        
        Args:
            callback: Callback function(game_info)
        
        Returns:
            Callback ID
        """
        try:
            with self._lock:
                callback_id = len(self._callbacks)
                self._callbacks.append(callback)
                self._log_debug(f"Added callback (ID: {callback_id})")
                return callback_id
        
        except Exception as e:
            self._log_error(f"Failed to add callback: {e}")
            return -1
    
    def remove_callback(self, callback_id: int):
        """Remove callback
        
        Args:
            callback_id: Callback ID
        """
        try:
            with self._lock:
                if 0 <= callback_id < len(self._callbacks):
                    self._callbacks[callback_id] = lambda g: None
                    self._log_debug(f"Removed callback (ID: {callback_id})")
        
        except Exception as e:
            self._log_error(f"Failed to remove callback: {e}")
    
    def get_current_game(self) -> Optional[Dict[str, Any]]:
        """Get current game as dictionary
        
        Returns:
            Game dictionary or None
        """
        try:
            with self._lock:
                if self._current_game:
                    return self._current_game.to_dict()
                return None
        
        except Exception as e:
            self._log_error(f"Failed to get current game: {e}")
            return None
    
    def get_state(self) -> DetectionState:
        """Get current state
        
        Returns:
            Current detection state
        """
        try:
            with self._lock:
                return self._state
        except Exception:
            return DetectionState.ERROR
    
    def is_running(self) -> bool:
        """Check if detection is running
        
        Returns:
            True if running
        """
        return self.get_state() == DetectionState.RUNNING
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status
        
        Returns:
            Status dictionary
        """
        try:
            with self._lock:
                return {
                    'state': self._state.value,
                    'interval': self._interval,
                    'detection_count': self._detection_count,
                    'error_count': self._error_count,
                    'consecutive_errors': self._consecutive_errors,
                    'has_game': self._current_game is not None,
                    'windows_api': WINDOWS_AVAILABLE,
                    'last_detection': self._last_detection_time,
                }
        
        except Exception as e:
            self._log_error(f"Failed to get status: {e}")
            return {'error': str(e)}
    
    def add_game_to_database(self, process_name: str, game_name: str) -> bool:
        """Add game to database
        
        Args:
            process_name: Process executable name
            game_name: Game display name
        
        Returns:
            True if added successfully
        """
        return self._database.add_game(process_name, game_name)
    
    def save_database(self) -> bool:
        """Save database to file
        
        Returns:
            True if saved successfully
        """
        return self._database.save_to_file()


# Testing
if __name__ == '__main__':
    print("="*60)
    print("GameDetectionService Test (with Error Handling)")
    print("="*60)
    print()
    
    # Create service
    service = GameDetectionService(interval=1000)
    
    # Add callback
    def on_game_detected(game: GameInfo):
        print(f"\n🎮 Detected: {game.name}")
        print(f"   Process: {game.process_name} (PID: {game.pid})")
        print(f"   Window: {game.window_title}")
        print(f"   Fullscreen: {game.is_fullscreen}")
    
    service.add_callback(on_game_detected)
    
    # Start detection
    print("Starting detection...")
    if service.start():
        print("✅ Started\n")
    else:
        print("❌ Failed to start\n")
    
    # Monitor for 10 seconds
    print("Monitoring for 10 seconds...")
    print("(Launch a game to test detection)\n")
    
    for i in range(10):
        time.sleep(1)
        game = service.get_current_game()
        if game:
            print(f"[{i+1}] Playing: {game['name']}")
        else:
            print(f"[{i+1}] No game detected")
    
    # Get status
    status = service.get_status()
    print("\nStatus:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Stop
    print("\nStopping detection...")
    if service.stop():
        print("✅ Stopped")
    else:
        print("❌ Failed to stop")
    
    print()
    print("✅ Test completed!")
