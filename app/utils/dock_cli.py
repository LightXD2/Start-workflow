import subprocess
import os
import win32gui
import win32con
import wmi

def detect_dock_path():
    """检测运行中的 Dock 程序路径"""
    try:
        # 先检查 Dock_64.exe
        process = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq Dock_64.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True
        )
        if 'Dock_64.exe' in process.stdout:
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
            c = wmi.WMI()
            for process in c.Win32_Process(name="dock.exe"):
                path = process.ExecutablePath
                if path and os.path.exists(path):
                    return path
        
        return None
    except Exception as e:
        print(f"检测失败: {str(e)}")
        return None

def main():
    # 检测 Dock 路径
    dock_path = detect_dock_path()
    if dock_path:
        print(f"找到 Dock 路径: {dock_path}")
    else:
        print("未找到运行中的 Dock 程序")

if __name__ == "__main__":
    main() 