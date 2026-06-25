param(
    [switch]$RebuildSidecar
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$tauriDir = "$PSScriptRoot"
$srcTauri = "$tauriDir\src-tauri"
$portableDir = "$tauriDir\portable\B2B Global 获客系统"

Write-Output "============================================"
Write-Output "  B2B Global 获客系统 - 便携版构建脚本"
Write-Output "============================================"
Write-Output ""

if ($RebuildSidecar) {
    Write-Output "[1/4] 重新打包 Python sidecar (PyInstaller)..."
    Push-Location $root
    try {
        pyinstaller --noconfirm backend/run_sidecar.py `
            --name backend `
            --onedir `
            --noconsole `
            --add-data "backend;backend" `
            --add-data "core;core" `
            --add-data "scraper;scraper" `
            --add-data "services;services" `
            --add-data "utils;utils" `
            --add-data "models;models" `
            --add-data "config.py;." `
            --add-data "data.py;." `
            --add-data "google_sheets_service.py;." `
            --add-data "keyword_manager.py;." `
            --add-data "scraper_core.py;." `
            --add-data "async_utils.py;." `
            --add-data "requirements.txt;." `
            --hidden-import uvicorn.logging `
            --hidden-import uvicorn.loops `
            --hidden-import uvicorn.loops.auto `
            --hidden-import uvicorn.protocols `
            --hidden-import uvicorn.protocols.http `
            --hidden-import uvicorn.protocols.http.auto `
            --hidden-import uvicorn.protocols.websockets `
            --hidden-import uvicorn.protocols.websockets.auto `
            --hidden-import fastapi `
            --hidden-import fastapi.middleware.cors `
            --hidden-import pydantic `
            --hidden-import starlette `
            --hidden-import backend.main `
            --hidden-import backend.routers.ai `
            --hidden-import backend.routers.config `
            --hidden-import backend.routers.data `
            --hidden-import backend.routers.google_oauth `
            --hidden-import backend.routers.keywords `
            --hidden-import backend.routers.logs `
            --hidden-import backend.routers.meta `
            --hidden-import backend.routers.scraper `
            --hidden-import backend.routers.sync `
            --hidden-import backend.routers.system `
            --hidden-import backend.schemas.common `
            --hidden-import backend.schemas.settings `
            --hidden-import backend.services.log_bus `
            --hidden-import backend.deps `
            --hidden-import core.config_service `
            --hidden-import core.keyword_service `
            --hidden-import core.scraper_controller `
            --hidden-import core.sync_service `
            --hidden-import scraper.email_extractor `
            --hidden-import scraper.file_export `
            --hidden-import scraper.google_maps `
            --hidden-import services.sheet_aggregator `
            --distpath $srcTauri/binaries
        Write-Output "PyInstaller 打包完成"
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Output "[1/4] 跳过 PyInstaller (使用已有的 sidecar)"
}

Write-Output "[2/4] 安装前端依赖..."
Push-Location $tauriDir
try {
    npm install
    Write-Output "依赖安装完成"
}
finally {
    Pop-Location
}

Write-Output "[3/4] 构建 Tauri 应用 (前端 + Rust)..."
Push-Location $tauriDir
try {
    npm run tauri:build
    Write-Output "Tauri 构建完成"
}
finally {
    Pop-Location
}

Write-Output "[4/4] 创建便携版目录..."
New-Item -ItemType Directory -Force -Path $portableDir | Out-Null

Copy-Item -Path "$srcTauri\target\release\app.exe" -Destination $portableDir -Force
Write-Output "  app.exe 已复制"

$backendBin = "$srcTauri\binaries\backend"
if (Test-Path $backendBin) {
    Copy-Item -Path "$backendBin\*" -Destination $portableDir -Recurse -Force
    Write-Output "  backend sidecar 已复制"
}
else {
    Write-Error "未找到 PyInstaller 输出: $backendBin"
    Write-Error "请先运行: .\build_portable.ps1 -RebuildSidecar"
    exit 1
}

# 复制 Playwright 浏览器到便携版目录
Write-Output "  正在复制 Playwright 浏览器..."
$pwBrowsersDir = "$env:USERPROFILE\AppData\Local\ms-playwright"
if (Test-Path $pwBrowsersDir) {
    $targetBrowsersDir = "$portableDir\playwright\chromium-1208\chrome-win64"
    $sourceChromium = "$pwBrowsersDir\chromium-1208\chrome-win64"
    if (Test-Path $sourceChromium) {
        New-Item -ItemType Directory -Force -Path $targetBrowsersDir | Out-Null
        Copy-Item -Path "$sourceChromium\*" -Destination $targetBrowsersDir -Recurse -Force
        Write-Output "  Playwright Chromium 浏览器已复制"
    } else {
        Write-Warning "  未找到 Playwright Chromium 浏览器: $sourceChromium"
        Write-Warning "  请先运行: playwright install chromium"
    }
} else {
    Write-Warning "  未找到 Playwright 浏览器缓存: $pwBrowsersDir"
    Write-Warning "  请先运行: playwright install chromium"
}

Write-Output ""
Write-Output "============================================"
Write-Output "  便携版构建完成!"
Write-Output "  位置: $portableDir"
Write-Output ""
Write-Output "  使用方法:"
Write-Output "    1. 将整个目录复制到 U 盘或目标电脑"
Write-Output "    2. 双击 app.exe 即可运行"
Write-Output "    3. 无需安装任何依赖"
Write-Output "============================================"
