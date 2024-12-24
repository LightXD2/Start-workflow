import os
import sys
import winreg

class AutoStartManager:
    def __init__(self):
        self.reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        self.app_name = "WorkHelper"
        
    def enable_autostart(self):
        """启用系统级开机自启"""
        try:
            # 获取程序路径
            exe_path = sys.executable
            
            # 打开注册表项
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,  # 改为 HKEY_LOCAL_MACHINE 实现系统级自启
                self.reg_path,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
            )
            
            # 写入注册表
            winreg.SetValueEx(
                key,
                self.app_name,
                0,
                winreg.REG_SZ,
                f'"{exe_path}"'
            )
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"启用系统级开机自启动失败: {str(e)}")
            return False
            
    def disable_autostart(self):
        """禁用系统级开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,  # 改为 HKEY_LOCAL_MACHINE
                self.reg_path,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY
            )
            
            winreg.DeleteValue(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"禁用系统级开机自启动失败: {str(e)}")
            return False
            
    def is_autostart_enabled(self):
        """检查是否已启用系统级开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,  # 改为 HKEY_LOCAL_MACHINE
                self.reg_path,
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            )
            
            winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except:
            return False