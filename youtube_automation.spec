# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from PyInstaller.building.build_main import Tree

# Base paths
base_path = os.path.abspath('.')
chrome_path = os.path.join(base_path, 'chrome-win64')
chromedriver_path = os.path.join(base_path, 'chromedriver.exe')

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[base_path, os.path.join(base_path, 'src')],
    binaries=[
        # Include ChromeDriver
        (chromedriver_path, '.'),
    ],
    datas=[
        # Configuration files
        ('config.json', '.'),
        ('accounts.json', '.'),
    ],
    hiddenimports=[
        # Selenium and webdriver imports
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.common.action_chains',
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.wait',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.remote',
        'selenium.webdriver.remote.webelement',
        
        # Webdriver manager
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core',
        
        # Other dependencies
        'colorama',
        'tqdm',
        'psutil',
        'dotenv',
        'python-dotenv',
        
        # Standard library modules that might be dynamically imported
        'encodings',
        'encodings.utf_8',
        'encodings.ascii',
        'encodings.latin_1',
        
        # Project modules
        'src',
        'src.browser_manager',
        'src.browser_manager_enhanced',
        'src.config_manager',
        'src.constants',
        'src.exceptions',
        'src.gmail_authenticator',
        'src.gmail_authenticator_enhanced',
        'src.gmail_authenticator_improved',
        'src.gmail_authenticator_updated',
        'src.logger',
        'src.main_controller',
        'src.utils',
        'src.youtube_automation',
        'account_loader',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test files
        'tests',
        'test_*',
        '*_test',
        
        # Exclude development files
        'diagnose_*',
        'troubleshoot_*',
        'fix_*',
        'download_*',
        'manual_*',
        'monitor_*',
        'view_*',
        
        # Exclude unnecessary modules
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Collect all data files from selenium package
selenium_datas = collect_data_files('selenium')
a.datas += selenium_datas

# Add Chrome directory
chrome_tree = Tree(chrome_path, prefix='chrome-win64')
a.datas += chrome_tree

# Add src directory
src_tree = Tree('src', prefix='src')
a.datas += src_tree

# PYZ configuration
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='youtube_automation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version=None,  # Add version file if needed
)

# Optional: Create a directory distribution instead of single file
# Uncomment the following if you prefer a folder distribution
"""
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='youtube_automation',
)
"""

# Post-build script to ensure Chrome paths are correctly set
def post_build():
    """
    This function can be called after building to verify Chrome paths.
    Add any post-build verification or setup here.
    """
    import shutil
    dist_path = os.path.join(base_path, 'dist', 'youtube_automation')
    
    if os.path.exists(dist_path):
        # Verify Chrome is bundled
        chrome_exe = os.path.join(dist_path, 'chrome-win64', 'chrome.exe')
        if not os.path.exists(chrome_exe):
            print(f"Warning: Chrome executable not found at {chrome_exe}")
        
        # Verify ChromeDriver is bundled
        chromedriver_exe = os.path.join(dist_path, 'chromedriver.exe')
        if not os.path.exists(chromedriver_exe):
            print(f"Warning: ChromeDriver not found at {chromedriver_exe}")
        
        # Create default config files if they don't exist
        config_json = os.path.join(dist_path, 'config.json')
        if not os.path.exists(config_json):
            default_config = {
                "browser": {
                    "chrome_binary_path": "./chrome-win64/chrome.exe",
                    "chromedriver_path": "./chromedriver.exe",
                    "headless": false,
                    "window_size": "1920,1080",
                    "user_agent": null,
                    "disable_gpu": true,
                    "no_sandbox": true,
                    "disable_dev_shm_usage": true
                },
                "automation": {
                    "loop_count": 10,
                    "min_watch_duration": 30,
                    "max_watch_duration": 120,
                    "between_loops_delay": [5, 15],
                    "human_simulation": true
                },
                "paths": {
                    "profile_directory": "./browser_profiles",
                    "downloads_directory": "./downloads",
                    "logs_directory": "./logs"
                }
            }
            import json
            with open(config_json, 'w') as f:
                json.dump(default_config, f, indent=4)
        
        accounts_json = os.path.join(dist_path, 'accounts.json')
        if not os.path.exists(accounts_json):
            default_accounts = {
                "accounts": [
                    {
                        "email": "example@gmail.com",
                        "password": "your_password_here",
                        "recovery_email": "recovery@example.com",
                        "phone": "+1234567890"
                    }
                ],
                "settings": {
                    "retry_failed_logins": true,
                    "max_login_attempts": 3,
                    "session_timeout": 3600
                }
            }
            with open(accounts_json, 'w') as f:
                json.dump(default_accounts, f, indent=4)

# Additional build notes:
"""
Build Instructions:
1. Ensure all dependencies are installed: pip install -r requirements.txt
2. Ensure Chrome portable is in chrome-win64 directory
3. Ensure chromedriver.exe is in the root directory
4. Run: pyinstaller youtube_automation.spec

The output will be in the 'dist' folder.

Runtime Notes:
- The executable will look for Chrome in ./chrome-win64/chrome.exe relative to itself
- ChromeDriver will be looked for at ./chromedriver.exe
- Config files (config.json, accounts.json) will be created with defaults if missing
- Browser profiles will be stored in ./browser_profiles
- Logs will be stored in ./logs

Chrome Path Resolution:
The application will use the bundled Chrome by default. The paths in config.json
should use relative paths starting with ./ to reference the bundled Chrome.
"""
