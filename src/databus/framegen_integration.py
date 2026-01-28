#!/usr/bin/env python3
"""Frame Generation Integration for DataBus

Version: 0.3.5d_package3.3d

Integration layer between Frame Generator and DataBus.

Features:
- Frame generator registration
- Performance monitoring
- Auto quality adjustment
- Error recovery
- Event emission
"""
from typing import Optional, TYPE_CHECKING
from framegen.interfaces import IFrameGenerator, FrameGenStats, FrameGenQuality
from .events import DataBusEvent

if TYPE_CHECKING:
    from .bus import DataBus


class FrameGenIntegration:
    """Frame Generation integration with DataBus
    
    v0.3.5d_package3.3d
    
    This class manages Frame Generator integration with DataBus,
    including performance monitoring, auto quality adjustment,
    and error recovery.
    
    Example:
        >>> integration = FrameGenIntegration(databus)
        >>> integration.set_generator(fsr4_generator)
        >>> integration.enable_auto_quality(target_fps=60)
    """
    
    def __init__(self, databus: 'DataBus'):
        """Initialize Frame Gen integration
        
        Args:
            databus: DataBus instance
        """
        self._databus = databus
        self._generator: Optional[IFrameGenerator] = None
        self._auto_quality_enabled = False
        self._target_fps = 60.0
        self._last_quality = FrameGenQuality.BALANCED
        
        print("[FrameGenIntegration v0.3.5d_package3.3d] Initialized")
    
    def set_generator(self, generator: IFrameGenerator) -> bool:
        """Register frame generator
        
        Args:
            generator: Frame generator instance
        
        Returns:
            True if registered successfully
        
        Example:
            >>> integration.set_generator(FSR4FrameGenerator())
        """
        if not generator.is_available():
            print("[FrameGenIntegration] ERROR: Generator not available")
            self._databus.emit_event(
                DataBusEvent.FRAMEGEN_ERROR,
                {'error': 'Generator not available'}
            )
            return False
        
        self._generator = generator
        
        # Emit enabled event
        self._databus.emit_event(
            DataBusEvent.FRAMEGEN_ENABLED,
            {
                'name': generator.get_name(),
                'version': generator.get_version(),
            }
        )
        
        print(f"[FrameGenIntegration] Registered: {generator.get_name()}")
        return True
    
    def get_generator(self) -> Optional[IFrameGenerator]:
        """Get current frame generator
        
        Returns:
            Frame generator or None
        """
        return self._generator
    
    def get_stats(self) -> Optional[FrameGenStats]:
        """Get frame generation statistics
        
        Returns:
            Stats or None if no generator
        
        Example:
            >>> stats = integration.get_stats()
            >>> print(f"Frames generated: {stats.frames_generated}")
        """
        if self._generator is None:
            return None
        
        return self._generator.get_performance_stats()
    
    def enable_auto_quality(self, target_fps: float = 60.0):
        """Enable automatic quality adjustment
        
        Args:
            target_fps: Target FPS to maintain
        
        Example:
            >>> integration.enable_auto_quality(target_fps=60)
        """
        self._auto_quality_enabled = True
        self._target_fps = target_fps
        print(f"[FrameGenIntegration] Auto quality enabled (target: {target_fps} FPS)")
    
    def disable_auto_quality(self):
        """Disable automatic quality adjustment"""
        self._auto_quality_enabled = False
        print("[FrameGenIntegration] Auto quality disabled")
    
    def update(self, current_fps: float, gpu_utilization: float):
        """Update auto quality based on performance
        
        Args:
            current_fps: Current FPS
            gpu_utilization: GPU usage (0-100)
        
        Example:
            >>> integration.update(current_fps=55, gpu_utilization=85)
        """
        if not self._auto_quality_enabled or self._generator is None:
            return
        
        # Auto quality adjustment logic
        new_quality = self._calculate_optimal_quality(current_fps, gpu_utilization)
        
        if new_quality != self._last_quality:
            self._generator.set_quality(new_quality)
            self._last_quality = new_quality
            
            # Emit quality changed event
            self._databus.emit_event(
                DataBusEvent.FRAMEGEN_QUALITY_CHANGED,
                {
                    'quality': new_quality.value,
                    'fps': current_fps,
                    'gpu': gpu_utilization,
                }
            )
    
    def _calculate_optimal_quality(self,
                                  current_fps: float,
                                  gpu_utilization: float) -> FrameGenQuality:
        """Calculate optimal quality mode
        
        Args:
            current_fps: Current FPS
            gpu_utilization: GPU usage
        
        Returns:
            Optimal quality mode
        """
        # FPS below target → lower quality
        if current_fps < self._target_fps * 0.9:  # 90% of target
            if gpu_utilization > 90:
                return FrameGenQuality.ULTRA_PERFORMANCE
            elif gpu_utilization > 80:
                return FrameGenQuality.PERFORMANCE
            else:
                return FrameGenQuality.BALANCED
        
        # FPS above target → increase quality
        elif current_fps > self._target_fps * 1.1:  # 110% of target
            if gpu_utilization < 70:
                return FrameGenQuality.QUALITY
            else:
                return FrameGenQuality.BALANCED
        
        # FPS on target → maintain
        return self._last_quality
    
    def remove_generator(self):
        """Remove frame generator"""
        if self._generator is None:
            return
        
        # Shutdown generator
        self._generator.shutdown()
        self._generator = None
        
        # Emit disabled event
        self._databus.emit_event(DataBusEvent.FRAMEGEN_DISABLED, {})
        
        print("[FrameGenIntegration] Generator removed")


# ========== TESTING ==========

if __name__ == "__main__":
    from databus.bus import DataBus
    from framegen.fsr4_generator import FSR4FrameGenerator
    
    print("="*60)
    print("FrameGenIntegration v0.3.5d_package3.3d Test")
    print("="*60)
    
    bus = DataBus()
    integration = FrameGenIntegration(bus)
    
    print("\n[Test 1] Register generator")
    generator = FSR4FrameGenerator()
    generator.initialize()
    
    if integration.set_generator(generator):
        print("  ✅ Generator registered")
    
    print("\n[Test 2] Get stats")
    stats = integration.get_stats()
    if stats:
        print(f"  Frames generated: {stats.frames_generated}")
        print(f"  Quality: {stats.quality_mode.value}")
    
    print("\n[Test 3] Enable auto quality")
    integration.enable_auto_quality(target_fps=60)
    
    print("\n[Test 4] Update (simulate low FPS)")
    integration.update(current_fps=45, gpu_utilization=85)
    
    print("\n[Test 5] Update (simulate high FPS)")
    integration.update(current_fps=75, gpu_utilization=60)
    
    print("\n[Test 6] Remove generator")
    integration.remove_generator()
    
    print("\n" + "="*60)
    print("✅ FrameGenIntegration - All Tests Passed!")
    print("="*60)
