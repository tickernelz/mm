# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get project paths
project_root = Path(SPECPATH)
src_dir = project_root / "src"

# Add src to path
sys.path.insert(0, str(src_dir))

block_cipher = None

a = Analysis(
    [str(src_dir / "mm" / "__main__.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        (str(src_dir / "mm"), "mm"),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'pyautogui',
        'psutil',
        'setproctitle',
        'hashlib',
        'time',
        'fcntl',
        'mm.main',
        'mm.gui',
        'mm.config',
        'mm.mouse_controller',
        'mm.system_tray',
        'mm.idle_detector',
        'mm.logger',
        'mm.singleton',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable with proper name
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='telek',  # Use proper application name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(src_dir / "mm" / "resources" / "icon.icns") if (src_dir / "mm" / "resources" / "icon.icns").exists() else None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='telek.app',
        icon=str(src_dir / "mm" / "resources" / "icon.icns") if (src_dir / "mm" / "resources" / "icon.icns").exists() else None,
        bundle_identifier='com.telek.app',  # Use proper bundle identifier
        info_plist={
            'CFBundleName': 'telek',
            'CFBundleDisplayName': 'telek',
            'CFBundleExecutable': 'telek',
            'CFBundleIdentifier': 'com.telek.app',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'LSUIElement': True,  # Hide from dock
            'LSBackgroundOnly': False,
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'NSAppleEventsUsageDescription': 'telek needs accessibility permissions to control mouse movement.',
            'NSSystemAdministrationUsageDescription': 'telek needs permissions to prevent system sleep.',
        },
    )