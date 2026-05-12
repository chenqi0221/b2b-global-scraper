"""新的入口文件"""

import ttkbootstrap as tb
from gui.app import ScraperApp


def main():
    """主函数"""
    root = tb.Window(themename="superhero")
    app = ScraperApp(root)
    app.run()


if __name__ == "__main__":
    main()
