#!/usr/bin/env python3
"""Universal Upscaler Core

Version: 0.4.0-alpha

Main upscaler class with auto-detection and backend management.
"""
import threading
from typing import Optional
import numpy as np

from .types import (
    UpscalerConfig,
    UpscalerBackend,
    UpscalerStatus,
    QualityMode,
    FrameData,
    PerformanceMetrics
)
from .exceptions import UpscalerException, UpscalerInitializationError
from .gpu_detector import detect_gpu, GPUVendor
from .backends import FSR3Backend, XeSSBackend, SoftwareBackend


class UpscalerContext:
    """Upscaling context
    
    Handles upscaling operations for a specific configuration.
    """
    
    def __init__(self, backend, backend_context, config: UpscalerConfig):
        self.backend = backend
        self.backend_context = backend_context
        self.config = config
        self._lock = threading.Lock()
        self._frames_processed = 0
    
    def upscale(self, frame_data: FrameData) -> tuple:
        """Upscale frame
        
        Args:
            frame_data: Input frame data
        
        Returns:
            (upscaled_frame, metrics)
        """
        with self._lock:
            try:
                upscaled, metrics = self.backend.upscale(frame_data)
                self._frames_processed += 1
                return upscaled, metrics
            
            except Exception as e:
                print(f"[Context] Upscale error: {e}")
                raise
    
    def get_stats(self) -> dict:
        """Get context statistics"""
        return {
            'frames_processed': self._frames_processed,
            'backend': self.backend.__class__.__name__,
        }


