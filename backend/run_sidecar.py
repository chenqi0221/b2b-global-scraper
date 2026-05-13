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

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> None:
    port = int(os.environ.get("B2B_PY_PORT", "8756"))
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    import uvicorn

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
