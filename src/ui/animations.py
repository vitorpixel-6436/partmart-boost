"""Animation Utilities

Version: 0.3.5c
Features:
- Common animation presets
- Easing curves
- Animation chains
"""
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
from typing import List, Optional


class AnimationPresets:
    """Common animation presets"""
    
    @staticmethod
    def fade_in(widget, duration: int = 300) -> QPropertyAnimation:
        """Fade in animation"""
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        return anim
    
    @staticmethod
    def fade_out(widget, duration: int = 300) -> QPropertyAnimation:
        """Fade out animation"""
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        return anim
    
    @staticmethod
    def slide_in(widget, direction: str = "left", duration: int = 400) -> QPropertyAnimation:
        """Slide in animation
        
        Args:
            direction: left, right, top, bottom
        """
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start position depends on direction
        current_pos = widget.pos()
        
        if direction == "left":
            start_pos = current_pos - QPoint(widget.width(), 0)
        elif direction == "right":
            start_pos = current_pos + QPoint(widget.width(), 0)
        elif direction == "top":
            start_pos = current_pos - QPoint(0, widget.height())
        else:  # bottom
            start_pos = current_pos + QPoint(0, widget.height())
        
        anim.setStartValue(start_pos)
        anim.setEndValue(current_pos)
        
        return anim
    
    @staticmethod
    def scale_in(widget, duration: int = 300) -> QPropertyAnimation:
        """Scale in animation (growing)"""
        # Note: QWidget doesn't have direct scale property
        # This is a placeholder - actual implementation needs geometry animation
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        return anim
    
    @staticmethod
    def bounce(widget, property_name: bytes = b"pos", duration: int = 500) -> QPropertyAnimation:
        """Bounce animation"""
        anim = QPropertyAnimation(widget, property_name)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        return anim


class AnimationChain:
    """Chain multiple animations together"""
    
    def __init__(self):
        self.parallel_group = QParallelAnimationGroup()
        self.sequential_group = QSequentialAnimationGroup()
        self._current_group = self.sequential_group
    
    def add_parallel(self, animations: List[QPropertyAnimation]):
        """Add animations to run in parallel"""
        group = QParallelAnimationGroup()
        for anim in animations:
            group.addAnimation(anim)
        self._current_group.addAnimation(group)
        return self
    
    def add_sequential(self, animations: List[QPropertyAnimation]):
        """Add animations to run sequentially"""
        for anim in animations:
            self._current_group.addAnimation(anim)
        return self
    
    def add_pause(self, duration: int):
        """Add a pause between animations"""
        from PyQt6.QtCore import QPauseAnimation
        pause = QPauseAnimation(duration)
        self._current_group.addAnimation(pause)
        return self
    
    def start(self):
        """Start the animation chain"""
        self._current_group.start()
    
    def stop(self):
        """Stop the animation chain"""
        self._current_group.stop()


class EasingCurves:
    """Common easing curves for animations"""
    
    # Smooth and natural
    SMOOTH = QEasingCurve.Type.OutCubic
    SMOOTH_IN = QEasingCurve.Type.InCubic
    SMOOTH_IN_OUT = QEasingCurve.Type.InOutCubic
    
    # Elastic
    ELASTIC = QEasingCurve.Type.OutElastic
    ELASTIC_IN = QEasingCurve.Type.InElastic
    
    # Bounce
    BOUNCE = QEasingCurve.Type.OutBounce
    BOUNCE_IN = QEasingCurve.Type.InBounce
    
    # Back (overshoot)
    BACK = QEasingCurve.Type.OutBack
    BACK_IN = QEasingCurve.Type.InBack
    
    # Sharp
    SHARP = QEasingCurve.Type.OutQuad


if __name__ == "__main__":
    print("[TEST] Animation Utilities")
    print("=" * 60)
    
    print("\n[INFO] Available animation presets:")
    print("  - fade_in")
    print("  - fade_out")
    print("  - slide_in")
    print("  - scale_in")
    print("  - bounce")
    
    print("\n[INFO] Available easing curves:")
    for attr in dir(EasingCurves):
        if not attr.startswith('_'):
            print(f"  - {attr}")
    
    print("\n" + "=" * 60)
    print("✅ Animation utilities ready!")
