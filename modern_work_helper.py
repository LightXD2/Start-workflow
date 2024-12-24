import os
import json
from datetime import datetime
import webbrowser
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from pynput import keyboard
import threading
from CTkMessagebox import CTkMessagebox

class AppGroup:
    def __init__(self, name, apps=None, websites=None, files=None, hotkey=None):
        self.name = name
        self.apps = apps or []
        self.websites = websites or []
        self.files = files or []
        self.hotkey = hotkey

class ModernWorkHelper:
    def __init__(self):
        # 基础设置
        self.root = ctk.CTk()
        self.root.title("工作助手")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        # 配置
        self.groups = {}
        self.config_file = "app_groups.json"
        
        # 创建UI
        self.create_ui()
        self.load_config()
        self.start_hotkey_listener()

    def create_ui(self):
        # 创建主容器
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 左侧面板 - 应用组列表 (设置固定宽度)
        left_frame = ctk.CTkFrame(main_container, width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 5))
        left_frame.pack_propagate(False)  # 保持固定宽度

        # 标题
        ctk.CTkLabel(
            left_frame, 
            text="应用组", 
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # 组列表
        self.groups_frame = ctk.CTkScrollableFrame(left_frame)
        self.groups_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 添加组按钮
        ctk.CTkButton(
            left_frame,
            text="添加新组",
            command=self.add_group_dialog
        ).pack(pady=10, padx=10, fill="x")

        # 右侧面板 - 项目创建
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            right_frame,
            text="项目创建",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # 项目名称
        ctk.CTkLabel(right_frame, text="项目名称:").pack(anchor="w", padx=10)
        self.project_name = ctk.CTkEntry(right_frame)
        self.project_name.pack(fill="x", padx=10, pady=5)

        # 项目路径
        path_frame = ctk.CTkFrame(right_frame)
        path_frame.pack(fill="x", padx=10, pady=5)

        self.project_path = ctk.CTkEntry(path_frame)
        self.project_path.pack(side="left", expand=True, fill="x", padx=(0,5))
        self.project_path.insert(0, str(Path.home() / "Projects"))

        ctk.CTkButton(
            path_frame,
            text="浏览",
            width=60,
            command=self.browse_path
        ).pack(side="right")

        # 创建按钮
        ctk.CTkButton(
            right_frame,
            text="创建项目",
            command=self.create_project
        ).pack(pady=20)

    def add_group_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("添加应用组")
        dialog.geometry("500x600")
        dialog.grab_set()

        # 组名
        ctk.CTkLabel(dialog, text="组名:").pack(anchor="w", padx=10, pady=5)
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(fill="x", padx=10)

        # 应用列表
        apps_frame = ctk.CTkFrame(dialog)
        apps_frame.pack(fill="x", padx=10, pady=10)
        
        apps_list = []
        apps_listbox = tk.Listbox(apps_frame, bg="#2b2b2b", fg="white")
        apps_listbox.pack(fill="x", pady=5)

        def add_app():
            file = filedialog.askopenfilename(
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if file:
                apps_list.append(file)
                apps_listbox.insert("end", file)

        ctk.CTkButton(
            apps_frame,
            text="添加应用",
            command=add_app
        ).pack()

        # 网站列表
        web_frame = ctk.CTkFrame(dialog)
        web_frame.pack(fill="x", padx=10, pady=10)
        
        websites_list = []
        web_listbox = tk.Listbox(web_frame, bg="#2b2b2b", fg="white")
        web_listbox.pack(fill="x", pady=5)

        web_entry = ctk.CTkEntry(web_frame)
        web_entry.pack(side="left", expand=True, fill="x", padx=(0,5))

        def add_website():
            url = web_entry.get()
            if url:
                websites_list.append(url)
                web_listbox.insert("end", url)
                web_entry.delete(0, "end")

        ctk.CTkButton(
            web_frame,
            text="添加",
            width=60,
            command=add_website
        ).pack(side="right")

        # 快捷键
        hotkey_frame = ctk.CTkFrame(dialog)
        hotkey_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(hotkey_frame, text="快捷键:").pack(side="left")
        hotkey_var = tk.StringVar()
        hotkey_entry = ctk.CTkEntry(
            hotkey_frame,
            textvariable=hotkey_var,
            state="readonly"
        )
        hotkey_entry.pack(side="left", padx=5)

        def record_hotkey():
            hotkey_btn.configure(text="请按下快捷键...")
            self.recording_hotkey = True

            def on_key_combination(keys):
                if self.recording_hotkey:
                    hotkey_var.set("+".join(sorted(keys)))
                    hotkey_btn.configure(text="设置快捷键")
                    self.recording_hotkey = False

            self.start_hotkey_recorder(on_key_combination)

        hotkey_btn = ctk.CTkButton(
            hotkey_frame,
            text="设置快捷键",
            command=record_hotkey
        )
        hotkey_btn.pack(side="left", padx=5)

        # 保存按钮
        def save():
            name = name_entry.get()
            if not name:
                CTkMessagebox(title="警告", message="请输入组名")
                return

            self.groups[name] = AppGroup(
                name=name,
                apps=apps_list,
                websites=websites_list,
                hotkey=hotkey_var.get()
            )
            self.save_config()
            self.update_groups_display()
            dialog.destroy()

        ctk.CTkButton(
            dialog,
            text="保存",
            command=save
        ).pack(pady=20)

    def update_groups_display(self):
        # 清除现有显示
        for widget in self.groups_frame.winfo_children():
            widget.destroy()

        # 显示所有组
        for group in self.groups.values():
            group_frame = ctk.CTkFrame(self.groups_frame)
            group_frame.pack(fill="x", pady=2)

            # 组信息
            info = f"{group.name}"
            if group.hotkey:
                info += f" ({group.hotkey})"
            
            ctk.CTkLabel(
                group_frame,
                text=info
            ).pack(side="left", padx=5)

            # 按钮
            ctk.CTkButton(
                group_frame,
                text="启动",
                width=60,
                command=lambda g=group: self.launch_group(g)
            ).pack(side="right", padx=2)

            ctk.CTkButton(
                group_frame,
                text="删除",
                width=60,
                fg_color="#FF4444",
                command=lambda n=group.name: self.delete_group(n)
            ).pack(side="right", padx=2)

    def launch_group(self, group):
        # 启动应用
        for app in group.apps:
            try:
                subprocess.Popen(app)
            except Exception as e:
                CTkMessagebox(title="错误", message=f"启动失败: {app}\n{str(e)}")

        # 打开网站
        for site in group.websites:
            try:
                webbrowser.open(site)
            except Exception as e:
                CTkMessagebox(title="错误", message=f"无法打开: {site}\n{str(e)}")

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path.delete(0, "end")
            self.project_path.insert(0, path)

    def create_project(self):
        project_name = self.project_name.get()
        if not project_name:
            CTkMessagebox(title="警告", message="请输入项目名称")
            return

        today = datetime.now().strftime("%Y_%m_%d")
        base_path = self.project_path.get()
        project_path = os.path.join(base_path, f"{today}_{project_name}")
        
        try:
            folders = ["素材", "原始素材", "工程文件", "导出"]
            os.makedirs(project_path, exist_ok=True)
            for folder in folders:
                os.makedirs(os.path.join(project_path, folder), exist_ok=True)

            CTkMessagebox(
                title="成功",
                message=f"项目创建成功！\n路径：{project_path}",
                icon="check"
            )
            os.startfile(project_path)
            
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"创建项目失败：{str(e)}",
                icon="cancel"
            )

    def start_hotkey_recorder(self, callback):
        self.pressed_keys = set()
        
        def on_press(key):
            try:
                key_str = key.char
            except AttributeError:
                key_str = str(key).replace("Key.", "")
            self.pressed_keys.add(key_str)
            
        def on_release(key):
            if self.pressed_keys:
                callback(self.pressed_keys)
                self.pressed_keys = set()
                return False
                
        keyboard.Listener(on_press=on_press, on_release=on_release).start()

    def start_hotkey_listener(self):
        def check_hotkeys():
            with keyboard.GlobalHotKeys({
                group.hotkey: (lambda g=group: self.launch_group(g))
                for group in self.groups.values()
                if group.hotkey
            }) as h:
                h.join()
                
        threading.Thread(target=check_hotkeys, daemon=True).start()

    def delete_group(self, name):
        if name in self.groups:
            del self.groups[name]
            self.save_config()
            self.update_groups_display()

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.groups = {
                    name: AppGroup(**group_data)
                    for name, group_data in data.items()
                }
                self.update_groups_display()
        except FileNotFoundError:
            pass
        except Exception as e:
            CTkMessagebox(title="错误", message=f"加载配置失败：{str(e)}")

    def save_config(self):
        try:
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
        except Exception as e:
            CTkMessagebox(title="错误", message=f"保存配置失败：{str(e)}")

def main():
    app = ModernWorkHelper()
    app.root.mainloop()

if __name__ == "__main__":
    main() 