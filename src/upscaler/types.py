#!/usr/bin/env python3
"""Upscaler Types and Enums

Version: 0.4.0-alpha
"""
from enum import IntEnum
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy.typing as npt


class QualityMode(IntEnum):
    """Upscaling quality modes (unified across backends)"""
    PERFORMANCE = 0      # 2.0x scale - Maximum FPS
    BALANCED = 1         # 1.7x scale - Balanced
    QUALITY = 2          # 1.5x scale - Best quality/perf
    ULTRA_QUALITY = 3    # 1.3x scale - Maximum quality
    NATIVE = 4           # 1.0x scale - Native + sharpening
    
    def get_scale_factor(self) -> float:
        """Get scale factor"""
        scales = {
            QualityMode.PERFORMANCE: 2.0,
            QualityMode.BALANCED: 1.7,
            QualityMode.QUALITY: 1.5,
            QualityMode.ULTRA_QUALITY: 1.3,
            QualityMode.NATIVE: 1.0,
        }
        return scales[self]


class UpscalerBackend(IntEnum):
    """Available upscaler backends"""
    FSR3 = 0         # AMD FidelityFX Super Resolution 3.1
    XESS = 1         # Intel Xe Super Sampling 2.1
    SOFTWARE = 2     # Software fallback
    AUTO = 99        # Auto-detect best


class UpscalerStatus(IntEnum):
    """Status codes"""
    OK = 0
    ERROR_INVALID_PARAM = -1
    ERROR_OUT_OF_MEMORY = -2
    ERROR_NOT_INITIALIZED = -3
    ERROR_BACKEND_NOT_AVAILABLE = -4
    ERROR_DLL_NOT_FOUND = -5
    ERROR_GPU_NOT_SUPPORTED = -6
    ERROR_PROCESSING_FAILED = -7


@dataclass
class UpscalerConfig:
    """Upscaler configuration"""
    input_resolution: Tuple[int, int]
    output_resolution: Tuple[int, int]
    quality_mode: QualityMode = QualityMode.QUALITY
    backend: UpscalerBackend = UpscalerBackend.AUTO
    enable_frame_gen: bool = False
    enable_sharpening: bool = True
    sharpness: float = 0.5
    enable_hdr: bool = False


@dataclass
class FrameData:
    """Frame data for upscaling"""
    color: npt.NDArray  # Color buffer (RGB/RGBA, uint8)
    depth: Optional[npt.NDArray] = None  # Depth buffer (float32)
    motion_vectors: Optional[npt.NDArray] = None  # Motion vectors (float32)
    timestamp: float = 0.0


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    backend: UpscalerBackend
    upscale_time_ms: float = 0.0
    frame_gen_time_ms: float = 0.0
    total_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    fps: float = 0.0
