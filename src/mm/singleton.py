"""
Singleton implementation to prevent multiple instances of the application
"""

import os
import sys
import fcntl
import tempfile
from pathlib import Path
from typing import Optional


class SingletonLock:
    """Ensures only one instance of the application can run at a time"""
    
    def __init__(self, app_name: str = "auto_mouse_move"):
        self.app_name = app_name
        self.lock_file: Optional[object] = None
        self.lock_path = self._get_lock_path()
    
    def _get_lock_path(self) -> Path:
        """Get the path for the lock file"""
        if sys.platform == "darwin":
            # macOS: Use ~/Library/Application Support
            lock_dir = Path.home() / "Library" / "Application Support" / "telek"
        else:
            # Other platforms: Use temp directory
            lock_dir = Path(tempfile.gettempdir()) / "telek"
        
        # Ensure directory exists
        lock_dir.mkdir(parents=True, exist_ok=True)
        
        return lock_dir / f"{self.app_name}.lock"
    
    def acquire(self) -> bool:
        """
        Acquire the singleton lock
        Returns True if successful, False if another instance is running
        """
        try:
            # Open the lock file
            self.lock_file = open(self.lock_path, 'w')
            
            # Try to acquire an exclusive lock (non-blocking)
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Write current process ID to the lock file
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            
            return True
            
        except (IOError, OSError):
            # Lock is already held by another process
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            return False
    
    def release(self):
        """Release the singleton lock"""
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                self.lock_file = None
                
                # Remove the lock file
                if self.lock_path.exists():
                    self.lock_path.unlink()
                    
            except (IOError, OSError):
                pass
    
    def is_running(self) -> bool:
        """Check if another instance is already running"""
        if not self.lock_path.exists():
            return False
        
        try:
            with open(self.lock_path, 'r') as f:
                pid_str = f.read().strip()
                if not pid_str:
                    return False
                
                pid = int(pid_str)
                
                # Check if the process is still running
                try:
                    os.kill(pid, 0)  # Signal 0 just checks if process exists
                    return True
                except OSError:
                    # Process doesn't exist, remove stale lock file
                    self.lock_path.unlink()
                    return False
                    
        except (IOError, OSError, ValueError):
            return False
    
    def get_running_pid(self) -> Optional[int]:
        """Get the PID of the running instance, if any"""
        if not self.lock_path.exists():
            return None
        
        try:
            with open(self.lock_path, 'r') as f:
                pid_str = f.read().strip()
                if pid_str:
                    pid = int(pid_str)
                    # Verify the process is still running
                    try:
                        os.kill(pid, 0)
                        return pid
                    except OSError:
                        # Process doesn't exist
                        self.lock_path.unlink()
                        return None
        except (IOError, OSError, ValueError):
            pass
        
        return None
    
    def __enter__(self):
        """Context manager entry"""
        if not self.acquire():
            raise RuntimeError("Another instance is already running")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


class SingletonApp:
    """Application singleton manager with user-friendly messaging"""
    
    def __init__(self, app_name: str = "auto_mouse_move"):
        self.app_name = app_name
        self.lock = SingletonLock(app_name)
    
    def ensure_single_instance(self) -> bool:
        """
        Ensure only one instance is running
        Returns True if this instance can proceed, False if should exit
        """
        if self.lock.is_running():
            running_pid = self.lock.get_running_pid()
            
            # Try to show a user-friendly message
            self._show_already_running_message(running_pid)
            return False
        
        # Try to acquire the lock
        if not self.lock.acquire():
            # Another instance started between our check and lock attempt
            self._show_already_running_message()
            return False
        
        return True
    
    def _show_already_running_message(self, pid: Optional[int] = None):
        """Show a message that the application is already running"""
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            from PyQt6.QtCore import Qt
            
            # Create a temporary QApplication if none exists
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            # Create message box
            msg_box = QMessageBox()
            msg_box.setWindowTitle("telek")
            msg_box.setIcon(QMessageBox.Icon.Information)
            
            if pid:
                msg_box.setText(f"telek is already running (PID: {pid}).")
            else:
                msg_box.setText("telek is already running.")
            
            msg_box.setInformativeText("Only one instance of the application can run at a time.\n\n"
                                     "Check your system tray for the running instance.")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            
            # Show the message
            msg_box.exec()
            
        except ImportError:
            # Fallback to console message if PyQt6 is not available
            if pid:
                print(f"telek is already running (PID: {pid}).")
            else:
                print("telek is already running.")
            print("Only one instance of the application can run at a time.")
            print("Check your system tray for the running instance.")
    
    def release(self):
        """Release the singleton lock"""
        self.lock.release()
    
    def __enter__(self):
        """Context manager entry"""
        if not self.ensure_single_instance():
            sys.exit(1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()