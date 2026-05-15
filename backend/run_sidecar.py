"""
PyInstaller 打包入口：在冻结环境中启动 Uvicorn（免用户机预装 Python）。

构建示例（在项目根目录）::

    pyinstaller build/pyinstaller/b2b-backend.spec

运行（默认端口 8756）::

    b2b-backend.exe
    b2b-backend.exe 8756
"""

from __future__ import annotations

import multiprocessing
import os
import sys
from pathlib import Path

# 支持 PyInstaller 冻结环境
if getattr(sys, "frozen", False):
    # 在 PyInstaller 中，exe 被解压到临时目录
    _ROOT = Path(sys.executable).resolve().parent
else:
    _ROOT = Path(__file__).resolve().parent.parent

if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# 调试：打印 sys.path 和 backend 模块路径
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("run_sidecar")
logger.info(f"sys.path={sys.path}")
logger.info(f"_ROOT={_ROOT}")
try:
    import backend
    logger.info(f"backend module file={backend.__file__}")
    logger.info(f"backend module path={backend.__path__}")
except Exception as e:
    logger.error(f"Failed to import backend: {e}")


def main() -> None:
    port = int(os.environ.get("B2B_PY_PORT", "8756"))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    import uvicorn

    # 在 PyInstaller 冻结环境中，直接导入 app 对象而非通过模块路径字符串
    if getattr(sys, "frozen", False):
        from backend.main import app
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info",
            access_log=False,
        )
    else:
        uvicorn.run(
            "backend.main:app",
            host="127.0.0.1",
            port=port,
            log_level="info",
            access_log=False,
        )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
