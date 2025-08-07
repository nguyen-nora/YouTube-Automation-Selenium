"""
Utility functions for YouTube Automation System.
"""

import json
import random
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from .logger import get_logger
from .exceptions import ConfigFileError

logger = get_logger(__name__)


class FileUtils:
    """File operation utilities."""
    
    @staticmethod
    def load_json_file(file_path: Union[str, Path], default: Optional[Dict] = None) -> Dict[str, Any]:
        """Load JSON file with error handling.
        
        Args:
            file_path: Path to JSON file
            default: Default value if file doesn't exist or is invalid
            
        Returns:
            Parsed JSON data
            
        Raises:
            ConfigFileError: If file cannot be read or parsed
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            if default is not None:
                logger.warning(f"File not found: {file_path}, using default")
                return default
            raise ConfigFileError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            if default is not None:
                return default
            raise ConfigFileError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            if default is not None:
                return default
            raise ConfigFileError(f"Error reading file: {e}")
    
    @staticmethod
    def save_json_file(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> None:
        """Save data to JSON file.
        
        Args:
            file_path: Path to save JSON file
            data: Data to save
            indent: JSON indentation level
        """
        file_path = Path(file_path)
        
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.debug(f"Saved JSON to {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSON to {file_path}: {e}")
            raise ConfigFileError(f"Error saving file: {e}")


class TimeUtils:
    """Time-related utility functions."""
    
    @staticmethod
    def random_delay(min_seconds: float, max_seconds: float) -> None:
        """Sleep for a random duration between min and max seconds.
        
        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Random delay: {delay:.2f} seconds")
        time.sleep(delay)
    
    @staticmethod
    def human_readable_duration(seconds: int) -> str:
        """Convert seconds to human-readable duration.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Human-readable duration string
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs}s"


class ValidationUtils:
    """Data validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """Validate YouTube video URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
        """
        import re
        patterns = [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(?:www\.)?youtu\.be/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        ]
        return any(re.match(pattern, url) for pattern in patterns)


class SystemUtils:
    """System-related utilities."""
    
    @staticmethod
    def get_chrome_paths() -> List[str]:
        """Get possible Chrome installation paths based on OS.
        
        Returns:
            List of possible Chrome paths
        """
        import platform
        import os
        
        system = platform.system()
        paths = []
        
        if system == "Windows":
            paths = [
                r"E:\SeleniumYtb\chrome-win64\chrome.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
        elif system == "Darwin":  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            ]
        elif system == "Linux":
            paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ]
        
        return paths
    
    @staticmethod
    def find_chrome() -> Optional[str]:
        """Find Chrome installation.
        
        Returns:
            Path to Chrome executable or None if not found
        """
        paths = SystemUtils.get_chrome_paths()
        
        for path in paths:
            if Path(path).exists():
                logger.info(f"Found Chrome at: {path}")
                return path
        
        logger.warning("Chrome not found in standard locations")
        return None
    
    @staticmethod
    def get_screen_dimensions() -> tuple[int, int]:
        """Get screen dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        try:
            import platform
            
            if platform.system() == "Windows":
                import ctypes
                user32 = ctypes.windll.user32
                return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            else:
                # Default for other systems
                return 1920, 1080
        except Exception as e:
            logger.warning(f"Could not get screen dimensions: {e}")
            return 1920, 1080


def calculate_window_position(instance_id: int, total_instances: int, 
                            max_per_row: int = 10) -> Dict[str, int]:
    """Calculate window position and size for multiple instances.
    
    Args:
        instance_id: Current instance ID (0-based)
        total_instances: Total number of instances
        max_per_row: Maximum windows per row
        
    Returns:
        Dictionary with x, y, width, height
    """
    import math
    
    screen_width, screen_height = SystemUtils.get_screen_dimensions()
    
    # Calculate grid layout
    cols = min(total_instances, max_per_row)
    rows = math.ceil(total_instances / max_per_row)
    
    # Calculate window dimensions
    window_width = screen_width // cols
    window_height = screen_height // rows
    
    # Calculate position
    col = instance_id % max_per_row
    row = instance_id // max_per_row
    
    x = col * window_width
    y = row * window_height
    
    return {
        'x': x,
        'y': y,
        'width': window_width,
        'height': window_height
    }
