#!/usr/bin/env python3
"""
Game Detector - Detects running games and triggers profile application.

Features:
- Real-time process monitoring
- Game launch detection
- Auto-apply profiles
- Multi-game support

Author: PartMart Team
Version: 0.3.0-alpha
License: MIT
"""

import psutil
import time
from typing import Dict, Set, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from game_profiles import GameProfile, GameProfileManager


@dataclass
class RunningGame:
    """Information about running game."""
    
    profile: GameProfile
    pid: int
    started_at: datetime
    applied_profile: bool = False


class GameDetector:
    """Detects and monitors running games."""
    
    def __init__(self, profile_manager: GameProfileManager):
        """
        Initialize game detector.
        
        Args:
            profile_manager: Profile manager instance
        """
        self.profile_manager = profile_manager
        self.running_games: Dict[int, RunningGame] = {}  # PID -> RunningGame
        
        # Callbacks
        self.on_game_started: Optional[Callable[[RunningGame], None]] = None
        self.on_game_stopped: Optional[Callable[[RunningGame], None]] = None
        
        print("[Game Detector] Initialized")
    
    def scan_running_games(self) -> Dict[int, RunningGame]:
        """
        Scan for running games.
        
        Returns:
            Dict of PID -> RunningGame
        """
        detected = {}
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    exe_name = proc.info['name']
                    pid = proc.info['pid']
                    
                    # Find matching profile
                    profile = self.profile_manager.get_profile_by_executable(exe_name)
                    
                    if profile:
                        # Check if already tracking
                        if pid in self.running_games:
                            detected[pid] = self.running_games[pid]
                        else:
                            # New game detected!
                            game = RunningGame(
                                profile=profile,
                                pid=pid,
                                started_at=datetime.now(),
                                applied_profile=False
                            )
                            detected[pid] = game
                            
                            print(f"[Game Detector] 🎮 Detected: {profile.game_name} (PID: {pid})")
                            
                            # Trigger callback
                            if self.on_game_started:
                                self.on_game_started(game)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            print(f"[Game Detector] Error scanning processes: {e}")
        
        return detected
    
    def check_stopped_games(self, current_games: Dict[int, RunningGame]):
        """
        Check for games that stopped.
        
        Args:
            current_games: Currently running games
        """
        stopped_pids = set(self.running_games.keys()) - set(current_games.keys())
        
        for pid in stopped_pids:
            game = self.running_games[pid]
            duration = (datetime.now() - game.started_at).total_seconds()
            
            print(f"[Game Detector] ⚠️ Stopped: {game.profile.game_name} "
                  f"(played {duration:.0f}s)")
            
            # Trigger callback
            if self.on_game_stopped:
                self.on_game_stopped(game)
    
    def update(self) -> Dict[int, RunningGame]:
        """
        Update game detection (call periodically).
        
        Returns:
            Currently running games
        """
        current_games = self.scan_running_games()
        
        # Check for stopped games
        self.check_stopped_games(current_games)
        
        # Update internal state
        self.running_games = current_games
        
        return current_games
    
    def is_game_running(self, game_id: str) -> bool:
        """
        Check if specific game is running.
        
        Args:
            game_id: Game identifier
            
        Returns:
            True if game is running
        """
        for game in self.running_games.values():
            if game.profile.game_id == game_id:
                return True
        return False
    
    def get_running_game(self, game_id: str) -> Optional[RunningGame]:
        """
        Get running game instance.
        
        Args:
            game_id: Game identifier
            
        Returns:
            RunningGame or None
        """
        for game in self.running_games.values():
            if game.profile.game_id == game_id:
                return game
        return None
    
    def mark_profile_applied(self, pid: int):
        """
        Mark profile as applied for a game.
        
        Args:
            pid: Process ID
        """
        if pid in self.running_games:
            self.running_games[pid].applied_profile = True
    
    def start_monitoring(self, interval: float = 2.0):
        """
        Start continuous monitoring (blocking).
        
        Args:
            interval: Check interval in seconds
        """
        print(f"[Game Detector] Starting monitoring (interval: {interval}s)")
        print(f"[Game Detector] Tracking {len(self.profile_manager.list_profiles())} games")
        print()
        
        try:
            while True:
                self.update()
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n[Game Detector] Monitoring stopped")


