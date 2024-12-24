import tkinter as tk
import ttkbootstrap as ttk
from app.work_helper import WorkHelperApp
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    root = ttk.Window()
    style = ttk.Style(theme="darkly")
    
    # 配置全局字体
    default_font = ("Microsoft YaHei UI", 10)
    style.configure(".", font=default_font)
    
    # 配置不同组件的字体
    style.configure("TLabel", font=default_font)
    style.configure("TButton", font=default_font)
    style.configure("TEntry", font=default_font)
    style.configure("Treeview", font=default_font)
    style.configure("TCheckbutton", font=default_font)
    
    # 标题和强调文字使用大一号字体
    title_font = ("Microsoft YaHei UI", 12, "bold")
    style.configure("Title.TLabel", font=title_font)
    
    # 自定义蓝色按钮样式
    style.configure(
        "blue.TButton",
        font=default_font,
        background="#00a4ff",
        foreground="white"
    )
    
    # 按钮悬停效果
    style.map(
        "blue.TButton",
        background=[("active", "#0093e6")],
        foreground=[("active", "white")]
    )
    
    app = WorkHelperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 