class UniversalUpscaler:
    """Universal Upscaler System
    
    Auto-detects GPU and selects best backend.
    Supports FSR 3.1, XeSS 2.1, and software fallback.
    """
    
    def __init__(self):
        self._initialized = False
        self._lock = threading.Lock()
        
        # Backends
        self._fsr3 = FSR3Backend()
        self._xess = XeSSBackend()
        self._software = SoftwareBackend()
        
        # Active backend
        self._active_backend = None
        self._backend_type = UpscalerBackend.AUTO
        
        # GPU info
        self._gpu_info = None
        
        print("[UniversalUpscaler] Created")
    
    def initialize(self, preferred_backend: UpscalerBackend = UpscalerBackend.AUTO) -> UpscalerStatus:
        """Initialize upscaler
        
        Args:
            preferred_backend: Preferred backend (AUTO = auto-detect)
        
        Returns:
            Status code
        """
        with self._lock:
            if self._initialized:
                print("[UniversalUpscaler] Already initialized")
                return UpscalerStatus.OK
            
            print("\n" + "="*60)
            print("UNIVERSAL UPSCALER INITIALIZATION")
            print("="*60)
            
            # Detect GPU
            print("\n[1/3] Detecting GPU...")
            self._gpu_info = detect_gpu()
            print(f"  ✅ GPU: {self._gpu_info.name} ({self._gpu_info.vendor.name})")
            
            # Initialize backends
            print("\n[2/3] Initializing backends...")
            backend_status = self._initialize_backends()
            
            # Select best backend
            print("\n[3/3] Selecting backend...")
            if preferred_backend == UpscalerBackend.AUTO:
                self._select_best_backend()
            else:
                self._select_backend(preferred_backend)
            
            if self._active_backend is None:
                print("\n❌ No backend available!")
                return UpscalerStatus.ERROR_BACKEND_NOT_AVAILABLE
            
            self._initialized = True
            
            print("\n" + "="*60)
            print(f"✅ UPSCALER READY (Backend: {self._backend_type.name})")
            print("="*60 + "\n")
            
            return UpscalerStatus.OK
    
    def _initialize_backends(self) -> dict:
        """Initialize all backends"""
        status = {}
        
        # FSR 3.1
        print("  [FSR 3.1] Checking...")
        status['fsr3'] = self._fsr3.initialize()
        if status['fsr3'] == UpscalerStatus.OK:
            print("    ✅ FSR 3.1 available")
        else:
            print("    ❌ FSR 3.1 not available (DLL not found)")
        
        # XeSS 2.1
        print("  [XeSS 2.1] Checking...")
        status['xess'] = self._xess.initialize()
        if status['xess'] == UpscalerStatus.OK:
            print("    ✅ XeSS 2.1 available")
        else:
            print("    ❌ XeSS 2.1 not available (DLL not found)")
        
        # Software
        print("  [Software] Checking...")
        status['software'] = self._software.initialize()
        if status['software'] == UpscalerStatus.OK:
            print("    ✅ Software fallback available")
        else:
            print("    ⚠️ Software fallback init warning")
        
        return status
    
    def _select_best_backend(self):
        """Auto-select best backend based on GPU and availability"""
        # Priority: FSR 3.1 > XeSS 2.1 > Software
        
        if self._fsr3._initialized:
            self._active_backend = self._fsr3
            self._backend_type = UpscalerBackend.FSR3
            print("  ⭐ Selected: FSR 3.1 (AMD FidelityFX)")
        
        elif self._xess._initialized:
            self._active_backend = self._xess
            self._backend_type = UpscalerBackend.XESS
            print("  ⭐ Selected: XeSS 2.1 (Intel)")
        
        elif self._software._initialized:
            self._active_backend = self._software
            self._backend_type = UpscalerBackend.SOFTWARE
            print("  ⭐ Selected: Software Fallback (Lanczos4)")
        
        else:
            self._active_backend = None
            print("  ❌ No backend available!")
    
    def _select_backend(self, backend: UpscalerBackend):
        """Select specific backend"""
        if backend == UpscalerBackend.FSR3 and self._fsr3._initialized:
            self._active_backend = self._fsr3
            self._backend_type = UpscalerBackend.FSR3
            print("  ⭐ Selected: FSR 3.1")
        
        elif backend == UpscalerBackend.XESS and self._xess._initialized:
            self._active_backend = self._xess
            self._backend_type = UpscalerBackend.XESS
            print("  ⭐ Selected: XeSS 2.1")
        
        elif backend == UpscalerBackend.SOFTWARE and self._software._initialized:
            self._active_backend = self._software
            self._backend_type = UpscalerBackend.SOFTWARE
            print("  ⭐ Selected: Software")
        
        else:
            print(f"  ❌ Backend {backend.name} not available, falling back...")
            self._select_best_backend()
    
    def create_context(self,
                      input_resolution: tuple,
                      output_resolution: tuple,
                      quality_mode: QualityMode = QualityMode.QUALITY,
                      **kwargs) -> Optional[UpscalerContext]:
        """Create upscaling context
        
        Args:
            input_resolution: Input size (width, height)
            output_resolution: Output size (width, height)
            quality_mode: Quality mode
            **kwargs: Additional config options
        
        Returns:
            Context or None on error
        """
        with self._lock:
            if not self._initialized:
                print("[UniversalUpscaler] ERROR: Not initialized")
                return None
            
            if self._active_backend is None:
                print("[UniversalUpscaler] ERROR: No backend available")
                return None
            
            try:
                config = UpscalerConfig(
                    input_resolution=input_resolution,
                    output_resolution=output_resolution,
                    quality_mode=quality_mode,
                    backend=self._backend_type,
                    **kwargs
                )
                
                backend_context = self._active_backend.create_context(config)
                
                if backend_context is None:
                    print("[UniversalUpscaler] ERROR: Context creation failed")
                    return None
                
                context = UpscalerContext(
                    self._active_backend,
                    backend_context,
                    config
                )
                
                return context
            
            except Exception as e:
                print(f"[UniversalUpscaler] Context creation error: {e}")
                return None
    
    def swap_backend(self, backend: UpscalerBackend) -> bool:
        """Swap to different backend at runtime
        
        Args:
            backend: New backend
        
        Returns:
            True if successful
        """
        with self._lock:
            if not self._initialized:
                return False
            
            print(f"\n[UniversalUpscaler] Swapping backend to {backend.name}...")
            self._select_backend(backend)
            
            return self._active_backend is not None
    
    def get_active_backend(self) -> UpscalerBackend:
        """Get currently active backend"""
        return self._backend_type
    
    def get_gpu_info(self) -> dict:
        """Get GPU information"""
        if self._gpu_info is None:
            return {}
        
        return {
            'vendor': self._gpu_info.vendor.name,
            'name': self._gpu_info.name,
            'memory_mb': self._gpu_info.memory_mb,
            'driver': self._gpu_info.driver_version,
        }
    
    def shutdown(self) -> UpscalerStatus:
        """Shutdown upscaler"""
        with self._lock:
            if not self._initialized:
                return UpscalerStatus.OK
            
            try:
                # Shutdown all backends
                if self._fsr3._initialized:
                    self._fsr3.shutdown()
                
                if self._xess._initialized:
                    self._xess.shutdown()
                
                if self._software._initialized:
                    self._software.shutdown()
                
                self._active_backend = None
                self._initialized = False
                
                print("[UniversalUpscaler] Shutdown complete")
                return UpscalerStatus.OK
            
            except Exception as e:
                print(f"[UniversalUpscaler] Shutdown error: {e}")
                return UpscalerStatus.ERROR_PROCESSING_FAILED
    
    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self._initialized
