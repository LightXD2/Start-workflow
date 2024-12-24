import sys
import os

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app.utils.singleton import SingletonManager
from main import main

if __name__ == "__main__":
    # 创建单例管理器会自动检查和处理多开情况
    singleton = SingletonManager()
    main() 