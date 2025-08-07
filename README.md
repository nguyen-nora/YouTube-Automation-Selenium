# YouTube Automation System

A powerful Selenium-based automation tool for managing multiple Gmail accounts and YouTube video loops. This system provides automated view farming capabilities with human-like behavior simulation.

## 🚀 Features

- **Multi-Account Management**: Handle multiple Gmail accounts simultaneously
- **Automated Gmail Login**: Secure authentication for each account
- **YouTube Video Looping**: Automated video playback with configurable loops
- **Optimized Loop Guarantee**: JavaScript injection ensures infinite looping even if UI fails
- **View Farming**: Human-like behavior simulation to avoid detection
- **Multi-Instance Support**: Parallel Chrome instances for different accounts
- **Anti-Detection Measures**: Advanced techniques to avoid automation detection
- **Crash Recovery**: Automatic restart of failed instances
- **Real-time Monitoring**: Live status monitoring and logging
- **Configurable Settings**: Flexible configuration for all aspects

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Google Chrome browser (latest version recommended)
- Windows 10/11, macOS, or Linux
- Minimum 4GB RAM (8GB recommended for multiple instances)
- Stable internet connection

### Prerequisites
- Gmail accounts with "Less secure app access" enabled or App Passwords configured
- Basic knowledge of command line operations
- Chrome must be installed in the default location or added to PATH

## 🛠️ Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd SeleniumYtb
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Chrome installation**:
   - Ensure Google Chrome is installed on your system
   - The tool will automatically download the appropriate ChromeDriver

## ⚙️ Configuration

### 1. Account Configuration

You can configure accounts in two ways:

#### Option A: Using `email.txt` (Recommended for simplicity)

Create an `email.txt` file in the project directory with your credentials:

```
# Format: email:password or email password
# Comments starting with # are ignored
# Empty lines are skipped

example1@gmail.com:mypassword123
example2@gmail.com:anotherpass456
example3@gmail.com password789

# You can also use tab or space as separator
john.doe@gmail.com	password123
jane.smith@gmail.com password456
```

**Email.txt Format Details:**
- One account per line
- Supported separators: colon `:`, space ` `, or tab `\t`
- Lines starting with `#` are treated as comments
- Empty lines are ignored
- File must be named exactly `email.txt` (case-sensitive)

#### Option B: Using `accounts.json`

Edit the `accounts.json` file to add your Gmail credentials:

```json
{
  "accounts": [
    {
      "email": "your_email1@gmail.com",
      "password": "your_password1",
      "enabled": true,
      "nickname": "Account 1"
    },
    {
      "email": "your_email2@gmail.com",
      "password": "your_password2",
      "enabled": true,
      "nickname": "Account 2"
    }
  ]
}
```

**Important Security Notes**:
- Passwords are now stored and handled in plain text for simplicity
- If `email.txt` exists, it will be used instead of `accounts.json`
- Keep your credential files secure and never commit them to version control
- Enable 2FA on your Gmail accounts for additional security

### 2. System Configuration (`config.json`)

The `config.json` file contains all system settings:

```json
{
  "youtube_settings": {
    "video_urls": [
      "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
    ],
    "loop_duration_minutes": 30,
    "view_farming_enabled": true,
    "random_delays": {
      "min_seconds": 5,
      "max_seconds": 15
    }
  },
  "browser_settings": {
    "headless": false,
    "window_size": "1920x1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "chrome_options": [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-blink-features=AutomationControlled"
    ]
  },
  "gmail_settings": {
    "login_timeout": 60,
    "max_login_attempts": 3,
    "two_factor_auth_enabled": false
  },
  "automation_settings": {
    "max_concurrent_instances": 5,
    "instance_startup_delay": 10,
    "monitoring_interval": 30,
    "auto_restart_on_crash": true
  }
}
```

### Configuration Options

#### YouTube Settings
- `video_urls`: Array of YouTube video URLs to loop
- `loop_duration_minutes`: Maximum duration for each loop session (minutes)
- `view_farming_enabled`: Enable human-like behavior simulation
- `random_delays`: Random delay ranges for natural behavior

**Important Note on Video Playback:**
Once a video starts playing, it will continue to play indefinitely in a loop without requiring any further actions. The system uses JavaScript injection to ensure the video loops continuously, even if the YouTube UI's loop button fails. The `loop_duration_minutes` setting controls how long each browser session runs before restarting, not individual video loops.

#### Browser Settings
- `headless`: Run browsers in background (no GUI)
- `window_size`: Browser window dimensions
- `user_agent`: Custom user agent string
- `chrome_options`: Additional Chrome command-line options

#### Gmail Settings
- `login_timeout`: Maximum time to wait for login (seconds)
- `max_login_attempts`: Maximum login retry attempts
- `two_factor_auth_enabled`: Enable 2FA support

#### Automation Settings
- `max_concurrent_instances`: Maximum parallel browser instances
- `instance_startup_delay`: Delay between instance startups (seconds)
- `monitoring_interval`: Status check interval (seconds)
- `auto_restart_on_crash`: Automatically restart failed instances

## 🚀 Usage

### Quick Start

