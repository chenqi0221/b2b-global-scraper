"""后端独立入口：供 PyInstaller 打包为 standalone exe，再由 Tauri 作为 sidecar 拉起。"""
import os
import sys

if getattr(sys, 'frozen', False):
    bundle_dir = os.path.dirname(sys.executable)
    os.chdir(bundle_dir)

if sys.stdout is None:
    log_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
    sys.stdout = open(os.path.join(log_dir, 'backend_stdout.log'), 'a', encoding='utf-8')
if sys.stderr is None:
    log_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
    sys.stderr = open(os.path.join(log_dir, 'backend_stderr.log'), 'a', encoding='utf-8')

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8756,
        log_level="info",
    )