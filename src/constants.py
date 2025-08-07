"""
Constants and configuration values for YouTube Automation System.
"""

from enum import Enum
from typing import Dict, List


class BrowserConstants:
    """Browser-related constants."""
    
    DEFAULT_WINDOW_WIDTH = 1920
    DEFAULT_WINDOW_HEIGHT = 1080
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Chrome options for anti-detection
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        "--remote-debugging-port=0",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--disable-gpu",
        "--disable-software-rasterizer"
    ]
    
    # Language settings
    LANGUAGE_OPTIONS = {
        "lang": "en-US",
        "accept_lang": "en-US,en",
        "intl.accept_languages": "en,en_US,en-US"
    }
    
    MAX_WINDOWS_PER_ROW = 10


class YouTubeSelectors:
    """YouTube DOM selectors."""
    
    PLAY_BUTTON = 'button[aria-label*="Play"]'
    PAUSE_BUTTON = 'button[aria-label*="Pause"]'
    VIDEO_PLAYER = '#movie_player'
    VIDEO_TITLE = 'h1.ytd-video-primary-info-renderer'
    LIKE_BUTTON = 'ytd-toggle-button-renderer[aria-label*="like"]'
    SUBSCRIBE_BUTTON = 'ytd-subscribe-button-renderer'
    COMMENT_SECTION = 'ytd-comments'
    AD_SKIP_BUTTON = 'button[aria-label*="Skip"]'
    AD_CLOSE_BUTTON = 'button[aria-label*="Close"]'
    VOLUME_SLIDER = 'ytd-volume-slider'
    FULLSCREEN_BUTTON = 'button[aria-label*="Full screen"]'
    SETTINGS_BUTTON = 'button[aria-label*="Settings"]'
    QUALITY_MENU = 'ytd-menu-renderer'
    LOOP_BUTTON = 'button[aria-label*="Loop"]'
    REPLAY_BUTTON = 'button[aria-label*="Replay"]'
    TIME_DURATION = 'span.ytp-time-duration'
    
    # Context menu items
    MENU_ITEMS = 'ytd-menu-service-item-renderer, tp-yt-paper-item, .ytp-menuitem'
    QUALITY_OPTIONS = 'span.ytp-menuitem-label'
    MENU_ITEM_ROLE = 'div[role="menuitem"], .ytp-menuitem'


class GmailSelectors:
    """Gmail DOM selectors."""
    
    EMAIL_INPUT = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    NEXT_BUTTON = '#identifierNext button'
    PASSWORD_NEXT_BUTTON = '#passwordNext button'
    SIGNIN_BUTTON = 'button[type="submit"]'
    ACCOUNT_PICKER = 'div[data-email]'
    USE_ANOTHER_ACCOUNT = 'div[data-email=""]'
    ADD_ACCOUNT = 'div[data-email=""]'
    
    # Profile indicators
    PROFILE_PICTURE = 'img[alt*="Profile picture"]'
    ACCOUNT_AVATAR = 'div[aria-label*="Account"]'
    ACCOUNT_TOOLTIP = 'div[data-tooltip*="Account"]'
    
    # Gmail interface
    GMAIL_MAIN = 'div[role="main"]'
    COMPOSE_BUTTON = 'div[data-tooltip="Compose"]'
    INBOX = 'div[aria-label="Inbox"]'
    
    # Sign out
    LOGOUT_LINK = 'a[href*="Logout"]'
    SIGNOUT_LABEL = 'div[aria-label*="Sign out"]'
    SIGNOUT_TOOLTIP = 'div[data-tooltip*="Sign out"]'
    
    # 2FA
    TOTP_INPUT = 'input[name="totpPin"]'
    VERIFICATION_INPUT = 'input[aria-label*="verification"]'
    PHONE_INPUT = 'input[type="tel"]'


class TimeoutConstants:
    """Timeout values in seconds."""
    
    PAGE_LOAD = 30
    ELEMENT_WAIT = 30
    LOGIN_TIMEOUT = 60
    VIDEO_LOAD = 15
    AD_SKIP_WAIT = 3
    POPUP_WAIT = 3
    TWO_FA_WAIT = 60


class DelayConstants:
    """Delay ranges for human-like behavior."""
    
    # General delays
    MIN_ACTION_DELAY = 0.5
    MAX_ACTION_DELAY = 1.5
    
    # Page navigation
    MIN_PAGE_DELAY = 2
    MAX_PAGE_DELAY = 4
    
    # Video interaction
    MIN_VIDEO_DELAY = 1
    MAX_VIDEO_DELAY = 3
    
    # Loop delays
    MIN_LOOP_DELAY = 5
    MAX_LOOP_DELAY = 15
    
    # Monitoring interval
    DEFAULT_MONITORING_INTERVAL = 30
    VIDEO_CHECK_INTERVAL = 10


