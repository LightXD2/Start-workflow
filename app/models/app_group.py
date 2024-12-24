class AppGroup:
    def __init__(self, name="", apps=None, websites=None, files=None, hotkey="", dock_enabled=False):
        self.name = name
        self.apps = apps or []
        self.websites = websites or []
        self.files = files or []
        self.hotkey = hotkey
        self.dock_enabled = dock_enabled
        self.project_type = "none"  # 可选值: "none", "project1", "project2"

    def to_dict(self):
        """转换为可序列化的字典"""
        return {
            'name': self.name,
            'apps': self.apps,
            'websites': self.websites,
            'files': self.files,
            'hotkey': self.hotkey,
            'dock_enabled': self.dock_enabled,
            'project_type': self.project_type
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        group = cls(
            name=data.get('name', ''),
            apps=data.get('apps', []),
            websites=data.get('websites', []),
            files=data.get('files', []),
            hotkey=data.get('hotkey', ''),
            dock_enabled=data.get('dock_enabled', False)
        )
        group.project_type = data.get('project_type', 'none')
        return group 