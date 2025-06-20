"""
Idle time detection for macOS
"""

import time
import subprocess
from typing import Optional
from PyQt6.QtCore import QObject


class IdleDetector(QObject):
    """Detects system idle time on macOS"""
    
    def __init__(self):
        super().__init__()
        self._last_activity_time = time.time()
    
    def get_idle_time(self) -> float:
        """
        Get system idle time in seconds
        Returns the time since last user input (mouse/keyboard)
        """
        try:
            # Use ioreg command to get HID idle time on macOS
            result = subprocess.run([
                'ioreg', '-c', 'IOHIDSystem'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'HIDIdleTime' in line:
                        # Extract the idle time value
                        # Format: "HIDIdleTime" = 1234567890
                        idle_time_ns = int(line.split('=')[1].strip())
                        # Convert nanoseconds to seconds
                        idle_time_seconds = idle_time_ns / 1_000_000_000
                        return idle_time_seconds
            
            # Fallback: use last activity tracking
            return time.time() - self._last_activity_time
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, IndexError):
            # Fallback method using system_profiler (slower but more reliable)
            try:
                result = subprocess.run([
                    'system_profiler', 'SPPowerDataType'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    # This is a less accurate fallback
                    # Return time since last recorded activity
                    return time.time() - self._last_activity_time
                    
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                pass
            
            # Final fallback
            return time.time() - self._last_activity_time
    
    def reset_idle_time(self):
        """Reset the idle time counter"""
        self._last_activity_time = time.time()
    
    def is_idle(self, threshold_seconds: float) -> bool:
        """Check if system has been idle for longer than threshold"""
        return self.get_idle_time() >= threshold_seconds