# Logging and Error Handling

The YouTube Automation System includes comprehensive logging and error handling to track the status of each account and handle failures gracefully.

## Features

### 1. Automatic Logging
- All automation activities are logged to timestamped files in the `logs/` directory
- Console output shows INFO level and above by default
- File logs contain DEBUG level details for troubleshooting

### 2. Account Status Tracking
- Success/failure status for each account is tracked
- Detailed error information is captured
- Status is saved to `logs/account_status.json` for analysis

### 3. Error Recovery
- Selenium/WebDriver errors are caught and logged
- Gmail authentication failures don't stop other accounts
- Each account runs independently in its own thread

## Log Files

### Main Log File
- Location: `logs/automation_YYYYMMDD_HHMMSS.log`
- Contains detailed execution logs for all accounts
- Includes timestamps, log levels, and function names

### Account Status File
- Location: `logs/account_status.json`
- JSON format for easy parsing
- Tracks success/failure/error status per account
- Includes error details and timestamps

## Viewing Account Status

Use the included utility to view account status:

```bash
# View summary of all accounts
python view_account_status.py

# View detailed history
python view_account_status.py --detailed

# Filter by specific email
python view_account_status.py --email user@gmail.com

# Use custom status file
python view_account_status.py --file path/to/status.json
```

## Log Levels

### Console Output
- **INFO** (Green): Normal operations and successes
- **WARNING** (Yellow): Non-critical issues that don't stop execution
- **ERROR** (Red): Critical errors that prevent operation

### File Output
- Includes all console output plus **DEBUG** level details
- Stack traces for exceptions
- Detailed function call information

## Error Types

### Authentication Errors
- Invalid credentials
- Account locked/suspended
- Two-factor authentication required
- Timeout during login

### Selenium Errors
- WebDriver initialization failures
- Element not found
- Page load timeouts
- JavaScript execution errors

### Network Errors
- Connection failures
- DNS resolution issues
- Proxy errors

## Debug Mode

Enable debug mode for verbose console output:

```bash
python main.py --debug --emails accounts.txt --video https://youtu.be/VIDEO_ID
```

This will:
- Show DEBUG level messages in console
- Display detailed Selenium operations
- Include timing information

## Log Rotation

To manage log file size:
- Each run creates a new timestamped log file
- Old logs can be safely deleted or archived
- Account status file appends new entries (consider periodic cleanup)

## Custom Logging

To add custom logging in your extensions:

```python
from src.logger import get_logger

logger = get_logger(__name__)

# Use the logger
logger.debug("Detailed debug information")
logger.info("Normal operation message")
logger.warning("Warning about potential issue")
logger.error("Error occurred: %s", error_message)
```

## Monitoring

### Real-time Monitoring
- Watch console output during execution
- Each account shows its current status
- Errors are highlighted in red

### Post-execution Analysis
- Review log files for detailed traces
- Use `view_account_status.py` for summary
- Parse JSON status file for custom analysis

## Best Practices

1. **Regular Monitoring**: Check logs periodically for patterns
2. **Error Investigation**: Use debug mode to diagnose failures
3. **Log Cleanup**: Archive old logs to save disk space
4. **Status Analysis**: Track success rates over time
5. **Alert Setup**: Parse status file for automated alerts
