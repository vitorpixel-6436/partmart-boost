"""Game Detection System

Version: 0.3.5a
"""
import psutil
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from .game_profiles import GameProfileManager, GameProfile


@dataclass
class DetectedGame:
    """Detected running game"""
    profile: GameProfile
    pid: int
    exe_name: str
    profile_applied: bool = False


class GameDetector:
    """Detect running games and apply profiles"""
    
    def __init__(self, profile_manager: GameProfileManager):
        self.profile_manager = profile_manager
        self.detected_games: Dict[int, DetectedGame] = {}
        
        # Callbacks
        self.on_game_started: Optional[Callable] = None
        self.on_game_stopped: Optional[Callable] = None
    
    def update(self):
        """Check for running games"""
        current_pids = set()
        
        # Check all processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                exe_name = proc.info['name']
                
                if not exe_name:
                    continue
                
                # Check if this exe matches any profile
                profile = self.profile_manager.get_profile_by_exe(exe_name)
                
                if profile:
                    current_pids.add(pid)
                    
                    # New game detected
                    if pid not in self.detected_games:
                        game = DetectedGame(
                            profile=profile,
                            pid=pid,
                            exe_name=exe_name
                        )
                        self.detected_games[pid] = game
                        
                        print(f"[GAME] Detected: {profile.game_name} (PID: {pid})")
                        
                        if self.on_game_started:
                            self.on_game_started(game)
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Check for stopped games
        stopped_pids = set(self.detected_games.keys()) - current_pids
        
        for pid in stopped_pids:
            game = self.detected_games.pop(pid)
            print(f"[GAME] Stopped: {game.profile.game_name} (PID: {pid})")
            
            if self.on_game_stopped:
                self.on_game_stopped(game)
    
    def get_detected_games(self) -> list:
        """Get currently detected games"""
        return list(self.detected_games.values())
    
    def mark_profile_applied(self, pid: int):
        """Mark profile as applied for game"""
        if pid in self.detected_games:
            self.detected_games[pid].profile_applied = True


if __name__ == "__main__":
    import time
    
    print("[TEST] Game Detector")
    print("="*60)
    
    from game_profiles import GameProfileManager
    
    manager = GameProfileManager("../../config/profiles")
    detector = GameDetector(manager)
    
    def on_started(game):
        print(f"[CALLBACK] Game started: {game.profile.game_name}")
    
    def on_stopped(game):
        print(f"[CALLBACK] Game stopped: {game.profile.game_name}")
    
    detector.on_game_started = on_started
    detector.on_game_stopped = on_stopped
    
    print("\n[INFO] Monitoring for games... (Press Ctrl+C to stop)")
    
    try:
        while True:
            detector.update()
            
            games = detector.get_detected_games()
            if games:
                print(f"\r[INFO] Active games: {len(games)}", end="", flush=True)
            
            time.sleep(3)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("✅ Detector test complete!")
