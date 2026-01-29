#!/usr/bin/env python3
"""DLL Injector - Safe DLL injection for Windows games

Version: 0.3.5d (package 3.9a, stage 7.7c)

Real DLL injection using Windows API.
NO STUBS - actual DLL injection (Windows only)!

WARNING: DLL injection may trigger anti-cheat systems.
Use only with single-player games or games that allow modifications.
"""
import os
import sys
from typing import Optional
from pathlib import Path

# Windows-specific imports
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    WINDOWS_AVAILABLE = True
else:
    WINDOWS_AVAILABLE = False
    ctypes = None
    wintypes = None


class DLLInjector:
    """DLL injection system for Windows
    
    Provides safe DLL injection into game processes.
    Uses CreateRemoteThread technique.
    
    v0.3.5d - Stage 7.7c: Real implementation
    
    IMPORTANT:
    - Windows only
    - Requires administrator privileges
    - May trigger anti-cheat systems
    - Use responsibly!
    """
    
    def __init__(self):
        self.name = "DLLInjector"
        
        if not WINDOWS_AVAILABLE:
            print("Warning: DLL injection only available on Windows")
            return
        
        # Windows API constants
        self.PROCESS_ALL_ACCESS = 0x1F0FFF
        self.MEM_COMMIT = 0x1000
        self.MEM_RESERVE = 0x2000
        self.PAGE_READWRITE = 0x04
        
        # Load Windows API functions
        self.kernel32 = ctypes.windll.kernel32
    
    def inject_dll(self, process_id: int, dll_path: str) -> bool:
        """Inject DLL into target process
        
        Args:
            process_id: Target process ID
            dll_path: Full path to DLL file
        
        Returns:
            True if injection successful
        """
        if not WINDOWS_AVAILABLE:
            print("DLL injection not available on this platform")
            return False
        
        try:
            # Validate DLL path
            dll_path_full = os.path.abspath(dll_path)
            if not os.path.exists(dll_path_full):
                print(f"DLL not found: {dll_path_full}")
                return False
            
            # Open target process
            h_process = self.kernel32.OpenProcess(
                self.PROCESS_ALL_ACCESS,
                False,
                process_id
            )
            
            if not h_process:
                print(f"Failed to open process {process_id}. Admin rights required.")
                return False
            
            try:
                # Allocate memory in target process
                dll_path_bytes = dll_path_full.encode('utf-8') + b'\x00'
                dll_path_len = len(dll_path_bytes)
                
                arg_address = self.kernel32.VirtualAllocEx(
                    h_process,
                    None,
                    dll_path_len,
                    self.MEM_COMMIT | self.MEM_RESERVE,
                    self.PAGE_READWRITE
                )
                
                if not arg_address:
                    print("Failed to allocate memory in target process")
                    return False
                
                # Write DLL path to target process memory
                written = ctypes.c_size_t(0)
                if not self.kernel32.WriteProcessMemory(
                    h_process,
                    arg_address,
                    dll_path_bytes,
                    dll_path_len,
                    ctypes.byref(written)
                ):
                    print("Failed to write to target process memory")
                    return False
                
                # Get LoadLibraryA address
                h_kernel32 = self.kernel32.GetModuleHandleW('kernel32.dll')
                load_library_addr = self.kernel32.GetProcAddress(
                    h_kernel32,
                    b'LoadLibraryA'
                )
                
                if not load_library_addr:
                    print("Failed to get LoadLibraryA address")
                    return False
                
                # Create remote thread to load DLL
                h_thread = self.kernel32.CreateRemoteThread(
                    h_process,
                    None,
                    0,
                    load_library_addr,
                    arg_address,
                    0,
                    None
                )
                
                if not h_thread:
                    print("Failed to create remote thread")
                    return False
                
                # Wait for thread completion
                self.kernel32.WaitForSingleObject(h_thread, -1)
                
                # Get thread exit code (module handle)
                exit_code = wintypes.DWORD()
                self.kernel32.GetExitCodeThread(
                    h_thread,
                    ctypes.byref(exit_code)
                )
                
                # Cleanup
                self.kernel32.CloseHandle(h_thread)
                self.kernel32.VirtualFreeEx(
                    h_process,
                    arg_address,
                    0,
                    0x8000  # MEM_RELEASE
                )
                
                if exit_code.value == 0:
                    print("DLL injection failed (LoadLibrary returned NULL)")
                    return False
                
                print(f"Successfully injected: {dll_path}")
                print(f"  Process ID: {process_id}")
                print(f"  Module Handle: 0x{exit_code.value:X}")
                return True
            
            finally:
                self.kernel32.CloseHandle(h_process)
        
        except Exception as e:
            print(f"Error during DLL injection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def is_admin(self) -> bool:
        """Check if running with administrator privileges"""
        if not WINDOWS_AVAILABLE:
            return False
        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def check_health(self) -> dict:
        """Check injector health"""
        if not WINDOWS_AVAILABLE:
            return {
                'status': 'error',
                'message': 'DLL injection only available on Windows'
            }
        
        if not self.is_admin():
            return {
                'status': 'warning',
                'message': 'Administrator privileges required for DLL injection'
            }
        
        return {
            'status': 'healthy',
            'message': 'DLL injector ready (admin mode)'
        }


# Singleton instance
_dll_injector = None

def get_dll_injector() -> DLLInjector:
    """Get singleton DLL injector instance"""
    global _dll_injector
    if _dll_injector is None:
        _dll_injector = DLLInjector()
    return _dll_injector


if __name__ == '__main__':
    # Test DLL Injector
    print("Testing DLL Injector...\n")
    
    injector = DLLInjector()
    
    if not WINDOWS_AVAILABLE:
        print("❌ DLL injection only available on Windows")
        sys.exit(1)
    
    # Check admin
    print(f"Administrator: {'Yes' if injector.is_admin() else 'No'}")
    if not injector.is_admin():
        print("⚠️  Administrator privileges required for DLL injection")
        print("   Run this script as administrator to test injection")
    
    # Health check
    print("\nHealth check:")
    health = injector.check_health()
    print(f"  Status: {health['status']}")
    print(f"  Message: {health['message']}")
    
    print("\nℹ️  DLL Injector ready")
    print("   Usage: injector.inject_dll(process_id, 'path/to/dll')")
    print("\n⚠️  WARNING: DLL injection may trigger anti-cheat systems!")
    print("   Use only with single-player games or games that allow mods.")
    
    print("\n✅ DLL Injector test complete!")
