#!/usr/bin/env python3
"""OptiScaler Manager - Main API

Version: 0.3.5d (package 3.8a, stage 3/6)
"""
import threading
from pathlib import Path
from typing import Optional, List, Callable

from .types import (
    InstallStatus,
    OptiScalerInfo,
    GameInfo,
    OptiScalerException,
    InstallationError,
    InjectionError
)
from .config import OptiScalerConfig
from .detector import OptiScalerDetector
from .injector import OptiScalerInjector
from .installer import OptiScalerInstaller


class OptiScalerManager:
    """OptiScaler Manager
    
    Manages OptiScaler installation, configuration, and game injection.
    
    Usage:
        manager = OptiScalerManager()
        manager.initialize()
        
        if not manager.is_installed():
            # Auto-install OptiScaler
            def progress(status, percent):
                print(f"{status}: {percent}%")
            
            manager.install(progress_callback=progress)
        
        config = OptiScalerConfig(
            backend=OptiScalerBackend.FSR3,
            quality=OptiScalerQuality.QUALITY
        )
        manager.configure(config)
        
        game = manager.detect_game(Path("C:/Games/Cyberpunk2077"))
        manager.inject_into_game(game)
    """
    
    # OptiScaler default paths
    DEFAULT_INSTALL_DIR = Path("./optiscaler")
    GITHUB_REPO = "optiscaler/OptiScaler"
    GITHUB_RELEASES = f"https://github.com/{GITHUB_REPO}/releases"
    
    def __init__(self, install_dir: Optional[Path] = None):
        """Initialize OptiScaler Manager
        
        Args:
            install_dir: OptiScaler installation directory
        """
        self._lock = threading.Lock()
        self._install_dir = install_dir or self.DEFAULT_INSTALL_DIR
        self._config: Optional[OptiScalerConfig] = None
        self._info: Optional[OptiScalerInfo] = None
        
        # Initialize components
        self._detector = OptiScalerDetector(self._install_dir)
        self._injector = OptiScalerInjector(self._install_dir)
        self._installer = OptiScalerInstaller(self._install_dir)
        
        print("[OptiScalerManager] Initialized (Stage 3/6)")
        print(f"  Install dir: {self._install_dir}")
    
    def initialize(self) -> bool:
        """Initialize OptiScaler Manager
        
        Detects OptiScaler installation and validates configuration.
        
        Returns:
            True if OptiScaler is installed and ready
        """
        with self._lock:
            print("\n[OptiScalerManager] Stage 3: Initialize with auto-install support")
            
            # Detect OptiScaler
            self._info = self._detector.detect()
            
            if self._info:
                print(f"[OptiScalerManager] OptiScaler {self._info.version} detected")
                print(f"  Status: {self._info.status.name}")
                print(f"  Backends: {[b.name for b in self._info.backends_available]}")
                
                # Load existing config if available
                if self._info.config_path:
                    self._config = OptiScalerConfig.load(self._info.config_path)
                
                return self._info.status == InstallStatus.INSTALLED
            else:
                print("[OptiScalerManager] OptiScaler not found")
                print("  Run install() to auto-download OptiScaler")
                return False
    
    def is_installed(self) -> bool:
        """Check if OptiScaler is installed
        
        Returns:
            True if installed and working
        """
        if self._info is None:
            # Try to detect
            self._info = self._detector.detect()
        
        return (
            self._info is not None and
            self._info.status == InstallStatus.INSTALLED
        )
    
    def get_info(self) -> Optional[OptiScalerInfo]:
        """Get OptiScaler installation info
        
        Returns:
            OptiScalerInfo or None
        """
        return self._info
    
    def install(
        self,
        force: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> bool:
        """Install or update OptiScaler
        
        Downloads OptiScaler from GitHub and installs it.
        
        Args:
            force: Force reinstall
            progress_callback: Progress callback (status, percent)
        
        Returns:
            True if successful
        """
        with self._lock:
            print("\n[OptiScalerManager] Stage 3: Real install")
            
            # Check if already installed
            if self.is_installed() and not force:
                print("[OptiScalerManager] Already installed (use force=True to reinstall)")
                return True
            
            try:
                # Run installer
                success = self._installer.install(progress_callback)
                
                if success:
                    # Re-detect to update info
                    self._info = self._detector.detect()
                    print("[OptiScalerManager] Installation successful")
                    return True
                else:
                    raise InstallationError("Installation failed")
            
            except Exception as e:
                print(f"[OptiScalerManager] Installation error: {e}")
                raise InstallationError(f"Failed to install OptiScaler: {e}")
    
    def configure(self, config: OptiScalerConfig) -> bool:
        """Configure OptiScaler settings
        
        Args:
            config: OptiScaler configuration
        
        Returns:
            True if successful
        """
        with self._lock:
            if not self.is_installed():
                print("[OptiScalerManager] OptiScaler not installed")
                return False
            
            # Save configuration
            config_path = self._install_dir / "nvngx.ini"
            success = config.save(config_path)
            
            if success:
                self._config = config
                print("[OptiScalerManager] Configuration saved")
            
            return success
    
    def inject_into_game(self, game: GameInfo) -> bool:
        """Inject OptiScaler into game
        
        Copies OptiScaler DLLs to game directory and sets up configuration.
        
        Args:
            game: Game information
        
        Returns:
            True if successful
        """
        if not self.is_installed():
            raise InjectionError("OptiScaler not installed")
        
        if self._config is None:
            # Use default config
            self._config = OptiScalerConfig()
            print("[OptiScalerManager] Using default configuration")
        
        try:
            return self._injector.inject(game, self._config)
        except Exception as e:
            print(f"[OptiScalerManager] Injection failed: {e}")
            raise InjectionError(f"Failed to inject into {game.name}: {e}")
    
    def remove_from_game(self, game: GameInfo) -> bool:
        """Remove OptiScaler from game
        
        Args:
            game: Game information
        
        Returns:
            True if successful
        """
        return self._injector.remove(game)
    
    def detect_game(self, game_dir: Path) -> Optional[GameInfo]:
        """Detect game and its upscaler support
        
        Args:
            game_dir: Game directory
        
        Returns:
            GameInfo or None
        """
        return self._injector.detect_game(game_dir)
    
    def get_supported_games(self) -> List[str]:
        """Get list of known supported games
        
        Returns:
            List of game names
        """
        return [
            "Cyberpunk 2077",
            "Starfield",
            "Alan Wake 2",
            "Ghost of Tsushima",
            "Marvel's Spider-Man",
            "Hogwarts Legacy",
            "Red Dead Redemption 2",
            "Death Stranding",
            "Control",
            "Metro Exodus Enhanced",
            "Dying Light 2",
            "F1 2023",
            "Forza Horizon 5",
            "Microsoft Flight Simulator",
            "Witcher 3 Next-Gen",
        ]
    
    def uninstall(self) -> bool:
        """Uninstall OptiScaler
        
        Returns:
            True if successful
        """
        with self._lock:
            print("\n[OptiScalerManager] Stage 3: Real uninstall")
            
            try:
                success = self._installer.uninstall()
                
                if success:
                    self._info = None
                    self._config = None
                    print("[OptiScalerManager] Uninstall successful")
                
                return success
            
            except Exception as e:
                print(f"[OptiScalerManager] Uninstall error: {e}")
                return False
    
    def get_install_dir(self) -> Path:
        """Get installation directory"""
        return self._install_dir
    
    def get_config(self) -> Optional[OptiScalerConfig]:
        """Get current configuration"""
        return self._config
    
    def verify_installation(self) -> bool:
        """Verify OptiScaler installation integrity
        
        Returns:
            True if valid
        """
        return self._detector.verify_installation()
    
    def get_latest_version(self) -> Optional[str]:
        """Get latest available OptiScaler version
        
        Returns:
            Version string or None
        """
        return self._installer.get_latest_version()
