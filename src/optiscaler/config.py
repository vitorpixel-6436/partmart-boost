#!/usr/bin/env python3
"""OptiScaler Configuration Management

Version: 0.3.5d (package 3.8a, stage 1/6)
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

from .types import OptiScalerBackend, OptiScalerQuality, ConfigurationError


@dataclass
class OptiScalerConfig:
    """OptiScaler configuration
    
    Matches OptiScaler's nvngx.ini format.
    
    Attributes:
        backend: Upscaling backend (FSR3/XeSS/DLSS)
        quality: Quality mode
        sharpness: Sharpness level (0.0-1.0)
        enable_frame_gen: Enable frame generation
        enable_hud_fix: Enable HUD position fix
        enable_overlay: Enable performance overlay
        output_scaling: Output scaling (0.5-2.0)
        mip_bias: Mipmap bias adjustment
    """
    backend: OptiScalerBackend = OptiScalerBackend.AUTO
    quality: OptiScalerQuality = OptiScalerQuality.QUALITY
    sharpness: float = 0.5
    enable_frame_gen: bool = False
    enable_hud_fix: bool = True
    enable_overlay: bool = False
    output_scaling: float = 1.0
    mip_bias: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptiScalerConfig':
        """Create from dictionary"""
        return cls(**data)
    
    def to_nvngx_ini(self) -> str:
        """Convert to OptiScaler nvngx.ini format
        
        Returns:
            INI format string
        """
        # Map our enums to OptiScaler values
        backend_map = {
            OptiScalerBackend.FSR3: "fsr31",
            OptiScalerBackend.XESS: "xess",
            OptiScalerBackend.DLSS: "dlss",
            OptiScalerBackend.AUTO: "auto"
        }
        
        quality_map = {
            OptiScalerQuality.PERFORMANCE: "performance",
            OptiScalerQuality.BALANCED: "balanced",
            OptiScalerQuality.QUALITY: "quality",
            OptiScalerQuality.ULTRA_QUALITY: "ultra_quality",
            OptiScalerQuality.NATIVE: "native"
        }
        
        ini_content = f"""
[Upscaler]
UpscalerMode={backend_map[self.backend]}
QualityMode={quality_map[self.quality]}
Sharpness={self.sharpness}

[FrameGeneration]
Enabled={str(self.enable_frame_gen).lower()}

[UI]
HUDFix={str(self.enable_hud_fix).lower()}
Overlay={str(self.enable_overlay).lower()}

[Advanced]
OutputScaling={self.output_scaling}
MipBias={self.mip_bias}
"""
        return ini_content.strip()
    
    @classmethod
    def from_nvngx_ini(cls, ini_content: str) -> 'OptiScalerConfig':
        """Parse from OptiScaler nvngx.ini format
        
        Args:
            ini_content: INI format string
        
        Returns:
            OptiScalerConfig instance
        """
        # Reverse maps
        backend_map = {
            "fsr31": OptiScalerBackend.FSR3,
            "xess": OptiScalerBackend.XESS,
            "dlss": OptiScalerBackend.DLSS,
            "auto": OptiScalerBackend.AUTO
        }
        
        quality_map = {
            "performance": OptiScalerQuality.PERFORMANCE,
            "balanced": OptiScalerQuality.BALANCED,
            "quality": OptiScalerQuality.QUALITY,
            "ultra_quality": OptiScalerQuality.ULTRA_QUALITY,
            "native": OptiScalerQuality.NATIVE
        }
        
        # Simple INI parser
        config = cls()
        current_section = None
        
        for line in ini_content.split('\n'):
            line = line.strip()
            
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().lower()
                
                # Parse values
                if key == "UpscalerMode":
                    config.backend = backend_map.get(value, OptiScalerBackend.AUTO)
                elif key == "QualityMode":
                    config.quality = quality_map.get(value, OptiScalerQuality.QUALITY)
                elif key == "Sharpness":
                    config.sharpness = float(value)
                elif key == "Enabled" and current_section == "FrameGeneration":
                    config.enable_frame_gen = value == "true"
                elif key == "HUDFix":
                    config.enable_hud_fix = value == "true"
                elif key == "Overlay":
                    config.enable_overlay = value == "true"
                elif key == "OutputScaling":
                    config.output_scaling = float(value)
                elif key == "MipBias":
                    config.mip_bias = float(value)
        
        return config
    
    def save(self, path: Path) -> bool:
        """Save configuration to file
        
        Args:
            path: Path to save (nvngx.ini)
        
        Returns:
            True if successful
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self.to_nvngx_ini())
            print(f"[OptiScalerConfig] Saved to: {path}")
            return True
        except Exception as e:
            print(f"[OptiScalerConfig] Save error: {e}")
            return False
    
    @classmethod
    def load(cls, path: Path) -> Optional['OptiScalerConfig']:
        """Load configuration from file
        
        Args:
            path: Path to load (nvngx.ini)
        
        Returns:
            OptiScalerConfig or None if not found
        """
        try:
            if not path.exists():
                print(f"[OptiScalerConfig] File not found: {path}")
                return None
            
            ini_content = path.read_text()
            config = cls.from_nvngx_ini(ini_content)
            print(f"[OptiScalerConfig] Loaded from: {path}")
            return config
        except Exception as e:
            print(f"[OptiScalerConfig] Load error: {e}")
            return None
