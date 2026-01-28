"""Configuration management for PartMart Boost"""
import json
import os
from typing import Any, Dict
from pathlib import Path

class Config:
    """Application configuration with JSON persistence"""
    
    DEFAULT_CONFIG = {
        "language": "auto",  # auto, en, ru
        "update_interval": 2000,  # milliseconds
        "ml_optimizer_enabled": False,  # Beta feature
        "theme": "dark",  # dark, light (future)
        "autostart": False,
        "minimize_to_tray": False,
        "show_cpu_temp": True,
        "show_gpu_hotspot": True,
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        "check_updates": True,
        "first_launch": True,
    }
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._ensure_config_dir()
        self.load()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        config_dir = os.path.dirname(self.config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
    
    def load(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults (in case new keys were added)
                self.config = {**self.DEFAULT_CONFIG, **loaded_config}
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            # First launch - create default config
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        self.config[key] = value
        self.save()
    
    def get_language(self) -> str:
        """Get language (auto-detect if needed)"""
        lang = self.get("language", "auto")
        if lang == "auto":
            # Auto-detect system language
            try:
                import locale
                system_lang = locale.getdefaultlocale()[0]
                if system_lang:
                    lang_code = system_lang.split('_')[0].lower()
                    if lang_code in ['ru', 'en']:
                        return lang_code
            except:
                pass
            return "en"  # Default fallback
        return lang
    
    def set_language(self, language: str):
        """Set language preference"""
        if language in ['auto', 'en', 'ru']:
            self.set("language", language)
    
    def is_ml_enabled(self) -> bool:
        """Check if ML optimizer is enabled"""
        return self.get("ml_optimizer_enabled", False)
    
    def enable_ml(self, enabled: bool):
        """Enable/disable ML optimizer"""
        self.set("ml_optimizer_enabled", enabled)
    
    def get_update_interval(self) -> int:
        """Get system monitoring update interval (milliseconds)"""
        return self.get("update_interval", 2000)
    
    def set_update_interval(self, interval: int):
        """Set update interval (1000-5000ms)"""
        if 1000 <= interval <= 5000:
            self.set("update_interval", interval)
    
    def is_first_launch(self) -> bool:
        """Check if this is first application launch"""
        return self.get("first_launch", True)
    
    def mark_launched(self):
        """Mark that application has been launched"""
        self.set("first_launch", False)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()

# Global config instance
_config = None

def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def init_config(config_path: str = "config/settings.json") -> Config:
    """Initialize global configuration"""
    global _config
    _config = Config(config_path)
    return _config

if __name__ == "__main__":
    # Test
    config = Config("test_config.json")
    print(f"Language: {config.get_language()}")
    print(f"ML enabled: {config.is_ml_enabled()}")
    print(f"Update interval: {config.get_update_interval()}ms")
    print(f"First launch: {config.is_first_launch()}")
    
    # Test save
    config.set_language("ru")
    config.enable_ml(True)
    config.mark_launched()
    
    # Reload
    config2 = Config("test_config.json")
    print(f"\nReloaded:")
    print(f"Language: {config2.get_language()}")
    print(f"ML enabled: {config2.is_ml_enabled()}")
    print(f"First launch: {config2.is_first_launch()}")
    
    # Cleanup
    import os
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
