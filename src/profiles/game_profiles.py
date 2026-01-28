#!/usr/bin/env python3
"""
Game Profiles System - Automatic optimization for detected games.

Features:
- Game detection (running processes)
- Per-game optimization profiles
- Auto-apply on game launch
- Profile templates for popular games

Author: PartMart Team
Version: 0.3.6-alpha
License: MIT
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class GameProfile:
    """Game optimization profile."""
    
    game_id: str                      # Unique ID (e.g., "gta5")
    game_name: str                    # Display name
    executable: str                   # Process name (e.g., "GTA5.exe")
    
    # GPU Settings
    gpu_power_limit: Optional[int] = None      # Power limit % (e.g., 110)
    gpu_clock_offset: Optional[int] = None     # Clock offset MHz (e.g., +150)
    gpu_mem_offset: Optional[int] = None       # Memory offset MHz (e.g., +500)
    gpu_fan_speed: Optional[int] = None        # Fan speed % (e.g., 75)
    
    # RAM Settings
    ram_cleanup: bool = True                   # Clear RAM before launch
    ram_priority: str = "high"                 # Process priority
    
    # System Settings
    fullscreen: bool = True                    # Force fullscreen
    disable_overlays: bool = False             # Disable overlays
    
    # Advanced
    custom_args: Optional[str] = None          # Launch arguments
    notes: str = ""                            # User notes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameProfile':
        """Create from dictionary."""
        return cls(**data)


class GameProfileManager:
    """Manages game profiles."""
    
    def __init__(self, profiles_dir: str = "config/profiles"):
        """
        Initialize profile manager.
        
        Args:
            profiles_dir: Directory for profile files
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self.profiles: Dict[str, GameProfile] = {}
        self._load_all_profiles()
        
        # Load default templates if no profiles exist
        if not self.profiles:
            self._create_default_profiles()
        
        print(f"[Game Profiles] Loaded {len(self.profiles)} profiles")
    
    def _load_all_profiles(self):
        """Load all profiles from disk."""
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profile = GameProfile.from_dict(data)
                    self.profiles[profile.game_id] = profile
            except Exception as e:
                print(f"[Game Profiles] Failed to load {profile_file}: {e}")
    
    def _create_default_profiles(self):
        """Create default game profiles."""
        defaults = [
            # GTA 5
            GameProfile(
                game_id="gta5",
                game_name="Grand Theft Auto V",
                executable="GTA5.exe",
                gpu_power_limit=110,
                gpu_clock_offset=100,
                gpu_mem_offset=400,
                gpu_fan_speed=70,
                ram_cleanup=True,
                ram_priority="high",
                fullscreen=True,
                notes="Оптимизация для GTA 5: +100 MHz GPU, +400 MHz VRAM"
            ),
            
            # Cyberpunk 2077
            GameProfile(
                game_id="cyberpunk2077",
                game_name="Cyberpunk 2077",
                executable="Cyberpunk2077.exe",
                gpu_power_limit=115,
                gpu_clock_offset=150,
                gpu_mem_offset=500,
                gpu_fan_speed=75,
                ram_cleanup=True,
                ram_priority="realtime",
                fullscreen=True,
                notes="Максимальная производительность для Cyberpunk 2077"
            ),
            
            # CS:GO / CS2
            GameProfile(
                game_id="cs2",
                game_name="Counter-Strike 2",
                executable="cs2.exe",
                gpu_power_limit=100,
                gpu_clock_offset=50,
                gpu_mem_offset=200,
                gpu_fan_speed=60,
                ram_cleanup=True,
                ram_priority="high",
                fullscreen=True,
                custom_args="-high -threads 12 -freq 240",
                notes="Оптимизация для конкурентной игры: низкая задержка"
            ),
            
            # Escape from Tarkov
            GameProfile(
                game_id="tarkov",
                game_name="Escape from Tarkov",
                executable="EscapeFromTarkov.exe",
                gpu_power_limit=110,
                gpu_clock_offset=120,
                gpu_mem_offset=450,
                gpu_fan_speed=70,
                ram_cleanup=True,
                ram_priority="high",
                fullscreen=True,
                notes="Tarkov: очистка RAM критична из-за утечек памяти"
            ),
            
            # Minecraft
            GameProfile(
                game_id="minecraft",
                game_name="Minecraft (Java)",
                executable="javaw.exe",
                gpu_power_limit=90,
                gpu_clock_offset=0,
                gpu_mem_offset=0,
                gpu_fan_speed=50,
                ram_cleanup=False,
                ram_priority="normal",
                fullscreen=False,
                custom_args="-Xmx8G -Xms4G",
                notes="Оптимизация Java: больше RAM, меньше GPU"
            ),
            
            # Valorant
            GameProfile(
                game_id="valorant",
                game_name="Valorant",
                executable="VALORANT-Win64-Shipping.exe",
                gpu_power_limit=100,
                gpu_clock_offset=50,
                gpu_mem_offset=150,
                gpu_fan_speed=60,
                ram_cleanup=True,
                ram_priority="high",
                fullscreen=True,
                notes="Низкая задержка для шутера"
            ),
            
            # League of Legends
            GameProfile(
                game_id="league",
                game_name="League of Legends",
                executable="League of Legends.exe",
                gpu_power_limit=95,
                gpu_clock_offset=0,
                gpu_mem_offset=0,
                gpu_fan_speed=50,
                ram_cleanup=False,
                ram_priority="normal",
                fullscreen=True,
                notes="Легкая игра, консервативные настройки"
            ),
            
            # Red Dead Redemption 2
            GameProfile(
                game_id="rdr2",
                game_name="Red Dead Redemption 2",
                executable="RDR2.exe",
                gpu_power_limit=115,
                gpu_clock_offset=150,
                gpu_mem_offset=500,
                gpu_fan_speed=80,
                ram_cleanup=True,
                ram_priority="high",
                fullscreen=True,
                notes="Тяжелая игра: максимальные настройки GPU"
            ),
        ]
        
        for profile in defaults:
            self.save_profile(profile)
        
        print(f"[Game Profiles] Created {len(defaults)} default profiles")
    
    def save_profile(self, profile: GameProfile):
        """
        Save profile to disk.
        
        Args:
            profile: Profile to save
        """
        self.profiles[profile.game_id] = profile
        
        profile_path = self.profiles_dir / f"{profile.game_id}.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_profile(self, game_id: str) -> Optional[GameProfile]:
        """
        Get profile by game ID.
        
        Args:
            game_id: Game identifier
            
        Returns:
            Game profile or None
        """
        return self.profiles.get(game_id)
    
    def get_profile_by_executable(self, exe_name: str) -> Optional[GameProfile]:
        """
        Find profile by executable name.
        
        Args:
            exe_name: Executable name (e.g., "GTA5.exe")
            
        Returns:
            Matching profile or None
        """
        exe_lower = exe_name.lower()
        
        for profile in self.profiles.values():
            if profile.executable.lower() == exe_lower:
                return profile
        
        return None
    
    def list_profiles(self) -> List[GameProfile]:
        """
        Get all profiles.
        
        Returns:
            List of all profiles
        """
        return list(self.profiles.values())
    
    def delete_profile(self, game_id: str) -> bool:
        """
        Delete profile.
        
        Args:
            game_id: Game identifier
            
        Returns:
            True if deleted
        """
        if game_id in self.profiles:
            del self.profiles[game_id]
            
            profile_path = self.profiles_dir / f"{game_id}.json"
            if profile_path.exists():
                profile_path.unlink()
            
            return True
        return False
    
    def create_profile(
        self,
        game_id: str,
        game_name: str,
        executable: str,
        **kwargs
    ) -> GameProfile:
        """
        Create new profile.
        
        Args:
            game_id: Unique ID
            game_name: Display name
            executable: Process name
            **kwargs: Additional settings
            
        Returns:
            Created profile
        """
        profile = GameProfile(
            game_id=game_id,
            game_name=game_name,
            executable=executable,
            **kwargs
        )
        
        self.save_profile(profile)
        return profile
    
    def update_profile(self, game_id: str, **updates) -> Optional[GameProfile]:
        """
        Update existing profile.
        
        Args:
            game_id: Game ID to update
            **updates: Fields to update
            
        Returns:
            Updated profile or None
        """
        profile = self.get_profile(game_id)
        if not profile:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        self.save_profile(profile)
        return profile


# ========== Testing ==========

if __name__ == '__main__':
    print("="*60)
    print("Game Profiles System Test")
    print("="*60)
    print()
    
    # Create manager
    manager = GameProfileManager(profiles_dir="test_profiles")
    
    # List all profiles
    print(f"Loaded profiles: {len(manager.list_profiles())}")
    print()
    
    for profile in manager.list_profiles():
        print(f"[{profile.game_id}] {profile.game_name}")
        print(f"  Executable: {profile.executable}")
        print(f"  GPU: +{profile.gpu_clock_offset}MHz core, +{profile.gpu_mem_offset}MHz mem")
        print(f"  RAM Cleanup: {profile.ram_cleanup}")
        print(f"  Notes: {profile.notes}")
        print()
    
    # Test executable search
    print("Testing executable search...")
    test_exes = ["GTA5.exe", "Cyberpunk2077.exe", "cs2.exe", "unknown.exe"]
    
    for exe in test_exes:
        profile = manager.get_profile_by_executable(exe)
        if profile:
            print(f"✅ {exe} → {profile.game_name}")
        else:
            print(f"❌ {exe} → Not found")
    
    print()
    print("="*60)
    print("✅ Game Profiles System works!")
    print("="*60)
