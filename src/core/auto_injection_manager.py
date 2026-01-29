#!/usr/bin/env python3
"""Auto Injection Manager - Automatic FSR injection on game detection

Version: 0.3.5d (package 3.9a, stage 7.7d)

Automatically injects FSR when supported games are detected.
"""
import time
import threading
from typing import Dict, Optional, Callable
from pathlib import Path

try:
    from core.game_detector import GameProcess
except ImportError:
    GameProcess = None

try:
    from core.game_profile_manager import (
        get_profile_manager, GameProfile, AutoInjectMode
    )
except ImportError:
    get_profile_manager = None
    GameProfile = None
    AutoInjectMode = None

try:
    from core.fsr_manager import get_fsr_manager
except ImportError:
    get_fsr_manager = None

try:
    from core.dll_injector import get_dll_injector
except ImportError:
    get_dll_injector = None


class AutoInjectionManager:
    """Automatic FSR injection system
    
    Monitors for game detection events and automatically injects FSR
    based on game profiles and user preferences.
    
    v0.3.5d - Stage 7.7d: Auto-injection system
    """
    
    def __init__(self):
        self.name = "AutoInjectionManager"
        
        # Managers
        self.profile_manager = None
        self.fsr_manager = None
        self.dll_injector = None
        
        if get_profile_manager:
            self.profile_manager = get_profile_manager()
        if get_fsr_manager:
            self.fsr_manager = get_fsr_manager()
        if get_dll_injector:
            self.dll_injector = get_dll_injector()
        
        # Injection tracking
        self._injected_pids: Dict[int, str] = {}  # pid -> game_name
        self._injection_threads: Dict[int, threading.Thread] = {}
        
        # Callbacks
        self._callbacks: list[Callable] = []
    
    def handle_game_detected(self, game: GameProcess) -> bool:
        """Handle game detection event
        
        Args:
            game: Detected game process
        
        Returns:
            True if injection initiated
        """
        if not all([self.profile_manager, self.fsr_manager, self.dll_injector]):
            return False
        
        # Check if already injected
        if game.pid in self._injected_pids:
            return False
        
        # Get profile by executable name
        profile = self.profile_manager.get_profile_by_executable(game.name)
        
        if not profile:
            # Create default profile
            print(f"Creating default profile for {game.display_name}")
            profile = self.profile_manager.create_default_profile(
                game_name=game.name.replace('.exe', ''),
                executable=game.name
            )
        
        # Check auto-inject setting
        if profile.auto_inject == AutoInjectMode.DISABLED:
            print(f"Auto-injection disabled for {game.display_name}")
            return False
        
        if profile.auto_inject == AutoInjectMode.ASK:
            # TODO: Show dialog to user
            print(f"Auto-injection: ASK mode for {game.display_name}")
            print("   (Dialog not implemented yet - defaulting to AUTO)")
            # For now, treat as AUTO
        
        # Check if FSR is enabled
        if not profile.fsr_enabled:
            print(f"FSR disabled for {game.display_name}")
            return False
        
        # Schedule injection with delay
        delay = profile.auto_inject_delay
        print(f"Scheduling FSR injection for {game.display_name} in {delay}s...")
        
        thread = threading.Thread(
            target=self._inject_with_delay,
            args=(game, profile, delay),
            daemon=True
        )
        thread.start()
        self._injection_threads[game.pid] = thread
        
        return True
    
    def _inject_with_delay(self, game: GameProcess, profile: GameProfile, delay: float):
        """Inject FSR after delay
        
        Args:
            game: Game process
            profile: Game profile
            delay: Delay in seconds
        """
        try:
            # Wait for delay
            time.sleep(delay)
            
            # Check if game is still running
            import psutil
            if not psutil.pid_exists(game.pid):
                print(f"Game {game.display_name} closed before injection")
                return
            
            # Perform injection
            success = self._perform_injection(game, profile)
            
            if success:
                self._injected_pids[game.pid] = profile.game_name
                self._notify_callbacks('injected', game, profile)
                print(f"\u2705 FSR injected successfully into {game.display_name}")
            else:
                print(f"\u274c FSR injection failed for {game.display_name}")
                self._notify_callbacks('failed', game, profile)
        
        except Exception as e:
            print(f"Error during injection: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup thread
            if game.pid in self._injection_threads:
                del self._injection_threads[game.pid]
    
    def _perform_injection(self, game: GameProcess, profile: GameProfile) -> bool:
        """Perform actual FSR injection
        
        Args:
            game: Game process
            profile: Game profile
        
        Returns:
            True if successful
        """
        try:
            # Get game directory
            game_dir = Path(game.exe_path).parent if game.exe_path else None
            if not game_dir or not game_dir.exists():
                print(f"Game directory not found: {game.exe_path}")
                return False
            
            # Load FSR config from profile
            if not profile.fsr_config:
                print("No FSR config in profile")
                return False
            
            # Reconstruct FSR config
            from core.fsr_manager import FSRConfig, FSRVersion, FSRPreset
            fsr_config = FSRConfig(
                version=FSRVersion(profile.fsr_config.get('version', '3.1')),
                preset=FSRPreset(profile.fsr_config.get('preset', 'quality')),
                render_scale=profile.fsr_config.get('render_scale', 0.67),
                sharpness=profile.fsr_config.get('sharpness', 0.5),
                enabled=profile.fsr_config.get('enabled', True),
                dx11_mode=profile.fsr_config.get('dx11_mode', False),
                dx12_mode=profile.fsr_config.get('dx12_mode', True),
                vulkan_mode=profile.fsr_config.get('vulkan_mode', False),
                frame_generation=profile.fsr_config.get('frame_generation', True),
                frame_interpolation=profile.fsr_config.get('frame_interpolation', True),
                async_compute=profile.fsr_config.get('async_compute', True),
                hdr_support=profile.fsr_config.get('hdr_support', False)
            )
            
            # Deploy FSR DLLs to game directory
            if not self.fsr_manager.deploy_fsr_to_game(str(game_dir), fsr_config):
                print("Failed to deploy FSR DLLs")
                return False
            
            print(f"FSR DLLs deployed to {game_dir}")
            print(f"Config: {fsr_config.preset.value}, FG: {fsr_config.frame_generation}")
            
            # Note: For true DLL injection into running process,
            # would use dll_injector.inject_dll() here
            # For now, we deploy DLLs which will be loaded on next game start
            
            return True
        
        except Exception as e:
            print(f"Error performing injection: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_game_closed(self, game: GameProcess):
        """Handle game close event
        
        Args:
            game: Closed game process
        """
        # Remove from tracking
        if game.pid in self._injected_pids:
            game_name = self._injected_pids.pop(game.pid)
            print(f"Game closed: {game.display_name} (was injected)")
            self._notify_callbacks('closed', game, None)
        
        # Cancel pending injection
        if game.pid in self._injection_threads:
            # Thread will check if pid exists and exit
            del self._injection_threads[game.pid]
    
    def is_injected(self, pid: int) -> bool:
        """Check if game is injected
        
        Args:
            pid: Process ID
        
        Returns:
            True if injected
        """
        return pid in self._injected_pids
    
    def get_injected_games(self) -> Dict[int, str]:
        """Get dict of injected games
        
        Returns:
            Dict of pid -> game_name
        """
        return self._injected_pids.copy()
    
    def register_callback(self, callback: Callable):
        """Register callback for injection events
        
        Callback signature: callback(event: str, game: GameProcess, profile: GameProfile)
        Events: 'injected', 'failed', 'closed'
        """
        self._callbacks.append(callback)
    
    def _notify_callbacks(self, event: str, game: GameProcess, profile: Optional[GameProfile]):
        """Notify registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(event, game, profile)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def check_health(self) -> dict:
        """Check manager health"""
        if not all([self.profile_manager, self.fsr_manager, self.dll_injector]):
            return {
                'status': 'warning',
                'message': 'Some components not available'
            }
        
        injected_count = len(self._injected_pids)
        pending_count = len(self._injection_threads)
        
        return {
            'status': 'healthy',
            'message': f'{injected_count} injected, {pending_count} pending'
        }


# Singleton instance
_auto_injection_manager = None

def get_auto_injection_manager() -> AutoInjectionManager:
    """Get singleton auto injection manager instance"""
    global _auto_injection_manager
    if _auto_injection_manager is None:
        _auto_injection_manager = AutoInjectionManager()
    return _auto_injection_manager
