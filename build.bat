@echo off
REM 安装依赖
pip install -r requirements.txt

REM 清理旧的构建文件
rmdir /s /q build dist

REM 打包
pyinstaller --clean ^
    --name "工作助手" ^
    --icon "app/assets/favicon (6).ico" ^
    --noconsole ^
    --add-data "app/assets/*;app/assets/" ^
    --hidden-import win32gui ^
    --hidden-import win32con ^
    --hidden-import winreg ^
    --hidden-import wmi ^
    --hidden-import keyboard ^
    --hidden-import PIL ^
    --hidden-import ttkbootstrap ^
    --hidden-import windnd ^
    --hidden-import pythoncom ^
    --hidden-import win32com.client ^
    --hidden-import pystray ^
    --hidden-import appdirs ^
    run.py

echo 打包完成！
pause 