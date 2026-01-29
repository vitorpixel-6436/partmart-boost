#!/usr/bin/env python3
"""Game Profile Manager - Per-game configuration and profiles

Version: 0.3.5d (package 3.9a, stage 7.7d)

Manages game-specific profiles with FSR settings, optimization preferences,
and auto-injection configuration.
"""
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

try:
    from core.fsr_manager import FSRConfig, FSRPreset, FSRVersion
except ImportError:
    FSRConfig = None
    FSRPreset = None
    FSRVersion = None


class AutoInjectMode(Enum):
    """Auto-injection modes"""
    DISABLED = "disabled"        # Never auto-inject
    ASK = "ask"                  # Ask user
    AUTO = "auto"                # Automatic injection


class OptimizationLevel(Enum):
    """System optimization levels"""
    NONE = "none"                # No optimization
    MINIMAL = "minimal"          # Minimal tweaks
    BALANCED = "balanced"        # Balanced optimization
    AGGRESSIVE = "aggressive"    # Maximum performance


@dataclass
class GameProfile:
    """Complete game profile with all settings"""
    # Basic info
    game_name: str
    executable: str
    display_name: str = ""
    game_path: str = ""
    
    # FSR settings
    fsr_enabled: bool = True
    fsr_config: Optional[Dict] = None  # FSRConfig as dict
    
    # Auto-injection
    auto_inject: AutoInjectMode = AutoInjectMode.ASK
    auto_inject_delay: float = 5.0  # seconds after game start
    
    # Optimization
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    priority_boost: bool = True
    disable_overlays: bool = False
    fullscreen_optimization: bool = True
    
    # Monitoring
    enable_monitoring: bool = True
    fps_overlay: bool = False
    performance_logging: bool = False
    
    # Custom settings
    custom_settings: Dict = None
    
    def __post_init__(self):
        if self.display_name == "":
            self.display_name = self.game_name
        if self.custom_settings is None:
            self.custom_settings = {}
        if self.fsr_config is None:
            self.fsr_config = {}


