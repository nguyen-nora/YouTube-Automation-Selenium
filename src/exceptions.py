"""
Custom exceptions for YouTube Automation System.
"""


class AutomationError(Exception):
    """Base exception for all automation errors."""
    pass


class BrowserError(AutomationError):
    """Browser-related errors."""
    pass


class DriverCreationError(BrowserError):
    """Error creating WebDriver instance."""
    pass


class ChromeNotFoundError(BrowserError):
    """Chrome browser not found."""
    pass


class ChromeDriverError(BrowserError):
    """ChromeDriver-related errors."""
    pass


class AuthenticationError(AutomationError):
    """Authentication-related errors."""
    pass


class LoginError(AuthenticationError):
    """Login failed."""
    pass


class CredentialsError(AuthenticationError):
    """Invalid or missing credentials."""
    pass


class TwoFactorAuthError(AuthenticationError):
    """Two-factor authentication error."""
    pass


class YouTubeError(AutomationError):
    """YouTube-related errors."""
    pass


class VideoPlayerError(YouTubeError):
    """Video player not found or not accessible."""
    pass


class VideoLoopError(YouTubeError):
    """Error setting up video loop."""
    pass


class ConfigurationError(AutomationError):
    """Configuration-related errors."""
    pass


class ConfigFileError(ConfigurationError):
    """Error reading configuration file."""
    pass


class InvalidConfigError(ConfigurationError):
    """Invalid configuration values."""
    pass


class NetworkError(AutomationError):
    """Network-related errors."""
    pass


class TimeoutError(NetworkError):
    """Operation timed out."""
    pass


class ElementNotFoundError(AutomationError):
    """DOM element not found."""
    pass
