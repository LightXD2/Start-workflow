import tkinter as tk
from tkinter import messagebox

class MessageDisplay:
    def __init__(self, parent):
        self.parent = parent
        
    def show_message(self, title, message):
        messagebox.showinfo(title, message)
        
    def show_error(self, message):
        messagebox.showerror("错误", message)
        
    def show_warning(self, message):
        messagebox.showwarning("警告", message)