# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/assets/favicon (6).ico', 'app/assets'),
        ('app/assets/LIGHTL加载.png', 'app/assets'),
    ],
    hiddenimports=[
        'win32gui',
        'win32con',
        'winreg',
        'wmi',
        'keyboard',
        'PIL',
        'ttkbootstrap',
        'windnd',
        'pythoncom',
        'win32com.client',
        'pystray',
        'appdirs',
        'win32api',
        'win32com',
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='工作助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/assets/favicon (6).ico',
    version='file_version_info.txt'
)
