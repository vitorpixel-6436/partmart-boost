#!/usr/bin/env python3
"""FSR Manager - AMD FidelityFX Super Resolution 3.x management

Version: 0.3.5d (package 3.9a, stage 7.7d)

Updated for FSR 3.x with frame generation support!
Real FSR library management and configuration.
"""
import os
import shutil
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class FSRVersion(Enum):
    """FSR version"""
    FSR_2_0 = "2.0"
    FSR_2_1 = "2.1"
    FSR_2_2 = "2.2"
    FSR_3_0 = "3.0"  # With frame generation!
    FSR_3_1 = "3.1"


class FSRPreset(Enum):
    """FSR quality presets"""
    ULTRA_QUALITY = "ultra_quality"      # 1.3x (77% render scale)
    QUALITY = "quality"                  # 1.5x (67% render scale)
    BALANCED = "balanced"                # 1.7x (59% render scale)
    PERFORMANCE = "performance"          # 2.0x (50% render scale)
    ULTRA_PERFORMANCE = "ultra_performance"  # 3.0x (33% render scale)
    NATIVE_AA = "native_aa"              # 1.0x (100% scale, FSR as AA)


@dataclass
class FSRConfig:
    """FSR configuration"""
    version: FSRVersion = FSRVersion.FSR_3_1
    preset: FSRPreset = FSRPreset.QUALITY
    render_scale: float = 0.67
    sharpness: float = 0.5  # 0.0 - 1.0
    enabled: bool = True
    
    # API support
    dx11_mode: bool = False
    dx12_mode: bool = True
    vulkan_mode: bool = False
    
    # FSR 3.x specific
    frame_generation: bool = True       # NEW: Frame generation
    frame_interpolation: bool = True    # NEW: Frame interpolation
    async_compute: bool = True          # NEW: Async compute
    hdr_support: bool = False
    
    # Advanced
    motion_vector_scale: float = 1.0
    reactive_mask_scale: float = 1.0
    auto_exposure: bool = True


