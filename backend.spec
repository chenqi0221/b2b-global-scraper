# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

ROOT = Path(SPECPATH)

added_files = []
for f in ['.env', 'client_secret.json', 'token.json', 'keywords_library.json', 'app_config.json']:
    p = ROOT / f
    if p.exists():
        added_files.append((str(p), '.'))

hiddenimports = []
for pkg in [
    'backend', 'backend.routers', 'backend.services', 'backend.schemas',
    'core', 'scraper', 'services',
    'fastapi', 'uvicorn', 'starlette',
    'playwright', 'playwright_stealth',
    'httpx', 'httpcore', 'socksio',
    'pandas', 'openpyxl', 'bs4',
    'openai', 'google.generativeai', 'google.api_core',
    'gspread', 'google.auth', 'google_auth_oauthlib', 'google_auth_httplib2',
    'pydantic', 'pydantic_core', 'python_dotenv',
    'tqdm', 'requests', 'urllib3',
    'certifi', 'charset_normalizer', 'idna',
    'anyio', 'sniffio', 'h11',
]:
    try:
        hiddenimports.extend(collect_submodules(pkg))
    except Exception:
        hiddenimports.append(pkg)

datas = []
for pkg in ['backend', 'core', 'scraper', 'services', 'playwright_stealth']:
    try:
        datas.extend(collect_data_files(pkg))
    except Exception:
        pass

a = Analysis(
    ['backend_main.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=added_files + datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'ttkbootstrap', 'PIL', 'matplotlib', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    a.zipfiles,
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)