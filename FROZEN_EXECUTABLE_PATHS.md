# Frozen Executable Path Handling

This document explains how the YouTube Automation System handles paths when running as a frozen executable (compiled with PyInstaller).

## Overview

The application has been modified to detect whether it's running as a frozen executable or in development mode, and adjusts all file paths accordingly.

## Key Changes

### 1. **Frozen State Detection**

All modified modules now detect if running as frozen executable using:
```python
is_frozen = getattr(sys, 'frozen', False)
```

### 2. **Bundle Directory Detection**

When frozen, PyInstaller extracts files to a temporary directory accessible via `sys._MEIPASS`:
```python
if is_frozen:
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
else:
    bundle_dir = os.path.abspath(os.path.dirname(__file__))
```

### 3. **Module-Specific Changes**

#### **src/youtube_automation.py**
- Detects frozen state in `__init__`
- Updates Chrome path to use bundled Chrome when frozen
- Provides `get_resource_path()` method for accessing bundled resources
- Falls back to executable-relative paths if bundle path doesn't exist

#### **src/browser_manager.py**
- Detects frozen state in `__init__`
- `_get_chromedriver_path()` checks for ChromeDriver in:
  1. PyInstaller bundle directory (_MEIPASS)
  2. Next to the executable
  3. Project root (for development)
  4. Current directory

#### **src/config_manager.py**
- Config files (config.json, accounts.json, email.txt) are looked for next to the executable when frozen
- In development mode, uses relative paths from project root

#### **src/logger.py**
- Creates logs directory next to the executable when frozen
- Account status JSON is saved in the same logs directory

#### **main.py**
- Adjusts Python path based on frozen state
- Looks for email.txt next to executable by default when frozen

## Directory Structure

### Development Mode:
```
SeleniumYtb/
├── main.py
├── config.json
├── accounts.json
├── email.txt
├── chromedriver.exe
├── chrome-win64/
│   └── chrome.exe
├── src/
│   ├── youtube_automation.py
│   ├── browser_manager.py
│   └── ...
└── logs/
    └── automation_*.log
```

### Frozen Executable:
```
dist/
├── youtube_automation.exe
├── config.json (user-provided)
├── accounts.json (user-provided)
├── email.txt (user-provided)
├── chromedriver.exe (bundled or next to exe)
├── chrome-win64/ (bundled or next to exe)
│   └── chrome.exe
└── logs/ (created at runtime)
    └── automation_*.log
```

## PyInstaller Bundling

When building with PyInstaller, ensure to:

1. Bundle Chrome and ChromeDriver:
   ```
   --add-data "chrome-win64;chrome-win64"
   --add-binary "chromedriver.exe;."
   ```

2. User config files (config.json, accounts.json, email.txt) should NOT be bundled - they go next to the executable

3. The PyInstaller spec file should handle these resources appropriately

## Testing

Use `test_frozen_paths.py` to verify path handling:
- In development: `python test_frozen_paths.py`
- As frozen executable: Run the compiled test executable

The test script verifies:
1. Correct path detection in both modes
2. Config file locations
3. Chrome and ChromeDriver paths
4. Log directory creation

## Benefits

1. **Portability**: Executable can be moved to any location
2. **User-Friendly**: Config files stay next to executable for easy editing
3. **Clean Distribution**: All resources bundled in single executable
4. **Backward Compatible**: Still works normally in development mode
