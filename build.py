import PyInstaller.__main__
import os
import shutil
import sys
import time
import tkinter

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义资源文件路径
assets_dir = os.path.join(current_dir, "app", "assets")
icon_path = os.path.join(assets_dir, "favicon (6).ico")
loading_path = os.path.join(assets_dir, "LIGHTL加载.png")

# 检查资源文件
if not os.path.exists(icon_path):
    print("错误: 找不到图标文件!")
    exit(1)

if not os.path.exists(loading_path):
    print("错误: 找不到加载图片!")
    exit(1)

# 定义打包参数
args = [
    'run.py',  # 入口文件
    '--name=工作助手',
    '--onefile',
    '--noconsole',
    '--windowed',
    f'--icon={icon_path}',
    '--noconfirm',
    '--clean',
    # 添加资源文件
    f'--add-data={icon_path};app/assets',
    f'--add-data={loading_path};app/assets',
    # 添加必要的导入
    '--hidden-import=ttkbootstrap',
    '--hidden-import=keyboard',
    '--hidden-import=windnd',
    '--hidden-import=win32gui',
    '--hidden-import=win32con',
    '--hidden-import=win32com',
    '--hidden-import=pythoncom',
    '--hidden-import=pystray',
    '--hidden-import=wmi',
    '--hidden-import=win32wmi',
    '--hidden-import=appdirs',
    '--hidden-import=win32event',
    '--hidden-import=winerror',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    # 收集所有依赖
    '--collect-all=ttkbootstrap',
    '--noupx',
]

try:
    # 清理旧的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        
    # 执行打包
    PyInstaller.__main__.run(args)
    print("打包完成！")
    print(f"可执行文件位置: {os.path.join(current_dir, 'dist', '工作助手.exe')}")
except Exception as e:
    print(f"打包失败: {str(e)}") 