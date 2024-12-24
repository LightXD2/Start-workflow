import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import subprocess
import winreg
import os
import sys
import win32gui
import win32con
import ctypes
from ctypes import wintypes

class DockManager:
    def __init__(self, app):
        self.app = app
        self.dock_enabled = tk.BooleanVar(value=False)
        self.proxy_enabled = tk.BooleanVar(value=self.get_system_proxy_state())
        self.autostart_var = None
        
        # 从配置中读取设置
        self.dock_path = self.app.config.dock_settings.get('dock_path', '')
        
        # 只在没有保存路径时才去检测
        if not self.dock_path:
            self.dock_path = self.detect_dock_path()
            if self.dock_path:
                self.app.config.dock_settings['dock_path'] = self.dock_path
                self.app.config.save()
        
        # 检查 Dock 运行状态
        self.check_dock_status()

    def detect_dock_path(self):
        """检测运行中的 Dock 程序路径"""
        try:
            # 先检查 Dock_64.exe
            process = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq Dock_64.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            if 'Dock_64.exe' in process.stdout:
                import wmi
                c = wmi.WMI()
                for process in c.Win32_Process(name="Dock_64.exe"):
                    path = process.ExecutablePath
                    if path and os.path.exists(path):
                        return path
            
            # 如果没找到，检查 dock.exe
            process = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq dock.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            if 'dock.exe' in process.stdout:
                import wmi
                c = wmi.WMI()
                for process in c.Win32_Process(name="dock.exe"):
                    path = process.ExecutablePath
                    if path and os.path.exists(path):
                        return path
            
            return ""
            
        except Exception as e:
            print(f"检测 Dock 路径失败: {str(e)}")
            return ""

    def create_dock_panel(self):
        # Dock 管理面板
        dock_frame = ttk.LabelFrame(self.app.root, text="Dock 管理", padding=10)
        dock_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # 控制按钮框架
        control_frame = ttk.Frame(dock_frame)
        control_frame.pack(fill=X)
        
        # Dock 开关
        ttk.Checkbutton(
            control_frame,
            text="Dock",
            variable=self.dock_enabled,
            command=self.toggle_dock,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=5)
        
        # 编辑路径按钮
        ttk.Button(
            control_frame,
            text="编辑路径",
            command=self.show_path_dialog,
            width=8
        ).pack(side=LEFT, padx=5)
        
        # 代理开关
        ttk.Checkbutton(
            control_frame,
            text="代理",
            variable=self.proxy_enabled,
            command=self.toggle_proxy,
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=5)
        
        # 系统级开机自启动选项
        self.autostart_var = tk.BooleanVar(value=self.check_autostart())
        ttk.Checkbutton(
            control_frame,
            text="系统自启",
            variable=self.autostart_var,
            command=self.toggle_autostart,
            bootstyle="round-toggle"
        ).pack(side=RIGHT, padx=5)

    def check_dock_status(self):
        """只检查 Dock 是否正在运行，不影响路径"""
        try:
            process = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq Dock_64.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            is_running = 'Dock_64.exe' in process.stdout
            self.dock_enabled.set(is_running)
            return is_running
        except Exception:
            return False

    def toggle_dock(self):
        """根据开关状态启动或关闭 Dock"""
        if self.dock_enabled.get():
            # 启用 Dock
            if self.dock_path:
                # 先隐藏任务栏
                try:
                    hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
                    if hwnd:
                        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                except Exception as e:
                    print(f"隐藏任务栏失败: {str(e)}")
                
                # 再启动 Dock
                subprocess.Popen([self.dock_path])
        else:
            # 禁用 Dock
            try:
                # 先结束 Dock 进程
                subprocess.run(['taskkill', '/F', '/IM', 'Dock_64.exe'], capture_output=True)
                subprocess.run(['taskkill', '/F', '/IM', 'dock.exe'], capture_output=True)
                
                # 关闭任务栏自动隐藏
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3",
                        0,
                        winreg.KEY_READ | winreg.KEY_WRITE
                    )
                    
                    settings = winreg.QueryValueEx(key, "Settings")[0]
                    # 修改设置以禁用自动隐藏
                    settings = (
                        b'\x30\x00\x00\x00\x2e\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                        b'\xd0\x02\x00\x00'
                    )
                    winreg.SetValueEx(key, "Settings", 0, winreg.REG_BINARY, settings)
                    winreg.CloseKey(key)
                except Exception as e:
                    print(f"禁用任务栏自动隐藏失败: {str(e)}")
                
                # 重启 explorer.exe 来应用更改
                subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'])
                subprocess.Popen('explorer.exe')
                
            except Exception as e:
                print(f"禁用 Dock 失败: {str(e)}")

    def check_autostart(self):
        """检查系统级开机自启动状态"""
        return self.app.autostart_manager.is_autostart_enabled()

    def toggle_autostart(self):
        """切换系统级开机自启动状态"""
        try:
            if self.autostart_var.get():
                if not self.app.autostart_manager.enable_autostart():
                    self.autostart_var.set(False)
                    self.app.message_display.show_error("启用系统自启失败，请以管理员身份运行")
            else:
                if not self.app.autostart_manager.disable_autostart():
                    self.autostart_var.set(True)
                    self.app.message_display.show_error("禁用系统自启失败，请以管理员身份运行")
        except Exception as e:
            self.app.message_display.show_error(f"切换系统自启状态失败: {str(e)}")
            self.autostart_var.set(not self.autostart_var.get())

    def show_path_dialog(self):
        # 创建对话框
        dialog = tk.Toplevel(self.app.root)
        dialog.title("设置 Dock 路径")
        dialog.geometry("500x200")
        dialog.transient(self.app.root)  # 设置为主窗口的子窗口
        dialog.grab_set()  # 模态对话框
        
        # 计算居中位置
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() - 500) // 2
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() - 200) // 2
        dialog.geometry(f"500x200+{x}+{y}")
        
        # 路径输入框
        path_frame = ttk.Frame(dialog, padding=15)
        path_frame.pack(fill=X)
        
        path_var = tk.StringVar(value=self.dock_path)
        path_entry = ttk.Entry(path_frame, textvariable=path_var)
        path_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        
        # 浏览按钮
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="选择 Dock 程序",
                filetypes=[("EXE files", "*.exe"), ("All files", "*.*")]
            )
            if file_path:
                path_var.set(file_path)
        
        ttk.Button(
            path_frame,
            text="浏览",
            command=browse_file,
            width=8
        ).pack(side=LEFT)
        
        # 自动搜索按钮
        def auto_detect():
            path = self.detect_dock_path()
            if path:
                path_var.set(path)
                self.app.message_display.show_message("成功", "已找到运行中的 Dock 程序")
            else:
                self.app.message_display.show_message("提示", "未找到运行中的 Dock 程序")
        
        ttk.Button(
            dialog,
            text="自动搜索",
            command=auto_detect,
            bootstyle="info",
            width=15
        ).pack(pady=15)
        
        # 确定和取消按钮
        btn_frame = ttk.Frame(dialog, padding=15)
        btn_frame.pack(fill=X, side=BOTTOM)
        
        def save_path():
            self.dock_path = path_var.get()
            self.app.config.dock_settings['dock_path'] = self.dock_path
            self.app.config.save()
            dialog.destroy()
        
        ttk.Button(
            btn_frame,
            text="确定",
            command=save_path,
            bootstyle="primary",
            width=8
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="取消",
            command=dialog.destroy,
            width=8
        ).pack(side=RIGHT)

    def auto_detect_path(self):
        """自动检测并设置 Dock 路径"""
        path = self.detect_dock_path()
        if path:
            self.dock_path = path
            self.app.config.dock_settings['dock_path'] = path
            self.app.config.save()
            self.app.message_display.show_message("成功", "已找到并保存 Dock 路径")
        else:
            self.app.message_display.show_message("提示", "未找到运行中的 Dock 程序")

    def toggle_proxy(self):
        """切换代理状态"""
        try:
            # 获取当前代理设置
            INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                0, winreg.KEY_ALL_ACCESS)
            
            # 切换启用/禁用状态
            winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyEnable', 0, winreg.REG_DWORD, 
                             1 if self.proxy_enabled.get() else 0)
            
            # 刷新系统代理设置
            INTERNET_OPTION_REFRESH = 37
            INTERNET_OPTION_SETTINGS_CHANGED = 39
            internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
            internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
            internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        except Exception as e:
            self.app.message_display.show_error(f"切换代理失败: {str(e)}")
            # 如果失败，恢复开关状态
            self.proxy_enabled.set(not self.proxy_enabled.get())

    def get_system_proxy_state(self):
        """获取系统代理状态"""
        try:
            INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                0, winreg.KEY_READ)
            
            proxy_enable, _ = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyEnable')
            winreg.CloseKey(INTERNET_SETTINGS)
            return bool(proxy_enable)
        except Exception:
            return False