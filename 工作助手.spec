# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('E:\\2024\\2024_11_19 三个易拉宝\\app\\assets\\favicon (6).ico', 'app/assets'), ('E:\\2024\\2024_11_19 三个易拉宝\\app\\assets\\LIGHTL加载.png', 'app/assets')]
binaries = []
hiddenimports = ['ttkbootstrap', 'keyboard', 'windnd', 'win32gui', 'win32con', 'win32com', 'pythoncom', 'pystray', 'wmi', 'win32wmi', 'appdirs', 'win32event', 'winerror', 'tkinter', 'tkinter.ttk']
tmp_ret = collect_all('ttkbootstrap')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='工作助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['E:\\2024\\2024_11_19 三个易拉宝\\app\\assets\\favicon (6).ico'],
)
