import time
import random
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from colorama import Fore, Style, init

init(autoreset=True)


class GmailAuthenticator:
    """Handles Gmail authentication and login processes with improved selector handling."""
    
    def __init__(self, browser_manager, config: Dict[str, Any]):
        self.browser_manager = browser_manager
        self.config = config
        self.gmail_settings = config.get('gmail_settings', {})
        
        # Primary selectors (updated based on diagnostics)
        self.selectors = {
            'email_input': 'input[type="email"]',
            'password_input': 'input[type="password"]',
            'next_button': '#identifierNext button',
            'password_next_button': 'div#passwordNext button[jsname="LgbsSe"]',
            'signin_button': 'button[jsname="LgbsSe"]',
            'account_picker': 'div[data-email]',
            'use_another_account': 'div[aria-label*="Use another account"]',
            'add_account': 'li[jsname="bN97Pc"]'
        }
        
        # Fallback selectors for critical elements
        self.fallback_selectors = {
            'email_input': [
                'input[type="email"]',
                'input[name="identifier"]',
                'input[id="identifierId"]',
                'input[autocomplete="username"]',
                'input[aria-label*="Email"]'
            ],
            'password_input': [
                'input[type="password"]',
                'input[name="Passwd"]',
                'input[jsname="YPqjbf"]',
                'input[name="password"]',
                'input[autocomplete="current-password"]'
            ],
            'next_button': [
                '#identifierNext button',
                'div[id="identifierNext"]',
                'button[jsname="LgbsSe"]',
                '#identifierNext'
            ],
            'password_next_button': [
                'div#passwordNext button[jsname="LgbsSe"]',
                '#passwordNext button',
                'div[id="passwordNext"]',
                '#passwordNext',
                'button[jsname="LgbsSe"]'
            ]
        }
    
    def find_element_with_fallbacks(self, driver: webdriver.Chrome, element_type: str, timeout: int = 10) -> Optional[Any]:
        """Try multiple selectors until one works."""
        selectors = self.fallback_selectors.get(element_type, [self.selectors.get(element_type)])
        
        for selector in selectors:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if element and element.is_displayed():
                    print(f"{Fore.GREEN}[Gmail Auth] Found {element_type} using selector: {selector}{Style.RESET_ALL}")
                    return element
            except TimeoutException:
                continue
            except Exception as e:
                print(f"{Fore.YELLOW}[Gmail Auth] Error with selector {selector}: {e}{Style.RESET_ALL}")
                continue
        
        print(f"{Fore.RED}[Gmail Auth] Could not find {element_type} with any selector{Style.RESET_ALL}")
        return None
    
    def detect_recaptcha(self, driver: webdriver.Chrome) -> bool:
        """Detect if reCAPTCHA challenge is present."""
        try:
            current_url = driver.current_url
            if "challenge/recaptcha" in current_url:
                return True
            
            # Check for reCAPTCHA iframe
            recaptcha_selectors = [
                'iframe[src*="recaptcha"]',
                'div.g-recaptcha',
                'div[id*="recaptcha"]'
            ]
            
            for selector in recaptcha_selectors:
                try:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def login_to_gmail(self, driver: webdriver.Chrome, account: Dict[str, Any]) -> bool:
        """Login to Gmail with the provided account credentials."""
        email = account.get('email')
        password = account.get('password')
        nickname = account.get('nickname', email)
        
        if not email or not password:
            print(f"{Fore.RED}[Gmail Auth] Missing credentials for {nickname}")
            return False
        
        print(f"{Fore.CYAN}[Gmail Auth] Attempting to login: {nickname}")
        
        max_attempts = self.gmail_settings.get('max_login_attempts', 3)
        retry_delay = [1, 2, 4]  # Exponential backoff
        
        for attempt in range(max_attempts):
            try:
                # Refresh driver if needed
                driver = self.browser_manager.refresh_driver(driver)
                if driver is None:
                    print(f"{Fore.RED}[Gmail Auth] Failed to refresh driver for {nickname}")
                    return False

                # Navigate to Gmail
                if not self.browser_manager.navigate_to_url(driver, "https://gmail.com"):
                    if attempt < max_attempts - 1:
                        print(f"{Fore.YELLOW}[Gmail Auth] Navigation failed, retrying... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(retry_delay[min(attempt, len(retry_delay)-1)])
                        continue
                    return False
                
                # Wait for page to settle
                self.browser_manager.random_delay(1, 2)
                
                # Check for reCAPTCHA
                if self.detect_recaptcha(driver):
                    print(f"{Fore.YELLOW}[Gmail Auth] reCAPTCHA detected for {nickname}. Cannot proceed automatically.")
                    return False
                
                # Check if already logged in
                if self.is_already_logged_in(driver, email):
                    print(f"{Fore.GREEN}[Gmail Auth] Already logged in: {nickname}")
                    return True
                
                # Handle account selection if multiple accounts are present
                if self.handle_account_selection(driver, email):
                    print(f"{Fore.GREEN}[Gmail Auth] Account selected: {nickname}")
                    return True
                
                # Enter email
                if not self.enter_email(driver, email):
                    if attempt < max_attempts - 1:
                        print(f"{Fore.YELLOW}[Gmail Auth] Email entry failed, retrying... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(retry_delay[min(attempt, len(retry_delay)-1)])
                        continue
                    return False
                
                # Wait for password page to load
                if not self.wait_for_password_page(driver):
                    if attempt < max_attempts - 1:
                        print(f"{Fore.YELLOW}[Gmail Auth] Password page not loaded, retrying... (attempt {attempt + 1}/{max_attempts})")
                        continue
                    return False
                
                # Check for reCAPTCHA again
                if self.detect_recaptcha(driver):
                    print(f"{Fore.YELLOW}[Gmail Auth] reCAPTCHA detected after email entry for {nickname}.")
                    return False
                
                # Check for 2-step verification before entering password
                if self.detect_two_step_verification(driver):
                    print(f"{Fore.YELLOW}[Gmail Auth] 2-step verification detected for {nickname}. Skipping this account.")
                    return False
                
                # Enter password
                if not self.enter_password(driver, password):
                    if attempt < max_attempts - 1:
                        print(f"{Fore.YELLOW}[Gmail Auth] Password entry failed, retrying... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(retry_delay[min(attempt, len(retry_delay)-1)])
                        continue
                    return False
                
                # Check for 2-step verification after password
                if self.detect_two_step_verification(driver):
                    print(f"{Fore.YELLOW}[Gmail Auth] 2-step verification detected for {nickname}. Skipping this account.")
                    return False
                
                # Check for successful login
                if self.verify_login_success(driver, email):
                    print(f"{Fore.GREEN}[Gmail Auth] Successfully logged in: {nickname}")
                    return True
                else:
                    if attempt < max_attempts - 1:
                        print(f"{Fore.YELLOW}[Gmail Auth] Login verification failed, retrying... (attempt {attempt + 1}/{max_attempts})")
                        continue
                    print(f"{Fore.RED}[Gmail Auth] Login verification failed: {nickname}")
                    return False
                    
            except TimeoutException as e:
                if attempt < max_attempts - 1:
                    print(f"{Fore.YELLOW}[Gmail Auth] Timeout during login, retrying... (attempt {attempt + 1}/{max_attempts})")
                    self.browser_manager.navigate_to_url(driver, "https://accounts.google.com/signin")
                    time.sleep(retry_delay[min(attempt, len(retry_delay)-1)])
                    continue
                else:
                    print(f"{Fore.RED}[Gmail Auth] Timeout error during login for {nickname}: {e}")
                    return False
            except Exception as e:
                print(f"{Fore.RED}[Gmail Auth] Error during login for {nickname}: {e}")
                return False
        
        print(f"{Fore.RED}[Gmail Auth] Failed to login after {max_attempts} attempts for {nickname}")
        return False
    
    def is_already_logged_in(self, driver: webdriver.Chrome, email: str) -> bool:
        """Check if already logged in with the target email."""
        try:
            current_url = driver.current_url
            if "accounts.google.com" in current_url:
                return False
            
            # Look for the account avatar or email indicator
            avatar_selectors = [
                'img[alt*="Profile picture"]',
                'div[aria-label*="Account"]',
                f'div[data-email="{email}"]',
                'a[aria-label*="Google Account"]'
            ]
            
            for selector in avatar_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}[Gmail Auth] Error checking login status: {e}")
            return False
    
    def handle_account_selection(self, driver: webdriver.Chrome, email: str) -> bool:
        """Handle account selection if multiple accounts are available."""
        try:
            # Look for account picker
            account_selectors = [
                f'div[data-email="{email}"]',
                f'div[aria-label*="{email}"]',
                f'div[title*="{email}"]'
            ]
            
            for selector in account_selectors:
                try:
                    element = self.browser_manager.wait_for_element(driver, By.CSS_SELECTOR, selector, 5)
                    if element:
                        element.click()
                        self.browser_manager.random_delay(2, 4)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}[Gmail Auth] Error in account selection: {e}")
            return False
    
    def enter_email(self, driver: webdriver.Chrome, email: str) -> bool:
        """Enter email address in the login form."""
        try:
            # Find email input using fallback selectors
            email_input = self.find_element_with_fallbacks(driver, 'email_input', 
                                                          self.gmail_settings.get('login_timeout', 90))
            
            if not email_input:
                print(f"{Fore.RED}[Gmail Auth] Email input field not found")
                return False
            
            # Clear and enter email
            email_input.clear()
            self.browser_manager.random_delay(0.5, 1.5)
            
            # Type email with human-like delays
            for char in email:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.browser_manager.random_delay(1, 2)
            
            # Click next button using fallbacks
            next_button = self.find_element_with_fallbacks(driver, 'next_button', 10)
            
            if next_button:
                # Check if clickable
                try:
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['next_button']))
                    )
                except:
                    pass
                
                next_button.click()
                return True
            else:
                print(f"{Fore.RED}[Gmail Auth] Next button not found after email entry")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[Gmail Auth] Error entering email: {e}")
            return False
    
    def enter_password(self, driver: webdriver.Chrome, password: str) -> bool:
        """Enter password in the login form."""
        try:
            # Find password input using fallback selectors
            password_input = self.find_element_with_fallbacks(driver, 'password_input',
                                                            self.gmail_settings.get('login_timeout', 90))
            
            if not password_input:
                print(f"{Fore.RED}[Gmail Auth] Password input field not found")
                return False
            
            # Ensure field is clickable
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['password_input']))
                )
            except:
                # Try JavaScript focus as fallback
                driver.execute_script("arguments[0].focus();", password_input)
            
            # Clear field
            driver.execute_script("arguments[0].value = '';", password_input)
            
            # Type password slowly to avoid detection
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.browser_manager.random_delay(1, 2)
            
            # Click next button using fallbacks
            next_button = self.find_element_with_fallbacks(driver, 'password_next_button', 10)
            
            if next_button:
                next_button.click()
                return True
            else:
                print(f"{Fore.RED}[Gmail Auth] Next button not found after password entry")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[Gmail Auth] Error entering password: {e}")
            return False
    
    def verify_login_success(self, driver: webdriver.Chrome, email: str) -> bool:
        """Verify that login was successful."""
        try:
            # Wait for redirect to Gmail
            WebDriverWait(driver, 30).until(
                lambda d: "mail.google.com" in d.current_url or "gmail.com" in d.current_url
            )
            
            # Additional verification - check for Gmail interface elements
            gmail_indicators = [
                'div[role="main"]',
                'div[data-tooltip="Compose"]',
                'div[aria-label="Inbox"]',
                'div[gh="cm"]'  # Compose button
            ]
            
            for indicator in gmail_indicators:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, indicator)
                    if element:
                        return True
                except NoSuchElementException:
                    continue
            
            return True  # If we reached Gmail URL, assume success
            
        except TimeoutException:
            print(f"{Fore.RED}[Gmail Auth] Timeout waiting for Gmail redirect")
            return False
        except Exception as e:
            print(f"{Fore.RED}[Gmail Auth] Error verifying login: {e}")
            return False
    
    def wait_for_password_page(self, driver: webdriver.Chrome) -> bool:
        """Wait for password page to load by checking URL and password field."""
        try:
            # Wait for URL to change from identifier page
            WebDriverWait(driver, self.gmail_settings.get('login_timeout', 90)).until(
                lambda d: "identifier" not in d.current_url or 
                         "challenge/pwd" in d.current_url or
                         "signin/v2/challenge" in d.current_url
            )
            
            # Also wait for password field to be present
            password_field = self.find_element_with_fallbacks(driver, 'password_input', 10)
            
            if password_field:
                # Add a small delay to ensure page is fully loaded
                time.sleep(2)
                return True
            
            return False
            
        except TimeoutException:
            print(f"{Fore.RED}[Gmail Auth] Timeout waiting for password page")
            return False
    
    def detect_two_step_verification(self, driver: webdriver.Chrome) -> bool:
        """Detect if 2-step verification page is shown."""
        try:
            # Look for 2FA input field indicators
            twofa_selectors = [
                'input[name="totpPin"]',
                'input[aria-label*="verification"]',
                'input[type="tel"][aria-label*="code"]',
                'input[id*="code"]',
                'div[data-form-action-uri*="challenge"]',
                'h1[id="headingText"]:has-text("2-Step Verification")',
                'span:has-text("Verify it\'s you")',
                'div:has-text("Enter the code")'
            ]
            
            # Quick check without waiting
            for selector in twofa_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        return True
                except:
                    continue
            
            # Also check URL patterns for 2FA
            current_url = driver.current_url
            twofa_url_patterns = [
                "challenge/totp",
                "challenge/ipp",
                "challenge/az",
                "challenge/sk",
                "signin/v2/challenge"
            ]
            
            for pattern in twofa_url_patterns:
                if pattern in current_url and "pwd" not in current_url:
                    return True
            
            return False
            
        except Exception as e:
            # Don't fail on detection errors
            return False
    
    def logout_from_gmail(self, driver: webdriver.Chrome) -> bool:
        """Logout from Gmail account."""
        try:
            # Navigate to Gmail if not already there
            if "mail.google.com" not in driver.current_url:
                self.browser_manager.navigate_to_url(driver, "https://gmail.com")
            
            # Click on account avatar
            avatar_selectors = [
                'img[alt*="Profile picture"]',
                'div[aria-label*="Account"]',
                'div[data-tooltip*="Account"]',
                'a[aria-label*="Google Account"]'
            ]
            
            for selector in avatar_selectors:
                try:
                    element = self.browser_manager.wait_for_element_clickable(driver, By.CSS_SELECTOR, selector, 5)
                    if element:
                        element.click()
                        self.browser_manager.random_delay(1, 2)
                        break
                except:
                    continue
            
            # Click sign out
            signout_selectors = [
                'a[href*="Logout"]',
                'div[aria-label*="Sign out"]',
                'div[data-tooltip*="Sign out"]',
                'a:contains("Sign out")'
            ]
            
            for selector in signout_selectors:
                try:
                    element = self.browser_manager.wait_for_element_clickable(driver, By.CSS_SELECTOR, selector, 5)
                    if element:
                        element.click()
                        self.browser_manager.random_delay(2, 4)
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}[Gmail Auth] Error during logout: {e}")
            return False
