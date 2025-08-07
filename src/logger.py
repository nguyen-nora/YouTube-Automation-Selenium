"""
Logging configuration for YouTube Automation System.
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from colorama import Fore, Style, init
import json
from typing import Dict, Any

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"
        return super().format(record)


class AutomationLogger:
    """Centralized logging for the automation system."""
    
    _instance: Optional['AutomationLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'AutomationLogger':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger configuration."""
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self) -> None:
        """Configure logging settings."""
        # Detect if running as frozen executable
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            # When frozen, create logs directory next to the executable
            base_dir = os.path.dirname(sys.executable)
            log_dir = Path(base_dir) / "logs"
        else:
            # In development, use current directory
            log_dir = Path("logs")
        
        log_dir.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"automation_{timestamp}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler with color
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler without color
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        # Set levels for third-party libraries
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
        
        self.log_file = log_file
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger instance for the given name.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    def set_console_level(self, level: int) -> None:
        """Set console logging level.
        
        Args:
            level: Logging level (e.g., logging.DEBUG)
        """
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)
    
    def get_log_file(self) -> Path:
        """Get current log file path.
        
        Returns:
            Path to log file
        """
        return self.log_file
    
    def log_account_status(self, email: str, status: str, details: Dict[str, Any] = None) -> None:
        """Log account-specific status with details.
        
        Args:
            email: Account email address
            status: Status (SUCCESS, FAILED, ERROR)
            details: Additional details about the status
        """
        logger = self.get_logger('account_status')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'email': email,
            'status': status,
            'details': details or {}
        }
        
        # Log to console with appropriate color
        if status == 'SUCCESS':
            logger.info(f"Account {email}: {status} - {details}")
        elif status == 'FAILED':
            logger.warning(f"Account {email}: {status} - {details}")
        elif status == 'ERROR':
            logger.error(f"Account {email}: {status} - {details}")
        
        # Write to account status file
        # Detect if running as frozen executable
        is_frozen = getattr(sys, 'frozen', False)
        
        if is_frozen:
            # When frozen, create logs directory next to the executable
            base_dir = os.path.dirname(sys.executable)
            status_file = Path(base_dir) / "logs" / "account_status.json"
        else:
            # In development, use current directory
            status_file = Path("logs") / "account_status.json"
        
        # Read existing status data
        existing_data = []
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # Append new entry
        existing_data.append(log_entry)
        
        # Write back
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)


# Initialize logger singleton
logger_config = AutomationLogger()


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger_config.get_logger(name)
