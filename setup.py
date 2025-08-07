#!/usr/bin/env python3
"""
Setup script for YouTube Automation System
Helps users install dependencies and configure the system.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def print_banner():
    """Print setup banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║              YouTube Automation System - Setup                ║
║                                                                  ║
║  Automated setup and configuration tool                        ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print(f"{Fore.RED}Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"{Fore.GREEN}✓ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required Python packages."""
    print(f"{Fore.CYAN}Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(f"{Fore.GREEN}✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✗ Failed to install dependencies: {e}")
        return False


def check_chrome_installation():
    """Check if Chrome is installed."""
    print(f"{Fore.CYAN}Checking Chrome installation...")
    
    # Common Chrome installation paths on Windows
    chrome_paths = [
        r"E:\SeleniumYtb\chrome-win64\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"{Fore.GREEN}✓ Chrome found at: {path}")
            return True
    
    print(f"{Fore.YELLOW}⚠ Chrome not found in common locations")
    print(f"{Fore.YELLOW}Please ensure Google Chrome is installed")
    return False


def create_config_files():
    """Create configuration files if they don't exist."""
    print(f"{Fore.CYAN}Setting up configuration files...")
    
    # Create config.json if it doesn't exist
    if not Path("config.json").exists():
        default_config = {
            "youtube_settings": {
                "video_urls": [
                    "https://www.youtube.com/watch?v=b1MTzkp7EbQ"
                ],
                "loop_duration_minutes": 30,
                "view_farming_enabled": True,
                "random_delays": {
                    "min_seconds": 5,
                    "max_seconds": 15
                }
            },
            "browser_settings": {
                "headless": False,
                "window_size": "1920x1080",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "chrome_options": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-images"
                ]
            },
            "gmail_settings": {
                "login_timeout": 60,
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
        
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=2)
        print(f"{Fore.GREEN}✓ Created config.json")
    else:
        print(f"{Fore.GREEN}✓ config.json already exists")
    
    # Create accounts.json if it doesn't exist
    if not Path("accounts.json").exists():
        default_accounts = {
            "accounts": [
                {
                    "email": "your_email1@gmail.com",
                    "password": "your_password1",
                    "enabled": True,
                    "nickname": "Account 1"
                },
                {
                    "email": "your_email2@gmail.com",
                    "password": "your_password2",
                    "enabled": True,
                    "nickname": "Account 2"
                }
            ]
        }
        
        with open("accounts.json", "w") as f:
            json.dump(default_accounts, f, indent=2)
        print(f"{Fore.GREEN}✓ Created accounts.json")
    else:
        print(f"{Fore.GREEN}✓ accounts.json already exists")


def create_directories():
    """Create necessary directories."""
    print(f"{Fore.CYAN}Creating directories...")
    
    directories = ["chrome_data", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"{Fore.GREEN}✓ Created directory: {directory}")


def test_selenium_installation():
    """Test if Selenium is working properly."""
    print(f"{Fore.CYAN}Testing Selenium installation...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Test ChromeDriver installation
        driver_path = ChromeDriverManager().install()
        print(f"{Fore.GREEN}✓ ChromeDriver installed at: {driver_path}")
        
        # Test basic WebDriver creation (headless)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"{Fore.GREEN}✓ Selenium test successful (page title: {title})")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Selenium test failed: {e}")
        return False


def show_next_steps():
    """Show next steps for the user."""
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                        Next Steps                           ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    steps = [
        "1. Edit accounts.json and add your Gmail credentials",
        "2. Edit config.json and add your YouTube video URLs",
        "3. Test with a single account first: python main.py --debug",
        "4. Run the full automation: python main.py",
        "5. Monitor the output for any issues",
        "",
        "Important:",
        "• Ensure your Gmail accounts have 2FA disabled or configured",
        "• Use strong passwords and keep credentials secure",
        "• Monitor your accounts for any suspicious activity",
        "• Use responsibly and in accordance with Terms of Service"
    ]
    
    for step in steps:
        if step.startswith("Important:"):
            print(f"{Fore.YELLOW}{step}")
        elif step.startswith("•"):
            print(f"{Fore.YELLOW}  {step}")
        elif step:
            print(f"{Fore.WHITE}{step}")
        else:
            print()


def main():
    """Main setup function."""
    print_banner()
    
    print(f"{Fore.CYAN}Starting setup process...\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print(f"{Fore.RED}Setup failed at dependency installation")
        sys.exit(1)
    
    # Check Chrome installation
    if not check_chrome_installation():
        print(f"{Fore.YELLOW}Warning: Chrome not found. Please install Google Chrome.")
    
    # Create configuration files
    create_config_files()
    
    # Create directories
    create_directories()
    
    # Test Selenium
    if not test_selenium_installation():
        print(f"{Fore.YELLOW}Warning: Selenium test failed. You may need to troubleshoot.")
    
    print(f"\n{Fore.GREEN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                    Setup Completed!                        ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    show_next_steps()


if __name__ == "__main__":
    main() 