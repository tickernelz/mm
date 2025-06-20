"""
Logging utility for Auto Mouse Move
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Centralized logging utility"""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logger with appropriate handlers"""
        self._logger = logging.getLogger("telek")
        self._logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler for all messages (optional)
        try:
            log_dir = Path.home() / ".config" / "auto-mouse-move"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "app.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, continue without it
            pass
    
    def debug(self, message: str):
        """Log debug message"""
        if self._logger:
            self._logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        if self._logger:
            self._logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        if self._logger:
            self._logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        if self._logger:
            self._logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        if self._logger:
            self._logger.critical(message)


# Global logger instance
logger = Logger()