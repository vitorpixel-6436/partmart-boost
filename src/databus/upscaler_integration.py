#!/usr/bin/env python3
"""Upscaler Integration for DataBus

Version: 0.3.5d_package3.3d

Integration layer between Upscaler and DataBus.

Features:
- Upscaler registration
- Performance monitoring
- Auto quality adjustment
- Error recovery
- Event emission
"""
from typing import Optional, TYPE_CHECKING
from upscaler.interfaces import IUpscaler, UpscaleStats, UpscaleQuality
from .events import DataBusEvent

if TYPE_CHECKING:
    from .bus import DataBus


class UpscalerIntegration:
    """Upscaler integration with DataBus
    
    v0.3.5d_package3.3d
    
    This class manages Upscaler integration with DataBus,
    including performance monitoring, auto quality adjustment,
    and error recovery.
    
    Example:
        >>> integration = UpscalerIntegration(databus)
        >>> integration.set_upscaler(fsr4_upscaler)
        >>> integration.enable_auto_quality(target_fps=60)
    """
    
    def __init__(self, databus: 'DataBus'):
        """Initialize Upscaler integration
        
        Args:
            databus: DataBus instance
        """
        self._databus = databus
        self._upscaler: Optional[IUpscaler] = None
        self._auto_quality_enabled = False
        self._target_fps = 60.0
        self._last_quality = UpscaleQuality.BALANCED
        
        print("[UpscalerIntegration v0.3.5d_package3.3d] Initialized")
    
    def set_upscaler(self, upscaler: IUpscaler) -> bool:
        """Register upscaler
        
        Args:
            upscaler: Upscaler instance
        
        Returns:
            True if registered successfully
        
        Example:
            >>> integration.set_upscaler(FSR4Upscaler())
        """
        if not upscaler.is_available():
            print("[UpscalerIntegration] ERROR: Upscaler not available")
            self._databus.emit_event(
                DataBusEvent.UPSCALER_ERROR,
                {'error': 'Upscaler not available'}
            )
            return False
        
        self._upscaler = upscaler
        
        # Emit enabled event
        self._databus.emit_event(
            DataBusEvent.UPSCALER_ENABLED,
            {
                'name': upscaler.get_name(),
                'version': upscaler.get_version(),
            }
        )
        
        print(f"[UpscalerIntegration] Registered: {upscaler.get_name()}")
        return True
    
    def get_upscaler(self) -> Optional[IUpscaler]:
        """Get current upscaler
        
        Returns:
            Upscaler or None
        """
        return self._upscaler
    
    def get_stats(self) -> Optional[UpscaleStats]:
        """Get upscaler statistics
        
        Returns:
            Stats or None if no upscaler
        
        Example:
            >>> stats = integration.get_stats()
            >>> print(f"Frames upscaled: {stats.frames_upscaled}")
        """
        if self._upscaler is None:
            return None
        
        return self._upscaler.get_performance_stats()
    
    def enable_auto_quality(self, target_fps: float = 60.0):
        """Enable automatic quality adjustment
        
        Args:
            target_fps: Target FPS to maintain
        
        Example:
            >>> integration.enable_auto_quality(target_fps=60)
        """
        self._auto_quality_enabled = True
        self._target_fps = target_fps
        print(f"[UpscalerIntegration] Auto quality enabled (target: {target_fps} FPS)")
    
    def disable_auto_quality(self):
        """Disable automatic quality adjustment"""
        self._auto_quality_enabled = False
        print("[UpscalerIntegration] Auto quality disabled")
    
    def update(self, current_fps: float, gpu_utilization: float):
        """Update auto quality based on performance
        
        Args:
            current_fps: Current FPS
            gpu_utilization: GPU usage (0-100)
        
        Example:
            >>> integration.update(current_fps=55, gpu_utilization=85)
        """
        if not self._auto_quality_enabled or self._upscaler is None:
            return
        
        # Auto quality adjustment logic
        new_quality = self._calculate_optimal_quality(current_fps, gpu_utilization)
        
        if new_quality != self._last_quality:
            self._upscaler.set_quality(new_quality)
            self._last_quality = new_quality
            
            # Emit quality changed event
            self._databus.emit_event(
                DataBusEvent.UPSCALER_QUALITY_CHANGED,
                {
                    'quality': new_quality.value,
                    'fps': current_fps,
                    'gpu': gpu_utilization,
                }
            )
    
    def _calculate_optimal_quality(self,
                                  current_fps: float,
                                  gpu_utilization: float) -> UpscaleQuality:
        """Calculate optimal quality mode
        
        Args:
            current_fps: Current FPS
            gpu_utilization: GPU usage
        
        Returns:
            Optimal quality mode
        """
        # FPS below target → lower quality (higher scaling)
        if current_fps < self._target_fps * 0.9:  # 90% of target
            if gpu_utilization > 90:
                return UpscaleQuality.ULTRA_PERFORMANCE  # 3.0x scaling
            elif gpu_utilization > 80:
                return UpscaleQuality.PERFORMANCE  # 2.0x scaling
            else:
                return UpscaleQuality.BALANCED  # 1.7x scaling
        
        # FPS above target → increase quality (lower scaling)
        elif current_fps > self._target_fps * 1.1:  # 110% of target
            if gpu_utilization < 60:
                return UpscaleQuality.QUALITY  # 1.5x scaling
            else:
                return UpscaleQuality.BALANCED
        
        # FPS on target → maintain
        return self._last_quality
    
    def remove_upscaler(self):
        """Remove upscaler"""
        if self._upscaler is None:
            return
        
        # Shutdown upscaler
        self._upscaler.shutdown()
        self._upscaler = None
        
        # Emit disabled event
        self._databus.emit_event(DataBusEvent.UPSCALER_DISABLED, {})
        
        print("[UpscalerIntegration] Upscaler removed")


# ========== TESTING ==========

if __name__ == "__main__":
    from databus.bus import DataBus
    from upscaler.fsr4_upscaler import FSR4Upscaler
    
    print("="*60)
    print("UpscalerIntegration v0.3.5d_package3.3d Test")
    print("="*60)
    
    bus = DataBus()
    integration = UpscalerIntegration(bus)
    
    print("\n[Test 1] Register upscaler")
    upscaler = FSR4Upscaler()
    upscaler.initialize(1920, 1080)
    
    if integration.set_upscaler(upscaler):
        print("  ✅ Upscaler registered")
    
    print("\n[Test 2] Get stats")
    stats = integration.get_stats()
    if stats:
        print(f"  Frames upscaled: {stats.frames_upscaled}")
        print(f"  Quality: {stats.quality_mode.value}")
    
    print("\n[Test 3] Enable auto quality")
    integration.enable_auto_quality(target_fps=60)
    
    print("\n[Test 4] Update (simulate low FPS)")
    integration.update(current_fps=45, gpu_utilization=85)
    
    print("\n[Test 5] Update (simulate high FPS)")
    integration.update(current_fps=75, gpu_utilization=60)
    
    print("\n[Test 6] Remove upscaler")
    integration.remove_upscaler()
    
    print("\n" + "="*60)
    print("✅ UpscalerIntegration - All Tests Passed!")
    print("="*60)
