#!/usr/bin/env python3
"""FSR4 Types and Enums

Version: 0.3.5d+patch8
"""
from enum import Enum, IntEnum
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import numpy.typing as npt


class FSR4QualityMode(IntEnum):
    """FSR4 Quality Modes
    
    Matches AMD FSR 4 quality presets.
    """
    PERFORMANCE = 0      # 2.0x scale (540p -> 1080p)
    BALANCED = 1         # 1.7x scale (635p -> 1080p)
    QUALITY = 2          # 1.5x scale (720p -> 1080p)
    ULTRA_QUALITY = 3    # 1.3x scale (831p -> 1080p)
    NATIVE = 4           # 1.0x scale (native resolution)


class FSR4Feature(IntEnum):
    """FSR4 Features"""
    UPSCALING = 1 << 0           # Basic upscaling
    FRAME_GENERATION = 1 << 1    # Frame generation
    ANTI_ALIASING = 1 << 2       # Temporal anti-aliasing
    SHARPENING = 1 << 3          # Adaptive sharpening
    MOTION_VECTORS = 1 << 4      # Motion vector support


class FSR4Status(IntEnum):
    """FSR4 Status Codes"""
    OK = 0
    ERROR_INVALID_PARAM = -1
    ERROR_OUT_OF_MEMORY = -2
    ERROR_NOT_INITIALIZED = -3
    ERROR_DEVICE_NOT_FOUND = -4
    ERROR_UNSUPPORTED_FORMAT = -5
    ERROR_PROCESSING_FAILED = -6


@dataclass
class FSR4Config:
    """FSR4 Configuration
    
    Attributes:
        input_resolution: Input frame size (width, height)
        output_resolution: Output frame size (width, height)
        quality_mode: Quality mode
        enable_frame_gen: Enable frame generation
        enable_sharpening: Enable sharpening
        sharpness: Sharpness level (0.0-1.0)
        enable_hdr: Enable HDR support
    """
    input_resolution: Tuple[int, int]
    output_resolution: Tuple[int, int]
    quality_mode: FSR4QualityMode = FSR4QualityMode.QUALITY
    enable_frame_gen: bool = False
    enable_sharpening: bool = True
    sharpness: float = 0.5
    enable_hdr: bool = False
    
    def get_scale_factor(self) -> float:
        """Get scale factor for quality mode"""
        scale_factors = {
            FSR4QualityMode.PERFORMANCE: 2.0,
            FSR4QualityMode.BALANCED: 1.7,
            FSR4QualityMode.QUALITY: 1.5,
            FSR4QualityMode.ULTRA_QUALITY: 1.3,
            FSR4QualityMode.NATIVE: 1.0,
        }
        return scale_factors[self.quality_mode]
    
    def get_render_resolution(self) -> Tuple[int, int]:
        """Get actual render resolution based on quality mode"""
        scale = self.get_scale_factor()
        width = int(self.output_resolution[0] / scale)
        height = int(self.output_resolution[1] / scale)
        return (width, height)


@dataclass
class FSR4FrameData:
    """Frame data for FSR4 processing
    
    Attributes:
        color: Color buffer (RGB or RGBA)
        depth: Depth buffer (optional)
        motion_vectors: Motion vectors (optional)
        exposure: Exposure value (optional)
        timestamp: Frame timestamp
    """
    color: npt.NDArray[np.uint8]
    depth: Optional[npt.NDArray[np.float32]] = None
    motion_vectors: Optional[npt.NDArray[np.float32]] = None
    exposure: Optional[float] = None
    timestamp: float = 0.0


@dataclass
class FSR4PerformanceMetrics:
    """Performance metrics
    
    Attributes:
        upscale_time_ms: Upscaling time (ms)
        frame_gen_time_ms: Frame generation time (ms)
        total_time_ms: Total processing time (ms)
        memory_used_mb: Memory used (MB)
        fps: Frames per second
    """
    upscale_time_ms: float = 0.0
    frame_gen_time_ms: float = 0.0
    total_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    fps: float = 0.0