class VideoQuality(Enum):
    """Video quality options."""
    
    AUTO = "Auto"
    P144 = "144p"
    P240 = "240p"
    P360 = "360p"
    P480 = "480p"
    P720 = "720p"
    P1080 = "1080p"
    P1440 = "1440p"
    P2160 = "2160p"


class LanguageKeywords:
    """Multi-language support keywords."""
    
    LOOP_KEYWORDS = [
        'loop', 'vòng lặp', '循环', '循环播放', 'boucle', 
        'schleife', 'bucle', 'ciclo', 'ripeti', 'повтор', 
        '루프', '循環', 'ループ'
    ]
    
    QUALITY_KEYWORDS = [
        'quality', 'chất lượng', 'qualité', 'qualität', 
        'calidad', 'qualità', 'качество', '화질', 
        '画质', '画質', '品質'
    ]
    
    ACCEPT_KEYWORDS = [
        'accept', 'agree', 'i agree', 'got it', 
        'ok', 'continue', 'next'
    ]


class URLConstants:
    """URL constants."""
    
    GMAIL_URL = "https://gmail.com"
    YOUTUBE_URL = "https://www.youtube.com"
    GOOGLE_URL = "https://www.google.com"
    
    GMAIL_DOMAINS = ["mail.google.com", "gmail.com"]
    YOUTUBE_DOMAINS = ["youtube.com", "www.youtube.com"]
    GOOGLE_ACCOUNTS = "accounts.google.com"


class ErrorMessages:
    """Standardized error messages."""
    
    # Browser errors
    DRIVER_CREATE_FAILED = "Failed to create browser instance"
    DRIVER_NOT_RESPONDING = "Driver not responding, refreshing..."
    CHROME_NOT_FOUND = "Chrome not found in common locations"
    CHROMEDRIVER_MISMATCH = "ChromeDriver architecture mismatch"
    
    # Authentication errors
    MISSING_CREDENTIALS = "Missing credentials for {}"
    LOGIN_FAILED = "Failed to login to Gmail"
    LOGIN_VERIFICATION_FAILED = "Login verification failed: {}"
    TWO_FA_REQUIRED = "2FA required - manual intervention needed"
    
    # YouTube errors
    VIDEO_PLAYER_NOT_FOUND = "Video player not found"
    LOOP_MODE_FAILED = "Failed to enable loop mode"
    VIDEO_NOT_PLAYING = "Video not playing"
    
    # Configuration errors
    NO_ENABLED_ACCOUNTS = "No enabled accounts found. Please configure accounts.json"
    NO_VIDEO_URLS = "No YouTube URLs configured. Please update config.json"
    CONFIG_LOAD_ERROR = "Error loading config: {}"
    
    # General errors
    UNEXPECTED_ERROR = "Unexpected error: {}"
    ELEMENT_NOT_FOUND = "Element not found: {}"
    TIMEOUT_ERROR = "Timeout waiting for {}"


class SuccessMessages:
    """Standardized success messages."""
    
    # Browser
    CHROME_FOUND = "Chrome found at: {}"
    DRIVER_CREATED = "Created Chrome instance {}"
    
    # Authentication
    ALREADY_LOGGED_IN = "Already logged in: {}"
    LOGIN_SUCCESS = "Successfully logged in: {}"
    ACCOUNT_SELECTED = "Account selected: {}"
    
    # YouTube
    LOOP_STARTED = "Loop started for {}"
    LOOP_ENABLED = "Enabled built-in loop mode"
    VIDEO_COMPLETED = "Video completed"
    RESOLUTION_SET = "Set video resolution to lowest"
    
    # System
    SETUP_COMPLETE = "Setup completed successfully"
    AUTOMATION_STARTED = "Starting YouTube Automation System"
    MONITORING_STARTED = "Monitoring started"


class DefaultConfig:
    """Default configuration values."""
    
    YOUTUBE_SETTINGS = {
        "video_urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
        "loop_duration_minutes": 30,
        "view_farming_enabled": True,
        "random_delays": {
            "min_seconds": 5,
            "max_seconds": 15
        }
    }
    
    BROWSER_SETTINGS = {
        "headless": False,
        "window_size": f"{BrowserConstants.DEFAULT_WINDOW_WIDTH}x{BrowserConstants.DEFAULT_WINDOW_HEIGHT}",
        "user_agent": BrowserConstants.DEFAULT_USER_AGENT,
        "chrome_options": BrowserConstants.CHROME_OPTIONS
    }
    
    GMAIL_SETTINGS = {
        "login_timeout": TimeoutConstants.LOGIN_TIMEOUT,
        "max_login_attempts": 3,
        "two_factor_auth_enabled": False
    }
    
    AUTOMATION_SETTINGS = {
        "max_concurrent_instances": 5,
        "instance_startup_delay": 10,
        "monitoring_interval": DelayConstants.DEFAULT_MONITORING_INTERVAL,
        "auto_restart_on_crash": True
    }
