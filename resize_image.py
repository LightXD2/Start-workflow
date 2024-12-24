from PIL import Image
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ImageResizerApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("图片尺寸调整工具 (800x800)")
        self.window.geometry("600x400")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.window, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选择路径的框架
        path_frame = ttk.LabelFrame(self.main_frame, text="选择路径", padding="10")
        path_frame.pack(fill=tk.X, pady=10)
        
        # 路径显示和选择按钮
        self.path_var = tk.StringVar(value="未选择任何文件或文件夹")
        path_label = ttk.Label(path_frame, textvariable=self.path_var, wraplength=500)
        path_label.pack(fill=tk.X, pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(path_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="选择文件", command=self.select_file, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="选择文件夹", command=self.select_folder, width=20).pack(side=tk.LEFT, padx=5)
        
        # 选项框架
        option_frame = ttk.Frame(self.main_frame)
        option_frame.pack(fill=tk.X, pady=10)
        
        # 添加智能裁切选项
        self.smart_crop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="智能裁切（保持图片比例）", 
                       variable=self.smart_crop_var).pack(side=tk.LEFT)
        
        # 处理按钮框架
        process_frame = ttk.Frame(self.main_frame)
        process_frame.pack(pady=10)
        
        # 添加两个处理按钮
        self.auto_btn = ttk.Button(process_frame, text="智能裁切", 
                                 command=self.auto_process_images, state='disabled', width=20)
        self.auto_btn.pack(side=tk.LEFT, padx=5)
        
        self.manual_btn = ttk.Button(process_frame, text="手动裁切", 
                                   command=self.manual_process_images, state='disabled', width=20)
        self.manual_btn.pack(side=tk.LEFT, padx=5)
        
        # 日志框架
        log_frame = ttk.LabelFrame(self.main_frame, text="处理日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.selected_path = None
        self.is_folder = False

    def smart_crop(self, img, target_size):
        # 保持原始比例的智能裁切
        width, height = img.size
        ratio = width / height
        
        if ratio > 1:  # 宽图
            new_width = int(target_size * ratio)
            new_height = target_size
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # 从中心裁切
            left = (new_width - target_size) // 2
            top = 0
            right = left + target_size
            bottom = target_size
        else:  # 高图
            new_width = target_size
            new_height = int(target_size / ratio)
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = 0
            top = (new_height - target_size) // 2
            right = target_size
            bottom = top + target_size
            
        return resized.crop((left, top, right, bottom))

    def manual_crop(self, img_path):
        # 创建裁切窗口
        crop_window = tk.Toplevel(self.window)
        crop_window.title("手动裁切")
        
        # 这里需要实现图片预览和裁切区域选择
        # 由于实现复杂，这里只是示例
        ttk.Label(crop_window, text="手动裁切功能开发中...").pack(pady=20)
        ttk.Button(crop_window, text="确定", command=crop_window.destroy).pack()

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.window.update()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.selected_path = file_path
            self.path_var.set(f"已选择文件：{file_path}")
            self.auto_btn.config(state='normal')
            self.manual_btn.config(state='normal')
            self.is_folder = False
            self.log("已选择单个文件")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="选择文件夹")
        if folder_path:
            self.selected_path = folder_path
            self.path_var.set(f"已选择文件夹：{folder_path}")
            self.auto_btn.config(state='normal')
            self.manual_btn.config(state='normal')
            self.is_folder = True
            self.log("已选择文件夹")

    def auto_process_images(self):
        if not self.selected_path:
            return
            
        try:
            if self.is_folder:
                output_folder = os.path.join(self.selected_path, "800x800")
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                    self.log(f"创建输出文件夹：{output_folder}")
                
                count = 0
                for filename in os.listdir(self.selected_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        input_path = os.path.join(self.selected_path, filename)
                        try:
                            img = Image.open(input_path)
                            if self.smart_crop_var.get():
                                resized_img = self.smart_crop(img, 800)
                            else:
                                resized_img = img.resize((800, 800), Image.Resampling.LANCZOS)
                            output_path = os.path.join(output_folder, filename)
                            resized_img.save(output_path)
                            count += 1
                            self.log(f"成功处理：{filename}")
                        except Exception as e:
                            self.log(f"处理失败：{filename} - {str(e)}")
                
                if count > 0:
                    self.log(f"\n处理完成！共处理 {count} 张图片")
                else:
                    self.log("\n未找到可处理的图片文件")
            
            else:
                folder_path = os.path.dirname(self.selected_path)
                output_folder = os.path.join(folder_path, "800x800")
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                    self.log(f"创建输出文件夹：{output_folder}")
                
                img = Image.open(self.selected_path)
                if self.smart_crop_var.get():
                    resized_img = self.smart_crop(img, 800)
                else:
                    resized_img = img.resize((800, 800), Image.Resampling.LANCZOS)
                filename = os.path.basename(self.selected_path)
                output_path = os.path.join(output_folder, filename)
                resized_img.save(output_path)
                self.log(f"成功处理：{filename}")
                self.log("\n处理完成！")
        
        except Exception as e:
            self.log(f"\n发生错误：{str(e)}")

    def manual_process_images(self):
        if not self.selected_path:
            return
            
        if self.is_folder:
            for filename in os.listdir(self.selected_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    input_path = os.path.join(self.selected_path, filename)
                    self.manual_crop(input_path)
        else:
            self.manual_crop(self.selected_path)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ImageResizerApp()
    app.run()