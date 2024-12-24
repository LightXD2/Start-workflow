import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
from app.utils.resource_utils import resource_path  # 改用新的导入

class LoadingWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)  # 无边框窗口
        
        try:
            # 使用正确的资源路径加载图片
            image_path = resource_path(os.path.join("app", "assets", "LIGHTL加载.png"))
            image = Image.open(image_path)
            
            # 获取原始尺寸并缩小到三分之一
            original_width, original_height = image.size
            new_width = original_width // 3
            new_height = original_height // 3
            
            # 调整大小，保持透明通道
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # 创建标签显示图片
            label = tk.Label(self.window, image=photo)
            label.image = photo  # 保持引用
            label.pack()
            
            # 设置窗口大小为调整后的图片大小
            self.window.geometry(f"{new_width}x{new_height}")
            
        except Exception as e:
            print(f"加载图片失败: {e}")
            # 如果加载图片失败，显示简单的文本
            tk.Label(self.window, text="加载中...", padx=20, pady=10).pack()
            self.window.geometry("100x50")
        
        # 居中显示
        self.center_window()
        
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def show(self):
        self.window.deiconify()
        self.window.update()
        
    def destroy(self):
        self.window.destroy() 