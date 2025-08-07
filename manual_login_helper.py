#!/usr/bin/env python3
"""
Manual Login Helper
Helps bypass CAPTCHA by allowing manual login and saving session cookies
"""

import json
import time
import pickle
from pathlib import Path
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

init(autoreset=True)


class ManualLoginHelper:
    def __init__(self):
        self.cookies_dir = Path("cookies")
        self.cookies_dir.mkdir(exist_ok=True)
        
    def manual_login_and_save_cookies(self, email):
        """Allow manual login and save cookies for later use."""
        driver = None
        
        try:
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}Manual Login Helper")
            print(f"{Fore.CYAN}{'='*60}\n")
            
            # Setup Chrome
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Use local Chrome
            chrome_path = r"E:\SeleniumYtb\chrome-win64\chrome.exe"
            if Path(chrome_path).exists():
                options.binary_location = chrome_path
            
            print(f"{Fore.YELLOW}Starting Chrome for manual login...")
            driver = webdriver.Chrome(options=options)
            
            # Navigate to Gmail
            driver.get("https://gmail.com")
            
            print(f"{Fore.GREEN}Browser opened successfully!")
            print(f"\n{Fore.YELLOW}INSTRUCTIONS:")
            print(f"1. Log in manually to Gmail with account: {email}")
            print(f"2. Complete any CAPTCHA or verification steps")
            print(f"3. Wait until you see the Gmail inbox")
            print(f"4. Press Enter here when login is complete...")
            
            input(f"\n{Fore.CYAN}Press Enter after successful login: ")
            
            # Verify login success
            current_url = driver.current_url
            if "mail.google.com" in current_url:
                print(f"{Fore.GREEN}✓ Login successful!")
                
                # Save cookies
                cookies = driver.get_cookies()
                cookie_file = self.cookies_dir / f"{email.replace('@', '_at_')}_cookies.pkl"
                
                with open(cookie_file, 'wb') as f:
                    pickle.dump(cookies, f)
                
                print(f"{Fore.GREEN}✓ Cookies saved to: {cookie_file}")
                
                # Also save as JSON for inspection
                json_file = self.cookies_dir / f"{email.replace('@', '_at_')}_cookies.json"
                with open(json_file, 'w') as f:
                    json.dump(cookies, f, indent=2)
                
                return True
            else:
                print(f"{Fore.RED}✗ Login not detected. Current URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            return False
            
        finally:
            if driver:
                driver.quit()
    
    def test_saved_cookies(self, email):
        """Test if saved cookies work for login."""
        driver = None
        cookie_file = self.cookies_dir / f"{email.replace('@', '_at_')}_cookies.pkl"
        
        if not cookie_file.exists():
            print(f"{Fore.RED}No saved cookies found for {email}")
            return False
        
        try:
            print(f"{Fore.CYAN}Testing saved cookies for {email}...")
            
            # Setup Chrome
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            chrome_path = r"E:\SeleniumYtb\chrome-win64\chrome.exe"
            if Path(chrome_path).exists():
                options.binary_location = chrome_path
            
            driver = webdriver.Chrome(options=options)
            
            # First navigate to Google domain
            driver.get("https://www.google.com")
            time.sleep(2)
            
            # Load cookies
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                # Skip cookies that might cause issues
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"{Fore.YELLOW}Skipped cookie: {cookie.get('name', 'unknown')}")
            
            print(f"{Fore.GREEN}✓ Cookies loaded")
            
            # Navigate to Gmail
            driver.get("https://gmail.com")
            
            # Wait and check if logged in
            time.sleep(5)
            current_url = driver.current_url
            
            if "mail.google.com" in current_url:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]'))
                    )
                    print(f"{Fore.GREEN}✓ Successfully logged in with saved cookies!")
                    return True
                except:
                    pass
            
            print(f"{Fore.RED}✗ Cookie login failed. Current URL: {current_url}")
            return False
            
        except Exception as e:
            print(f"{Fore.RED}Error testing cookies: {e}")
            return False
            
        finally:
            if driver:
                input(f"\n{Fore.YELLOW}Press Enter to close browser...")
                driver.quit()
    
    def clear_cookies(self, email=None):
        """Clear saved cookies."""
        if email:
            cookie_file = self.cookies_dir / f"{email.replace('@', '_at_')}_cookies.pkl"
            json_file = self.cookies_dir / f"{email.replace('@', '_at_')}_cookies.json"
            
            if cookie_file.exists():
                cookie_file.unlink()
                print(f"{Fore.GREEN}✓ Deleted cookies for {email}")
            
            if json_file.exists():
                json_file.unlink()
        else:
            # Clear all cookies
            for file in self.cookies_dir.glob("*.pkl"):
                file.unlink()
            for file in self.cookies_dir.glob("*.json"):
                file.unlink()
            print(f"{Fore.GREEN}✓ All cookies cleared")


def main():
    """Run the manual login helper."""
    helper = ManualLoginHelper()
    
    while True:
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Manual Login Helper Menu")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"\n1. Manual login and save cookies")
        print(f"2. Test saved cookies")
        print(f"3. Clear saved cookies")
        print(f"4. Exit")
        
        choice = input(f"\n{Fore.YELLOW}Enter choice (1-4): ")
        
        if choice == '1':
            email = input(f"{Fore.CYAN}Enter email address: ")
            helper.manual_login_and_save_cookies(email)
            
        elif choice == '2':
            email = input(f"{Fore.CYAN}Enter email address: ")
            helper.test_saved_cookies(email)
            
        elif choice == '3':
            email = input(f"{Fore.CYAN}Enter email to clear (or press Enter for all): ")
            helper.clear_cookies(email if email else None)
            
        elif choice == '4':
            print(f"{Fore.GREEN}Goodbye!")
            break
        
        else:
            print(f"{Fore.RED}Invalid choice!")


if __name__ == "__main__":
    main()