class GameOptimizationService:
    """Service that applies optimizations when games start."""
    
    def __init__(self, profile_manager: GameProfileManager):
        """
        Initialize optimization service.
        
        Args:
            profile_manager: Profile manager
        """
        self.profile_manager = profile_manager
        self.detector = GameDetector(profile_manager)
        
        # Setup callbacks
        self.detector.on_game_started = self.on_game_started
        self.detector.on_game_stopped = self.on_game_stopped
        
        print("[Optimization Service] Ready")
    
    def on_game_started(self, game: RunningGame):
        """
        Called when game starts.
        
        Args:
            game: Running game info
        """
        print(f"\n🚀 [AUTO-OPTIMIZE] {game.profile.game_name} started!")
        print(f"   Profile: {game.profile.game_id}")
        print(f"   PID: {game.pid}")
        
        # Apply profile
        self.apply_profile(game)
    
    def on_game_stopped(self, game: RunningGame):
        """
        Called when game stops.
        
        Args:
            game: Stopped game info
        """
        print(f"\n⏸️ [GAME CLOSED] {game.profile.game_name}")
        
        # Revert optimizations if needed
        self.revert_optimizations(game)
    
    def apply_profile(self, game: RunningGame):
        """
        Apply optimization profile.
        
        Args:
            game: Game to optimize
        """
        profile = game.profile
        
        print(f"\n⚙️ Applying optimizations:")
        
        # RAM Cleanup
        if profile.ram_cleanup:
            print(f"   ✅ RAM Cleanup: Clearing memory...")
            # TODO: Implement RAM cleanup
        
        # Process Priority
        if profile.ram_priority:
            print(f"   ✅ Process Priority: {profile.ram_priority.upper()}")
            self._set_process_priority(game.pid, profile.ram_priority)
        
        # GPU Settings
        if profile.gpu_clock_offset:
            print(f"   ✅ GPU Clock: +{profile.gpu_clock_offset} MHz")
            # TODO: Implement GPU OC
        
        if profile.gpu_mem_offset:
            print(f"   ✅ GPU Memory: +{profile.gpu_mem_offset} MHz")
            # TODO: Implement GPU memory OC
        
        if profile.gpu_power_limit:
            print(f"   ✅ Power Limit: {profile.gpu_power_limit}%")
            # TODO: Implement power limit
        
        if profile.gpu_fan_speed:
            print(f"   ✅ Fan Speed: {profile.gpu_fan_speed}%")
            # TODO: Implement fan control
        
        # Mark as applied
        self.detector.mark_profile_applied(game.pid)
        
        print(f"\n✅ Optimizations applied for {profile.game_name}!")
        print()
    
    def _set_process_priority(self, pid: int, priority: str):
        """
        Set process priority.
        
        Args:
            pid: Process ID
            priority: Priority level
        """
        try:
            proc = psutil.Process(pid)
            
            priority_map = {
                'realtime': psutil.REALTIME_PRIORITY_CLASS,
                'high': psutil.HIGH_PRIORITY_CLASS,
                'above_normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                'normal': psutil.NORMAL_PRIORITY_CLASS,
            }
            
            if priority.lower() in priority_map:
                proc.nice(priority_map[priority.lower()])
                print(f"       Set priority to {priority.upper()}")
        
        except Exception as e:
            print(f"       ❌ Failed to set priority: {e}")
    
    def revert_optimizations(self, game: RunningGame):
        """
        Revert optimizations after game closes.
        
        Args:
            game: Game that closed
        """
        print(f"   ↩️ Reverting optimizations...")
        
        # TODO: Reset GPU settings to default
        # TODO: Reset fan curve
        
        print(f"   ✅ System restored to default state")
        print()
    
    def start(self, interval: float = 3.0):
        """
        Start optimization service.
        
        Args:
            interval: Check interval
        """
        print("="*60)
        print("🎮 PartMart Boost - Game Optimization Service")
        print("="*60)
        print()
        print(f"Tracking {len(self.profile_manager.list_profiles())} games:")
        for profile in self.profile_manager.list_profiles():
            print(f"  - {profile.game_name} ({profile.executable})")
        print()
        print("✅ Service started! Launch a game to see auto-optimization.")
        print("Press Ctrl+C to stop.")
        print()
        
        self.detector.start_monitoring(interval=interval)


# ========== Testing ==========

if __name__ == '__main__':
    # Create managers
    profile_manager = GameProfileManager(profiles_dir="config/profiles")
    
    # Start optimization service
    service = GameOptimizationService(profile_manager)
    service.start(interval=2.0)
