#!/usr/bin/env python3
"""Upscaler Types and Enums

Version: 0.3.5d (package 3.8a, stage 4/6)
"""
from enum import IntEnum, IntFlag
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np


class UpscalerBackend(IntEnum):
    """Upscaling backend type"""
    SOFTWARE = 0      # CPU fallback
    FSR3 = 1         # AMD FSR 3.1 (direct DLL)
    XESS = 2         # Intel XeSS 2.1 (direct DLL)
    OPTISCALER = 3   # OptiScaler middleware (FSR3/XeSS/DLSS)


class UpscalerQuality(IntEnum):
    """Quality modes for upscaling"""
    PERFORMANCE = 0      # 2.0x scale - max FPS
    BALANCED = 1         # 1.7x scale - balance
    QUALITY = 2          # 1.5x scale - recommended
    ULTRA_QUALITY = 3    # 1.3x scale - best quality
    NATIVE = 4           # 1.0x scale - no upscaling


class UpscalerFeature(IntFlag):
    """Feature flags for upscaler capabilities"""
    UPSCALING = 1 << 0          # Basic upscaling
    FRAME_GENERATION = 1 << 1   # Frame interpolation
    MOTION_VECTORS = 1 << 2     # Motion vector support
    SHARPENING = 1 << 3         # Sharpening filter
    HDR = 1 << 4               # HDR support


@dataclass
class UpscaleConfig:
    """Upscaling configuration
    
    Attributes:
        input_resolution: Input resolution (width, height)
        output_resolution: Output resolution (width, height)
        quality: Quality mode
        enable_frame_gen: Enable frame generation
        sharpness: Sharpness level (0.0-1.0)
    """
    input_resolution: Tuple[int, int]
    output_resolution: Tuple[int, int]
    quality: UpscalerQuality = UpscalerQuality.QUALITY
    enable_frame_gen: bool = False
    sharpness: float = 0.5


@dataclass
class FrameData:
    """Frame data for upscaling
    
    Attributes:
        color: RGB color data (H, W, 3)
        depth: Depth buffer (optional)
        motion_vectors: Motion vectors (optional)
    """
    color: np.ndarray
    depth: Optional[np.ndarray] = None
    motion_vectors: Optional[np.ndarray] = None


@dataclass
class UpscaleMetrics:
    """Performance metrics for upscaling
    
    Attributes:
        backend: Backend used
        upscale_time_ms: Time spent upscaling (ms)
        frame_gen_time_ms: Time spent on frame generation (ms)
        total_time_ms: Total processing time (ms)
        memory_used_mb: Memory used (MB)
        fps: Frames per second
    """
    backend: UpscalerBackend
    upscale_time_ms: float
    frame_gen_time_ms: float = 0.0
    total_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    fps: float = 0.0


@dataclass
class BackendInfo:
    """Backend information
    
    Attributes:
        backend: Backend type
        version: Backend version
        available: Whether backend is available
        features: Supported features
        gpu_name: GPU name
        driver_version: Driver version
    """
    backend: UpscalerBackend
    version: str
    available: bool
    features: UpscalerFeature
    gpu_name: str = "Unknown"
    driver_version: str = "Unknown"
