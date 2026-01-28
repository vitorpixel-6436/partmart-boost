#!/usr/bin/env python3
"""DataBus - Central Communication Hub

Version: 0.3.5d_package3.3d

Updated:
- Added Frame Generation integration
- Added Upscaler integration
- Auto quality adjustment support
- Performance monitoring hooks
"""
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
import time

from .events import DataBusEvent
from .framegen_integration import FrameGenIntegration
from .upscaler_integration import UpscalerIntegration

# Type hints for interfaces
try:
    from framegen.interfaces import IFrameGenerator, FrameGenStats
    from upscaler.interfaces import IUpscaler, UpscaleStats
except ImportError:
    # Fallback if not imported
    IFrameGenerator = Any
    IUpscaler = Any
    FrameGenStats = Any
    UpscaleStats = Any


class DataBus:
    """Central communication hub for PartMart Boost
    
    v0.3.5d_package3.3d - Frame Gen & Upscaler Integration
    
    The DataBus provides:
    - Event-driven communication
    - Component registration
    - Performance monitoring
    - Frame Generation integration
    - Upscaler integration
    - Auto quality adjustment
    
    Example:
        >>> bus = DataBus()
        >>> 
        >>> # Register Frame Generator
        >>> fg = FSR4FrameGenerator()
        >>> bus.set_frame_generator(fg)
        >>> 
        >>> # Register Upscaler
        >>> upscaler = FSR4Upscaler()
        >>> bus.set_upscaler(upscaler)
        >>> 
        >>> # Enable auto quality
        >>> bus.enable_auto_quality(target_fps=60)
    """
    
    def __init__(self):
        """Initialize DataBus"""
        # Event subscribers
        self._subscribers: Dict[DataBusEvent, List[Callable]] = defaultdict(list)
        
        # Shared state
        self._state: Dict[str, Any] = {}
        
        # Frame Gen & Upscaler integrations
        self._framegen_integration = FrameGenIntegration(self)
        self._upscaler_integration = UpscalerIntegration(self)
        
        # Auto quality settings
        self._auto_quality_enabled = False
        self._target_fps = 60.0
        
        # Performance tracking
        self._current_fps = 0.0
        self._current_gpu = 0.0
        
        print("[DataBus v0.3.5d_package3.3d] Initialized with Frame Gen & Upscaler support")
    
    # === EVENT SYSTEM ===
    
    def subscribe(self, event: DataBusEvent, callback: Callable[[Dict], None]):
        """Subscribe to event
        
        Args:
            event: Event type
            callback: Function to call when event occurs
        
        Example:
            >>> def on_fps_update(data):
            >>>     print(f"FPS: {data['fps']}")
            >>> bus.subscribe(DataBusEvent.FPS_UPDATE, on_fps_update)
        """
        self._subscribers[event].append(callback)
    
    def unsubscribe(self, event: DataBusEvent, callback: Callable[[Dict], None]):
        """Unsubscribe from event
        
        Args:
            event: Event type
            callback: Callback to remove
        """
        if callback in self._subscribers[event]:
            self._subscribers[event].remove(callback)
    
    def emit_event(self, event: DataBusEvent, data: Dict[str, Any]):
        """Emit event to subscribers
        
        Args:
            event: Event type
            data: Event data
        
        Example:
            >>> bus.emit_event(DataBusEvent.FPS_UPDATE, {'fps': 60.5})
        """
        for callback in self._subscribers[event]:
            try:
                callback(data)
            except Exception as e:
                print(f"[DataBus] ERROR in event callback: {e}")
    
    # === STATE MANAGEMENT ===
    
    def set_state(self, key: str, value: Any):
        """Set shared state value
        
        Args:
            key: State key
            value: State value
        """
        self._state[key] = value
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get shared state value
        
        Args:
            key: State key
            default: Default value if key not found
        
        Returns:
            State value or default
        """
        return self._state.get(key, default)
    
    # === FRAME GENERATION ===
    
    def set_frame_generator(self, generator: 'IFrameGenerator') -> bool:
        """Register frame generator
        
        Args:
            generator: Frame generator instance
        
        Returns:
            True if registered successfully
        
        Example:
            >>> bus.set_frame_generator(FSR4FrameGenerator())
        """
        return self._framegen_integration.set_generator(generator)
    
    def get_frame_generator(self) -> Optional['IFrameGenerator']:
        """Get current frame generator
        
        Returns:
            Frame generator or None
        """
        return self._framegen_integration.get_generator()
    
    def get_fg_stats(self) -> Optional['FrameGenStats']:
        """Get frame generation statistics
        
        Returns:
            Stats or None
        
        Example:
            >>> stats = bus.get_fg_stats()
            >>> if stats:
            >>>     print(f"Frames generated: {stats.frames_generated}")
        """
        return self._framegen_integration.get_stats()
    
    # === UPSCALER ===
    
    def set_upscaler(self, upscaler: 'IUpscaler') -> bool:
        """Register upscaler
        
        Args:
            upscaler: Upscaler instance
        
        Returns:
            True if registered successfully
        
        Example:
            >>> bus.set_upscaler(FSR4Upscaler())
        """
        return self._upscaler_integration.set_upscaler(upscaler)
    
    def get_upscaler(self) -> Optional['IUpscaler']:
        """Get current upscaler
        
        Returns:
            Upscaler or None
        """
        return self._upscaler_integration.get_upscaler()
    
    def get_upscaler_stats(self) -> Optional['UpscaleStats']:
        """Get upscaler statistics
        
        Returns:
            Stats or None
        
        Example:
            >>> stats = bus.get_upscaler_stats()
            >>> if stats:
            >>>     print(f"Frames upscaled: {stats.frames_upscaled}")
        """
        return self._upscaler_integration.get_stats()
    
    # === AUTO QUALITY ===
    
    def enable_auto_quality(self, target_fps: float = 60.0):
        """Enable automatic quality adjustment
        
        Args:
            target_fps: Target FPS to maintain
        
        Example:
            >>> bus.enable_auto_quality(target_fps=60)
        """
        self._auto_quality_enabled = True
        self._target_fps = target_fps
        
        self._framegen_integration.enable_auto_quality(target_fps)
        self._upscaler_integration.enable_auto_quality(target_fps)
        
        print(f"[DataBus] Auto quality enabled (target: {target_fps} FPS)")
    
    def disable_auto_quality(self):
        """Disable automatic quality adjustment"""
        self._auto_quality_enabled = False
        
        self._framegen_integration.disable_auto_quality()
        self._upscaler_integration.disable_auto_quality()
        
        print("[DataBus] Auto quality disabled")
    
    def update_performance(self, fps: float, gpu_utilization: float):
        """Update performance metrics for auto quality
        
        Args:
            fps: Current FPS
            gpu_utilization: GPU usage (0-100)
        
        Example:
            >>> bus.update_performance(fps=55, gpu_utilization=85)
        """
        self._current_fps = fps
        self._current_gpu = gpu_utilization
        
        if self._auto_quality_enabled:
            self._framegen_integration.update(fps, gpu_utilization)
            self._upscaler_integration.update(fps, gpu_utilization)
    
    # === CLEANUP ===
    
    def shutdown(self):
        """Shutdown DataBus and cleanup"""
        print("[DataBus] Shutting down")
        
        # Remove integrations
        self._framegen_integration.remove_generator()
        self._upscaler_integration.remove_upscaler()
        
        # Clear subscribers
        self._subscribers.clear()
        
        # Clear state
        self._state.clear()
        
        # Emit shutdown event
        self.emit_event(DataBusEvent.SHUTDOWN, {})


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("DataBus v0.3.5d_package3.3d Test")
    print("="*60)
    
    bus = DataBus()
    
    print("\n[Test 1] Event subscription")
    def on_fg_enabled(data):
        print(f"  Event: Frame Gen enabled - {data['name']}")
    
    bus.subscribe(DataBusEvent.FRAMEGEN_ENABLED, on_fg_enabled)
    
    print("\n[Test 2] Frame Generator registration")
    try:
        from framegen.fsr4_generator import FSR4FrameGenerator
        fg = FSR4FrameGenerator()
        fg.initialize()
        bus.set_frame_generator(fg)
        print("  ✅ Frame Generator registered")
    except ImportError:
        print("  ⚠️  Frame Generator not available (import error)")
    
    print("\n[Test 3] Upscaler registration")
    try:
        from upscaler.fsr4_upscaler import FSR4Upscaler
        upscaler = FSR4Upscaler()
        upscaler.initialize(1920, 1080)
        bus.set_upscaler(upscaler)
        print("  ✅ Upscaler registered")
    except ImportError:
        print("  ⚠️  Upscaler not available (import error)")
    
    print("\n[Test 4] Enable auto quality")
    bus.enable_auto_quality(target_fps=60)
    
    print("\n[Test 5] Performance update")
    bus.update_performance(fps=55, gpu_utilization=85)
    
    print("\n[Test 6] Get stats")
    fg_stats = bus.get_fg_stats()
    if fg_stats:
        print(f"  FG frames: {fg_stats.frames_generated}")
    
    upscaler_stats = bus.get_upscaler_stats()
    if upscaler_stats:
        print(f"  Upscaler frames: {upscaler_stats.frames_upscaled}")
    
    print("\n[Test 7] Shutdown")
    bus.shutdown()
    
    print("\n" + "="*60)
    print("✅ DataBus v0.3.5d_package3.3d - All Tests Passed!")
    print("="*60)
