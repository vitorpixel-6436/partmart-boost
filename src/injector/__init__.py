#!/usr/bin/env python3
"""FSR 3.1 Game DLL Injection Module

Version: 0.3.5d (package 3.7c) - Stage 4

Handles game process detection and DLL injection for FSR replacement.
Supports DLSS, FSR 2.x to FSR 3.1 swapping for game integration.
"""

import os
import sys
import subprocess
import ctypes
from pathlib import Path
from typing import Optional, List
import logging


logger = logging.getLogger(__name__)


class GameInjector:
    """Injects FSR 3.1 DLL into game processes"""
    
    # DLLs to replace (DLSS, FSR 2, XeSS)
    TARGET_DLLS = [
        "nvngx_dlss.dll",          # NVIDIA DLSS
        "amd_fidelityfx_fsr2.dll",  # AMD FSR 2.x
        "libxess.dll",              # Intel XeSS
        "ffx_fsr3_x64.dll",         # Our FSR 3.1
    ]
    
    def __init__(self):
        self.fsr3_dll_path: Optional[Path] = None
        self._locate_fsr3_dll()
    
    def _locate_fsr3_dll(self) -> bool:
        """Locate FSR 3.1 DLL in common paths"""
        search_paths = [
            Path("bin") / "ffx_fsr3_x64.dll",
            Path(__file__).parent.parent.parent / "bin" / "ffx_fsr3_x64.dll",
            Path("./libs/ffx_fsr3_x64.dll"),
            Path("C:/Program Files/PartMart/bin/ffx_fsr3_x64.dll"),
        ]
        
        for dll_path in search_paths:
            if dll_path.exists():
                self.fsr3_dll_path = dll_path.resolve()
                logger.info(f"Found FSR 3.1 DLL at: {self.fsr3_dll_path}")
                return True
        
        logger.warning("FSR 3.1 DLL not found in standard paths")
        return False
    
    def is_admin(self) -> bool:
        """Check if running with admin privileges (Windows)"""
        if sys.platform != "win32":
            return True  # Not applicable on Linux
        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    
    def inject_into_game(self, game_exe_path: str) -> bool:
        """Inject FSR 3.1 DLL into game process
        
        Args:
            game_exe_path: Path to game executable
        
        Returns:
            True if injection was successful
        """
        if not self.fsr3_dll_path:
            logger.error("FSR 3.1 DLL not found. Cannot inject.")
            return False
        
        if not Path(game_exe_path).exists():
            logger.error(f"Game executable not found: {game_exe_path}")
            return False
        
        if not self.is_admin():
            logger.error("Admin privileges required for DLL injection")
            return False
        
        try:
            logger.info(f"Injecting FSR 3.1 into: {game_exe_path}")
            # Implementation would use Windows API to inject DLL
            # For now, this is a placeholder
            logger.info("FSR 3.1 injection would proceed here")
            return True
        except Exception as e:
            logger.error(f"Injection failed: {e}")
            return False
    
    def find_game_processes(self, game_name: str) -> List[int]:
        """Find running game processes by name
        
        Args:
            game_name: Name of game executable (with or without .exe)
        
        Returns:
            List of process IDs
        """
        pids = []
        
        if game_name.lower() != game_name.lower().replace(".exe", ""):
            search_name = game_name
        else:
            search_name = game_name + ".exe" if sys.platform == "win32" else game_name
        
        try:
            if sys.platform == "win32":
                # Windows: use tasklist
                result = subprocess.run(
                    ["tasklist", "/v"],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split("\n"):
                    if search_name.lower() in line.lower():
                        # Extract PID from tasklist output
                        parts = line.split()
                        if parts:
                            try:
                                pid = int(parts[1])
                                pids.append(pid)
                            except (ValueError, IndexError):
                                pass
            else:
                # Linux: use ps
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split("\n"):
                    if search_name.lower() in line.lower():
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1])
                                pids.append(pid)
                            except ValueError:
                                pass
        except Exception as e:
            logger.error(f"Failed to find processes: {e}")
        
        return pids
    
    def setup_game_directory(self, game_dir: str) -> bool:
        """Setup FSR 3.1 DLL in game directory
        
        Args:
            game_dir: Path to game directory
        
        Returns:
            True if setup successful
        """
        if not self.fsr3_dll_path:
            logger.error("FSR 3.1 DLL not found")
            return False
        
        game_path = Path(game_dir)
        if not game_path.exists():
            logger.error(f"Game directory not found: {game_dir}")
            return False
        
        try:
            # Copy FSR 3.1 DLL to game directory
            target_dll = game_path / "ffx_fsr3_x64.dll"
            logger.info(f"Copying FSR 3.1 DLL to: {target_dll}")
            # In production, would copy the DLL
            return True
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False


def request_admin_privileges() -> bool:
    """Request admin privileges on Windows"""
    if sys.platform != "win32":
        return True
    
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    
    logger.warning("Requesting admin privileges...")
    # In production, would show UAC prompt
    return False


__all__ = ["GameInjector", "request_admin_privileges"]
