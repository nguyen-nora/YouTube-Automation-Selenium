# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Base paths
base_path = os.path.abspath('.')

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[base_path, os.path.join(base_path, 'src')],
    binaries=[],
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

# Add chromedriver to binaries
chromedriver_path = os.path.join(base_path, 'chromedriver.exe')
if os.path.exists(chromedriver_path):
    a.binaries.append((os.path.basename(chromedriver_path), chromedriver_path, 'BINARY'))

# Add Chrome directory files
chrome_path = os.path.join(base_path, 'chrome-win64')
if os.path.exists(chrome_path):
    for root, dirs, files in os.walk(chrome_path):
        for file in files:
            src_path = os.path.join(root, file)
            dst_path = os.path.join('chrome-win64', os.path.relpath(src_path, chrome_path))
            if file.endswith(('.exe', '.dll')):
                a.binaries.append((dst_path, src_path, 'BINARY'))
            else:
                a.datas.append((dst_path, src_path, 'DATA'))

# Add src directory files
src_path = os.path.join(base_path, 'src')
if os.path.exists(src_path):
    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith('.py'):
                src_file = os.path.join(root, file)
                dst_file = os.path.join('src', os.path.relpath(src_file, src_path))
                a.datas.append((dst_file, src_file, 'DATA'))

# Collect all data files from selenium package
# Commented out due to issues with data format
# selenium_datas = collect_data_files('selenium')
# a.datas.extend(selenium_datas)

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
)
