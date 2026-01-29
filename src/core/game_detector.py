#!/usr/bin/env python3
"""Game Detector - Automatic game process detection

Version: 0.3.5d (package 3.9a, stage 7.7c)

Real game detection using process monitoring.
NO STUBS - actual process detection!
"""
import psutil
import time
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from threading import Thread, Lock


@dataclass
class GameProcess:
    """Detected game process"""
    pid: int
    name: str
    exe_path: str
    display_name: str
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    create_time: float = 0.0


class GameDetector:
    """Automatic game detection system
    
    Monitors running processes and detects known games.
    Uses whitelist of game executables.
    
    v0.3.5d - Stage 7.7c: Real implementation
    """
    
    # Known game executables (expand as needed)
    KNOWN_GAMES = {
        # Popular games
        'GTA5.exe': 'Grand Theft Auto V',
        'RDR2.exe': 'Red Dead Redemption 2',
        'Cyberpunk2077.exe': 'Cyberpunk 2077',
        'witcher3.exe': 'The Witcher 3',
        'EscapeFromTarkov.exe': 'Escape from Tarkov',
        'Valorant.exe': 'Valorant',
        'FortniteClient-Win64-Shipping.exe': 'Fortnite',
        'csgo.exe': 'Counter-Strike: Global Offensive',
        'cs2.exe': 'Counter-Strike 2',
        'overwatch.exe': 'Overwatch',
        'ApexLegends.exe': 'Apex Legends',
        'destiny2.exe': 'Destiny 2',
        'EldenRing.exe': 'Elden Ring',
        'DarkSoulsIII.exe': 'Dark Souls III',
        'sekiro.exe': 'Sekiro: Shadows Die Twice',
        'MonsterHunterWorld.exe': 'Monster Hunter: World',
        'MHRise.exe': 'Monster Hunter Rise',
        'DOOM.exe': 'DOOM',
        'DOOMEternal.exe': 'DOOM Eternal',
        'Minecraft.exe': 'Minecraft',
        'javaw.exe': 'Minecraft Java',
        'StarCitizen.exe': 'Star Citizen',
        'HorizonZeroDawn.exe': 'Horizon Zero Dawn',
        'GoW.exe': 'God of War',
        'SpiderMan.exe': 'Spider-Man',
        'RatchetAndClank.exe': 'Ratchet & Clank',
        'FIFA23.exe': 'FIFA 23',
        'FC24.exe': 'EA Sports FC 24',
        'NBA2K23.exe': 'NBA 2K23',
        'BattlefieldV.exe': 'Battlefield V',
        'Battlefield2042.exe': 'Battlefield 2042',
        'CoD.exe': 'Call of Duty',
        'ModernWarfare.exe': 'Call of Duty: Modern Warfare',
        'Warzone.exe': 'Call of Duty: Warzone',
        # Launchers (sometimes used)
        'steam.exe': 'Steam',
        'EpicGamesLauncher.exe': 'Epic Games',
        'Origin.exe': 'EA Origin',
        'uplay.exe': 'Ubisoft Connect',
    }
    
    def __init__(self):
        self.name = "GameDetector"
        self._running = False
        self._thread = None
        self._lock = Lock()
        self._detected_games: Dict[int, GameProcess] = {}
        self._scan_interval = 2.0  # seconds
        self._callbacks: List[callable] = []
    
    def start(self) -> bool:
        """Start game detection"""
        if self._running:
            return True
        
        self._running = True
        self._thread = Thread(target=self._detection_loop, daemon=True)
        self._thread.start()
        return True
    
    def stop(self) -> bool:
        """Stop game detection"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        return True
    
    def _detection_loop(self):
        """Main detection loop"""
        while self._running:
            try:
                self._scan_processes()
            except Exception as e:
                print(f"Error scanning processes: {e}")
            
            time.sleep(self._scan_interval)
    
    def _scan_processes(self):
        """Scan for game processes"""
        current_games: Dict[int, GameProcess] = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                name = proc.info['name']
                
                # Check if this is a known game
                if name in self.KNOWN_GAMES:
                    exe_path = proc.info['exe'] or ''
                    display_name = self.KNOWN_GAMES[name]
                    
                    # Get resource usage
                    cpu_percent = proc.info['cpu_percent'] or 0.0
                    memory_mb = (proc.info['memory_info'].rss / (1024 * 1024)) if proc.info['memory_info'] else 0.0
                    create_time = proc.info['create_time'] or time.time()
                    
                    game = GameProcess(
                        pid=proc.info['pid'],
                        name=name,
                        exe_path=exe_path,
                        display_name=display_name,
                        cpu_percent=cpu_percent,
                        memory_mb=memory_mb,
                        create_time=create_time
                    )
                    current_games[game.pid] = game
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Update detected games and trigger callbacks
        with self._lock:
            # Check for new games
            new_pids = set(current_games.keys()) - set(self._detected_games.keys())
            if new_pids:
                for pid in new_pids:
                    game = current_games[pid]
                    print(f"Game detected: {game.display_name} (PID: {pid})")
                    self._notify_callbacks('detected', game)
            
            # Check for closed games
            closed_pids = set(self._detected_games.keys()) - set(current_games.keys())
            if closed_pids:
                for pid in closed_pids:
                    game = self._detected_games[pid]
                    print(f"Game closed: {game.display_name} (PID: {pid})")
                    self._notify_callbacks('closed', game)
            
            self._detected_games = current_games
    
    def get_detected_games(self) -> List[GameProcess]:
        """Get currently detected games"""
        with self._lock:
            return list(self._detected_games.values())
    
    def is_game_running(self, name: str) -> bool:
        """Check if specific game is running"""
        with self._lock:
            return any(g.name.lower() == name.lower() or g.display_name.lower() == name.lower() 
                      for g in self._detected_games.values())
    
    def get_game_by_name(self, name: str) -> Optional[GameProcess]:
        """Get game process by name"""
        with self._lock:
            for game in self._detected_games.values():
                if game.name.lower() == name.lower() or game.display_name.lower() == name.lower():
                    return game
        return None
    
    def register_callback(self, callback: callable):
        """Register callback for game events
        
        Callback signature: callback(event_type: str, game: GameProcess)
        event_type: 'detected' or 'closed'
        """
        self._callbacks.append(callback)
    
    def _notify_callbacks(self, event_type: str, game: GameProcess):
        """Notify registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(event_type, game)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def add_game(self, exe_name: str, display_name: str):
        """Add custom game to detection list"""
        self.KNOWN_GAMES[exe_name] = display_name
    
    def check_health(self) -> dict:
        """Check detector health"""
        games = self.get_detected_games()
        
        return {
            'status': 'healthy',
            'message': f'Monitoring {len(games)} game(s)'
        }


