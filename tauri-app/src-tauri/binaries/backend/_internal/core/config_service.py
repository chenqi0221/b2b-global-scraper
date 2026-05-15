"""配置服务"""

import os
from typing import Dict, Optional


class ConfigService:
    """配置服务，负责读写 .env 文件"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
    
    def load_config(self) -> Dict[str, str]:
        """加载配置"""
        config = {}
        if os.path.exists(self.env_file):
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")
        return config
    
    def save_config(self, config: Dict[str, str]):
        """保存配置"""
        # 读取现有配置
        existing = self.load_config()
        
        # 更新配置
        existing.update(config)
        
        # 写入文件
        with open(self.env_file, "w", encoding="utf-8") as f:
            for key, value in existing.items():
                f.write(f'{key}="{value}"\n')
    
    def get(self, key: str, default: str = "") -> str:
        """获取配置项"""
        config = self.load_config()
        return config.get(key, default)
