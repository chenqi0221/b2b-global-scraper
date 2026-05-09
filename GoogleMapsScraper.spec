# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_scraper.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('pages', 'pages'), ('date_data', 'date_data'), ('.env', '.'), ('client_secret.json', '.'), ('token.json', '.'), ('keywords_library.json', '.'), ('app_config.json', '.'), ('data.py', '.'), (r'C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\site-packages\playwright_stealth\js', 'playwright_stealth\js')],
    hiddenimports=['svglib', 'reportlab', 'openai', 'google.generativeai', 'pydantic'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GoogleMapsScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GoogleMapsScraper',
)
