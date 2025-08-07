#!/usr/bin/env python3
"""
ChromeDriver Fix Script
Manually download and setup ChromeDriver to fix compatibility issues.
"""

import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def print_banner():
    """Print fix banner."""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                ChromeDriver Fix Tool                        ║
║                                                                  ║
║  Manually download and setup ChromeDriver                      ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def get_chrome_version():
    """Get Chrome version from the custom installation."""
    chrome_path = r"E:\SeleniumYtb\chrome-win64\chrome.exe"
    
    if os.path.exists(chrome_path):
        try:
            import subprocess
            result = subprocess.run([chrome_path, "--version"], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                version_text = result.stdout.strip()
                # Extract version number (e.g., "Google Chrome 138.0.7204.168")
                if "Chrome" in version_text:
                    version = version_text.split()[-1]
                    print(f"{Fore.GREEN}✓ Chrome version: {version}")
                    return version
        except Exception as e:
            print(f"{Fore.YELLOW}Could not get Chrome version: {e}")
    
    # Fallback to a common version
    print(f"{Fore.YELLOW}Using fallback Chrome version: 120.0.6099.109")
    return "120.0.6099.109"


def download_chromedriver(version):
    """Download ChromeDriver for the specified Chrome version."""
    print(f"{Fore.CYAN}Downloading ChromeDriver for Chrome version {version}...")
    
    # Extract major version
    major_version = version.split('.')[0]
    
    # ChromeDriver download URL
    base_url = "https://chromedriver.storage.googleapis.com"
    
    # Try to get the latest version for this major version
    try:
        # Get the latest version info
        version_url = f"{base_url}/LATEST_RELEASE_{major_version}"
        response = requests.get(version_url, timeout=10)
        if response.status_code == 200:
            driver_version = response.text.strip()
            print(f"{Fore.GREEN}✓ Found ChromeDriver version: {driver_version}")
        else:
            # Fallback to a known working version
            driver_version = "120.0.6099.109"
            print(f"{Fore.YELLOW}Using fallback ChromeDriver version: {driver_version}")
    except Exception as e:
        print(f"{Fore.YELLOW}Could not get latest version, using fallback: {e}")
        driver_version = "120.0.6099.109"
    
    # Download URL
    download_url = f"{base_url}/{driver_version}/chromedriver_win64.zip"
    
    try:
        print(f"{Fore.CYAN}Downloading from: {download_url}")
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            # Save the zip file
            zip_path = "chromedriver_win64.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print(f"{Fore.GREEN}✓ Downloaded ChromeDriver zip file")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('.')
            
            print(f"{Fore.GREEN}✓ Extracted ChromeDriver")
            
            # Clean up zip file
            os.remove(zip_path)
            print(f"{Fore.GREEN}✓ Cleaned up zip file")
            
            # Verify chromedriver.exe exists
            if os.path.exists("chromedriver.exe"):
                print(f"{Fore.GREEN}✓ ChromeDriver setup complete!")
                return True
            else:
                print(f"{Fore.RED}✗ ChromeDriver.exe not found after extraction")
                return False
                
        else:
            print(f"{Fore.RED}✗ Failed to download ChromeDriver (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}✗ Error downloading ChromeDriver: {e}")
        return False


def test_chromedriver():
    """Test the downloaded ChromeDriver."""
    print(f"{Fore.CYAN}Testing ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Use custom Chrome path
        custom_chrome_path = r"E:\SeleniumYtb\chrome-win64\chrome.exe"
        if os.path.exists(custom_chrome_path):
            chrome_options.binary_location = custom_chrome_path
        
        # Test with local chromedriver.exe
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"{Fore.GREEN}✓ ChromeDriver test successful (title: {title})")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ ChromeDriver test failed: {e}")
        return False


def main():
    """Main fix function."""
    print_banner()
    
    print(f"{Fore.CYAN}Starting ChromeDriver fix process...\n")
    
    # Get Chrome version
    chrome_version = get_chrome_version()
    
    # Download ChromeDriver
    if download_chromedriver(chrome_version):
        # Test the downloaded ChromeDriver
        if test_chromedriver():
            print(f"\n{Fore.GREEN}╔══════════════════════════════════════════════════════════════╗")
            print(f"║                Fix Completed Successfully!                ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}You can now run the main automation:")
            print(f"{Fore.WHITE}python main.py")
        else:
            print(f"\n{Fore.RED}ChromeDriver test failed. Please check the error messages above.")
    else:
        print(f"\n{Fore.RED}Failed to download ChromeDriver. Please try manual installation.")
        print(f"{Fore.YELLOW}Manual steps:")
        print(f"1. Go to https://chromedriver.chromium.org/")
        print(f"2. Download ChromeDriver for Chrome version {chrome_version}")
        print(f"3. Extract chromedriver.exe to this directory")


if __name__ == "__main__":
    main() 