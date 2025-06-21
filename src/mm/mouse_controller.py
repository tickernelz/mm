"""
Mouse movement and scrolling controller
"""

import random
import math
import time
import sys
import pyautogui
from pathlib import Path
from typing import Tuple
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

# Add the parent directory to sys.path for absolute imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mm.idle_detector import IdleDetector
from mm.config import ConfigManager
from mm.keyboard_macro import KeyboardMacroManager
from mm.logger import logger


class MouseController(QObject):
    """Controls mouse movement and scrolling to prevent idle"""
    
    status_changed = pyqtSignal(str)  # Emits status messages
    activity_performed = pyqtSignal(str)  # Emits when activity is performed
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.idle_detector = IdleDetector()
        self.keyboard_macro_manager = KeyboardMacroManager()
        self.system_tray = None
        
        # Set up PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Timer for checking idle status
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_idle_and_act)
        
        # Movement state
        self._last_move_time = 0
        self._movement_angle = 0
        self._is_enabled = False
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Connect to config changes to update timer interval
        self.config_manager.config_changed.connect(self._on_config_changed)
        
        # Connect keyboard macro signals
        self.keyboard_macro_manager.macro_executed.connect(self.activity_performed.emit)
        
    def set_system_tray(self, system_tray):
        """Set reference to system tray for notifications"""
        self.system_tray = system_tray
    
    def start(self):
        """Start the mouse controller"""
        if not self._is_enabled:
            self._is_enabled = True
            interval = self.config_manager.get("check_interval", 5) * 1000  # Convert to ms
            self.check_timer.start(interval)
            self.status_changed.emit("Mouse controller started")
            if self.system_tray:
                self.system_tray.show_notification("Auto Mouse Move", "Started monitoring")
    
    def stop(self):
        """Stop the mouse controller"""
        if self._is_enabled:
            self._is_enabled = False
            self.check_timer.stop()
            self.status_changed.emit("Mouse controller stopped")
            if self.system_tray:
                self.system_tray.show_notification("Auto Mouse Move", "Stopped monitoring")
    
    def is_enabled(self) -> bool:
        """Check if controller is enabled"""
        return self._is_enabled
    
    def _check_idle_and_act(self):
        """Check if system is idle and perform action if needed"""
        if not self._is_enabled:
            return
        
        try:
            idle_time = self.idle_detector.get_idle_time()
            idle_threshold = self.config_manager.get("idle_threshold", 300)
            move_interval = self.config_manager.get("move_interval", 30)
            
            current_time = time.time()
            time_since_last_move = current_time - self._last_move_time
            
            # Check if we should act
            should_act = (idle_time >= idle_threshold and 
                         time_since_last_move >= move_interval)
            
            if should_act:
                self._perform_activity()
                self._last_move_time = current_time
                self.idle_detector.reset_idle_time()
            
            # Emit status
            status = f"Idle: {idle_time:.1f}s, Threshold: {idle_threshold}s"
            self.status_changed.emit(status)
            
        except Exception as e:
            self.status_changed.emit(f"Error: {str(e)}")
    
    def _perform_activity(self):
        """Perform activity to prevent idle: mouse move -> scroll -> keyboard macros"""
        mouse_enabled = self.config_manager.get("mouse_move_enabled", True)
        scroll_enabled = self.config_manager.get("scroll_enabled", True)
        keyboard_enabled = self.keyboard_macro_manager.is_enabled()
        
        if not mouse_enabled and not scroll_enabled and not keyboard_enabled:
            return
        
        try:
            # Step 1: Perform mouse movement first if enabled
            if mouse_enabled:
                self._move_mouse()
                # Small delay between mouse movement and scroll
                time.sleep(0.1)
            
            # Step 2: Then perform scroll if enabled
            if scroll_enabled:
                self._scroll_mouse()
                # Small delay between scroll and keyboard macro
                time.sleep(0.1)
            
            # Step 3: Finally execute keyboard macro if enabled
            if keyboard_enabled:
                self._execute_keyboard_macro()
                
        except Exception as e:
            self.activity_performed.emit(f"Error performing activity: {str(e)}")
    
    def _execute_keyboard_macro(self):
        """Execute a random keyboard macro"""
        try:
            success = self.keyboard_macro_manager.execute_random_macro()
            if not success:
                self.activity_performed.emit("No keyboard macros available to execute")
        except Exception as e:
            self.activity_performed.emit(f"Error executing keyboard macro: {str(e)}")
    
    def _move_mouse(self):
        """Move mouse cursor"""
        current_x, current_y = pyautogui.position()
        pattern = self.config_manager.get("movement_pattern", "random")
        distance = self.config_manager.get("move_distance", 5)
        
        if pattern == "random":
            new_x, new_y = self._get_random_position(current_x, current_y, distance)
        elif pattern == "circular":
            new_x, new_y = self._get_circular_position(current_x, current_y, distance)
        else:  # linear
            new_x, new_y = self._get_linear_position(current_x, current_y, distance)
        
        # Ensure position is within screen bounds
        new_x = max(0, min(self.screen_width - 1, new_x))
        new_y = max(0, min(self.screen_height - 1, new_y))
        
        # Move mouse
        pyautogui.moveTo(new_x, new_y, duration=0.2)
        self.activity_performed.emit(f"Mouse moved to ({new_x}, {new_y})")
    
    def _scroll_mouse(self):
        """Scroll mouse wheel"""
        scroll_amount = self.config_manager.get("scroll_amount", 3)
        scroll_pattern = self.config_manager.get("scroll_pattern", "random")
        
        # Get current mouse position for scrolling
        current_x, current_y = pyautogui.position()
        
        if scroll_pattern == "random":
            # Random scroll in all directions (up, down, left, right)
            directions = [
                ("up", 0, scroll_amount),
                ("down", 0, -scroll_amount),
                ("left", -scroll_amount, 0),
                ("right", scroll_amount, 0)
            ]
            direction_name, h_scroll, v_scroll = random.choice(directions)
            
            # Perform scroll
            if h_scroll != 0:
                pyautogui.hscroll(h_scroll, x=current_x, y=current_y)
            if v_scroll != 0:
                pyautogui.scroll(v_scroll, x=current_x, y=current_y)
                
            self.activity_performed.emit(f"Scrolled {direction_name} ({scroll_amount} clicks)")
            
        elif scroll_pattern == "up":
            pyautogui.scroll(scroll_amount, x=current_x, y=current_y)
            self.activity_performed.emit(f"Scrolled up ({scroll_amount} clicks)")
            
        elif scroll_pattern == "down":
            pyautogui.scroll(-scroll_amount, x=current_x, y=current_y)
            self.activity_performed.emit(f"Scrolled down ({scroll_amount} clicks)")
            
        elif scroll_pattern == "left":
            pyautogui.hscroll(-scroll_amount, x=current_x, y=current_y)
            self.activity_performed.emit(f"Scrolled left ({scroll_amount} clicks)")
            
        elif scroll_pattern == "right":
            pyautogui.hscroll(scroll_amount, x=current_x, y=current_y)
            self.activity_performed.emit(f"Scrolled right ({scroll_amount} clicks)")
    
    def _get_random_position(self, current_x: int, current_y: int, distance: int) -> Tuple[int, int]:
        """Get random position within distance"""
        angle = random.uniform(0, 2 * math.pi)
        actual_distance = random.uniform(1, distance)
        
        new_x = current_x + int(actual_distance * math.cos(angle))
        new_y = current_y + int(actual_distance * math.sin(angle))
        
        return new_x, new_y
    
    def _get_circular_position(self, current_x: int, current_y: int, distance: int) -> Tuple[int, int]:
        """Get position in circular pattern"""
        self._movement_angle += 0.2  # Increment angle for circular movement
        if self._movement_angle >= 2 * math.pi:
            self._movement_angle = 0
        
        new_x = current_x + int(distance * math.cos(self._movement_angle))
        new_y = current_y + int(distance * math.sin(self._movement_angle))
        
        return new_x, new_y
    
    def _get_linear_position(self, current_x: int, current_y: int, distance: int) -> Tuple[int, int]:
        """Get position in linear pattern (back and forth)"""
        # Simple back and forth movement
        if not hasattr(self, '_linear_direction'):
            self._linear_direction = 1
        
        new_x = current_x + (distance * self._linear_direction)
        new_y = current_y
        
        # Check bounds and reverse direction if needed
        if new_x <= 10 or new_x >= self.screen_width - 10:
            self._linear_direction *= -1
            new_x = current_x + (distance * self._linear_direction)
        
        return new_x, new_y
    
    def force_activity(self):
        """Force perform activity immediately"""
        if self._is_enabled:
            self._perform_activity()
            self._last_move_time = time.time()
            self.idle_detector.reset_idle_time()
    
    def _on_config_changed(self):
        """Handle configuration changes"""
        if self._is_enabled:
            # Update timer interval if it changed
            new_interval = self.config_manager.get("check_interval", 5) * 1000
            if self.check_timer.interval() != new_interval:
                self.check_timer.setInterval(new_interval)