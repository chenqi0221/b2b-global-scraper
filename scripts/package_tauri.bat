@echo off
setlocal
chcp 65001 >nul
rem 仅打包。需先 pytest+build+check 请用 run_all.bat
set "ROOT=%~dp0.."
cd /d "%ROOT%\tauri-app"

echo ==== npm run build + tauri build ====
call npm run package
if errorlevel 1 (
  echo [FAIL] Desktop package build failed.
  exit /b 1
)

echo [OK] Artifacts under tauri-app\src-tauri\target\release\bundle\
exit /b 0
