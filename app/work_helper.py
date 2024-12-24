import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.models.app_group import AppGroup
from app.ui.dock_manager import DockManager
from app.ui.group_manager import GroupManager
from app.utils.config_manager import ConfigManager
from app.utils.message_display import MessageDisplay
from app.ui.loading_window import LoadingWindow
from app.ui.project_creator import ProjectCreator
from app.utils.resource_utils import resource_path  # 改用新的导入
from app.utils.autostart import AutoStartManager  # 添加导入
from app.utils.singleton import SingletonManager  # 添加单例管理器

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import json
from datetime import datetime
import webbrowser
import subprocess
import keyboard
import winreg
import win32gui
import win32con
import pystray
from PIL import Image

class WorkHelperApp:
    def __init__(self, root):
        # 在最开始就初始化单例管理器
        self.singleton_manager = SingletonManager()
        
        self.root = root
        self.root.title("工作助手")
        self.root.geometry("900x600")
        self.root.withdraw()  # 先隐藏主窗口
        
        # 显示加载窗口
        self.loading = LoadingWindow(self.root)
        self.loading.show()
        
        # 将窗口居中显示
        self.center_window()
        
        # 设置图标
        self.setup_icon()
        
        # 初始化组件
        self.config = ConfigManager()
        self.message_display = MessageDisplay(self)
        
        # 初始化管理器
        self.autostart_manager = AutoStartManager()
        self.dock_manager = DockManager(self)
        self.group_manager = GroupManager(self)
        
        # 创建主布局
        self.create_main_layout()
        
        # 加载配置
        self.load_config()
        
        # 启动快捷键监听
        self.start_hotkey_listener()
        
        # 创建系统托盘
        self.create_tray()
        
        # 绑定关闭按钮事件
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        # 关闭加载窗口，显示主窗口
        self.loading.destroy()
        self.root.deiconify()

    def center_window(self):
        # 获取屏幕宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 获取窗口宽度和高度
        window_width = 900
        window_height = 600
        
        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_main_layout(self):
        # 创建左右分栏
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # 左侧面板 - 应用组列表
        self.group_manager.create_group_panel(paned)

        # 右侧面板 - 项目创建
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # 添加项目创建面板
        self.project_creator = ProjectCreator(right_frame, self)
        self.project_creator.pack(fill=BOTH, expand=YES)
        
        # 添加 Dock 管理面板到底部
        self.dock_manager.create_dock_panel()

    def toggle_startup(self, enabled):
        if enabled:
            # 添加到开机启动
            self.add_to_startup()
        else:
            # 从开机启动移除
            self.remove_from_startup()

    def add_to_startup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                key,
                "工作助手",
                0,
                winreg.REG_SZ,
                sys.executable
            )
            winreg.CloseKey(key)
        except Exception as e:
            self.message_display.show_error(f"添加开机启动失败: {str(e)}")

    def remove_from_startup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, "工作助手")
            winreg.CloseKey(key)
        except Exception as e:
            self.message_display.show_error(f"移除开机启动失败: {str(e)}")

    def load_config(self):
        self.config.load()
        self.group_manager.update_groups_display()
        # 同时更新托盘菜单
        if hasattr(self, 'groups_menu'):
            self.update_groups_menu()

    def start_hotkey_listener(self):
        def register_hotkeys():
            keyboard.unhook_all()
            for group in self.config.groups.values():
                if not group.hotkey:
                    continue
                try:
                    keys = []
                    for key in group.hotkey.split('+'):
                        if key == '□':
                            keys.append('space')
                        elif key in {'CTRL', 'ALT', 'SHIFT'}:
                            keys.append(key.lower())
                        else:
                            keys.append(key.lower())
                    
                    hotkey = '+'.join(keys)
                    keyboard.add_hotkey(
                        hotkey,
                        lambda g=group: self.group_manager.launch_group(g),
                        suppress=True
                    )
                except Exception as e:
                    print(f"注册快捷键失败 {group.hotkey}: {str(e)}")
        
        register_hotkeys() 

    def hide_window(self):
        """隐藏窗口到托盘"""
        self.root.withdraw()
        # 确保托盘图标存在
        try:
            icon_path = resource_path(os.path.join("app", "assets", "favicon (6).ico"))
            if os.path.exists(icon_path):
                icon = win32gui.LoadImage(
                    0, 
                    icon_path,
                    win32con.IMAGE_ICON,
                    0, 0,
                    win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                )
            else:
                icon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
            
            nid = (self.hwnd, 0, win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                   win32con.WM_USER + 20, icon, "工作助手")
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
        except:
            # 如果修改失败，尝试重新创建
            self.create_tray()

    def show_window(self):
        self.root.deiconify()  # 显示窗口
        self.root.lift()  # 将窗口提升到顶层
        self.root.focus_force()  # 强制获取焦点

    def on_destroy(self, hwnd, msg, wparam, lparam):
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 0))
        win32gui.PostQuitMessage(0)

    def on_command(self, hwnd, msg, wparam, lparam):
        id = wparam & 0xFFFF
        if id == 1:  # 显示
            self.show_window()
        elif id == 2:  # 退出
            win32gui.DestroyWindow(self.hwnd)
            self.root.quit()
        elif 100 <= id < 200:  # 应用组
            # 获取对应的应用组
            groups = list(self.config.groups.values())
            group_index = id - 100
            if group_index < len(groups):
                self.group_manager.launch_group(groups[group_index])

    def on_tray(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONUP:  # 左键点击
            self.show_window()
        elif lparam == win32con.WM_RBUTTONUP:  # 右键点击
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(
                self.menu,
                win32con.TPM_LEFTALIGN | win32con.TPM_BOTTOMALIGN,
                pos[0],
                pos[1],
                0,
                self.hwnd,
                None
            )
        return True

    def quit_app(self, icon=None, item=None):
        """退出应用程序"""
        try:
            # 删除托盘图标
            nid = (self.hwnd, 0)
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        except:
            pass
        
        # 确保在退出时释放互斥体
        del self.singleton_manager
        self.root.destroy()
        sys.exit()

    def setup_icon(self):
        icon_path = resource_path(os.path.join("app", "assets", "favicon (6).ico"))
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

    def create_tray(self):
        # 创建托盘图标
        message_map = {
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER + 20: self.on_tray,
        }

        # 注册窗口类
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = "WorkHelperTray"
        wc.hInstance = win32gui.GetModuleHandle(None)
        
        # 注册
        self.class_atom = win32gui.RegisterClass(wc)
        
        # 创建窗口
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            self.class_atom,
            "WorkHelper",
            style,
            0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
            0, 0, wc.hInstance, None
        )
        
        # 加载自定义图标
        icon_path = resource_path(os.path.join("app", "assets", "favicon (6).ico"))
        if os.path.exists(icon_path):
            icon = win32gui.LoadImage(
                0, 
                icon_path,
                win32con.IMAGE_ICON,
                0, 0,
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            )
        else:
            icon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        
        # 创建托盘图标
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, icon, "工作助手")
        try:
            # 先尝试删除可能存在的旧图标
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        except:
            pass
        # 添加新图标
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        
        # 创建右键菜单
        self.menu = win32gui.CreatePopupMenu()
        
        # 添加应用组子菜单
        self.groups_menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(self.menu, win32con.MF_POPUP, self.groups_menu, "应用组")
        
        # 添加分隔线
        win32gui.AppendMenu(self.menu, win32con.MF_SEPARATOR, 0, '')
        
        # 添加显示和退出选项
        win32gui.AppendMenu(self.menu, win32con.MF_STRING, 1, "显示")
        win32gui.AppendMenu(self.menu, win32con.MF_STRING, 2, "退出")
        
        # 更新应用组菜单
        self.update_groups_menu()

    def update_groups_menu(self):
        """更新托盘菜单中的应用组列表"""
        # 清空现有菜单项
        while win32gui.GetMenuItemCount(self.groups_menu) > 0:
            win32gui.DeleteMenu(self.groups_menu, 0, win32con.MF_BYPOSITION)
        
        # 添加应用组
        for i, group in enumerate(self.config.groups.values()):
            win32gui.AppendMenu(
                self.groups_menu,
                win32con.MF_STRING,
                100 + i,  # 使用 100 以上的 ID 避免冲突
                group.name
            )