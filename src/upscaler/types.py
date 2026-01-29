#!/usr/bin/env python3
"""Universal Upscaler Types

Version: 0.3.5d (package 3.7a)
"""
from enum import IntEnum
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
import numpy as np
import numpy.typing as npt


class UpscalerBackend(IntEnum):
    """Available upscaler backends"""
    FSR3 = 0        # AMD FidelityFX Super Resolution 3.1
    XESS = 1        # Intel Xe Super Sampling 2.1
    SOFTWARE = 2    # Software fallback (bicubic + enhancements)


class UpscalerQuality(IntEnum):
    """Quality modes (universal across all backends)"""
    PERFORMANCE = 0      # 2.0x scale - max FPS
    BALANCED = 1         # 1.7x scale - balance
    QUALITY = 2          # 1.5x scale - recommended
    ULTRA_QUALITY = 3    # 1.3x scale - best quality
    NATIVE = 4           # 1.0x scale - no upscaling


class UpscalerFeature(IntEnum):
    """Backend features"""
    UPSCALING = 1 << 0           # Basic upscaling
    FRAME_GENERATION = 1 << 1    # Frame generation
    HDR = 1 << 2                 # HDR support
    MOTION_VECTORS = 1 << 3      # Motion vector support
    ASYNC = 1 << 4               # Async processing


@dataclass
class UpscaleConfig:
    """Universal upscale configuration
    
    Attributes:
        input_resolution: Input frame size (width, height)
        output_resolution: Output frame size (width, height)
        quality: Quality mode
        backend: Preferred backend (None = auto)
        enable_frame_gen: Enable frame generation
        enable_hdr: Enable HDR
        sharpness: Sharpness level (0.0-1.0)
    """
    input_resolution: Tuple[int, int]
    output_resolution: Tuple[int, int]
    quality: UpscalerQuality = UpscalerQuality.QUALITY
    backend: Optional[UpscalerBackend] = None  # None = auto-detect
    enable_frame_gen: bool = False
    enable_hdr: bool = False
    sharpness: float = 0.5
    
    def get_scale_factor(self) -> float:
        """Get scale factor for quality mode"""
        scales = {
            UpscalerQuality.PERFORMANCE: 2.0,
            UpscalerQuality.BALANCED: 1.7,
            UpscalerQuality.QUALITY: 1.5,
            UpscalerQuality.ULTRA_QUALITY: 1.3,
            UpscalerQuality.NATIVE: 1.0,
        }
        return scales[self.quality]
    
    def get_render_resolution(self) -> Tuple[int, int]:
        """Get actual render resolution based on quality"""
        scale = self.get_scale_factor()
        w = int(self.output_resolution[0] / scale)
        h = int(self.output_resolution[1] / scale)
        return (w, h)


@dataclass
class FrameData:
    """Frame data for upscaling
    
    Attributes:
        color: Color buffer (RGB/RGBA, uint8)
        depth: Depth buffer (optional, float32)
        motion_vectors: Motion vectors (optional, float32)
        exposure: Exposure value (optional)
        timestamp: Frame timestamp
    """
    color: npt.NDArray[np.uint8]
    depth: Optional[npt.NDArray[np.float32]] = None
    motion_vectors: Optional[npt.NDArray[np.float32]] = None
    exposure: Optional[float] = None
    timestamp: float = 0.0


@dataclass
class UpscaleMetrics:
    """Performance metrics
    
    Attributes:
        backend: Backend used
        upscale_time_ms: Upscaling time (ms)
        frame_gen_time_ms: Frame generation time (ms)
        total_time_ms: Total processing time (ms)
        memory_used_mb: Memory used (MB)
        fps: Frames per second
    """
    backend: UpscalerBackend
    upscale_time_ms: float = 0.0
    frame_gen_time_ms: float = 0.0
    total_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    fps: float = 0.0


@dataclass
class BackendInfo:
    """Backend information
    
    Attributes:
        backend: Backend type
        version: Backend version string
        available: Is backend available
        features: Supported features (bitmask)
        gpu_name: GPU name (if applicable)
        driver_version: Driver version (if applicable)
    """
    backend: UpscalerBackend
    version: str
    available: bool
    features: int  # UpscalerFeature bitmask
    gpu_name: Optional[str] = None
    driver_version: Optional[str] = None
    
    def has_feature(self, feature: UpscalerFeature) -> bool:
        """Check if backend supports feature"""
        return bool(self.features & feature)


# Exceptions

class UpscalerException(Exception):
    """Base upscaler exception"""
    pass


class BackendNotAvailableError(UpscalerException):
    """Backend not available"""
    pass


class UpscaleError(UpscalerException):
    """Upscaling failed"""
    pass


class FrameGenerationError(UpscalerException):
    """Frame generation failed"""
    pass
