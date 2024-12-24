import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import keyboard
import os
from datetime import datetime

class ProjectCreator(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.project_frames = []
        self.create_widgets()
        
    def create_widgets(self):
        # 创建一个可滚动的框架
        self.canvas = tk.Canvas(self, bg='#2E2E2E')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 创建固定的两个项目框架
        self.create_project_frame("项目 1")
        self.create_project_frame("项目 2")

    def create_project_frame(self, title):
        frame = ttk.LabelFrame(self.scrollable_frame, text=title)
        frame.pack(fill="x", padx=5, pady=5)

        # 项目名称
        name_frame = ttk.Frame(frame)
        name_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(name_frame, text="项目名称:").pack(side="left")
        name_entry = ttk.Entry(name_frame)
        name_entry.pack(side="left", fill="x", expand=True, padx=5)

        # 项目路径
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(path_frame, text="项目路径:").pack(side="left")
        path_entry = ttk.Entry(path_frame)
        path_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # 设置默认路径
        project_key = 'project1' if title == "项目 1" else 'project2'
        default_path = self.app.config.project_paths.get(project_key, 'E:/2024')
        path_entry.insert(0, default_path)
        
        def browse_path():
            path = filedialog.askdirectory()
            if path:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, path)
                # 保存新路径到配置
                self.app.config.project_paths[project_key] = path
                self.app.config.save()
        
        ttk.Button(
            path_frame,
            text="浏览",
            command=browse_path,
            bootstyle="secondary",
            width=8
        ).pack(side="right", padx=5)

        # 创建项目按钮
        ttk.Button(
            frame,
            text="创建项目",
            style="blue.TButton",
            command=lambda: self.create_project(name_entry.get(), path_entry.get())
        ).pack(pady=5)

    def browse_path(self, entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def create_project(self, name, path):
        try:
            if not name:
                self.app.message_display.show_message("警告", "请输入项目名称")
                return
            
            if not path:
                self.app.message_display.show_message("警告", "请选择项目路径")
                return
            
            if not os.path.exists(path):
                self.app.message_display.show_message("警告", "项目路径不存在")
                return
            
            # 获取当前日期并格式化
            today = datetime.now().strftime("%Y_%m_%d")
            
            # 创建新项目目录
            project_name = f"{today} {name}"
            project_path = os.path.join(path, project_name)
            
            # 创建项目目录结构
            folders = ['导出', '工程文件', '素材', '原始素材']
            try:
                # 创建主项目目录
                os.makedirs(project_path, exist_ok=True)
                
                # 创建子文件夹
                for folder in folders:
                    folder_path = os.path.join(project_path, folder)
                    os.makedirs(folder_path, exist_ok=True)
                    
            except Exception as e:
                self.app.message_display.show_error(f"创建项目目录失败: {str(e)}")
                return
            
            # 保存项目配置
            self.app.config.projects[project_name] = {
                'path': project_path
            }
            self.app.config.save()
            
            # 打开项目目录
            try:
                os.startfile(project_path)
            except Exception as e:
                self.app.message_display.show_error(f"打开项目目录失败: {str(e)}")
            
        except Exception as e:
            self.app.message_display.show_error(f"创建项目失败: {str(e)}")