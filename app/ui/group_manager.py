import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
from tkinter import messagebox, filedialog
import os
import webbrowser
import subprocess
import keyboard
from app.models.app_group import AppGroup
from PIL import Image, ImageTk
import windnd  # 添加这行
import win32com.client
import pythoncom

class GroupManager:
    def __init__(self, app):
        self.app = app
        self.groups_frame = None
        self.hotkey_recording = False
        self.pressed_keys = set()
        
    def create_group_panel(self, parent):
        left_frame = ttk.LabelFrame(parent, text="应用组", padding=10)
        self.groups_frame = ScrolledFrame(left_frame)
        self.groups_frame.pack(fill=BOTH, expand=YES)
        
        add_group_btn = ttk.Button(
            left_frame,
            text="添加新组",
            command=self.add_group_dialog,
            style="blue.TButton",
            width=25
        )
        add_group_btn.pack(pady=10)
        
        parent.add(left_frame, weight=1)
        
        # 启用拖放功能
        windnd.hook_dropfiles(self.groups_frame, func=self.handle_drop)

    def handle_drop(self, files):
        try:
            # 检查是否有选中的组
            if not hasattr(self, 'current_group') or not self.current_group:
                self.app.message_display.show_error("请先选择一个应用组")
                return
            
            for file in files:
                # 将 bytes 转换为字符串
                file_path = file.decode('gbk')
                # 添加到当前选中的组
                self.add_app_to_group(self.current_group, file_path)
        except Exception as e:
            self.app.message_display.show_error(f"处理拖放文件失败: {str(e)}")

    def add_group_dialog(self):
        dialog = ttk.Toplevel(self.app.root)
        dialog.title("添加应用组")
        dialog.geometry("400x150")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # 使用微软雅黑字体
        ttk.Label(
            frame,
            text="确认组名：",
            font=("Microsoft YaHei UI", 10)  # 使用统一的微软雅黑字体
        ).pack(anchor=W)
        
        group_name = ttk.Entry(frame, width=40)
        group_name.pack(fill=X, pady=(0, 10))
        
        def save_group():
            name = group_name.get()
            if not name:
                self.app.message_display.show_message("警告", "请输入组名")
                return
            
            self.app.config.groups[name] = AppGroup(name=name)
            self.app.config.save()
            self.update_groups_display()
            dialog.destroy()
        
        # 添加回车确认功能
        group_name.bind('<Return>', lambda e: save_group())
        
        ttk.Button(
            frame,
            text="保存",
            command=save_group,
            style="blue.TButton",
            width=20
        ).pack(pady=10)

        # 设置对话框为模态并居中显示
        dialog.transient(self.app.root)
        dialog.grab_set()
        self.center_window(dialog)
        
        # 聚焦到输入框
        group_name.focus()

    def edit_group_dialog(self, group):
        """编辑应用组对话框"""
        dialog = ttk.Toplevel(self.app.root)
        dialog.title(f"编辑应用组 - {group.name}")
        dialog.geometry("600x700")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        # 创建notebook
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=BOTH, expand=YES, pady=10)
        
        # 应用程序标签页
        apps_frame = self.create_apps_tab(notebook, group)
        notebook.add(apps_frame, text="应用程序")
        
        # 网站标签页
        websites_frame = self.create_websites_tab(notebook, group)
        notebook.add(websites_frame, text="网站")
        
        # 文件标签页
        files_frame = self.create_files_tab(notebook, group)
        notebook.add(files_frame, text="文件")
        
        # 项目标签页
        project_frame = ttk.Frame(notebook, padding=10)
        notebook.add(project_frame, text="项目")
        
        # 项目选择
        ttk.Label(project_frame, text="启动时创建项目:").pack(pady=10)
        project_var = tk.StringVar(value=self.get_project_choice(group))
        project_combo = ttk.Combobox(
            project_frame,
            textvariable=project_var,
            values=["不创建", "项目1", "项目2"],
            state="readonly",
            width=20
        )
        project_combo.pack(pady=5)
        
        # 设置当前值
        if group.project_type == "project1":
            project_combo.set("项目1")
        elif group.project_type == "project2":
            project_combo.set("项目2")
        else:
            project_combo.set("不创建")
        
        # 设置框架
        settings_frame = ttk.Frame(frame)
        settings_frame.pack(fill=X, pady=10)
        
        # Dock 设置
        dock_frame = ttk.Frame(settings_frame)
        dock_frame.pack(fill=X, pady=(0, 5))
        
        dock_var = tk.BooleanVar(value=group.dock_enabled)
        ttk.Checkbutton(
            dock_frame,
            text="启动时开启 Dock",
            variable=dock_var,
            bootstyle="round-toggle"
        ).pack(side=LEFT)
        
        # 快捷键设置
        hotkey_frame = ttk.Frame(settings_frame)
        hotkey_frame.pack(fill=X, pady=5)
        
        ttk.Label(hotkey_frame, text="快捷键：").pack(side=LEFT)
        hotkey_var = tk.StringVar(value=group.hotkey)
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=hotkey_var, state="readonly")
        hotkey_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        # 清空快捷键按钮
        def clear_hotkey():
            hotkey_var.set("")
            keyboard.unhook_all()  # 清除当前的热键监听
        
        ttk.Button(
            hotkey_frame,
            text="清空",
            command=clear_hotkey,
            bootstyle="danger",
            width=8
        ).pack(side=RIGHT, padx=5)
        
        def start_hotkey_recording():
            self.record_hotkey(hotkey_var, hotkey_btn)
            
        hotkey_btn = ttk.Button(
            hotkey_frame,
            text="设置快捷键",
            command=start_hotkey_recording,
            width=15
        )
        hotkey_btn.pack(side=RIGHT)
        
        def save_changes():
            group.hotkey = hotkey_var.get()
            group.dock_enabled = dock_var.get()
            # 保存项目选择
            choice = project_var.get()
            if choice == "项目1":
                group.project_type = "project1"
            elif choice == "项目2":
                group.project_type = "project2"
            else:
                group.project_type = "none"
            self.app.config.save()
            self.update_groups_display()
            self.app.start_hotkey_listener()
            dialog.destroy()
            
        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        # 保存按钮
        ttk.Button(
            btn_frame,
            text="保存更改",
            command=save_changes,
            style="blue.TButton",
            width=20
        ).pack(side=LEFT, padx=5)
        
        # 删除按钮（垃圾桶样式）
        ttk.Button(
            btn_frame,
            text="🗑",  # 使用垃圾桶 Unicode 字符
            command=lambda: self.delete_group_from_dialog(group.name, dialog),
            bootstyle="danger",
            width=3
        ).pack(side=LEFT, padx=5)

        # 设置对话框为模态并居中显示
        dialog.transient(self.app.root)
        dialog.grab_set()
        self.center_window(dialog)

    def delete_group_from_dialog(self, name, dialog):
        if messagebox.askyesno("确认", f"确定要删除组 '{name}' 吗？"):
            del self.app.config.groups[name]
            self.app.config.save()
            self.update_groups_display()
            dialog.destroy()

    def create_apps_tab(self, notebook, group):
        frame = ttk.Frame(notebook, padding=10)
        
        # 应用列表
        listbox = tk.Listbox(frame, height=10)
        listbox.pack(fill=BOTH, expand=YES, pady=5)
        
        for app in group.apps:
            listbox.insert(tk.END, app)
        
        # 启用拖放功能
        windnd.hook_dropfiles(listbox, func=lambda files: self.handle_apps_drop(files, group, listbox))
        
        # 添加双击打开功能
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                app_path = group.apps[index]
                try:
                    if os.path.exists(app_path):
                        subprocess.Popen(app_path, shell=True)
                    else:
                        self.app.message_display.show_error(f"找不到程序: {app_path}")
                except Exception as e:
                    self.app.message_display.show_error(f"启动程序失败: {str(e)}")
        
        listbox.bind('<Double-Button-1>', on_double_click)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=X, pady=5)
        
        def add_app():
            file_path = filedialog.askopenfilename(
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if file_path and file_path not in group.apps:
                group.apps.append(file_path)
                app_list.insert(tk.END, file_path)
                
        def remove_selected():
            selection = app_list.curselection()
            if selection:
                for index in reversed(selection):
                    del group.apps[index]
                    app_list.delete(index)
                    
        ttk.Button(
            btn_frame,
            text="添加程序",
            command=add_app,
            width=15
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="删除选中",
            command=remove_selected,
            width=15
        ).pack(side=LEFT, padx=5)
        
        return frame

    def handle_apps_drop(self, files, group, listbox):
        try:
            for file in files:
                # 将 bytes 转换为字符串
                file_path = file.decode('gbk')
                
                # 获取文件扩展名
                ext = os.path.splitext(file_path)[1].lower()
                
                # 处理快捷方式
                if ext == '.lnk':
                    target_path = self.resolve_shortcut(file_path)
                    if target_path:  # 如果成功解析到 exe 路径
                        if target_path not in group.apps:
                            group.apps.append(target_path)
                            listbox.insert(tk.END, target_path)
                # 只接受 exe 文件
                elif ext == '.exe':
                    if file_path not in group.apps:
                        group.apps.append(file_path)
                        listbox.insert(tk.END, file_path)
                    
        except Exception as e:
            pass  # 静默处理错误

    def create_websites_tab(self, notebook, group):
        frame = ttk.Frame(notebook, padding=10)
        
        # 网站列表
        listbox = tk.Listbox(frame, height=10)
        listbox.pack(fill=BOTH, expand=YES, pady=5)
        
        for site in group.websites:
            listbox.insert(tk.END, site)
        
        # 启用拖放功能
        windnd.hook_dropfiles(listbox, func=lambda files: self.handle_websites_drop(files, group, listbox))
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=X, pady=5)
        
        website_entry = ttk.Entry(input_frame)
        website_entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        
        def add_website():
            url = website_entry.get()
            if url and url not in group.websites:
                group.websites.append(url)
                listbox.insert(tk.END, url)
                website_entry.delete(0, tk.END)
        
        def remove_selected():
            selection = listbox.curselection()
            if selection:
                for index in reversed(selection):
                    del group.websites[index]
                    listbox.delete(index)
                    
        ttk.Button(
            input_frame,
            text="添加",
            command=add_website,
            width=8
        ).pack(side=LEFT)
        
        ttk.Button(
            input_frame,
            text="删除选中",
            command=remove_selected,
            width=15
        ).pack(side=LEFT, padx=5)
        
        return frame

    def handle_websites_drop(self, files, group, listbox):
        try:
            for file in files:
                # 将 bytes 转换为字符串
                file_path = file.decode('gbk')
                
                # 尝试读取文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 简单的 URL 检测
                    if 'http://' in content or 'https://' in content:
                        # 提取第一个 URL
                        import re
                        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', content)
                        
                        if urls:
                            url = urls[0]
                            # 确保 URL 以 http:// 或 https:// 开头
                            if not url.startswith(('http://', 'https://')):
                                url = 'http://' + url
                                
                            if url not in group.websites:
                                group.websites.append(url)
                                listbox.insert(tk.END, url)
                                
                except Exception:
                    pass  # 忽略无法读取的文件
                    
        except Exception as e:
            pass  # 静默处理错误

    def create_files_tab(self, notebook, group):
        frame = ttk.Frame(notebook, padding=10)
        
        # 文件列表
        listbox = tk.Listbox(frame, height=10)
        listbox.pack(fill=BOTH, expand=YES, pady=5)
        
        for file in group.files:
            listbox.insert(tk.END, os.path.basename(file))
        
        # 启用拖放功能
        windnd.hook_dropfiles(listbox, func=lambda files: self.handle_files_drop(files, group, listbox))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=X, pady=5)
        
        def add_files():
            file_paths = filedialog.askopenfilenames()
            for path in file_paths:
                if path not in group.files:
                    group.files.append(path)
                    listbox.insert(tk.END, os.path.basename(path))
                    
        def add_folder():
            folder_path = filedialog.askdirectory()
            if folder_path and folder_path not in group.files:
                group.files.append(folder_path)
                listbox.insert(tk.END, os.path.basename(folder_path))
                
        def remove_selected():
            selection = listbox.curselection()
            if selection:
                for index in reversed(selection):
                    del group.files[index]
                    listbox.delete(index)
                    
        def open_file_location():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                file_path = group.files[index]
                if os.path.exists(file_path):
                    # 如果是文件，打开其所在文件夹
                    if os.path.isfile(file_path):
                        subprocess.run(['explorer', '/select,', file_path])
                    # 如果是文件夹，直接打开
                    else:
                        os.startfile(file_path)
                
        # 添加文件按钮
        ttk.Button(
            btn_frame,
            text="添加文件",
            command=add_files,
            width=15
        ).pack(side=LEFT, padx=5)
        
        # 添加文件夹按钮
        ttk.Button(
            btn_frame,
            text="添加文件夹",
            command=add_folder,
            width=15
        ).pack(side=LEFT, padx=5)
        
        # 删除按钮
        ttk.Button(
            btn_frame,
            text="删除选中",
            command=remove_selected,
            width=15
        ).pack(side=LEFT, padx=5)
        
        # 打开所在位置按钮
        ttk.Button(
            btn_frame,
            text="打开所在位置",
            command=open_file_location,
            width=15
        ).pack(side=LEFT, padx=5)
        
        # 添加双击打开功能
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                file_path = group.files[index]
                if os.path.exists(file_path):
                    try:
                        os.startfile(file_path)
                    except Exception as e:
                        messagebox.showerror("错误", f"无法打开文件: {str(e)}")
        
        listbox.bind('<Double-Button-1>', on_double_click)
        
        return frame

    def handle_files_drop(self, files, group, listbox):
        try:
            for file in files:
                # 将 bytes 转换为字符串
                file_path = file.decode('gbk')
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    continue
                
                # 检查是否已存在
                if file_path not in group.files:
                    group.files.append(file_path)
                    listbox.insert(tk.END, os.path.basename(file_path))
                    
        except Exception as e:
            pass  # 静默处理错误

    def record_hotkey(self, hotkey_var, hotkey_btn):
        self.hotkey_recording = True
        self.pressed_keys.clear()
        hotkey_btn.configure(text="请按下快捷键组合...")
        
        def on_press(e):
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
            if key not in self.pressed_keys:
                self.pressed_keys.add(key)
                
                modifiers = {'CTRL', 'ALT', 'SHIFT'}
                sorted_keys = []
                
                for mod in ['CTRL', 'ALT', 'SHIFT']:
                    if mod in self.pressed_keys:
                        sorted_keys.append(mod)
                        
                other_keys = sorted(k for k in self.pressed_keys if k not in modifiers)
                sorted_keys.extend(other_keys)
                
                hotkey = '+'.join(sorted_keys)
                hotkey_var.set(hotkey)
                
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
                
            if not self.pressed_keys:
                self.hotkey_recording = False
                keyboard.unhook_all()
                hotkey_btn.configure(text="设置快捷键")
                
        keyboard.on_press(on_press)
        keyboard.on_release(on_release)

    def launch_group(self, group):
        """启动应用组"""
        try:
            # 处理项目创建
            if group.project_type == "project1":
                self.show_project_dialog(1)
            elif group.project_type == "project2":
                self.show_project_dialog(2)
            
            # 如果设置了启动时开启 Dock
            if group.dock_enabled and self.app.dock_manager:
                # 设置 Dock 开关状态并启动
                self.app.dock_manager.dock_enabled.set(True)
                self.app.dock_manager.toggle_dock()
            elif not group.dock_enabled and self.app.dock_manager.dock_enabled.get():
                # 如果组设置不启动 Dock，但 Dock 当前是开启状态，则关闭它
                self.app.dock_manager.dock_enabled.set(False)
                self.app.dock_manager.toggle_dock()
            elif not group.dock_enabled and not self.app.dock_manager.dock_enabled.get():
                # 如果组设置不启动 Dock，且 Dock 当前也是关闭状态，只刷新任务栏
                try:
                    # 重启 explorer.exe 来刷新任务栏
                    subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'])
                    subprocess.Popen('explorer.exe')
                    
                    # 等待一下确保 explorer 重启完成
                    self.app.root.after(1000)
                except Exception as e:
                    print(f"刷新任务栏失败: {str(e)}")

            # 启动应用程序
            for app_path in group.apps:
                try:
                    if not os.path.exists(app_path):
                        self.app.message_display.show_error(f"找不到应用: {app_path}")
                        continue
                    subprocess.Popen(app_path)
                except Exception as e:
                    self.app.message_display.show_error(f"启动应用失败: {app_path}\n{str(e)}")
            
            # 打开网站
            for url in group.websites:
                try:
                    webbrowser.open(url)
                except Exception as e:
                    self.app.message_display.show_error(f"打开网站失败: {url}\n{str(e)}")
            
            # 打开文件或文件夹
            for file_path in group.files:
                try:
                    if os.path.exists(file_path):
                        os.startfile(file_path)
                    else:
                        self.app.message_display.show_error(f"找不到文件: {file_path}")
                except Exception as e:
                    self.app.message_display.show_error(f"打开文件失败: {file_path}\n{str(e)}")
                
        except Exception as e:
            self.app.message_display.show_error(f"启动组失败: {str(e)}")

    def start_group(self, group_id):
        """启动指定的应用组"""
        if group_id in self.app.config.groups:
            group = self.app.config.groups[group_id]
            self.launch_group(group)
        else:
            self.app.message_display.show_error(f"找不到应用组: {group_id}")

    def kill_group(self, group_id):
        """结束指定的应用组"""
        if group_id in self.app.config.groups:
            group = self.app.config.groups[group_id]
            for app_path in group.apps:  # 这里也是一样
                try:
                    # 获取应用名称
                    app_name = os.path.basename(app_path)  # 直接使用 app_path
                    # 结束进程
                    subprocess.run(['taskkill', '/F', '/IM', app_name], capture_output=True)
                except Exception as e:
                    self.app.message_display.show_error(f"结束应用失败: {app_path}\n{str(e)}")
        else:
            self.app.message_display.show_error(f"找不到应用组: {group_id}")

    def update_groups_display(self):
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
            
        for group in self.app.config.groups.values():
            self.create_group_widget(group)

    def create_group_widget(self, group):
        group_frame = ttk.Frame(self.groups_frame)
        group_frame.pack(fill=X, pady=5, padx=5)
        
        info_frame = ttk.Frame(group_frame)
        info_frame.pack(fill=X, expand=True)
        
        ttk.Label(
            info_frame,
            text=f"{group.name}",
            font=("Helvetica", 12, "bold")
        ).pack(side=LEFT)
        
        if group.hotkey:
            ttk.Label(
                info_frame,
                text=f" ({group.hotkey})",
                font=("Helvetica", 11)
            ).pack(side=LEFT)
        
        btn_frame = ttk.Frame(group_frame)
        btn_frame.pack(fill=X, pady=5)
        
        ttk.Button(
            btn_frame,
            text="启动",
            command=lambda: self.launch_group(group),
            style="blue.TButton",
            width=15
        ).pack(side=LEFT, padx=2)
        
        ttk.Button(
            btn_frame,
            text="⚙",
            command=lambda: self.edit_group_dialog(group),
            bootstyle="secondary",
            width=3
        ).pack(side=LEFT, padx=2)
        
        # 启用/停用开关
        enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            btn_frame,
            variable=enabled_var,
            command=lambda: self.toggle_group(group, enabled_var),
            bootstyle="round-toggle"
        ).pack(side=LEFT, padx=2)

    def toggle_group(self, group, enabled_var):
        if enabled_var.get():
            print(f"启用组: {group.name}")
            # 这里添加启用组的逻辑
        else:
            print(f"停用组: {group.name}")
            # 这里添加停用组的逻辑
        
    def center_window(self, window):
        # 更新窗口大小信息
        window.update_idletasks()
        
        # 获取主窗口位置和大小
        main_x = self.app.root.winfo_x()
        main_y = self.app.root.winfo_y()
        main_width = self.app.root.winfo_width()
        main_height = self.app.root.winfo_height()
        
        # 获取对话框大小
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        
        # 计算居中位置
        x = main_x + (main_width - window_width) // 2
        y = main_y + (main_height - window_height) // 2
        
        # 设置窗口位置
        window.geometry(f"+{x}+{y}")
        
    def add_app_to_group(self, group, path):
        try:
            # 检查文件是否存在
            if not os.path.exists(path):
                return
            
            # 获取文件扩展名
            ext = os.path.splitext(path)[1].lower()
            
            # 处理快捷方式
            if ext == '.lnk':
                target_path = self.resolve_shortcut(path)
                if target_path:  # 如果成功解析到 exe 路径
                    path = target_path
                else:
                    return
            # 只接受 exe 文件
            elif ext != '.exe':
                return
            
            # 检查是否已存在
            if path not in group.apps:
                group.apps.append(path)
                self.app.config.save()
                # 更新显示
                self.update_groups_display()
                
        except Exception as e:
            pass  # 静默处理错误

    def handle_drop(self, files, group):
        try:
            for file in files:
                # 将 bytes 转换为字符串
                file_path = file.decode('gbk')
                # 添加到指定组
                self.add_app_to_group(group, file_path)
        except Exception as e:
            self.app.message_display.show_error(f"处理拖放文件失败: {str(e)}")
        
    def resolve_shortcut(self, shortcut_path):
        """解析快捷方式，返回目标路径"""
        try:
            pythoncom.CoInitialize()  # 初始化COM
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            target_path = shortcut.Targetpath
            pythoncom.CoUninitialize()  # 释放COM
            
            # 检查目标是否为 exe
            if target_path and os.path.exists(target_path):
                if os.path.splitext(target_path)[1].lower() == '.exe':
                    return target_path
            return None
        except:
            return None
        
    def show_project_dialog(self, project_type):
        """显示项目创建对话框"""
        dialog = ttk.Toplevel(self.app.root)
        dialog.title("创建项目")
        dialog.geometry("400x150")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)
        
        ttk.Label(frame, text="项目名称：").pack(anchor=W)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.pack(fill=X, pady=(0, 10))
        
        def create():
            name = name_entry.get()
            if not name:
                self.app.message_display.show_message("警告", "请输入项目名称")
                return
            
            path = self.app.config.project_paths[f'project{project_type}']
            self.create_project(name, path)
            dialog.destroy()
        
        # 添加回车确认功能
        name_entry.bind('<Return>', lambda e: create())
        
        ttk.Button(
            frame,
            text="创建",
            command=create,
            style="blue.TButton",
            width=20
        ).pack(pady=10)
        
        # 设置对话框为模态并居中显示
        dialog.transient(self.app.root)
        dialog.grab_set()
        self.center_window(dialog)
        
        # 聚焦到输入框
        name_entry.focus()
        
    def create_project(self, name, path):
        """创建项目"""
        try:
            from datetime import datetime
            today = datetime.now().strftime("%Y_%m_%d")
            project_path = os.path.join(path, f"{today} {name}")
            
            # 创建项目目录结构
            folders = ['导出', '工程文件', '素材', '原始素材']
            
            # 创建主项目目录
            os.makedirs(project_path, exist_ok=True)
            
            # 创建子文件夹
            for folder in folders:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
            
            # 打开项目目录
            os.startfile(project_path)
            
        except Exception as e:
            self.app.message_display.show_error(f"创建项目失败: {str(e)}")

    def get_project_choice(self, group):
        """获取项目选择的显示文本"""
        if group.project_type == "project1":
            return "项目1"
        elif group.project_type == "project2":
            return "项目2"
        return "不创建"
        