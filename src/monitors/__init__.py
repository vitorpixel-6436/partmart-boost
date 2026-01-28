"""Monitoring package for GPU, CPU, and RAM

Provides modular monitoring with graceful degradation.

Usage:
    >>> from monitors import GPUMonitor, CPUMonitor, RAMMonitor
    >>> 
    >>> gpu = GPUMonitor()
    >>> cpu = CPUMonitor()
    >>> ram = RAMMonitor()
    >>> 
    >>> if gpu.is_available():
    ...     gpu_data = gpu.get_data()
    ...     print(f"GPU: {gpu_data['temp_gpu']}°C")
    >>> 
    >>> cpu_data = cpu.get_data()
    >>> ram_data = ram.get_data()
"""

from .gpu_monitor import GPUMonitor
from .cpu_monitor import CPUMonitor
from .ram_monitor import RAMMonitor

__all__ = ['GPUMonitor', 'CPUMonitor', 'RAMMonitor']
__version__ = '0.3.4'
