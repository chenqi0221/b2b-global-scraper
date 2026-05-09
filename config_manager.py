import json
import os

CONFIG_FILE = "app_config.json"

def load_config():
    """加载应用程序配置，包括窗口大小和位置"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    """保存应用程序配置"""
    try:
        current_config = load_config()
        current_config.update(config)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current_config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False
