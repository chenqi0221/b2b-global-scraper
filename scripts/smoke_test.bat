@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
cd /d "%ROOT%"

echo ==== 1/3 pytest ====
python -m pytest tests/ -v --tb=short
if errorlevel 1 (
  echo [FAIL] pytest
  exit /b 1
)

echo ==== 2/3 npm run build (tauri-app) ====
cd /d "%ROOT%\tauri-app"
call npm run build
if errorlevel 1 (
  echo [FAIL] npm run build
  exit /b 1
)

echo ==== 3/3 cargo check (src-tauri) ====
cd /d "%ROOT%\tauri-app\src-tauri"
cargo check
if errorlevel 1 (
  echo [FAIL] cargo check
  exit /b 1
)

echo [OK] All smoke steps passed.
exit /b 0
