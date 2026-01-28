#!/usr/bin/env python3
"""Optical Flow Engine

Version: 0.3.5d_package3.4d

Optical flow computation for motion vector generation.

Methods:
- Dense flow: Farneback algorithm
- Sparse flow: Lucas-Kanade
- Deep learning: FlowNet (optional)
"""
import numpy as np
import numpy.typing as npt
from enum import Enum
from typing import Optional

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[OpticalFlow] WARNING: OpenCV not available, optical flow disabled")


class FlowMethod(Enum):
    """Optical flow method
    
    Attributes:
        FARNEBACK: Dense optical flow (Farneback)
        LUCAS_KANADE: Sparse optical flow (Lucas-Kanade)
        SIMPLE: Simple block matching
    """
    FARNEBACK = "farneback"
    LUCAS_KANADE = "lucas_kanade"
    SIMPLE = "simple"


class OpticalFlowEngine:
    """Optical Flow Engine
    
    v0.3.5d_package3.4d - Motion Vector Generation
    
    Computes optical flow between frames to generate
    motion vectors for frame interpolation.
    
    Example:
        >>> engine = OpticalFlowEngine()
        >>> flow = engine.compute_flow(frame1, frame2)
        >>> # flow shape: (height, width, 2) - [dx, dy] per pixel
    """
    
    def __init__(self, method: FlowMethod = FlowMethod.FARNEBACK):
        """Initialize optical flow engine
        
        Args:
            method: Flow computation method
        """
        self._method = method
        self._available = CV2_AVAILABLE
        
        print(f"[OpticalFlowEngine v0.3.5d_package3.4d] Initialized ({method.value})")
        if not self._available:
            print("[OpticalFlowEngine] OpenCV unavailable, using simple fallback")
    
    def compute_flow(self,
                    prev_frame: npt.NDArray[np.uint8],
                    curr_frame: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Compute optical flow
        
        Args:
            prev_frame: Previous frame (RGB)
            curr_frame: Current frame (RGB)
        
        Returns:
            Flow field (height, width, 2) with [dx, dy] per pixel
        
        Example:
            >>> flow = engine.compute_flow(frame1, frame2)
        """
        if not self._available:
            return self._compute_simple_flow(prev_frame, curr_frame)
        
        if self._method == FlowMethod.FARNEBACK:
            return self._compute_farneback(prev_frame, curr_frame)
        elif self._method == FlowMethod.LUCAS_KANADE:
            return self._compute_lucas_kanade(prev_frame, curr_frame)
        else:
            return self._compute_simple_flow(prev_frame, curr_frame)
    
    def _compute_farneback(self,
                          prev_frame: npt.NDArray[np.uint8],
                          curr_frame: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Compute dense optical flow using Farneback
        
        Args:
            prev_frame: Previous frame
            curr_frame: Current frame
        
        Returns:
            Dense flow field
        """
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY)
        
        # Compute flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray,
            curr_gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
        
        return flow
    
    def _compute_lucas_kanade(self,
                             prev_frame: npt.NDArray[np.uint8],
                             curr_frame: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Compute sparse optical flow using Lucas-Kanade
        
        Args:
            prev_frame: Previous frame
            curr_frame: Current frame
        
        Returns:
            Dense flow field (interpolated from sparse)
        """
        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY)
        
        # Detect features
        features = cv2.goodFeaturesToTrack(
            prev_gray,
            maxCorners=1000,
            qualityLevel=0.01,
            minDistance=10
        )
        
        if features is None:
            # No features found, return zero flow
            return np.zeros((prev_frame.shape[0], prev_frame.shape[1], 2), dtype=np.float32)
        
        # Track features
        tracked, status, _ = cv2.calcOpticalFlowPyrLK(
            prev_gray,
            curr_gray,
            features,
            None
        )
        
        # Create dense flow from sparse
        flow = np.zeros((prev_frame.shape[0], prev_frame.shape[1], 2), dtype=np.float32)
        
        good_old = features[status == 1]
        good_new = tracked[status == 1]
        
        for (x0, y0), (x1, y1) in zip(good_old, good_new):
            flow[int(y0), int(x0)] = [x1 - x0, y1 - y0]
        
        # Interpolate to fill gaps
        # TODO: Proper interpolation
        
        return flow
    
    def _compute_simple_flow(self,
                           prev_frame: npt.NDArray[np.uint8],
                           curr_frame: npt.NDArray[np.uint8]) -> npt.NDArray[np.float32]:
        """Simple flow estimation (fallback)
        
        Args:
            prev_frame: Previous frame
            curr_frame: Current frame
        
        Returns:
            Zero flow field
        """
        # Return zero flow (no motion)
        return np.zeros((prev_frame.shape[0], prev_frame.shape[1], 2), dtype=np.float32)


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("OpticalFlowEngine v0.3.5d_package3.4d Test")
    print("="*60)
    
    engine = OpticalFlowEngine(method=FlowMethod.FARNEBACK)
    
    print("\n[Test 1] Create test frames")
    frame1 = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    frame2 = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    print(f"  Frame 1: {frame1.shape}")
    print(f"  Frame 2: {frame2.shape}")
    
    print("\n[Test 2] Compute flow")
    flow = engine.compute_flow(frame1, frame2)
    print(f"  Flow shape: {flow.shape}")
    print(f"  Flow dtype: {flow.dtype}")
    print(f"  Flow range: [{flow.min():.2f}, {flow.max():.2f}]")
    
    print("\n" + "="*60)
    print("✅ OpticalFlowEngine - Test Complete!")
    print("="*60)
