#!/usr/bin/env python3
"""GPU Detection System

Version: 0.4.0-alpha

Detects GPU vendor and capabilities.
"""
import platform
import subprocess
from typing import Optional, Dict
from enum import IntEnum


class GPUVendor(IntEnum):
    """GPU vendors"""
    UNKNOWN = 0
    NVIDIA = 1
    AMD = 2
    INTEL = 3


class GPUInfo:
    """GPU information"""
    
    def __init__(self):
        self.vendor = GPUVendor.UNKNOWN
        self.name = "Unknown"
        self.memory_mb = 0
        self.driver_version = ""
        self.supports_fsr = False
        self.supports_xess = False
    
    def __repr__(self):
        return f"GPU({self.vendor.name}: {self.name}, {self.memory_mb}MB)"


def detect_gpu() -> GPUInfo:
    """Detect GPU information
    
    Returns:
        GPUInfo object with detection results
    """
    info = GPUInfo()
    
    # Try multiple detection methods
    _detect_nvidia(info)
    if info.vendor == GPUVendor.UNKNOWN:
        _detect_amd(info)
    if info.vendor == GPUVendor.UNKNOWN:
        _detect_intel(info)
    
    # Determine backend support
    _check_backend_support(info)
    
    return info


def _detect_nvidia(info: GPUInfo):
    """Detect NVIDIA GPU using nvidia-smi"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0 and result.stdout:
            parts = result.stdout.strip().split(',')
            if len(parts) >= 3:
                info.vendor = GPUVendor.NVIDIA
                info.name = parts[0].strip()
                info.memory_mb = int(parts[1].strip().split()[0])
                info.driver_version = parts[2].strip()
                print(f"[GPU Detector] NVIDIA GPU detected: {info.name}")
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        pass


def _detect_amd(info: GPUInfo):
    """Detect AMD GPU"""
    # Try rocm-smi (Linux)
    try:
        result = subprocess.run(
            ['rocm-smi', '--showproductname'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0 and 'GPU' in result.stdout:
            info.vendor = GPUVendor.AMD
            # Parse output
            for line in result.stdout.split('\n'):
                if 'Card series' in line:
                    info.name = line.split(':')[1].strip()
                    break
            if not info.name:
                info.name = "AMD Radeon"
            print(f"[GPU Detector] AMD GPU detected: {info.name}")
            return
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    # Fallback: check for AMD in system info
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'path', 'win32_videocontroller', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    lower = line.lower()
                    if 'radeon' in lower or 'amd' in lower:
                        info.vendor = GPUVendor.AMD
                        info.name = line.strip()
                        print(f"[GPU Detector] AMD GPU detected: {info.name}")
                        return
    except Exception:
        pass


def _detect_intel(info: GPUInfo):
    """Detect Intel GPU"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'path', 'win32_videocontroller', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    lower = line.lower()
                    if 'intel' in lower or 'arc' in lower or 'iris' in lower:
                        info.vendor = GPUVendor.INTEL
                        info.name = line.strip()
                        print(f"[GPU Detector] Intel GPU detected: {info.name}")
                        return
    except Exception:
        pass


def _check_backend_support(info: GPUInfo):
    """Check which backends are supported"""
    # FSR 3.1 - works on all GPUs
    info.supports_fsr = True
    
    # XeSS 2.1 - works on all GPUs (better on Intel)
    info.supports_xess = True
    
    # Note: Actual support depends on DLL availability


if __name__ == "__main__":
    print("="*60)
    print("GPU Detection Test")
    print("="*60)
    
    gpu = detect_gpu()
    print(f"\nDetected GPU:")
    print(f"  Vendor: {gpu.vendor.name}")
    print(f"  Name: {gpu.name}")
    print(f"  Memory: {gpu.memory_mb} MB")
    print(f"  Driver: {gpu.driver_version}")
    print(f"\nBackend Support:")
    print(f"  FSR 3.1: {'✅' if gpu.supports_fsr else '❌'}")
    print(f"  XeSS 2.1: {'✅' if gpu.supports_xess else '❌'}")
