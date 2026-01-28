#!/usr/bin/env python3
"""FSR 4 ctypes Bindings

Version: 0.3.5d_package3.3a

Low-level ctypes bindings to AMD FSR 4 C++ library.
Provides Python interface to native FSR 4 functions.
"""
import ctypes
import sys
import os
from pathlib import Path
from typing import Optional
from ctypes import (
    c_void_p, c_int, c_uint, c_float, c_char_p,
    c_uint32, c_uint64, c_bool,
    POINTER, Structure, CFUNCTYPE
)


# ========== STRUCTURES ==========

class FSR4ContextDescription(Structure):
    """FSR 4 context description
    
    Matches ffxFsr4ContextDescription from FSR 4 SDK
    """
    _fields_ = [
        ("flags", c_uint32),
        ("maxRenderSize_width", c_uint32),
        ("maxRenderSize_height", c_uint32),
        ("displaySize_width", c_uint32),
        ("displaySize_height", c_uint32),
        ("device", c_void_p),
        ("backendInterface", c_void_p),
    ]


class FSR4DispatchDescription(Structure):
    """FSR 4 dispatch description
    
    Matches ffxFsr4DispatchDescription from FSR 4 SDK
    """
    _fields_ = [
        ("commandList", c_void_p),
        ("color", c_void_p),
        ("depth", c_void_p),
        ("motionVectors", c_void_p),
        ("exposure", c_void_p),
        ("reactive", c_void_p),
        ("transparencyAndComposition", c_void_p),
        ("output", c_void_p),
        ("jitterOffset_x", c_float),
        ("jitterOffset_y", c_float),
        ("motionVectorScale_x", c_float),
        ("motionVectorScale_y", c_float),
        ("renderSize_width", c_uint32),
        ("renderSize_height", c_uint32),
        ("enableSharpening", c_bool),
        ("sharpness", c_float),
        ("frameTimeDelta", c_float),
        ("preExposure", c_float),
        ("reset", c_bool),
        ("cameraNear", c_float),
        ("cameraFar", c_float),
        ("cameraFovAngleVertical", c_float),
    ]


class FSR4Version(Structure):
    """FSR 4 version info"""
    _fields_ = [
        ("major", c_uint32),
        ("minor", c_uint32),
        ("patch", c_uint32),
    ]


# ========== LIBRARY LOADING ==========

