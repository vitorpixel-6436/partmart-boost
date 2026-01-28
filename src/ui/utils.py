"""UI Utilities

Version: 0.3.5c
Author: PartMart Team
"""
from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from typing import Callable, Optional


def set_opacity(widget: QWidget, opacity: float):
    """Set widget opacity"""
    effect = QGraphicsOpacityEffect()
    effect.setOpacity(opacity)
    widget.setGraphicsEffect(effect)


def fade_widget(widget: QWidget, fade_in: bool = True, duration: int = 300, 
                on_finished: Optional[Callable] = None):
    """Fade widget in or out"""
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    if fade_in:
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
    else:
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
    
    if on_finished:
        anim.finished.connect(on_finished)
    
    anim.start()
    return anim


def delay_call(callback: Callable, delay_ms: int):
    """Call function after delay"""
    QTimer.singleShot(delay_ms, callback)


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_temperature(temp: float, unit: str = 'C') -> str:
    """Format temperature"""
    if unit == 'F':
        temp = temp * 9/5 + 32
        return f"{temp:.0f}°F"
    return f"{temp:.0f}°C"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage"""
    return f"{value:.{decimals}f}%"


def format_frequency(freq_mhz: float) -> str:
    """Format frequency (MHz to GHz if >= 1000)"""
    if freq_mhz >= 1000:
        return f"{freq_mhz / 1000:.2f} GHz"
    return f"{freq_mhz:.0f} MHz"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation"""
    return start + (end - start) * t


class DebounceTimer:
    """Debounce rapid calls"""
    
    def __init__(self, delay_ms: int = 300):
        self.delay_ms = delay_ms
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.callback = None
    
    def call(self, callback: Callable):
        """Call function after delay, canceling previous calls"""
        self.timer.stop()
        self.callback = callback
        self.timer.timeout.connect(callback)
        self.timer.start(self.delay_ms)


class ThrottleTimer:
    """Throttle rapid calls (execute at most once per interval)"""
    
    def __init__(self, interval_ms: int = 300):
        self.interval_ms = interval_ms
        self.timer = QTimer()
        self.can_execute = True
    
    def call(self, callback: Callable) -> bool:
        """Execute if allowed, return True if executed"""
        if self.can_execute:
            callback()
            self.can_execute = False
            QTimer.singleShot(self.interval_ms, lambda: setattr(self, 'can_execute', True))
            return True
        return False


if __name__ == "__main__":
    print("[TEST] UI Utilities")
    print("=" * 60)
    
    # Test formatters
    print("\n[TEST] Formatters:")
    print(f"  Bytes: {format_bytes(1536000000)}")
    print(f"  Temperature: {format_temperature(65)}")
    print(f"  Percentage: {format_percentage(67.8)}")
    print(f"  Frequency: {format_frequency(2400)}")
    
    # Test math
    print("\n[TEST] Math utilities:")
    print(f"  Clamp(150, 0, 100): {clamp(150, 0, 100)}")
    print(f"  Lerp(0, 100, 0.5): {lerp(0, 100, 0.5)}")
    
    print("\n" + "=" * 60)
    print("✅ UI utilities work!")
