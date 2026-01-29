#!/usr/bin/env python3
"""Universal Upscaler - Main API

Version: 0.3.5d (package 3.8a, stage 4/6)
"""
import threading
from typing import Optional, List
from pathlib import Path

from .types import (
    UpscalerBackend,
    UpscalerQuality,
    UpscaleConfig,
    FrameData,
    UpscaleMetrics,
    BackendInfo
)
from .backends.base import BaseBackend


class UniversalUpscaler:
    """Universal Upscaler - Auto-detecting multi-backend upscaling system
    
    Supports:
    - OptiScaler (FSR 3.1 / XeSS 2.1 / DLSS via middleware) ⭐ PRIMARY
    - FSR 3.1 (AMD, direct DLL)
    - XeSS 2.1 (Intel, direct DLL)
    - Software fallback (always works)
    
    Usage:
        upscaler = UniversalUpscaler()
        upscaler.initialize()  # Auto-detects best backend
        
        context = upscaler.create_context(
            input_resolution=(1920, 1080),
            output_resolution=(3840, 2160),
            quality=UpscalerQuality.QUALITY
        )
        
        upscaled, metrics = context.upscale(frame)
    """
    
    def __init__(self, backend: Optional[UpscalerBackend] = None):
        """Initialize Universal Upscaler
        
        Args:
            backend: Force specific backend (None = auto-detect)
        """
        self._lock = threading.Lock()
        self._backend: Optional[BaseBackend] = None
        self._forced_backend = backend
        self._config: Optional[UpscaleConfig] = None
        
        print("[UniversalUpscaler] Initialized (Package 3.8a, Stage 4/6)")
    
    def initialize(self) -> bool:
        """Initialize upscaler with best available backend
        
        Priority:
        1. OptiScaler (if installed) → Real FSR 3.1 on GPU
        2. Direct DLL (if available) → FSR/XeSS via DLL
        3. Software (always works) → CPU fallback
        
        Returns:
            True if successful
        """
        with self._lock:
            print("\n[UniversalUpscaler] Stage 4: Initialize with OptiScaler support")
            
            if self._forced_backend:
                # Use forced backend
                return self._init_backend(self._forced_backend)
            
            # Try backends in priority order
            backends_to_try = [
                UpscalerBackend.OPTISCALER,  # Try OptiScaler first ⭐
                UpscalerBackend.FSR3,         # Then direct FSR DLL
                UpscalerBackend.XESS,         # Then XeSS DLL
                UpscalerBackend.SOFTWARE,     # Software fallback
            ]
            
            for backend_type in backends_to_try:
                if self._init_backend(backend_type):
                    info = self._backend.get_info()
                    print(f"\n[UniversalUpscaler] Using backend: {info.backend.name}")
                    print(f"  Version: {info.version}")
                    print(f"  GPU: {info.gpu_name}")
                    return True
            
            print("[UniversalUpscaler] ERROR: No backend available!")
            return False
    
    def _init_backend(self, backend_type: UpscalerBackend) -> bool:
        """Initialize specific backend
        
        Args:
            backend_type: Backend to initialize
        
        Returns:
            True if successful
        """
        try:
            # Import backend
            if backend_type == UpscalerBackend.OPTISCALER:
                from .backends.optiscaler_backend import OptiScalerBackend
                backend = OptiScalerBackend()
            elif backend_type == UpscalerBackend.FSR3:
                from .backends.fsr3 import FSR3Backend
                backend = FSR3Backend()
            elif backend_type == UpscalerBackend.XESS:
                from .backends.xess import XeSSBackend
                backend = XeSSBackend()
            elif backend_type == UpscalerBackend.SOFTWARE:
                from .backends.software import SoftwareBackend
                backend = SoftwareBackend()
            else:
                return False
            
            # Check availability
            if not backend.is_available():
                print(f"[UniversalUpscaler] {backend_type.name} not available")
                return False
            
            # Initialize
            if not backend.initialize():
                print(f"[UniversalUpscaler] {backend_type.name} initialization failed")
                return False
            
            self._backend = backend
            return True
        
        except ImportError as e:
            print(f"[UniversalUpscaler] Failed to import {backend_type.name}: {e}")
            return False
        except Exception as e:
            print(f"[UniversalUpscaler] {backend_type.name} init error: {e}")
            return False
    
    def create_context(self, config: UpscaleConfig) -> 'UpscaleContext':
        """Create upscaling context
        
        Args:
            config: Upscaling configuration
        
        Returns:
            UpscaleContext instance
        """
        if not self._backend:
            raise RuntimeError("UniversalUpscaler not initialized")
        
        self._config = config
        
        if not self._backend.create_context(config):
            raise RuntimeError("Failed to create backend context")
        
        return UpscaleContext(self._backend, config)
    
    def get_backend_info(self) -> Optional[BackendInfo]:
        """Get current backend information
        
        Returns:
            BackendInfo or None
        """
        if self._backend:
            return self._backend.get_info()
        return None
    
    def switch_backend(self, backend_type: UpscalerBackend) -> bool:
        """Switch to different backend at runtime
        
        Args:
            backend_type: New backend type
        
        Returns:
            True if successful
        """
        with self._lock:
            # Shutdown current backend
            if self._backend:
                self._backend.shutdown()
            
            # Initialize new backend
            success = self._init_backend(backend_type)
            
            # Recreate context if we had one
            if success and self._config:
                self._backend.create_context(self._config)
            
            return success
    
    def shutdown(self):
        """Shutdown upscaler"""
        with self._lock:
            if self._backend:
                self._backend.shutdown()
                self._backend = None


class UpscaleContext:
    """Upscaling context for a specific configuration"""
    
    def __init__(self, backend: BaseBackend, config: UpscaleConfig):
        self.backend = backend
        self.config = config
    
    def upscale(self, frame: FrameData) -> tuple[np.ndarray, UpscaleMetrics]:
        """Upscale a frame
        
        Args:
            frame: Input frame data
        
        Returns:
            Tuple of (upscaled_frame, metrics)
        """
        return self.backend.upscale(frame)
    
    def generate_frame(
        self,
        prev_frame: FrameData,
        next_frame: FrameData,
        t: float = 0.5
    ) -> tuple[np.ndarray, UpscaleMetrics]:
        """Generate intermediate frame
        
        Args:
            prev_frame: Previous frame
            next_frame: Next frame
            t: Interpolation factor
        
        Returns:
            Tuple of (generated_frame, metrics)
        """
        return self.backend.generate_frame(prev_frame, next_frame, t)
