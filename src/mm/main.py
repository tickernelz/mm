#!/usr/bin/env python3
"""
Main entry point for Auto Mouse Move application
"""

import sys
import signal
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Add the parent directory to sys.path for absolute imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from mm.gui import MainWindow
from mm.system_tray import SystemTrayManager
from mm.mouse_controller import MouseController
from mm.config import ConfigManager
from mm.logger import logger
from mm.singleton import SingletonApp


def _spoof_process_name():
    """Advanced process name spoofing for macOS"""
    # Generate a unique but inconspicuous name that won't conflict with system processes
    import hashlib
    import time
    
    # Create a unique identifier based on current time and a salt
    unique_id = hashlib.md5(f"telek_{time.time()}".encode()).hexdigest()[:8]
    target_name = f"CoreDisplayAgent_{unique_id}"
    spoofing_success = False
    
    # Method 1: setproctitle (most effective)
    try:
        import setproctitle
        setproctitle.setproctitle(target_name)
        spoofing_success = True
        logger.debug("Process name spoofed using setproctitle")
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"setproctitle failed: {e}")
    
    # Method 2: Modify sys.argv[0] (affects ps output)
    try:
        original_argv0 = sys.argv[0]
        sys.argv[0] = target_name
        spoofing_success = True
        logger.debug("Process name spoofed using argv[0] modification")
    except Exception as e:
        logger.debug(f"argv[0] modification failed: {e}")
    
    # Method 3: macOS specific - modify process name via ctypes (for Activity Monitor)
    if sys.platform == "darwin":
        try:
            import ctypes
            import ctypes.util
            
            # Load libc
            libc = ctypes.CDLL(ctypes.util.find_library("c"))
            
            # Try pthread_setname_np (affects Activity Monitor on macOS)
            try:
                pthread_setname_np = libc.pthread_setname_np
                pthread_setname_np.argtypes = [ctypes.c_char_p]
                pthread_setname_np.restype = ctypes.c_int
                
                result = pthread_setname_np(target_name.encode('utf-8'))
                if result == 0:
                    spoofing_success = True
                    logger.debug("Process name spoofed using pthread_setname_np")
                else:
                    logger.debug(f"pthread_setname_np failed with code: {result}")
            except AttributeError:
                logger.debug("pthread_setname_np not available")
            
            # Try alternative approach with __progname
            try:
                # Get the address of __progname
                progname_addr = ctypes.cast(libc.__progname, ctypes.POINTER(ctypes.c_char_p))
                
                # Create a new string buffer
                new_name = ctypes.create_string_buffer(target_name.encode('utf-8'))
                
                # Update __progname (this affects some system utilities)
                progname_addr.contents = ctypes.cast(new_name, ctypes.c_char_p)
                spoofing_success = True
                logger.debug("Process name spoofed using __progname modification")
            except (AttributeError, OSError) as e:
                logger.debug(f"__progname modification failed: {e}")
                
        except Exception as e:
            logger.debug(f"macOS-specific spoofing failed: {e}")
    
    # Method 4: Environment variable approach (affects some process listings)
    try:
        os.environ['_'] = target_name
        os.environ['PROCESS_NAME'] = target_name
        logger.debug("Process name spoofed using environment variables")
    except Exception as e:
        logger.debug(f"Environment variable spoofing failed: {e}")
    
    # Method 5: For PyInstaller executables - try to modify the executable name in memory
    if getattr(sys, 'frozen', False):  # Running as PyInstaller executable
        try:
            import ctypes
            import ctypes.util
            
            # Get current process ID
            pid = os.getpid()
            
            # Try to use proc_name from libproc (macOS specific)
            try:
                libc = ctypes.CDLL(ctypes.util.find_library("c"))
                libproc = ctypes.CDLL("/usr/lib/libproc.dylib")
                
                # Define proc_name function
                proc_name = libproc.proc_name
                proc_name.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
                proc_name.restype = ctypes.c_int
                
                # Create buffer for new name
                name_buffer = ctypes.create_string_buffer(target_name.encode('utf-8'), 256)
                
                # This is a read function, but we'll try to use it for verification
                result = proc_name(pid, name_buffer, 256)
                logger.debug(f"proc_name result: {result}")
                
            except Exception as e:
                logger.debug(f"libproc approach failed: {e}")
                
        except Exception as e:
            logger.debug(f"PyInstaller-specific spoofing failed: {e}")
    
    if spoofing_success:
        logger.debug(f"Process name spoofing completed - target: {target_name}")
    else:
        logger.debug("Process name spoofing had limited success")


def main():
    """Main application entry point"""
    logger.info("Starting Auto Mouse Move application")
    
    # Check for singleton - ensure only one instance runs
    singleton_app = SingletonApp("telek")
    if not singleton_app.ensure_single_instance():
        logger.info("Another instance is already running. Exiting.")
        return 1
    
    # Advanced process name spoofing for macOS
    _spoof_process_name()
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    app.setApplicationName("telek")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("telek")
    
    # Initialize components
    config_manager = ConfigManager()
    mouse_controller = MouseController(config_manager)
    main_window = MainWindow(config_manager, mouse_controller)
    system_tray = SystemTrayManager(main_window, mouse_controller)
    
    # Connect components
    mouse_controller.set_system_tray(system_tray)
    
    # Apply saved configuration
    if config_manager.get("enabled", False):
        mouse_controller.start()
    
    # Show system tray
    system_tray.show()
    
    # Show main window if not set to start minimized
    if not config_manager.get("start_minimized", False):
        main_window.show()
    
    # Start the application
    try:
        result = app.exec()
    finally:
        # Clean up singleton lock
        singleton_app.release()
        logger.info("Application shutdown complete")
    
    return result


if __name__ == "__main__":
    sys.exit(main())