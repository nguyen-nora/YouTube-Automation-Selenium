import json
import os
import sys
from typing import Dict, Any, List
from pathlib import Path


class ConfigManager:
    """Manages configuration settings for the YouTube automation tool."""
    
    def __init__(self, config_path: str = "config.json", accounts_path: str = "accounts.json"):
        # Detect if running as frozen executable
        self.is_frozen = getattr(sys, 'frozen', False)
        self.bundle_dir = self._get_bundle_dir()
        
        # Adjust paths for frozen executable
        self.config_path = self._get_config_path(config_path)
        self.accounts_path = self._get_config_path(accounts_path)
        
        self.config = {}
        self.accounts = []
        self.load_config()
        self.load_accounts()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.create_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.create_default_config()
        return self.config
    
    def load_accounts(self) -> List[Dict[str, Any]]:
        """Load Gmail accounts from JSON file or email.txt."""
        try:
            # First check if email.txt exists
            email_txt_path = self._get_config_path('email.txt')
            if email_txt_path.exists():
                print("Loading accounts from email.txt")
                self.accounts = self._load_accounts_from_txt(email_txt_path)
            elif self.accounts_path.exists():
                with open(self.accounts_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = data.get('accounts', [])
            else:
                self.create_default_accounts()
        except Exception as e:
            print(f"Error loading accounts: {e}")
            self.create_default_accounts()
        return self.accounts
    
    def create_default_config(self):
        """Create default configuration file."""
        default_config = {
            "youtube_settings": {
                "video_urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                "loop_duration_minutes": 30,
                "view_farming_enabled": True,
                "random_delays": {"min_seconds": 5, "max_seconds": 15}
            },
            "browser_settings": {
                "headless": False,
                "window_size": "1920x1080",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "chrome_options": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            },
            "gmail_settings": {
                "login_timeout": 90,
                "max_login_attempts": 3,
                "two_factor_auth_enabled": False
            },
            "automation_settings": {
                "max_concurrent_instances": 5,
                "instance_startup_delay": 10,
                "monitoring_interval": 30,
                "auto_restart_on_crash": True
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        self.config = default_config
    
    def create_default_accounts(self):
        """Create default accounts file."""
        default_accounts = {
            "accounts": [
                {
                    "email": "your_email1@gmail.com",
                    "password": "your_password1",
                    "enabled": True,
                    "nickname": "Account 1"
                }
            ]
        }
        
        with open(self.accounts_path, 'w', encoding='utf-8') as f:
            json.dump(default_accounts, f, indent=2)
        self.accounts = default_accounts['accounts']
    
    def get_youtube_settings(self) -> Dict[str, Any]:
        """Get YouTube-specific settings."""
        return self.config.get('youtube_settings', {})
    
    def get_browser_settings(self) -> Dict[str, Any]:
        """Get browser-specific settings."""
        return self.config.get('browser_settings', {})
    
    def get_gmail_settings(self) -> Dict[str, Any]:
        """Get Gmail-specific settings."""
        return self.config.get('gmail_settings', {})
    
    def get_automation_settings(self) -> Dict[str, Any]:
        """Get automation-specific settings."""
        return self.config.get('automation_settings', {})
    
    def get_enabled_accounts(self) -> List[Dict[str, Any]]:
        """Get list of enabled accounts."""
        return [acc for acc in self.accounts if acc.get('enabled', False)]
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def save_accounts(self):
        """Save current accounts to file."""
        with open(self.accounts_path, 'w', encoding='utf-8') as f:
            json.dump({"accounts": self.accounts}, f, indent=2)
    
    def _load_accounts_from_txt(self, txt_path: Path) -> List[Dict[str, Any]]:
        """Load accounts from email.txt file.
        
        Expected format:
        email@example.com:password
        email2@example.com:password2
        
        Or:
        email@example.com password
        email2@example.com password2
        """
        accounts = []
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                
                # Try colon separator first
                if ':' in line:
                    parts = line.split(':', 1)
                else:
                    # Try space separator
                    parts = line.split(None, 1)
                
                if len(parts) >= 2:
                    email, password = parts[0].strip(), parts[1].strip()
                    accounts.append({
                        "email": email,
                        "password": password,  # Plain text password
                        "enabled": True,
                        "nickname": f"Account {i+1}"
                    })
                else:
                    print(f"Warning: Invalid format on line {i+1}: {line}")
        
        except Exception as e:
            print(f"Error loading accounts from {txt_path}: {e}")
            accounts = []
        
        return accounts 
    
    def _get_bundle_dir(self):
        """Get the base directory whether running as script or frozen executable."""
        if self.is_frozen:
            # When frozen, config files should be next to the executable
            return os.path.dirname(sys.executable)
        else:
            # Get the directory of the parent of this file (project root)
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    def _get_config_path(self, filename: str) -> Path:
        """Get the correct path for config files based on execution context."""
        if self.is_frozen:
            # Look for config files next to the executable
            return Path(os.path.join(self.bundle_dir, filename))
        else:
            # In development, use relative paths
            return Path(filename)
