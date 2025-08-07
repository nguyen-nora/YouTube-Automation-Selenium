# -*- mode: python ; coding: utf-8 -*-
# Directory Distribution Version - Creates a folder with all dependencies

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all

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
        
        # Chrome browser directory - include entire portable Chrome
        (chrome_path, 'chrome-win64'),
        
        # Include src directory
        ('src', 'src'),
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
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.remote',
        'selenium.webdriver.remote.webelement',
        'selenium.webdriver.remote.webdriver',
        'selenium.common',
        'selenium.common.exceptions',
        
        # Webdriver manager
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core',
        'webdriver_manager.core.driver_cache',
        'webdriver_manager.core.manager',
        'webdriver_manager.core.utils',
        'webdriver_manager.drivers',
        'webdriver_manager.drivers.chrome',
        
        # Other dependencies
        'colorama',
        'colorama.ansi',
        'colorama.ansitowin32',
        'colorama.initialise',
        'colorama.win32',
        'colorama.winterm',
        'tqdm',
        'tqdm.auto',
        'tqdm.std',
        'psutil',
        'psutil._common',
        'psutil._pswindows',
        'dotenv',
        'python-dotenv',
        
        # Standard library modules that might be dynamically imported
        'encodings',
        'encodings.utf_8',
        'encodings.ascii',
        'encodings.latin_1',
        'encodings.cp1252',
        'encodings.idna',
        
        # Threading and async modules
        'concurrent',
        'concurrent.futures',
        'asyncio',
        'threading',
        'queue',
        
        # Network modules
        'urllib',
        'urllib.request',
        'urllib.parse',
        'urllib.error',
        'http',
        'http.client',
        'socket',
        'ssl',
        
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
        
        # Exclude unnecessary heavy modules
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Collect all data files from selenium package
selenium_datas = collect_data_files('selenium')
a.datas += selenium_datas

# Collect additional data from webdriver_manager
wdm_datas = collect_data_files('webdriver_manager')
a.datas += wdm_datas

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
    [],
    exclude_binaries=True,  # Important for COLLECT
    name='youtube_automation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console window for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

# COLLECT - Create directory distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[
        'chrome.exe',  # Don't compress Chrome executable
        'chromedriver.exe',  # Don't compress ChromeDriver
        '*.dll',  # Don't compress DLLs
    ],
    name='youtube_automation',
)

# Create a batch file launcher for easy execution
launcher_content = """@echo off
cd /d "%~dp0"
echo Starting YouTube Automation System...
echo.
youtube_automation.exe %*
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
"""

# Create a PowerShell launcher as alternative
ps_launcher_content = """# YouTube Automation System Launcher
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Starting YouTube Automation System..." -ForegroundColor Cyan
Write-Host ""

& "./youtube_automation.exe" $args

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Application exited with an error." -ForegroundColor Red
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
"""

# Build notes and post-build instructions
"""
Directory Distribution Build Instructions:
=========================================

1. Install PyInstaller and all dependencies:
   pip install pyinstaller
   pip install -r requirements.txt

2. Ensure Chrome portable is in chrome-win64 directory
3. Ensure chromedriver.exe is in the root directory
4. Run: pyinstaller youtube_automation_dir.spec

The output will be in: dist/youtube_automation/

Directory Structure After Build:
================================
dist/youtube_automation/
├── youtube_automation.exe      # Main executable
├── chromedriver.exe           # ChromeDriver
├── chrome-win64/              # Portable Chrome browser
│   ├── chrome.exe
│   ├── chrome_data/
│   ├── locales/
│   └── ...
├── src/                       # Source modules
├── config.json               # Configuration file
├── accounts.json             # Accounts template
├── _internal/                # PyInstaller dependencies
│   ├── base_library.zip
│   ├── python*.dll
│   └── ...
└── [various .dll and .pyd files]

Advantages of Directory Distribution:
=====================================
1. Easier to debug - can see all files
2. Can manually edit config files
3. Chrome updates are simpler - just replace chrome-win64 folder
4. Better compatibility with antivirus software
5. Smaller memory footprint when running

Post-Build Steps:
=================
1. Test the executable:
   cd dist/youtube_automation
   youtube_automation.exe --help

2. Create launchers (optional):
   - Save the batch file content as 'launch.bat'
   - Save the PowerShell content as 'launch.ps1'

3. Package for distribution:
   - Zip the entire youtube_automation folder
   - Include a README with usage instructions

Chrome Path Configuration:
==========================
The bundled Chrome will be used automatically. If you need to update Chrome:
1. Download new Chrome portable
2. Replace the chrome-win64 folder in the distribution
3. Ensure chromedriver.exe version matches Chrome version

Troubleshooting:
================
- If Chrome doesn't launch: Check chrome-win64/chrome.exe exists
- If ChromeDriver fails: Ensure version compatibility
- For path issues: Use relative paths starting with ./ in config.json
- For missing modules: Check _internal folder is complete
"""
