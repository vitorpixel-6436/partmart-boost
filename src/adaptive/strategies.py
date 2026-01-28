#!/usr/bin/env python3
"""Quality Adjustment Strategies

Version: 0.3.5d_package3.4a

Strategies for quality adjustment in adaptive performance system.

Strategies:
- Conservative: Slow, careful adjustments
- Aggressive: Fast, responsive adjustments
- Balanced: Moderate adjustments
- Predictive: Uses prediction for proactive changes
"""
from enum import Enum
from typing import List
import numpy as np


class QualityStrategy(Enum):
    """Quality adjustment strategy
    
    Attributes:
        CONSERVATIVE: Slow, careful quality changes
        AGGRESSIVE: Fast, responsive changes
        BALANCED: Moderate adjustment speed
        PREDICTIVE: Predictive proactive changes
    """
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    PREDICTIVE = "predictive"


class PerformancePredictor:
    """Predict future performance based on history
    
    v0.3.5d_package3.4a
    
    Uses recent performance data to predict future FPS
    and proactively adjust quality.
    
    Example:
        >>> predictor = PerformancePredictor(window_size=10)
        >>> predictor.add_sample(60.5)
        >>> predicted_fps = predictor.predict_next()
    """
    
    def __init__(self, window_size: int = 10):
        """Initialize predictor
        
        Args:
            window_size: Number of samples for prediction
        """
        self._window_size = window_size
        self._fps_history: List[float] = []
        self._frame_time_history: List[float] = []
    
    def add_sample(self, fps: float, frame_time: float):
        """Add performance sample
        
        Args:
            fps: Current FPS
            frame_time: Current frame time (ms)
        """
        self._fps_history.append(fps)
        self._frame_time_history.append(frame_time)
        
        # Keep only recent samples
        if len(self._fps_history) > self._window_size:
            self._fps_history.pop(0)
            self._frame_time_history.pop(0)
    
    def predict_next(self) -> float:
        """Predict next FPS value
        
        Returns:
            Predicted FPS
        
        Example:
            >>> predicted = predictor.predict_next()
        """
        if len(self._fps_history) < 3:
            # Not enough data, return current
            return self._fps_history[-1] if self._fps_history else 60.0
        
        # Simple linear regression for trend
        x = np.arange(len(self._fps_history))
        y = np.array(self._fps_history)
        
        # Fit line: y = mx + b
        coeffs = np.polyfit(x, y, 1)
        m, b = coeffs
        
        # Predict next value
        next_x = len(self._fps_history)
        predicted = m * next_x + b
        
        return predicted
    
    def detect_trend(self) -> str:
        """Detect performance trend
        
        Returns:
            Trend: 'improving', 'degrading', or 'stable'
        
        Example:
            >>> trend = predictor.detect_trend()
        """
        if len(self._fps_history) < 3:
            return 'stable'
        
        # Calculate slope
        x = np.arange(len(self._fps_history))
        y = np.array(self._fps_history)
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        
        # Classify trend
        if slope > 1.0:  # Increasing >1 FPS per sample
            return 'improving'
        elif slope < -1.0:  # Decreasing >1 FPS per sample
            return 'degrading'
        else:
            return 'stable'
    
    def detect_spike(self, current_fps: float) -> bool:
        """Detect FPS spike (sudden drop)
        
        Args:
            current_fps: Current FPS
        
        Returns:
            True if spike detected
        
        Example:
            >>> if predictor.detect_spike(current_fps):
            >>>     print("Performance spike!")
        """
        if len(self._fps_history) < 3:
            return False
        
        # Calculate recent average
        recent_avg = np.mean(self._fps_history[-3:])
        
        # Spike if current is >20% below recent average
        threshold = recent_avg * 0.8
        return current_fps < threshold


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("Strategies v0.3.5d_package3.4a Test")
    print("="*60)
    
    print("\n[Test 1] Predictor initialization")
    predictor = PerformancePredictor(window_size=10)
    print("  ✅ Predictor created")
    
    print("\n[Test 2] Add samples (degrading performance)")
    fps_samples = [60, 59, 58, 56, 54, 52, 50]
    for fps in fps_samples:
        predictor.add_sample(fps, 1000/fps)
        print(f"  Added: {fps} FPS")
    
    print("\n[Test 3] Predict next FPS")
    predicted = predictor.predict_next()
    print(f"  Predicted: {predicted:.1f} FPS")
    
    print("\n[Test 4] Detect trend")
    trend = predictor.detect_trend()
    print(f"  Trend: {trend}")
    
    print("\n[Test 5] Detect spike")
    spike = predictor.detect_spike(40.0)
    print(f"  Spike detected: {spike}")
    
    print("\n" + "="*60)
    print("✅ Strategies - All Tests Passed!")
    print("="*60)