class GameProfileManager:
    """Game profile management system
    
    Manages per-game profiles with FSR settings, optimization preferences,
    and auto-injection configuration.
    
    v0.3.5d - Stage 7.7d: Profile system
    """
    
    def __init__(self, profiles_dir: str = 'data/profiles'):
        self.name = "GameProfileManager"
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Loaded profiles
        self._profiles: Dict[str, GameProfile] = {}
        
        # Load all profiles
        self._load_all_profiles()
    
    def create_profile(
        self,
        game_name: str,
        executable: str,
        display_name: str = "",
        **kwargs
    ) -> GameProfile:
        """Create new game profile
        
        Args:
            game_name: Internal game identifier
            executable: Game executable name (e.g., 'GTA5.exe')
            display_name: Human-readable name
            **kwargs: Additional profile settings
        
        Returns:
            New game profile
        """
        profile = GameProfile(
            game_name=game_name,
            executable=executable,
            display_name=display_name or game_name,
            **kwargs
        )
        
        self._profiles[game_name] = profile
        return profile
    
    def save_profile(self, profile: GameProfile) -> bool:
        """Save game profile to disk
        
        Args:
            profile: Game profile to save
        
        Returns:
            True if saved successfully
        """
        try:
            profile_file = self.profiles_dir / f"{profile.game_name}.json"
            
            # Convert to dict
            profile_dict = asdict(profile)
            # Convert enums to strings
            profile_dict['auto_inject'] = profile.auto_inject.value
            profile_dict['optimization_level'] = profile.optimization_level.value
            
            with open(profile_file, 'w') as f:
                json.dump(profile_dict, f, indent=2)
            
            self._profiles[profile.game_name] = profile
            return True
        
        except Exception as e:
            print(f"Error saving profile for {profile.game_name}: {e}")
            return False
    
    def load_profile(self, game_name: str) -> Optional[GameProfile]:
        """Load game profile from disk
        
        Args:
            game_name: Game identifier
        
        Returns:
            Game profile or None if not found
        """
        # Check cache first
        if game_name in self._profiles:
            return self._profiles[game_name]
        
        # Load from file
        try:
            profile_file = self.profiles_dir / f"{game_name}.json"
            if not profile_file.exists():
                return None
            
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
            
            # Convert strings back to enums
            profile = GameProfile(
                game_name=profile_data['game_name'],
                executable=profile_data['executable'],
                display_name=profile_data.get('display_name', ''),
                game_path=profile_data.get('game_path', ''),
                fsr_enabled=profile_data.get('fsr_enabled', True),
                fsr_config=profile_data.get('fsr_config'),
                auto_inject=AutoInjectMode(profile_data.get('auto_inject', 'ask')),
                auto_inject_delay=profile_data.get('auto_inject_delay', 5.0),
                optimization_level=OptimizationLevel(profile_data.get('optimization_level', 'balanced')),
                priority_boost=profile_data.get('priority_boost', True),
                disable_overlays=profile_data.get('disable_overlays', False),
                fullscreen_optimization=profile_data.get('fullscreen_optimization', True),
                enable_monitoring=profile_data.get('enable_monitoring', True),
                fps_overlay=profile_data.get('fps_overlay', False),
                performance_logging=profile_data.get('performance_logging', False),
                custom_settings=profile_data.get('custom_settings', {})
            )
            
            self._profiles[game_name] = profile
            return profile
        
        except Exception as e:
            print(f"Error loading profile for {game_name}: {e}")
            return None
    
    def _load_all_profiles(self):
        """Load all profiles from disk"""
        try:
            for profile_file in self.profiles_dir.glob('*.json'):
                game_name = profile_file.stem
                self.load_profile(game_name)
        except Exception as e:
            print(f"Error loading profiles: {e}")
    
    def get_profile(self, game_name: str) -> Optional[GameProfile]:
        """Get profile by game name
        
        Args:
            game_name: Game identifier
        
        Returns:
            Game profile or None
        """
        return self._profiles.get(game_name)
    
    def get_profile_by_executable(self, executable: str) -> Optional[GameProfile]:
        """Get profile by executable name
        
        Args:
            executable: Executable filename (e.g., 'GTA5.exe')
        
        Returns:
            Game profile or None
        """
        for profile in self._profiles.values():
            if profile.executable.lower() == executable.lower():
                return profile
        return None
    
    def list_profiles(self) -> List[GameProfile]:
        """Get list of all profiles
        
        Returns:
            List of game profiles
        """
        return list(self._profiles.values())
    
    def delete_profile(self, game_name: str) -> bool:
        """Delete game profile
        
        Args:
            game_name: Game identifier
        
        Returns:
            True if deleted successfully
        """
        try:
            profile_file = self.profiles_dir / f"{game_name}.json"
            if profile_file.exists():
                profile_file.unlink()
            
            if game_name in self._profiles:
                del self._profiles[game_name]
            
            return True
        
        except Exception as e:
            print(f"Error deleting profile for {game_name}: {e}")
            return False
    
    def should_auto_inject(self, game_name: str) -> bool:
        """Check if auto-injection is enabled for game
        
        Args:
            game_name: Game identifier
        
        Returns:
            True if should auto-inject
        """
        profile = self.get_profile(game_name)
        if not profile:
            return False
        
        return (
            profile.fsr_enabled and
            profile.auto_inject == AutoInjectMode.AUTO
        )
    
    def create_default_profile(self, game_name: str, executable: str) -> GameProfile:
        """Create default profile for game
        
        Args:
            game_name: Game identifier
            executable: Executable filename
        
        Returns:
            New default profile
        """
        profile = self.create_profile(
            game_name=game_name,
            executable=executable,
            fsr_enabled=True,
            auto_inject=AutoInjectMode.ASK,
            optimization_level=OptimizationLevel.BALANCED
        )
        
        # Create default FSR config
        if FSRConfig:
            from core.fsr_manager import get_fsr_manager
            fsr_manager = get_fsr_manager()
            fsr_config = fsr_manager.create_config(
                version=FSRVersion.FSR_3_1,
                preset=FSRPreset.QUALITY,
                frame_generation=True
            )
            profile.fsr_config = asdict(fsr_config)
            # Convert enums
            profile.fsr_config['version'] = fsr_config.version.value
            profile.fsr_config['preset'] = fsr_config.preset.value
        
        self.save_profile(profile)
        return profile
    
    def check_health(self) -> dict:
        """Check profile manager health"""
        profile_count = len(self._profiles)
        
        return {
            'status': 'healthy',
            'message': f'{profile_count} game profile(s) loaded'
        }


# Singleton instance
_profile_manager = None

def get_profile_manager() -> GameProfileManager:
    """Get singleton profile manager instance"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = GameProfileManager()
    return _profile_manager
