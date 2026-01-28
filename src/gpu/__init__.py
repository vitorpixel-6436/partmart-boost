"""
GPU Optimization Module

Supported vendors:
- NVIDIA (GTX 10xx - RTX 40xx)
- AMD (RX 5xx - RX 7xxx)
- Intel Arc
"""

from src.gpu.nvidia_control import NVIDIAControl
from src.gpu.amd_control import AMDControl

__all__ = ['NVIDIAControl', 'AMDControl']
