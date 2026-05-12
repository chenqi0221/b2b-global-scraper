"""测试导入"""
import sys
print("Python 版本:", sys.version, flush=True)

try:
    import ttkbootstrap as tb
    print("ttkbootstrap 导入成功", flush=True)
    
    from gui.app import ScraperApp
    print("ScraperApp 导入成功", flush=True)
    
    root = tb.Window(themename='superhero')
    print("窗口创建成功", flush=True)
    app = ScraperApp(root)
    print("应用初始化成功", flush=True)
    root.destroy()
    print("测试通过！", flush=True)
except Exception as e:
    print(f"错误: {e}", flush=True)
    import traceback
    traceback.print_exc()
