#!/usr/bin/env python3
"""Universal Upscaler - Main API

Version: 0.3.5d (package 3.7a) - Stage 1/9
"""
import threading
from typing import Optional, Tuple, List
import numpy.typing as npt

from .types import (
    UpscaleConfig,
    FrameData,
    UpscaleMetrics,
    BackendInfo,
    UpscalerBackend,
    BackendNotAvailableError,
    UpscaleError
)
from .backends import BaseBackend, FSR3Backend, XeSSBackend, SoftwareBackend


class UniversalUpscaler:
    """Universal Upscaler System
    
    Auto-detects and uses best available backend:
    1. FSR 3.1 (AMD, if available)
    2. XeSS 2.1 (Intel, if available)
    3. Software (always available)
    
    Can hot-swap between backends.
    """
    
    def __init__(self):
        """Initialize Universal Upscaler"""
        self._lock = threading.Lock()
        self._backends: List[BaseBackend] = []
        self._current_backend: Optional[BaseBackend] = None
        self._config: Optional[UpscaleConfig] = None
        
        print("[UniversalUpscaler] Initializing (Stage 1/9)")
        print("  Next stages will add:")
        print("  - Stage 2: GPU Detector")
        print("  - Stage 3: Backend Manager")
        print("  - Stage 4: Real FSR 3.1")
        print("  - Stage 5: Real XeSS 2.1")
        print("  - Stage 6: Enhanced Software")
        print("  - Stage 7: Frame Generation")
        print("  - Stage 8: Integration")
        print("  - Stage 9: Tests & Docs")
    
    def initialize(self) -> bool:
        """Initialize upscaler system
        
        Returns:
            True if successful
        """
        with self._lock:
            print("\n[UniversalUpscaler] Stage 1: Stub initialize")
            
            # Stage 1: Create backend stubs
            self._backends = [
                FSR3Backend(),
                XeSSBackend(),
                SoftwareBackend()
            ]
            
            # Stage 2 will add: Auto-detect best backend
            # Stage 3 will add: Backend manager
            
            print("[UniversalUpscaler] Stage 1: Architecture ready")
            return True
    
    def get_available_backends(self) -> List[BackendInfo]:
        """Get list of available backends
        
        Returns:
            List of backend info
        """
        with self._lock:
            return [b.get_info() for b in self._backends]
    
    def create_context(
        self,
        config: UpscaleConfig
    ) -> bool:
        """Create upscaling context
        
        Args:
            config: Upscale configuration
        
        Returns:
            True if successful
        """
        with self._lock:
            print("[UniversalUpscaler] Stage 1: Stub create_context")
            self._config = config
            # Stage 2-3 will add: Backend selection and initialization
            return True
    
    def upscale(self, frame: FrameData) -> Tuple[npt.NDArray, UpscaleMetrics]:
        """Upscale frame
        
        Args:
            frame: Input frame data
        
        Returns:
            Tuple of (upscaled_frame, metrics)
        """
        raise NotImplementedError("UniversalUpscaler: Upscale in Stage 3+")
    
    def generate_frame(
        self,
        prev_frame: FrameData,
        next_frame: FrameData,
        t: float = 0.5
    ) -> Tuple[npt.NDArray, UpscaleMetrics]:
        """Generate intermediate frame
        
        Args:
            prev_frame: Previous frame
            next_frame: Next frame
            t: Interpolation factor (0.0-1.0)
        
        Returns:
            Tuple of (generated_frame, metrics)
        """
        raise NotImplementedError("UniversalUpscaler: Frame gen in Stage 7")
    
    def swap_backend(self, backend: UpscalerBackend) -> bool:
        """Swap to different backend
        
        Args:
            backend: Target backend
        
        Returns:
            True if successful
        """
        with self._lock:
            print(f"[UniversalUpscaler] Stage 1: Stub swap to {backend.name}")
            # Stage 3 will add: Real backend swapping
            return False
    
    def get_current_backend(self) -> Optional[UpscalerBackend]:
        """Get current backend
        
        Returns:
            Current backend or None
        """
        with self._lock:
            if self._current_backend:
                return self._current_backend.get_backend_type()
            return None
    
    def shutdown(self) -> bool:
        """Shutdown upscaler and cleanup
        
        Returns:
            True if successful
        """
        with self._lock:
            for backend in self._backends:
                backend.shutdown()
            self._backends.clear()
            self._current_backend = None
            print("[UniversalUpscaler] Stage 1: Shutdown complete")
            return True
