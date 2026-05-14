"""项目内路径校验（防止任意文件读写）。"""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def downloads_dir() -> Path:
    return project_root() / "Downloads"


def resolve_under_root(path_str: str, *, must_exist: bool, expect_dir: bool | None = False) -> Path:
    """解析为绝对路径并限制在项目根目录或 Downloads 输出目录下。

    ``expect_dir``：``True`` 要求目录；``False`` 要求文件；``None`` 不校验类型（用于先解析再分支处理的路径）。
    """
    root = project_root()
    downloads = downloads_dir()
    raw = Path(path_str).expanduser()
    path = raw if raw.is_absolute() else (root / raw).resolve()
    path = path.resolve()

    # 允许项目根目录或 Downloads 目录下的路径
    try:
        path.relative_to(root)
    except ValueError:
        try:
            path.relative_to(downloads)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="路径必须位于项目根目录或 Downloads 目录内") from e

    if must_exist and not path.exists():
        raise HTTPException(status_code=400, detail="路径不存在")
    if expect_dir is True and path.exists() and not path.is_dir():
        raise HTTPException(status_code=400, detail="需要目录路径")
    if expect_dir is False and path.exists() and not path.is_file():
        raise HTTPException(status_code=400, detail="需要文件路径")
    return path
