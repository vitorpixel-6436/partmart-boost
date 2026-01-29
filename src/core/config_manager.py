#!/usr/bin/env python3
"""Configuration Manager

Version: 0.3.5h (package 3.9a, stage 7.6/7.7)

Package 3.9a Stage 7.6: Configuration management system.

Features:
- Hierarchical configuration
- Schema validation
- Type checking
- Default values
- File persistence (JSON)
- Change notifications
- Thread-safe
"""
import json
import os
import threading
import copy
from typing import Any, Dict, Optional, List, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConfigSchema:
    """Configuration schema definition
    
    Attributes:
        key: Configuration key (dot notation)
        type: Expected type (int, float, str, bool, list, dict)
        default: Default value
        description: Human-readable description
        min_value: Minimum value (numeric types)
        max_value: Maximum value (numeric types)
        choices: Valid choices (list)
        required: Whether value is required
    """
    key: str
    type: type
    default: Any
    description: str = ""
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    required: bool = False
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate value against schema
        
        Args:
            value: Value to validate
        
        Returns:
            (is_valid, error_message)
        """
        # Check required
        if value is None:
            if self.required:
                return False, f"{self.key} is required"
            return True, None
        
        # Check type
        if not isinstance(value, self.type):
            return False, f"{self.key} must be {self.type.__name__}, got {type(value).__name__}"
        
        # Check numeric bounds
        if self.type in (int, float):
            if self.min_value is not None and value < self.min_value:
                return False, f"{self.key} must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"{self.key} must be <= {self.max_value}"
        
        # Check choices
        if self.choices is not None and value not in self.choices:
            return False, f"{self.key} must be one of {self.choices}"
        
        return True, None


class ConfigManager:
    """Configuration Manager
    
    v0.3.5h (package 3.9a, stage 7.6/7.7)
    
    Features:
    - Hierarchical config (dot notation)
    - Schema validation
    - File persistence
    - Change notifications
    - Thread-safe
    
    Usage:
        >>> config = ConfigManager('config.json')
        >>> 
        >>> # Get value
        >>> theme = config.get('ui.theme', 'dark')
        >>> 
        >>> # Set value
        >>> config.set('ui.theme', 'light')
        >>> 
        >>> # Subscribe to changes
        >>> config.subscribe('ui.*', lambda key, value: print(f"{key} = {value}"))
        >>> 
        >>> # Save to file
        >>> config.save()
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize config manager
        
        Args:
            config_file: Path to config file (JSON)
        """
        self._config: Dict[str, Any] = {}
        self._schema: Dict[str, ConfigSchema] = {}
        self._subscribers: List[tuple[str, Callable]] = []
        self._lock = threading.RLock()
        self._config_file = config_file
        
        # Initialize default schema
        self._init_default_schema()
        
        # Load from file if exists
        if config_file and os.path.exists(config_file):
            self.load(config_file)
        else:
            # Load defaults from schema
            self._load_defaults()
        
        print(f"[ConfigManager] Initialized (file: {config_file or 'none'})")
    
    def _init_default_schema(self):
        """Initialize default configuration schema"""
        schemas = [
            # UI settings
            ConfigSchema('ui.theme', str, 'dark', 'UI theme', choices=['dark', 'light']),
            ConfigSchema('ui.language', str, 'en', 'Interface language', choices=['en', 'ru']),
            ConfigSchema('ui.show_fps', bool, True, 'Show FPS overlay'),
            ConfigSchema('ui.window.width', int, 1200, 'Window width', min_value=800, max_value=3840),
            ConfigSchema('ui.window.height', int, 800, 'Window height', min_value=600, max_value=2160),
            
            # Monitoring settings
            ConfigSchema('monitor.enabled', bool, True, 'Enable performance monitoring'),
            ConfigSchema('monitor.interval_ms', int, 100, 'Monitoring interval (ms)', min_value=10, max_value=5000),
            ConfigSchema('monitor.history_size', int, 1000, 'History buffer size', min_value=100, max_value=10000),
            
            # Performance settings
            ConfigSchema('performance.boost_enabled', bool, True, 'Enable performance boost'),
            ConfigSchema('performance.priority', str, 'high', 'Process priority', choices=['normal', 'high', 'realtime']),
            ConfigSchema('performance.affinity_enabled', bool, False, 'Enable CPU affinity'),
            
            # Game detection
            ConfigSchema('games.auto_detect', bool, True, 'Auto-detect games'),
            ConfigSchema('games.boost_on_start', bool, True, 'Boost when game starts'),
            
            # Advanced settings
            ConfigSchema('advanced.analytics_interval', int, 10, 'Analytics interval (s)', min_value=5, max_value=60),
            ConfigSchema('advanced.log_level', str, 'info', 'Logging level', choices=['debug', 'info', 'warning', 'error']),
            ConfigSchema('advanced.auto_save', bool, True, 'Auto-save configuration'),
        ]
        
        for schema in schemas:
            self._schema[schema.key] = schema
    
    def _load_defaults(self):
        """Load default values from schema"""
        for key, schema in self._schema.items():
            self._set_value(key, schema.default, notify=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key (dot notation)
            default: Default value if not found
        
        Returns:
            Configuration value
        """
        with self._lock:
            return self._get_value(key, default)
    
    def _get_value(self, key: str, default: Any = None) -> Any:
        """Get value (internal, no lock)"""
        parts = key.split('.')
        current = self._config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any, validate: bool = True) -> bool:
        """Set configuration value
        
        Args:
            key: Configuration key (dot notation)
            value: Value to set
            validate: Whether to validate against schema
        
        Returns:
            True if successful
        """
        with self._lock:
            # Validate if schema exists
            if validate and key in self._schema:
                is_valid, error = self._schema[key].validate(value)
                if not is_valid:
                    print(f"[ConfigManager] Validation error: {error}")
                    return False
            
            # Set value
            old_value = self._get_value(key)
            self._set_value(key, value)
            
            # Notify subscribers
            if old_value != value:
                self._notify_subscribers(key, value)
            
            return True
    
    def _set_value(self, key: str, value: Any, notify: bool = True):
        """Set value (internal, no lock)"""
        parts = key.split('.')
        current = self._config
        
        # Navigate to parent
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set value
        current[parts[-1]] = value
    
    def get_section(self, prefix: str) -> Dict[str, Any]:
        """Get all keys with prefix
        
        Args:
            prefix: Key prefix (e.g., 'ui', 'monitor')
        
        Returns:
            Dictionary of matching keys/values
        """
        with self._lock:
            result = {}
            
            for key in self.get_all_keys():
                if key.startswith(prefix):
                    result[key] = self._get_value(key)
            
            return result
    
    def get_all_keys(self) -> List[str]:
        """Get all configuration keys
        
        Returns:
            List of all keys
        """
        with self._lock:
            return self._get_keys_recursive(self._config)
    
    def _get_keys_recursive(self, obj: Dict, prefix: str = '') -> List[str]:
        """Get keys recursively"""
        keys = []
        
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                keys.extend(self._get_keys_recursive(value, full_key))
            else:
                keys.append(full_key)
        
        return keys
    
    def subscribe(self, pattern: str, callback: Callable[[str, Any], None]) -> int:
        """Subscribe to configuration changes
        
        Args:
            pattern: Key pattern (supports '*' wildcard)
            callback: Callback function(key, value)
        
        Returns:
            Subscription ID
        """
        with self._lock:
            sub_id = len(self._subscribers)
            self._subscribers.append((pattern, callback))
            return sub_id
    
    def unsubscribe(self, sub_id: int):
        """Unsubscribe from changes
        
        Args:
            sub_id: Subscription ID
        """
        with self._lock:
            if 0 <= sub_id < len(self._subscribers):
                self._subscribers[sub_id] = None
    
    def _notify_subscribers(self, key: str, value: Any):
        """Notify subscribers of change"""
        for pattern, callback in self._subscribers:
            if callback is None:
                continue
            
            if self._match_pattern(key, pattern):
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"[ConfigManager] Subscriber error: {e}")
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern
        
        Args:
            key: Configuration key
            pattern: Pattern (supports '*' wildcard)
        
        Returns:
            True if matches
        """
        if pattern == '*' or pattern == '**':
            return True
        
        # Convert pattern to regex-like matching
        pattern_parts = pattern.split('.')
        key_parts = key.split('.')
        
        if len(pattern_parts) != len(key_parts):
            # Check for trailing wildcard
            if pattern_parts[-1] == '*' and len(key_parts) >= len(pattern_parts) - 1:
                pattern_parts = pattern_parts[:-1]
            else:
                return False
        
        for p_part, k_part in zip(pattern_parts, key_parts):
            if p_part != '*' and p_part != k_part:
                return False
        
        return True
    
    def load(self, filename: Optional[str] = None) -> bool:
        """Load configuration from file
        
        Args:
            filename: Config file path (uses default if None)
        
        Returns:
            True if successful
        """
        filename = filename or self._config_file
        
        if not filename:
            print("[ConfigManager] No config file specified")
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            with self._lock:
                # Merge loaded config with defaults
                self._config = self._merge_configs(self._get_defaults(), loaded)
            
            print(f"[ConfigManager] ✅ Loaded from {filename}")
            return True
        
        except FileNotFoundError:
            print(f"[ConfigManager] Config file not found: {filename}")
            return False
        
        except json.JSONDecodeError as e:
            print(f"[ConfigManager] Invalid JSON: {e}")
            return False
        
        except Exception as e:
            print(f"[ConfigManager] Load error: {e}")
            return False
    
    def save(self, filename: Optional[str] = None) -> bool:
        """Save configuration to file
        
        Args:
            filename: Config file path (uses default if None)
        
        Returns:
            True if successful
        """
        filename = filename or self._config_file
        
        if not filename:
            print("[ConfigManager] No config file specified")
            return False
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with self._lock:
                config_copy = copy.deepcopy(self._config)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config_copy, f, indent=2, ensure_ascii=False)
            
            print(f"[ConfigManager] ✅ Saved to {filename}")
            return True
        
        except Exception as e:
            print(f"[ConfigManager] Save error: {e}")
            return False
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        defaults = {}
        
        for key, schema in self._schema.items():
            parts = key.split('.')
            current = defaults
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = schema.default
        
        return defaults
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Merge two configs (override takes precedence)"""
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reset(self, key: Optional[str] = None):
        """Reset to defaults
        
        Args:
            key: Specific key to reset (None = reset all)
        """
        with self._lock:
            if key is None:
                # Reset all
                self._config = {}
                self._load_defaults()
                print("[ConfigManager] Reset to defaults")
            elif key in self._schema:
                # Reset specific key
                old_value = self._get_value(key)
                self._set_value(key, self._schema[key].default)
                self._notify_subscribers(key, self._schema[key].default)
                print(f"[ConfigManager] Reset {key} to default")
    
    def get_schema(self, key: str) -> Optional[ConfigSchema]:
        """Get schema for key
        
        Args:
            key: Configuration key
        
        Returns:
            ConfigSchema or None
        """
        return self._schema.get(key)
    
    def get_all_schemas(self) -> Dict[str, ConfigSchema]:
        """Get all schemas
        
        Returns:
            Dictionary of schemas
        """
        return copy.copy(self._schema)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary
        
        Returns:
            Configuration dictionary
        """
        with self._lock:
            return copy.deepcopy(self._config)


# Testing
if __name__ == '__main__':
    print("="*60)
    print("ConfigManager Test")
    print("="*60)
    print()
    
    # Create config manager
    config = ConfigManager('test_config.json')
    
    # Get values
    print("Default values:")
    print(f"  Theme: {config.get('ui.theme')}")
    print(f"  Monitor interval: {config.get('monitor.interval_ms')}")
    print(f"  Boost enabled: {config.get('performance.boost_enabled')}")
    print()
    
    # Set values
    print("Setting values:")
    config.set('ui.theme', 'light')
    config.set('monitor.interval_ms', 200)
    print(f"  Theme: {config.get('ui.theme')}")
    print(f"  Monitor interval: {config.get('monitor.interval_ms')}")
    print()
    
    # Subscribe to changes
    print("Testing subscriptions:")
    def on_ui_change(key, value):
        print(f"  UI changed: {key} = {value}")
    
    config.subscribe('ui.*', on_ui_change)
    config.set('ui.theme', 'dark')
    config.set('ui.show_fps', False)
    print()
    
    # Get section
    print("UI section:")
    ui_config = config.get_section('ui')
    for key, value in ui_config.items():
        print(f"  {key}: {value}")
    print()
    
    # Save and reload
    print("Save/Load test:")
    config.save()
    print("  Saved")
    
    config2 = ConfigManager('test_config.json')
    print(f"  Loaded theme: {config2.get('ui.theme')}")
    print()
    
    # Cleanup
    os.remove('test_config.json')
    
    print("✅ Test completed!")
