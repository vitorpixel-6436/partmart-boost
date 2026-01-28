"""Game Profiles Package

Provides game detection and optimization.

Version: 0.3.5a
"""

from .game_profiles import GameProfile, GameProfileManager
from .game_detector import GameDetector, DetectedGame
from .optimization_applier import ProfileApplier

__all__ = [
    'GameProfile',
    'GameProfileManager',
    'GameDetector',
    'DetectedGame',
    'ProfileApplier',
]