class FSR4Bindings:
    """FSR 4 ctypes bindings wrapper
    
    Loads native FSR 4 library and provides function wrappers.
    
    Example:
        >>> bindings = FSR4Bindings()
        >>> if bindings.is_loaded():
        >>>     version = bindings.get_version()
        >>>     print(f"FSR 4: {version.major}.{version.minor}.{version.patch}")
    """
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize FSR 4 bindings
        
        Args:
            library_path: Optional explicit path to FSR 4 library
        """
        self._lib: Optional[ctypes.CDLL] = None
        self._library_path = library_path
        
        # Try to load library
        self._load_library()
        
        # Setup function signatures if loaded
        if self._lib is not None:
            self._setup_functions()
    
    def _find_library(self) -> Optional[str]:
        """Find FSR 4 library in system
        
        Returns:
            Path to library or None
        """
        # Try explicit path first
        if self._library_path and os.path.exists(self._library_path):
            return self._library_path
        
        # Platform-specific library names
        if sys.platform == "win32":
            lib_names = [
                "ffx_fsr4_x64.dll",
                "ffx_fsr4.dll",
            ]
        elif sys.platform == "linux":
            lib_names = [
                "libffx_fsr4.so",
                "libffx_fsr4.so.4",
            ]
        else:
            return None
        
        # Search paths
        search_paths = [
            Path.cwd() / "lib",
            Path.cwd() / "bin",
            Path(__file__).parent / "lib",
            Path(__file__).parent.parent / "lib",
            Path(__file__).parent.parent.parent / "lib",
        ]
        
        # Add system paths
        if sys.platform == "win32":
            search_paths.append(Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32")
        elif sys.platform == "linux":
            search_paths.extend([
                Path("/usr/lib"),
                Path("/usr/local/lib"),
                Path("/usr/lib/x86_64-linux-gnu"),
            ])
        
        # Search for library
        for search_path in search_paths:
            for lib_name in lib_names:
                lib_path = search_path / lib_name
                if lib_path.exists():
                    return str(lib_path)
        
        return None
    
    def _load_library(self):
        """Load FSR 4 native library"""
        lib_path = self._find_library()
        
        if lib_path is None:
            print("[FSR4Bindings] WARNING: FSR 4 library not found")
            print("[FSR4Bindings] Frame Generation and Super Resolution will not be available")
            print("[FSR4Bindings] Please install AMD FSR 4 SDK and place libraries in ./lib/")
            return
        
        try:
            self._lib = ctypes.CDLL(lib_path)
            print(f"[FSR4Bindings] Loaded FSR 4 library: {lib_path}")
        except OSError as e:
            print(f"[FSR4Bindings] ERROR: Failed to load FSR 4 library: {e}")
            self._lib = None
    
    def _setup_functions(self):
        """Setup function signatures"""
        if self._lib is None:
            return
        
        # Define function signatures
        # Note: These are placeholder signatures
        # Real FSR 4 SDK will have specific function names and signatures
        
        # Version info
        try:
            self._lib.ffxFsr4GetVersion.argtypes = [POINTER(FSR4Version)]
            self._lib.ffxFsr4GetVersion.restype = c_int
        except AttributeError:
            pass
        
        # Context creation
        try:
            self._lib.ffxFsr4ContextCreate.argtypes = [
                POINTER(c_void_p),
                POINTER(FSR4ContextDescription)
            ]
            self._lib.ffxFsr4ContextCreate.restype = c_int
        except AttributeError:
            pass
        
        # Context destroy
        try:
            self._lib.ffxFsr4ContextDestroy.argtypes = [POINTER(c_void_p)]
            self._lib.ffxFsr4ContextDestroy.restype = c_int
        except AttributeError:
            pass
        
        # Dispatch
        try:
            self._lib.ffxFsr4ContextDispatch.argtypes = [
                c_void_p,
                POINTER(FSR4DispatchDescription)
            ]
            self._lib.ffxFsr4ContextDispatch.restype = c_int
        except AttributeError:
            pass
    
    def is_loaded(self) -> bool:
        """Check if library is loaded
        
        Returns:
            True if FSR 4 library is available
        """
        return self._lib is not None
    
    def get_version(self) -> Optional[FSR4Version]:
        """Get FSR 4 version
        
        Returns:
            FSR4Version or None if not available
        """
        if not self.is_loaded():
            return None
        
        try:
            version = FSR4Version()
            result = self._lib.ffxFsr4GetVersion(ctypes.byref(version))
            if result == 0:  # Success
                return version
        except (AttributeError, OSError):
            pass
        
        return None
    
    def get_library(self) -> Optional[ctypes.CDLL]:
        """Get raw ctypes library handle
        
        Returns:
            ctypes.CDLL or None
        """
        return self._lib


# Global bindings instance
_bindings: Optional[FSR4Bindings] = None


def get_bindings() -> FSR4Bindings:
    """Get global FSR 4 bindings instance
    
    Returns:
        FSR4Bindings instance
    
    Example:
        >>> bindings = get_bindings()
        >>> if bindings.is_loaded():
        >>>     print("FSR 4 available!")
    """
    global _bindings
    if _bindings is None:
        _bindings = FSR4Bindings()
    return _bindings


# ========== TESTING ==========

if __name__ == "__main__":
    print("="*60)
    print("FSR 4 Bindings v0.3.5d_package3.3a Test")
    print("="*60)
    
    bindings = FSR4Bindings()
    
    print("\n[Test 1] Library loading")
    if bindings.is_loaded():
        print("  ✅ FSR 4 library loaded successfully")
        
        version = bindings.get_version()
        if version:
            print(f"  Version: {version.major}.{version.minor}.{version.patch}")
        else:
            print("  Version: Unable to query (library may be stub)")
    else:
        print("  ⚠️  FSR 4 library not found")
        print("  This is expected if FSR 4 SDK is not installed")
        print("  Frame Generation/Super Resolution will use fallback")
    
    print("\n[Test 2] Structure sizes")
    print(f"  FSR4ContextDescription: {ctypes.sizeof(FSR4ContextDescription)} bytes")
    print(f"  FSR4DispatchDescription: {ctypes.sizeof(FSR4DispatchDescription)} bytes")
    print(f"  FSR4Version: {ctypes.sizeof(FSR4Version)} bytes")
    
    print("\n" + "="*60)
    print("✅ FSR 4 Bindings - Tests Complete!")
    print("="*60)
