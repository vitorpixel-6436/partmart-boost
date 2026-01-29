#!/usr/bin/env python3
"""Software Fallback Backend

Version: 0.3.5d (package 3.7a) - Stage 1/9

STUB: Enhanced implementation in Stage 6
"""
import numpy as np
from typing import Tuple

from .base import BaseBackend
from ..types import (
    UpscaleConfig,
    FrameData,
    UpscaleMetrics,
    BackendInfo,
    UpscalerBackend,
    UpscalerFeature
)


class SoftwareBackend(BaseBackend):
    """Software Fallback Backend
    
    CPU-based upscaling that works everywhere.
    Stage 6 will add:
    - Lanczos upscaling
    - Edge-aware sharpening
    - Better temporal filtering
    - Optimized performance
    """
    
    def __init__(self):
        super().__init__()
        print("[SoftwareBackend] Stage 1: Stub created (enhanced in Stage 6)")
    
    def initialize(self) -> bool:
        """Initialize software backend"""
        print("[SoftwareBackend] Stage 1: Stub initialize (enhanced in Stage 6)")
        self._initialized = True  # Always available
        return True
    
    def shutdown(self) -> bool:
        """Shutdown software backend"""
        self._initialized = False
        return True
    
    def is_available(self) -> bool:
        """Check if software backend is available"""
        return True  # Always available
    
    def get_info(self) -> BackendInfo:
        """Get software backend info"""
        return BackendInfo(
            backend=UpscalerBackend.SOFTWARE,
            version="1.0.0 (stub)",
            available=True,
            features=(
                UpscalerFeature.UPSCALING |
                UpscalerFeature.FRAME_GENERATION
            ),
            gpu_name="CPU",
            driver_version="N/A"
        )
    
    def create_context(self, config: UpscaleConfig) -> bool:
        """Create software context"""
        print("[SoftwareBackend] Stage 1: Stub create_context")
        return True
    
    def upscale(self, frame: FrameData) -> Tuple[np.ndarray, UpscaleMetrics]:
        """Upscale with software"""
        raise NotImplementedError("SoftwareBackend: Enhanced in Stage 6")
    
    def generate_frame(
        self,
        prev_frame: FrameData,
        next_frame: FrameData,
        t: float = 0.5
    ) -> Tuple[np.ndarray, UpscaleMetrics]:
        """Generate frame with software"""
        raise NotImplementedError("SoftwareBackend: Enhanced in Stage 6")
    
    def get_backend_type(self) -> UpscalerBackend:
        return UpscalerBackend.SOFTWARE
