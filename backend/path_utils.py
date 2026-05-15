"""项目内路径校验（防止任意文件读写）。"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import HTTPException


def _get_app_dir() -> Path:
    """返回应用实际运行目录（PyInstaller 下为 exe 所在目录，开发时为项目根）。"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def project_root() -> Path:
    """项目根目录：优先使用 exe 所在目录（便携版），否则源码目录。"""
    return _get_app_dir()


def downloads_dir() -> Path:
    return project_root() / "Downloads"


def resolve_under_root(path_str: str, *, must_exist: bool, expect_dir: bool | None = False) -> Path:
    """解析为绝对路径。不再限制在项目根目录下，允许任意合法路径。

    ``expect_dir``：``True`` 要求目录；``False`` 要求文件；``None`` 不校验类型（用于先解析再分支处理的路径）。
    """
    raw = Path(path_str).expanduser()
    path = raw if raw.is_absolute() else raw.resolve()
    path = path.resolve()

    if must_exist and not path.exists():
        raise HTTPException(status_code=400, detail="路径不存在")
    if expect_dir is True and path.exists() and not path.is_dir():
        raise HTTPException(status_code=400, detail="需要目录路径")
    if expect_dir is False and path.exists() and not path.is_file():
        raise HTTPException(status_code=400, detail="需要文件路径")
    return path
