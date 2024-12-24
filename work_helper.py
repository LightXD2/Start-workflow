import os
import json
from datetime import datetime
import webbrowser
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import keyboard
import threading
from PIL import Image, ImageTk
import time
import sys
import winreg
import win32gui
import win32con

class AppGroup:
    def __init__(self, name, apps=None, websites=None, files=None, hotkey=None):
        self.name = name
        self.apps = apps or []
        self.websites = websites or []
        self.files = files or []
        self.hotkey = hotkey

class WorkHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("工作助手")
        self.root.geometry("900x600")
        
        # 设置图标
        icon_path = "favicon (6).ico"
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        self.groups = {}
        self.config_file = "app_groups.json"
        
        # 设置深色主题
        style = ttk.Style(theme="darkly")
        
        # 添加自定义蓝色按钮样式
        style.configure(
            "blue.TButton",
            background="#00a4ff",
            foreground="white"
        )
        style.map(
            "blue.TButton",
            background=[("active", "#0093e6"), ("pressed", "#0082cc")],
            foreground=[("active", "white"), ("pressed", "white")]
        )
        
        # 添加 primary 样式
        style.configure(
            "primary.TButton",
            background="#00a4ff",
            foreground="white"
        )
        style.map(
            "primary.TButton",
            background=[("active", "#0093e6"), ("pressed", "#0082cc")],
            foreground=[("active", "white"), ("pressed", "white")]
        )
        
        # 创建主布局
        self.create_main_layout()
        
        # 加载保存的配置
        self.load_config()
        
        # 启动快捷键监听
        self.start_hotkey_listener()
        
        # 修改 Dock 程序路径，从配置文件读取
        self.dock_path = self.load_dock_config().get('dock_path', r"D:\RuanJian2\steam2\steamapps\common\MyDockFinder\Dock_64.exe")
        
        # 添加 Dock 管理按钮
        self.add_dock_controls()
        
        self.hotkey_recording = False  # 添加标志位
        self.hotkey_listener = None    # 保存监听器引用

    def create_main_layout(self):
        # 创建左右分栏
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # 左侧面板 - 应用组列表
        left_frame = ttk.LabelFrame(paned, text="应用组", padding=10)
        self.groups_frame = ScrolledFrame(left_frame)
        self.groups_frame.pack(fill=BOTH, expand=YES)
        
        # 添加新组按钮
        add_group_btn = ttk.Button(
            left_frame,
            text="添加新组",
            command=self.add_group_dialog,
            style="blue.TButton",
            width=20
        )
        add_group_btn.pack(pady=10)
        
        paned.add(left_frame, weight=1)

        # 右侧面板 - 项目创建
        right_frame = ttk.LabelFrame(paned, text="项目创建", padding=10)
        
        # 项目名称输入
        ttk.Label(right_frame, text="项目名称：").pack(pady=5)
        self.project_name = ttk.Entry(right_frame, width=30)
        self.project_name.pack(pady=5)
        
        # 项目路径选择
        path_frame = ttk.Frame(right_frame)
        path_frame.pack(fill=X, pady=5)
        
        self.project_path = ttk.Entry(path_frame, width=30)
        self.project_path.pack(side=LEFT, expand=YES, fill=X, padx=(0, 5))
        self.project_path.insert(0, r"E:\2024")
        
        browse_btn = ttk.Button(
            path_frame,
            text="浏览",
            command=self.browse_path,
            bootstyle="secondary-outline",
            width=8
        )
        browse_btn.pack(side=RIGHT)
        
        # 创建项目按钮
        create_btn = ttk.Button(
            right_frame,
            text="创建项目",
            command=self.create_project,
            style="blue.TButton",
            width=20
        )
        create_btn.pack(pady=20)
        
        paned.add(right_frame, weight=1)

    def add_group_dialog(self):
        dialog = ttk.Toplevel(self.root)
        dialog.title("添加应用组")
        dialog.geometry("600x700")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # 组名
        ttk.Label(frame, text="组名：").pack(anchor=W)
        group_name = ttk.Entry(frame, width=40)
        group_name.pack(fill=X, pady=(0, 10))
        
        def save_group():
            name = group_name.get()
            if not name:
                messagebox.showwarning("警告", "请输入组名")
                return
            
            self.groups[name] = AppGroup(
                name=name,
                apps=[],
                websites=[],
                files=[],
                hotkey=""
            )
            
            self.save_config()
            self.update_groups_display()
            dialog.destroy()
        
        # 保存按钮
        ttk.Button(
            frame,
            text="保存",
            command=save_group,
            style="blue.TButton",
            width=20
        ).pack(pady=10)

    def start_hotkey_recorder(self, callback):
        """记录快捷键组合"""
        self.hotkey_recording = True
        self.pressed_keys = set()
        
        def on_press(e):
            if not self.hotkey_recording:
                return
            
            key = e.name.upper()
            # 标准化按键名称
            key_mapping = {
                'CONTROL': 'CTRL',
                'CTRL': 'CTRL',
                'ALT': 'ALT',
                'SHIFT': 'SHIFT',
                'SPACE': '□'
            }
            
            key = key_mapping.get(key, key)
            if key not in self.pressed_keys:
                self.pressed_keys.add(key)
                
                # 生成当前组合键字符串
                modifiers = {'CTRL', 'ALT', 'SHIFT'}
                sorted_keys = []
                
                # 修饰键优先
                for mod in ['CTRL', 'ALT', 'SHIFT']:
                    if mod in self.pressed_keys:
                        sorted_keys.append(mod)
                
                # 其他键按字母顺序
                other_keys = sorted(k for k in self.pressed_keys if k not in modifiers)
                sorted_keys.extend(other_keys)
                
                hotkey = '+'.join(sorted_keys)
                callback(hotkey)
        
        def on_release(e):
            if not self.hotkey_recording:
                return
            
            key = e.name.upper()
            key_mapping = {
                'CONTROL': 'CTRL',
                'CTRL': 'CTRL',
                'ALT': 'ALT',
                'SHIFT': 'SHIFT',
                'SPACE': '□'
            }
            key = key_mapping.get(key, key)
            
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            
            if not self.pressed_keys:  # 当所有键都释放时
                self.hotkey_recording = False
                keyboard.unhook_all()
        
        keyboard.on_press(on_press)
        keyboard.on_release(on_release)

    def start_hotkey_listener(self):
        """启动全局快捷键监听"""
        def register_hotkeys():
            keyboard.unhook_all()  # 清除所有现有的快捷键
            
            for group in self.groups.values():
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
                        lambda g=group: self.launch_group(g),
                        suppress=True
                    )
                except Exception as e:
                    print(f"注册快捷键失败 {group.hotkey}: {str(e)}")
        
        register_hotkeys()

    def launch_group(self, group):
        # 启动应用程序
        for app in group.apps:
            try:
                # 检查文件是否存在
                if not os.path.exists(app):
                    messagebox.showerror("错误", f"找不到程序: {app}")
                    continue
                    
                # 使用 subprocess.Popen 启动程序，并添加错误处理
                process = subprocess.Popen(app, shell=True)
                
            except PermissionError:
                messagebox.showerror("错误", f"没有权限运行程序: {app}")
            except Exception as e:
                messagebox.showerror("错误", f"启动程序失败 {app}: {str(e)}")
        
        # 打开网站
        for site in group.websites:
            try:
                webbrowser.open(site)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开网站 {site}: {str(e)}")
        
        # 打开文件
        for file in group.files:
            try:
                if not os.path.exists(file):
                    messagebox.showerror("错误", f"找不到文件: {file}")
                    continue
                    
                os.startfile(file)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件 {file}: {str(e)}")

    def update_groups_display(self):
        # 清除现有显示
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
            
        # 显示所有组
        for group in self.groups.values():
            group_frame = ttk.Frame(self.groups_frame)
            group_frame.pack(fill=X, pady=5, padx=5)
            
            # 左侧信息
            info_frame = ttk.Frame(group_frame)
            info_frame.pack(fill=X, expand=True)
            
            ttk.Label(
                info_frame,
                text=f"{group.name}",
                font=("Helvetica", 10, "bold")
            ).pack(side=LEFT)
            
            if group.hotkey:
                ttk.Label(
                    info_frame,
                    text=f" ({group.hotkey})",
                    font=("Helvetica", 9)
                ).pack(side=LEFT)
            
            # 按钮容器
            btn_frame = ttk.Frame(group_frame)
            btn_frame.pack(fill=X, pady=5)
            
            # 启动按钮
            ttk.Button(
                btn_frame,
                text="启动",
                command=lambda g=group: self.launch_group(g),
                style="blue.TButton",
                width=15
            ).pack(side=LEFT, padx=5)
            
            # 编辑按钮（使用⚙图标）
            ttk.Button(
                btn_frame,
                text="⚙",
                command=lambda g=group: self.edit_group_dialog(g),
                bootstyle="secondary",
                width=3
            ).pack(side=LEFT, padx=5)
            
            # 删除按钮
            ttk.Button(
                btn_frame,
                text="删除",
                command=lambda n=group.name: self.delete_group(n),
                bootstyle="danger",
                width=15
            ).pack(side=LEFT, padx=5)

    def edit_group_dialog(self, group):
        dialog = ttk.Toplevel(self.root)
        dialog.title(f"编辑应用组 - {group.name}")
        dialog.geometry("600x700")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # 组名
        ttk.Label(frame, text="组名：").pack(anchor=W)
        group_name = ttk.Entry(frame, width=40)
        group_name.insert(0, group.name)
        group_name.pack(fill=X, pady=(0, 10))
        
        # 创建notebook用于分类显示
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=BOTH, expand=YES, pady=10)
        
        # 应用程序标签页
        apps_frame = ttk.Frame(notebook, padding=10)
        notebook.add(apps_frame, text="应用程序")
        
        apps_list = group.apps.copy()
        
        # 应用程序控制按钮
        apps_btn_frame = ttk.Frame(apps_frame)
        apps_btn_frame.pack(fill=X, pady=(0, 5))
        
        # 使用 Listbox 替代 Text 控件来显示应用列表
        apps_listbox = tk.Listbox(apps_frame, height=10)
        apps_listbox.pack(fill=BOTH, expand=YES, pady=5)
        
        def update_apps_display():
            apps_listbox.delete(0, tk.END)
            for app in apps_list:
                apps_listbox.insert(tk.END, app)
        
        def add_app():
            file_path = filedialog.askopenfilename(
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if file_path:
                apps_list.append(file_path)
                update_apps_display()
        
        def delete_selected_apps():
            selection = apps_listbox.curselection()
            if selection:
                # 从后往前删除，避免索引变化
                for index in reversed(selection):
                    del apps_list[index]
                update_apps_display()
        
        # 添加应用按钮
        ttk.Button(
            apps_btn_frame,
            text="添加应用",
            command=add_app,
            bootstyle="secondary-outline",
            width=15
        ).pack(side=LEFT, padx=2)
        
        # 删除选中按钮
        ttk.Button(
            apps_btn_frame,
            text="删除选中",
            command=delete_selected_apps,
            bootstyle="danger-outline",
            width=15
        ).pack(side=LEFT, padx=2)
        
        # 初始显示应用列表
        update_apps_display()
        
        # 网站标签页
        websites_frame = ttk.Frame(notebook, padding=10)
        notebook.add(websites_frame, text="网站")
        
        websites_list = group.websites.copy()
        
        # 网站控制按钮和输入框
        web_input_frame = ttk.Frame(websites_frame)
        web_input_frame.pack(fill=X, pady=(0, 5))
        
        # 添加网站输入框
        website_entry = ttk.Entry(web_input_frame)
        website_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        
        # 网站列表显示
        websites_listbox = tk.Listbox(websites_frame, height=10)
        websites_listbox.pack(fill=BOTH, expand=YES, pady=5)
        
        def update_websites_display():
            websites_listbox.delete(0, tk.END)
            for site in websites_list:
                websites_listbox.insert(tk.END, site)
        
        def add_website():
            website = website_entry.get()
            if website:
                websites_list.append(website)
                website_entry.delete(0, tk.END)
                update_websites_display()
        
        def delete_selected_websites():
            selection = websites_listbox.curselection()
            if selection:
                for index in reversed(selection):
                    del websites_list[index]
                update_websites_display()
        
        # 添加网站按钮
        ttk.Button(
            web_input_frame,
            text="添加",
            command=add_website,
            bootstyle="secondary-outline",
            width=8
        ).pack(side=LEFT, padx=2)
        
        # 删除选中按钮
        ttk.Button(
            web_input_frame,
            text="删除选中",
            command=delete_selected_websites,
            bootstyle="danger-outline",
            width=15
        ).pack(side=LEFT, padx=2)
        
        # 初始显示网站列表
        update_websites_display()
        
        # 文件标签页
        files_frame = ttk.Frame(notebook, padding=10)
        notebook.add(files_frame, text="文件")
        
        files_list = group.files.copy() if group.files else []
        
        # 文件控制按钮
        files_btn_frame = ttk.Frame(files_frame)
        files_btn_frame.pack(fill=X, pady=(0, 5))
        
        # 文件列表显示
        files_listbox = tk.Listbox(files_frame, height=10)
        files_listbox.pack(fill=BOTH, expand=YES, pady=5)
        
        def update_files_display():
            files_listbox.delete(0, tk.END)
            for file_path in files_list:
                file_name = os.path.basename(file_path)
                files_listbox.insert(tk.END, file_name)
        
        def add_files():
            file_paths = filedialog.askopenfilenames(
                title="选择文件",
                filetypes=[("所有文件", "*.*")]
            )
            if file_paths:
                for path in file_paths:
                    if path not in files_list:
                        files_list.append(path)
                update_files_display()
        
        def delete_selected_files():
            selection = files_listbox.curselection()
            if selection:
                for index in reversed(selection):
                    del files_list[index]
                update_files_display()
        
        # 添加文件按钮
        ttk.Button(
            files_btn_frame,
            text="添加文件",
            command=add_files,
            bootstyle="secondary-outline",
            width=15
        ).pack(side=LEFT, padx=2)
        
        # 删除文件按钮
        ttk.Button(
            files_btn_frame,
            text="删除选中",
            command=delete_selected_files,
            bootstyle="danger-outline",
            width=15
        ).pack(side=LEFT, padx=2)
        
        # 双击打开文件
        def on_double_click(event):
            selection = files_listbox.curselection()
            if selection:
                index = selection[0]
                file_path = files_list[index]
                try:
                    os.startfile(file_path)
                except Exception as e:
                    messagebox.showerror("错误", f"无法打开文件: {str(e)}")
        
        files_listbox.bind("<Double-Button-1>", on_double_click)
        
        # 初始显示文件列表
        update_files_display()
        
        # 快捷键和保存按钮放在底部固定位置
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill=X, side=BOTTOM, pady=10)
        
        # 快捷键
        hotkey_frame = ttk.Frame(bottom_frame)
        hotkey_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(hotkey_frame, text="快捷键：").pack(side=LEFT)
        hotkey_var = tk.StringVar(value=group.hotkey or "")
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=hotkey_var, state="readonly")
        hotkey_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        def record_hotkey():
            hotkey_btn.config(text="请按下快捷键组合...")
            
            def on_hotkey_set(hotkey):
                # 检查快捷键是否已被使用
                for g in self.groups.values():
                    if g.name != group.name and g.hotkey == hotkey:
                        messagebox.showwarning(
                            "警告",
                            f"快捷键 {hotkey} 已被组 '{g.name}' 使用"
                        )
                        hotkey_btn.config(text="设置快捷键")
                        return
                        
                hotkey_var.set(hotkey)
                hotkey_btn.config(text="设置快捷键")
                
            self.start_hotkey_recorder(on_hotkey_set)
            
        hotkey_btn = ttk.Button(
            hotkey_frame,
            text="设置快捷键",
            command=record_hotkey,
            bootstyle="secondary-outline"
        )
        hotkey_btn.pack(side=RIGHT)
        
        # 保存按钮
        def save_changes():
            name = group_name.get()
            if not name:
                messagebox.showwarning("警告", "请输入组名")
                return
        
            # 如果组名改变了，需要删除旧组
            if name != group.name:
                del self.groups[group.name]
        
            # 更新组信息
            self.groups[name] = AppGroup(
                name=name,
                apps=apps_list,
                websites=websites_list,
                files=files_list,
                hotkey=hotkey_var.get()
            )
            
            self.save_config()
            self.update_groups_display()
            dialog.destroy()
        
        ttk.Button(
            bottom_frame,
            text="保存更改",
            command=save_changes,
            bootstyle="primary",
            width=20
        ).pack(pady=(10, 0))

    def delete_group(self, name):
        if messagebox.askyesno("确认", f"确定要删除组 '{name}' 吗？"):
            del self.groups[name]
            self.save_config()
            self.update_groups_display()

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path.delete(0, tk.END)
            self.project_path.insert(0, path)

    def create_project(self):
        project_name = self.project_name.get()
        if not project_name:
            return
        
        today = datetime.now().strftime("%Y_%m_%d")  # 使用下划线连接日期
        base_path = self.project_path.get()
        project_path = os.path.join(base_path, f"{today} {project_name}")  # 日期和项目名之间用空格
        subfolders = ["素材", "原始素材", "工程文件", "导出"]
        
        try:
            os.makedirs(project_path, exist_ok=True)
            for folder in subfolders:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                
            self.show_temp_message("成功", f"项目文件夹创建成功：\n{project_path}")
            os.startfile(project_path)
            
        except Exception as e:
            self.show_temp_message("错误", f"创建文件夹时出错：{str(e)}")

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # 检查是否是新格式（包含 groups 和 project_hotkey）
                    if 'groups' in data:
                        self.groups = {
                            name: AppGroup(**group_data)
                            for name, group_data in data['groups'].items()
                        }
                        self.project_hotkey = data.get('project_hotkey', '')
                    # 旧格式（直接是组的数据）
                    else:
                        self.groups = {
                            name: AppGroup(
                                name=group_data['name'],
                                apps=group_data.get('apps', []),
                                websites=group_data.get('websites', []),
                                files=group_data.get('files', []),
                                hotkey=group_data.get('hotkey', '')
                            )
                            for name, group_data in data.items()
                        }
                self.update_groups_display()
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件时出错：{str(e)}")
            # 如果配置文件损坏，初始化为空配置
            self.groups = {}
            self.project_hotkey = ""

    def save_config(self):
        """保存配置后重新注册快捷键"""
        data = {
            name: {
                'name': group.name,
                'apps': group.apps,
                'websites': group.websites,
                'files': group.files,
                'hotkey': group.hotkey
            }
            for name, group in self.groups.items()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 重新注册快捷键
        keyboard.unhook_all()
        self.start_hotkey_listener()

    def add_dock_controls(self):
        # 创建 Dock 控制面板
        dock_frame = ttk.LabelFrame(self.root, text="Dock 管理", padding=10)
        dock_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        # 创建按钮容器
        btn_frame = ttk.Frame(dock_frame)
        btn_frame.pack(fill=X)
        
        # 启动 Dock 按钮
        start_dock_btn = ttk.Button(
            btn_frame,
            text="启动 Dock",
            command=self.start_dock,
            style="blue.TButton",
            width=15
        )
        start_dock_btn.pack(side=LEFT, padx=5)
        
        # 结束 Dock 按钮
        kill_dock_btn = ttk.Button(
            btn_frame,
            text="结束 Dock",
            command=self.kill_dock,
            bootstyle="danger-outline",
            width=15
        )
        kill_dock_btn.pack(side=LEFT, padx=5)
        
        # 编辑路径按钮
        edit_path_btn = ttk.Button(
            btn_frame,
            text="编辑路径",
            command=self.edit_dock_path,
            bootstyle="secondary-outline",
            width=15
        )
        edit_path_btn.pack(side=LEFT, padx=5)
        
        # 开机自启动选项
        self.autostart_var = tk.BooleanVar(value=self.check_autostart())
        autostart_cb = ttk.Checkbutton(
            btn_frame,
            text="开机自启",
            variable=self.autostart_var,
            command=self.toggle_autostart,
            bootstyle="primary-round-toggle"
        )
        autostart_cb.pack(side=LEFT, padx=5)

    def start_dock(self):
        try:
            subprocess.Popen(self.dock_path)
            self.show_temp_message("成功", "Dock 已启动")
        except Exception as e:
            self.show_temp_message("错误", f"无法启动 Dock: {str(e)}")

    def kill_dock(self):
        try:
            # 先获取进程 ID
            process = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq Dock_64.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            
            if 'Dock_64.exe' in process.stdout:
                # 结束进程
                subprocess.run(
                    ['taskkill', '/F', '/IM', 'Dock_64.exe'],
                    capture_output=True
                )
                
                # 修改任务栏设置为始终显示
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\StuckRects3",
                                    0, 
                                    winreg.KEY_SET_VALUE)
                
                # 设置任务栏属性：
                # 位置在底部(03)，始终显示(02)
                settings = (
                    b'\x30\x00\x00\x00'  # 头部
                    b'\xfe\xff\xff\xff'   # 设置标识
                    b'\x02\x00\x00\x00'   # 显示设置 (02 = 始终显示)
                    b'\x03\x00\x00\x00'   # 位置 (03 = 底部)
                    b'\x00\x00\x00\x00'   # 左边界
                    b'\x00\x00\x00\x00'   # 顶边界
                    b'\x00\x04\x00\x00'   # 右边界
                    b'\xd0\x02\x00\x00'   # 底边界
                )
                
                winreg.SetValueEx(key, "Settings", 0, winreg.REG_BINARY, settings)
                winreg.CloseKey(key)
                
                # 重启资源管理器以应用更改
                subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'])
                subprocess.Popen('explorer.exe')
                
                self.show_temp_message("成功", "Dock 已结束，任务栏已设置为始终显示")
            else:
                self.show_temp_message("提示", "Dock 进程未运行")
                
        except Exception as e:
            self.show_temp_message("错误", f"操作失败: {str(e)}")

    def edit_dock_path(self):
        file_path = filedialog.askopenfilename(
            title="选择 Dock 程序",
            filetypes=[("EXE files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.dock_path = file_path
            self.save_dock_config({'dock_path': file_path})
            self.show_temp_message("成功", "Dock 路径已更新")

    def check_autostart(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, "WorkHelper")
                return True
            except:
                return False
            finally:
                winreg.CloseKey(key)
        except:
            return False

    def toggle_autostart(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_READ
            )
            
            if self.autostart_var.get():
                # 添加开机自启
                exe_path = sys.executable
                if hasattr(sys, '_MEIPASS'):  # 如果是打包后的exe
                    exe_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(
                    key,
                    "WorkHelper",
                    0,
                    winreg.REG_SZ,
                    f'"{exe_path}"'
                )
                self.show_temp_message("成功", "已添加到开机自启")
            else:
                # 移除开机自启
                try:
                    winreg.DeleteValue(key, "WorkHelper")
                    self.show_temp_message("成功", "已移除开机自启")
                except:
                    pass
            
            winreg.CloseKey(key)
        except Exception as e:
            self.show_temp_message("错误", f"设置开机自启失败: {str(e)}")
            self.autostart_var.set(not self.autostart_var.get())  # 恢复复选框状态

    def save_dock_config(self, settings):
        try:
            data = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            data['dock_settings'] = settings
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def load_dock_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('dock_settings', {})
        except:
            return {}

    def create_project_dialog(self):
        dialog = ttk.Toplevel(self.root)
        dialog.title("创建项目")
        dialog.geometry("300x150")
        
        # 设置对话框在屏幕中央
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # 设置为模态对话框
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # 项目名称输入
        ttk.Label(frame, text="项目名称：").pack(pady=5)
        project_name_entry = ttk.Entry(frame, width=30)
        project_name_entry.pack(pady=5)
        project_name_entry.focus()  # 自动聚焦到输入框
        
        def create_and_close():
            project_name = project_name_entry.get()
            if project_name:
                base_path = self.project_path.get()
                today = datetime.now().strftime("%Y_%m_%d")  # 使用下划线连接日期
                project_path = os.path.join(base_path, f"{today} {project_name}")  # 日期和项目名之间用空格
                subfolders = ["素材", "原始素材", "工程文件", "导出"]
                
                try:
                    os.makedirs(project_path, exist_ok=True)
                    for folder in subfolders:
                        folder_path = os.path.join(project_path, folder)
                        os.makedirs(folder_path, exist_ok=True)
                        
                    os.startfile(project_path)
                    dialog.destroy()
                    
                except Exception as e:
                    print(f"创建文件夹时出错：{str(e)}")
            else:
                print("请输入项目名称")
        
        # 回车键绑定
        project_name_entry.bind('<Return>', lambda e: create_and_close())
        
        # 创建按钮
        ttk.Button(
            frame,
            text="创建项目",
            command=create_and_close,
            bootstyle="primary",
            width=20
        ).pack(pady=20)

    def show_temp_message(self, title, message, parent=None):
        dialog = ttk.Toplevel(parent or self.root)
        dialog.title(title)
        dialog.geometry("300x100")
        
        # 设置窗口样式
        dialog.transient(parent or self.root)
        dialog.overrideredirect(True)  # 移除标题栏
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # 创建消息标签
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # 添加图标标签
        icon_label = ttk.Label(frame, text="i", font=("Segoe UI", 20))
        icon_label.pack()
        
        msg_label = ttk.Label(frame, text=message)
        msg_label.pack(pady=10)
        
        # 2秒后自动关闭
        dialog.after(2000, dialog.destroy)

    def toggle_dock(self, enabled):
        if enabled:
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
                # 先显示任务栏
                hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                
                # 再结束 Dock 进程
                subprocess.run(['taskkill', '/F', '/IM', 'Dock_64.exe'], capture_output=True)
                subprocess.run(['taskkill', '/F', '/IM', 'dock.exe'], capture_output=True)
            except Exception as e:
                print(f"禁用 Dock 失败: {str(e)}")

def main():
    root = ttk.Window()
    style = ttk.Style(theme="darkly")
    app = WorkHelperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 

