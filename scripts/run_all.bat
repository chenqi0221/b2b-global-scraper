@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
cd /d "%ROOT%"

echo ========================================
echo  B2B 一键：测试 + 前端构建 + Rust 检查 + 桌面打包
echo  仓库：%ROOT%
echo ========================================

call "%~dp0smoke_test.bat"
if errorlevel 1 (
  echo [FAIL] smoke_test 未通过，已中止（未执行打包）。
  exit /b 1
)

echo.
echo ==== 4/4 npm run package ^(tauri build，可能数分钟^) ====
cd /d "%ROOT%\tauri-app"
call npm run package
if errorlevel 1 (
  echo [FAIL] npm run package
  exit /b 1
)

echo.
echo [OK] 全部完成。安装包见 tauri-app\src-tauri\target\release\bundle\nsis\
exit /b 0
