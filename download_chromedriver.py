#!/usr/bin/env python3
"""
Simple ChromeDriver Download Script
Downloads a known working ChromeDriver version.
"""

import os
import requests
import zipfile
from colorama import Fore, Style, init

init(autoreset=True)


def download_chromedriver():
    """Download a known working ChromeDriver version."""
    print(f"{Fore.CYAN}Downloading ChromeDriver...")
    
    # Use ChromeDriver version that matches Chrome 138
    driver_version = "138.0.7204.168"
    download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{driver_version}/win64/chromedriver-win64.zip"
    
    try:
        print(f"{Fore.CYAN}Downloading ChromeDriver {driver_version}...")
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            # Save the zip file
            zip_path = "chromedriver-win64.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print(f"{Fore.GREEN}✓ Downloaded ChromeDriver zip file")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('.')
            
            print(f"{Fore.GREEN}✓ Extracted ChromeDriver")
            
            # Move chromedriver.exe to current directory
            extracted_path = "chromedriver-win64/chromedriver.exe"
            if os.path.exists(extracted_path):
                import shutil
                shutil.move(extracted_path, "chromedriver.exe")
                print(f"{Fore.GREEN}✓ Moved chromedriver.exe to current directory")
                
                # Clean up
                import shutil
                shutil.rmtree("chromedriver-win64", ignore_errors=True)
                os.remove(zip_path)
                print(f"{Fore.GREEN}✓ Cleaned up temporary files")
                
                return True
            else:
                print(f"{Fore.RED}✗ chromedriver.exe not found in extracted files")
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
    """Main function."""
    print(f"{Fore.CYAN}ChromeDriver Download Tool{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=========================={Style.RESET_ALL}\n")
    
    # Download ChromeDriver
    if download_chromedriver():
        # Test the downloaded ChromeDriver
        if test_chromedriver():
            print(f"\n{Fore.GREEN}✓ ChromeDriver setup completed successfully!")
            print(f"{Fore.CYAN}You can now run the main automation:")
            print(f"{Fore.WHITE}python main.py")
        else:
            print(f"\n{Fore.RED}ChromeDriver test failed. Please check the error messages above.")
    else:
        print(f"\n{Fore.RED}Failed to download ChromeDriver.")
        print(f"{Fore.YELLOW}Please try manual installation:")
        print(f"1. Go to https://chromedriver.chromium.org/")
        print(f"2. Download ChromeDriver for your Chrome version")
        print(f"3. Extract chromedriver.exe to this directory")


if __name__ == "__main__":
    main() 