"""
PyInstaller 打包入口：作为 Tauri sidecar 运行，启动 uvicorn 服务。

打包命令（在项目根目录执行）：
    pyinstaller backend/run_sidecar.py \
        --name backend \
        --onedir \
        --noconsole \
        --add-data "backend;backend" \
        --add-data "core;core" \
        --add-data "scraper;scraper" \
        --add-data "services;services" \
        --add-data "utils;utils" \
        --add-data "models;models" \
        --add-data "config.py;." \
        --add-data "data.py;." \
        --add-data "google_sheets_service.py;." \
        --add-data "keyword_manager.py;." \
        --add-data "scraper_core.py;." \
        --add-data "async_utils.py;." \
        --add-data "requirements.txt;." \
        --hidden-import uvicorn.logging \
        --hidden-import uvicorn.loops \
        --hidden-import uvicorn.loops.auto \
        --hidden-import uvicorn.protocols \
        --hidden-import uvicorn.protocols.http \
        --hidden-import uvicorn.protocols.http.auto \
        --hidden-import uvicorn.protocols.websockets \
        --hidden-import uvicorn.protocols.websockets.auto \
        --hidden-import fastapi \
        --hidden-import fastapi.middleware.cors \
        --hidden-import pydantic \
        --hidden-import starlette \
        --hidden-import backend.main \
        --hidden-import backend.routers.ai \
        --hidden-import backend.routers.config \
        --hidden-import backend.routers.data \
        --hidden-import backend.routers.google_oauth \
        --hidden-import backend.routers.keywords \
        --hidden-import backend.routers.logs \
        --hidden-import backend.routers.meta \
        --hidden-import backend.routers.scraper \
        --hidden-import backend.routers.sync \
        --hidden-import backend.routers.system \
        --hidden-import backend.schemas.common \
        --hidden-import backend.schemas.settings \
        --hidden-import backend.services.log_bus \
        --hidden-import backend.deps \
        --hidden-import core.config_service \
        --hidden-import core.keyword_service \
        --hidden-import core.scraper_controller \
        --hidden-import core.sync_service \
        --hidden-import scraper.email_extractor \
        --hidden-import scraper.file_export \
        --hidden-import scraper.google_maps \
        --hidden-import services.sheet_aggregator \
        --distpath tauri-app/src-tauri/binaries
"""

import sys
import os
from pathlib import Path


def _resolve_repo_root() -> Path:
    """在 PyInstaller 环境中定位仓库根目录。"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的 exe 所在目录
        exe_dir = Path(sys.executable).parent.resolve()
        # onedir 模式下，exe 在 backend/ 子目录中，向上找
        for parent in [exe_dir, exe_dir.parent]:
            if (parent / "backend" / "main.py").is_file():
                return parent
        # fallback：exe 同级
        return exe_dir
    else:
        # 开发模式：本文件在 backend/ 下
        return Path(__file__).resolve().parent.parent


def _fix_stdio():
    """PyInstaller --noconsole 下 sys.stdout/stderr 为 None，uvicorn 日志初始化会崩溃。"""
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")


def main():
    _fix_stdio()

    root = _resolve_repo_root()
    os.chdir(root)

    # 确保根目录在 sys.path 首位
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    # 设置环境变量，让 backend/main.py 中的路径解析正确
    os.environ.setdefault("B2B_REPO_ROOT", root_str)

    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8756,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
