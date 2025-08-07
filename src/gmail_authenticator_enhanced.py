import time
import random
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, Style, init
from .logger import get_logger

init(autoreset=True)
logger = get_logger(__name__)


class GmailAuthenticatorEnhanced:
    """Enhanced Gmail authenticator with improved error handling and anti-detection measures."""
    
    def __init__(self, browser_manager, config: Dict[str, Any]):
        self.browser_manager = browser_manager
        self.config = config
        self.gmail_settings = config.get('gmail_settings', {})
        
        # Enhanced selector system with XPath fallbacks
        self.selectors = {
            'email_input': {
                'primary': 'input[type="email"]',
                'fallbacks': [
                    'input[name="identifier"]',
                    'input[id="identifierId"]',
                    'input[autocomplete="username"]',
                    '//input[@type="email"]',
                    '//input[@name="identifier"]',
                    '//input[@aria-label[contains(., "Email")]]'
                ]
            },
            'password_input': {
                'primary': 'input[type="password"]:not([name="hiddenPassword"])',
                'fallbacks': [
                    'input[name="Passwd"]',
                    'input[name="password"]',
                    'input[jsname="YPqjbf"]',
                    '//input[@type="password" and @name!="hiddenPassword"]',
                    '//input[@name="Passwd" or @name="password"]',
                    '//div[@id="password"]//input[@type="password"]'
                ]
            },
            'next_button': {
                'primary': '#identifierNext button',
                'fallbacks': [
                    '#identifierNext',
                    'button[jsname="LgbsSe"]',
                    'div[id="identifierNext"]',
                    '//button[ancestor::div[@id="identifierNext"]]',
                    '//div[@id="identifierNext"]//button',
                    '//button[contains(@class, "VfPpkd-LgbsSe")]'
                ]
            },
            'password_next_button': {
                'primary': 'div#passwordNext button[jsname="LgbsSe"]',
                'fallbacks': [
                    '#passwordNext button',
                    '#passwordNext',
                    'div[id="passwordNext"]',
                    '//button[ancestor::div[@id="passwordNext"]]',
                    '//div[@id="passwordNext"]//button'
                ]
            }
        }
        
        # Rate limiting configuration
        self.rate_limit_config = {
            'max_attempts_per_hour': 10,
            'cooldown_minutes': 5,
            'stagger_delay_range': (30, 120)  # seconds
        }
        
        # Load or initialize rate limit tracking
        self.rate_limit_file = 'logs/rate_limit_tracker.json'
        self.load_rate_limits()
        
        # 2FA and CAPTCHA detection patterns
        self.verification_patterns = {
            '2fa': [
                'challenge/totp', 'challenge/ipp', 'challenge/az',
                'challenge/sk', 'signin/v2/challenge', '2-Step Verification',
                'Verify it\'s you', 'Enter the code', 'verification code'
            ],
            'captcha': [
                'challenge/recaptcha', 'g-recaptcha', 'recaptcha',
                'captcha', 'I\'m not a robot'
            ],
            'unusual_activity': [
                'unusual activity', 'suspicious activity', 
                'verify your identity', 'confirm it\'s you'
            ]
        }
        
        # Failed login tracking
        self.failed_accounts_file = 'logs/failed_accounts.json'
        self.load_failed_accounts()
    
    def load_rate_limits(self):
        """Load rate limit tracking data."""
        try:
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, 'r') as f:
                    self.rate_limits = json.load(f)
            else:
                self.rate_limits = {}
        except Exception as e:
            logger.error(f"Error loading rate limits: {e}")
            self.rate_limits = {}
    
    def save_rate_limits(self):
        """Save rate limit tracking data."""
        try:
            os.makedirs(os.path.dirname(self.rate_limit_file), exist_ok=True)
            with open(self.rate_limit_file, 'w') as f:
                json.dump(self.rate_limits, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving rate limits: {e}")
    
    def load_failed_accounts(self):
        """Load failed accounts tracking."""
        try:
            if os.path.exists(self.failed_accounts_file):
                with open(self.failed_accounts_file, 'r') as f:
                    self.failed_accounts = json.load(f)
            else:
                self.failed_accounts = {}
        except Exception as e:
            logger.error(f"Error loading failed accounts: {e}")
            self.failed_accounts = {}
    
    def save_failed_accounts(self):
        """Save failed accounts tracking."""
        try:
            os.makedirs(os.path.dirname(self.failed_accounts_file), exist_ok=True)
            with open(self.failed_accounts_file, 'w') as f:
                json.dump(self.failed_accounts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving failed accounts: {e}")
    
    def check_rate_limit(self, email: str) -> Tuple[bool, Optional[int]]:
        """Check if account is rate limited.
        
        Returns:
            Tuple of (is_allowed, wait_time_seconds)
        """
        current_time = datetime.now()
        
        if email not in self.rate_limits:
            self.rate_limits[email] = {
                'attempts': [],
                'last_cooldown': None
            }
        
        account_limits = self.rate_limits[email]
        
        # Clean up old attempts (older than 1 hour)
        cutoff_time = current_time - timedelta(hours=1)
        account_limits['attempts'] = [
            attempt for attempt in account_limits['attempts']
            if datetime.fromisoformat(attempt) > cutoff_time
        ]
        
        # Check if in cooldown
        if account_limits['last_cooldown']:
            cooldown_end = datetime.fromisoformat(account_limits['last_cooldown']) + \
                          timedelta(minutes=self.rate_limit_config['cooldown_minutes'])
            if current_time < cooldown_end:
                wait_seconds = int((cooldown_end - current_time).total_seconds())
                return False, wait_seconds
        
        # Check attempts in last hour
        if len(account_limits['attempts']) >= self.rate_limit_config['max_attempts_per_hour']:
            # Set cooldown
            account_limits['last_cooldown'] = current_time.isoformat()
            self.save_rate_limits()
            return False, self.rate_limit_config['cooldown_minutes'] * 60
        
        return True, None
    
    def record_login_attempt(self, email: str, success: bool):
        """Record a login attempt for rate limiting."""
        if email not in self.rate_limits:
            self.rate_limits[email] = {
                'attempts': [],
                'last_cooldown': None
            }
        
        self.rate_limits[email]['attempts'].append(datetime.now().isoformat())
        
        if not success:
            # Record failed attempt
            if email not in self.failed_accounts:
                self.failed_accounts[email] = {
                    'failures': 0,
                    'last_failure': None,
                    'reasons': []
                }
            
            self.failed_accounts[email]['failures'] += 1
            self.failed_accounts[email]['last_failure'] = datetime.now().isoformat()
        
        self.save_rate_limits()
        self.save_failed_accounts()
    
    def should_skip_account(self, email: str) -> Tuple[bool, Optional[str]]:
        """Check if account should be skipped due to repeated failures."""
        if email in self.failed_accounts:
            failures = self.failed_accounts[email]['failures']
            if failures >= 3:  # Skip after 3 failures
                return True, f"Account has failed {failures} times"
        
        return False, None
    
    def find_element_enhanced(self, driver: webdriver.Chrome, element_type: str, 
                            timeout: int = 10) -> Optional[Any]:
        """Enhanced element finding with multiple selector strategies."""
        selector_config = self.selectors.get(element_type, {})
        primary = selector_config.get('primary')
        fallbacks = selector_config.get('fallbacks', [])
        
        all_selectors = [primary] + fallbacks if primary else fallbacks
        
        for selector in all_selectors:
            try:
                # Determine if it's XPath or CSS selector
                by_type = By.XPATH if selector.startswith('//') else By.CSS_SELECTOR
                
                # Try to find element
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((by_type, selector))
                )
                
                # Verify element is visible and interactable
                if element and element.is_displayed() and element.is_enabled():
                    logger.info(f"Found {element_type} using selector: {selector}")
                    return element
                    
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        logger.error(f"Could not find {element_type} with any selector")
        return None
    
    def detect_verification_challenge(self, driver: webdriver.Chrome) -> Dict[str, bool]:
        """Detect various verification challenges."""
        challenges = {
            '2fa': False,
            'captcha': False,
            'unusual_activity': False
        }
        
        try:
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            # Check URL patterns
            for challenge_type, patterns in self.verification_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in current_url.lower() or pattern.lower() in page_source:
                        challenges[challenge_type] = True
                        break
            
            # Additional element checks for CAPTCHA
            captcha_elements = driver.find_elements(By.CSS_SELECTOR, 
                'iframe[src*="recaptcha"], div.g-recaptcha, div[id*="recaptcha"]')
            if captcha_elements:
                challenges['captcha'] = True
            
            # Check for 2FA input fields
            tfa_elements = driver.find_elements(By.CSS_SELECTOR,
                'input[name="totpPin"], input[type="tel"][aria-label*="code"], input[id*="code"]')
            if tfa_elements:
                challenges['2fa'] = True
                
        except Exception as e:
            logger.error(f"Error detecting challenges: {e}")
        
        return challenges
    
    def apply_anti_detection_measures(self, driver: webdriver.Chrome):
        """Apply various anti-detection measures."""
        try:
            # Remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Add missing image
            driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Randomize window dimensions slightly
            current_size = driver.get_window_size()
            driver.set_window_size(
                current_size['width'] + random.randint(-50, 50),
                current_size['height'] + random.randint(-50, 50)
            )
            
            # Add random mouse movements
            actions = ActionChains(driver)
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(100, 500)
                y_offset = random.randint(100, 500)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.3))
            actions.perform()
            
        except Exception as e:
            logger.debug(f"Error applying anti-detection: {e}")
    
    def human_like_typing(self, element, text: str):
        """Type text with human-like delays and corrections."""
        element.clear()
        
        for i, char in enumerate(text):
            element.send_keys(char)
            
            # Random typing speed
            delay = random.uniform(0.05, 0.25)
            
            # Occasionally make "mistakes" and correct them
            if random.random() < 0.02 and i < len(text) - 1:
                # Type wrong character
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                
                # Delete and correct
                element.send_keys('\b')
                time.sleep(random.uniform(0.1, 0.2))
            
            time.sleep(delay)
    
    def login_to_gmail(self, driver: webdriver.Chrome, account: Dict[str, Any]) -> bool:
        """Enhanced Gmail login with comprehensive error handling."""
        email = account.get('email')
        password = account.get('password')
        nickname = account.get('nickname', email)
        
        if not email or not password:
            logger.error(f"Missing credentials for {nickname}")
            return False
        
        # Check if account should be skipped
        should_skip, skip_reason = self.should_skip_account(email)
        if should_skip:
            logger.warning(f"Skipping {nickname}: {skip_reason}")
            return False
        
        # Check rate limits
        allowed, wait_time = self.check_rate_limit(email)
        if not allowed:
            logger.warning(f"Rate limited for {nickname}. Wait {wait_time} seconds")
            return False
        
        # Apply staggered delay for concurrent logins
        stagger_delay = random.uniform(*self.rate_limit_config['stagger_delay_range'])
        logger.info(f"Applying stagger delay of {stagger_delay:.1f}s for {nickname}")
        time.sleep(stagger_delay)
        
        logger.info(f"Starting enhanced login for {nickname}")
        
        try:
            # Apply anti-detection measures
            self.apply_anti_detection_measures(driver)
            
            # Navigate to Gmail using browser manager's navigation method
            if not self.browser_manager.navigate_to_url(driver, "https://accounts.google.com/signin"):
                logger.error(f"Failed to navigate to Gmail login page for {nickname}")
                self.record_login_attempt(email, False)
                return False
            time.sleep(random.uniform(2, 4))
            
            # Check for existing login
            if "mail.google.com" in driver.current_url:
                logger.info(f"Already logged in: {nickname}")
                self.record_login_attempt(email, True)
                return True
            
            # Detect initial challenges
            challenges = self.detect_verification_challenge(driver)
            if challenges['captcha']:
                logger.warning(f"CAPTCHA detected for {nickname}. Cannot proceed.")
                self.record_login_attempt(email, False)
                if email not in self.failed_accounts:
                    self.failed_accounts[email] = {'failures': 0, 'last_failure': None, 'reasons': []}
                self.failed_accounts[email]['reasons'].append('CAPTCHA')
                self.save_failed_accounts()
                return False
            
            # Enter email
            email_input = self.find_element_enhanced(driver, 'email_input', 
                                                    self.gmail_settings.get('login_timeout', 120))
            if not email_input:
                logger.error(f"Email input not found for {nickname}")
                self.record_login_attempt(email, False)
                return False
            
            self.human_like_typing(email_input, email)
            time.sleep(random.uniform(1, 2))
            
            # Click next
            next_button = self.find_element_enhanced(driver, 'next_button')
            if next_button:
                next_button.click()
            else:
                logger.error(f"Next button not found for {nickname}")
                self.record_login_attempt(email, False)
                return False
            
            # Wait for password page
            time.sleep(random.uniform(3, 5))
            
            # Check for challenges after email
            challenges = self.detect_verification_challenge(driver)
            if challenges['captcha']:
                logger.warning(f"CAPTCHA after email for {nickname}")
                self.record_login_attempt(email, False)
                if email not in self.failed_accounts:
                    self.failed_accounts[email] = {'failures': 0, 'last_failure': None, 'reasons': []}
                self.failed_accounts[email]['reasons'].append('CAPTCHA_AFTER_EMAIL')
                self.save_failed_accounts()
                return False
            
            if challenges['2fa']:
                logger.warning(f"2FA detected for {nickname}. Skipping.")
                self.record_login_attempt(email, False)
                if email not in self.failed_accounts:
                    self.failed_accounts[email] = {'failures': 0, 'last_failure': None, 'reasons': []}
                self.failed_accounts[email]['reasons'].append('2FA')
                self.save_failed_accounts()
                return False
            
            # Enter password
            password_input = self.find_element_enhanced(driver, 'password_input',
                                                      self.gmail_settings.get('login_timeout', 120))
            if not password_input:
                logger.error(f"Password input not found for {nickname}")
                self.record_login_attempt(email, False)
                return False
            
            # Focus on password field
            driver.execute_script("arguments[0].focus();", password_input)
            time.sleep(random.uniform(0.5, 1))
            
            self.human_like_typing(password_input, password)
            time.sleep(random.uniform(1, 2))
            
            # Click password next
            password_next = self.find_element_enhanced(driver, 'password_next_button')
            if password_next:
                password_next.click()
            else:
                logger.error(f"Password next button not found for {nickname}")
                self.record_login_attempt(email, False)
                return False
            
            # Wait for login completion
            time.sleep(random.uniform(3, 5))
            
            # Final verification
            max_wait = 30
            start_time = time.time()
            while time.time() - start_time < max_wait:
                current_url = driver.current_url
                
                if "mail.google.com" in current_url or "myaccount.google.com" in current_url:
                    logger.info(f"Successfully logged in: {nickname}")
                    self.record_login_attempt(email, True)
                    return True
                
                # Check for post-login challenges
                challenges = self.detect_verification_challenge(driver)
                if any(challenges.values()):
                    challenge_types = [k for k, v in challenges.items() if v]
                    logger.warning(f"Post-login challenges for {nickname}: {challenge_types}")
                    self.record_login_attempt(email, False)
                    if email not in self.failed_accounts:
                        self.failed_accounts[email] = {'failures': 0, 'last_failure': None, 'reasons': []}
                    self.failed_accounts[email]['reasons'].extend(challenge_types)
                    self.save_failed_accounts()
                    return False
                
                time.sleep(1)
            
            logger.error(f"Login timeout for {nickname}")
            self.record_login_attempt(email, False)
            return False
            
        except Exception as e:
            logger.error(f"Login error for {nickname}: {e}")
            self.record_login_attempt(email, False)
            return False
    
    def get_login_statistics(self) -> Dict[str, Any]:
        """Get statistics about login attempts and failures."""
        stats = {
            'total_accounts': len(self.rate_limits),
            'failed_accounts': len(self.failed_accounts),
            'rate_limited_accounts': 0,
            'captcha_blocks': 0,
            '2fa_blocks': 0,
            'other_failures': 0
        }
        
        current_time = datetime.now()
        
        # Count rate limited accounts
        for email, limits in self.rate_limits.items():
            if limits['last_cooldown']:
                cooldown_end = datetime.fromisoformat(limits['last_cooldown']) + \
                              timedelta(minutes=self.rate_limit_config['cooldown_minutes'])
                if current_time < cooldown_end:
                    stats['rate_limited_accounts'] += 1
        
        # Count failure reasons
        for email, data in self.failed_accounts.items():
            reasons = data.get('reasons', [])
            if 'CAPTCHA' in reasons or 'CAPTCHA_AFTER_EMAIL' in reasons:
                stats['captcha_blocks'] += 1
            elif '2FA' in reasons or '2fa' in reasons:
                stats['2fa_blocks'] += 1
            else:
                stats['other_failures'] += 1
        
        return stats
