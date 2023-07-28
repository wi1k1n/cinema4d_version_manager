# -*- mode: python ; coding: utf-8 -*-

APP_NAME = 'C4DVersionManager' # !!! Changing this would create separate .spec file with default settings

# PyInstaller configs
block_cipher = None
a = Analysis(
    ['../../source/__init__.py'],
    pathex=['../../venv/Lib/site-packages', '../../source'],
    binaries=[],
    datas=[('../../res/images', './res/images'),
           (f'build/{APP_NAME}/build.txt', '.')],
    hiddenimports=[],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    icon='../../res/images/icon.png',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
