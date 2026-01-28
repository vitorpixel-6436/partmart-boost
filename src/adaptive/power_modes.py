#!/usr/bin/env python3
"""Power Modes and Profiles

Version: 0.3.5d_package3.4a

Power mode definitions for adaptive performance system.

Modes:
- Maximum Performance: No limits, highest quality
- Balanced: Optimal quality/performance ratio
- Power Saver: Minimize power consumption
- Custom: User-defined targets
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class PowerMode(Enum):
    """Power mode presets
    
    Attributes:
        MAX_PERFORMANCE: Maximum performance, no limits
        BALANCED: Balanced quality and power
        POWER_SAVER: Minimize power consumption
        CUSTOM: Custom user-defined mode
    """
    MAX_PERFORMANCE = "max_performance"
    BALANCED = "balanced"
    POWER_SAVER = "power_saver"
    CUSTOM = "custom"


@dataclass
class PowerProfile:
    """Power profile configuration
    
    Attributes:
        target_fps: Target FPS to maintain
        fps_tolerance: FPS tolerance (0.0-1.0, e.g., 0.1 = ±10%)
        max_gpu_utilization: Max GPU usage (0-100)
        max_cpu_utilization: Max CPU usage (0-100)
        max_temperature: Max temperature threshold (°C)
        max_power_draw: Max power draw (watts)
        quality_floor: Minimum quality level (0-4)
        quality_ceiling: Maximum quality level (0-4)
        adjustment_speed: Quality change speed (0.0-1.0)
    """
    target_fps: float
    fps_tolerance: float
    max_gpu_utilization: float
    max_cpu_utilization: float
    max_temperature: float
    max_power_draw: Optional[float]
    quality_floor: int
    quality_ceiling: int
    adjustment_speed: float


# Preset profiles
PROFILES = {
    PowerMode.MAX_PERFORMANCE: PowerProfile(
        target_fps=144.0,
        fps_tolerance=0.05,  # ±5%
        max_gpu_utilization=100.0,
        max_cpu_utilization=100.0,
        max_temperature=90.0,
        max_power_draw=None,  # No limit
        quality_floor=0,  # Ultra Performance allowed
        quality_ceiling=4,  # Ultra quality allowed
        adjustment_speed=1.0,  # Fast adjustments
    ),
    PowerMode.BALANCED: PowerProfile(
        target_fps=60.0,
        fps_tolerance=0.1,  # ±10%
        max_gpu_utilization=85.0,
        max_cpu_utilization=80.0,
        max_temperature=80.0,
        max_power_draw=150.0,
        quality_floor=1,  # Performance minimum
        quality_ceiling=3,  # Quality maximum
        adjustment_speed=0.5,  # Moderate adjustments
    ),
    PowerMode.POWER_SAVER: PowerProfile(
        target_fps=30.0,
        fps_tolerance=0.15,  # ±15%
        max_gpu_utilization=70.0,
        max_cpu_utilization=60.0,
        max_temperature=70.0,
        max_power_draw=75.0,
        quality_floor=0,  # Ultra Performance preferred
        quality_ceiling=2,  # Balanced maximum
        adjustment_speed=0.3,  # Slow adjustments
    ),
}


def get_profile(mode: PowerMode) -> PowerProfile:
    """Get power profile for mode
    
    Args:
        mode: Power mode
    
    Returns:
        Power profile
    
    Example:
        >>> profile = get_profile(PowerMode.BALANCED)
        >>> print(f"Target FPS: {profile.target_fps}")
    """
    return PROFILES.get(mode, PROFILES[PowerMode.BALANCED])


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("Power Modes v0.3.5d_package3.4a Test")
    print("="*60)
    
    print("\nPower Profiles:")
    for mode in PowerMode:
        if mode == PowerMode.CUSTOM:
            continue
        
        profile = get_profile(mode)
        print(f"\n{mode.value.upper()}:")
        print(f"  Target FPS: {profile.target_fps}")
        print(f"  FPS Tolerance: ±{profile.fps_tolerance*100:.0f}%")
        print(f"  Max GPU: {profile.max_gpu_utilization:.0f}%")
        print(f"  Max Temp: {profile.max_temperature:.0f}°C")
        print(f"  Quality Range: {profile.quality_floor}-{profile.quality_ceiling}")
    
    print("\n" + "="*60)
    print("✅ Power Modes - Test Complete!")
    print("="*60)
