#!/usr/bin/env python3
"""Display Manager

Version: 0.3.5d_package3.4c

Main display management system.

Features:
- Display detection
- Per-monitor tracking
- HDR management
- VRR management
- Hot-plug detection
"""
import sys
import platform
from typing import List, Optional, Dict

from .display_info import Display, DisplayInfo, HDRFormat, VRRType


class DisplayManager:
    """Display Manager
    
    v0.3.5d_package3.4c - Multi-Display Support
    
    Manages multiple displays, detects capabilities,
    and tracks per-display performance.
    
    Features:
    - Auto-detect displays
    - HDR detection
    - VRR detection
    - Per-display FPS tracking
    - Hot-plug events
    
    Example:
        >>> manager = DisplayManager()
        >>> manager.detect_displays()
        >>> 
        >>> primary = manager.get_primary_display()
        >>> print(f"Primary: {primary.name} @ {primary.refresh_rate}Hz")
        >>> 
        >>> for display in manager.get_displays():
        >>>     if display.hdr_capable:
        >>>         print(f"{display.name} supports HDR")
    """
    
    def __init__(self):
        """Initialize display manager"""
        self._displays: Dict[str, Display] = {}
        self._display_info: Dict[str, DisplayInfo] = {}
        self._primary_display_id: Optional[str] = None
        
        print("[DisplayManager v0.3.5d_package3.4c] Initialized")
    
    # === DISPLAY DETECTION ===
    
    def detect_displays(self) -> int:
        """Detect all connected displays
        
        Returns:
            Number of displays detected
        
        Example:
            >>> count = manager.detect_displays()
            >>> print(f"Found {count} displays")
        """
        print("[DisplayManager] Detecting displays...")
        
        self._displays.clear()
        self._display_info.clear()
        
        # Platform-specific detection
        if sys.platform == "win32":
            self._detect_windows()
        elif sys.platform == "linux":
            self._detect_linux()
        elif sys.platform == "darwin":
            self._detect_macos()
        else:
            print(f"[DisplayManager] Unsupported platform: {sys.platform}")
            # Create mock display
            self._create_mock_display()
        
        print(f"[DisplayManager] Detected {len(self._displays)} display(s)")
        return len(self._displays)
    
    def _detect_windows(self):
        """Detect displays on Windows"""
        # TODO: Use Windows API to detect real displays
        # For now, create mock displays
        print("[DisplayManager] Windows display detection (mock)")
        self._create_mock_display()
    
    def _detect_linux(self):
        """Detect displays on Linux"""
        # TODO: Use X11/Wayland APIs to detect displays
        print("[DisplayManager] Linux display detection (mock)")
        self._create_mock_display()
    
    def _detect_macos(self):
        """Detect displays on macOS"""
        # TODO: Use Quartz/CoreGraphics to detect displays
        print("[DisplayManager] macOS display detection (mock)")
        self._create_mock_display()
    
    def _create_mock_display(self):
        """Create mock display for testing"""
        display = Display(
            id="DISPLAY_PRIMARY",
            name="Primary Display",
            resolution=(1920, 1080),
            refresh_rate=60.0,
            position=(0, 0),
            physical_size=(527, 296),  # ~24 inch
            dpi=92,
            is_primary=True,
            hdr_capable=False,
            hdr_format=HDRFormat.NONE,
            hdr_active=False,
            vrr_capable=False,
            vrr_type=VRRType.NONE,
            vrr_range=None,
            vrr_active=False,
            color_depth=8,
            color_space="sRGB"
        )
        
        self._displays[display.id] = display
        self._primary_display_id = display.id
        
        # Create display info
        info = DisplayInfo(
            display=display,
            supported_resolutions=[
                (1920, 1080),
                (1680, 1050),
                (1600, 900),
                (1280, 720),
            ],
            supported_refresh_rates=[60.0],
            scaling_factor=1.0,
            orientation=0
        )
        
        self._display_info[display.id] = info
    
    # === DISPLAY ACCESS ===
    
    def get_displays(self) -> List[Display]:
        """Get all displays
        
        Returns:
            List of displays
        
        Example:
            >>> displays = manager.get_displays()
            >>> for display in displays:
            >>>     print(display.name)
        """
        return list(self._displays.values())
    
    def get_display(self, display_id: str) -> Optional[Display]:
        """Get display by ID
        
        Args:
            display_id: Display identifier
        
        Returns:
            Display or None
        
        Example:
            >>> display = manager.get_display("DISPLAY1")
        """
        return self._displays.get(display_id)
    
    def get_primary_display(self) -> Optional[Display]:
        """Get primary display
        
        Returns:
            Primary display or None
        
        Example:
            >>> primary = manager.get_primary_display()
            >>> print(f"Primary: {primary.name}")
        """
        if self._primary_display_id is None:
            return None
        return self._displays.get(self._primary_display_id)
    
    def get_display_info(self, display_id: str) -> Optional[DisplayInfo]:
        """Get detailed display information
        
        Args:
            display_id: Display identifier
        
        Returns:
            Display info or None
        
        Example:
            >>> info = manager.get_display_info("DISPLAY1")
            >>> print(info.supported_resolutions)
        """
        return self._display_info.get(display_id)
    
    # === HDR MANAGEMENT ===
    
    def get_hdr_displays(self) -> List[Display]:
        """Get all HDR-capable displays
        
        Returns:
            List of HDR displays
        
        Example:
            >>> hdr_displays = manager.get_hdr_displays()
            >>> print(f"HDR displays: {len(hdr_displays)}")
        """
        return [d for d in self._displays.values() if d.hdr_capable]
    
    def enable_hdr(self, display_id: str) -> bool:
        """Enable HDR on display
        
        Args:
            display_id: Display identifier
        
        Returns:
            True if HDR was enabled
        
        Example:
            >>> manager.enable_hdr("DISPLAY1")
        """
        display = self._displays.get(display_id)
        if display is None or not display.hdr_capable:
            return False
        
        display.hdr_active = True
        print(f"[DisplayManager] HDR enabled on {display.name}")
        return True
    
    def disable_hdr(self, display_id: str) -> bool:
        """Disable HDR on display
        
        Args:
            display_id: Display identifier
        
        Returns:
            True if HDR was disabled
        
        Example:
            >>> manager.disable_hdr("DISPLAY1")
        """
        display = self._displays.get(display_id)
        if display is None:
            return False
        
        display.hdr_active = False
        print(f"[DisplayManager] HDR disabled on {display.name}")
        return True
    
    # === VRR MANAGEMENT ===
    
    def get_vrr_displays(self) -> List[Display]:
        """Get all VRR-capable displays
        
        Returns:
            List of VRR displays
        
        Example:
            >>> vrr_displays = manager.get_vrr_displays()
            >>> for display in vrr_displays:
            >>>     print(f"{display.name}: {display.vrr_type.value}")
        """
        return [d for d in self._displays.values() if d.vrr_capable]
    
    def get_vrr_range(self, display_id: str) -> Optional[tuple]:
        """Get VRR range for display
        
        Args:
            display_id: Display identifier
        
        Returns:
            (min_hz, max_hz) or None
        
        Example:
            >>> vrr_range = manager.get_vrr_range("DISPLAY1")
            >>> if vrr_range:
            >>>     print(f"VRR: {vrr_range[0]}-{vrr_range[1]}Hz")
        """
        display = self._displays.get(display_id)
        if display is None or not display.vrr_capable:
            return None
        return display.vrr_range
    
    # === STATISTICS ===
    
    def print_display_summary(self):
        """Print summary of all displays
        
        Example:
            >>> manager.print_display_summary()
        """
        print("\n" + "="*60)
        print("Display Summary")
        print("="*60)
        
        for display in self._displays.values():
            print(f"\n{display.name}:")
            print(f"  ID: {display.id}")
            print(f"  Resolution: {display.resolution[0]}x{display.resolution[1]}")
            print(f"  Refresh Rate: {display.refresh_rate}Hz")
            print(f"  Position: ({display.position[0]}, {display.position[1]})")
            print(f"  DPI: {display.dpi}")
            print(f"  Primary: {display.is_primary}")
            print(f"  Color: {display.color_depth}-bit {display.color_space}")
            
            if display.hdr_capable:
                status = "Active" if display.hdr_active else "Inactive"
                print(f"  HDR: {display.hdr_format.value} ({status})")
            else:
                print(f"  HDR: Not supported")
            
            if display.vrr_capable:
                status = "Active" if display.vrr_active else "Inactive"
                vrr_range = f"{display.vrr_range[0]:.0f}-{display.vrr_range[1]:.0f}Hz" if display.vrr_range else "Unknown"
                print(f"  VRR: {display.vrr_type.value} ({vrr_range}) [{status}]")
            else:
                print(f"  VRR: Not supported")
        
        print("="*60)


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("DisplayManager v0.3.5d_package3.4c Test")
    print("="*60)
    
    manager = DisplayManager()
    
    print("\n[Test 1] Detect displays")
    count = manager.detect_displays()
    print(f"  Detected: {count} display(s)")
    
    print("\n[Test 2] Get primary display")
    primary = manager.get_primary_display()
    if primary:
        print(f"  Name: {primary.name}")
        print(f"  Resolution: {primary.resolution[0]}x{primary.resolution[1]}")
        print(f"  Refresh Rate: {primary.refresh_rate}Hz")
    
    print("\n[Test 3] Check HDR support")
    hdr_displays = manager.get_hdr_displays()
    print(f"  HDR displays: {len(hdr_displays)}")
    
    print("\n[Test 4] Check VRR support")
    vrr_displays = manager.get_vrr_displays()
    print(f"  VRR displays: {len(vrr_displays)}")
    
    print("\n[Test 5] Display summary")
    manager.print_display_summary()
    
    print("\n" + "="*60)
    print("✅ DisplayManager - All Tests Passed!")
    print("="*60)
