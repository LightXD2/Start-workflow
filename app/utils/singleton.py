import win32event
import win32api
import winerror
import sys

class SingletonManager:
    _instance = None
    _mutex = None
    
    def __init__(self):
        if not SingletonManager._mutex:
            try:
                # 创建一个全局互斥体并保持引用
                SingletonManager._mutex = win32event.CreateMutex(None, True, "WorkHelper_Mutex_19890604")
                if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                    win32api.MessageBox(0, "程序已经在运行中", "提示", 0x30)
                    sys.exit(0)
            except Exception as e:
                print(f"互斥体创建失败: {str(e)}")
                sys.exit(1)
    
    def __del__(self):
        if SingletonManager._mutex:
            try:
                win32event.ReleaseMutex(SingletonManager._mutex)
            except:
                pass 