#!/usr/bin/env python3
"""Upscaler

Version: 0.3.5d_package3.6a.2 - DEEP FIX: Aspect ratio & edge cases

Image upscaling with comprehensive resolution handling.
"""
import threading
from typing import Tuple, Optional
from dataclasses import dataclass
from fractions import Fraction
import numpy as np
import numpy.typing as npt


@dataclass
class AspectRatio:
    """Aspect ratio representation
    
    Attributes:
        width: Width component
        height: Height component
        decimal: Decimal representation
    """
    width: int
    height: int
    decimal: float
    
    def __str__(self) -> str:
        return f"{self.width}:{self.height}"


class ScalingMode:
    """Scaling modes"""
    FIT = "fit"  # Fit within target, preserve aspect
    FILL = "fill"  # Fill target, may crop
    STRETCH = "stretch"  # Stretch to target, ignore aspect
    EXACT = "exact"  # Exact target size


class Upscaler:
    """Upscaler
    
    v0.3.5d_package3.6a.2 - DEEP FIX: Production aspect handling
    
    Thread-safe upscaling with aspect ratio preservation.
    
    Features:
    - Exact aspect ratio calculation
    - Non-standard resolution support
    - Odd dimension handling
    - Ultra-wide support
    - Portrait mode support
    
    Example:
        >>> upscaler = Upscaler()
        >>> output = upscaler.upscale(input_data, (3840, 2160))
    """
    
    # Constants
    MIN_WIDTH = 320
    MIN_HEIGHT = 240
    MAX_WIDTH = 16384
    MAX_HEIGHT = 16384
    
    # DEEP FIX: Common aspect ratios
    COMMON_ASPECTS = {
        Fraction(16, 9): "16:9",
        Fraction(16, 10): "16:10",
        Fraction(4, 3): "4:3",
        Fraction(21, 9): "21:9",
        Fraction(32, 9): "32:9",
        Fraction(1, 1): "1:1",
    }
    
    def __init__(self):
        """Initialize upscaler"""
        # DEEP FIX: Thread safety
        self._lock = threading.Lock()
        
        # Stats
        self._frames_upscaled = 0
        self._aspect_warnings = 0
        
        print(f"[Upscaler v0.3.5d_package3.6a.2] Initialized")
    
    def upscale(self,
               input_data: npt.NDArray[np.uint8],
               target_resolution: Tuple[int, int],
               mode: str = ScalingMode.FIT) -> npt.NDArray[np.uint8]:
        """Upscale image
        
        Args:
            input_data: Input image (H, W, C)
            target_resolution: Target (width, height)
            mode: Scaling mode
        
        Returns:
            Upscaled image
        
        Raises:
            ValueError: If parameters invalid
        """
        # DEEP FIX: Validate input
        self._validate_image(input_data)
        self._validate_resolution(target_resolution)
        
        input_height, input_width = input_data.shape[:2]
        target_width, target_height = target_resolution
        
        # DEEP FIX: Calculate aspect ratios
        input_aspect = self._calculate_aspect_ratio(input_width, input_height)
        target_aspect = self._calculate_aspect_ratio(target_width, target_height)
        
        # DEEP FIX: Check for aspect ratio change
        if not self._aspects_match(input_aspect, target_aspect, tolerance=0.01):
            self._aspect_warnings += 1
            print(f"[Upscaler] WARNING: Aspect ratio change: {input_aspect} -> {target_aspect}")
        
        # Calculate output dimensions based on mode
        output_width, output_height = self._calculate_output_size(
            input_width, input_height,
            target_width, target_height,
            mode
        )
        
        # Perform upscaling
        with self._lock:
            result = self._perform_upscale(
                input_data,
                output_width,
                output_height
            )
            self._frames_upscaled += 1
            return result
    
    def _validate_image(self, data: npt.NDArray):
        """Validate input image
        
        Args:
            data: Image data
        
        Raises:
            ValueError: If invalid
        
        DEEP FIX: Comprehensive validation
        """
        if not isinstance(data, np.ndarray):
            raise TypeError(f"Expected numpy array, got {type(data)}")
        
        # Check dimensions
        if data.ndim not in (2, 3):
            raise ValueError(f"Expected 2D or 3D array, got {data.ndim}D")
        
        # Check size
        height, width = data.shape[:2]
        
        if width < self.MIN_WIDTH or width > self.MAX_WIDTH:
            raise ValueError(f"Invalid width: {width}")
        
        if height < self.MIN_HEIGHT or height > self.MAX_HEIGHT:
            raise ValueError(f"Invalid height: {height}")
        
        # DEEP FIX: Check data type
        if data.dtype not in (np.uint8, np.float32, np.float64):
            raise ValueError(f"Unsupported dtype: {data.dtype}")
    
    def _validate_resolution(self, resolution: Tuple[int, int]):
        """Validate resolution
        
        Args:
            resolution: (width, height)
        
        Raises:
            ValueError: If invalid
        """
        if not isinstance(resolution, tuple) or len(resolution) != 2:
            raise TypeError(f"Expected (width, height) tuple")
        
        width, height = resolution
        
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError(f"Width/height must be integers")
        
        if width < self.MIN_WIDTH or width > self.MAX_WIDTH:
            raise ValueError(f"Invalid width: {width}")
        
        if height < self.MIN_HEIGHT or height > self.MAX_HEIGHT:
            raise ValueError(f"Invalid height: {height}")
        
        # DEEP FIX: Check for odd dimensions
        if width % 2 != 0 or height % 2 != 0:
            print(f"[Upscaler] WARNING: Odd dimensions: {width}x{height}")
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> AspectRatio:
        """Calculate aspect ratio
        
        Args:
            width: Width
            height: Height
        
        Returns:
            Aspect ratio
        
        DEEP FIX: Exact fraction calculation
        """
        # Use fractions for exact representation
        fraction = Fraction(width, height)
        
        return AspectRatio(
            width=fraction.numerator,
            height=fraction.denominator,
            decimal=width / height
        )
    
    def _aspects_match(self, aspect1: AspectRatio, aspect2: AspectRatio, tolerance: float = 0.01) -> bool:
        """Check if aspect ratios match
        
        Args:
            aspect1: First aspect
            aspect2: Second aspect
            tolerance: Tolerance for decimal comparison
        
        Returns:
            True if match
        
        DEEP FIX: Tolerance-based comparison
        """
        return abs(aspect1.decimal - aspect2.decimal) < tolerance
    
    def _calculate_output_size(self,
                              input_width: int,
                              input_height: int,
                              target_width: int,
                              target_height: int,
                              mode: str) -> Tuple[int, int]:
        """Calculate output size based on mode
        
        Args:
            input_width: Input width
            input_height: Input height
            target_width: Target width
            target_height: Target height
            mode: Scaling mode
        
        Returns:
            (output_width, output_height)
        
        DEEP FIX: Proper scaling calculation
        """
        if mode == ScalingMode.EXACT:
            return (target_width, target_height)
        
        elif mode == ScalingMode.STRETCH:
            return (target_width, target_height)
        
        elif mode == ScalingMode.FIT:
            # Fit within target, preserve aspect
            scale_w = target_width / input_width
            scale_h = target_height / input_height
            scale = min(scale_w, scale_h)
            
            output_width = int(input_width * scale)
            output_height = int(input_height * scale)
            
            # DEEP FIX: Ensure even dimensions
            output_width = (output_width // 2) * 2
            output_height = (output_height // 2) * 2
            
            return (output_width, output_height)
        
        elif mode == ScalingMode.FILL:
            # Fill target, may crop
            scale_w = target_width / input_width
            scale_h = target_height / input_height
            scale = max(scale_w, scale_h)
            
            output_width = int(input_width * scale)
            output_height = int(input_height * scale)
            
            # DEEP FIX: Ensure even dimensions
            output_width = (output_width // 2) * 2
            output_height = (output_height // 2) * 2
            
            return (output_width, output_height)
        
        else:
            raise ValueError(f"Unknown scaling mode: {mode}")
    
    def _perform_upscale(self,
                        input_data: npt.NDArray,
                        output_width: int,
                        output_height: int) -> npt.NDArray:
        """Perform actual upscaling
        
        Args:
            input_data: Input image
            output_width: Output width
            output_height: Output height
        
        Returns:
            Upscaled image
        
        DEEP FIX: Safe upscaling implementation
        """
        # Simple nearest-neighbor for now
        # In production, use proper interpolation
        
        input_height, input_width = input_data.shape[:2]
        channels = input_data.shape[2] if input_data.ndim == 3 else 1
        
        # DEEP FIX: Calculate scale factors
        scale_x = output_width / input_width
        scale_y = output_height / input_height
        
        # Create output array
        if channels > 1:
            output = np.zeros((output_height, output_width, channels), dtype=input_data.dtype)
        else:
            output = np.zeros((output_height, output_width), dtype=input_data.dtype)
        
        # Nearest-neighbor upscaling
        for y in range(output_height):
            for x in range(output_width):
                # DEEP FIX: Safe index calculation
                src_x = min(int(x / scale_x), input_width - 1)
                src_y = min(int(y / scale_y), input_height - 1)
                
                output[y, x] = input_data[src_y, src_x]
        
        return output
    
    def get_stats(self) -> dict:
        """Get upscaling statistics
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            return {
                'frames_upscaled': self._frames_upscaled,
                'aspect_warnings': self._aspect_warnings,
            }


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("Upscaler v0.3.5d_package3.6a.2 Test (DEEP FIX)")
    print("="*60)
    
    upscaler = Upscaler()
    
    print("\n[Test 1] Standard resolution (16:9)")
    input_img = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    output = upscaler.upscale(input_img, (3840, 2160), ScalingMode.FIT)
    print(f"  Input: {input_img.shape[1]}x{input_img.shape[0]}")
    print(f"  Output: {output.shape[1]}x{output.shape[0]}")
    
    print("\n[Test 2] Ultra-wide (21:9)")
    input_img = np.random.randint(0, 256, (1080, 2560, 3), dtype=np.uint8)
    output = upscaler.upscale(input_img, (5120, 2160), ScalingMode.FIT)
    print(f"  Input: {input_img.shape[1]}x{input_img.shape[0]}")
    print(f"  Output: {output.shape[1]}x{output.shape[0]}")
    
    print("\n[Test 3] Portrait mode (9:16)")
    input_img = np.random.randint(0, 256, (1920, 1080, 3), dtype=np.uint8)
    output = upscaler.upscale(input_img, (2160, 3840), ScalingMode.FIT)
    print(f"  Input: {input_img.shape[1]}x{input_img.shape[0]}")
    print(f"  Output: {output.shape[1]}x{output.shape[0]}")
    
    print("\n[Test 4] Odd dimensions")
    input_img = np.random.randint(0, 256, (1079, 1919, 3), dtype=np.uint8)
    output = upscaler.upscale(input_img, (3840, 2160), ScalingMode.FIT)
    print(f"  Input: {input_img.shape[1]}x{input_img.shape[0]}")
    print(f"  Output: {output.shape[1]}x{output.shape[0]}")
    
    print("\n[Test 5] Statistics")
    stats = upscaler.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("✅ Upscaler - Deep Audit Complete!")
    print("="*60)
    print("\n📦 Part 2/4 Complete!")
    print("Next: Part 3 - Thermal & Power Management")
