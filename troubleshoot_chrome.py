#!/usr/bin/env python3
"""
ChromeDriver Troubleshooting Script
Helps diagnose and fix ChromeDriver compatibility issues.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def print_banner():
    """Print troubleshooting banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║              ChromeDriver Troubleshooting Tool                ║
║                                                                  ║
║  Diagnose and fix ChromeDriver compatibility issues            ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def get_system_info():
    """Get system information."""
    print(f"{Fore.CYAN}System Information:{Style.RESET_ALL}")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.architecture()[0]}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Python Architecture: {platform.architecture()[0]}")
    print()


def find_chrome_installations():
    """Find Chrome installations on the system."""
    print(f"{Fore.CYAN}Chrome Installations:{Style.RESET_ALL}")
    
    chrome_paths = [
        r"E:\SeleniumYtb\chrome-win64\chrome.exe",  # Custom path
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe"
    ]
    
    found_chrome = False
    for path in chrome_paths:
        if os.path.exists(path):
            found_chrome = True
            print(f"  ✓ Found: {path}")
            
            # Try to get version
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"    Version: {version}")
                    
                    # Check if it's 32-bit or 64-bit
                    try:
                        # This is a rough check - in practice, you'd need to check the binary
                        if "x86" in path or "(x86)" in path:
                            print(f"    Architecture: 32-bit")
                        else:
                            print(f"    Architecture: 64-bit")
                    except:
                        print(f"    Architecture: Unknown")
                        
            except Exception as e:
                print(f"    Version: Could not determine ({e})")
        else:
            print(f"  ✗ Not found: {path}")
    
    if not found_chrome:
        print(f"  {Fore.RED}No Chrome installations found!")
        print(f"  {Fore.YELLOW}Please install Google Chrome first.")
    
    print()
    return found_chrome


def check_chromedriver():
    """Check ChromeDriver installation."""
    print(f"{Fore.CYAN}ChromeDriver Status:{Style.RESET_ALL}")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to install/get ChromeDriver
        driver_path = ChromeDriverManager().install()
        print(f"  ✓ ChromeDriver installed: {driver_path}")
        
        # Check if it's executable
        if os.path.exists(driver_path):
            print(f"  ✓ ChromeDriver file exists")
            
            # Try to get version
            try:
                result = subprocess.run([driver_path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"  ✓ ChromeDriver version: {version}")
                else:
                    print(f"  ✗ Could not get ChromeDriver version")
            except Exception as e:
                print(f"  ✗ Error getting ChromeDriver version: {e}")
        else:
            print(f"  ✗ ChromeDriver file not found")
            
    except Exception as e:
        print(f"  ✗ ChromeDriver installation failed: {e}")
    
    print()


def test_selenium_installation():
    """Test Selenium installation."""
    print(f"{Fore.CYAN}Selenium Test:{Style.RESET_ALL}")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print(f"  ✓ Selenium imported successfully")
        
        # Test basic WebDriver creation
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Try to use custom Chrome path
        custom_chrome_path = r"E:\SeleniumYtb\chrome-win64\chrome.exe"
        if os.path.exists(custom_chrome_path):
            chrome_options.binary_location = custom_chrome_path
            print(f"  ✓ Using custom Chrome path: {custom_chrome_path}")
        
        print(f"  ✓ Attempting to create WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print(f"  ✓ WebDriver created successfully")
        
        # Test navigation
        driver.get("https://www.google.com")
        title = driver.title
        print(f"  ✓ Navigation test successful (title: {title})")
        
        driver.quit()
        print(f"  ✓ WebDriver closed successfully")
        print(f"  {Fore.GREEN}✓ Selenium test completed successfully!")
        
    except Exception as e:
        print(f"  {Fore.RED}✗ Selenium test failed: {e}")
        
        # Provide specific advice for common errors
        if "WinError 193" in str(e):
            print(f"  {Fore.YELLOW}Troubleshooting WinError 193:")
            print(f"    - This indicates architecture mismatch")
            print(f"    - Ensure Chrome and ChromeDriver are both 32-bit or both 64-bit")
            print(f"    - Try downloading ChromeDriver manually from:")
            print(f"      https://chromedriver.chromium.org/")
        
        elif "chromedriver" in str(e).lower():
            print(f"  {Fore.YELLOW}ChromeDriver issues detected:")
            print(f"    - Try updating Chrome to latest version")
            print(f"    - Download matching ChromeDriver version")
            print(f"    - Check PATH environment variable")
    
    print()


def suggest_solutions():
    """Suggest solutions based on findings."""
    print(f"{Fore.CYAN}Suggested Solutions:{Style.RESET_ALL}")
    
    solutions = [
        "1. Update Chrome to the latest version",
        "2. Download ChromeDriver that matches your Chrome version:",
        "   https://chromedriver.chromium.org/",
        "3. Ensure ChromeDriver is in your PATH or in the project directory",
        "4. If using custom Chrome installation, verify the path is correct",
        "5. Try running as administrator if you encounter permission issues",
        "6. Check Windows Defender or antivirus isn't blocking ChromeDriver",
        "",
        "Manual ChromeDriver Setup:",
        "1. Go to https://chromedriver.chromium.org/",
        "2. Download the version matching your Chrome version",
        "3. Extract chromedriver.exe to your project directory",
        "4. Or add it to your system PATH",
        "",
        "Alternative: Use webdriver-manager (automatic):",
        "pip install --upgrade webdriver-manager"
    ]
    
    for solution in solutions:
        if solution.startswith("1.") or solution.startswith("2.") or solution.startswith("3.") or solution.startswith("4.") or solution.startswith("5.") or solution.startswith("6."):
            print(f"  {Fore.WHITE}{solution}")
        elif solution.startswith("Manual") or solution.startswith("Alternative"):
            print(f"  {Fore.YELLOW}{solution}")
        elif solution.startswith("   ") or solution.startswith("  "):
            print(f"  {Fore.WHITE}{solution}")
        elif solution:
            print(f"  {Fore.CYAN}{solution}")
        else:
            print()


def main():
    """Main troubleshooting function."""
    print_banner()
    
    print(f"{Fore.CYAN}Starting ChromeDriver troubleshooting...\n")
    
    # Get system information
    get_system_info()
    
    # Find Chrome installations
    chrome_found = find_chrome_installations()
    
    # Check ChromeDriver
    check_chromedriver()
    
    # Test Selenium
    test_selenium_installation()
    
    # Suggest solutions
    suggest_solutions()
    
    print(f"{Fore.GREEN}╔══════════════════════════════════════════════════════════════╗")
    print(f"║                Troubleshooting Complete!                    ║")
    print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 