#!/usr/bin/env python3
"""DataBus Events

Version: 0.3.5d_package3.3d

Event types for DataBus communication.

Updated:
- Added Frame Generation events
- Added Upscaler events
"""
from enum import Enum, auto


class DataBusEvent(Enum):
    """DataBus event types
    
    Events for communication between components.
    
    Performance Events:
        FPS_UPDATE: FPS changed
        FRAME_TIME_UPDATE: Frame time changed
        PERFORMANCE_WARNING: Performance issue detected
        PERFORMANCE_CRITICAL: Critical performance issue
    
    Frame Generation Events:
        FRAMEGEN_ENABLED: Frame generation enabled
        FRAMEGEN_DISABLED: Frame generation disabled
        FRAMEGEN_QUALITY_CHANGED: FG quality mode changed
        FRAMEGEN_ERROR: Frame generation error
    
    Upscaler Events:
        UPSCALER_ENABLED: Upscaler enabled
        UPSCALER_DISABLED: Upscaler disabled
        UPSCALER_QUALITY_CHANGED: Upscaler quality changed
        UPSCALER_ERROR: Upscaler error
    
    System Events:
        SHUTDOWN: System shutdown
        ERROR: General error
    """
    # Performance events
    FPS_UPDATE = auto()
    FRAME_TIME_UPDATE = auto()
    PERFORMANCE_WARNING = auto()
    PERFORMANCE_CRITICAL = auto()
    
    # Frame Generation events
    FRAMEGEN_ENABLED = auto()
    FRAMEGEN_DISABLED = auto()
    FRAMEGEN_QUALITY_CHANGED = auto()
    FRAMEGEN_ERROR = auto()
    
    # Upscaler events
    UPSCALER_ENABLED = auto()
    UPSCALER_DISABLED = auto()
    UPSCALER_QUALITY_CHANGED = auto()
    UPSCALER_ERROR = auto()
    
    # System events
    SHUTDOWN = auto()
    ERROR = auto()


if __name__ == "__main__":
    print("="*60)
    print("DataBus Events v0.3.5d_package3.3d")
    print("="*60)
    
    print("\nPerformance Events:")
    print(f"  - {DataBusEvent.FPS_UPDATE.name}")
    print(f"  - {DataBusEvent.FRAME_TIME_UPDATE.name}")
    print(f"  - {DataBusEvent.PERFORMANCE_WARNING.name}")
    print(f"  - {DataBusEvent.PERFORMANCE_CRITICAL.name}")
    
    print("\nFrame Generation Events:")
    print(f"  - {DataBusEvent.FRAMEGEN_ENABLED.name}")
    print(f"  - {DataBusEvent.FRAMEGEN_DISABLED.name}")
    print(f"  - {DataBusEvent.FRAMEGEN_QUALITY_CHANGED.name}")
    print(f"  - {DataBusEvent.FRAMEGEN_ERROR.name}")
    
    print("\nUpscaler Events:")
    print(f"  - {DataBusEvent.UPSCALER_ENABLED.name}")
    print(f"  - {DataBusEvent.UPSCALER_DISABLED.name}")
    print(f"  - {DataBusEvent.UPSCALER_QUALITY_CHANGED.name}")
    print(f"  - {DataBusEvent.UPSCALER_ERROR.name}")
    
    print("\nSystem Events:")
    print(f"  - {DataBusEvent.SHUTDOWN.name}")
    print(f"  - {DataBusEvent.ERROR.name}")
    
    print("\n" + "="*60)
    print(f"Total events: {len(DataBusEvent)}")
    print("="*60)
