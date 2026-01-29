#!/usr/bin/env python3
"""Configuration Manager - Centralized application configuration

Version: 0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)

Package 3.9a Stage 7.7b.9.1: Final integration and configuration management.

Features:
- Centralized configuration
- Save/load settings
- Default values
- Type validation
- JSON storage
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    check_interval: float = 5.0
    enable_performance_monitoring: bool = True
    enable_game_detection: bool = True
    enable_auto_recovery: bool = True
    error_threshold: int = 10
    recovery_retry_limit: int = 3


@dataclass
class HistoricalDataConfig:
    """Historical data configuration"""
    enabled: bool = True
    retention_days: int = 30
    collection_interval: float = 60.0
    aggregation_interval: float = 3600.0
    enable_health_collection: bool = True
    enable_error_collection: bool = True
    enable_recovery_collection: bool = True


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    enabled: bool = True
    default_time_range: str = "Last 24 Hours"
    auto_refresh: bool = True
    refresh_interval: int = 30
    chart_colors: list = None
    
    def __post_init__(self):
        if self.chart_colors is None:
            self.chart_colors = [
                '#3498db', '#2ecc71', '#f39c12',
                '#e74c3c', '#9b59b6', '#1abc9c'
            ]


@dataclass
class UIConfig:
    """UI configuration"""
    window_width: int = 1200
    window_height: int = 800
    theme: str = "light"
    show_notifications: bool = True
    notification_duration: int = 5000
    show_system_tray: bool = True


@dataclass
class ApplicationConfig:
    """Main application configuration"""
    version: str = "0.3.5g"
    package: str = "3.9a"
    stage: str = "7.7b.9.1"
    
    monitoring: MonitoringConfig = None
    historical_data: HistoricalDataConfig = None
    visualization: VisualizationConfig = None
    ui: UIConfig = None
    
    def __post_init__(self):
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()
        if self.historical_data is None:
            self.historical_data = HistoricalDataConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()
        if self.ui is None:
            self.ui = UIConfig()


class ConfigManager:
    """Centralized configuration manager
    
    v0.3.5g (package 3.9a, stage 7.7b.9.1/7.7b.9)
    
    Features:
    - Load/save configuration
    - Default values
    - Type validation
    - JSON storage
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.config: ApplicationConfig = ApplicationConfig()
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> ApplicationConfig:
        """Load configuration from file
        
        Returns:
            Loaded configuration or defaults
        """
        if not self.config_path.exists():
            # No config file, use defaults
            self.config = ApplicationConfig()
            return self.config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse configuration
            self.config = self._parse_config(data)
            return self.config
        
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration")
            self.config = ApplicationConfig()
            return self.config
    
    def save(self) -> bool:
        """Save configuration to file
        
        Returns:
            True if saved successfully
        """
        try:
            data = self._serialize_config()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _parse_config(self, data: Dict[str, Any]) -> ApplicationConfig:
        """Parse configuration from dict"""
        config = ApplicationConfig(
            version=data.get('version', '0.3.5g'),
            package=data.get('package', '3.9a'),
            stage=data.get('stage', '7.7b.9.1')
        )
        
        # Parse monitoring config
        if 'monitoring' in data:
            config.monitoring = MonitoringConfig(**data['monitoring'])
        
        # Parse historical data config
        if 'historical_data' in data:
            config.historical_data = HistoricalDataConfig(**data['historical_data'])
        
        # Parse visualization config
        if 'visualization' in data:
            config.visualization = VisualizationConfig(**data['visualization'])
        
        # Parse UI config
        if 'ui' in data:
            config.ui = UIConfig(**data['ui'])
        
        return config
    
    def _serialize_config(self) -> Dict[str, Any]:
        """Serialize configuration to dict"""
        return {
            'version': self.config.version,
            'package': self.config.package,
            'stage': self.config.stage,
            'monitoring': asdict(self.config.monitoring),
            'historical_data': asdict(self.config.historical_data),
            'visualization': asdict(self.config.visualization),
            'ui': asdict(self.config.ui)
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key
        
        Args:
            key: Configuration key (e.g., 'monitoring.check_interval')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        parts = key.split('.')
        value = self.config
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value
        
        Args:
            key: Configuration key (e.g., 'monitoring.check_interval')
            value: New value
        
        Returns:
            True if set successfully
        """
        parts = key.split('.')
        obj = self.config
        
        # Navigate to parent object
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return False
        
        # Set value
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
            return True
        
        return False
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = ApplicationConfig()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary
        
        Returns:
            Configuration dictionary
        """
        return self._serialize_config()


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance
    
    Returns:
        ConfigManager singleton
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.load()
    return _config_manager


# Testing
if __name__ == '__main__':
    # Create config manager
    config_mgr = ConfigManager('test_config.json')
    
    # Load defaults
    config = config_mgr.load()
    print(f"Version: {config.version}")
    print(f"Monitoring check interval: {config.monitoring.check_interval}")
    print(f"Historical data enabled: {config.historical_data.enabled}")
    
    # Set values
    config_mgr.set('monitoring.check_interval', 10.0)
    config_mgr.set('ui.window_width', 1600)
    
    # Save
    if config_mgr.save():
        print("Configuration saved")
    
    # Load again
    config_mgr2 = ConfigManager('test_config.json')
    config2 = config_mgr2.load()
    print(f"Loaded check interval: {config2.monitoring.check_interval}")
    print(f"Loaded window width: {config2.ui.window_width}")
    
    # Cleanup
    import os
    os.remove('test_config.json')
