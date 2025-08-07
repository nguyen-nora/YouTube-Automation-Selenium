import time
import random
import os
import sys
import platform
import subprocess
import threading
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from colorama import Fore, Style, init

init(autoreset=True)


class BrowserManager:
    """Manages Chrome browser instances and WebDriver operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser_settings = config.get('browser_settings', {})
        self.drivers = []
        self.active_instances = 0
        self.heartbeat_timers = {}  # Store heartbeat timers for each driver
        
        # Detect if running as frozen executable
        self.is_frozen = getattr(sys, 'frozen', False)
        self.bundle_dir = self._get_bundle_dir()
    
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
                    # Extract version number (e.g., "Google Chrome 138.0.7204.168")
                    if "Chrome" in version_text:
                        version = version_text.split()[-1]
                        print(f"{Fore.GREEN}[Browser Manager] Chrome version: {version}")
                        return version
            except Exception as e:
                print(f"{Fore.YELLOW}[Browser Manager] Could not get Chrome version: {e}")
        
        # Fallback to None - let ChromeDriverManager handle it
        print(f"{Fore.YELLOW}[Browser Manager] Could not determine Chrome version")
        return None
    
    def create_driver(self, instance_id: int = 0, total_instances: int = 1) -> Optional[webdriver.Chrome]:
        """Create a new Chrome WebDriver instance and arrange it on the screen."""
        # Retry configuration
        max_retries = 3
        retry_delays = [0.5, 2, 5]  # Exponential backoff delays in seconds
        
        for attempt in range(max_retries):
            try:
                chrome_options = Options()
                
                # Apply browser settings
                if self.browser_settings.get('headless', False):
                    chrome_options.add_argument('--headless')
                
                window_size = self.browser_settings.get('window_size', '1920x1080')
                chrome_options.add_argument(f'--window-size={window_size}')
                
                user_agent = self.browser_settings.get('user_agent')
                if user_agent:
                    chrome_options.add_argument(f'--user-agent={user_agent}')
                
                # Add custom Chrome options
                for option in self.browser_settings.get('chrome_options', []):
                    chrome_options.add_argument(option)
                
                # Force Chrome to use English language
                chrome_options.add_argument('--lang=en-US')
                chrome_options.add_argument('--lang=en')
                chrome_options.add_argument('--accept-lang=en-US,en')
                chrome_options.add_experimental_option('prefs', {
                    'intl.accept_languages': 'en,en_US,en-US'
                })
                # Set environment variable for language
                os.environ['LANG'] = 'en_US.UTF-8'
                os.environ['LANGUAGE'] = 'en_US:en'
                os.environ['LC_ALL'] = 'en_US.UTF-8'
                
                # Additional options for automation detection avoidance
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                
                # Add additional options to fix DevTools issues
                chrome_options.add_argument('--remote-debugging-port=0')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--no-first-run')
                chrome_options.add_argument('--no-default-browser-check')
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-software-rasterizer')
                
                # Try to use custom Chrome path if specified
                custom_chrome_path = self.browser_settings.get('chrome_path')
                if custom_chrome_path and os.path.exists(custom_chrome_path):
                    chrome_options.binary_location = custom_chrome_path
                    print(f"{Fore.GREEN}[Browser Manager] Using custom Chrome path: {custom_chrome_path}")
                
                # Get Chrome version and use version-specific ChromeDriver
                chrome_version = self.get_chrome_version(custom_chrome_path)
                driver = None
                
                # Initialize ChromeDriver with better error handling
                try:
                    if chrome_version:
                        # Extract major version for ChromeDriverManager
                        major_version = chrome_version.split('.')[0]
                        print(f"{Fore.CYAN}[Browser Manager] Using ChromeDriver for Chrome major version {major_version}")
                        driver_path = ChromeDriverManager(version=f"{major_version}.0.0.0").install()
                    else:
                        # Let ChromeDriverManager auto-detect
                        driver_path = ChromeDriverManager().install()
                    
                    print(f"{Fore.GREEN}[Browser Manager] ChromeDriver installed at: {driver_path}")
                    if not driver_path.endswith('chromedriver.exe') and not driver_path.endswith('chromedriver'):
                        print(f"{Fore.YELLOW}[Browser Manager] ChromeDriver path seems incorrect, trying alternative...")
                        driver_dir = os.path.dirname(driver_path)
                        # Try different possible locations
                        possible_paths = [
                            os.path.join(driver_dir, 'chromedriver.exe'),
                            os.path.join(driver_dir, 'chromedriver'),
                            os.path.join(os.path.dirname(driver_dir), 'chromedriver.exe'),
                            driver_path.replace('/THIRD_PARTY_NOTICES.chromedriver', '/chromedriver.exe')
                        ]
                        for possible_path in possible_paths:
                            if os.path.exists(possible_path):
                                driver_path = possible_path
                                print(f"{Fore.GREEN}[Browser Manager] Found actual ChromeDriver at: {driver_path}")
                                break
                        else:
                            raise Exception("ChromeDriver file not found")
                    
                    # Initialize Service with port=0 to let Selenium choose a free port
                    service = Service(driver_path, port=0)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                    # Navigate to about:blank to ensure the session is alive
                    driver.get("about:blank")
                    
                    # Execute script to remove automation indicators after successful navigation
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    
                except Exception as e:
                    print(f"{Fore.YELLOW}[Browser Manager] ChromeDriver error: {e}")
                    print(f"{Fore.YELLOW}[Browser Manager] Attempting fallback to local ChromeDriver...")
                    
                    # Fallback to bundled or local chromedriver.exe
                    local_driver_path = self._get_chromedriver_path()
                    if local_driver_path and os.path.exists(local_driver_path):
                        try:
                            print(f"{Fore.GREEN}[Browser Manager] Using local ChromeDriver: {local_driver_path}")
                            # Initialize Service with port=0 to let Selenium choose a free port
                            service = Service(local_driver_path, port=0)
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                            
                            # Navigate to about:blank to ensure the session is alive
                            driver.get("about:blank")
                            
                            # Execute script to remove automation indicators after successful navigation
                            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                            
                        except Exception as e2:
                            if attempt < max_retries - 1:
                                print(f"{Fore.YELLOW}[Browser Manager] Attempt {attempt + 1} failed: {e2}")
                                print(f"{Fore.YELLOW}[Browser Manager] Retrying in {retry_delays[attempt]} seconds...")
                                time.sleep(retry_delays[attempt])
                                continue
                            else:
                                print(f"{Fore.RED}[Browser Manager] Local ChromeDriver failed after {max_retries} attempts: {e2}")
                                if not self.is_frozen:
                                    print(f"{Fore.YELLOW}[Browser Manager] Please run 'python fix_chromedriver.py' to download a compatible ChromeDriver")
                                return None
                    else:
                        if attempt < max_retries - 1:
                            print(f"{Fore.YELLOW}[Browser Manager] Attempt {attempt + 1} failed: No local ChromeDriver found")
                            print(f"{Fore.YELLOW}[Browser Manager] Retrying in {retry_delays[attempt]} seconds...")
                            time.sleep(retry_delays[attempt])
                            continue
                        else:
                            print(f"{Fore.RED}[Browser Manager] No local ChromeDriver found after {max_retries} attempts")
                            if not self.is_frozen:
                                print(f"{Fore.YELLOW}[Browser Manager] Please run 'python fix_chromedriver.py' to download a compatible ChromeDriver")
                            return None
            
                # --- SCALE AND ARRANGE WINDOWS ---
                try:
                    # Place up to 10 windows per row, then start a new row (for up to 20+ windows)
                    import math
                    screen_width = 1920
                    screen_height = 1080
                    max_per_row = 10
                    try:
                        import ctypes
                        user32 = ctypes.windll.user32
                        screen_width = user32.GetSystemMetrics(0)
                        screen_height = user32.GetSystemMetrics(1)
                    except Exception:
                        pass
                    cols = min(total_instances, max_per_row)
                    rows = math.ceil(total_instances / max_per_row)
                    win_w = int(screen_width / max_per_row)
                    win_h = int(screen_height / rows)
                    col = instance_id % max_per_row
                    row = instance_id // max_per_row
                    x = col * win_w
                    y = row * win_h
                    driver.set_window_size(win_w, win_h)
                    driver.set_window_position(x, y)
                except Exception as e:
                    print(f"{Fore.YELLOW}[Browser Manager] Could not arrange window: {e}")
                # --- END SCALE AND ARRANGE ---
                
                self.drivers.append(driver)
                self.active_instances += 1
                print(f"{Fore.GREEN}[Browser Manager] Created Chrome instance {instance_id} successfully")
                
                # Start heartbeat monitoring for this driver
                self._start_heartbeat(driver)
                
                return driver
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"{Fore.YELLOW}[Browser Manager] Attempt {attempt + 1} failed: {e}")
                    print(f"{Fore.YELLOW}[Browser Manager] Retrying in {retry_delays[attempt]} seconds...")
                    time.sleep(retry_delays[attempt])
                    continue
                else:
                    print(f"{Fore.RED}[Browser Manager] Error creating driver after {max_retries} attempts: {e}")
                    if "WinError 193" in str(e):
                        print(f"{Fore.YELLOW}[Browser Manager] Troubleshooting WinError 193:")
                        print(f"{Fore.YELLOW}  - This usually means ChromeDriver architecture mismatch")
                        print(f"{Fore.YELLOW}  - Ensure Chrome and ChromeDriver are both 32-bit or both 64-bit")
                        print(f"{Fore.YELLOW}  - Try updating Chrome to the latest version")
                        print(f"{Fore.YELLOW}  - Check if you have the correct ChromeDriver for your Chrome version")
                    return None
        
        # This should never be reached due to the loop structure, but just in case
        print(f"{Fore.RED}[Browser Manager] Failed to create driver after all retries")
        return None
    
    def close_driver(self, driver: webdriver.Chrome):
        try:
            # Stop the heartbeat timer for this driver
            if driver in self.heartbeat_timers:
                timer = self.heartbeat_timers[driver]
                timer.cancel()
                del self.heartbeat_timers[driver]
                print(f"{Fore.CYAN}[Browser Manager] Stopped heartbeat for driver")
            
            if driver in self.drivers:
                self.drivers.remove(driver)
                self.active_instances -= 1
            driver.quit()
            print(f"{Fore.YELLOW}[Browser Manager] Closed Chrome instance")
        except Exception as e:
            print(f"{Fore.RED}[Browser Manager] Error closing driver: {e}")
    
    def close_all_drivers(self):
        # Cancel all heartbeat timers first
        for driver, timer in list(self.heartbeat_timers.items()):
            timer.cancel()
        self.heartbeat_timers.clear()
        
        # Close all drivers
        for driver in self.drivers[:]:
            self.close_driver(driver)
    
    def navigate_to_url(self, driver: webdriver.Chrome, url: str, timeout: int = 30):
        try:
            driver.get(url)
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print(f"{Fore.GREEN}[Browser Manager] Successfully navigated to {url}")
            return True
        except TimeoutException:
            print(f"{Fore.RED}[Browser Manager] Timeout navigating to {url}")
            return False
        except Exception as e:
            print(f"{Fore.RED}[Browser Manager] Error navigating to {url}: {e}")
            return False
    
    def wait_for_element(self, driver: webdriver.Chrome, by: By, value: str, timeout: int = 30):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"{Fore.RED}[Browser Manager] Element not found: {value}")
            return None
    
    def wait_for_element_clickable(self, driver: webdriver.Chrome, by: By, value: str, timeout: int = 30):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            print(f"{Fore.RED}[Browser Manager] Element not clickable: {value}")
            return None
    
    def safe_click(self, driver: webdriver.Chrome, by: By, value: str, timeout: int = 30):
        try:
            element = self.wait_for_element_clickable(driver, by, value, timeout)
            if element:
                element.click()
                return True
            return False
        except Exception as e:
            print(f"{Fore.RED}[Browser Manager] Error clicking element {value}: {e}")
            return False
    
    def safe_send_keys(self, driver: webdriver.Chrome, by: By, value: str, text: str, timeout: int = 30):
        try:
            element = self.wait_for_element(driver, by, value, timeout)
            if element:
                element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            print(f"{Fore.RED}[Browser Manager] Error sending keys to {value}: {e}")
            return False
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def get_active_instances_count(self) -> int:
        return self.active_instances
    
    def is_driver_alive(self, driver: webdriver.Chrome) -> bool:
        try:
            driver.current_url
            return True
        except:
            return False
    
    def refresh_driver(self, driver: webdriver.Chrome) -> Optional[webdriver.Chrome]:
        if not self.is_driver_alive(driver):
            print(f"{Fore.YELLOW}[Browser Manager] Driver not responding, refreshing...")
            self.close_driver(driver)
            return self.create_driver()
        return driver
    
    def keep_alive(self, driver: webdriver.Chrome):
        """Execute heartbeat check for a driver and restart if needed."""
        try:
            # Try to execute a simple script to check if driver is responsive
            result = driver.execute_script("return 1")
            if result == 1:
                # Driver is alive, schedule next heartbeat
                if driver in self.drivers and driver in self.heartbeat_timers:
                    timer = threading.Timer(30.0, self.keep_alive, args=[driver])
                    self.heartbeat_timers[driver] = timer
                    timer.start()
            else:
                raise WebDriverException("Unexpected result from heartbeat check")
        except WebDriverException as e:
            print(f"{Fore.YELLOW}[Browser Manager] Heartbeat failed: {e}")
            print(f"{Fore.YELLOW}[Browser Manager] Attempting to refresh driver...")
            
            # Remove the old driver from tracking
            if driver in self.heartbeat_timers:
                del self.heartbeat_timers[driver]
            
            # Find the index of the driver to maintain the same position
            driver_index = -1
            if driver in self.drivers:
                driver_index = self.drivers.index(driver)
            
            # Close and recreate the driver
            try:
                driver.quit()
            except:
                pass
            
            # Create a new driver
            new_driver = self.create_driver(instance_id=driver_index if driver_index >= 0 else 0)
            
            if new_driver:
                # Replace the old driver reference if it was in the list
                if driver_index >= 0 and driver_index < len(self.drivers):
                    self.drivers[driver_index] = new_driver
                
                # Note: heartbeat is already started by create_driver
                print(f"{Fore.GREEN}[Browser Manager] Driver refreshed successfully")
            else:
                print(f"{Fore.RED}[Browser Manager] Failed to refresh driver")
                # Remove the dead driver from the list
                if driver in self.drivers:
                    self.drivers.remove(driver)
                    self.active_instances -= 1
    
    def _start_heartbeat(self, driver: webdriver.Chrome):
        """Start the heartbeat timer for a driver."""
        if driver not in self.heartbeat_timers:
            print(f"{Fore.CYAN}[Browser Manager] Starting heartbeat for driver")
            timer = threading.Timer(30.0, self.keep_alive, args=[driver])
            self.heartbeat_timers[driver] = timer
            timer.start()
    
    def stop_heartbeat(self, driver: webdriver.Chrome):
        """Stop the heartbeat timer for a specific driver."""
        if driver in self.heartbeat_timers:
            timer = self.heartbeat_timers[driver]
            timer.cancel()
            del self.heartbeat_timers[driver]
            print(f"{Fore.CYAN}[Browser Manager] Stopped heartbeat for driver")
    
    def start_heartbeat(self, driver: webdriver.Chrome):
        """Manually start heartbeat monitoring for a driver."""
        if driver in self.drivers:
            self._start_heartbeat(driver)
        else:
            print(f"{Fore.YELLOW}[Browser Manager] Driver not found in active drivers list")
    
    def _get_bundle_dir(self):
        """Get the base directory whether running as script or frozen executable."""
        if self.is_frozen:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            return getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
        else:
            # Get the directory of the parent of this file (project root)
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    def _get_chromedriver_path(self):
        """Get the path to ChromeDriver, checking bundled location first if frozen."""
        if self.is_frozen:
            # Try bundled ChromeDriver in PyInstaller temp directory
            bundled_path = os.path.join(self.bundle_dir, 'chromedriver.exe')
            if os.path.exists(bundled_path):
                print(f"{Fore.GREEN}[Browser Manager] Using bundled ChromeDriver: {bundled_path}")
                return bundled_path
            
            # Try ChromeDriver relative to executable
            exe_dir = os.path.dirname(sys.executable)
            exe_relative_path = os.path.join(exe_dir, 'chromedriver.exe')
            if os.path.exists(exe_relative_path):
                print(f"{Fore.GREEN}[Browser Manager] Using ChromeDriver relative to exe: {exe_relative_path}")
                return exe_relative_path
        
        # Fallback to local chromedriver.exe in project root
        local_path = os.path.join(self.bundle_dir, 'chromedriver.exe')
        if os.path.exists(local_path):
            return local_path
        
        # Try current directory
        if os.path.exists('./chromedriver.exe'):
            return './chromedriver.exe'
        
        return None
