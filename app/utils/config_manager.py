import os
import json
import appdirs
from app.models.app_group import AppGroup

class ConfigManager:
    def __init__(self):
        # 获取用户配置目录
        self.config_dir = appdirs.user_config_dir("WorkHelper")
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.groups = {}
        self.dock_settings = {
            'dock_path': '',
            'proxy_enabled': False  # 添加代理状态配置
        }
        self.project_paths = {
            'project1': 'E:/2024',
            'project2': 'E:/2024'
        }
        
        # 加载配置
        self.load()
    
    def load(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 将字典转换为 AppGroup 对象
                    self.groups = {
                        name: AppGroup.from_dict(group_data) 
                        for name, group_data in data.get('groups', {}).items()
                    }
                    self.dock_settings = data.get('dock_settings', {})
                    # 加载项目路径配置
                    self.project_paths = data.get('project_paths', {
                        'project1': 'E:/2024',
                        'project2': 'E:/2024'
                    })
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
    
    def save(self):
        """保存配置文件"""
        try:
            # 将 AppGroup 对象转换为可序列化的字典
            groups_dict = {
                name: group.to_dict() 
                for name, group in self.groups.items()
            }
            
            data = {
                'groups': groups_dict,
                'dock_settings': self.dock_settings,
                'project_paths': self.project_paths
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {str(e)}") 