import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
import os
from datetime import datetime

class ProjectManager:
    def __init__(self, app):
        self.app = app
        self.project_name = None
        self.project_path = None

    def create_project_panel(self, parent):
        right_frame = ttk.LabelFrame(parent, text="项目创建", padding=10)
        
        # 项目名称输入框架
        name_frame = ttk.Frame(right_frame)
        name_frame.pack(fill=X, pady=5)
        
        ttk.Label(
            name_frame,
            text="项目名称：",
            font=("Helvetica", 10)
        ).pack(side=LEFT)
        
        self.project_name = ttk.Entry(name_frame)
        self.project_name.pack(side=LEFT, fill=X, expand=YES)
        
        # 项目路径选择框架
        path_frame = ttk.Frame(right_frame)
        path_frame.pack(fill=X, pady=5)
        
        ttk.Label(
            path_frame,
            text="项目路径：",
            font=("Helvetica", 10)
        ).pack(side=LEFT)
        
        self.project_path = ttk.Entry(path_frame)
        self.project_path.pack(side=LEFT, fill=X, expand=YES)
        self.project_path.insert(0, r"E:\2024")  # 默认路径
        
        ttk.Button(
            path_frame,
            text="浏览",
            command=self.browse_path,
            bootstyle="secondary-outline",
            width=8
        ).pack(side=LEFT, padx=5)
        
        # 创建项目按钮
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="创建项目",
            command=self.create_project,
            style="blue.TButton",
            width=20
        ).pack(side=LEFT)
        
        parent.add(right_frame, weight=1)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.project_path.delete(0, tk.END)
            self.project_path.insert(0, path)

    def create_project(self):
        project_name = self.project_name.get()
        if not project_name:
            self.app.message_display.show_message("警告", "请输入项目名称")
            return
            
        today = datetime.now().strftime("%Y_%m_%d")
        base_path = self.project_path.get()
        project_path = os.path.join(base_path, f"{today} {project_name}")
        subfolders = ["素材", "原始素材", "工程文件", "导出"]
        
        try:
            os.makedirs(project_path, exist_ok=True)
            for folder in subfolders:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                
            self.app.message_display.show_message(
                "成功", 
                f"项目文件夹创建成功：\n{project_path}"
            )
            os.startfile(project_path)
            
        except Exception as e:
            self.app.message_display.show_message(
                "错误",
                f"创建文件夹时出错：{str(e)}"
            )