# -*- mode: python ; coding: utf-8 -*-


import os

# Base paths
base_path = os.path.abspath('.')

a = Analysis(
    ['test_bundle.py'],
    pathex=[base_path],
    binaries=[],
    datas=[
        # Configuration files
        ('config.json', '.'),
        ('accounts.json', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='test_bundle',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