class FSRManager:
    """FSR 3.x library management system
    
    Manages FSR 3.x DLL files, configurations, and game-specific settings.
    Supports FSR 3.x for DirectX 11/12 and Vulkan with frame generation!
    
    v0.3.5d - Stage 7.7d: FSR 3.x support
    """
    
    # FSR DLL filenames by API and version
    FSR_DLLS = {
        'dx11': 'ffx_fsr3_api_dx11_x64.dll',
        'dx12': 'ffx_fsr3_api_dx12_x64.dll',
        'vk': 'ffx_fsr3_api_vk_x64.dll',
        # Frame generation DLLs
        'fg_dx12': 'ffx_framegeneration_dx12_x64.dll',
        'fg_vk': 'ffx_framegeneration_vk_x64.dll'
    }
    
    # Render scale by preset
    PRESET_SCALES = {
        FSRPreset.NATIVE_AA: 1.0,
        FSRPreset.ULTRA_QUALITY: 0.77,
        FSRPreset.QUALITY: 0.67,
        FSRPreset.BALANCED: 0.59,
        FSRPreset.PERFORMANCE: 0.50,
        FSRPreset.ULTRA_PERFORMANCE: 0.33
    }
    
    def __init__(self, data_dir: str = 'data/fsr'):
        self.name = "FSRManager"
        self.data_dir = Path(data_dir)
        self.dll_dir = self.data_dir / 'dlls'
        self.config_dir = self.data_dir / 'configs'
        self.backup_dir = self.data_dir / 'backups'
        
        # Create directories
        self.dll_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Current configurations per game
        self._game_configs: Dict[str, FSRConfig] = {}
        
        # Load saved configurations
        self._load_configs()
    
    def get_preset_scale(self, preset: FSRPreset) -> float:
        """Get render scale for preset"""
        return self.PRESET_SCALES.get(preset, 0.67)
    
    def create_config(
        self,
        version: FSRVersion = FSRVersion.FSR_3_1,
        preset: FSRPreset = FSRPreset.QUALITY,
        frame_generation: bool = True,
        **kwargs
    ) -> FSRConfig:
        """Create FSR configuration
        
        Args:
            version: FSR version (3.1 recommended)
            preset: Quality preset
            frame_generation: Enable frame generation (FSR 3.x only)
            **kwargs: Additional config options
        
        Returns:
            FSR configuration object
        """
        render_scale = self.get_preset_scale(preset)
        
        # Frame generation only for FSR 3.x
        if version in [FSRVersion.FSR_2_0, FSRVersion.FSR_2_1, FSRVersion.FSR_2_2]:
            frame_generation = False
        
        config = FSRConfig(
            version=version,
            preset=preset,
            render_scale=render_scale,
            frame_generation=frame_generation,
            **kwargs
        )
        
        return config
    
    def save_game_config(self, game_name: str, config: FSRConfig) -> bool:
        """Save FSR configuration for specific game"""
        try:
            config_file = self.config_dir / f"{game_name}.json"
            
            # Convert to dict
            config_dict = asdict(config)
            # Convert enums to strings
            config_dict['version'] = config.version.value
            config_dict['preset'] = config.preset.value
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self._game_configs[game_name] = config
            return True
        
        except Exception as e:
            print(f"Error saving config for {game_name}: {e}")
            return False
    
    def load_game_config(self, game_name: str) -> Optional[FSRConfig]:
        """Load FSR configuration for specific game"""
        # Check memory cache first
        if game_name in self._game_configs:
            return self._game_configs[game_name]
        
        # Load from file
        try:
            config_file = self.config_dir / f"{game_name}.json"
            if not config_file.exists():
                return None
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Convert strings back to enums
            config = FSRConfig(
                version=FSRVersion(config_data['version']),
                preset=FSRPreset(config_data['preset']),
                render_scale=config_data['render_scale'],
                sharpness=config_data.get('sharpness', 0.5),
                enabled=config_data.get('enabled', True),
                dx11_mode=config_data.get('dx11_mode', False),
                dx12_mode=config_data.get('dx12_mode', True),
                vulkan_mode=config_data.get('vulkan_mode', False),
                frame_generation=config_data.get('frame_generation', True),
                frame_interpolation=config_data.get('frame_interpolation', True),
                async_compute=config_data.get('async_compute', True),
                hdr_support=config_data.get('hdr_support', False),
                motion_vector_scale=config_data.get('motion_vector_scale', 1.0),
                reactive_mask_scale=config_data.get('reactive_mask_scale', 1.0),
                auto_exposure=config_data.get('auto_exposure', True)
            )
            
            self._game_configs[game_name] = config
            return config
        
        except Exception as e:
            print(f"Error loading config for {game_name}: {e}")
            return None
    
    def _load_configs(self):
        """Load all saved configurations"""
        try:
            for config_file in self.config_dir.glob('*.json'):
                game_name = config_file.stem
                self.load_game_config(game_name)
        except Exception as e:
            print(f"Error loading configs: {e}")
    
    def get_dll_path(self, api: str = 'dx12', frame_gen: bool = False) -> Optional[Path]:
        """Get path to FSR DLL for specific API
        
        Args:
            api: Graphics API ('dx11', 'dx12', 'vk')
            frame_gen: Get frame generation DLL
        
        Returns:
            Path to DLL or None if not found
        """
        if frame_gen and api == 'dx12':
            dll_name = self.FSR_DLLS['fg_dx12']
        elif frame_gen and api == 'vk':
            dll_name = self.FSR_DLLS['fg_vk']
        elif api in self.FSR_DLLS:
            dll_name = self.FSR_DLLS[api]
        else:
            return None
        
        dll_path = self.dll_dir / dll_name
        return dll_path if dll_path.exists() else None
    
    def get_required_dlls(self, config: FSRConfig) -> List[str]:
        """Get list of required DLLs for config
        
        Args:
            config: FSR configuration
        
        Returns:
            List of DLL names needed
        """
        dlls = []
        
        # Base FSR DLL
        if config.dx12_mode:
            dlls.append(self.FSR_DLLS['dx12'])
        elif config.dx11_mode:
            dlls.append(self.FSR_DLLS['dx11'])
        elif config.vulkan_mode:
            dlls.append(self.FSR_DLLS['vk'])
        
        # Frame generation DLL (FSR 3.x only)
        if config.frame_generation and config.version.value.startswith('3.'):
            if config.dx12_mode:
                dlls.append(self.FSR_DLLS['fg_dx12'])
            elif config.vulkan_mode:
                dlls.append(self.FSR_DLLS['fg_vk'])
        
        return dlls
    
    def install_fsr_dlls(self, source_dir: str) -> bool:
        """Install FSR DLLs from source directory"""
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                print(f"Source directory not found: {source_dir}")
                return False
            
            # Copy each DLL
            installed = 0
            for dll_type, dll_name in self.FSR_DLLS.items():
                source_dll = source_path / dll_name
                if source_dll.exists():
                    dest_dll = self.dll_dir / dll_name
                    shutil.copy2(source_dll, dest_dll)
                    print(f"Installed: {dll_name}")
                    installed += 1
            
            if installed == 0:
                print("No FSR DLLs found in source directory")
                return False
            
            print(f"Installed {installed} FSR DLL(s)")
            return True
        
        except Exception as e:
            print(f"Error installing FSR DLLs: {e}")
            return False
    
    def deploy_fsr_to_game(self, game_exe_dir: str, config: FSRConfig) -> bool:
        """Deploy FSR DLLs to game directory
        
        Args:
            game_exe_dir: Game executable directory
            config: FSR configuration
        
        Returns:
            True if deployed successfully
        """
        try:
            game_dir = Path(game_exe_dir)
            if not game_dir.exists():
                print(f"Game directory not found: {game_exe_dir}")
                return False
            
            # Get required DLLs
            required_dlls = self.get_required_dlls(config)
            if not required_dlls:
                print("No DLLs required for configuration")
                return False
            
            # Deploy each DLL
            for dll_name in required_dlls:
                source = self.dll_dir / dll_name
                if not source.exists():
                    print(f"DLL not found: {dll_name}")
                    return False
                
                # Backup existing
                dest = game_dir / dll_name
                if dest.exists():
                    import time
                    backup_name = f"{dll_name}.backup.{int(time.time())}"
                    backup_dest = self.backup_dir / backup_name
                    shutil.copy2(dest, backup_dest)
                
                # Copy DLL
                shutil.copy2(source, dest)
                print(f"Deployed: {dll_name}")
            
            # Create FSR config file
            self._create_fsr_config_file(game_dir, config)
            
            return True
        
        except Exception as e:
            print(f"Error deploying FSR: {e}")
            return False
    
    def _create_fsr_config_file(self, game_dir: Path, config: FSRConfig):
        """Create FSR configuration file in game directory"""
        try:
            config_file = game_dir / 'fsr_config.ini'
            
            with open(config_file, 'w') as f:
                f.write("[FSR]\n")
                f.write(f"Version={config.version.value}\n")
                f.write(f"QualityMode={config.preset.value}\n")
                f.write(f"RenderScale={config.render_scale:.2f}\n")
                f.write(f"Sharpness={config.sharpness:.2f}\n")
                f.write(f"Enabled={'1' if config.enabled else '0'}\n")
                f.write(f"FrameGeneration={'1' if config.frame_generation else '0'}\n")
                f.write(f"FrameInterpolation={'1' if config.frame_interpolation else '0'}\n")
                f.write(f"AsyncCompute={'1' if config.async_compute else '0'}\n")
                f.write(f"HDR={'1' if config.hdr_support else '0'}\n")
            
            print(f"Created FSR config: {config_file}")
        
        except Exception as e:
            print(f"Error creating FSR config file: {e}")
    
    def check_health(self) -> dict:
        """Check FSR manager health"""
        # Check if FSR DLLs are available
        available_dlls = []
        for dll_type, dll_name in self.FSR_DLLS.items():
            dll_path = self.dll_dir / dll_name
            if dll_path.exists():
                available_dlls.append(dll_type)
        
        if not available_dlls:
            return {
                'status': 'warning',
                'message': 'No FSR 3.x DLLs installed. Download from AMD FidelityFX SDK.'
            }
        
        # Check for frame generation support
        has_frame_gen = 'fg_dx12' in available_dlls or 'fg_vk' in available_dlls
        
        message = f"FSR 3.x DLLs available: {', '.join(available_dlls)}"
        if has_frame_gen:
            message += " (Frame Generation ready!)"
        
        return {
            'status': 'healthy',
            'message': message
        }


# Singleton instance
_fsr_manager = None

def get_fsr_manager() -> FSRManager:
    """Get singleton FSR manager instance"""
    global _fsr_manager
    if _fsr_manager is None:
        _fsr_manager = FSRManager()
    return _fsr_manager
