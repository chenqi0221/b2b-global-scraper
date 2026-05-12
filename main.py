"""新的入口文件"""

import ttkbootstrap as tb
from gui.app import ScraperApp
from gui.effects.glassmorphism import apply_mica_to_window, apply_rounded_corners
from gui.effects.style_config import setup_global_styles


def main():
    """主函数"""
    root = tb.Window(themename="superhero")

    # 设置全局样式
    setup_global_styles(root)

    app = ScraperApp(root)

    # 应用 Windows 11 毛玻璃效果 (Mica) 或 Windows 10 (Acrylic)
    # 需要在窗口显示后应用才能生效
    def _apply_effects():
        # 先尝试 Mica (Win11)，失败则尝试 Acrylic (Win10)
        if not apply_mica_to_window(root, dark_mode=True):
            print("尝试应用 Acrylic 效果...")
            from gui.effects.glassmorphism import apply_acrylic_to_window
            apply_acrylic_to_window(root, dark_mode=True)
        apply_rounded_corners(root, radius=12)

    root.after(500, _apply_effects)

    app.run()


if __name__ == "__main__":
    main()
