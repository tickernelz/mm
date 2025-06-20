"""
Configuration management for Auto Mouse Move
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal

# Add the parent directory to sys.path for absolute imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mm.logger import logger


class ConfigManager(QObject):
    """Manages application configuration"""
    
    config_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.config_dir = Path.home() / ".config" / "auto-mouse-move"
        self.config_file = self.config_dir / "config.json"
        self._config = self._load_default_config()
        self._ensure_config_dir()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "idle_threshold": 300,  # seconds (5 minutes) - range: 3 to 18000 (5 hours)
            "move_interval": 30,    # seconds
            "move_distance": 5,     # pixels
            "scroll_enabled": True,
            "scroll_amount": 3,     # scroll clicks
            "enabled": False,       # Start disabled
            "minimize_to_tray": True,
            "start_minimized": False,
            "mouse_move_enabled": True,
            "movement_pattern": "random",  # random, circular, linear
            "check_interval": 5,    # seconds - how often to check idle time
        }
    
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to handle new config keys
                    self._config.update(loaded_config)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.config_changed.emit()
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = self._load_default_config()
        self.save_config()