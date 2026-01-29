#!/usr/bin/env python3
"""Dependency Checker

Version: 0.3.5e (package 3.9a, stage 7.1/7.7)

Validate all dependencies before startup.

Package 3.9a Stage 7.1: Dependency validation.

Features:
- Check required packages
- Check optional packages
- Version compatibility
- Platform checks
"""
import sys
import importlib
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    """Dependency check result"""
    success: bool
    missing: List[str] = field(default_factory=list)
    available: List[str] = field(default_factory=list)
    optional_missing: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    versions: Dict[str, str] = field(default_factory=dict)


class DependencyChecker:
    """Dependency Checker
    
    Validates all required and optional dependencies.
    
    Required Dependencies:
    - numpy: Numerical computing
    - psutil: System monitoring
    - PyQt6: GUI framework
    - Pillow: Image processing
    - requests: HTTP requests
    - pyyaml: Configuration files
    - colorama: Terminal colors
    
    Optional Dependencies:
    - GPUtil: GPU monitoring
    - wmi: Windows Management (Windows only)
    - numba: JIT compilation (Python < 3.12)
    - typing-extensions: Type hints (Python < 3.10)
    
    Usage:
        checker = DependencyChecker()
        result = checker.check_all()
        
        if result.success:
            print("All dependencies OK")
        else:
            print(f"Missing: {result.missing}")
    """
    
    # Required packages
    REQUIRED = [
        'numpy',
        'psutil',
        'PIL',  # Pillow
        'requests',
        'yaml',  # pyyaml
        'colorama',
    ]
    
    # Optional packages
    OPTIONAL = [
        'GPUtil',
        'PyQt6',  # Can run without GUI
    ]
    
    # Platform-specific optional
    PLATFORM_SPECIFIC = {
        'win32': ['wmi'],
    }
    
    def __init__(self):
        """Initialize checker"""
        pass
    
    def check_all(self) -> CheckResult:
        """Check all dependencies
        
        Returns:
            CheckResult with status
        """
        missing = []
        available = []
        optional_missing = []
        warnings = []
        versions = {}
        
        # Check required
        for package in self.REQUIRED:
            if self._check_package(package):
                available.append(package)
                versions[package] = self._get_version(package)
            else:
                missing.append(package)
        
        # Check optional
        for package in self.OPTIONAL:
            if self._check_package(package):
                available.append(package)
                versions[package] = self._get_version(package)
            else:
                optional_missing.append(package)
        
        # Check platform-specific
        platform_packages = self.PLATFORM_SPECIFIC.get(sys.platform, [])
        for package in platform_packages:
            if not self._check_package(package):
                warnings.append(f"{package} not available (platform-specific)")
        
        # Check Python version
        if sys.version_info < (3, 8):
            warnings.append(f"Python {sys.version_info.major}.{sys.version_info.minor} not fully supported (3.8+ recommended)")
        
        # Check for PyQt6 specifically (important for UI)
        if 'PyQt6' not in available:
            warnings.append("PyQt6 not available - GUI will not work")
        
        success = len(missing) == 0
        
        return CheckResult(
            success=success,
            missing=missing,
            available=available,
            optional_missing=optional_missing,
            warnings=warnings,
            versions=versions
        )
    
    def _check_package(self, package: str) -> bool:
        """Check if package is available
        
        Args:
            package: Package name
        
        Returns:
            True if available
        """
        try:
            importlib.import_module(package)
            return True
        except ImportError:
            return False
    
    def _get_version(self, package: str) -> str:
        """Get package version
        
        Args:
            package: Package name
        
        Returns:
            Version string or 'unknown'
        """
        try:
            mod = importlib.import_module(package)
            
            # Try common version attributes
            for attr in ['__version__', 'VERSION', 'version']:
                if hasattr(mod, attr):
                    version = getattr(mod, attr)
                    if isinstance(version, str):
                        return version
                    elif isinstance(version, tuple):
                        return '.'.join(map(str, version))
            
            return 'unknown'
        
        except Exception:
            return 'unknown'
    
    def has_gui_support(self) -> bool:
        """Check if GUI is available
        
        Returns:
            True if PyQt6 available
        """
        return self._check_package('PyQt6')
    
    def has_gpu_support(self) -> bool:
        """Check if GPU monitoring available
        
        Returns:
            True if GPUtil available
        """
        return self._check_package('GPUtil')
    
    def has_wmi_support(self) -> bool:
        """Check if WMI available (Windows)
        
        Returns:
            True if wmi available
        """
        return self._check_package('wmi')
    
    def print_report(self):
        """Print dependency report"""
        result = self.check_all()
        
        print("\n" + "="*60)
        print("DEPENDENCY REPORT")
        print("="*60)
        
        print(f"\n✅ Available ({len(result.available)}):")
        for package in result.available:
            version = result.versions.get(package, 'unknown')
            print(f"   {package} ({version})")
        
        if result.missing:
            print(f"\n❌ Missing ({len(result.missing)}):")
            for package in result.missing:
                print(f"   {package}")
        
        if result.optional_missing:
            print(f"\n⚠️  Optional Missing ({len(result.optional_missing)}):")
            for package in result.optional_missing:
                print(f"   {package}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"   {warning}")
        
        print("\n" + "="*60)
        
        if result.success:
            print("✅ All required dependencies available")
        else:
            print("❌ Some dependencies missing")
            print("\nInstall missing packages:")
            print(f"   pip install {' '.join(result.missing)}")
        
        print("="*60 + "\n")


if __name__ == '__main__':
    checker = DependencyChecker()
    checker.print_report()
    
    result = checker.check_all()
    sys.exit(0 if result.success else 1)