# Singleton instance
_game_detector = None

def get_game_detector() -> GameDetector:
    """Get singleton game detector instance"""
    global _game_detector
    if _game_detector is None:
        _game_detector = GameDetector()
    return _game_detector


if __name__ == '__main__':
    # Test game detector
    print("Testing Game Detector...\n")
    
    detector = GameDetector()
    
    # Register callback
    def on_game_event(event_type: str, game: GameProcess):
        print(f"\n🎮 Event: {event_type}")
        print(f"   Game: {game.display_name}")
        print(f"   PID: {game.pid}")
        print(f"   CPU: {game.cpu_percent:.1f}%")
        print(f"   Memory: {game.memory_mb:.0f} MB")
    
    detector.register_callback(on_game_event)
    detector.start()
    
    print("Scanning for games for 30 seconds...")
    print("(Launch a game to test detection)\n")
    
    for i in range(30):
        time.sleep(1)
        games = detector.get_detected_games()
        if games:
            print(f"\rDetected: {', '.join(g.display_name for g in games)}", end='')
    
    print("\n\nFinal results:")
    games = detector.get_detected_games()
    if games:
        for game in games:
            print(f"\n  {game.display_name}")
            print(f"    PID: {game.pid}")
            print(f"    CPU: {game.cpu_percent:.1f}%")
            print(f"    Memory: {game.memory_mb:.0f} MB")
            print(f"    Path: {game.exe_path}")
    else:
        print("  No games detected")
    
    detector.stop()
    print("\n✅ Game Detector test complete!")
