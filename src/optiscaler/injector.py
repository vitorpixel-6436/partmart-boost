#!/usr/bin/env python3
"""OptiScaler Game Injection System

Version: 0.3.5d (package 3.8a, stage 2/6)
"""
import shutil
import ctypes
import sys
from pathlib import Path
from typing import Optional, List

from .types import GameInfo, InjectionError
from .config import OptiScalerConfig


class OptiScalerInjector:
    """Injects OptiScaler into game directories"""
    
    # Target DLLs to replace/intercept
    TARGET_DLLS = {
        "nvngx_dlss.dll": "DLSS",       # NVIDIA DLSS
        "amd_fidelityfx_fsr2.dll": "FSR2",  # AMD FSR 2
        "libxess.dll": "XeSS",          # Intel XeSS
    }
    
    # OptiScaler files to copy
    OPTISCALER_FILES = [
        "nvngx.dll",           # Main OptiScaler
        "ffx_fsr3_x64.dll",    # FSR 3.1 backend
        "libxess.dll",         # XeSS backend (optional)
        "nvngx.ini",           # Configuration
    ]
    
    def __init__(self, optiscaler_dir: Path):
        """Initialize injector
        
        Args:
            optiscaler_dir: OptiScaler installation directory
        """
        self.optiscaler_dir = optiscaler_dir
    
    def detect_game(self, game_dir: Path) -> Optional[GameInfo]:
        """Detect game and its upscaler support
        
        Args:
            game_dir: Game installation directory
        
        Returns:
            GameInfo or None
        """
        if not game_dir.exists():
            return None
        
        # Find game executable
        exe_path = self._find_game_exe(game_dir)
        if not exe_path:
            return None
        
        # Detect upscaler support
        has_dlss = (game_dir / "nvngx_dlss.dll").exists()
        has_fsr = (game_dir / "amd_fidelityfx_fsr2.dll").exists()
        has_xess = (game_dir / "libxess.dll").exists()
        
        # Get game name from exe
        game_name = exe_path.stem
        
        game_info = GameInfo(
            name=game_name,
            exe_path=exe_path,
            game_dir=game_dir,
            has_dlss=has_dlss,
            has_fsr=has_fsr,
            has_xess=has_xess
        )
        
        print(f"[OptiScalerInjector] Detected game: {game_name}")
        print(f"  DLSS: {has_dlss}, FSR2: {has_fsr}, XeSS: {has_xess}")
        
        return game_info
    
    def _find_game_exe(self, game_dir: Path) -> Optional[Path]:
        """Find main game executable
        
        Args:
            game_dir: Game directory
        
        Returns:
            Path to exe or None
        """
        # Common exe locations
        patterns = [
            "*.exe",
            "bin/*.exe",
            "Binaries/*.exe",
            "x64/*.exe",
        ]
        
        for pattern in patterns:
            for exe_path in game_dir.glob(pattern):
                # Skip installers and launchers
                name_lower = exe_path.name.lower()
                if any(skip in name_lower for skip in ['unins', 'setup', 'launcher', 'crash']):
                    continue
                return exe_path
        
        return None
    
    def inject(self, game: GameInfo, config: OptiScalerConfig) -> bool:
        """Inject OptiScaler into game
        
        Args:
            game: Game information
            config: OptiScaler configuration
        
        Returns:
            True if successful
        """
        if not self.optiscaler_dir.exists():
            raise InjectionError("OptiScaler not installed")
        
        if not game.game_dir.exists():
            raise InjectionError(f"Game directory not found: {game.game_dir}")
        
        # Check if game supports any upscaler
        if not (game.has_dlss or game.has_fsr or game.has_xess):
            print("[OptiScalerInjector] Warning: Game may not support upscaling")
        
        print(f"[OptiScalerInjector] Injecting into {game.name}...")
        
        try:
            # Step 1: Backup original DLLs
            self._backup_original_dlls(game)
            
            # Step 2: Copy OptiScaler files
            self._copy_optiscaler_files(game)
            
            # Step 3: Write configuration
            self._write_config(game, config)
            
            print(f"[OptiScalerInjector] Successfully injected into {game.name}")
            return True
        
        except Exception as e:
            print(f"[OptiScalerInjector] Injection failed: {e}")
            raise InjectionError(f"Injection failed: {e}")
    
    def _backup_original_dlls(self, game: GameInfo):
        """Backup original upscaler DLLs
        
        Args:
            game: Game information
        """
        backup_dir = game.game_dir / "optiscaler_backup"
        backup_dir.mkdir(exist_ok=True)
        
        for dll_name in self.TARGET_DLLS.keys():
            dll_path = game.game_dir / dll_name
            if dll_path.exists():
                backup_path = backup_dir / dll_name
                if not backup_path.exists():  # Don't overwrite existing backup
                    shutil.copy2(dll_path, backup_path)
                    print(f"[OptiScalerInjector] Backed up: {dll_name}")
    
    def _copy_optiscaler_files(self, game: GameInfo):
        """Copy OptiScaler files to game directory
        
        Args:
            game: Game information
        """
        for file_name in self.OPTISCALER_FILES:
            src = self.optiscaler_dir / file_name
            dst = game.game_dir / file_name
            
            # Skip if file doesn't exist in OptiScaler dir
            if not src.exists():
                if file_name == "nvngx.ini":  # Config will be created
                    continue
                if file_name == "libxess.dll":  # Optional
                    continue
                print(f"[OptiScalerInjector] Warning: {file_name} not found in OptiScaler")
                continue
            
            try:
                shutil.copy2(src, dst)
                print(f"[OptiScalerInjector] Copied: {file_name}")
            except Exception as e:
                print(f"[OptiScalerInjector] Failed to copy {file_name}: {e}")
    
    def _write_config(self, game: GameInfo, config: OptiScalerConfig):
        """Write OptiScaler configuration
        
        Args:
            game: Game information
            config: OptiScaler configuration
        """
        config_path = game.game_dir / "nvngx.ini"
        config.save(config_path)
        print(f"[OptiScalerInjector] Configuration written: {config_path}")
    
    def remove(self, game: GameInfo) -> bool:
        """Remove OptiScaler from game
        
        Args:
            game: Game information
        
        Returns:
            True if successful
        """
        print(f"[OptiScalerInjector] Removing OptiScaler from {game.name}...")
        
        try:
            # Remove OptiScaler files
            for file_name in self.OPTISCALER_FILES:
                file_path = game.game_dir / file_name
                if file_path.exists():
                    file_path.unlink()
                    print(f"[OptiScalerInjector] Removed: {file_name}")
            
            # Restore backups
            backup_dir = game.game_dir / "optiscaler_backup"
            if backup_dir.exists():
                for backup_file in backup_dir.iterdir():
                    dst = game.game_dir / backup_file.name
                    shutil.copy2(backup_file, dst)
                    print(f"[OptiScalerInjector] Restored: {backup_file.name}")
                
                # Remove backup directory
                shutil.rmtree(backup_dir)
            
            print(f"[OptiScalerInjector] Successfully removed from {game.name}")
            return True
        
        except Exception as e:
            print(f"[OptiScalerInjector] Removal failed: {e}")
            return False
    
    @staticmethod
    def is_admin() -> bool:
        """Check if running with admin privileges
        
        Returns:
            True if admin
        """
        if sys.platform != "win32":
            return True  # Not applicable on Linux
        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
