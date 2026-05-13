@echo off
chcp 65001 >nul
title WhatsApp Bot 启动器
echo ==========================================
echo    WhatsApp Bot 自动化工具
echo ==========================================
echo.

REM 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo [1/3] Node.js 版本: 
node --version
echo.

REM 进入项目目录
cd /d "E:\办公小程序\WhatsApp自动化库\whatsapp-web.js"
if errorlevel 1 (
    echo [错误] 无法进入项目目录
    pause
    exit /b 1
)

echo [2/3] 项目目录: %cd%
echo.

REM 检查 node_modules 是否存在
if not exist "node_modules" (
    echo [3/3] 正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [3/3] 依赖已安装
)

echo.
echo ==========================================
echo    正在启动 WhatsApp Bot...
echo    启动后会自动打开浏览器访问管理界面
echo    地址: http://localhost:3003
echo ==========================================
echo.

REM 启动服务
node web.js

REM 如果服务异常退出，暂停显示错误
if errorlevel 1 (
    echo.
    echo [错误] 服务异常退出
    pause
)
