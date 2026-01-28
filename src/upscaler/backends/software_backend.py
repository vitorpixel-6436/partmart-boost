#!/usr/bin/env python3
"""Software Fallback Backend

Version: 0.4.0-alpha

High-quality CPU-based upscaling fallback.
"""
import time
from typing import Optional
import numpy as np

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

from ..types import UpscalerStatus, FrameData, PerformanceMetrics, UpscalerBackend
from ..exceptions import UpscalerBackendError


class SoftwareBackend:
    """Software fallback backend
    
    Uses Lanczos resampling (best quality for software).
    """
    
    def __init__(self):
        self._initialized = False
        self._context = None
    
    def is_available(self) -> bool:
        """Always available"""
        return True
    
    def initialize(self) -> UpscalerStatus:
        """Initialize software backend"""
        if self._initialized:
            return UpscalerStatus.OK
        
        if not HAS_OPENCV:
            print("[Software] WARNING: OpenCV not available, using basic fallback")
        
        self._initialized = True
        print("[Software] Backend initialized (Lanczos4 upscaling)")
        return UpscalerStatus.OK
    
    def create_context(self, config) -> Optional[object]:
        """Create upscaling context"""
        if not self._initialized:
            return None
        
        print(f"[Software] Context created ({config.input_resolution} → {config.output_resolution})")
        
        self._context = {
            'config': config,
            'initialized': True
        }
        
        return self._context
    
    def upscale(self, frame_data: FrameData) -> tuple:
        """Upscale frame using software
        
        Args:
            frame_data: Input frame
        
        Returns:
            (upscaled_frame, metrics)
        """
        if not self._initialized or not self._context:
            raise UpscalerBackendError("Software backend not initialized")
        
        start = time.perf_counter()
        
        try:
            config = self._context['config']
            target = config.output_resolution
            
            if HAS_OPENCV:
                # Use Lanczos4 (best quality)
                upscaled = cv2.resize(
                    frame_data.color,
                    target,
                    interpolation=cv2.INTER_LANCZOS4
                )
                
                # Apply sharpening if enabled
                if config.enable_sharpening:
                    upscaled = self._apply_sharpening(upscaled, config.sharpness)
            
            else:
                # Basic fallback
                from scipy import ndimage
                h, w = frame_data.color.shape[:2]
                scale_y = target[1] / h
                scale_x = target[0] / w
                
                if len(frame_data.color.shape) == 3:
                    channels = []
                    for i in range(frame_data.color.shape[2]):
                        channel = ndimage.zoom(
                            frame_data.color[:, :, i],
                            (scale_y, scale_x),
                            order=3
                        )
                        channels.append(channel)
                    upscaled = np.stack(channels, axis=2).astype(np.uint8)
                else:
                    upscaled = ndimage.zoom(
                        frame_data.color,
                        (scale_y, scale_x),
                        order=3
                    ).astype(np.uint8)
            
            elapsed = (time.perf_counter() - start) * 1000
            
            metrics = PerformanceMetrics(
                backend=UpscalerBackend.SOFTWARE,
                upscale_time_ms=elapsed,
                total_time_ms=elapsed,
                memory_used_mb=upscaled.nbytes / (1024*1024),
                fps=1000.0/elapsed if elapsed > 0 else 0
            )
            
            return upscaled, metrics
        
        except Exception as e:
            print(f"[Software] Upscale error: {e}")
            raise UpscalerBackendError(f"Software upscale failed: {e}")
    
    def _apply_sharpening(self, frame: np.ndarray, strength: float) -> np.ndarray:
        """Apply unsharp mask sharpening"""
        if not HAS_OPENCV or strength < 0.01:
            return frame
        
        blurred = cv2.GaussianBlur(frame, (0, 0), 2.0)
        sharpened = cv2.addWeighted(
            frame, 1.0 + strength,
            blurred, -strength,
            0
        )
        
        return np.clip(sharpened, 0, 255).astype(np.uint8)
    
    def shutdown(self) -> UpscalerStatus:
        """Shutdown software backend"""
        if not self._initialized:
            return UpscalerStatus.OK
        
        self._context = None
        self._initialized = False
        print("[Software] Backend shutdown")
        return UpscalerStatus.OK
