"""Game Profile Management

Version: 0.3.5b_hotfix
Fixed: Better validation
Fixed: Proper reload handling
"""
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GameProfile:
    """Game optimization profile"""
    game_name: str
    enabled: bool
    executable_names: List[str]
    priority: str = "high"
    affinity: str = "auto"
    
    # GPU settings
    gpu_enabled: bool = True
    gpu_power_limit: int = 100
    gpu_temp_limit: int = 85
    gpu_fan_curve: str = "aggressive"
    
    # RAM settings
    ram_enabled: bool = True
    ram_cleanup: bool = True
    ram_reserved_mb: int = 2048
    
    # Windows settings
    windows_game_mode: bool = True
    windows_fso: bool = False
    windows_hags: bool = True
    windows_game_bar: bool = False
    
    @staticmethod
    def from_dict(data: Dict) -> 'GameProfile':
        """Create profile from dict with validation
        
        Fixed: Better validation
        """
        gpu = data.get('gpu', {})
        ram = data.get('ram', {})
        windows = data.get('windows', {})
        
        # Validate executable_names
        exe_names = data.get('executable_names', [])
        if not exe_names or not isinstance(exe_names, list):
            raise ValueError(f"Invalid executable_names in profile {data.get('game_name')}")
        
        # Filter out empty strings
        exe_names = [name.strip() for name in exe_names if name and name.strip()]
        if not exe_names:
            raise ValueError(f"No valid executables in profile {data.get('game_name')}")
        
        return GameProfile(
            game_name=data.get('game_name', 'Unknown'),
            enabled=data.get('enabled', False),
            executable_names=exe_names,
            priority=data.get('priority', 'high'),
            affinity=data.get('affinity', 'auto'),
            
            gpu_enabled=gpu.get('enabled', True),
            gpu_power_limit=gpu.get('power_limit', 100),
            gpu_temp_limit=gpu.get('temp_limit', 85),
            gpu_fan_curve=gpu.get('fan_curve', 'aggressive'),
            
            ram_enabled=ram.get('enabled', True),
            ram_cleanup=ram.get('cleanup_before_launch', True),
            ram_reserved_mb=ram.get('reserved_mb', 2048),
            
            windows_game_mode=windows.get('game_mode', True),
            windows_fso=windows.get('fullscreen_optimizations', False),
            windows_hags=windows.get('hags', True),
            windows_game_bar=windows.get('game_bar', False),
        )
    
    def to_dict(self) -> Dict:
        """Convert to dict"""
        return {
            'game_name': self.game_name,
            'enabled': self.enabled,
            'executable_names': self.executable_names,
            'priority': self.priority,
            'affinity': self.affinity,
            'gpu': {
                'enabled': self.gpu_enabled,
                'power_limit': self.gpu_power_limit,
                'temp_limit': self.gpu_temp_limit,
                'fan_curve': self.gpu_fan_curve,
            },
            'ram': {
                'enabled': self.ram_enabled,
                'cleanup_before_launch': self.ram_cleanup,
                'reserved_mb': self.ram_reserved_mb,
            },
            'windows': {
                'game_mode': self.windows_game_mode,
                'fullscreen_optimizations': self.windows_fso,
                'hags': self.windows_hags,
                'game_bar': self.windows_game_bar,
            },
        }


class GameProfileManager:
    """Manage game profiles
    
    Version: 0.3.5b_hotfix
    Fixed: Proper reload handling
    """
    
    def __init__(self, profiles_dir: str = "config/profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles: Dict[str, GameProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load all profiles from directory
        
        Fixed: Better error handling
        """
        if not self.profiles_dir.exists():
            print(f"[WARN] Profiles directory not found: {self.profiles_dir}")
            self.profiles_dir.mkdir(parents=True, exist_ok=True)
            return
        
        loaded_count = 0
        error_count = 0
        
        for file in self.profiles_dir.glob("*.json"):
            if file.name == "example_game.json":
                continue
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profile = GameProfile.from_dict(data)
                    
                    if profile.enabled:
                        self.profiles[profile.game_name] = profile
                        loaded_count += 1
                        print(f"[OK] Loaded profile: {profile.game_name}")
                    else:
                        print(f"[INFO] Skipped disabled profile: {profile.game_name}")
            
            except ValueError as e:
                print(f"[ERROR] Invalid profile {file.name}: {e}")
                error_count += 1
            except json.JSONDecodeError as e:
                print(f"[ERROR] Invalid JSON in {file.name}: {e}")
                error_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to load {file.name}: {e}")
                error_count += 1
        
        print(f"[INFO] Loaded {loaded_count} profiles ({error_count} errors)")
    
    def get_profile_by_exe(self, exe_name: str) -> Optional[GameProfile]:
        """Find profile by executable name
        
        Fixed: Case-insensitive matching
        """
        if not exe_name:
            return None
        
        exe_lower = exe_name.lower()
        
        for profile in self.profiles.values():
            for exe in profile.executable_names:
                if exe and exe.lower() == exe_lower:
                    return profile
        
        return None
    
    def get_all_profiles(self) -> List[GameProfile]:
        """Get all loaded profiles"""
        return list(self.profiles.values())
    
    def reload(self):
        """Reload all profiles
        
        Fixed: Properly clears and reloads
        """
        print("[INFO] Reloading profiles...")
        self.profiles.clear()
        self._load_profiles()
        print(f"[OK] Reload complete: {len(self.profiles)} profiles loaded")
