import time
import random
import os
import platform
import subprocess
import threading
import json
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from colorama import Fore, Style, init
from .logger import get_logger

init(autoreset=True)
logger = get_logger(__name__)


class BrowserManagerEnhanced:
    """Enhanced browser manager with anti-detection features and profile management."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser_settings = config.get('browser_settings', {})
        self.network_settings = config.get('network_settings', {})
        self.drivers = []
        self.active_instances = 0
        self.heartbeat_timers = {}
        
        # Browser profiles directory
        self.profiles_dir = 'browser_profiles'
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # User agent pool
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        # Anti-detection plugins
        self.stealth_script = """
            // Pass webdriver check
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Pass chrome check
            window.chrome = {
                runtime: {},
            };
            
            // Pass permissions check
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Pass plugins check
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Pass languages check
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Pass WebGL vendor check
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter(parameter);
            };
        """
    
    def create_browser_profile(self, email: str) -> str:
        """Create a persistent browser profile for an account."""
        profile_path = os.path.join(self.profiles_dir, email.replace('@', '_').replace('.', '_'))
        os.makedirs(profile_path, exist_ok=True)
        
        # Create preferences file with anti-detection settings
        prefs = {
            "profile": {
                "default_content_setting_values": {
                    "notifications": 1,
                    "geolocation": 1
                }
            },
            "safebrowsing": {
                "enabled": True
            },
            "webkit": {
                "webprefs": {
                    "webgl_vendor": "Intel Inc.",
                    "webgl_renderer": "Intel Iris OpenGL Engine"
                }
            }
        }
        
        prefs_file = os.path.join(profile_path, 'Default', 'Preferences')
        os.makedirs(os.path.dirname(prefs_file), exist_ok=True)
        
        try:
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f)
        except:
            pass
        
        return profile_path
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        if self.network_settings.get('user_agent_rotation', True):
            return random.choice(self.user_agents)
        return self.browser_settings.get('user_agent', self.user_agents[0])
    
    def create_driver(self, instance_id: int = 0, total_instances: int = 1, 
                     email: Optional[str] = None) -> Optional[webdriver.Chrome]:
        """Create a new Chrome WebDriver instance with enhanced anti-detection."""
        max_retries = 3
        retry_delays = [1, 3, 5]
        
        for attempt in range(max_retries):
            try:
                chrome_options = Options()
                
                # Basic options
                if self.browser_settings.get('headless', False):
                    chrome_options.add_argument('--headless=new')  # New headless mode
                
                # Window size with slight randomization
                base_width, base_height = map(int, self.browser_settings.get('window_size', '1920x1080').split('x'))
                width = base_width + random.randint(-50, 50)
                height = base_height + random.randint(-50, 50)
                chrome_options.add_argument(f'--window-size={width},{height}')
                
                # User agent
                user_agent = self.get_random_user_agent()
                chrome_options.add_argument(f'--user-agent={user_agent}')
                
                # Language settings
                chrome_options.add_argument('--lang=en-US')
                chrome_options.add_argument('--accept-lang=en-US,en;q=0.9')
                
                # Anti-detection options
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                
                # Fingerprint randomization
                if self.network_settings.get('fingerprint_randomization', True):
                    # Canvas fingerprinting protection
                    chrome_options.add_argument('--disable-features=WebRtcHideLocalIpsWithMdns')
                    
                    # WebGL randomization
                    chrome_options.add_experimental_option("prefs", {
                        "webgl_vendor": "Intel Inc.",
                        "webgl_renderer": "Intel Iris OpenGL Engine",
                        "intl.accept_languages": "en-US,en",
                        "profile.default_content_setting_values.notifications": 1,
                        "credentials_enable_service": False,
                        "profile.password_manager_enabled": False
                    })
                
                # Browser profile for persistence (temporarily disabled due to DevToolsActivePort issue)
                # if email:
                #     profile_path = self.create_browser_profile(email)
                #     chrome_options.add_argument(f'--user-data-dir={profile_path}')
                #     logger.info(f"Using browser profile: {profile_path}")
                
                # Performance and stability options
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--disable-setuid-sandbox')
                
                # Additional stealth options
                chrome_options.add_argument('--disable-infobars')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--no-default-browser-check')
                
                # Custom Chrome path
                custom_chrome_path = self.browser_settings.get('chrome_path')
                if custom_chrome_path and os.path.exists(custom_chrome_path):
                    chrome_options.binary_location = custom_chrome_path
                    logger.info(f"Using custom Chrome path: {custom_chrome_path}")
                
                # Get ChromeDriver
                chrome_version = self.get_chrome_version(custom_chrome_path)
                
                if chrome_version:
                    major_version = chrome_version.split('.')[0]
                    driver_path = ChromeDriverManager(version=f"{major_version}.0.0.0").install()
                else:
                    driver_path = ChromeDriverManager().install()
                
                # Fix driver path if needed
                if 'THIRD_PARTY_NOTICES' in driver_path:
                    # WebDriver Manager returns the wrong file, get the actual chromedriver.exe
                    driver_dir = os.path.dirname(driver_path)
                    driver_path = os.path.join(driver_dir, 'chromedriver.exe')
                    if not os.path.exists(driver_path):
                        # Try local chromedriver as fallback
                        local_driver = "./chromedriver.exe"
                        if os.path.exists(local_driver):
                            driver_path = os.path.abspath(local_driver)
                            logger.info(f"Using local ChromeDriver: {driver_path}")
                        else:
                            raise Exception(f"ChromeDriver not found at {driver_path} or locally")
                    else:
                        logger.info(f"Using ChromeDriver: {driver_path}")
                
                # Create driver
                service = Service(driver_path, port=0)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Apply stealth JavaScript
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': self.stealth_script
                })
                
                # Additional CDP commands for stealth
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": user_agent,
                    "platform": "Windows",
                    "acceptLanguage": "en-US,en;q=0.9"
                })
                
                # Navigate to about:blank first to ensure session is established
                driver.get("about:blank")
                time.sleep(0.5)
                
                # Position window
                self._position_window(driver, instance_id, total_instances)
                
                self.drivers.append(driver)
                self.active_instances += 1
                
                # Start heartbeat
                self._start_heartbeat(driver)
                
                logger.info(f"Created enhanced Chrome instance {instance_id}")
                return driver
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(retry_delays[attempt])
                    continue
                else:
                    logger.error(f"Failed to create driver after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def get_chrome_version(self, chrome_path: str = None) -> Optional[str]:
        """Get Chrome version from the custom installation."""
        if not chrome_path:
            chrome_path = self.browser_settings.get('chrome_path', r"E:\SeleniumYtb\chrome-win64\chrome.exe")
        
        if os.path.exists(chrome_path):
            try:
                result = subprocess.run([chrome_path, "--version"], 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    version_text = result.stdout.strip()
                    if "Chrome" in version_text:
                        version = version_text.split()[-1]
                        logger.info(f"Chrome version: {version}")
                        return version
            except Exception as e:
                logger.warning(f"Could not get Chrome version: {e}")
        
        return None
    
    def _position_window(self, driver: webdriver.Chrome, instance_id: int, total_instances: int):
        """Position browser window in a grid layout."""
        try:
            import math
            
            # Get screen dimensions
            screen_width = 1920
            screen_height = 1080
            
            try:
                import ctypes
                user32 = ctypes.windll.user32
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)
            except:
                pass
            
            # Calculate grid
            max_per_row = 10
            cols = min(total_instances, max_per_row)
            rows = math.ceil(total_instances / max_per_row)
            
            # Window dimensions
            win_w = int(screen_width / cols)
            win_h = int(screen_height / rows)
            
            # Position
            col = instance_id % cols
            row = instance_id // cols
            x = col * win_w
            y = row * win_h
            
            # Apply with slight randomization
            x += random.randint(-20, 20)
            y += random.randint(-20, 20)
            win_w += random.randint(-30, 30)
            win_h += random.randint(-30, 30)
            
            driver.set_window_size(win_w, win_h)
            driver.set_window_position(x, y)
            
        except Exception as e:
            logger.warning(f"Could not position window: {e}")
    
    def apply_runtime_stealth(self, driver: webdriver.Chrome):
        """Apply additional runtime stealth measures."""
        try:
            # Randomize viewport
            viewport_script = """
                Object.defineProperty(window, 'innerWidth', {
                    get: function() { return %d; }
                });
                Object.defineProperty(window, 'innerHeight', {
                    get: function() { return %d; }
                });
            """ % (
                random.randint(1000, 1920),
                random.randint(600, 1080)
            )
            driver.execute_script(viewport_script)
            
            # Randomize screen properties
            screen_script = """
                Object.defineProperty(screen, 'width', {
                    get: function() { return %d; }
                });
                Object.defineProperty(screen, 'height', {
                    get: function() { return %d; }
                });
                Object.defineProperty(screen, 'availWidth', {
                    get: function() { return %d; }
                });
                Object.defineProperty(screen, 'availHeight', {
                    get: function() { return %d; }
                });
            """ % (
                random.randint(1366, 1920),
                random.randint(768, 1080),
                random.randint(1366, 1920),
                random.randint(768, 1080)
            )
            driver.execute_script(screen_script)
            
            # Add fake media devices
            media_script = """
                navigator.mediaDevices.enumerateDevices = async () => {
                    return [
                        {deviceId: "default", kind: "audioinput", label: "Default Audio Device", groupId: "default"},
                        {deviceId: "communications", kind: "audioinput", label: "Communications Device", groupId: "communications"},
                        {deviceId: "default", kind: "videoinput", label: "Integrated Camera", groupId: "default"}
                    ];
                };
            """
            driver.execute_script(media_script)
            
        except Exception as e:
            logger.debug(f"Error applying runtime stealth: {e}")
    
    def close_driver(self, driver: webdriver.Chrome):
        """Close a driver instance."""
        try:
            if driver in self.heartbeat_timers:
                timer = self.heartbeat_timers[driver]
                timer.cancel()
                del self.heartbeat_timers[driver]
            
            if driver in self.drivers:
                self.drivers.remove(driver)
                self.active_instances -= 1
            
            driver.quit()
            logger.info("Closed Chrome instance")
            
        except Exception as e:
            logger.error(f"Error closing driver: {e}")
    
    def close_all_drivers(self):
        """Close all driver instances."""
        for driver, timer in list(self.heartbeat_timers.items()):
            timer.cancel()
        self.heartbeat_timers.clear()
        
        for driver in self.drivers[:]:
            self.close_driver(driver)
    
    def navigate_to_url(self, driver: webdriver.Chrome, url: str, timeout: int = 30):
        """Navigate to URL with stealth measures."""
        try:
            # Apply runtime stealth before navigation
            self.apply_runtime_stealth(driver)
            
            driver.get(url)
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Re-apply stealth after navigation
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': self.stealth_script
            })
            
            logger.info(f"Successfully navigated to {url}")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout navigating to {url}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def _start_heartbeat(self, driver: webdriver.Chrome):
        """Start heartbeat monitoring for a driver."""
        if driver not in self.heartbeat_timers:
            timer = threading.Timer(30.0, self.keep_alive, args=[driver])
            self.heartbeat_timers[driver] = timer
            timer.start()
    
    def keep_alive(self, driver: webdriver.Chrome):
        """Execute heartbeat check for a driver."""
        try:
            result = driver.execute_script("return 1")
            if result == 1 and driver in self.drivers:
                timer = threading.Timer(30.0, self.keep_alive, args=[driver])
                self.heartbeat_timers[driver] = timer
                timer.start()
        except:
            logger.warning("Heartbeat failed, driver may be dead")
            if driver in self.heartbeat_timers:
                del self.heartbeat_timers[driver]
    
    def wait_for_element(self, driver: webdriver.Chrome, by: By, value: str, timeout: int = 30):
        """Wait for element with timeout."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {value}")
            return None
    
    def wait_for_element_clickable(self, driver: webdriver.Chrome, by: By, value: str, timeout: int = 30):
        """Wait for element to be clickable."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Element not clickable: {value}")
            return None
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Random delay between actions."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def refresh_driver(self, driver: webdriver.Chrome) -> Optional[webdriver.Chrome]:
        """Refresh driver if not responding."""
        try:
            driver.current_url
            return driver
        except:
            logger.warning("Driver not responding, needs refresh")
            return None
