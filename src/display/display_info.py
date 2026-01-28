#!/usr/bin/env python3
"""Display Information Structures

Version: 0.3.5d_package3.4c

Data structures for display information.

Structures:
- Display: Display properties
- DisplayInfo: Detailed display information
- HDRFormat: HDR format enum
- VRRType: VRR technology enum
"""
from dataclasses import dataclass
from typing import Tuple, List, Optional
from enum import Enum


class HDRFormat(Enum):
    """HDR format types
    
    Attributes:
        NONE: No HDR support
        HDR10: HDR10 standard
        HDR10_PLUS: HDR10+ with dynamic metadata
        DOLBY_VISION: Dolby Vision
    """
    NONE = "none"
    HDR10 = "hdr10"
    HDR10_PLUS = "hdr10_plus"
    DOLBY_VISION = "dolby_vision"


class VRRType(Enum):
    """VRR technology types
    
    Attributes:
        NONE: No VRR support
        GSYNC: NVIDIA G-Sync
        FREESYNC: AMD FreeSync
        HDMI_VRR: HDMI Variable Refresh Rate
        VESA_ADAPTIVE_SYNC: VESA Adaptive-Sync
    """
    NONE = "none"
    GSYNC = "g-sync"
    FREESYNC = "freesync"
    HDMI_VRR = "hdmi_vrr"
    VESA_ADAPTIVE_SYNC = "adaptive_sync"


@dataclass
class Display:
    """Display properties
    
    Attributes:
        id: Display identifier
        name: Display name/model
        resolution: Resolution (width, height)
        refresh_rate: Refresh rate (Hz)
        position: Desktop position (x, y)
        physical_size: Physical size in mm (width, height)
        dpi: Dots per inch
        is_primary: Is primary display
        hdr_capable: HDR support
        hdr_format: HDR format if supported
        hdr_active: HDR currently active
        vrr_capable: VRR support
        vrr_type: VRR technology type
        vrr_range: VRR range (min_hz, max_hz)
        vrr_active: VRR currently active
        color_depth: Bit depth (8, 10, 12)
        color_space: Color space (e.g., 'sRGB', 'DCI-P3')
    """
    id: str
    name: str
    resolution: Tuple[int, int]
    refresh_rate: float
    position: Tuple[int, int]
    physical_size: Tuple[int, int]
    dpi: int
    is_primary: bool
    hdr_capable: bool
    hdr_format: HDRFormat
    hdr_active: bool
    vrr_capable: bool
    vrr_type: VRRType
    vrr_range: Optional[Tuple[float, float]]
    vrr_active: bool
    color_depth: int
    color_space: str


@dataclass
class DisplayInfo:
    """Detailed display information
    
    Attributes:
        display: Display properties
        supported_resolutions: List of supported resolutions
        supported_refresh_rates: List of supported refresh rates
        scaling_factor: DPI scaling factor
        orientation: Display orientation (0, 90, 180, 270)
    """
    display: Display
    supported_resolutions: List[Tuple[int, int]]
    supported_refresh_rates: List[float]
    scaling_factor: float
    orientation: int


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("DisplayInfo v0.3.5d_package3.4c Test")
    print("="*60)
    
    print("\n[Test 1] Create display")
    display = Display(
        id="DISPLAY1",
        name="Samsung Odyssey G9",
        resolution=(5120, 1440),
        refresh_rate=240.0,
        position=(0, 0),
        physical_size=(1193, 336),
        dpi=109,
        is_primary=True,
        hdr_capable=True,
        hdr_format=HDRFormat.HDR10,
        hdr_active=False,
        vrr_capable=True,
        vrr_type=VRRType.GSYNC,
        vrr_range=(48.0, 240.0),
        vrr_active=True,
        color_depth=10,
        color_space="DCI-P3"
    )
    
    print(f"  Name: {display.name}")
    print(f"  Resolution: {display.resolution[0]}x{display.resolution[1]}")
    print(f"  Refresh Rate: {display.refresh_rate}Hz")
    print(f"  HDR: {display.hdr_capable} ({display.hdr_format.value})")
    print(f"  VRR: {display.vrr_capable} ({display.vrr_type.value})")
    if display.vrr_range:
        print(f"  VRR Range: {display.vrr_range[0]}-{display.vrr_range[1]}Hz")
    
    print("\n[Test 2] Display info")
    info = DisplayInfo(
        display=display,
        supported_resolutions=[
            (5120, 1440),
            (3840, 1080),
            (2560, 1440),
        ],
        supported_refresh_rates=[60.0, 120.0, 144.0, 240.0],
        scaling_factor=1.0,
        orientation=0
    )
    
    print(f"  Supported resolutions: {len(info.supported_resolutions)}")
    print(f"  Supported refresh rates: {len(info.supported_refresh_rates)}")
    
    print("\n" + "="*60)
    print("✅ DisplayInfo - All Tests Passed!")
    print("="*60)
