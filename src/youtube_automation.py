import time
import random
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from colorama import Fore, init
from .logger import get_logger
from .config_manager import ConfigManager
from .browser_manager import BrowserManager
from .gmail_authenticator import GmailAuthenticator

init(autoreset=True)

logger = get_logger(__name__)


class YouTubeAutomation:
    """Simplified YouTube automation for video playback."""
    
    def __init__(self):
        # Detect if running as frozen executable
        self.is_frozen = getattr(sys, 'frozen', False)
        self.bundle_dir = self._get_bundle_dir()
        
        # Load configuration
        config_manager = ConfigManager()
        self.config = config_manager.config
        
        # Update Chrome path if running as frozen executable
        if self.is_frozen:
            self._update_frozen_paths()
        
        self.browser_manager = BrowserManager(self.config)
        self.gmail_auth = GmailAuthenticator(self.browser_manager, self.config)
        
        # YouTube selectors
        self.selectors = {
            'video_player': '#movie_player',
            'settings_button': 'button[aria-label*="Settings"]',
            'email_input': 'input[type="email"]',
            'password_input': 'input[type="password"], input[name="password"], input[name="Passwd"]',
            'next_button': '#identifierNext, #passwordNext, button[type="submit"]',
            'signin_button': 'button[aria-label*="Sign in"], a[aria-label*="Sign in"], ytd-button-renderer#button'
        }
    
    def run(self, email: str, password: str, video_url: str, headless: bool = False, stop_event=None, instance_id: int = 0, total_instances: int = 1) -> bool:
        """Log in to Gmail, open video URL, set resolution, and loop.
        
        Args:
            email: Gmail email address
            password: Gmail password
            video_url: YouTube video URL to loop
            headless: Whether to run in headless mode
            stop_event: Threading event to signal when to stop (optional)
            instance_id: The ID of this browser instance (for positioning)
            total_instances: Total number of browser instances (for grid layout)
            
        Returns:
            bool: True if automation was successful, False otherwise
        """
        driver = None
        try:
            logger.info(f"Starting automation for {email}")
            
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            # Add additional options to help with element interaction
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=400,300')
            
            # Create driver using BrowserManager
            try:
                driver = self.browser_manager.create_driver(instance_id, total_instances)
                if driver is None:
                    logger.error(f"Failed to create Chrome driver for {email}")
                    return False
                logger.debug(f"Chrome driver created successfully for {email}")
            except Exception as e:
                logger.error(f"Failed to create Chrome driver for {email}: {e}")
                return False
            
            # Gmail login using GmailAuthenticator
            account_data = {
                'email': email,
                'password': password,
                'nickname': email.split('@')[0]
            }
            
            if not self.gmail_auth.login(driver, email, password):
                logger.error(f"Failed to login to Gmail for {email}")
                return False
            
            logger.info(f"Successfully logged into Gmail for {email}")
            
            # Wait a bit before navigating to YouTube to ensure Gmail is fully loaded
            logger.info(f"Waiting before navigating to YouTube...")
            time.sleep(random.uniform(3, 5))
            
            # Navigate to YouTube video
            try:
                logger.info(f"Navigating to YouTube video: {video_url}")
                driver.get(video_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['video_player']))
                )
                logger.debug(f"Successfully loaded YouTube video for {email}")
            except TimeoutException:
                logger.error(f"Timeout loading YouTube video for {email}")
                return False
            except Exception as e:
                logger.error(f"Error loading YouTube video for {email}: {e}")
                return False
            
            # Setup video
            self.enable_youtube_loop(driver)
            self.inject_loop_javascript(driver)
            self.set_highest_resolution(driver)
            self.skip_ads(driver)
            logger.info(f"Setup complete for {email} on video {video_url}")
            
            # Keep running until stop_event is set
            check_counter = 0
            while True:
                if stop_event and stop_event.is_set():
                    logger.info(f"Stopping automation for {email} due to stop event")
                    break
                time.sleep(60)
                
                # Check if driver is still alive
                try:
                    _ = driver.current_url
                    
                    # Check for ads every minute
                    self.skip_ads(driver)
                    
                    # Re-inject JavaScript every 5 minutes to ensure loop continues
                    check_counter += 1
                    if check_counter >= 5:
                        check_counter = 0
                        # Check if video is still looping properly
                        is_looping = driver.execute_script("""
                            const v = document.querySelector('video');
                            return v && v.loop;
                        """)
                        
                        if not is_looping:
                            logger.warning(f"Loop disabled for {email}, re-injecting JavaScript...")
                            self.inject_loop_javascript(driver)
                    
                except Exception as e:
                    logger.error(f"Driver crashed for {email}: {e}")
                    return False
            
            # If we exited normally (due to stop event), return True
            return True
                    
        except Exception as e:
            logger.error(f"Unexpected error during automation for {email}: {type(e).__name__}: {e}")
            return False
        finally:
            if driver:
                try:
                    self.browser_manager.close_driver(driver)
                    logger.debug(f"Driver closed for {email}")
                except Exception as e:
                    logger.warning(f"Error closing driver for {email}: {e}")
    

    def enable_youtube_loop(self, driver: webdriver.Chrome):
        """Right-click the video and enable YouTube's built-in loop mode if not already enabled."""
        try:
            # Wait for the video player
            video_player = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['video_player']))
            )
            if not video_player:
                logger.error("Video player not found for loop mode")
                return False
            actions = ActionChains(driver)
            # Right-click on the center of the video player
            actions.move_to_element(video_player).context_click().perform()
            time.sleep(1)
            # List of possible translations for 'Loop'
            loop_keywords = ['loop', 'vòng lặp', '循环', '循环播放', 'boucle', 'schleife', 'bucle', 'ciclo', 'ripeti', 'повтор', '루프']
            menu_items = driver.find_elements(By.CSS_SELECTOR, 'ytd-menu-service-item-renderer, tp-yt-paper-item, .ytp-menuitem')
            for item in menu_items:
                try:
                    text = item.text.strip().lower()
                    if any(keyword in text for keyword in loop_keywords):
                        # If not already checked, click it
                        aria_checked = item.get_attribute('aria-checked')
                        if aria_checked != 'true':
                            item.click()
                            logger.info("Enabled built-in loop mode")
                        else:
                            logger.info("Loop mode already enabled")
                        return True
                except Exception:
                    continue
            logger.warning("Loop menu item not found (may already be enabled)")
            return False
        except Exception as e:
            logger.error(f"Error enabling loop mode: {e}")
            return False

    def inject_loop_javascript(self, driver: webdriver.Chrome):
        """Inject JavaScript to guarantee video looping even if UI loop fails."""
        try:
            # Wait a moment for video element to be ready
            time.sleep(2)
            
            # Inject JavaScript for guaranteed looping
            loop_script = """
                const v = document.querySelector('video');
                if (v) {
                    v.loop = true;
                    v.addEventListener('ended', () => {
                        console.log('[YouTube Automation] Video ended, restarting...');
                        v.play();
                    });
                    console.log('[YouTube Automation] JavaScript loop injection successful');
                    return true;
                } else {
                    console.log('[YouTube Automation] Video element not found');
                    return false;
                }
            """
            
            result = driver.execute_script(loop_script)
            
            if result:
                logger.info("JavaScript loop injection successful - guaranteed infinite looping")
            else:
                logger.warning("JavaScript loop injection failed - video element not found")
                
            return result
            
        except Exception as e:
            logger.error(f"Error injecting loop JavaScript: {e}")
            return False

    def set_highest_resolution(self, driver: webdriver.Chrome):
        """Set YouTube video resolution to the highest available."""
        try:
            # Open settings menu
            settings_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors['settings_button']))
            )
            if not settings_button:
                logger.warning("Settings button not found for resolution change")
                return False
            settings_button.click()
            time.sleep(1)
            # Find and click 'Quality' menu item (support multiple languages)
            quality_keywords = ['quality', 'chất lượng', 'qualité', 'qualität', 'calidad', 'qualità', 'качество', '화질', '画质', '画質']
            menu_items = driver.find_elements(By.CSS_SELECTOR, 'div[role="menuitem"], .ytp-menuitem')
            for item in menu_items:
                text = item.text.strip().lower()
                if any(keyword in text for keyword in quality_keywords):
                    item.click()
                    time.sleep(1)
                    break
            # Find all available quality options
            quality_options = driver.find_elements(By.CSS_SELECTOR, 'span.ytp-menuitem-label')
            if not quality_options:
                logger.warning("No quality options found")
                return False
            # Click the first (highest) quality option
            quality_options[0].click()
            logger.info("Set video resolution to highest")
            return True
        except Exception as e:
            logger.warning(f"Error setting highest resolution: {e}")
            return False

    def skip_ads(self, driver: webdriver.Chrome):
        """Skip ads if they appear while playing the video."""
        try:
            # Check if an ad is playing, identified by the presence of the "Skip Ads" button
            skip_button_selectors = [
                '.ytp-ad-skip-button',
                '.ytp-ad-overlay-close-button'
            ]
            for selector in skip_button_selectors:
                skip_button = driver.find_elements(By.CSS_SELECTOR, selector)
                if skip_button:
                    skip_button[0].click()
                    logger.info("Ad skipped successfully.")
        except Exception as e:
            logger.warning(f"Could not skip ad: {e}")
    
    def position_window(self, driver: webdriver.Chrome, instance_id: int, total_instances: int):
        """Position browser window in a grid layout to fit multiple instances on screen."""
        try:
            import math
            # Get screen dimensions (default to 1920x1080 if can't detect)
            screen_width = 1920
            screen_height = 1080
            
            try:
                # Try to get actual screen dimensions on Windows
                import ctypes
                user32 = ctypes.windll.user32
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)
            except Exception:
                pass
            
            # Calculate grid layout (aim for roughly square grid)
            cols = math.ceil(math.sqrt(total_instances))
            rows = math.ceil(total_instances / cols)
            
            # Calculate window dimensions
            window_width = screen_width // cols
            window_height = screen_height // rows
            
            # Calculate position for this instance
            col = instance_id % cols
            row = instance_id // cols
            x = col * window_width
            y = row * window_height
            
            # Set window size and position
            driver.set_window_size(window_width, window_height)
            driver.set_window_position(x, y)
            
            logger.info(f"Positioned window {instance_id} at ({x}, {y}) with size {window_width}x{window_height}")
            
        except Exception as e:
            logger.warning(f"Could not position window: {e}")
    
    def _get_bundle_dir(self):
        """Get the base directory whether running as script or frozen executable."""
        if self.is_frozen:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            return getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
        else:
            # Get the directory of this file
            return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    def _update_frozen_paths(self):
        """Update configuration paths for frozen executable."""
        logger.info(f"Running as frozen executable from: {self.bundle_dir}")
        
        # Update Chrome path to use bundled Chrome
        chrome_path = os.path.join(self.bundle_dir, 'chrome-win64', 'chrome.exe')
        if os.path.exists(chrome_path):
            self.config['browser_settings']['chrome_path'] = chrome_path
            logger.info(f"Updated Chrome path for frozen executable: {chrome_path}")
        else:
            logger.warning(f"Bundled Chrome not found at: {chrome_path}")
            # Try relative to executable location
            exe_dir = os.path.dirname(sys.executable)
            alt_chrome_path = os.path.join(exe_dir, 'chrome-win64', 'chrome.exe')
            if os.path.exists(alt_chrome_path):
                self.config['browser_settings']['chrome_path'] = alt_chrome_path
                logger.info(f"Found Chrome relative to executable: {alt_chrome_path}")
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and frozen."""
        return os.path.join(self.bundle_dir, relative_path)
