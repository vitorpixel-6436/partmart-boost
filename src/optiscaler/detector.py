#!/usr/bin/env python3
"""OptiScaler Detection System

Version: 0.3.5d (package 3.8a, stage 2/6)
"""
import re
from pathlib import Path
from typing import Optional, List

from .types import (
    InstallStatus,
    OptiScalerInfo,
    OptiScalerBackend
)


class OptiScalerDetector:
    """Detects OptiScaler installation and configuration"""
    
    # Required files for OptiScaler
    REQUIRED_FILES = [
        "nvngx.dll",           # Main OptiScaler DLL
        "version.txt",         # Version info (optional)
    ]
    
    # Backend DLL files
    BACKEND_FILES = {
        OptiScalerBackend.FSR3: ["ffx_fsr3_x64.dll", "libffx_fsr31.dll"],
        OptiScalerBackend.XESS: ["libxess.dll", "xess.dll"],
        OptiScalerBackend.DLSS: ["nvngx_dlss.dll"],
    }
    
    def __init__(self, install_dir: Path):
        """Initialize detector
        
        Args:
            install_dir: OptiScaler installation directory
        """
        self.install_dir = install_dir
    
    def detect(self) -> Optional[OptiScalerInfo]:
        """Detect OptiScaler installation
        
        Returns:
            OptiScalerInfo or None if not found
        """
        if not self.install_dir.exists():
            print(f"[OptiScalerDetector] Directory not found: {self.install_dir}")
            return None
        
        # Check for main DLL
        main_dll = self.install_dir / "nvngx.dll"
        if not main_dll.exists():
            print("[OptiScalerDetector] Main DLL (nvngx.dll) not found")
            return None
        
        # Get version
        version = self._detect_version()
        
        # Check available backends
        backends = self._detect_backends()
        
        # Get config path
        config_path = self.install_dir / "nvngx.ini"
        if not config_path.exists():
            config_path = None
        
        # Determine status
        status = self._determine_status()
        
        info = OptiScalerInfo(
            version=version,
            install_path=self.install_dir,
            status=status,
            backends_available=backends,
            config_path=config_path
        )
        
        print(f"[OptiScalerDetector] Detected OptiScaler {version}")
        print(f"  Backends: {[b.name for b in backends]}")
        print(f"  Status: {status.name}")
        
        return info
    
    def _detect_version(self) -> str:
        """Detect OptiScaler version
        
        Returns:
            Version string
        """
        # Try version.txt
        version_file = self.install_dir / "version.txt"
        if version_file.exists():
            try:
                content = version_file.read_text().strip()
                # Extract version number (e.g., "0.7.1")
                match = re.search(r'(\d+\.\d+\.\d+)', content)
                if match:
                    return match.group(1)
            except Exception as e:
                print(f"[OptiScalerDetector] Version read error: {e}")
        
        # Try README.md
        readme = self.install_dir / "README.md"
        if readme.exists():
            try:
                content = readme.read_text()
                match = re.search(r'version\s+(\d+\.\d+\.\d+)', content, re.IGNORECASE)
                if match:
                    return match.group(1)
            except Exception:
                pass
        
        # Default unknown
        return "unknown"
    
    def _detect_backends(self) -> List[OptiScalerBackend]:
        """Detect available backends
        
        Returns:
            List of available backends
        """
        backends = []
        
        for backend, dll_names in self.BACKEND_FILES.items():
            for dll_name in dll_names:
                dll_path = self.install_dir / dll_name
                if dll_path.exists():
                    backends.append(backend)
                    print(f"[OptiScalerDetector] Found {backend.name}: {dll_name}")
                    break
        
        return backends
    
    def _determine_status(self) -> InstallStatus:
        """Determine installation status
        
        Returns:
            InstallStatus
        """
        # Check main DLL
        main_dll = self.install_dir / "nvngx.dll"
        if not main_dll.exists():
            return InstallStatus.NOT_INSTALLED
        
        # Check file size (corrupted if too small)
        try:
            size = main_dll.stat().st_size
            if size < 1024:  # Less than 1KB = corrupted
                return InstallStatus.CORRUPTED
        except Exception:
            return InstallStatus.CORRUPTED
        
        # Check if any backend available
        backends = self._detect_backends()
        if not backends:
            print("[OptiScalerDetector] No backend DLLs found")
            return InstallStatus.CORRUPTED
        
        return InstallStatus.INSTALLED
    
    def verify_installation(self) -> bool:
        """Verify OptiScaler installation integrity
        
        Returns:
            True if valid
        """
        info = self.detect()
        if not info:
            return False
        
        return info.status == InstallStatus.INSTALLED