```bash
# Basic execution - uses email.txt or accounts.json
python main.py
```

### Common CLI Examples

```bash
# Run with browser windows visible (default)
python main.py

# Run in background mode (no browser windows)
python main.py --headless

# Enable detailed logging for troubleshooting
python main.py --debug

# Use custom configuration file
python main.py --config custom_config.json

# Use custom accounts file (if not using email.txt)
python main.py --accounts custom_accounts.json

# Combine multiple options
python main.py --headless --debug --config production.json

# Show all available options
python main.py --help

# Show detailed help with examples
python main.py --help-detailed
```

### Advanced Usage Examples

```bash
# Production setup with custom files
python main.py --config prod_config.json --accounts prod_accounts.json --headless

# Development/testing with debug output
python main.py --debug --config test_config.json

# Minimal resource usage
python main.py --headless --config minimal_config.json
```

### Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|----------|
| `--config <path>` | Path to configuration file | `config.json` | `--config prod_config.json` |
| `--accounts <path>` | Path to accounts file | `accounts.json` | `--accounts gmail_accounts.json` |
| `--headless` | Run browsers in background (no GUI) | False | `--headless` |
| `--debug` | Enable verbose debug logging | False | `--debug` |
| `--help` | Show basic help message | - | `--help` |
| `--help-detailed` | Show detailed help with examples | - | `--help-detailed` |

## 📊 Monitoring and Control

### Real-time Status

The system provides real-time monitoring with colored output:
- 🟢 **Green**: Successful operations
- 🔵 **Blue**: Information and status updates
- 🟡 **Yellow**: Warnings and non-critical issues
- 🔴 **Red**: Errors and critical issues

### Control Commands

- **Ctrl+C**: Graceful shutdown of all processes
- **Automatic Recovery**: Failed instances are automatically restarted
- **Status Monitoring**: Continuous monitoring of active instances and loops

## 🔧 Troubleshooting

### Common Issues

1. **ChromeDriver Issues**:
   - Ensure Chrome is up to date
   - The tool automatically downloads the correct ChromeDriver version

2. **Login Failures**:
   - Verify Gmail credentials are correct
   - Check if 2FA is enabled and configured properly
   - Ensure accounts are not locked or suspended

3. **YouTube Detection**:
   - Reduce the number of concurrent instances
   - Increase random delays
   - Use different user agents
   - Consider using proxies for multiple accounts

4. **Performance Issues**:
   - Reduce `max_concurrent_instances`
   - Enable headless mode
   - Close other applications to free up resources

### Debug Mode

Enable debug logging to get detailed information:

```bash
python main.py --debug
```

This will show:
- Detailed Selenium operations
- Element interaction logs
- Timing information
- Error stack traces

## ⚠️ Important Notes

### Legal and Ethical Considerations

- **Terms of Service**: Ensure compliance with YouTube's Terms of Service
- **Personal Use**: This tool is intended for personal use only
- **Responsible Usage**: Use responsibly and avoid excessive automation
- **Account Safety**: Monitor your accounts for any suspicious activity

### Security Best Practices

1. **Credential Management**:
   - Use strong, unique passwords
   - Enable 2FA on all accounts
   - Regularly rotate credentials
   - Consider using app-specific passwords

2. **Network Security**:
   - Use VPN if running multiple accounts
   - Monitor for IP-based restrictions
   - Avoid running from public networks

3. **System Security**:
   - Keep the system updated
   - Use antivirus software
   - Monitor for unauthorized access

### Performance Optimization

1. **Resource Management**:
   - Monitor CPU and memory usage
   - Adjust `max_concurrent_instances` based on system capabilities
   - Use headless mode for better performance
   - Each Chrome instance typically uses 200-500MB RAM

2. **Network Optimization**:
   - Ensure stable internet connection
   - Consider bandwidth limitations
   - Monitor for rate limiting
   - Videos continue playing even during brief connection interruptions

## 📁 Project Structure

```
SeleniumYtb/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── config.json            # System configuration
├── accounts.json          # Gmail account credentials (optional)
├── email.txt              # Simple email:password list (optional)
├── README.md              # This file
└── src/                   # Source code
    ├── __init__.py
    ├── config_manager.py  # Configuration management
    ├── browser_manager.py # Browser instance management
    ├── gmail_authenticator.py # Gmail login automation
    ├── youtube_automation.py  # YouTube video automation
    └── main_controller.py     # Main orchestration logic
```

## 🤝 Contributing

This is a personal project. If you find bugs or have suggestions:

1. Test thoroughly before reporting issues
2. Provide detailed error logs
3. Include system information and configuration
4. Be respectful and constructive

## 📄 License

This project is provided as-is for educational and personal use. Users are responsible for compliance with all applicable terms of service and laws.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Enable debug mode and review logs
3. Verify configuration files
4. Test with a single account first

## 🔄 Updates

The system may need updates as YouTube and Gmail change their interfaces. Monitor for:
- Login page changes
- YouTube UI updates
- New anti-automation measures
- Chrome version compatibility

---

**Disclaimer**: This tool is provided for educational purposes. Users are responsible for compliance with all applicable terms of service and laws. Use responsibly and at your own risk. 