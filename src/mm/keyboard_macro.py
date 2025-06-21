"""
Keyboard macro management and execution
"""

import json
import time
import random
import pyautogui
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from mm.logger import logger


class KeyboardMacro:
    """Represents a single keyboard macro"""
    
    def __init__(self, name: str, keys: List[str], delay: float = 0.1, description: str = ""):
        self.name = name
        self.keys = keys  # List of key combinations or single keys
        self.delay = delay  # Delay between key presses
        self.description = description
        self.enabled = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert macro to dictionary for serialization"""
        return {
            "name": self.name,
            "keys": self.keys,
            "delay": self.delay,
            "description": self.description,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyboardMacro':
        """Create macro from dictionary"""
        macro = cls(
            name=data.get("name", ""),
            keys=data.get("keys", []),
            delay=data.get("delay", 0.1),
            description=data.get("description", "")
        )
        macro.enabled = data.get("enabled", True)
        return macro


class KeyboardMacroManager(QObject):
    """Manages keyboard macros"""
    
    macro_executed = pyqtSignal(str)  # Emits when a macro is executed
    macros_changed = pyqtSignal()     # Emits when macros list changes
    
    def __init__(self):
        super().__init__()
        self.config_dir = Path.home() / ".config" / "auto-mouse-move"
        self.macros_file = self.config_dir / "macros.json"
        self._macros: List[KeyboardMacro] = []
        self._enabled = False
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load macros and create defaults if none exist
        self.load_macros()
        if not self._macros:
            self._create_default_macros()
    
    def _create_default_macros(self):
        """Create default macros for common use cases"""
        default_macros = [
            KeyboardMacro(
                name="Refresh Page",
                keys=["f5"],
                delay=0.1,
                description="Refresh the current page (F5)"
            ),
            KeyboardMacro(
                name="Alt+Tab",
                keys=["alt+tab"],
                delay=0.1,
                description="Switch between applications"
            ),
            KeyboardMacro(
                name="Ctrl+Tab",
                keys=["ctrl+tab"],
                delay=0.1,
                description="Switch between browser tabs"
            ),
            KeyboardMacro(
                name="Space Bar",
                keys=["space"],
                delay=0.1,
                description="Press space bar (useful for video players)"
            ),
            KeyboardMacro(
                name="Arrow Keys",
                keys=["up", "down", "left", "right"],
                delay=0.2,
                description="Random arrow key press"
            ),
            KeyboardMacro(
                name="Ctrl+S",
                keys=["ctrl+s"],
                delay=0.1,
                description="Save current document"
            ),
            KeyboardMacro(
                name="Escape",
                keys=["escape"],
                delay=0.1,
                description="Press escape key"
            )
        ]
        
        self._macros = default_macros
        self.save_macros()
    
    def load_macros(self):
        """Load macros from file"""
        try:
            if self.macros_file.exists():
                with open(self.macros_file, 'r') as f:
                    data = json.load(f)
                    self._macros = [KeyboardMacro.from_dict(macro_data) 
                                  for macro_data in data.get("macros", [])]
                    self._enabled = data.get("enabled", False)
                logger.info(f"Loaded {len(self._macros)} keyboard macros")
        except Exception as e:
            logger.error(f"Failed to load macros: {e}")
            self._macros = []
    
    def save_macros(self):
        """Save macros to file"""
        try:
            data = {
                "enabled": self._enabled,
                "macros": [macro.to_dict() for macro in self._macros]
            }
            with open(self.macros_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.macros_changed.emit()
        except Exception as e:
            logger.error(f"Failed to save macros: {e}")
    
    def add_macro(self, macro: KeyboardMacro):
        """Add a new macro"""
        self._macros.append(macro)
        self.save_macros()
    
    def remove_macro(self, name: str) -> bool:
        """Remove a macro by name"""
        for i, macro in enumerate(self._macros):
            if macro.name == name:
                del self._macros[i]
                self.save_macros()
                return True
        return False
    
    def update_macro(self, old_name: str, updated_macro: KeyboardMacro) -> bool:
        """Update an existing macro"""
        for i, macro in enumerate(self._macros):
            if macro.name == old_name:
                self._macros[i] = updated_macro
                self.save_macros()
                return True
        return False
    
    def get_macro(self, name: str) -> Optional[KeyboardMacro]:
        """Get a macro by name"""
        for macro in self._macros:
            if macro.name == name:
                return macro
        return None
    
    def get_all_macros(self) -> List[KeyboardMacro]:
        """Get all macros"""
        return self._macros.copy()
    
    def get_enabled_macros(self) -> List[KeyboardMacro]:
        """Get only enabled macros"""
        return [macro for macro in self._macros if macro.enabled]
    
    def is_enabled(self) -> bool:
        """Check if keyboard macros are enabled"""
        return self._enabled
    
    def set_enabled(self, enabled: bool):
        """Enable or disable keyboard macros"""
        self._enabled = enabled
        self.save_macros()
    
    def execute_random_macro(self) -> bool:
        """Execute a random enabled macro"""
        if not self._enabled:
            return False
        
        enabled_macros = self.get_enabled_macros()
        if not enabled_macros:
            return False
        
        # Select a random macro
        macro = random.choice(enabled_macros)
        return self.execute_macro(macro)
    
    def execute_macro(self, macro: KeyboardMacro) -> bool:
        """Execute a specific macro"""
        if not macro.enabled:
            return False
        
        try:
            # If macro has multiple keys, choose one randomly
            if len(macro.keys) > 1:
                key_to_press = random.choice(macro.keys)
            else:
                key_to_press = macro.keys[0] if macro.keys else ""
            
            if not key_to_press:
                return False
            
            # Execute the key press
            self._press_key(key_to_press)
            
            # Add delay
            time.sleep(macro.delay)
            
            self.macro_executed.emit(f"Executed macro '{macro.name}': {key_to_press}")
            logger.debug(f"Executed keyboard macro: {macro.name} -> {key_to_press}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute macro '{macro.name}': {e}")
            return False
    
    def _press_key(self, key_combination: str):
        """Press a key or key combination"""
        try:
            # Handle key combinations (e.g., "ctrl+s", "alt+tab", "shift+cmd+ctrl+right")
            if '+' in key_combination:
                keys = [k.strip().lower() for k in key_combination.split('+')]
                
                # Map platform-specific keys to PyAutoGUI equivalents
                mapped_keys = []
                for key in keys:
                    mapped_key = self._map_key_name(key)
                    mapped_keys.append(mapped_key)
                
                logger.debug(f"Executing key combination: {key_combination} -> {mapped_keys}")
                
                # Use pyautogui's hotkey function for combinations
                pyautogui.hotkey(*mapped_keys)
            else:
                # Single key press
                key = key_combination.strip().lower()
                mapped_key = self._map_key_name(key)
                logger.debug(f"Executing single key: {key} -> {mapped_key}")
                pyautogui.press(mapped_key)
                
        except Exception as e:
            logger.error(f"Failed to press key '{key_combination}': {e}")
            raise
    
    def _map_key_name(self, key: str) -> str:
        """Map key names to PyAutoGUI equivalents"""
        key = key.strip().lower()
        
        # Platform-specific key mappings
        key_mappings = {
            # macOS specific
            'cmd': 'command',
            'command': 'command',
            
            # Windows specific  
            'win': 'winleft',
            'windows': 'winleft',
            'winleft': 'winleft',
            'winright': 'winright',
            
            # Common modifiers
            'ctrl': 'ctrl',
            'control': 'ctrl',
            'alt': 'alt',
            'option': 'alt',  # macOS
            'shift': 'shift',
            
            # Arrow keys
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            
            # Function keys
            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
            'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
            'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
            
            # Special keys
            'space': 'space',
            'enter': 'enter',
            'return': 'enter',
            'tab': 'tab',
            'escape': 'esc',
            'esc': 'esc',
            'backspace': 'backspace',
            'delete': 'delete',
            'home': 'home',
            'end': 'end',
            'pageup': 'pageup',
            'pagedown': 'pagedown',
            'insert': 'insert',
            
            # Punctuation and symbols
            'comma': ',',
            'period': '.',
            'slash': '/',
            'backslash': '\\',
            'semicolon': ';',
            'quote': "'",
            'bracket_left': '[',
            'bracket_right': ']',
            'minus': '-',
            'equal': '=',
            'backtick': '`',
        }
        
        # Return mapped key or original if no mapping exists
        return key_mappings.get(key, key)
    
    def test_macro(self, macro: KeyboardMacro) -> bool:
        """Test a macro execution (for testing purposes)"""
        try:
            logger.info(f"Testing macro: {macro.name}")
            return self.execute_macro(macro)
        except Exception as e:
            logger.error(f"Failed to test macro '{macro.name}': {e}")
            return False
    
    def validate_key_combination(self, key_combination: str) -> bool:
        """Validate if a key combination is valid"""
        try:
            # Basic validation - check if keys are recognized
            if '+' in key_combination:
                keys = [k.strip().lower() for k in key_combination.split('+')]
                
                # Define all valid keys
                valid_modifiers = ['ctrl', 'control', 'alt', 'option', 'shift', 'cmd', 'command', 'win', 'windows', 'winleft', 'winright']
                valid_function_keys = [f'f{i}' for i in range(1, 13)]
                valid_special_keys = [
                    'space', 'enter', 'return', 'tab', 'escape', 'esc', 'backspace', 
                    'delete', 'home', 'end', 'pageup', 'pagedown', 'insert',
                    'up', 'down', 'left', 'right',
                    'comma', 'period', 'slash', 'backslash', 'semicolon', 'quote',
                    'bracket_left', 'bracket_right', 'minus', 'equal', 'backtick'
                ]
                
                # Check if all keys are valid
                for key in keys:
                    # Single character keys (a-z, 0-9) are always valid
                    if len(key) == 1 and (key.isalnum() or key in '`~!@#$%^&*()_+-=[]{}|;:\'",.<>?/\\'):
                        continue
                    
                    # Check against known valid keys
                    if key not in valid_modifiers and key not in valid_function_keys and key not in valid_special_keys:
                        # Try to map the key and see if it's valid
                        mapped_key = self._map_key_name(key)
                        if mapped_key == key:  # No mapping found
                            return False
                            
            else:
                # Single key validation
                key = key_combination.strip().lower()
                if len(key) == 1:
                    return True  # Single character keys are valid
                
                # Check if it's a known key
                mapped_key = self._map_key_name(key)
                if mapped_key == key and key not in ['space', 'enter', 'tab', 'escape', 'esc', 'backspace', 
                                                   'delete', 'home', 'end', 'pageup', 'pagedown', 'insert',
                                                   'up', 'down', 'left', 'right'] and not key.startswith('f'):
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"Error validating key combination '{key_combination}': {e}")
            return False